# -*- coding: utf-8 -*-
"""A股股票全面分析（全维透视）HTML 生成器 v1.1（模板）
【能力 #8】整合个股速览/财务/估值/成长预测/业绩前瞻/市场环境/机构资金/风险，一站式分析单只股票，给出投资指导。
【模板使用说明】
①hithink CLI 拉行情/估值/财务/历史K（market snapshot、valuation snapshot、financials income/indicators、market history）
②WebSearch 补主营构成/券商一致预期/机构持仓/订单（页脚标注来源，数据来源铁律）
③替换 BASE/DATE 与数据区（CONFIG/SNAP/BIZ/FIN_Y/FIN_Q/VAL/FC/CATALYST/ENV/INST/RISK/GUIDE/NOTE/TITLE_SUB + HIST 路径）
④运行 → 输出 `全面分析_{名称}_{YYYYMMDD}.html`
v1.1：hero 大标题=股票名（CONFIG['name']），报告类型小字 TITLE_SUB 独立字段（此前硬编码"股票全面分析"当大字，2026-09-03 用户纠正）
【风格】与其他能力一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-10、insight金色结论条
【口径】数据标 [ASSUMED]/[MISSING]；券商预测 WebSearch 标注；仅供研究参考不构成投资建议
"""
import json
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
HIST = os.path.join(BASE, ".workbuddy", "output", "verify", "hist_600522.json")
DATE = "2026-08-21"
WEEKDAY = "周五"

# ================= 数据（全部参数化） =================
CONFIG = {
    "name": "中天科技", "code": "600522.SH", "sector": "通信设备·光通信", "sector_icon": "🔆",
    "px": 32.00, "chg_pct": -4.28,
    "verdict": "高景气 · 估值消化中", "verdict_short": "成长",
    "verdict_note": "占位", "guide_summary": "占位",
}
# hero 大标题右侧小字 = 报告类型标识（不随股票变，但禁止硬编码进 TPL）
TITLE_SUB = "股票全面分析 · 全维透视 · 单股研究"
SNAP = {"open": 0, "high": 0, "low": 0, "prev": 0, "turnover": 0, "pe": 0, "pb": 0, "ps": 0, "pcf": 0,
        "mcap": 0, "hist_chg_1y": 0, "hi_52": 0, "lo_52": 0}
BIZ = {"main": "占位", "intro": "占位", "tags": ["占位"]}
FIN_Y = [(2021, 0, 0), (2022, 0, 0), (2023, 0, 0), (2024, 0, 0), (2025, 0, 0)]
FIN_Q = {"rev": 0, "rev_yoy": "0%", "np": 0, "np_yoy": "0%", "gm": 0, "roe": 0, "note": "占位"}
VAL = {"pe": 0, "pb": 0, "ps": 0, "pe_med": 0, "pe_fwd": 0, "note": "占位",
       "peers": [("同行", 0, 0, False)]}
FC = {"y26": 0, "y27": 0, "y28": 0, "fwd_pe": 0, "target": 0, "note": "占位",
      "scenarios": [("乐观", 0, "占位"), ("中性", 0, "占位"), ("悲观", 0, "占位")]}
CATALYST = [("事件", "时间", "说明")]
ENV = {"sector_pos": "占位", "sector_note": "占位", "sentiment": "占位", "sentiment_note": "占位"}
INST = {"fund_pct": 0, "fund_note": "占位", "north_note": "占位", "lhb_note": "占位"}
RISK = ["占位"]
GUIDE = [("结论", "占位"), ("数据含义", "占位"), ("情景", "占位"), ("操作", "占位"), ("跟踪", "占位")]
NOTE = "占位"

PEER_TITLE = '光通信/海缆同行对比'
FC_Y1 = '2026E'
FC_Y23 = '2027E / 2028E'

# ================= 历史K（52周走势） =================
with open(HIST, "r", encoding="utf-8") as f:
    hd = json.load(f)["data"]
