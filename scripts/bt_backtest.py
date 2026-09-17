# -*- coding: utf-8 -*-
"""DuckDB 回测引擎 v3.6 —— 20 大经典策略模板引擎（10 经典 + 9 短线 + W底）
读 strategies.json 策略定义（五要素齐全），SQL 一次预计算全部技术指标列，
按 buy_signal/sell_signal 分派信号，事件驱动回测（单标的满仓、开盘价成交）。
用法：python bt_backtest.py --all            # 跑全部策略
      python bt_backtest.py --strategy ma_cross   # 跑单个
路径约定（v3.5）：
- 策略定义 = **脚本同目录的 strategies.json**（以 skill 内版本为准；THS_STRATEGIES 可覆盖）
- 数据(parquet/hs300) 与 产物(bt_result_*.json/bt_all.json) = <工作区>/.workbuddy/output/（自动创建）
股票名称（v3.6，坑 41）：
- 本地 v_symbol.name 全 NULL → 引擎自动加载 `<工作区>/.workbuddy/output/bt_name_map.json`（thscode→name）
  回填每笔交易 name 字段；文件缺失时自动调 `hithink-finance symbol list` 生成，失败则回退显示代码。
输出：.workbuddy/output/bt_result_{id}.json（单策略）+ bt_all.json（汇总对比）
【口径（必须标注）】
- 数据：本地 DuckDB v_daily_qfq 前复权日K（2025-08-22~2026-08-21，含 MA/RSI 预热）
- 涨停判定：主板(60/00) >= +9.8%；创业板/科创板(30/688) >= +19.8%（前复权相邻日收益率）
- RSI14 为 SMA 均值口径（非 Wilder 平滑）[ASSUMED]；布林=MA20±2σ（stddev_samp）
- 唐奇安通道：突破前 20 日最高 / 跌破前 10 日最低（不含当日）
- 短线指标（v3.4 新增）：KDJ(9,3,3) 用 SMA 平滑口径 [ASSUMED]；MACD(12,26,9) 用 EMA；
  乖离率 bias20=close/MA20-1；连阳 cnt_up=截至当日连续收阳天数（含当日）；
  振幅振幅5=近5日(high-low)/prev_close 均值；缺口 gap=open/prev_close-1（未回补判定用 前日 high）
- 买入仓位=满仓、卖出仓位=清仓、按开盘价成交、单边 0.03% 费率（印花税未含）
- 当前资金：初始 1,000,000 元，每笔清仓后按 (1+ret) 滚动累计
- 市场情绪代理（仅 streak_2）：当日涨停≥20 家且上涨占比>50% [ASSUMED]
- 热度代理：当日成交额 amount [ASSUMED]
"""
import json
import os
import argparse
import duckdb

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
OUT = os.path.join(BASE, ".workbuddy", "output")      # 产物目录：数据 + 回测结果 json
PARQUET = os.path.join(OUT, "bt_qfq_1y.parquet")
HS300 = os.path.join(OUT, "bt_hs300.json")
# ✅ 策略定义与脚本同目录（skill 自身目录）——始终以 skill 内版本为准，工作区只放产物。
#    可用环境变量 THS_STRATEGIES 覆盖（指向自定义策略文件）。
STRATEGIES = os.environ.get("THS_STRATEGIES", os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategies.json"))

CFG = {
    "bt_start": "2025-08-22",
    "bt_end": "2026-08-21",
    "gap_threshold": -0.03,
    "limit_up_main": 0.098,
    "limit_up_ge": 0.198,
    "market_strong_cnt": 20,
    "market_strong_ratio": 0.50,
    "fee_rate": 0.0003,
    "initial_capital": 1_000_000,
}

# ================= 股票名称映射（坑 41：本地 v_symbol.name 全 NULL） =================
# 本地 DuckDB 的 v_symbol.name 全为 NULL，交易明细必须回填真实名称，否则「股票」列会显示成代码。
# 引擎自动加载 bt_name_map.json（dict: thscode -> name）；缺失时按需从远端 symbol list 生成。
NAME_MAP = os.path.join(OUT, "bt_name_map.json")

def load_name_map():
    """返回 {thscode: name}；文件不存在或为空时返回 {}（并在回测前提示生成方法）。"""
    if not os.path.exists(NAME_MAP):
        return {}
    try:
        with open(NAME_MAP, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) and d else {}
    except Exception:
        return {}

def ensure_name_map():
    """确保名称映射可用：缺失时自动用 CLI 拉取远端 symbol list 生成（失败则告警不阻断）。"""
    m = load_name_map()
    if m:
        return m
    import subprocess
    raw = os.path.join(OUT, "_symbol_list_raw.json")
    print("⚠️ 未找到 bt_name_map.json —— 正在用 hithink-finance symbol list 拉取全市场名称…")
    try:
        os.makedirs(OUT, exist_ok=True)
        r = subprocess.run(
            ["hithink-finance", "symbol", "list", "--asset-type", "a-share",
             "--exchange", "SH,SZ,BJ", "--limit", "10000", "--output", raw],
            capture_output=True, text=True, timeout=300, shell=(os.name == "nt"))
        if r.returncode != 0:
            print(f"⚠️ symbol list 失败（{r.returncode}）：{(r.stderr or r.stdout or '')[:200]}")
            return {}
        d = json.load(open(raw, encoding="utf-8"))
        items = (d.get("data") or {}).get("item") or d.get("data") or []
        m = {}
        for it in items:
            code = it.get("thscode") or it.get("code")
            nm = it.get("name") or it.get("secu_name")
            if code and nm:
                m[code] = nm
        if m:
            with open(NAME_MAP, "w", encoding="utf-8") as f:
                json.dump(m, f, ensure_ascii=False)
            print(f"✓ 名称映射已生成：{NAME_MAP}（{len(m)} 条）")
        else:
            print("⚠️ symbol list 返回为空，名称映射不可用；明细「股票」列将回退显示代码。")
    except Exception as e:
        print(f"⚠️ 生成名称映射失败：{e}；明细「股票」列将回退显示代码。")
    finally:
        try:
            if os.path.exists(raw):
                os.remove(raw)
        except Exception:
            pass
    return m

def check_data_readiness(force=False):
    """回测前数据就绪检查：①DuckDB 本地库是否初始化 ②回测数据 bt_qfq_1y.parquet 是否存在
    ③最新交易日是否在一个月内（>30 天视为过期）。不满足 → 打印提醒与更新方法，并**交互式询问
    用户是否先更新数据**（y=更新后重跑 / n=跳过检查继续 / q=退出）；非交互环境（无 TTY）默认退出；
    --force 可跳过交互直接继续。"""
    import datetime
    now = datetime.date.today()
    problems = []

    # ① DuckDB 本地库是否初始化（market.duckdb 是否存在）
    la = os.environ.get("LOCALAPPDATA", "")
    db_path = os.path.join(la, "hithink-finance", "data", "market.duckdb")
    if not os.path.exists(db_path):
        problems.append((
            "本地 DuckDB 库未初始化（找不到 market.duckdb）",
            "初始化方法（全量重拉）：\n"
            "  ① 到同花顺开放平台签预签名 URL 并下载两个文件（约 172MB+0.3MB，URL 5 分钟有效）：\n"
            "     GET /api/dump/market-dumps/daily-k/download-url\n"
            "     GET /api/dump/market-dumps/adjustment-factors/download-url\n"
            "  ② 执行：hithink-finance data init --kline <daily-k文件> --events <复权事件文件>\n"
            "  ③ 验证：hithink-finance data status  和  hithink-finance db query \"SELECT max(date) FROM raw_kline_daily\""))

    # ② 回测数据 parquet 是否存在
    pq_ok = os.path.exists(PARQUET)
    if not pq_ok:
        problems.append((
            "回测数据 bt_qfq_1y.parquet 不存在",
            "先初始化 DuckDB 本地库（见上），再从 v_daily_qfq 导出前复权日K：\n"
            "  hithink-finance db export --sql \"SELECT thscode,date,open,high,low,close,volume,amount FROM v_daily_qfq WHERE date >= '<回测开始前120个交易日>'\" "
            "--output bt_qfq_1y.parquet --file-format parquet\n"
            "  口径：回测窗口最近一年 + 前 120 日指标预热窗口。"))

    # ③ 数据新鲜度（最新交易日距今是否 >30 天）
    max_date = None
    if pq_ok:
        try:
            con = duckdb.connect()
            max_date = con.execute("SELECT CAST(MAX(date) AS DATE) FROM read_parquet(?)", [PARQUET]).fetchone()[0]
        except Exception as e:
            problems.append(("回测数据读取失败", f"read_parquet 报错: {e}\n请确认 parquet 已正确导出（见上）。"))
    if max_date is not None:
        days_old = (now - max_date).days
        if days_old > 30:
            problems.append((
                f"回测数据已过期（最新交易日 {max_date}，距今 {days_old} 天 > 30 天）",
                "更新本地库方法：\n"
                "  ① hithink-finance data status   查看落后交易日数\n"
                "  ② 落后 ≤7 交易日：hithink-finance data sync（增量更新）\n"
                "  ③ 落后 >7 交易日（月度未更）：全量重拉（同上方初始化流程 data init --kline ... --events ...）\n"
                "  ④ 更新后重新导出 bt_qfq_1y.parquet（见上）"))

    if not problems:
        if max_date is not None:
            print(f"数据就绪检查 ✓：DuckDB 已初始化 · 回测数据最新 {max_date}（{days_old} 天前）")
        return True
    if force:
        print("⚠️  数据就绪检查未通过但已加 --force，继续回测（结果可能基于缺失/过期数据）：")
        for t, _ in problems:
            print(f"   - {t}")
        return True
    print("=" * 68)
    print("⚠️  回测数据就绪检查未通过 —— 请先初始化/更新数据：")
    print("=" * 68)
    for i, (title, method) in enumerate(problems, 1):
        print(f"\n[{i}] {title}\n{method}")
    # 交互式确认：先问用户是否更新数据（y=去更新 / n=跳过检查继续 / q=退出）
    try:
        ans = input("\n是否先更新数据再回测？[y=更新后重跑 / n=跳过检查继续 / q=退出]: ").strip().lower()
    except EOFError:
        ans = "q"
    if ans == "y":
        print("请按上方方法更新数据（未初始化→data init 全量重拉；过期→data sync 增量或全量重拉），"
              "完成后重新运行回测。")
        return False
    if ans == "n":
        print("⚠️  已选择跳过数据检查继续回测（结果可能基于缺失/过期数据，仅供参考）。")
        return True
    print("已退出回测。")
    return False


def load_data():
    """SQL 一次预计算全部指标列，返回 by_date 嵌套 dict"""
    con = duckdb.connect()
    con.execute("CREATE TABLE k AS SELECT thscode, date, open, high, low, close, volume, amount FROM read_parquet(?)", [PARQUET])
    con.execute("""
        CREATE TABLE k2 AS SELECT *,
          LAG(close) OVER (PARTITION BY thscode ORDER BY date) AS prev_close,
          close / LAG(close) OVER (PARTITION BY thscode ORDER BY date) - 1 AS ret
        FROM k""")
    con.execute("""
        CREATE TABLE k3 AS SELECT *,
          CASE WHEN substr(thscode,1,2) IN ('30','68') THEN ? ELSE ? END AS limit_th,
          CASE WHEN close / LAG(close) OVER (PARTITION BY thscode ORDER BY date) - 1
                    >= CASE WHEN substr(thscode,1,2) IN ('30','68') THEN ? ELSE ? END
               THEN 1 ELSE 0 END AS is_limit_up
        FROM k2""", [CFG["limit_up_ge"], CFG["limit_up_main"], CFG["limit_up_ge"], CFG["limit_up_main"]])
    con.execute("""
        CREATE TABLE k4 AS SELECT *,
          ROW_NUMBER() OVER (PARTITION BY thscode, grp ORDER BY date) - 1 AS streak
        FROM (SELECT *,
                SUM(CASE WHEN is_limit_up=0 THEN 1 ELSE 0 END) OVER (PARTITION BY thscode ORDER BY date) AS grp
              FROM k3) t""")
    con.execute("""
        CREATE TABLE k5 AS SELECT *,
          AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS ma5,
          AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS ma10,
          AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma20,
          (AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
            > AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW)
            AND AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW)
            > AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
          ) AS bull
        FROM k4""")
    con.execute("""
        CREATE TABLE k6 AS SELECT *,
          AVG(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS ma60,
          (ma5 > ma20 AND ma20 > ma60) AS bull3,
          CASE WHEN close > LAG(close) OVER (PARTITION BY thscode ORDER BY date)
               THEN close - LAG(close) OVER (PARTITION BY thscode ORDER BY date) ELSE 0 END AS gain,
          CASE WHEN close < LAG(close) OVER (PARTITION BY thscode ORDER BY date)
               THEN LAG(close) OVER (PARTITION BY thscode ORDER BY date) - close ELSE 0 END AS loss
        FROM k5""")
    con.execute("""
        CREATE TABLE k7 AS SELECT *,
          STDDEV_SAMP(close) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS sd20,
          MAX(high) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS prior20_high,
          MIN(low) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING) AS prior10_low,
          MIN(low) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS prior60_low,
          MAX(high) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 120 PRECEDING AND 1 PRECEDING) AS prior120_high,
          AVG(volume) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS vol_ma20,
          LAG(ma5) OVER (PARTITION BY thscode ORDER BY date) AS prev_ma5,
          LAG(ma10) OVER (PARTITION BY thscode ORDER BY date) AS prev_ma10,
          LAG(ma20) OVER (PARTITION BY thscode ORDER BY date) AS prev_ma20,
          LAG(close) OVER (PARTITION BY thscode ORDER BY date) AS prev_close2,
          LAG(is_limit_up) OVER (PARTITION BY thscode ORDER BY date) AS prev_is_limit_up,
          100 - 100 / (1 + AVG(gain) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
            / NULLIF(AVG(loss) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)) AS rsi14
        FROM k6""")
    con.execute("""
        CREATE TABLE k8 AS SELECT *,
          ma20 + 2*sd20 AS boll_upper,
          ma20 - 2*sd20 AS boll_lower,
          LAG(ma20 + 2*sd20) OVER (PARTITION BY thscode ORDER BY date) AS prev_boll_upper,
          volume / NULLIF(vol_ma20, 0) AS vol_ratio,
          -- close/MA20 乖离率（正值=高于 MA20）
          CASE WHEN ma20 > 0 THEN close / ma20 - 1 END AS bias20,
          LAG(rsi14) OVER (PARTITION BY thscode ORDER BY date) AS prev_rsi14,
          -- 一字/巨量判定：近5日均振幅（(high-low)/prev_close）
          AVG((high - low) / NULLIF(prev_close, 0))
            OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS amp5,
          AVG(amount) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS amt_ma5,
          AVG(amount) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS amt_ma20,
          MAX(high) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 9 PRECEDING AND 1 PRECEDING) AS prior10_high,
          MIN(low)  OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING) AS prior5_low,
          LAG(prior20_high) OVER (PARTITION BY thscode ORDER BY date) AS prev_prior20_high,
          LAG(is_limit_up) OVER (PARTITION BY thscode ORDER BY date) AS _dummy_plu,
          LAG(open) OVER (PARTITION BY thscode ORDER BY date) AS prev_open
        FROM k7""")
    # 连阳天数 cnt_up：用「收阴日分组 + 组内行号」求真实连续收阳长度
    # ⚠️ 坑：SUM(CASE WHEN close>open...) OVER (UNBOUNDED PRECEDING) 得到的是全历史累计
    #    收阳数（实测可达 168），不是连续长度 →「连续≥3根阳线」条件恒不成立、
    #    first_red_pullback 策略 0 笔。必须用分组+行号法（2026-09-10 实测教训）。
    con.execute("""
        CREATE TABLE k8b AS SELECT * EXCLUDE (_dummy_plu),
          CASE WHEN close > open
               THEN ROW_NUMBER() OVER (PARTITION BY thscode, grp_up ORDER BY date)
               ELSE 0 END AS cnt_up
        FROM (SELECT *,
                SUM(CASE WHEN close > open THEN 0 ELSE 1 END)
                  OVER (PARTITION BY thscode ORDER BY date) AS grp_up
              FROM k8) t""")
    # 昨日连阳数（首阴判定用：昨日仍是长阳线、今日转阴 = 首阴）
    # ⚠️ 坑：阴线当日 cnt_up 必为 0，若用「当日 cnt_up>=N」判「前有长阳」永远不成立
    #    → first_red_pullback 策略 0 笔（2026-09-10 实测）。必须看昨日值。
    con.execute("""
        CREATE TABLE k8c AS SELECT *,
          LAG(cnt_up) OVER (PARTITION BY thscode ORDER BY date) AS prev_cnt_up
        FROM k8b""")
    # KDJ(9,3,3)：RSV=9日随机指标，K/D 用 SMA 平滑（K=2/3*prevK+1/3*RSV）
    con.execute("""
        CREATE TABLE k9 AS SELECT *,
          (close - MIN(low) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW))
          / NULLIF(MAX(high) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW)
                   - MIN(low) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW), 0) AS rsv
        FROM k8c""")
    con.execute("""
        CREATE TABLE k10 AS SELECT *,
          AVG(rsv) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS kv,
          AVG(rsv) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS kd,
          AVG(rsv) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS kr
        FROM k9""")
    con.execute("""
        CREATE TABLE k11 AS SELECT *,
          LAG(kv) OVER (PARTITION BY thscode ORDER BY date) AS prev_k,
          LAG(kd) OVER (PARTITION BY thscode ORDER BY date) AS prev_d,
          kv - kd AS kdj_j_diff
        FROM k10""")
    # 每日市场情绪（仅 streak_2 使用）
    con.execute("""
        CREATE TABLE mkt AS
        SELECT date, SUM(is_limit_up) AS lim_cnt,
          SUM(CASE WHEN ret > 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(*) AS up_ratio
        FROM k3 WHERE date >= ? GROUP BY date""", [CFG["bt_start"]])
    market_strong = {str(r[0]): (r[1] >= CFG["market_strong_cnt"] and r[2] > CFG["market_strong_ratio"])
                     for r in con.execute("SELECT * FROM mkt").fetchall()}
    # 转 Python（只取回测区间）
    cols = ["thscode", "date", "open", "high", "low", "close", "prev_close", "ret",
            "streak", "ma5", "ma10", "ma20", "ma60", "bull", "bull3", "amount",
            "is_limit_up", "rsi14", "boll_upper", "boll_lower", "vol_ratio",
            "prior20_high", "prior10_low", "prior60_low", "prior120_high",
            "prev_ma5", "prev_ma10", "prev_ma20", "prev_close2", "prev_is_limit_up", "prev_boll_upper",
            # ---- v3.4 新增（9 个短线策略所需）----
            "bias20", "cnt_up", "prev_cnt_up", "kv", "kd", "prev_k", "prev_d",
            "amp5", "amt_ma5", "amt_ma20", "prior10_high", "prior5_low",
            "prev_prior20_high", "prev_open", "prev_rsi14"]
    rows = con.execute(
        "SELECT " + ", ".join(cols).replace("date", "CAST(date AS VARCHAR) AS date", 1) + " FROM k11 WHERE date >= ? ORDER BY date, thscode",
        [CFG["bt_start"]]).fetchall()
    by_date = {}
    for r in rows:
        rec = dict(zip(cols, r))
        by_date.setdefault(rec["date"], {})[rec["thscode"]] = rec
    dates = sorted(by_date.keys())
    # ---- Python 端补算 MACD(12,26,9)：真 EMA 递推（SQL 窗口函数做不了递归）----
    seed = {}
    for d in dates:
        for thscode, rec in by_date[d].items():
            c = rec["close"]
            e12, e26 = seed.get(thscode, (c, c))
            e12 = c * (2 / 13) + e12 * (11 / 13)
            e26 = c * (2 / 27) + e26 * (25 / 27)
            seed[thscode] = (e12, e26)
            rec["ema12"], rec["ema26"] = e12, e26
            rec["dif"] = e12 - e26
            rec["prev_dif"] = None  # 次日循环时回填
    # 回填 prev_dif 与 dea（DEA = DIF 的 9 日 EMA）
    dea_seed = {}
    prev_dif_seed = {}
    for d in dates:
        for thscode, rec in by_date[d].items():
            rec["prev_dif"] = prev_dif_seed.get(thscode)
            difv = rec["dif"]
            dea = dea_seed.get(thscode, difv)
            dea = difv * (2 / 10) + dea * (8 / 10)
            dea_seed[thscode] = dea
            rec["dea"] = dea
            rec["macd_bar"] = (difv - dea) * 2
            prev_dif_seed[thscode] = difv
    for i, d in enumerate(dates):
        if i == 0:
            continue
        for thscode, rec in by_date[d].items():
            p = by_date[dates[i - 1]].get(thscode)
            rec["prev_dea"] = p["dea"] if p else None
            rec["prev_macd_bar"] = p["macd_bar"] if p else None
    for thscode, rec in by_date[dates[0]].items():
        rec["prev_dea"], rec["prev_macd_bar"] = None, None
    print(f"数据就绪: {dates[0]} ~ {dates[-1]} · {len(dates)} 交易日 · {sum(len(d) for d in by_date.values()):,} 行"
          f"（MACD 真 EMA 已补算）")
    return by_date, dates, market_strong

# ---------------- 买入信号 ----------------
def find_w_bottom(closes, tol=0.05, min_gap=5, lookback=60):
    """检测 W 底（双重底）形态，返回 (颈线价, 右底价) 或 None。
    右底 = 最近 20 日内最低收盘；左底 = 右底之前至少 min_gap 日的最低收盘；
    两底接近（|L2-L1|/L1 ≤ tol）；颈线 = 两底之间最高收盘（须高于两底 ≥2% 形成反弹）；
    当前收盘 > 颈线 = 突破确认（形态成立，买入信号触发）。"""
    if closes is None or len(closes) < lookback:
        return None
    seq = closes[-lookback:]
    n = len(seq)
    r = 20
    r_seg = seq[n - r:]
    L2_idx = n - r + r_seg.index(min(r_seg))
    L2 = seq[L2_idx]
    if L2_idx < min_gap + 2:
        return None
    left = seq[:L2_idx - min_gap + 1]
    L1_idx = left.index(min(left))
    L1 = left[L1_idx]
    if L1 <= 0 or abs(L2 - L1) / L1 > tol:
        return None
    neck = max(seq[L1_idx:L2_idx + 1])
    if neck <= max(L1, L2) * 1.02:
        return None
    if seq[-1] <= neck:
        return None
    return neck, L2


def is_buy(strat, rec):
    sig = strat["buy_signal"]
    p = strat["params"]
    ma5, ma20 = rec["ma5"], rec["ma20"]
    if sig == "ma_cross":
        return (None not in (ma5, ma20, rec["prev_ma5"], rec["prev_ma20"])
                and ma5 > ma20 and rec["prev_ma5"] <= rec["prev_ma20"])
    if sig == "ma20_break":
        vr = rec["vol_ratio"]
        return (ma20 is not None and rec["close"] > ma20
                and (vr is None or vr >= p.get("vol_ratio", 1.2))
                and rec["prev_close2"] is not None and rec["prev_close2"] <= rec["prev_ma20"])
    if sig == "channel_break":
        return rec["prior20_high"] is not None and rec["close"] > rec["prior20_high"]
    if sig == "boll_break":
        return (rec["boll_upper"] is not None and rec["close"] > rec["boll_upper"]
                and rec["prev_boll_upper"] is not None and rec["prev_close2"] is not None
                and rec["prev_close2"] <= rec["prev_boll_upper"])
    if sig == "rsi_oversold":
        return rec["rsi14"] is not None and rec["rsi14"] < p.get("rsi_buy", 30)
    if sig == "new_low_rebound":
        return rec["prior60_low"] is not None and rec["low"] <= rec["prior60_low"] and rec["close"] > rec["open"]
    if sig == "new_high":
        return rec["prior120_high"] is not None and rec["high"] > rec["prior120_high"]
    if sig == "bull_retrace":
        dev = p.get("retrace_dev", 0.02)
        return rec["bull3"] and rec["ma20"] and abs(rec["close"] / rec["ma20"] - 1) <= dev
    if sig == "limit_low_open":
        return (rec["prev_is_limit_up"] == 1 and rec["prev_close"] and rec["open"] is not None
                and rec["open"] / rec["prev_close"] - 1 <= p.get("low_open_pct", -0.02))
    if sig == "streak_2":
        return rec["streak"] == p.get("streak", 2) and rec["bull"]
    # ==================== v3.4 新增：9 个经典短线策略 ====================
    # 1) KDJ 低位金叉（K 上穿 D 且处低位区）
    if sig == "kdj_golden":
        if None in (rec["kv"], rec["kd"], rec["prev_k"], rec["prev_d"]):
            return False
        return (rec["kv"] > rec["kd"] and rec["prev_k"] <= rec["prev_d"]
                and rec["kd"] <= p.get("kd_max", 35))
    # 2) MACD 金叉（DIF 上穿 DEA，可选零轴下/上）
    if sig == "macd_golden":
        if None in (rec["dif"], rec["dea"], rec["prev_dif"], rec["prev_dea"]):
            return False
        cross = rec["dif"] > rec["dea"] and rec["prev_dif"] <= rec["prev_dea"]
        if not cross:
            return False
        mode = p.get("macd_pos", "any")
        if mode == "below" and not (rec["dif"] < 0):
            return False
        if mode == "above" and not (rec["dif"] > 0):
            return False
        # 可选：要求放量确认
        if p.get("vol_min") and (rec["vol_ratio"] is None or rec["vol_ratio"] < p["vol_min"]):
            return False
        return True
    # 3) 向上跳空缺口 + 放量（缺口未回补）
    if sig == "gap_up":
        if rec["prev_close"] in (None, 0) or rec["open"] is None:
            return False
        gap = rec["open"] / rec["prev_close"] - 1
        if gap < p.get("gap_min", 0.02):
            return False
        # 缺口未回补：当日最低价须仍高于前日最高价（前日 high 用 prev_close 之外的近似：
        # 用当日 low > prev_close 作为保守未回补判定，因 SQL 未取 prev_high）
        if p.get("keep_gap", True) and rec["low"] <= rec["prev_close"]:
            return False
        if p.get("vol_min") and (rec["vol_ratio"] is None or rec["vol_ratio"] < p["vol_min"]):
            return False
        return True
    # 4) 缩量回踩 MA5/MA10（多头排列中的低吸）
    if sig == "shrink_pullback":
        if rec["ma5"] is None or rec["ma10"] is None:
            return False
        if not rec["bull"]:
            return False
        near = p.get("near_dev", 0.015)
        touch = (abs(rec["close"] / rec["ma5"] - 1) <= near) or (abs(rec["close"] / rec["ma10"] - 1) <= near)
        if not touch:
            return False
        # 缩量：量比 < 阈值
        if rec["vol_ratio"] is None or rec["vol_ratio"] > p.get("vol_max", 0.9):
            return False
        return True
    # 5) 首阴低吸（强势股高位首根阴线，博反抽）
    if sig == "first_red_pullback":
        if rec["close"] >= rec["open"]:      # 当日须收阴
            return False
        if (rec["prev_cnt_up"] or 0) < p.get("min_up", 3):   # 昨日（转阴之前）仍是长阳线
            return False
        if not rec["bull"]:
            return False
        # 必须是"首阴"：前一天仍是阳线（cnt_up>=min_up 已隐含，此处再确认昨日 not 阴）
        if rec["prev_open"] is None or rec["prev_close"] is None:
            return False
        if p.get("limit_streak", True) and rec["streak"] > 0:
            return False
        return True
    # 6) 均线粘合突破（MA5/10/20/p>60 高度收敛后收盘向上突破）
    if sig == "ma_squeeze_break":
        vals = [rec.get("ma5"), rec.get("ma10"), rec.get("ma20"), rec.get("ma60")]
        if any(v is None or v <= 0 for v in vals):
            return False
        mx, mn = max(vals), min(vals)
        if (mx - mn) / mn > p.get("squeeze", 0.03):
            return False
        # 突破：收盘高于全部均线，且前一日收盘不高于最长均线
        if not (rec["close"] > mx):
            return False
        pmax = max(v for v in [rec.get("prev_ma5"), rec.get("prev_ma10"),
                               rec.get("prev_ma20")] if v is not None)
        if rec["prev_close2"] is None or rec["prev_close2"] > pmax:
            return False
        if p.get("vol_min") and (rec["vol_ratio"] is None or rec["vol_ratio"] < p["vol_min"]):
            return False
        return True
    # 7) 二阳接力/连续阳线（放量连阳，短线接力）
    if sig == "consec_up":
        if rec["cnt_up"] < p.get("min_up", 3):
            return False
        if rec["vol_ratio"] is None or rec["vol_ratio"] < p.get("vol_min", 1.2):
            return False
        if p.get("need_bull") and not rec["bull"]:
            return False
        return True
    # 8) 强势股回踩 20 日线不破（趋势中继）
    if sig == "strong_pullback_ma20":
        if rec["ma20"] is None or rec["bias20"] is None:
            return False
        if rec["cnt_up"] > p.get("max_up", 0):  # 当日不宜已连阳多日
            return False
        dev = p.get("dev", 0.02)
        if not (-dev <= rec["bias20"] <= dev):   # 贴近 MA20 ±dev
            return False
        # 须仍在中长期上（MA20 上行 + 收盘在 MA60 上方）
        if rec["ma60"] is None or rec["close"] < rec["ma60"]:
            return False
        # 缩量回踩
        if rec["vol_ratio"] is None or rec["vol_ratio"] > p.get("vol_max", 1.0):
            return False
        return True
    # 9) 涨停基因回踩（近期有涨停、回踩不破关键均线）
    if sig == "limit_gene_pullback":
        if not rec["bull3"]:
            return False
        if rec["bias20"] is None or rec["bias20"] > p.get("max_bias", 0.06):
            return False
        if rec["vol_ratio"] is None or rec["vol_ratio"] > p.get("vol_max", 1.0):
            return False
        if rec["close"] < rec["ma20"] * (1 - p.get("break_dev", 0.01)):
            return False
        return True
    # 10) 布林下轨超卖低吸（触及下轨 + 收阳止跌）
    if sig == "boll_lower_buy":
        if rec["boll_lower"] is None:
            return False
        if rec["low"] > rec["boll_lower"]:
            return False
        if rec["close"] <= rec["open"]:
            return False
        if p.get("rsi_max") and (rec["rsi14"] is None or rec["rsi14"] > p["rsi_max"]):
            return False
        return True
    # 11) RSI 超卖二次探底（RSI 回升且前值更低）
    if sig == "rsi_double_bottom":
        if None in (rec["rsi14"], rec["prev_rsi14"]):
            return False
        return (rec["prev_rsi14"] < p.get("rsi_low", 30) and rec["rsi14"] >= rec["prev_rsi14"]
                and rec["rsi14"] < p.get("rsi_buy", 40))
    # 12) 长下影线止跌（锤子线）
    if sig == "hammer":
        if rec["prev_close"] in (None, 0):
            return False
        rng = rec["high"] - rec["low"]
        if rng <= 0:
            return False
        lower = min(rec["open"], rec["close"]) - rec["low"]
        body = abs(rec["close"] - rec["open"])
        if lower / rng < p.get("shadow_ratio", 0.5):
            return False
        if body / rng > p.get("body_max", 0.35):
            return False
        if p.get("need_below_ma20") and rec["ma20"] and rec["close"] > rec["ma20"]:
            return False
        return True
    return False

# ---------------- 卖出信号（返回 reason 或 None） ----------------
def check_sell(strat, rec, position, consec_loss, gain):
    sig = strat["sell_signal"]
    p = strat["params"]
    day_ret = rec["ret"] if rec["ret"] is not None else 0.0
    # 通用止损（所有策略）
    if day_ret < p.get("stop_single", -0.07):
        return "单日跌超" + f"{abs(p.get('stop_single', -0.07))*100:.0f}%止损"
    if rec["close"] < rec["prev_close"]:
        consec_loss.append(day_ret)
        if sum(consec_loss) < p.get("stop_consec_sum", -0.10):
            return "连续亏损累计超10%"
    else:
        consec_loss.clear()
    # 策略特定卖出
    if sig == "ma_dead" and rec["ma5"] is not None and rec["ma20"] is not None and rec["ma5"] < rec["ma20"]:
        return "MA5死叉MA20"
    if sig in ("close_below_ma20",) and rec["ma20"] is not None and rec["close"] < rec["ma20"]:
        return "跌破MA20"
    if sig == "close_below_ma10" and rec["ma10"] is not None and rec["close"] < rec["ma10"]:
        return "跌破MA10"
    if sig == "channel_exit" and rec["prior10_low"] is not None and rec["close"] < rec["prior10_low"]:
        return "跌破唐奇安下轨"
    if sig == "boll_mid" and rec["boll_lower"] is not None and rec["close"] < rec["ma20"]:
        return "跌破布林中轨"
    if sig == "w_fail":
        wl = position.get("w_low")
        if wl is not None and rec["close"] < wl:
            return "跌破W底右底止损"
        wn = position.get("w_neck")
        if wn is not None and rec["close"] < wn:
            return "跌回颈线下方·形态失败"
    if sig == "rsi_overbought":
        if rec["rsi14"] is not None and rec["rsi14"] > p.get("rsi_sell", 70):
            return "RSI超买"
        if p.get("take_profit") and gain >= p["take_profit"]:
            return f"止盈+{p['take_profit']*100:.0f}%"
    if sig == "kdj_dead":
        if None not in (rec["kv"], rec["kd"], rec["prev_k"], rec["prev_d"]) \
                and rec["kv"] < rec["kd"] and rec["prev_k"] >= rec["prev_d"]:
            return "KDJ死叉"
    if sig == "macd_dead":
        if None not in (rec["dif"], rec["dea"], rec["prev_dif"], rec["prev_dea"]) \
                and rec["dif"] < rec["dea"] and rec["prev_dif"] >= rec["prev_dea"]:
            return "MACD死叉"
    if sig == "gap_fill" and rec["prev_close"] and rec["close"] < rec["prev_close"]:
        return "缺口回补·跌破前收"
    if sig == "close_below_ma5" and rec["ma5"] is not None and rec["close"] < rec["ma5"]:
        return "跌破MA5"
    if sig == "close_below_ma60" and rec["ma60"] is not None and rec["close"] < rec["ma60"]:
        return "跌破MA60"
    if sig == "bear_engulf":
        if rec["prev_open"] is None or rec["prev_close"] is None:
            pass
        elif rec["close"] < rec["open"] and rec["open"] > rec["prev_close"] \
                and rec["close"] < rec["prev_open"]:
            return "阴包阳·反转离场"
    if sig == "macd_bar_shrink" and rec["prev_macd_bar"] is not None and rec["macd_bar"] is not None:
        if rec["macd_bar"] < rec["prev_macd_bar"] and rec["macd_bar"] > 0 and rec["dif"] > rec["dea"]:
            return "MACD红柱缩短·动能衰竭"
    if p.get("take_profit") and sig != "rsi_overbought" and gain >= p["take_profit"]:
        return f"止盈+{p['take_profit']*100:.0f}%"
    if p.get("max_hold") and position["days"] >= p["max_hold"]:
        return f"持有{p['max_hold']}天到期"
    return None

def run_strategy(strat, by_date, dates, market_strong, hs_ret):
    sid, name, p = strat["id"], strat["name"], strat["params"]
    nmap = globals().get("_NAME_MAP") or {}
    # 候选索引（当日满足买入信号的股票）
    daily_cands = {}
    need_wb = strat["buy_signal"] == "w_bottom"
    hist, prev_break, w_info = ({}, {}, {}) if need_wb else (None, None, None)
    for d, day in by_date.items():
        if need_wb:
            cands = []
            for thscode, rec in day.items():
                seq = hist.setdefault(thscode, [])
                seq.append(rec["close"])
                wb = find_w_bottom(seq, p.get("tol", 0.05), p.get("min_gap", 5), p.get("lookback", 60))
                if wb is None:
                    continue
                neck, L2 = wb
                if thscode in prev_break and neck <= prev_break[thscode] * 1.01:
                    continue  # 同一形态已触发过（颈线未显著抬高），避免反复买入
                prev_break[thscode] = neck
                w_info[thscode] = (neck, L2)
                cands.append(rec)
            if cands:
                daily_cands[d] = cands
        else:
            cands = [rec for rec in day.values() if is_buy(strat, rec)]
            if strat["buy_signal"] == "streak_2" and p.get("market_strong"):
                if market_strong.get(str(d), False):
                    daily_cands[d] = cands
            else:
                if cands:
                    daily_cands[d] = cands
    # 事件循环
    trades, nav_curve, position, plan, sell_pending, consec_loss = [], [], None, None, None, []
    cash_nav, daily_close_nav = 1.0, 1.0
    for d in dates:
        day = by_date[d]
        if sell_pending:
            ticker, reason, sig_d = sell_pending
            bar = day.get(ticker)
            if bar and bar["open"] and bar["prev_close"]:
                sell_price = bar["open"]
                ret_t = (sell_price - position["buy_price"]) / position["buy_price"] - CFG["fee_rate"]
                cash_nav *= (1 + ret_t)
                trades.append({
                    "ticker": ticker, "sel_date": position["sel_date"], "buy_date": position["buy_date"],
                    "buy_price": round(position["buy_price"], 3), "sell_date": d,
                    "signal_date": sig_d, "cand_cnt": position.get("cand_cnt"),
                    "sell_price": round(sell_price, 3), "ret": round(ret_t * 100, 2),
                    "days": position["days"], "reason": reason,
                    "equity": round(CFG["initial_capital"] * cash_nav, 2),
                    # 股票名称：优先用名称映射，缺失时回退代码（坑 41）
                    "name": nmap.get(ticker) or ticker,
                })
                position, consec_loss = None, []
            sell_pending = None
            daily_close_nav = cash_nav
            nav_curve.append((d, daily_close_nav))
            continue
        if position is None:
            if plan:
                ticker, sel_d, cand_cnt = plan
                plan = None
                bar = day.get(ticker)
                if bar is None or bar["open"] is None or bar["prev_close"] is None:
                    continue
                sel_close = by_date[sel_d][ticker]["close"]
                gap = bar["open"] / sel_close - 1 if sel_close else -1
                if strat["buy_signal"] == "streak_2" and gap < CFG["gap_threshold"]:
                    continue
                buy_price = bar["open"]
                position = {"ticker": ticker, "sel_date": sel_d, "buy_date": d, "buy_price": buy_price,
                            "days": 1, "cand_cnt": cand_cnt}
                if need_wb:
                    wn, wl = w_info.get(ticker, (None, None))
                    position["w_neck"] = wn
                    position["w_low"] = wl
                daily_close_nav = cash_nav
                nav_curve.append((d, daily_close_nav))
                continue
            else:
                cands = daily_cands.get(d, [])
                if cands:
                    pick = max(cands, key=lambda x: x["amount"] or 0)["thscode"]
                    plan = (pick, d, len(cands))
                daily_close_nav = cash_nav
                nav_curve.append((d, daily_close_nav))
                continue
        bar = day.get(position["ticker"])
        if bar is None:
            nav_curve.append((d, daily_close_nav))
            continue
        gain = (bar["close"] - position["buy_price"]) / position["buy_price"]
        if position["days"] == 1 and strat["sell_signal"] == "streak_sell":
            if bar["close"] < position["buy_price"]:
                sell_pending = (position["ticker"], "当日收阴·第3天开盘卖", d)
        else:
            reason = check_sell(strat, bar, position, consec_loss, gain)
            if reason:
                sell_pending = (position["ticker"], reason, d)
        position["days"] += 1
        daily_close_nav = cash_nav * (bar["close"] / position["buy_price"])
        nav_curve.append((d, daily_close_nav))
    # 统计
    n = len(trades)
    wins = [t for t in trades if t["ret"] > 0]
    loss = [t for t in trades if t["ret"] <= 0]
    win_rate = len(wins) / n * 100 if n else 0
    avg_win = sum(t["ret"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["ret"] for t in loss) / len(loss) if loss else 0
    total_ret = (nav_curve[-1][1] - 1) * 100 if nav_curve else 0
    peak, mdd = 1.0, 0.0
    for _, nv in nav_curve:
        if nv > peak:
            peak = nv
        dd = nv / peak - 1
        if dd < mdd:
            mdd = dd
    ann = ((nav_curve[-1][1]) ** (252 / max(len(nav_curve), 1)) - 1) * 100 if nav_curve else 0
    result = {
        "strategy": {"id": sid, "name": name, "family": strat["family"]},
        "dates": dates[0], "dates_end": dates[-1], "days": len(dates),
        "trades": trades, "n": n, "win_rate": round(win_rate, 1),
        "avg_win": round(avg_win, 2), "avg_loss": round(avg_loss, 2),
        "profit_loss_ratio": round(abs(avg_win / avg_loss), 2) if avg_loss else None,
        "total_ret": round(total_ret, 2), "mdd": round(mdd * 100, 2), "ann": round(ann, 2),
        "hs_ret": round(hs_ret, 2), "nav_curve": nav_curve,
        "reason_cnt": {r: sum(1 for t in trades if t["reason"] == r) for r in set(t["reason"] for t in trades)},
        "initial_capital": CFG["initial_capital"],
    }
    print(f"[{sid}] {name}: {n}笔 胜率{result['win_rate']}% 盈亏比{result['profit_loss_ratio']} 总收益{result['total_ret']:+.1f}% 回撤{result['mdd']:.1f}%")
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default=None, help="strategy id 或 all")
    ap.add_argument("--all", action="store_true", help="跑全部策略")
    ap.add_argument("--universe", default=None, help="限定标的池: thscode,thscode,...（默认全市场）")
    ap.add_argument("--tag", default="", help="输出文件后缀标签（如股票名），防止多标的池结果互相覆盖")
    ap.add_argument("--parquet", default=None, help="自定义回测数据 parquet（默认 A 股 bt_qfq_1y.parquet；ETF/指数等自定义数据源用）")
    ap.add_argument("--force", action="store_true", help="跳过数据就绪检查（DuckDB 初始化/数据新鲜度），强制回测")
    args = ap.parse_args()
    if args.parquet:
        PARQUET_OVERRIDE = args.parquet if os.path.isabs(args.parquet) else os.path.join(BASE, args.parquet)
        if not os.path.exists(PARQUET_OVERRIDE):
            print(f"parquet 不存在: {PARQUET_OVERRIDE}"); return
        globals()["PARQUET"] = PARQUET_OVERRIDE
    if not check_data_readiness(force=args.force):
        return
    specs = json.load(open(STRATEGIES, encoding="utf-8"))
    print(f"策略定义: {STRATEGIES}（{len(specs['strategies'])} 个）")
    print(f"产物目录: {OUT}")
    # 股票名称映射（坑 41）：交易明细「股票」列须显示名称+代码，缺映射会退化成纯代码
    globals()["_NAME_MAP"] = ensure_name_map()
    if globals()["_NAME_MAP"]:
        print(f"名称映射: {NAME_MAP}（{len(globals()['_NAME_MAP'])} 条）")
    strategies = specs["strategies"]
    hs = json.load(open(HS300, encoding="utf-8"))["data"]["item"]
    hs_ret = (hs[-1]["close_price"] / hs[0]["close_price"] - 1) * 100
    by_date, dates, market_strong = load_data()
    # 限定标的池（默认全市场）
    uni_label = "全市场"
    if args.universe:
        uni = set(x.strip() for x in args.universe.split(","))
        by_date = {d: {k: v for k, v in day.items() if k in uni} for d, day in by_date.items()}
        by_date = {d: day for d, day in by_date.items() if day}
        dates = sorted(by_date.keys())
        uni_label = args.universe
    print(f"标的池: {uni_label} · {len(dates)} 交易日")
    sel = strategies if (args.all or args.strategy in (None, "all")) else \
          [s for s in strategies if s["id"] == args.strategy]
    if not sel:
        print("strategy not found:", args.strategy); return
    tag = f"_{args.tag}" if args.tag else ""
    summary = {}
    for s in sel:
        res = run_strategy(s, by_date, dates, market_strong, hs_ret)
        res["universe"] = uni_label
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, f"bt_result_{s['id']}{tag}.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False)
        summary[s["id"]] = {
            "name": s["name"], "family": s["family"],
            "n": res["n"], "win_rate": res["win_rate"], "avg_win": res["avg_win"],
            "avg_loss": res["avg_loss"], "pl": res["profit_loss_ratio"],
            "total_ret": res["total_ret"], "mdd": res["mdd"], "ann": res["ann"], "hs_ret": res["hs_ret"],
        }
    with open(os.path.join(OUT, f"bt_all{tag}.json"), "w", encoding="utf-8") as f:
        json.dump({"range": f"{dates[0]}~{dates[-1]}", "days": len(dates), "universe": uni_label, "strategies": summary}, f, ensure_ascii=False, indent=1)
    print("\n全部完成 -> bt_all" + tag + ".json")

if __name__ == "__main__":
    main()
