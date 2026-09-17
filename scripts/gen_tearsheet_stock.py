# -*- coding: utf-8 -*-
"""A股个股速览卡 HTML 生成器（v5.2 通用模板）
用途：将单只 A 股的全部研究信息渲染为单页 HTML 速览卡。
能力点：价格Hero / 当日行情+K线标注 / 估值主卡+副卡(含解释) / 财务指标4卡 /
       近5年营收净利柱状图(支持负值) / 年报·最新报告期·资产负债3卡 /
       近1年走势图(MA20+MACD+KDJ副图) / 现金流+分红双卡
模板约定：
  1. 本文件是【模板】——使用前必须将 CONFIG 与下方各数据字典替换为目标标的数据
  2. 数据获取方式：先加载 hithink-finance skill，用 CLI 拉取后填入（见 SKILL.md 工作流）
  3. 报告期参数化：CONFIG.report_label/report_hint 驱动，年报/中报/一季报通用
  4. 百分比口径：所有百分数指标值按服务端口径直接展示（不乘 100）
  5. 输出命名：{comp_name}_{date 去掉连字符}.html
数据源: hithink-finance CLI v0.1.5（远端快照 + 本地前复权日K）
"""
import json, os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
HIST = os.path.join(BASE, ".workbuddy", "output", "htfz_history.json")

# ================= 通用配置 =================
CONFIG = {
    "comp_name": "航天发展", "comp_short": "航天", "thscode": "000547.SZ",
    "exchange": "深市主板", "sector": "国防军工", "sector_desc": "军工电子 / 电子蓝军 / 指控通信",
    "sector_icon": "🛰️",
    "biz": "电子蓝军、指控通信、电磁安防和发电设备；网络信息安全、数据采集分析、数据保护及安全存储、政务管理信息化",
    "intro": ("航天工业发展股份有限公司（航天发展）成立于1993年，同年11月于深交所上市，是中国航天科工集团控股的央企上市公司，"
              "以军用产业、军民融合产业为主要业务板块，聚焦电子蓝军、指控通信、电磁安防、网络信息安全四大产业，"
              "旗下拥有南京长峰、重庆金美通信、航天新通等子公司，是电子信息领域核心供应商。"),
    "intro_tags": ["央企·航天科工", "成立1993年", "上市1993年", "军工电子核心供应商"],
    "report_label": "2026 中报（累计）",
    "report_hint": "2026 中报 (2026-2) · 财务指标为 2026 一季报口径",
    "rpt_rev_lab": "营业收入 (H1累计)", "rpt_np_lab": "归母净利 (H1累计)", "rpt_eps_lab": "EPS (H1累计)",
    "date": "2026-08-21", "weekday": "周五", "xd": False, "div_amt": 0.0,
    "quote_date": "2026-08-21",
}
SNAP = {"last": 13.88, "chg": 0.02, "pct": 0.14, "open": 13.70, "high": 13.98,
        "low": 13.58, "prev": 13.86, "vol": 45587339, "turnover": 629715060}
VAL = [("PE (TTM)", -19.23, "滚动12个月每股收益为负（亏损中），PE 为负值不具参考性，需结合 PB/PS 判断"),
       ("PE (MRQ)", -49.62, "最近一期报告盈利为负，PE 无意义，反映公司当前处于亏损状态"),
       ("PB (MRQ)", 6.06, "股价/每股净资产，当前高于1，未破净"),
       ("PS (TTM)", 7.66, "市值/营收，亏损公司常参考 PS 估值"),
       ("PCF (TTM)", 58.13, "市值/经营现金流，现金流角度估值")]
IND = {
    "profit": [("加权ROE", "-2.88%"), ("扣非加权ROE", "-32.60%"), ("毛利率", "7.92%"), ("净利率", "-20.05%"), ("总资产净利率", "-1.41%")],
    "growth": [("营业收入同比", "+118.36%"), ("营业利润同比", "+43.15%"), ("归母净利同比", "+39.16%"), ("总资产同比", "-7.99%")],
    "solvency": [("资产负债率", "47.96%"), ("流动比率", "1.43"), ("速动比率", "1.06"), ("利息保障倍数", "[MISSING]")],
    "oper": [("总资产周转率", "0.07"), ("存货周转率", "0.46"), ("应收账款周转率", "0.35"), ("经营现金流/营收", "-37.15%")],
}
INC_Y = [(2021, 42.25, 6.28, 0.39), (2022, 35.64, 0.33, 0.02),
         (2023, 18.63, -19.24, -1.20), (2024, 18.69, -16.73, -1.05),
         (2025, 25.01, -13.09, -0.82)]
BS = {"assets": 82.29, "debt": 38.74, "equity": 43.55, "cash": 13.38,
      "dr": 47.96, "cr": 1.43, "qr": 1.06}
CF = [(2023, -3.06, 0.55, 1.73), (2024, 1.17, 3.92, -3.34), (2025, 3.72, 1.35, -1.32)]
CF_2025 = {"capex": 0.40, "div": 0.31, "net": 3.77}
DIVS = [("2023-06-30", 0.0351), ("2022-07-01", 0.024), ("2021-07-08", 0.035),
        ("2020-06-30", 0.088), ("2017-06-18", 0.055), ("2016-06-07", 0.045)]
RPT = {"rev": 10.84, "np": -2.24, "eps": -0.14, "rev_yoy": "+57.33%", "np_yoy": "减亏40.7%"}
FY25 = {"rev": 25.01, "cost": 25.54, "gp": "-2.12%", "op": -14.56, "np": -13.09, "eps": "-0.82 元"}
DIV_SUM = sum(d[1] for d in DIVS[:2])
DIV_YIELD = DIV_SUM / SNAP["last"] * 100
amp = (SNAP["high"] - SNAP["low"]) / SNAP["prev"] * 100

FY_LABEL = '2025 年报'
CF_DIV_HINT = '现金流量：年度亿元 · 分红：近6次除息'

# ================= 历史日K =================
with open(HIST, "r", encoding="utf-8") as f:
    bars = json.load(f)["data"]
