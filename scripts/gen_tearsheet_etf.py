# -*- coding: utf-8 -*-
"""ETF 速览卡 HTML 生成器（v1 通用模板）
用途：将一只 ETF（场内）的全部研究信息渲染为单页 HTML 速览卡。
能力点：价格Hero / 当日行情+K线标注 / 区间收益表格+横向条形图(含同类排名) /
       基金资料(规模/净值/费率/经理/仓位) / 前十大持仓表 / 近1年走势图(MA20+MACD+KDJ)
模板约定：
  1. 本文件是【模板】——使用前必须将 CONFIG 与下方各数据字典替换为目标 ETF 数据
  2. 数据获取方式：先加载 hithink-finance skill，用 fund.* CLI 拉取后填入（见 SKILL.md 工作流）
  3. ETF 无 PE/PB 估值、无三大报表，用收益/净值/持仓替代
  4. 历史K结构为 data.item[] + date_ms/close_price（与 A 股个股 data(list)+date/close 不同，解析已兼容）
  5. 百分比口径：所有百分数指标值按服务端口径直接展示（不乘 100）
数据源: hithink-finance CLI v0.1.5（fund.* 接口）
"""
import json, os, datetime

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
HIST = os.path.join(BASE, ".workbuddy", "output", "nzke_history.json")

# ================= ETF 配置 =================
CONFIG = {
    "comp_name": "纳指科技ETF景顺", "comp_short": "纳指", "thscode": "159509.SZ",
    "exchange": "深市 · 跨境QDII", "sector": "QDII · 跨境ETF", "sector_desc": "跟踪纳斯达克科技市值加权指数",
    "sector_icon": "🌐",
    "biz": "完全复制法跟踪纳斯达克科技市值加权指数，聚焦微软、苹果、英伟达、谷歌等全球科技龙头",
    "intro": ("纳指科技ETF景顺（159509）成立于2023年7月，是国内唯一跟踪纳斯达克科技市值加权指数的ETF。"
              "该指数从纳斯达克100中筛选ICB行业为'科技'的股票，科技属性更纯正，前十大成分股权重超60%，"
              "聚焦半导体、计算机硬件等硬科技赛道。管理人为景顺长城基金，托管人招商银行。"),
    "intro_tags": ["成立2023-07", "国内唯一跟踪标的", "规模147亿", "QDII跨境ETF"],
    "date": "2026-08-21", "weekday": "周五",
    "quote_date": "2026-08-21",
    "fund_scale": "147.44亿", "unit_nav": "2.2266",
    "mgmt_rate": "0.80%", "custody_rate": "0.20%",
    "mgmt_name": "景顺长城基金", "manager": "张晓南（任期回报+126.28%）",
    "estab": "2023-07-19", "stock_ratio": "96.22%", "concentration": "75.36%",
    "div_note": "自成立以来暂无分红记录",
}
SNAP = {"last": 2.782, "chg": -0.01, "pct": -0.36, "open": 2.778, "high": 2.789,
        "low": 2.771, "prev": 2.792, "vol": 202801380, "turnover": 563523680,
        "amp": 0.644699, "turnover_ratio": 3.06}
# 收益（%）
RET = [("近1周", -3.67), ("近1月", 1.21), ("近3月", 0.98), ("近6月", 24.25),
       ("近1年", 32.58), ("近2年", 58.02), ("近3年", 137.28), ("今年以来", 17.92),
       ("成立以来", 122.66)]
RANK_NOTE = "同类排名：近1年 27/445 · 近3年 9/445 · 近6月 14/445"
# 前10持仓
HOLD = [("英伟达", "NVDA.O", 13.01, "+0.32%"), ("苹果", "AAPL.O", 12.73, "+0.42%"),
        ("微软", "MSFT.O", 9.52, "-2.60%"), ("谷歌A", "GOOGL.O", 6.69, "+0.59%"),
        ("谷歌C", "GOOG.O", 6.20, "+0.51%"), ("博通", "AVGO.O", 6.15, "-1.10%"),
        ("美光科技", "MU.O", 5.66, "+2.72%"), ("Meta", "META.O", 5.38, "-1.41%"),
        ("超威半导体", "AMD.O", 4.12, "+1.72%"), ("英特尔", "INTC.O", 3.05, "[MISSING]")]

HOLD_PERIOD = '2026年中报'

# ================= 历史日K（ETF结构 data.item[] + close_price） =================
with open(HIST, "r", encoding="utf-8") as f:
    env = json.load(f)