bars = hd if isinstance(hd, list) else hd.get("item", [])
dates = [b["date"] if "date" in b else __import__("datetime").datetime.fromtimestamp(b["date_ms"]/1000).strftime("%Y-%m-%d") for b in bars]
closes = [b["close"] if "close" in b else b["close_price"] for b in bars]

# ================= 渲染 =================
def snap_rows():
    s = SNAP
    items = [("开盘", s["open"]), ("最高", s["high"]), ("最低", s["low"]), ("昨收", s["prev"]),
             ("成交额", f"{s['turnover']/1e8:.1f}亿"), ("总市值", f"{s['mcap']:.0f}亿"),
             ("PE(TTM)", s["pe"]), ("PB(MRQ)", s["pb"]), ("PS(TTM)", s["ps"]), ("PCF(TTM)", s["pcf"]),
             ("近1年涨跌", f"{s['hist_chg_1y']:+.0f}%"), ("52周区间", f"{s['lo_52']:.1f}~{s['hi_52']:.1f}")]
    out = []
    for k, v in items:
        cls = ""
        if k == "近1年涨跌":
            cls = ' style="color:var(--red);font-weight:800"' if SNAP["hist_chg_1y"] > 0 else ' style="color:var(--green);font-weight:800"'
        out.append(f'<div class="kv" style="padding:5px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 76px">{k}</span><b{cls}>{v}</b></div>')
    return "".join(out)