dates = [b["date"] for b in bars]
closes = [b["close"] for b in bars]
highs = [b["high"] for b in bars]
lows = [b["low"] for b in bars]
vols = [b["volume"] for b in bars]
hi_52 = max(highs)
lo_52 = min(lows)
chg_52 = (closes[-1] / closes[0] - 1) * 100
n = len(bars)

# ---------- 技术指标 ----------
def ema(vals, period):
    k = 2 / (period + 1)
    out, prev = [], None
    for v in vals:
        prev = v if prev is None else v * k + prev * (1 - k)
        out.append(prev)
    return out

ema12 = ema(closes, 12)
ema26 = ema(closes, 26)
dif = [a - b for a, b in zip(ema12, ema26)]
dea = ema(dif, 9)
macd_hist = [2 * (d - e) for d, e in zip(dif, dea)]

def sma(vals, period):
    out, prev = [], None
    for v in vals:
        prev = v if prev is None else (prev * (period - 1) + v) / period
        out.append(prev)
    return out

rsv = []
for i in range(n):
    lo9 = min(lows[max(0, i-8):i+1])
    hi9 = max(highs[max(0, i-8):i+1])
    rsv.append(50.0 if hi9 == lo9 else (closes[i] - lo9) / (hi9 - lo9) * 100)
k_arr = sma(rsv, 3)
d_arr = sma(k_arr, 3)
j_arr = [3 * k - 2 * d for k, d in zip(k_arr, d_arr)]

# ================= 最近一日 K 线 =================
kb = bars[-1]
k_prev = bars[-2]["close"] if n >= 2 else kb["open"]
k_up = kb["close"] >= kb["open"]
k_color = "#e5484d" if k_up else "#2fa36b"
KW, KH, KPAD = 300, 320, 46
kr = max(kb["high"], k_prev) - min(kb["low"], k_prev)
k_ymin = min(kb["low"], k_prev) - kr * 0.12
k_ymax = max(kb["high"], k_prev) + kr * 0.12
def kpy(v): return KPAD + (k_ymax - v) / (k_ymax - k_ymin) * (KH - 2 * KPAD)
cx = KW / 2 - 14
body_w = 34
hy, ly = kpy(kb["high"]), kpy(kb["low"])
oy, cy = kpy(kb["open"]), kpy(kb["close"])
body_top, body_h = min(oy, cy), abs(oy - cy) or 2
k_marks = [("最高", kb["high"], hy, "#c8102e"), ("收盘", kb["close"], cy, "#1f3a93"),
           ("开盘", kb["open"], oy, "#5b6470"), ("昨收", k_prev, kpy(k_prev), "#98a1ad"),
           ("最低", kb["low"], ly, "#2fa36b")]
k_mark_svg = []
for label, price, y, color in k_marks:
    k_mark_svg.append(f'<line x1="{cx-body_w/2-14:.1f}" y1="{y:.1f}" x2="{cx+body_w/2+14:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="4 3" opacity="0.75"/>')
    k_mark_svg.append(f'<text x="{cx+body_w/2+20:.1f}" y="{y+4:.1f}" font-size="11" fill="{color}" font-weight="600">{label} {price:.2f}</text>')
k_mark_svg = "".join(k_mark_svg)
kline_svg = f'''
<svg viewBox="0 0 {KW} {KH}" width="100%" style="min-width:260px" role="img" aria-label="最近交易日K线">
  <rect x="0" y="0" width="{KW}" height="{KH}" rx="12" fill="#fafbfc"/>
  <text x="{cx}" y="22" text-anchor="middle" font-size="12.5" font-weight="700" fill="#5b6470">{kb["date"]}</text>
  <line x1="{cx-body_w/2-14:.1f}" y1="{ly:.1f}" x2="{cx+body_w/2+14:.1f}" y2="{ly:.1f}" stroke="#e8eaee"/>
  <line x1="{cx:.1f}" y1="{ly:.1f}" x2="{cx:.1f}" y2="{hy:.1f}" stroke="{k_color}" stroke-width="1.6"/>
  <rect x="{cx-body_w/2:.1f}" y="{body_top:.1f}" width="{body_w}" height="{body_h:.1f}" rx="2" fill="{k_color}"/>
  {k_mark_svg}
  <text x="{cx}" y="{KH-14}" text-anchor="middle" font-size="11" fill="#98a1ad">{"上涨" if k_up else "下跌"} · 红涨绿跌</text>
</svg>'''

# ================= 走势图 =================
W, HP, HV, HM, HK, PAD = 880, 210, 76, 92, 92, 52
y_min, y_max = min(closes) * 0.965, max(closes) * 1.02
def px(i): return PAD + i * (W - 2 * PAD) / (n - 1)
def py(v): return HP + 16 - (v - y_min) / (y_max - y_min) * (HP - 32)
vol_max = max(vols)
pts = " ".join(f"{px(i):.1f},{py(c):.1f}" for i, c in enumerate(closes))
area_pts = f"{PAD},{HP+16} " + pts + f" {W-PAD},{HP+16}"
ma20 = []
for i in range(n):
    s = sum(closes[max(0, i-19):i+1]) / (i - max(0, i-19) + 1)
    ma20.append(s)
pts_ma = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(ma20))
vol_rects = []
for i, v in enumerate(vols):
    h = max(v / vol_max * (HV - 20), 1.0)
    up = closes[i] >= closes[i-1] if i > 0 else True
    color = "#e5484d" if up else "#2fa36b"
    vol_rects.append(f'<rect x="{px(i)-1.1:.1f}" y="{HP+22+(HV-20-h):.1f}" width="2.2" height="{h:.1f}" rx="0.5" fill="{color}" opacity="0.8"/>')
grid = []
for k in range(5):
    v = y_min + (y_max - y_min) * k / 4
    grid.append(f'<line x1="{PAD}" y1="{py(v):.1f}" x2="{W-PAD}" y2="{py(v):.1f}" stroke="#eef0f3" stroke-dasharray="3 4"/>')
    grid.append(f'<text x="{PAD-9}" y="{py(v)+4:.1f}" text-anchor="end" font-size="11" fill="#98a1ad">{v:.1f}</text>')