items = env["data"]["item"] if isinstance(env.get("data"), dict) else env["data"]
def dtf(ms): return datetime.datetime.fromtimestamp(ms/1000).strftime("%Y-%m-%d")
dates = [dtf(b["date_ms"]) for b in items]
closes = [b["close_price"] for b in items]
highs = [b["high_price"] for b in items]
lows = [b["low_price"] for b in items]
vols = [b["volume"] for b in items]
hi_52 = max(highs)
lo_52 = min(lows)
chg_52 = (closes[-1] / closes[0] - 1) * 100
n = len(items)

# ================= 技术指标 =================
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
kb = items[-1]
k_prev = items[-2]["close_price"] if n >= 2 else kb["open_price"]
k_up = kb["close_price"] >= kb["open_price"]
k_color = "#e5484d" if k_up else "#2fa36b"
KW, KH, KPAD = 300, 320, 46
kr = max(kb["high_price"], k_prev) - min(kb["low_price"], k_prev)
k_ymin = min(kb["low_price"], k_prev) - kr * 0.12
k_ymax = max(kb["high_price"], k_prev) + kr * 0.12
def kpy(v): return KPAD + (k_ymax - v) / (k_ymax - k_ymin) * (KH - 2 * KPAD)
cx = KW / 2 - 14
body_w = 34
hy, ly = kpy(kb["high_price"]), kpy(kb["low_price"])
oy, cy = kpy(kb["open_price"]), kpy(kb["close_price"])
body_top, body_h = min(oy, cy), abs(oy - cy) or 2
k_marks = [("最高", kb["high_price"], hy, "#c8102e"), ("收盘", kb["close_price"], cy, "#1f3a93"),
           ("开盘", kb["open_price"], oy, "#5b6470"), ("昨收", k_prev, kpy(k_prev), "#98a1ad"),
           ("最低", kb["low_price"], ly, "#2fa36b")]
k_mark_svg = []
for label, price, y, color in k_marks:
    k_mark_svg.append(f'<line x1="{cx-body_w/2-14:.1f}" y1="{y:.1f}" x2="{cx+body_w/2+14:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="4 3" opacity="0.75"/>')
    k_mark_svg.append(f'<text x="{cx+body_w/2+20:.1f}" y="{y+4:.1f}" font-size="11" fill="{color}" font-weight="600">{label} {price:.3f}</text>')
k_mark_svg = "".join(k_mark_svg)
kline_svg = f'''
<svg viewBox="0 0 {KW} {KH}" width="100%" style="min-width:260px" role="img" aria-label="最近交易日K线">
  <rect x="0" y="0" width="{KW}" height="{KH}" rx="12" fill="#fafbfc"/>
  <text x="{cx}" y="22" text-anchor="middle" font-size="12.5" font-weight="700" fill="#5b6470">{dtf(kb["date_ms"])}</text>
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
    grid.append(f'<text x="{PAD-9}" y="{py(v)+4:.1f}" text-anchor="end" font-size="11" fill="#98a1ad">{v:.2f}</text>')
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
<text x="{PAD+44}" y="{macd_top-2}" font-size="10" fill="#1f3a93">DIF {dif[-1]:.3f}</text>
<text x="{PAD+112}" y="{macd_top-2}" font-size="10" fill="#e8a020">DEA {dea[-1]:.3f}</text>
<text x="{PAD+180}" y="{macd_top-2}" font-size="10" fill="#e5484d">柱 {macd_hist[-1]:.3f}</text>
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
<svg id="trendChart" viewBox="0 0 {W} {total_h}" width="100%" role="img" aria-label="近一年净值走势与技术指标">
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

# ================= 收益/持仓 HTML =================
def ret_table():
    rows = []
    for name, v in RET:
        color = "var(--red)" if v >= 0 else "var(--green)"
        sign = "+" if v >= 0 else ""
        if name in ("近1年", "成立以来"):
            rows.append(f'<tr style="background:#f4f6fb"><td><b>{name}</b></td><td class="num" style="color:{color};font-weight:800">{sign}{v:.2f}%</td></tr>')
        else:
            rows.append(f'<tr><td>{name}</td><td class="num" style="color:{color}">{sign}{v:.2f}%</td></tr>')
    return "".join(rows)

def ret_bar_svg():
    """区间收益横向条形图：0 轴居中，正收益红条向右、负收益绿条向左"""
    BW, BH = 460, 360
    pad_l, pad_r, pad_t, row_h, gap = 86, 58, 24, 34, 4
    # 数据范围（含负值）
    vmax = max(v for _, v in RET)
    vmin = min(0, min(v for _, v in RET))
    span = (vmax - vmin) or 1
    def bx(v): return pad_l + (v - vmin) / span * (BW - pad_l - pad_r)
    zero_x = bx(0)
    parts = []
    # 0 轴线
    parts.append(f'<line x1="{zero_x:.1f}" y1="{pad_t-8}" x2="{zero_x:.1f}" y2="{BH-16}" stroke="#c9a227" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.7"/>')
    for i, (name, v) in enumerate(RET):
        y = pad_t + i * (row_h + gap)
        x0, x1 = zero_x, bx(v)
        left, right = min(x0, x1), max(x0, x1)
        w = max(right - left, 3)
        color = "#e5484d" if v >= 0 else "#2fa36b"
        sign = "+" if v >= 0 else ""
        # 区间名（左侧固定列，右对齐）
        parts.append(f'<text x="{pad_l-12}" y="{y+row_h/2+4:.1f}" text-anchor="end" font-size="12" fill="#5b6470">{name}</text>')
        # 条形
        parts.append(f'<rect x="{left:.1f}" y="{y+4:.1f}" width="{w:.1f}" height="{row_h-8}" rx="5" fill="{color}" opacity="0.85"/>')
        if v >= 0:
            # 正值：标签在条右端外侧
            parts.append(f'<text x="{right+8:.1f}" y="{y+row_h/2+4:.1f}" text-anchor="start" font-size="11.5" font-weight="700" fill="{color}">{sign}{v:.2f}%</text>')
        else:
            # 负值：标签在条正上方（避免与左侧区间名重叠）
            parts.append(f'<text x="{left+w/2:.1f}" y="{y+2:.1f}" text-anchor="middle" font-size="11.5" font-weight="700" fill="{color}">{sign}{v:.2f}%</text>')
    return f'''
