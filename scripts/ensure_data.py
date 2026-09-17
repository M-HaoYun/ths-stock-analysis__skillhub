#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据新鲜度门禁（通用前置检查，所有依赖本地 DuckDB 的分析能力开工前调用）

背景：回测引擎/情绪扫描(涨跌家数)/板块轮动/组合风险等能力依赖本地 DuckDB（market.duckdb）。
本地库若停留在旧交易日，本地查询会缺最近数据（涨跌家数直接为空），被迫转远端 + WebSearch
兜底，费时且口径不一致（2026-09-03 教训：库停在 08-21，情绪扫描涨跌家数折腾半天改 WebSearch）。
因此**任何分析开工前先把数据更新到最新**（用户定稿规则）。

用法（任意目录运行，脚本只调 CLI 不落盘）：
    python ensure_data.py            # 检查；落后则询问 y=自动同步 / n=跳过 / q=退出
    python ensure_data.py --yes      # 非交互：落后直接自动同步（Agent 场景推荐）
    python ensure_data.py --check    # 仅检查不更新：exit 0=已最新 1=落后 2=未初始化 3=CLI异常

判定逻辑：
1. 本地库是否初始化：`db query SELECT max(date) FROM raw_kline_daily`（未 init 会报错/返回空）
2. 最近完整交易日：`market calendar` 解析最后一个 ≤ 今天的交易日
   （calendar 返回过去一年窗口 ~243 个交易日、含最近交易日，可放心用；
   坑：禁止 head 截断看开头——2026-09-03 曾 head -c 2000 看到全 2025 条目误判"不含 09-02"）
3. 比较：本地==最近交易日 → 通过；
   落后 ≤10 自然日 → `data sync` 增量（同步包 daily-k-10d = 仅覆盖最近 10 自然日 ≈7 交易日）；
   落后 >10 自然日（月度场景）→ 增量无法补齐，需全量重拉（打印指引）
4. 同步后复验 max(date)，仍落后 → 打印全量重拉指引

⚠️ DuckDB 内存坑（重要，2026-09-03 实测）：CLI 默认 DuckDB 内存上限 = min(1GiB, 25% 物理内存)，
本地库 ~750MB 时 `data sync` commit 报 "failed to pin block ... (1023.7 MiB/1.0 GiB used)" 失败！
→ 本机已持久化用户级环境变量 HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT=4GiB（15.8GB 内存）；
  新机器若遇该错：`setx HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT 4GiB`（或临时 export）后重试。
  另有 HITHINK_FINANCE_DUCKDB_THREADS（1-64 整数）可限线程。
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys


def run_cli(args, timeout=180):
    """执行 hithink-finance CLI，返回 (exit_code, stdout_text)。找不到命令时自动 which 兜底。"""
    exe = os.environ.get("HITHINK_FINANCE_CLI") or "hithink-finance"
    try:
        p = subprocess.run([exe] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, p.stdout
    except FileNotFoundError:
        found = shutil.which("hithink-finance")
        if not found:
            print("[ensure_data] ❌ 找不到 hithink-finance CLI —— 请先安装 hithink-finance skill 并确认 `hithink-finance --version` 可用（坑22：先 which 定位，勿凭记忆写路径）")
            sys.exit(3)
        p = subprocess.run([found] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        print(f"[ensure_data] ❌ CLI 调用超时(>{timeout}s): {' '.join(args)}")
        sys.exit(3)


def extract_json(text):
    """优先整体解析；失败则取最后一个 '{' 到结尾的子串（data sync 进度条混入 stdout 时兜底）。"""
    try:
        return json.loads(text)
    except Exception:
        pass
    i = text.rfind("{")
    if i < 0:
        return None
    try:
        return json.loads(text[i:])
    except Exception:
        return None


def recent_trade_day():
    """目标最新交易日 = 最近一个已收盘且已发布的交易日（calendar 中 < 今天的最大日期）。

    关键：**今天(当日)无论盘中/盘后都不作为目标**——日K当日要收盘后晚间才由服务端发布
    （实测 2026-09-03 盘中 data sync 停在 release 20260902）；把"今天"当目标会在盘中误报
    落后 1 天并触发无谓 sync。今天的数据明天跑 ensure 自然拿到（sync 幂等、无缺口）。
    返回 'YYYY-MM-DD' 或 None。
    """
    rc, out = run_cli(["market", "calendar", "--format", "json"])
    d = extract_json(out)
    if not d or not d.get("ok"):
        return None
    data = d["data"]
    items = data["item"] if isinstance(data, dict) and "item" in data else (data if isinstance(data, list) else [])
    today = dt.date.today()
    days = []
    for x in items:
        try:
            dd = dt.datetime.strptime(str(x["date"]), "%Y%m%d").date()
        except Exception:
            continue
        if dd < today:          # 严格 < 今天（当日未发布，跳过）
            days.append(dd)
    return max(days).isoformat() if days else None


def local_max_date():
    """本地库最新交易日 → 'YYYY-MM-DD'；未初始化/无表 → None。"""
    rc, out = run_cli(["db", "query", "--sql", "SELECT max(date) AS m FROM raw_kline_daily"])
    d = extract_json(out)
    if not d or not d.get("ok") or not d.get("data"):
        return None
    return d["data"][0].get("m")


def full_reload_guide():
    print("""
[ensure_data] ⚠️ 落后超过增量覆盖范围（>10 自然日 ≈7+ 交易日，月度场景）→ 需全量重拉：
  ① 同花顺开放平台签预签名 URL（详见 hithink-finance skill references/数据初始化文档）：
     GET /api/dump/market-dumps/daily-k/download-url 与 /adjustment-factors/download-url
  ② 下载 daily-k（~172MB，约 11 分钟 @264KB/s）+ adjustment-factors 两文件（预签名 5 分钟有效）
  ③ hithink-finance data init --kline <daily-k文件> --events <adjustment-factors文件>
  ④ 验证：hithink-finance data status && db query "SELECT max(date) FROM raw_kline_daily"
  可考虑把月度全量重拉做成定时自动任务（参考项目长期记忆·本地库更新）。
""")


def main():
    check_only = "--check" in sys.argv
    auto_yes = "--yes" in sys.argv

    local = local_max_date()
    if not local:
        print("[ensure_data] ❌ 本地 DuckDB 未初始化或 raw_kline_daily 表不存在")
        print("   初始化：同花顺开放平台签预签名 URL 下载 daily-k + adjustment-factors →")
        print("   `hithink-finance data init --kline <文件> --events <文件>` → `data status` 验证")
        print("   （详见 hithink-finance skill references 数据初始化文档）")
        sys.exit(2)

    latest = recent_trade_day()
    if not latest:
        print(f"[ensure_data] ⚠️ 无法获取交易日历（网络/接口异常），本地数据最新={local} —— 跳过自动更新，注意数据可能滞后")
        sys.exit(3)

    if local >= latest:
        print(f"[ensure_data] ✅ 数据已最新：本地 {local} == 最近交易日 {latest}，可直接开工")
        sys.exit(0)

    lag = (dt.date.fromisoformat(latest) - dt.date.fromisoformat(local)).days
    print(f"[ensure_data] ⚠️ 本地库落后：本地 {local} / 最近交易日 {latest}（差 {lag} 自然日）")

    if lag > 10:
        full_reload_guide()
        sys.exit(1)

    if check_only:
        print(f"[ensure_data] 落后 {lag} 自然日（≤10，增量可覆盖）→ 运行 `python ensure_data.py` 或 `--yes` 执行 data sync")
        sys.exit(1)

    # 落后 ≤10 自然日 → data sync 增量
    if auto_yes:
        ans = "y"
    elif sys.stdin.isatty():
        ans = input("[ensure_data] 是否现在执行 `data sync` 增量同步到最新？(y=同步 / n=跳过 / q=退出) ").strip().lower()
    else:
        ans = "y"  # 非交互（Agent 自动化）默认同步——"以后用这个 skill 都先将数据更新到最新"
    if ans == "q":
        print("[ensure_data] 已退出。注意：本地库滞后，依赖本地数据的分析（涨跌家数/复权K线）可能缺最近数据")
        sys.exit(1)
    if ans != "y":
        print("[ensure_data] 已跳过更新（数据滞后，本地查询可能为空/缺失）")
        sys.exit(1)

    print(f"[ensure_data] ⏳ 执行 data sync（增量 daily-k-10d + adjustment-factors，约 1-3 分钟）...")
    rc, out = run_cli(["data", "sync"], timeout=900)
    d = extract_json(out)
    if rc == 0 and d and d.get("ok"):
        rel = (d.get("data") or {}).get("release_id", "")
        print(f"[ensure_data] ✅ data sync 成功：{rel}")
    else:
        tail = out.strip().splitlines()
        print(f"[ensure_data] ❌ data sync 失败 rc={rc}：{tail[-1][:300] if tail else '(无输出)'}")
        print("   若报 DuckDB 内存错误(failed to pin block/1.0 GiB used)：先设 HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT=4GiB（见文件头）再重试")
        full_reload_guide()
        sys.exit(1)

    local2 = local_max_date()
    if local2 and local2 >= latest:
        print(f"[ensure_data] ✅ 更新完成：本地 {local2} == 最近交易日 {latest}")
        sys.exit(0)
    print(f"[ensure_data] ⚠️ 同步后本地仍为 {local2}（< {latest}）——可能已超出增量覆盖范围，需全量重拉")
    full_reload_guide()
    sys.exit(1)


if __name__ == "__main__":
    main()
