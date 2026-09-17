# -*- coding: utf-8 -*-
"""指标与 K 线口径的**唯一实现**（供各能力脚本 import，别再各写一遍）。

为什么要它
----------
短线指标/窗口/解析口径散落在若干脚本里各写一遍，很容易「同名不同算法」：
MA 用简单均值还是 EMA、RSI 用 Wilder 还是 SMA、布林用样本还是总体标准差、量比含不含当日、
「近1年」是 252 个交易日还是 365 个自然日……一旦不一致，**报告之间互相打架且看不出谁错**。
本模块把口径固定下来，脚本只调它；改口径只改这里（口径由来见 references/CLI与数据坑清单.md 坑 35/61）。

口径约定（与回测引擎 SQL 保持一致）
----------------------------------
- MA   ：**简单均值**（`np.mean(close[-n:])`）
- RSI14：**Wilder 平滑**（首值=前 14 日涨跌幅均值；此后 `(prev*(n-1)+cur)/n`；全跌 avg_loss=0 → 100）
- MACD ：EMA12/EMA26/DEA9，`k=2/(n+1)`，初值取首收盘，柱 `(DIF-DEA)*2`
- BOLL ：MA20 ± 2σ，**样本标准差（ddof=1）**（与 DuckDB `stddev_samp` 一致）
- 量比 ：`今量 ÷ 前 5 日均量`（**不含当日**；与交易所「5 日同期分钟量」口径不同，报告须标「自算」）
- 近1年：**最后交易日回溯 252 个交易日**（坑 61）——不是自然年、也不是「喂了多少根」

用法
----
    from ths_indicators import load_bars, sma, rsi14, macd, boll_pctb, vol_ratio, window_52w, judge_short_term
    bars = load_bars("hist.json")           # 兼容本地/远端双结构 + date 转 str
    print(window_52w(bars))                 # {'start','end','n','hi','lo','chg'}
    print(judge_short_term(bars))           # 超买/超卖/中性 + 触发项

    python ths_indicators.py --selftest     # 公式自检
"""
from __future__ import annotations

import argparse
import json
import sys

W52_BARS = 252          # 近一年窗口（交易日）
RSI_N = 14
BOLL_N, BOLL_K = 20, 2.0
VOL_MA_N = 5


# --------------------------------------------------------------------------- #
# 数据装载
# --------------------------------------------------------------------------- #
def load_bars(path: str) -> list[dict]:
    """读 K 线 JSON，统一成 6 字段 dict 列表 [{date,open,high,low,close,volume}]。

    - 兼容两种结构（坑 10）：本地 `data`(list)+`date/close`；远端/ETF `data.item[]`+`date_ms/*_price`
    - `date` 一律转 **str**（坑 31：parquet 导出的 date 可能是 datetime.date，字符串比较会恒 False）
    - 丢弃多余字段（坑 56①：多余字段会进 JSON 甚至 SVG）
    """
    import datetime as _dt

    env = json.load(open(path, encoding="utf-8"))
    data = env.get("data", env)
    rows = data.get("item") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError(f"无法识别的 K 线结构：{list(data)[:6] if isinstance(data, dict) else type(data)}")

    out = []
    for b in rows:
        if "date_ms" in b or "close_price" in b:            # 远端/ETF 结构
            ms = b.get("date_ms")
            d = _dt.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d") if ms else str(b.get("date", ""))
            rec = {"date": d, "open": b.get("open_price"), "high": b.get("high_price"),
                   "low": b.get("low_price"), "close": b.get("close_price"), "volume": b.get("volume")}
        else:                                               # 本地结构
            rec = {"date": str(b.get("date")), "open": b.get("open"), "high": b.get("high"),
                   "low": b.get("low"), "close": b.get("close"), "volume": b.get("volume")}
        out.append({k: (round(v, 2) if k in ("open", "high", "low", "close") and isinstance(v, float) else v)
                    for k, v in rec.items()})
    return out


def dump_hist(bars: list[dict], path: str) -> None:
    """写出符合坑 56 要求的 HIST JSON：只留 6 字段、价格 round(x,2)、date 为 str。"""
    clean = [{k: (round(b[k], 2) if isinstance(b.get(k), float) else b.get(k))
              for k in ("date", "open", "high", "low", "close", "volume")} for b in bars]
    json.dump({"data": clean}, open(path, "w", encoding="utf-8"), ensure_ascii=False)