def fin_svg():
    """5年营收/归母双柱"""
    W, H, P = 880, 260, 60
    ys = [y for y, _, _ in FIN_Y]
    revs = [r for _, r, _ in FIN_Y]
    nps = [n for _, _, n in FIN_Y]
    maxv = max(max(revs), max(abs(n) for n in nps)) * 1.2
    bw = (W - 2 * P) / len(ys)
    parts = []
    for i, y in enumerate(ys):
        cx = P + bw * i + bw / 2
        h1 = revs[i] / maxv * (H - 70)
        parts.append(f'<rect x="{cx-34:.1f}" y="{H-40-h1:.1f}" width="28" height="{h1:.1f}" rx="4" fill="#1f3a93" opacity="0.85"/>')
        parts.append(f'<text x="{cx-20:.1f}" y="{H-40-h1-4:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#1f3a93">{revs[i]:.0f}</text>')
        h2 = nps[i] / maxv * (H - 70)
        c2 = "#e5484d" if nps[i] > 0 else "#2fa36b"
        parts.append(f'<rect x="{cx+6:.1f}" y="{H-40-h2:.1f}" width="28" height="{max(h2,2):.1f}" rx="4" fill="{c2}" opacity="0.85"/>')
        parts.append(f'<text x="{cx+20:.1f}" y="{H-40-h2-4:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="{c2}">{nps[i]:.1f}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{H-16}" text-anchor="middle" font-size="11.5" fill="#6b7280">{y}</text>')
    parts.append(f'<text x="{P+8}" y="16" font-size="11.5" font-weight="700" fill="#1f3a93">营收（亿）</text>')
    parts.append(f'<text x="{P+90}" y="16" font-size="11.5" font-weight="700" fill="#e5484d">归母净利（亿）</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="近五年营收与归母净利润">{"" .join(parts)}</svg>'

def val_rows():
    v = VAL
    out = [f'<div class="kv" style="padding:5px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 110px">PE(TTM)</span><b>{v["pe"]}</b> <span style="color:var(--ink-3);font-size:11px">vs 同行中位 {v["pe_med"]}</span></div>',
           f'<div class="kv" style="padding:5px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 110px">PB(MRQ)</span><b>{v["pb"]}</b></div>',
           f'<div class="kv" style="padding:5px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 110px">PS(TTM)</span><b>{v["ps"]}</b></div>',
           f'<div class="kv" style="padding:5px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 110px">__FC_Y1__ forward PE</span><b style="color:var(--red)">{v["pe_fwd"]}</b></div>']
    return "".join(out)

def peer_rows():
    rows = ""
    for name, pe, pb, self_flag in VAL["peers"]:
        hl = ' style="background:#fdf9ec"' if self_flag else ""
        rows += f'<tr{hl}><td><b>{name}</b></td><td class="num">{pe:.1f}</td><td class="num">{pb:.2f}</td></tr>'
    return rows

def scen_rows():
    rows = ""
    for name, np_, note in FC["scenarios"]:
        cls = "sum-tag" if name == "乐观" else "sum-tag2"
        rows += f'<tr><td><span class="{cls}">{name}</span></td><td class="num" style="font-weight:700">{np_}亿</td><td style="font-size:11px;color:var(--ink-2)">{note}</td></tr>'
    return rows

def catalyst_rows():
    rows = ""
    for ev, t, desc in CATALYST:
        rows += f'<tr><td style="font-weight:600">{ev}</td><td class="num" style="color:var(--ink-2);white-space:nowrap">{t}</td><td style="font-size:11.5px;color:var(--ink-2)">{desc}</td></tr>'
    return rows

def env_rows():
    e = ENV
    return (f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 76px">板块位置</span><b>{e["sector_pos"]}</b></div>'
            f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12px;color:var(--ink-2)">{e["sector_note"]}</div>'
            f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 76px">市场情绪</span><b>{e["sentiment"]}</b></div>'
            f'<div class="kv" style="padding:6px 0;font-size:12px;color:var(--ink-2)">{e["sentiment_note"]}</div>')

def inst_rows():
    i = INST
    return (f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px"><span style="color:var(--ink-2);flex:0 0 76px">基金持股</span><b>{i["fund_pct"]}%</b></div>'
            f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12px;color:var(--ink-2)">{i["fund_note"]}</div>'
            f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12px;color:var(--ink-2)">{i["north_note"]}</div>'
            f'<div class="kv" style="padding:6px 0;font-size:12px;color:var(--ink-2)">{i["lhb_note"]}</div>')

def guide_rows():
    rows = ""
    for tag, desc in GUIDE:
        cls = "sum-tag" if tag == "结论" else "sum-tag2"
        rows += f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>'
    return rows

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全面分析__NAME__</title>
<style>
  :root{ --brand:#1f3a93; --brand-soft:#eef2fb; --gold:#c9a227; --gold-soft:#fdf9ec;
    --red:#e5484d; --green:#2fa36b; --ink:#1d2433; --ink-2:#5b6470; --ink-3:#9aa1ad;
    --border:#e8eaee; --bg:#f4f5f7; --shadow-sm:0 1px 3px rgba(16,24,40,.06); --shadow-md:0 4px 14px rgba(16,24,40,.08); }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;padding:28px 20px 40px}
  .num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum"}
  .wrap{max-width:980px;margin:0 auto}
  .card{background:#fff;border:1px solid var(--border);border-radius:14px;padding:18px 20px;margin-bottom:16px;box-shadow:var(--shadow-sm);transition:box-shadow .18s,transform .18s}
  .card:hover{box-shadow:var(--shadow-md);transform:translateY(-1px)}
  .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  @media(max-width:760px){.grid-2{grid-template-columns:1fr}}
  .sec{display:flex;align-items:baseline;gap:10px;margin:26px 0 12px;flex-wrap:wrap}
  .sec h2{font-size:17px;color:var(--ink);font-weight:800}
  .sec .no{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:22px;padding:0 6px;border-radius:6px;background:linear-gradient(135deg,#e8b83a,#c9a227);color:#fff;font-size:12px;font-weight:800}
  .sec .hint{font-size:11.5px;color:var(--ink-3);font-weight:400}
  table{width:100%;border-collapse:collapse;font-size:12.5px}
  th{background:#f7f8fa;color:var(--ink-2);font-weight:600;font-size:11px;padding:7px 8px;text-align:left;border-bottom:1px solid var(--border)}
  td{padding:7px 8px;border-bottom:1px dashed #f0f1f4}
  tbody tr:hover{background:#f7f9fd}
  .vbadge{display:inline-block;font-size:15px;font-weight:800;padding:4px 18px;border-radius:24px;color:#fff;background:linear-gradient(135deg,#2fa36b,#27905f);border:1px solid #27905f;box-shadow:0 2px 8px rgba(47,163,107,.25)}
  .vbadge.gd{background:linear-gradient(135deg,#e5484d,#c0392b);border-color:#c0392b;box-shadow:0 2px 8px rgba(229,72,77,.25)}
  .hero{background:linear-gradient(135deg,#1f3a93 0%,#2a4db8 60%,#3358c9 100%);border-radius:16px;padding:22px 24px;color:#fff;position:relative;overflow:hidden}
  .hero::after{content:"";position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(201,162,39,.35),transparent 70%)}
  .hero .title{font-size:22px;font-weight:800;letter-spacing:.5px}
  .hero .tcode{font-size:13px;color:rgba(255,255,255,.65);font-weight:600;margin-left:8px}
  .hero .sub{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}
  .pill{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px}
  .pill.gold{background:rgba(201,162,39,.2);color:#f5d47a;border:1px solid rgba(201,162,39,.4)}
  .pill.brand{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.25)}
  .insight{margin-top:12px;padding:10px 14px;border-radius:10px;background:linear-gradient(120deg,#fdf9ec,#faf3d8);border:1px solid #eddcab;font-size:12.5px;font-weight:600;color:#8a6d12;line-height:1.7}
  .kv{display:flex;justify-content:space-between;align-items:baseline;padding:5px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px}
  .sum-row{display:flex;align-items:baseline;gap:8px;padding:9px 0;border-bottom:1px dashed #f0f1f4;font-size:13px;flex-wrap:wrap}
  .sum-row:last-child{border-bottom:none}
  .sum-tag{flex-shrink:0;font-size:11px;font-weight:800;color:#fff;background:linear-gradient(180deg,var(--gold),#a8871d);border-radius:5px;padding:2px 9px;white-space:nowrap}
  .sum-tag2{flex-shrink:0;font-size:11px;font-weight:800;color:var(--brand);background:var(--brand-soft);border:1px solid #d5def5;border-radius:5px;padding:2px 9px;white-space:nowrap}
  .note{font-size:11px;color:var(--ink-3);margin-top:14px;line-height:1.7}
  @media print{body{background:#fff}.card{box-shadow:none;border-color:#ddd}}
</style>
</head>
<body>
<div class="wrap">

  <div class="hero">
    <div class="title">__NAME__ <span class="tcode">__TITLE_SUB__</span></div>
    <div class="sub">
      <span class="pill gold">__DATE_SHOW__</span>
      <span class="pill brand">__NAME__ · __CODE__</span>
      <span class="pill brand">__SECTOR__</span>
    </div>
  </div>

  <div class="sec"><h2><span class="no">01</span>总览</h2><span class="hint">多能力整合 · 模型输出 [MODEL]</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:10px">
      <span class="vbadge__VBADGE_CLASS__">__VERDICT__</span>
      <span style="font-size:13px;color:var(--ink);font-weight:700">__NAME__ <span style="color:var(--ink-2);font-weight:400">现价 __PX__（__CHG__）</span></span>
    </div>
    <div style="font-size:13px;color:var(--ink-2);line-height:1.8">__VERDICT_NOTE__</div>
  </div>

  <div class="sec"><h2><span class="no">02</span>公司速览</h2><span class="hint">行情快照 · 主营构成 · 简介</span></div>
  <div class="grid-2">
    <div class="card"><h3 style="font-size:14px;margin-bottom:8px">行情快照</h3>__SNAP_ROWS__</div>
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:8px">主营构成</h3>
      <div style="font-size:13px;font-weight:700;color:var(--brand)">__BIZ_MAIN__</div>
      <div style="font-size:12.5px;color:var(--ink-2);line-height:1.8;margin-top:8px">__BIZ_INTRO__</div>
      <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">__BIZ_TAGS__</div>
    </div>
  </div>

  <div class="sec"><h2><span class="no">03</span>财务分析</h2><span class="hint">近5年营收/归母 · 最新季度亮点</span></div>
  <div class="card">__FIN_SVG__
    <div style="display:flex;gap:18px;margin-top:12px;flex-wrap:wrap">
      <div style="flex:1;min-width:200px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px 12px">
        <div style="font-size:11px;color:var(--ink-3)">最新季度营收 / 同比</div>
        <div style="font-size:17px;font-weight:800;color:var(--brand)">__FIN_Q_REV__ <span style="font-size:12px;color:var(--red)">__FIN_Q_REV_YOY__</span></div>
      </div>
      <div style="flex:1;min-width:200px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px 12px">
        <div style="font-size:11px;color:var(--ink-3)">最新季度归母 / 同比</div>
        <div style="font-size:17px;font-weight:800;color:var(--red)">__FIN_Q_NP__ <span style="font-size:12px;color:var(--red)">__FIN_Q_NP_YOY__</span></div>
      </div>
      <div style="flex:1;min-width:200px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px 12px">
        <div style="font-size:11px;color:var(--ink-3)">毛利率 / ROE</div>
        <div style="font-size:17px;font-weight:800;color:var(--ink)">__FIN_Q_GM__ <span style="font-size:12px;color:var(--ink-2)">/ __FIN_Q_ROE__</span></div>
      </div>
    </div>
    <div class="insight">💡 __FIN_Q_NOTE__</div>
  </div>

  <div class="sec"><h2><span class="no">04</span>估值分析</h2><span class="hint">当前估值 vs 同行 · forward PE</span></div>
  <div class="grid-2">
    <div class="card"><h3 style="font-size:14px;margin-bottom:8px">估值指标</h3>__VAL_ROWS__
      <div class="insight">💡 __VAL_NOTE__</div>
    </div>
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:8px">__PEER_TITLE__</h3>
      <table><tr><th>公司</th><th>PE(TTM)</th><th>PB</th></tr>__PEER_ROWS__</table>
    </div>
  </div>

  <div class="sec"><h2><span class="no">05</span>成长预测</h2><span class="hint">券商一致预期 · 三情景 · WebSearch 公开披露</span></div>
  <div class="card">
    <div style="display:flex;gap:14px;margin-bottom:10px;flex-wrap:wrap">
      <div style="flex:1;min-width:150px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px;text-align:center">
        <div style="font-size:11px;color:var(--ink-3)">__FC_Y1__ 归母</div><div style="font-size:18px;font-weight:800;color:var(--red)">__FC_Y26__亿</div></div>
      <div style="flex:1;min-width:150px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px;text-align:center">
        <div style="font-size:11px;color:var(--ink-3)">__FC_Y23__</div><div style="font-size:18px;font-weight:800;color:var(--ink)">__FC_Y27__ / __FC_Y28__亿</div></div>
      <div style="flex:1;min-width:150px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px;text-align:center">
        <div style="font-size:11px;color:var(--ink-3)">__FC_Y1__ forward PE</div><div style="font-size:18px;font-weight:800;color:var(--brand)">__FC_FWD_PE__倍</div></div>
      <div style="flex:1;min-width:150px;background:#fbfcfe;border:1px solid var(--border);border-radius:10px;padding:10px;text-align:center">
        <div style="font-size:11px;color:var(--ink-3)">机构目标价</div><div style="font-size:18px;font-weight:800;color:var(--gold)">__FC_TARGET__元</div></div>
    </div>
    <table><tr><th>情景</th><th>__FC_Y1__ 归母</th><th>假设</th></tr>__SCEN_ROWS__</table>
    <div class="insight">💡 __FC_NOTE__</div>
  </div>

  <div class="sec"><h2><span class="no">06</span>业绩前瞻与催化剂</h2><span class="hint">披露/订单/事件跟踪</span></div>
  <div class="card">
    <table><tr><th>催化剂</th><th>时点</th><th>说明</th></tr>__CATALYST_ROWS__</table>
  </div>

  <div class="sec"><h2><span class="no">07</span>市场环境</h2><span class="hint">板块位置 · 市场情绪</span></div>
  <div class="card">__ENV_ROWS__</div>

  <div class="sec"><h2><span class="no">08</span>机构与资金</h2><span class="hint">基金/北向/龙虎榜 · WebSearch 公开披露</span></div>
  <div class="card">__INST_ROWS__</div>

  <div class="sec"><h2><span class="no">09</span>风险清单</h2><span class="hint">模型输出 [MODEL]</span></div>
  <div class="card">__RISK_ROWS__</div>

  <div class="sec"><h2><span class="no">10</span>投资指导</h2><span class="hint">综合结论 · 仅供研究参考</span></div>
  <div class="card">__GUIDE_ROWS__</div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

def main():
    tags = "".join(f'<span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;background:var(--brand-soft);color:var(--brand);border:1px solid #d5def5">{t}</span>' for t in BIZ["tags"])
    risk_rows = "".join(f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:12.5px;color:var(--ink-2)">⚠️ {r}</div>' for r in RISK)
    verdict_good = CONFIG["verdict_short"] in ("成长", "低估", "买入")
    html = TPL
    html = (html.replace("__DATE_SHOW__", f"{DATE.replace('-', '')}")
            .replace("__TITLE_SUB__", TITLE_SUB)
            .replace("__NAME__", CONFIG["name"]).replace("__CODE__", CONFIG["code"])
            .replace("__SECTOR__", CONFIG["sector"])
            .replace("__VERDICT__", CONFIG["verdict"])
            .replace("__VBADGE_CLASS__", "" if verdict_good else " gd")
            .replace("__PX__", f"{CONFIG['px']:.2f}").replace("__CHG__", f"{CONFIG['chg_pct']:+.2f}%")
            .replace("__VERDICT_NOTE__", CONFIG["verdict_note"])
            .replace("__SNAP_ROWS__", snap_rows())
            .replace("__BIZ_MAIN__", BIZ["main"]).replace("__BIZ_INTRO__", BIZ["intro"]).replace("__BIZ_TAGS__", tags)
            .replace("__FIN_SVG__", fin_svg())
            .replace("__FIN_Q_REV__", f"{FIN_Q['rev']:.1f}").replace("__FIN_Q_REV_YOY__", FIN_Q["rev_yoy"])
            .replace("__FIN_Q_NP__", f"{FIN_Q['np']:.1f}").replace("__FIN_Q_NP_YOY__", FIN_Q["np_yoy"])
            .replace("__FIN_Q_GM__", f"{FIN_Q['gm']:.1f}%").replace("__FIN_Q_ROE__", f"{FIN_Q['roe']:.1f}%")
            .replace("__FIN_Q_NOTE__", FIN_Q["note"])
            .replace("__VAL_ROWS__", val_rows()).replace("__VAL_NOTE__", VAL["note"])
            .replace("__PEER_ROWS__", peer_rows())
            .replace("__FC_Y26__", str(FC["y26"])).replace("__FC_Y27__", str(FC["y27"])).replace("__FC_Y28__", str(FC["y28"]))
            .replace("__FC_FWD_PE__", str(FC["fwd_pe"])).replace("__FC_TARGET__", str(FC["target"]))
            .replace("__FC_NOTE__", FC["note"]).replace("__SCEN_ROWS__", scen_rows())
            .replace("__CATALYST_ROWS__", catalyst_rows())
            .replace("__ENV_ROWS__", env_rows())
            .replace("__INST_ROWS__", inst_rows())
            .replace("__RISK_ROWS__", risk_rows)
            .replace("__GUIDE_ROWS__", guide_rows())
            .replace("__NOTE__", NOTE)
            .replace("__PEER_TITLE__", PEER_TITLE)
            .replace("__FC_Y1__", FC_Y1)
            .replace("__FC_Y23__", FC_Y23))
    out_path = os.path.join(BASE, f"全面分析_{CONFIG['name']}_{DATE.replace('-', '')}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK ->", out_path, "| size:", len(html.encode("utf-8")))

if __name__ == "__main__":
    main()