xt = []
for idx in [0, n//4, n//2, 3*n//4, n-1]:
    xt.append(f'<text x="{px(idx):.1f}" y="{HP+HV+HM+HK+16}" text-anchor="middle" font-size="11" fill="#98a1ad">{dates[idx]}</text>')
hi_y, lo_y = py(hi_52), py(lo_52)
hi_anno = f'<line x1="{PAD}" y1="{hi_y:.1f}" x2="{W-PAD}" y2="{hi_y:.1f}" stroke="#c9a227" stroke-width="1" stroke-dasharray="5 4" opacity="0.7"/>' \
          f'<rect x="{W-PAD-92}" y="{hi_y-18:.1f}" width="92" height="17" rx="8" fill="#c9a227"/><text x="{W-PAD-46}" y="{hi_y-6:.1f}" text-anchor="middle" font-size="10.5" fill="#fff">52周高 {hi_52:.2f}</text>'
lo_anno = f'<line x1="{PAD}" y1="{lo_y:.1f}" x2="{W-PAD}" y2="{lo_y:.1f}" stroke="#98a1ad" stroke-width="1" stroke-dasharray="5 4" opacity="0.6"/>' \
          f'<rect x="{PAD}" y="{lo_y+2:.1f}" width="96" height="17" rx="8" fill="#98a1ad"/><text x="{PAD+48}" y="{lo_y+14:.1f}" text-anchor="middle" font-size="10.5" fill="#fff">52周低 {lo_52:.2f}</text>'

macd_vals = dif + dea + macd_hist
mmax, mmin = max(macd_vals), min(macd_vals)
mspan = (mmax - mmin) or 1
def mpy(v, top): return top + 10 - (v - mmin) / mspan * (HM - 26)
macd_top = HP + 18 + HV + 6
pts_dif = " ".join(f"{px(i):.1f},{mpy(v, macd_top):.1f}" for i, v in enumerate(dif))
pts_dea = " ".join(f"{px(i):.1f},{mpy(v, macd_top):.1f}" for i, v in enumerate(dea))
macd_bars = []
zero_y = mpy(0, macd_top)
for i, v in enumerate(macd_hist):
    y0, y1 = mpy(v, macd_top), zero_y
    top_y, hh = min(y0, y1), abs(y1 - y0) or 0.6
    color = "#e5484d" if v >= 0 else "#2fa36b"
    macd_bars.append(f'<rect x="{px(i)-1.2:.1f}" y="{top_y:.1f}" width="2.4" height="{hh:.1f}" rx="0.5" fill="{color}" opacity="0.85"/>')
macd_svg = f'''
<text x="{PAD}" y="{macd_top-2}" font-size="11" font-weight="700" fill="#5b6470">MACD</text>
<text x="{PAD+44}" y="{macd_top-2}" font-size="10" fill="#1f3a93">DIF {dif[-1]:.2f}</text>
<text x="{PAD+112}" y="{macd_top-2}" font-size="10" fill="#e8a020">DEA {dea[-1]:.2f}</text>
<text x="{PAD+180}" y="{macd_top-2}" font-size="10" fill="#e5484d">柱 {macd_hist[-1]:.2f}</text>
<line x1="{PAD}" y1="{zero_y:.1f}" x2="{W-PAD}" y2="{zero_y:.1f}" stroke="#d8dce2" stroke-width="0.8"/>
<g>{''.join(macd_bars)}</g>
<polyline points="{pts_dif}" fill="none" stroke="#1f3a93" stroke-width="1.3"/>
<polyline points="{pts_dea}" fill="none" stroke="#e8a020" stroke-width="1.3"/>
'''

kdj_top = macd_top + HM + 6
def kpy2(v): return kdj_top + 10 - v / 100 * (HK - 26)
pts_k = " ".join(f"{px(i):.1f},{kpy2(v):.1f}" for i, v in enumerate(k_arr))
pts_d = " ".join(f"{px(i):.1f},{kpy2(v):.1f}" for i, v in enumerate(d_arr))
pts_j = " ".join(f"{px(i):.1f},{kpy2(v):.1f}" for i, v in enumerate(j_arr))
kdj_svg = f'''
<text x="{PAD}" y="{kdj_top-2}" font-size="11" font-weight="700" fill="#5b6470">KDJ</text>
<text x="{PAD+44}" y="{kdj_top-2}" font-size="10" fill="#1f3a93">K {k_arr[-1]:.1f}</text>
<text x="{PAD+112}" y="{kdj_top-2}" font-size="10" fill="#e8a020">D {d_arr[-1]:.1f}</text>
<text x="{PAD+180}" y="{kdj_top-2}" font-size="10" fill="#8b5cf6">J {j_arr[-1]:.1f}</text>
<line x1="{PAD}" y1="{kpy2(80):.1f}" x2="{W-PAD}" y2="{kpy2(80):.1f}" stroke="#eef0f3" stroke-dasharray="3 4"/>
<line x1="{PAD}" y1="{kpy2(50):.1f}" x2="{W-PAD}" y2="{kpy2(50):.1f}" stroke="#eef0f3" stroke-dasharray="3 4"/>
<line x1="{PAD}" y1="{kpy2(20):.1f}" x2="{W-PAD}" y2="{kpy2(20):.1f}" stroke="#eef0f3" stroke-dasharray="3 4"/>
<polyline points="{pts_j}" fill="none" stroke="#8b5cf6" stroke-width="1.1" opacity="0.85"/>
<polyline points="{pts_k}" fill="none" stroke="#1f3a93" stroke-width="1.3"/>
<polyline points="{pts_d}" fill="none" stroke="#e8a020" stroke-width="1.3"/>
'''

total_h = HP + 16 + HV + 12 + HM + 8 + HK + 22
chart_svg = f'''
<svg id="trendChart" viewBox="0 0 {W} {total_h}" width="100%" role="img" aria-label="近一年股价走势与技术指标">
  <defs>
    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1f3a93" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#1f3a93" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="{PAD}" y="0" width="{W-2*PAD}" height="{total_h-14}" rx="10" fill="#fafbfc"/>
  {''.join(grid)}
  <g>{''.join(vol_rects)}</g>
  <polygon points="{area_pts}" fill="url(#areaGrad)"/>
  <polyline points="{pts_ma}" fill="none" stroke="#e8a020" stroke-width="1.5" opacity="0.95"/>
  <polyline points="{pts}" fill="none" stroke="#1f3a93" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="{px(n-1):.1f}" cy="{py(closes[-1]):.1f}" r="4" fill="#fff" stroke="#1f3a93" stroke-width="2"/>
  {hi_anno}{lo_anno}
  {macd_svg}
  {kdj_svg}
  {''.join(xt)}
  <text x="{W-14}" y="{HP+10}" text-anchor="end" font-size="11" fill="#98a1ad">成交量(柱) · 红涨绿跌</text>
</svg>'''

# ================= 5年柱状图 =================
W2, H2, P2 = 880, 300, 64
all_vals = [r for _, r, _, _ in INC_Y] + [np_ for _, _, np_, _ in INC_Y]
vmax = max(all_vals) * 1.08
vmin = min(0, min(all_vals)) * 1.08  # 支持负值（亏损）
vrange = vmax - vmin
def bpx(i, half): return P2 + 44 + i * ((W2 - 2*P2 - 88) / 5) + (16 if half else 52)
def bpy(v): return H2 - 34 - ((v - vmin) / vrange) * (H2 - 80)
zero_y = bpy(0)
bars2 = []
for i, (y, r, np_, _) in enumerate(INC_Y):
    x1, x2 = bpx(i, 0), bpx(i, 1)
    y0_r, h_r = min(bpy(r), zero_y), max(abs(bpy(r) - zero_y), 1.5)
    y0_n, h_n = min(bpy(np_), zero_y), max(abs(bpy(np_) - zero_y), 1.5)
    np_color = "url(#barNp)" if np_ >= 0 else "#c9555a"  # 亏损用红
    bars2.append(f'<rect x="{x1:.1f}" y="{y0_r:.1f}" width="36" height="{h_r:.1f}" rx="2" fill="url(#barRev)"/>')
    bars2.append(f'<rect x="{x2:.1f}" y="{y0_n:.1f}" width="36" height="{h_n:.1f}" rx="2" fill="{np_color}"/>')
    ty_r = bpy(r) - 7 if r >= 0 else bpy(r) + 15
    ty_n = bpy(np_) - 7 if np_ >= 0 else bpy(np_) + 15
    bars2.append(f'<text x="{x1+18:.1f}" y="{ty_r:.1f}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#1f3a93">{r:.0f}</text>')
    bars2.append(f'<text x="{x2+18:.1f}" y="{ty_n:.1f}" text-anchor="middle" font-size="11.5" font-weight="600" fill="#b08d1c"{"".join("") if np_>=0 else ""} fill-opacity="{1 if np_>=0 else 0.9}">{np_:.0f}</text>')
    bars2.append(f'<text x="{x1+34:.1f}" y="{H2-16}" text-anchor="middle" font-size="12" fill="#6b7280">{y}</text>')
bars2 = "".join(bars2)
bar_svg = f'''
<svg viewBox="0 0 {W2} {H2}" width="100%" role="img" aria-label="近五年营收与归母净利润，单位亿元">
  <defs>
    <linearGradient id="barRev" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2f56c9"/><stop offset="100%" stop-color="#1f3a93"/></linearGradient>
    <linearGradient id="barNp" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#e8b83a"/><stop offset="100%" stop-color="#c9a227"/></linearGradient>
  </defs>
  <line x1="{P2}" y1="{zero_y:.1f}" x2="{W2-24}" y2="{zero_y:.1f}" stroke="#c9a227" stroke-width="1" stroke-dasharray="4 3" opacity="0.6"/>
  {bars2}
</svg>'''

# ================= HTML 模板 =================
TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__COMP_NAME__ __THSCODE__ · 速览卡</title>
<style>
  :root {
    --bg: #f4f5f7; --surface: #ffffff; --surface-2: #fafbfc;
    --ink: #1a1d24; --ink-2: #5b6470; --ink-3: #98a1ad;
    --brand: #1f3a93; --brand-2: #2f56c9; --brand-soft: #eef1fa;
    --gold: #c9a227; --gold-soft: #faf5e3;
    --red: #e5484d; --green: #2fa36b;
    --border: #e8eaee; --radius: 14px;
    --shadow-sm: 0 1px 2px rgba(20,24,35,.04);
    --shadow-md: 0 1px 2px rgba(20,24,35,.04), 0 8px 24px -12px rgba(20,24,35,.08);
    --shadow-lg: 0 2px 4px rgba(20,24,35,.05), 0 16px 32px -14px rgba(20,24,35,.14);
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--ink); font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.55; padding:0 0 64px; }
  .goldbar { height:3px; background:linear-gradient(90deg,var(--gold),var(--brand),var(--gold)); }
  .wrap { max-width:960px; margin:0 auto; padding:0 18px; }
  .num { font-variant-numeric:tabular-nums; }

  .topbar { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; padding:22px 0 6px; }
  .brand { display:flex; align-items:center; gap:12px; }
  .logo { width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg,#1f3a93,#2f56c9); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:15px; letter-spacing:.5px; box-shadow:0 4px 14px -4px rgba(31,58,147,.5); }
  .brand .nm { font-size:22px; font-weight:700; line-height:1.3; }
  .pill { display:inline-block; font-size:11.5px; font-weight:600; padding:2px 10px; border-radius:20px; vertical-align:2px; }
  .pill.code { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
  .pill.xd { background:var(--gold-soft); color:#9a7b14; border:1px solid #ead9a0; }
  .meta { text-align:right; font-size:12px; color:var(--ink-3); }
  .meta b { color:var(--ink-2); font-weight:600; }

  .sectorbar { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:14px 0; padding:11px 16px; border-radius:12px; background:linear-gradient(120deg,#fdf9ec,#faf3d8); border:1px solid #eddcab; }
  .sectorbar .ic { font-size:17px; }
  .sectorbar .sc { font-size:14px; font-weight:700; color:#8a6d12; }
  .sectorbar .scd { font-size:12px; color:#a8883a; }
  .sectorbar .biz { font-size:12px; color:#7a6a2a; background:rgba(255,255,255,.55); border:1px solid #ead9a0; padding:2px 10px; border-radius:8px; }
  .sectorbar .tag { margin-left:auto; font-size:11px; color:#a8883a; }

  .intro-card { background:linear-gradient(150deg,#ffffff,#f8faff); border:1px solid var(--border); border-radius:var(--radius); box-shadow:var(--shadow-sm); padding:18px 22px; margin-bottom:4px; }
  .intro-card h3 { font-size:13.5px; font-weight:700; margin-bottom:8px; display:flex; align-items:center; gap:8px; }
  .intro-card h3::before { content:""; width:4px; height:14px; border-radius:2px; background:linear-gradient(180deg,var(--gold),var(--brand)); }
  .intro-card p { font-size:13px; color:var(--ink-2); line-height:1.8; }
  .intro-tags { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
  .intro-tags span { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:600; }

  .hero { background:linear-gradient(150deg,#ffffff 30%,#fbfcfe 100%); border:1px solid var(--border); border-radius:18px; box-shadow:var(--shadow-md); padding:24px 28px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px; position:relative; overflow:hidden; }
  .hero::before { content:""; position:absolute; right:-70px; top:-70px; width:240px; height:240px; border-radius:50%; background:radial-gradient(circle,rgba(201,162,39,.12),transparent 65%); }
  .hero::after { content:""; position:absolute; left:-50px; bottom:-90px; width:200px; height:200px; border-radius:50%; background:radial-gradient(circle,rgba(31,58,147,.06),transparent 70%); }
  .hero .big { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; position:relative; z-index:1; }
  .hero .price { font-size:54px; font-weight:800; letter-spacing:-1.5px; }
  .hero .price .cur { font-size:27px; font-weight:600; color:var(--ink-2); margin-right:2px; }
  .hero .chg { font-size:19px; font-weight:700; color:var(--__CHG_COLOR_VAR__); }
  .hero .arrow { display:inline-block; margin-right:4px; }
  .hero .sub { margin-top:10px; font-size:12.5px; color:var(--ink-3); position:relative; z-index:1; }
  .hero .kpis { display:flex; gap:28px; position:relative; z-index:1; }
  .hero .kpi { text-align:right; }
  .hero .kpi .v { font-size:16px; font-weight:750; }
  .hero .kpi .k { font-size:11.5px; color:var(--ink-3); margin-top:2px; }

  .sec { display:flex; align-items:center; justify-content:space-between; margin:30px 2px 12px; }
  .sec h2 { font-size:15px; font-weight:700; letter-spacing:.2px; display:flex; align-items:center; gap:9px; }
  .sec h2 .no { font-size:11px; font-weight:800; color:#fff; background:linear-gradient(180deg,var(--gold),#a8871d); border-radius:5px; padding:2px 6px; letter-spacing:0; }
  .sec h2::after { content:""; width:4px; height:16px; border-radius:2px; background:linear-gradient(180deg,var(--gold),var(--brand)); }
  .sec .hint { font-size:12px; color:var(--ink-3); font-weight:400; }

  .card { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px 18px; box-shadow:var(--shadow-sm); transition:transform .18s ease, box-shadow .18s ease; }
  .card:hover { transform:translateY(-2px); box-shadow:var(--shadow-lg); }
  .card h3 { font-size:13.5px; font-weight:700; margin-bottom:10px; display:flex; justify-content:space-between; align-items:baseline; }
  .card h3 .unit { font-size:11px; color:var(--ink-3); font-weight:400; }
  .mcard { text-align:center; padding:16px 10px 14px; }
  .mcard .mv { font-size:22px; font-weight:750; letter-spacing:-.3px; }
  .mcard .mk { font-size:12px; color:var(--ink-3); margin-top:3px; }
  .mcard.pe .mv { color:var(--red); }

  .quote-box { display:grid; grid-template-columns:1.15fr .85fr; gap:16px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:18px; box-shadow:var(--shadow-md); }
  .quote-left { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; align-content:center; }
  .qk { background:var(--surface-2); border:1px solid var(--border); border-radius:10px; padding:13px 10px; text-align:center; transition:border-color .18s; }
  .qk:hover { border-color:#d5def5; }
  .qk .qv { font-size:19px; font-weight:750; }
  .qk .qk2 { font-size:11.5px; color:var(--ink-3); margin-top:2px; }
  .qk.hl .qv { color:var(--red); } .qk.ll .qv { color:var(--green); }
  .quote-right { display:flex; align-items:stretch; }
  .quote-right svg { height:100%; max-height:340px; }

  .val-wrap { display:grid; grid-template-columns:1.2fr 1fr; gap:12px; }
  .val-main { background:linear-gradient(150deg,#1f3a93,#2747a8); border-radius:var(--radius); padding:22px 24px; color:#fff; box-shadow:0 10px 28px -12px rgba(31,58,147,.5); position:relative; overflow:hidden; }
  .val-main::after { content:""; position:absolute; right:-40px; top:-40px; width:160px; height:160px; border-radius:50%; background:radial-gradient(circle,rgba(255,255,255,.12),transparent 70%); }
  .val-main .vk { font-size:12.5px; opacity:.85; letter-spacing:.4px; }
  .val-main .vv { font-size:40px; font-weight:800; margin:6px 0 10px; letter-spacing:-1px; }
  .val-main .vd { font-size:12.5px; line-height:1.7; opacity:.92; }
  .val-main .src { position:absolute; right:18px; bottom:14px; font-size:10.5px; opacity:.5; }
  .val-sub { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .val-sub .vs { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:14px 16px; box-shadow:var(--shadow-sm); display:flex; flex-direction:column; transition:border-color .18s, box-shadow .18s; }
  .val-sub .vs:hover { border-color:#d5def5; box-shadow:var(--shadow-md); }
  .val-sub .vst { display:flex; justify-content:space-between; align-items:baseline; }
  .val-sub .vsn { font-size:12px; color:var(--ink-3); }
  .val-sub .vsv { font-size:20px; font-weight:750; }
  .val-sub .vsd { font-size:11.5px; color:var(--ink-3); line-height:1.6; margin-top:6px; }

  .grid-2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }
  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink-2); }
  .kv .v { font-weight:650; }
  .kv .v.grow { color:var(--red); }

  .chart-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:18px 20px 14px; box-shadow:var(--shadow-md); }
  .legend { display:flex; gap:18px; font-size:12px; color:var(--ink-2); margin-bottom:12px; align-items:center; }
  .legend i { display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:6px; vertical-align:-1px; }
  .legend .sp { margin-left:auto; font-size:12.5px; }
  .legend .sp b { color:var(--red); font-size:14px; }

  table { width:100%; border-collapse:collapse; font-size:13.5px; }
  th, td { padding:8px 10px; text-align:right; border-bottom:1px solid var(--border); }
  th { color:var(--ink-3); font-weight:500; font-size:12px; background:var(--surface-2); }
  th:first-child, td:first-child { text-align:left; }
  tbody tr:nth-child(even) td { background:#fbfcfd; }
  tbody tr:last-child td { border-bottom:none; }
  tbody tr:hover td { background:#f4f6fb; }
  .pos { color:var(--red); } .neg { color:var(--green); }

  .note { font-size:11.5px; color:var(--ink-3); margin-top:10px; line-height:1.6; }
  .foot { margin-top:36px; padding:18px 4px 0; border-top:1px solid var(--border); color:var(--ink-3); font-size:11.5px; line-height:1.75; }
  .foot b { color:var(--ink-2); }
  a:focus-visible, button:focus-visible, [tabindex]:focus-visible { outline:2px solid var(--brand-2); outline-offset:2px; border-radius:4px; }

  @media (max-width:760px) {
    .quote-box { grid-template-columns:1fr; }
    .val-wrap { grid-template-columns:1fr; }
    .hero .kpis { gap:18px; }
    .hero .price { font-size:42px; }
  }
  @media print {
    body { background:#fff; }
    .card, .hero, .chart-card, .quote-box { box-shadow:none; }
    .goldbar { display:none; }
  }
</style>
</head>
<body>
<div class="goldbar"></div>
<div class="wrap">

  <div class="topbar">
    <div class="brand">
      <div class="logo">__COMP_SHORT__</div>
      <div class="nm">__COMP_NAME__ <span class="pill code">__THSCODE__</span></div>
    </div>
    <div class="meta">数据日期 <b>__DATE__（__WEEKDAY__）收盘</b><br>数据源 · 同花顺金融数据</div>
  </div>

  <div class="sectorbar">
    <span class="ic">__SECTOR_ICON__</span>
    <span class="sc">__SECTOR__</span>
    <span class="scd">· __SECTOR_DESC__</span>
    <span class="biz">主营：__BIZ__</span>
    <span class="tag">所属板块</span>
  </div>

  <div class="intro-card">
    <h3>公司简介</h3>
    <p>__INTRO__</p>
    <div class="intro-tags">__INTRO_TAGS__</div>
  </div>

  <div class="hero" style="margin-top:14px">
    <div>
      <div class="big">
        <span class="price num"><span class="cur">¥</span>__LAST__</span>
        <span class="chg num"><span class="arrow">__ARROW__</span>__CHG__</span>
        <span class="pill up num" style="background:__CHG_BG__;color:var(--__CHG_COLOR_VAR__)">__PCT__</span>
        __XD_PILL__
      </div>
      <div class="sub">最新收盘价 · 前复权口径 · 行情/估值快照 __QUOTE_DATE__</div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num">__TURNOVER__</div><div class="k">成交额(元)</div></div>
      <div class="kpi"><div class="v num">__VOL__</div><div class="k">成交量(股)</div></div>
      <div class="kpi"><div class="v num" style="color:var(--__Y52_COLOR_VAR__)">__CHG52_PCT__</div><div class="k">近1年涨幅</div></div>
    </div>
  </div>

  <div class="sec"><h2><span class="no">01</span>当日行情</h2><span class="hint">__DATE__ · 最近交易日 K 线标注</span></div>
  <div class="quote-box">
    <div class="quote-left">
      <div class="qk"><div class="qv num">__O__</div><div class="qk2">今开</div></div>
      <div class="qk hl"><div class="qv num">__H__</div><div class="qk2">最高</div></div>
      <div class="qk ll"><div class="qv num">__L__</div><div class="qk2">最低</div></div>
      <div class="qk"><div class="qv num">__PREV__</div><div class="qk2">昨收</div></div>
      <div class="qk"><div class="qv num">__LAST__</div><div class="qk2">最新收盘</div></div>
      <div class="qk"><div class="qv num">__AMP__%</div><div class="qk2">振幅(高-低/昨收)</div></div>
    </div>
    <div class="quote-right">__KLINE_SVG__</div>
  </div>

  <div class="sec"><h2><span class="no">02</span>估值快照</h2><span class="hint">__QUOTE_DATE__ · 每个指标附含义与作用</span></div>
  <div class="val-wrap">
    <div class="val-main">
      <div class="vk">PE · 市盈率（滚动 12 个月）</div>
      <div class="vv num">__VAL0__</div>
      <div class="vd">__VAL0_D__</div>
      <div class="src">核心估值指标</div>
    </div>
    <div class="val-sub">
      <div class="vs"><div class="vst"><span class="vsn">PE (MRQ)</span><span class="vsv num">__VAL1__</span></div><div class="vsd">__VAL1_D__</div></div>
      <div class="vs"><div class="vst"><span class="vsn">PB (MRQ)</span><span class="vsv num">__VAL2__</span></div><div class="vsd">__VAL2_D__</div></div>
      <div class="vs"><div class="vst"><span class="vsn">PS (TTM)</span><span class="vsv num">__VAL3__</span></div><div class="vsd">__VAL3_D__</div></div>
      <div class="vs"><div class="vst"><span class="vsn">PCF (TTM)</span><span class="vsv num">__VAL4__</span></div><div class="vsd">__VAL4_D__</div></div>
    </div>
  </div>

  <div class="sec"><h2><span class="no">03</span>财务指标</h2><span class="hint">__REPORT_HINT__</span></div>
  <div class="grid-2">
    <div class="card"><h3>盈利能力 <span class="unit">%</span></h3>__PROFIT__</div>
    <div class="card"><h3>成长能力 <span class="unit">同比 %</span></h3>__GROWTH__</div>
    <div class="card"><h3>偿债能力</h3>__SOLVENCY__</div>
    <div class="card"><h3>营运与现金流</h3>__OPER__</div>
  </div>

  <div class="sec"><h2><span class="no">04</span>近 5 年业绩</h2><span class="hint">年度 · 单位：亿元</span></div>
  <div class="chart-card">
    <div class="legend"><span><i style="background:linear-gradient(180deg,#2f56c9,#1f3a93)"></i>营业收入</span><span><i style="background:linear-gradient(180deg,#e8b83a,#c9a227)"></i>归母净利润</span></div>
    __BAR_SVG__
  </div>

  <div class="grid-2" style="margin-top:14px">
    <div class="card"><h3>__FY_LABEL__ <span class="unit">亿元</span></h3>
      <div class="kv"><span class="k">营业收入</span><span class="v num">__FY_REV__</span></div>
      <div class="kv"><span class="k">营业成本</span><span class="v num">__FY_COST__</span></div>
      <div class="kv"><span class="k">毛利率</span><span class="v num">__FY_GP__</span></div>
      <div class="kv"><span class="k">营业利润</span><span class="v num">__FY_OP__</span></div>
      <div class="kv"><span class="k">归母净利润</span><span class="v num" style="color:var(--red)">__FY_NP__</span></div>
      <div class="kv"><span class="k">基本 EPS</span><span class="v num">__FY_EPS__</span></div>
    </div>
    <div class="card"><h3>__REPORT_LABEL__ <span class="unit">亿元</span></h3>
      <div class="kv"><span class="k">__RPT_REV_LAB__</span><span class="v num">__RPT_REV__</span></div>
      <div class="kv"><span class="k">__RPT_NP_LAB__</span><span class="v num" style="color:var(--red)">__RPT_NP__</span></div>
      <div class="kv"><span class="k">__RPT_EPS_LAB__</span><span class="v num">__RPT_EPS__ 元</span></div>
      <div class="kv"><span class="k">营收同比</span><span class="v num" style="color:var(--red)">__RPT_REV_YOY__</span></div>
      <div class="kv"><span class="k">归母净利同比</span><span class="v num" style="color:var(--red)">__RPT_NP_YOY__</span></div>
    </div>
    <div class="card"><h3>资产负债（最新报告期末） <span class="unit">亿元</span></h3>
      <div class="kv"><span class="k">总资产</span><span class="v num">__BS_A__</span></div>
      <div class="kv"><span class="k">总负债</span><span class="v num">__BS_D__</span></div>
      <div class="kv"><span class="k">所有者权益</span><span class="v num">__BS_E__</span></div>
      <div class="kv"><span class="k">货币资金</span><span class="v num">__BS_C__</span></div>
      <div class="kv"><span class="k">资产负债率</span><span class="v num">__BS_DR__%</span></div>
      <div class="note">流动比率 __BS_CR__ · 速动比率 __BS_QR__</div>
    </div>
  </div>

  <div class="sec"><h2><span class="no">05</span>近 1 年股价走势</h2><span class="hint">前复权 · 共 __N__ 个交易日 · MACD/KDJ 由收盘价计算</span></div>
  <div class="chart-card">
    <div class="legend">
      <span><i style="background:#1f3a93"></i>收盘价</span>
      <span><i style="background:#e8a020"></i>MA20</span>
      <span class="sp">区间涨幅 <b class="num">__CHG52_PCT__</b></span>
    </div>
    __CHART_SVG__
  </div>

  <div class="sec"><h2><span class="no">06</span>现金流与分红</h2><span class="hint">__CF_DIV_HINT__</span></div>
  <div class="grid-2">
    <div class="card">
      <table>
        <tr><th>年度</th><th>经营净额</th><th>投资净额</th><th>筹资净额</th></tr>
        __CF_ROWS__
      </table>
      <div class="note">__CF_NOTE__</div>
    </div>
    <div class="card">
      <table>
        <tr><th>除息日</th><th>每股派息(元)</th></tr>
        __DIV_ROWS__
      </table>
      <div class="note">__DIV_NOTE__</div>
    </div>
  </div>

  <div class="foot">
    <b>数据口径与来源</b>：行情/估值/财务/分红来自同花顺金融数据（hithink-finance v0.1.5，远端快照接口）；历史日K为本地 DuckDB 前复权数据；主营业务与公司简介来自公司公开年报/官网；MACD、KDJ 由历史收盘价/最高价/最低价计算，为技术指标模型输出。<br>
    财务指标为最新报告期口径；ROE 为加权口径；同比增速为累计口径；所有百分数指标值均已按服务端口径直接展示（不乘 100）。<br>
    本报告仅供研究参考，不构成个人投资建议。
  </div>

</div>
</body>
</html>"""

# ================= 组装 =================
def kv_rows(items, grow=False):
    cls = 'v num grow' if grow else 'v num'
    return "".join(f'<div class="kv"><span class="k">{k}</span><span class="{cls}">{v}</span></div>' for k, v in items)

def cf_rows():
    out = []
    for y, o, i, f in CF:
        oc = "pos" if o >= 0 else "neg"
        ic = "pos" if i >= 0 else "neg"
        fc = "pos" if f >= 0 else "neg"
        out.append(f'<tr><td>{y}</td><td class="{oc} num">{o:.2f}</td><td class="{ic} num">{i:.2f}</td><td class="{fc} num">{f:.2f}</td></tr>')
    return "".join(out)

# 涨跌方向配色（红涨绿跌）：一律由真实涨跌符号推导，供 TPL 占位符注入，
# 修正原模板把「当日涨跌 / 近1年涨幅」方向色写死为单一颜色的缺陷。
CHG_UP = SNAP["pct"] is not None and SNAP["pct"] >= 0
CHG_COLOR_VAR = "red" if CHG_UP else "green"
CHG_BG = "#fdecec" if CHG_UP else "#eaf6f0"
Y52_UP = chg_52 is not None and chg_52 >= 0
Y52_COLOR_VAR = "red" if Y52_UP else "green"

up_arrow = "▲" if SNAP["pct"] >= 0 else "▼"
intro_tags = "".join(f'<span>{t}</span>' for t in CONFIG["intro_tags"])

html = (TPL
        .replace("__COMP_NAME__", CONFIG["comp_name"])
        .replace("__FY_LABEL__", FY_LABEL)
        .replace("__CF_DIV_HINT__", CF_DIV_HINT)
        .replace("__COMP_SHORT__", CONFIG["comp_short"])
        .replace("__THSCODE__", CONFIG["thscode"])
        .replace("__DATE__", CONFIG["date"])
        .replace("__WEEKDAY__", CONFIG["weekday"])
        .replace("__SECTOR__", CONFIG["sector"])
        .replace("__SECTOR_DESC__", CONFIG["sector_desc"])
        .replace("__SECTOR_ICON__", CONFIG.get("sector_icon", "⛏️"))
        .replace("__BIZ__", CONFIG["biz"])
        .replace("__INTRO__", CONFIG["intro"])
        .replace("__INTRO_TAGS__", intro_tags)
        .replace("__REPORT_LABEL__", CONFIG["report_label"])
        .replace("__REPORT_HINT__", CONFIG["report_hint"])
        .replace("__RPT_REV_LAB__", CONFIG["rpt_rev_lab"])
        .replace("__RPT_NP_LAB__", CONFIG["rpt_np_lab"])
        .replace("__RPT_EPS_LAB__", CONFIG["rpt_eps_lab"])
        .replace("__LAST__", f"{SNAP['last']:.2f}")
        .replace("__CHG__", f"{SNAP['chg']:+.2f}")
        .replace("__PCT__", f"{SNAP['pct']:+.2f}%")
        .replace("__ARROW__", up_arrow)
        .replace("__CHG_COLOR_VAR__", CHG_COLOR_VAR)
        .replace("__CHG_BG__", CHG_BG)
        .replace("__Y52_COLOR_VAR__", Y52_COLOR_VAR)
        .replace("__XD_PILL__", f'<span class="pill xd">当日除息 · 每股派 {CONFIG["div_amt"]:.2f} 元</span>' if CONFIG["xd"] else "")
        .replace("__QUOTE_DATE__", CONFIG["quote_date"])
        .replace("__TURNOVER__", f"{SNAP['turnover']/1e8:.2f}亿")
        .replace("__VOL__", f"{SNAP['vol']/1e8:.2f}亿")
        .replace("__CHG52_PCT__", f"{chg_52:+.1f}%")
        .replace("__O__", f"{SNAP['open']:.2f}")
        .replace("__H__", f"{SNAP['high']:.2f}")
        .replace("__L__", f"{SNAP['low']:.2f}")
        .replace("__PREV__", f"{SNAP['prev']:.2f}")
        .replace("__AMP__", f"{amp:.2f}")
        .replace("__KLINE_SVG__", kline_svg)
        .replace("__VAL0__", f"{VAL[0][1]:.2f}").replace("__VAL0_D__", VAL[0][2])
        .replace("__VAL1__", f"{VAL[1][1]:.2f}").replace("__VAL1_D__", VAL[1][2])
        .replace("__VAL2__", f"{VAL[2][1]:.2f}").replace("__VAL2_D__", VAL[2][2])
        .replace("__VAL3__", f"{VAL[3][1]:.2f}").replace("__VAL3_D__", VAL[3][2])
        .replace("__VAL4__", f"{VAL[4][1]:.2f}").replace("__VAL4_D__", VAL[4][2])
        .replace("__PROFIT__", kv_rows(IND["profit"]))
        .replace("__GROWTH__", kv_rows(IND["growth"], grow=True))
        .replace("__SOLVENCY__", kv_rows(IND["solvency"]))
        .replace("__OPER__", kv_rows(IND["oper"]))
        .replace("__BAR_SVG__", bar_svg)
        .replace("__FY_REV__", f"{FY25['rev']:.2f}").replace("__FY_COST__", f"{FY25['cost']:.2f}")
        .replace("__FY_GP__", FY25["gp"]).replace("__FY_OP__", f"{FY25['op']:.2f}")
        .replace("__FY_NP__", f"{FY25['np']:.2f}").replace("__FY_EPS__", FY25["eps"])
        .replace("__RPT_REV__", f"{RPT['rev']:.2f}").replace("__RPT_NP__", f"{RPT['np']:.2f}")
        .replace("__RPT_EPS__", f"{RPT['eps']:.3f}").replace("__RPT_REV_YOY__", RPT["rev_yoy"])
        .replace("__RPT_NP_YOY__", RPT["np_yoy"])
        .replace("__BS_A__", f"{BS['assets']:.2f}").replace("__BS_D__", f"{BS['debt']:.2f}")
        .replace("__BS_E__", f"{BS['equity']:.2f}").replace("__BS_C__", f"{BS['cash']:.2f}")
        .replace("__BS_DR__", f"{BS['dr']:.2f}").replace("__BS_CR__", f"{BS['cr']:.2f}")
        .replace("__BS_QR__", f"{BS['qr']:.2f}")
        .replace("__N__", str(n))
        .replace("__CHART_SVG__", chart_svg)
        .replace("__CF_ROWS__", cf_rows())
        .replace("__CF_NOTE__", f'{CF[-1][0]}年：购建资产支出 {CF_2025["capex"]:.2f}亿 · 分红付息 {CF_2025["div"]:.2f}亿 · 现金净增加 {CF_2025["net"]:.2f}亿')
        .replace("__DIV_ROWS__", "".join(f'<tr><td>{d}</td><td class="num">{v:.2f}</td></tr>' for d, v in DIVS))
        .replace("__DIV_NOTE__", f'近两期年度累计每股派息 {DIV_SUM:.2f} 元 · 按现价约合股息率 <b>{DIV_YIELD:.2f}%</b>（静态估算）'))

out = os.path.join(BASE, f'{CONFIG["comp_name"]}_{CONFIG["date"].replace("-", "")}.html')
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("OK ->", out, "| size:", os.path.getsize(out), "bytes")