def last_n_bars(bars: list[dict], n: int = W52_BARS) -> list[dict]:
    """近一年窗口 = 最后交易日回溯 n 个交易日（坑 61）。不足则取全量。"""
    return bars[-n:] if len(bars) > n else bars


# --------------------------------------------------------------------------- #
# 指标（口径唯一来源）
# --------------------------------------------------------------------------- #
def sma(vals: list[float], n: int) -> list[float]:
    """简单均值（不足 n 根时用已有根数平均，与图表左端一致）。"""
    out = []
    for i in range(len(vals)):
        seg = vals[max(0, i - n + 1): i + 1]
        out.append(sum(seg) / len(seg))
    return out


def ema(vals: list[float], n: int) -> list[float]:
    """指数均值：k=2/(n+1)，初值取首值。"""
    k = 2 / (n + 1)
    out, prev = [], None
    for v in vals:
        prev = v if prev is None else v * k + prev * (1 - k)
        out.append(prev)
    return out


def rsi14(closes: list[float], n: int = RSI_N) -> float:
    """RSI(n)，Wilder 平滑。不足 n+1 根返回 None；全跌（avg_loss=0）返回 100.0。"""
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    ag, al = sum(gains) / n, sum(losses) / n
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (n - 1) + max(d, 0.0)) / n
        al = (al * (n - 1) + max(-d, 0.0)) / n
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def macd(closes: list[float]) -> dict:
    """MACD(12,26,9)：返回末值 dif/dea/hist。"""
    if len(closes) < 2:
        return {"dif": None, "dea": None, "hist": None}
    e12, e26 = ema(closes, 12), ema(closes, 26)
    dif = [a - b for a, b in zip(e12, e26)]
    dea = ema(dif, 9)
    return {"dif": dif[-1], "dea": dea[-1], "hist": (dif[-1] - dea[-1]) * 2}


def boll_pctb(closes: list[float], n: int = BOLL_N, k: float = BOLL_K) -> float:
    """布林 %B = (close-下轨)/(上轨-下轨)*100，样本标准差 ddof=1（与 SQL stddev_samp 一致）。"""
    if len(closes) < n:
        return None
    seg = closes[-n:]
    ma = sum(seg) / n
    var = sum((v - ma) ** 2 for v in seg) / (n - 1)
    sd = var ** 0.5
    up, lo = ma + k * sd, ma - k * sd
    return 100.0 if up == lo else (closes[-1] - lo) / (up - lo) * 100


def vol_ratio(vols: list[float], n: int = VOL_MA_N) -> float:
    """量比 = 今量 ÷ 前 n 日均量（不含当日）。口径与交易所不同，报告须标「自算」。"""
    if len(vols) < n + 1:
        return None
    prev = vols[-(n + 1):-1]
    base = sum(prev) / n
    return None if not base else vols[-1] / base


def dist_ma_pct(closes: list[float], n: int = 20) -> float:
    """乖离率 = (收盘 - MAn) / MAn * 100。"""
    ma = sma(closes, n)[-1]
    return None if not ma else (closes[-1] - ma) / ma * 100


# --------------------------------------------------------------------------- #
# 近一年窗口（坑 61）
# --------------------------------------------------------------------------- #
def window_52w(bars: list[dict], n: int = W52_BARS) -> dict:
    """近一年口径：{start,end,n,hi,lo,chg}。hi/lo 取 high/low，chg 取首尾**收盘**。"""
    win = last_n_bars(bars, n)
    cs = [b["close"] for b in win]
    return {"start": win[0]["date"], "end": win[-1]["date"], "n": len(win),
            "hi": max(b["high"] for b in win), "lo": min(b["low"] for b in win),
            "chg": (cs[-1] / cs[0] - 1) * 100 if cs and cs[0] else None,
            "full_window": len(bars) >= n}


# --------------------------------------------------------------------------- #
# 短线判读（阈值口径，坑 35）
# --------------------------------------------------------------------------- #
def judge_short_term(bars: list[dict]) -> dict:
    """按统一阈值给短线状态：RSI>70 + %B>100 + 乖离MA20>8% = 超买；%B<0 或 RSI<30 = 超卖。"""
    closes = [b["close"] for b in bars]
    vols = [b["volume"] for b in bars]
    r, pb, dm = rsi14(closes), boll_pctb(closes), dist_ma_pct(closes, 20)
    hits = []
    if r is not None and r > 70:
        hits.append(f"RSI14={r:.1f}>70")
    if pb is not None and pb > 100:
        hits.append(f"%B={pb:.1f}>100")
    if dm is not None and dm > 8:
        hits.append(f"乖离MA20={dm:+.1f}%>8%")
    if len(hits) >= 3:
        state = "超买"
    elif (pb is not None and pb < 0) or (r is not None and r < 30):
        state = "超卖"
    else:
        state = "中性"
    return {"state": state, "hits": hits, "rsi14": r, "pctb": pb,
            "dist_ma20": dm, "vol_ratio": vol_ratio(vols), "macd": macd(closes),
            "w52": window_52w(bars)}