<svg viewBox="0 0 {BW} {BH}" width="100%" role="img" aria-label="区间收益横向条形图">
  {''.join(parts)}
</svg>'''

hold_rows = "".join(
    f'<tr><td><b>{i}</b></td><td>{nm}</td><td class="num" style="color:var(--ink-3)">{code}</td><td class="num" style="font-weight:700">{r:.2f}%</td><td class="num" style="color:var(--{"red" if chg.startswith("+") else "green"})">{chg}</td></tr>'
    for i, (nm, code, r, chg) in enumerate(HOLD, 1))

amp = SNAP["amp"]

# ================= HTML =================
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
  .brand .nm { font-size:21px; font-weight:700; line-height:1.3; }
  .pill { display:inline-block; font-size:11.5px; font-weight:600; padding:2px 10px; border-radius:20px; vertical-align:2px; }
  .pill.code { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
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
  .mcard .mv { font-size:20px; font-weight:750; letter-spacing:-.3px; }
  .mcard .mk { font-size:12px; color:var(--ink-3); margin-top:3px; }

  .quote-box { display:grid; grid-template-columns:1.15fr .85fr; gap:16px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:18px; box-shadow:var(--shadow-md); }
  .quote-left { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; align-content:center; }
  .qk { background:var(--surface-2); border:1px solid var(--border); border-radius:10px; padding:13px 10px; text-align:center; transition:border-color .18s; }
  .qk:hover { border-color:#d5def5; }
  .qk .qv { font-size:19px; font-weight:750; }
  .qk .qk2 { font-size:11.5px; color:var(--ink-3); margin-top:2px; }
  .qk.hl .qv { color:var(--red); } .qk.ll .qv { color:var(--green); }
  .quote-right { display:flex; align-items:stretch; }
  .quote-right svg { height:100%; max-height:340px; }

  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; }
  .grid-2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }
  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink-2); }
  .kv .v { font-weight:650; }

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
    <span class="biz">投资策略：__BIZ__</span>
    <span class="tag">基金类型</span>
  </div>

  <div class="intro-card">
    <h3>基金简介</h3>
    <p>__INTRO__</p>
    <div class="intro-tags">__INTRO_TAGS__</div>
  </div>

  <div class="hero" style="margin-top:14px">
    <div>
      <div class="big">
        <span class="price num"><span class="cur">¥</span>__LAST__</span>
        <span class="chg num"><span class="arrow">__ARROW__</span>__CHG__</span>
        <span class="pill num" style="background:__CHG_BG__;color:var(--__CHG_COLOR_VAR__)">__PCT__</span>
      </div>
      <div class="sub">最新交易价格（场内）· 净值口径见基金资料 · 行情快照 __QUOTE_DATE__</div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num">__TURNOVER__</div><div class="k">成交额(元)</div></div>
      <div class="kpi"><div class="v num">__VOL__</div><div class="k">成交量(份)</div></div>
      <div class="kpi"><div class="v num" style="color:var(--__Y52_COLOR_VAR__)">__CHG52_PCT__</div><div class="k">近1年涨幅</div></div>
    </div>
  </div>

  <!-- 当日行情 -->
  <div class="sec"><h2><span class="no">01</span>当日行情</h2><span class="hint">__DATE__ · 最近交易日 K 线标注 · 单位：元</span></div>
  <div class="quote-box">
    <div class="quote-left">
      <div class="qk"><div class="qv num">__O__</div><div class="qk2">今开</div></div>
      <div class="qk hl"><div class="qv num">__H__</div><div class="qk2">最高</div></div>
      <div class="qk ll"><div class="qv num">__L__</div><div class="qk2">最低</div></div>
      <div class="qk"><div class="qv num">__PREV__</div><div class="qk2">昨收</div></div>
      <div class="qk"><div class="qv num">__AMP__%</div><div class="qk2">振幅</div></div>
      <div class="qk"><div class="qv num">__TR__%</div><div class="qk2">换手率</div></div>
    </div>
    <div class="quote-right">__KLINE_SVG__</div>
  </div>

  <!-- 收益表现 -->
  <div class="sec"><h2><span class="no">02</span>区间收益</h2><span class="hint">__QUOTE_DATE__ · __RANK_NOTE__</span></div>
  <div class="grid-2">
    <div class="card">
      <table>
        <tr><th>区间</th><th>收益率</th></tr>
        __RET_TABLE__
      </table>
    </div>
    <div class="card" style="display:flex;align-items:center;">
      __RET_BAR_SVG__
    </div>
  </div>

  <!-- 基金资料 -->
  <div class="sec"><h2><span class="no">03</span>基金资料</h2><span class="hint">数据源：基金资料接口</span></div>
  <div class="grid-2">
    <div class="card"><h3>基本信息</h3>
      <div class="kv"><span class="k">基金规模</span><span class="v num">__FUND_SCALE__</span></div>
      <div class="kv"><span class="k">单位净值</span><span class="v num">__UNIT_NAV__</span></div>
      <div class="kv"><span class="k">管理费率</span><span class="v num">__MGMT_RATE__</span></div>
      <div class="kv"><span class="k">托管费率</span><span class="v num">__CUSTODY_RATE__</span></div>
      <div class="kv"><span class="k">成立日期</span><span class="v num">__ESTAB__</span></div>
    </div>
    <div class="card"><h3>管理人</h3>
      <div class="kv"><span class="k">基金公司</span><span class="v num">__MGMT_NAME__</span></div>
      <div class="kv"><span class="k">基金经理</span><span class="v num">__MANAGER__</span></div>
      <div class="kv"><span class="k">股票仓位</span><span class="v num">__STOCK_RATIO__</span></div>
      <div class="kv"><span class="k">持仓集中度</span><span class="v num">__CONC__</span></div>
      <div class="kv"><span class="k">分红记录</span><span class="v num">__DIV_NOTE__</span></div>
    </div>
  </div>

  <!-- 前十大持仓 -->
  <div class="sec"><h2><span class="no">04</span>前十大持仓</h2><span class="hint">__HOLD_PERIOD__披露 · 合计占比 __HOLD_SUM__%</span></div>
  <div class="card">
    <table>
      <tr><th>#</th><th>股票</th><th>代码</th><th>占净值比</th><th>期间涨跌</th></tr>
      __HOLD_ROWS__
    </table>
    <div class="note">持仓数据来自基金定期报告（前十大），期间涨跌为报告期区间涨跌；[MISSING] 表示数据未披露。个股仅为持仓披露，不构成投资建议。</div>
  </div>

  <!-- 走势图 -->
  <div class="sec"><h2><span class="no">05</span>近 1 年价格走势</h2><span class="hint">场内交易价 · 共 __N__ 个交易日 · MACD/KDJ 由收盘价计算</span></div>
  <div class="chart-card">
    <div class="legend">
      <span><i style="background:#1f3a93"></i>收盘价</span>
      <span><i style="background:#e8a020"></i>MA20</span>
      <span class="sp">区间涨幅 <b class="num">__CHG52_PCT__</b></span>
    </div>
    __CHART_SVG__
  </div>

  <div class="foot">
    <b>数据口径与来源</b>：行情/收益/资料/持仓/分红来自同花顺金融数据（hithink-finance v0.1.5，fund 接口）；历史K为场内交易价（非单位净值），MACD/KDJ 由收盘价计算，为技术指标模型输出。<br>
    区间收益为基金官方披露口径；持仓为定期报告披露。ETF 投资涉及市场波动与汇率风险，跨境 QDII 产品需关注溢价与申赎限制。<br>
    本报告仅供研究参考，不构成个人投资建议。
  </div>

</div>
</body>
</html>"""

# ================= 组装 =================
# 涨跌方向配色（红涨绿跌）：一律由真实涨跌符号推导，供 TPL 占位符注入，
# 修正原模板把「当日涨跌 / 近1年涨幅」方向色写死为单一颜色的缺陷。
CHG_UP = SNAP["pct"] is not None and SNAP["pct"] >= 0
CHG_COLOR_VAR = "red" if CHG_UP else "green"
CHG_BG = "#fdecec" if CHG_UP else "#eaf6f0"
Y52_UP = chg_52 is not None and chg_52 >= 0
Y52_COLOR_VAR = "red" if Y52_UP else "green"

up_arrow = "▲" if SNAP["pct"] >= 0 else "▼"
intro_tags = "".join(f'<span>{t}</span>' for t in CONFIG["intro_tags"])
chg52_pct = f"{chg_52:+.1f}%"
hold_sum = sum(h[2] for h in HOLD)

html = (TPL
        .replace("__COMP_NAME__", CONFIG["comp_name"])
        .replace("__HOLD_PERIOD__", HOLD_PERIOD)
        .replace("__COMP_SHORT__", CONFIG["comp_short"])
        .replace("__THSCODE__", CONFIG["thscode"])
        .replace("__DATE__", CONFIG["date"])
        .replace("__WEEKDAY__", CONFIG["weekday"])
        .replace("__SECTOR__", CONFIG["sector"])
        .replace("__SECTOR_DESC__", CONFIG["sector_desc"])
        .replace("__SECTOR_ICON__", CONFIG["sector_icon"])
        .replace("__BIZ__", CONFIG["biz"])
        .replace("__INTRO__", CONFIG["intro"])
        .replace("__INTRO_TAGS__", intro_tags)
        .replace("__LAST__", f"{SNAP['last']:.3f}")
        .replace("__CHG__", f"{SNAP['chg']:+.2f}")
        .replace("__PCT__", f"{SNAP['pct']:+.2f}%")
        .replace("__ARROW__", up_arrow)
        .replace("__CHG_COLOR_VAR__", CHG_COLOR_VAR)
        .replace("__CHG_BG__", CHG_BG)
        .replace("__Y52_COLOR_VAR__", Y52_COLOR_VAR)
        .replace("__QUOTE_DATE__", CONFIG["quote_date"])
        .replace("__TURNOVER__", f"{SNAP['turnover']/1e8:.2f}亿")
        .replace("__VOL__", f"{SNAP['vol']/1e8:.2f}亿")
        .replace("__CHG52_PCT__", chg52_pct)
        .replace("__O__", f"{SNAP['open']:.3f}")
        .replace("__H__", f"{SNAP['high']:.3f}")
        .replace("__L__", f"{SNAP['low']:.3f}")
        .replace("__PREV__", f"{SNAP['prev']:.3f}")
        .replace("__AMP__", f"{amp:.2f}")
        .replace("__TR__", f"{SNAP['turnover_ratio']:.2f}")
        .replace("__KLINE_SVG__", kline_svg)
        .replace("__RET_TABLE__", ret_table())
        .replace("__RET_BAR_SVG__", ret_bar_svg())
        .replace("__RANK_NOTE__", RANK_NOTE)
        .replace("__FUND_SCALE__", CONFIG["fund_scale"])
        .replace("__UNIT_NAV__", CONFIG["unit_nav"])
        .replace("__MGMT_RATE__", CONFIG["mgmt_rate"])
        .replace("__CUSTODY_RATE__", CONFIG["custody_rate"])
        .replace("__ESTAB__", CONFIG["estab"])
        .replace("__MGMT_NAME__", CONFIG["mgmt_name"])
        .replace("__MANAGER__", CONFIG["manager"])
        .replace("__STOCK_RATIO__", CONFIG["stock_ratio"])
        .replace("__CONC__", CONFIG["concentration"])
        .replace("__DIV_NOTE__", CONFIG["div_note"])
        .replace("__HOLD_ROWS__", hold_rows)
        .replace("__HOLD_SUM__", f"{hold_sum:.2f}")
        .replace("__N__", str(n))
        .replace("__CHART_SVG__", chart_svg))

out = os.path.join(BASE, f'{CONFIG["comp_name"]}_{CONFIG["date"].replace("-", "")}.html')
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("OK ->", out, "| size:", os.path.getsize(out), "bytes")
