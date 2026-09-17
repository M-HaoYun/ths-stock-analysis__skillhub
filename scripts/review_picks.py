# -*- coding: utf-8 -*-
"""推荐复盘器：扫描工作区里的历史「精选N股推荐」报告，回算推荐后的真实表现。

用途
----
回答「之前推荐的股票后来涨了还是跌了、这套策略准不准」。产出：
  1. 逐笔明细（建仓价 / 最新价 / 收益 / 区间最大浮盈 / 最大回撤）
  2. 汇总（胜率 / 平均 / 中位数 / 最好最差 / **剔除最大盈利单笔后的平均**）
  3. 不同离场规则的对比（持有 / 破 MA5 / 破 MA10 / 固定止损 -5% / -8%）

口径（务必与结论一起读）
------------------------
  · 建仓 = 推荐日**次一交易日的开盘价**（读者最早能执行的价格）
  · 平仓 = 最新可得交易日收盘（`--end` 可指定）
  · 收益 = 平仓价 / 建仓价 - 1
  · ⚠️ 报告正文通常写「只做回踩、不追高」，而本脚本按「次日开盘买入」计算 →
    **不是照报告纪律执行的结果**，而是「照最粗暴方式买入」的结果。两者差值本身就是结论。
  · ⚠️ 未计交易成本（手续费/印花税/滑点），实际收益每笔再低约 0.1~0.3pct。

用法（在**工作区根目录**执行；需已装 hithink-finance CLI 且本地库已同步）
--------------------------------------------------------------------
    python <skill>/scripts/review_picks.py
    python <skill>/scripts/review_picks.py --end 2026-09-16
    python <skill>/scripts/review_picks.py --pattern "精选*推荐_*.html" --json out.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from statistics import mean

# ---- CLI 定位（不写死可执行名，避免 PATH 差异）----
def _cli_cmd() -> list[str]:
    """返回调用 hithink-finance CLI 的命令前缀。

    解析顺序：① 环境变量 HITHINK_CLI ② PATH 上的 hithink-finance
    ③ 常见 node_modules 路径下的 @hithink-tech/hithink-finance-cli/dist/cli/main.js
    （含 `~/.workbuddy/binaries/node/versions/*/node_modules` 这种版本化布局）
    """
    import shutil as _sh
    exe = os.environ.get("HITHINK_CLI")
    if exe:
        return [exe]
    found = _sh.which("hithink-finance")
    if found:
        return [found]

    rel = os.path.join("@hithink-tech", "hithink-finance-cli", "dist", "cli", "main.js")
    roots = [
        os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules"),
        os.path.join(os.path.expanduser("~"), ".workbuddy", "binaries", "node", "workspace", "node_modules"),
    ]
    # 版本化布局：~/.workbuddy/binaries/node/versions/<ver>/node_modules
    vroot = os.path.join(os.path.expanduser("~"), ".workbuddy", "binaries", "node", "versions")
    if os.path.isdir(vroot):
        for ver in sorted(os.listdir(vroot), reverse=True):
            roots.append(os.path.join(vroot, ver, "node_modules"))
    for base in roots:
        p = os.path.join(base, rel)
        if os.path.exists(p):
            node = os.environ.get("NODE_BIN")
            if not node:
                # 优先用与 CLI 同居的 node 二进制
                cand = os.path.join(os.path.dirname(os.path.dirname(base)), "node.exe")
                node = cand if os.path.exists(cand) else "node"
            return [node, p]
    return ["hithink-finance"]


CLI = _cli_cmd()

# 卡片标记：**必须容许额外属性**（历史报告被注入过 data-page-node-id="…"，
# 插在 class="no" 与 class="nm" 之间）。曾因正则太严导致"抓全文代码"→ 把被剔除的标的当成推荐。
_NAME_CODE = r'class="nm"[^>]*>([^<]{1,16})</span>\s*<span class="tcode"[^>]*>([0-9]{6}\.[A-Z]{2})'
CARD_MAIN = re.compile(_NAME_CODE)
CARD_IN_CARD = re.compile(r'<div class="card-head">.{0,400}?' + _NAME_CODE, re.S)


def query(sql: str, timeout: int = 180) -> list[dict]:
    r = subprocess.run([*CLI, "db", "query", "--sql", sql, "--format", "json"],
                       capture_output=True, timeout=timeout)
    try:
        d = json.loads(r.stdout.decode("utf-8", "replace"))
        return (d.get("data") or []) if d.get("ok") else []
    except Exception:
        return []


def parse_reports(pattern: str) -> dict[str, list[tuple[str, str]]]:
    """{推荐日 YYYY-MM-DD: [(名称, 代码)]} —— 从文件名取日期，从卡片取标的。"""
    out: dict[str, list[tuple[str, str]]] = {}
    for f in sorted(glob.glob(pattern)):
        m = re.search(r"(\d{4})(\d{2})(\d{2})", os.path.basename(f))
        if not m:
            continue
        day = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        html = open(f, encoding="utf-8", errors="replace").read()
        cards = CARD_IN_CARD.findall(html)
        if not cards:
            cards = CARD_MAIN.findall(html)
            print(f"  ⚠️ {os.path.basename(f)}：未匹配到推荐卡标记，退回宽松匹配（{len(cards)} 项），请人工核对名单")
        if len(cards) > 8:
            print(f"  ⚠️ {os.path.basename(f)}：匹配到 {len(cards)} 项（疑似过度捕获），只取前 5 项")
            cards = cards[:5]
        print(f"  · {os.path.basename(f)} → {len(cards)} 只：{', '.join(n for n, _ in cards)}")
        # 去重（同页正文可能重复提及）
        seen, uniq = set(), []
        for nm, code in cards:
            if code not in seen:
                seen.add(code)
                uniq.append((nm, code))
        if uniq:
            out[day] = uniq
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="精选*推荐_*.html", help="历史推荐报告的文件通配")
    ap.add_argument("--end", default=None, help="平仓日（缺省=本地库最新交易日）")
    ap.add_argument("--json", default=None, help="把逐笔明细另存为 JSON")
    args = ap.parse_args()

    picks = parse_reports(args.pattern)
    if not picks:
        print(f"未找到匹配 {args.pattern} 的历史推荐报告（请在**工作区根目录**执行）")
        return 2
    print(f"发现 {len(picks)} 期推荐，共 {sum(len(v) for v in picks.values())} 笔\n")

    codes = sorted({c for v in picks.values() for _, c in v})
    inlist = ",".join(f"'{c}'" for c in codes)
    rows = query(f"SELECT thscode,date,open,high,low,close FROM v_daily_qfq "
                 f"WHERE thscode IN ({inlist}) AND date >= '2020-01-01' ORDER BY thscode, date")
    bars: dict[str, list[dict]] = {}
    for r in rows:
        bars.setdefault(str(r["thscode"]), []).append(r)
    for k in bars:
        bars[k].sort(key=lambda x: x["date"])
    # 用最长的序列当交易日历
    cal = max((b for b in bars.values()), key=len) if bars else []
    cal = [b["date"] for b in cal]
    if args.end:
        cal = [d for d in cal if d <= args.end]
    if not cal:
        print("本地库无行情，请先 `data sync`")
        return 3

    def ma(code: str, upto: int, n: int) -> float | None:
        bs = bars.get(code) or []
        if upto + 1 < n:
            return None
        return mean(b["close"] for b in bs[upto - n + 1: upto + 1])

    detail, notes = [], []
    for rec, items in sorted(picks.items()):
        after = [d for d in cal if d > rec]
        if not after:
            notes.append(f"[{rec}] 无后续交易日，跳过")
            continue
        entry_date = after[0]
        print("=" * 100)
        print(f"### 推荐日 {rec} → 建仓日 {entry_date}（次日开盘）  [{len(items)} 只]")
        print(f"{'代码':<12}{'名称':<10}{'开仓价':>9}{'最新价':>9}{'收益':>9}{'最高':>9}{'最低':>9}{'最大浮盈':>9}{'最大回撤':>9}")
        for nm, code in items:
            bs = bars.get(code) or []
            idx = next((i for i, b in enumerate(bs) if b["date"] == entry_date), None)
            if idx is None:
                print(f"{code:<12}{nm:<10}   （该日无行情，跳过）")
                notes.append(f"[{rec}] {nm} {code} 建仓日无行情")
                continue
            op = bs[idx]["open"]
            win = [b for b in bs[idx:] if b["date"] <= cal[-1]]
            if not win:
                continue
            last, hi, lo = win[-1]["close"], max(b["high"] for b in win), min(b["low"] for b in win)
            ret, mfe, mae = last / op - 1, hi / op - 1, lo / op - 1
            # 离场规则
            ex = {}
            for tag, n in (("破MA5", 5), ("破MA10", 10)):
                px = win[-1]["close"]
                for j in range(idx, idx + len(win)):
                    m = ma(code, j, n)
                    if m is not None and bs[j]["close"] < m:
                        px = bs[j + 1]["open"] if j + 1 < len(bs) else bs[j]["close"]
                        break
                ex[tag] = px / op - 1
            for tag, sl in (("止损5%", 0.05), ("止损8%", 0.08)):
                trig = op * (1 - sl)
                hit = next((b for b in win if b["low"] <= trig), None)
                ex[tag] = (trig / op - 1) if hit else ret
            detail.append({"rec": rec, "code": code, "name": nm, "entry": entry_date,
                           "open": op, "last": last, "ret": ret, "mfe": mfe, "mae": mae, **ex})
            print(f"{code:<12}{nm:<10}{op:>9.2f}{last:>9.2f}{ret*100:>8.2f}%{hi:>9.2f}{lo:>9.2f}"
                  f"{mfe*100:>8.2f}%{mae*100:>8.2f}%")
        print()

    if not detail:
        print("无有效样本")
        return 4

    n = len(detail)
    rets = [d["ret"] for d in detail]
    win_cnt = sum(1 for r in rets if r > 0)
    print("=" * 100)
    print(f"### 汇总（{n} 笔；建仓=推荐日次日开盘，平仓={cal[-1]}）")
    print(f"  胜率               : {win_cnt}/{n} = {win_cnt/n*100:.1f}%")
    print(f"  平均收益           : {mean(rets)*100:+.2f}%")
    srt = sorted(rets)
    med = srt[n // 2] if n % 2 else (srt[n // 2 - 1] + srt[n // 2]) / 2
    print(f"  中位数             : {med*100:+.2f}%")
    print(f"  最好 / 最差        : {max(rets)*100:+.2f}% / {min(rets)*100:+.2f}%")
    if n > 2:
        s2 = sorted(rets, reverse=True)[1:]
        flag = "更差 → 无单笔驱动的假优势" if mean(s2) < mean(rets) else "更好 → 有单笔虚增"
        print(f"  ★剔除最大盈利单笔后: {mean(s2)*100:+.2f}%（原 {mean(rets)*100:+.2f}%）  {flag}")

    print(f"\n### 离场规则对比（同一批建仓）")
    for tag in ("破MA5", "破MA10", "止损5%", "止损8%"):
        vals = [d[tag] for d in detail]
        w = sum(1 for v in vals if v > 0)
        print(f"  {tag:<8} 平均 {mean(vals)*100:>+7.2f}%   胜率 {w}/{n}={w/n*100:>5.1f}%   最差 {min(vals)*100:>+7.2f}%")
    print(f"  持有     平均 {mean(rets)*100:>+7.2f}%   胜率 {win_cnt}/{n}={win_cnt/n*100:>5.1f}%   最差 {min(rets)*100:>+7.2f}%")

    print("\n### ⚠️ 结论必须附带的样本局限")
    print(f"  样本仅 {n} 笔、{len(picks)} 期；单一市场环境；持有期可能未走完（策略定义 3~10 个交易日）；未计交易成本。"
          "\n  → 任何按特征切分的规则都属于过拟合，需累积 50~100 笔再谈有效性。")
    for x in notes:
        print("  ·", x)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, indent=1)
        print("\n明细已落盘:", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