# --------------------------------------------------------------------------- #
def selftest() -> int:
    ok = True

    def chk(name, got, want, tol=1e-6):
        nonlocal ok
        good = (abs(got - want) <= tol) if isinstance(want, (int, float)) and isinstance(got, (int, float)) else got == want
        print(f"  {'✅' if good else '❌'} {name}: {got} (期望 {want})")
        ok = ok and good

    print("=" * 72)
    print("ths_indicators 自检")
    print("=" * 72)
    chk("sma([1..5], 5)", sma([1, 2, 3, 4, 5], 5)[-1], 3.0)
    chk("sma 不足窗口用已有均值", sma([2, 4], 5)[-1], 3.0)
    chk("ema 首值=首输入", ema([10, 20], 3)[0], 10.0)
    chk("ema(3) 第二步 10*0.5+20*0.5", ema([10, 20], 3)[-1], 15.0)
    # RSI：连续上涨 15 根 → 100
    chk("rsi 全涨=100", rsi14(list(range(1, 17))), 100.0)
    # RSI：全跌 → 0
    chk("rsi 全跌=0", round(rsi14(list(range(17, 1, -1))), 6), 0.0)
    chk("rsi 数据不足", rsi14([1, 2, 3]), None)
    # 布林：常数序列 σ=0 → 上下轨相同 → 返回 100
    chk("boll 常数序列", boll_pctb([5.0] * 20), 100.0)
    chk("boll 数据不足", boll_pctb([1.0] * 5), None)
    # 量比：今量 10，前 5 日均量 5 → 2.0
    chk("vol_ratio=10/5", vol_ratio([5, 5, 5, 5, 5, 10]), 2.0)
    chk("vol_ratio 数据不足", vol_ratio([1, 2, 3]), None)
    # 乖离率：19 根 10 + 1 根 11 → MA20=(19*10+11)/20=10.05，乖离=(11-10.05)/10.05*100
    chk("dist_ma_pct(19×10+1×11)", round(dist_ma_pct([10.0] * 19 + [11.0]), 4),
        round((11 - 10.05) / 10.05 * 100, 4))
    # 乖离率：恒定 10 后收 11（MA 仍是 10.05）→ 同上；恒定序列 → 0
    chk("dist_ma_pct 恒定序列=0", dist_ma_pct([10.0] * 20), 0.0)
    # 252 窗口：300 根，末 252 根首尾
    bars = [{"date": f"d{i:04d}", "open": 1.0, "high": 2.0 + i, "low": 0.5, "close": 1.0 + i,
             "volume": 100} for i in range(300)]
    w = window_52w(bars)
    chk("52周窗口根数", w["n"], 252)
    chk("52周窗口起点=第49根", w["start"], "d0048")
    chk("52周窗口终点", w["end"], "d0299")
    chk("52周涨跌=(300/49-1)*100", round(w["chg"], 4), round((300 / 49 - 1) * 100, 4))
    chk("52周高=末根high", w["hi"], 2.0 + 299)
    chk("不足252标记", window_52w(bars[:100])["full_window"], False)
    # round(2) 落盘
    import os
    import tempfile
    p = os.path.join(tempfile.mkdtemp(), "h.json")
    dump_hist([{"date": "2026-09-17", "open": 1.23456, "high": 2.0, "low": 1.0,
                "close": 1.5, "volume": 1, "ticker": "x"}], p)
    got = json.load(open(p, encoding="utf-8"))["data"][0]
    chk("dump_hist 字段数=6", len(got), 6)
    chk("dump_hist 已 round(2)", got["open"], 1.23)
    print(f"\n  {'全部通过 ✅' if ok else '有失败项 ❌'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="指标与 K 线口径的唯一实现")
    ap.add_argument("--hist", help="K 线 JSON 路径：打印全部口径指标")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.hist:
        bars = load_bars(a.hist)
        print(json.dumps(judge_short_term(bars), ensure_ascii=False, indent=2, default=str))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
