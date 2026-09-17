# -*- coding: utf-8 -*-
"""A股个股财务预测器 HTML 生成器 v1.0（模板）
【模板使用说明】生成某股票"未来 3 年营收/利润会怎样？"财务预测器：
①hithink CLI 拉近5年利润表(financials income annual) + 最新季度 + 财务指标(毛利率/ROE/增速)
②WebSearch 查行业驱动（订单/产能/价格）与券商一致预期/分机构预测 → 作为三情景锚点
③三情景假设（乐观/中性/悲观：营收增速+净利率），中性贴近券商区间中枢
④替换 BASE/DATE/WEEKDAY 与数据区（CFG/HIST_YEARS/SCENARIOS/SENS/DRIVERS/BROKERS/RISK/SUMMARY/NOTE）⑤运行 → 输出 `财务预测器_{名称}_{YYYYMMDD}.html`
口径：预测为【模型输出】基于历史报表+公开研报假设外推，标 [MODEL]/[ASSUMED]；券商预测来自公开研报（页脚标注来源，数据来源铁律）；
换标的前 grep 旧标的名清理残留（insight 全部在数据区）
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-08-21"
WEEKDAY = "周五"

# ================= 数据 =================
CFG = {
    "name": "亨通光电", "code": "600487.SH", "sector": "通信设备", "sector_icon": "🔌",
    "px": 62.18, "chg_pct": 0.26, "base_year": 2025, "base_rev": 668.55, "base_np": 26.80,
    "base_gm": 13.18, "latest": "2026 一季报", "q_rev": 177.91, "q_rev_yoy": "+34.09%",
    "q_np": 11.05, "q_np_yoy": "+98.53%", "q_gm": 15.98,
    "verdict": "高增长·拐点确认", "verdict_short": "高增",
    "verdict_note": ("2025 归母 26.8 亿（-3.2%）筑底后，2026Q1 营收 +34%/归母 +98.5% 确认业绩拐点；"
                     "AI 数据中心光纤需求爆发 + 海缆订单兑现 + 光纤涨价驱动，券商一致预期 2026E 归母 79 亿（+196%）；"
                     "三情景中枢 2026E 归母 42-50 亿，2028E 中枢 70-85 亿——未来 3 年高成长确定性较强，核心变量是光纤价格与海缆交付节奏。"),
}
# 历史业绩（近5年）
HIST_YEARS = [
    (2021, 412.71, 14.36, "-11.2%", "-5.9%"), (2022, 464.64, 15.86, "+12.6%", "+10.4%"),
    (2023, 476.22, 21.54, "+2.5%", "+35.8%"), (2024, 599.84, 27.69, "+26.0%", "+28.6%"),
    (2025, 668.55, 26.80, "+11.5%", "-3.2%"),
]
# 三情景预测（2026-2028 营收/归母，亿元）
SCENARIOS = {
    "乐观": {"rev": [850, 1000, 1150], "np": [50, 68, 85], "desc": "AI 光纤需求超预期+海缆集中交付+光模块放量（高盛/中信建投/大摩口径）"},
    "中性": {"rev": [800, 930, 1060], "np": [45, 60, 78], "desc": "光纤涨价+海缆订单稳步兑现（券商一致预期中枢下修）"},
    "悲观": {"rev": [720, 810, 890], "np": [32, 45, 58], "desc": "光纤价格回落+海缆交付延迟+地缘扰动（东兴等保守口径）"},
}
# 敏感性矩阵（2028E 归母净利：营收 × 净利率，亿元）
SENS_ROWS = ["营收 890（悲观）", "营收 1060（中性）", "营收 1150（乐观）"]
SENS_COLS = ["净利率 5.0%（悲观）", "净利率 6.5%（中性）", "净利率 8.0%（乐观）"]
SENS = [[44.5, 57.9, 71.2], [53.0, 68.9, 84.8], [57.5, 74.8, 92.0]]
# 成长驱动因素
DRIVERS = [
    ("🧠 AI 数据中心", "AI 数据中心光纤", "AI 先进光纤材料研发中心扩产（空芯/超低损/多芯光纤），G.657 单模光纤供不应求，光纤价格持续上行"),
    ("🌊 海缆订单", "全球海缆「新旧更替期」", "+海上风电，在手订单超 270 亿（能源 200 亿+海洋通信 70 亿+PEACE 跨洋 3 亿美元）"),
    ("📡 光模块", "800G/1.6T 光模块", "800G 光模块批量交付、1.6T 加速量产，AI 算力互联高速升级"),
    ("⚙️ 盈利结构", "毛利率修复", "高毛利业务（海缆/光模块/特种光纤）占比提升，毛利率从 13.2% 向 18-21% 修复"),
]
# 券商预测对照（公开研报）
BROKERS = [
    ("一致预期(26家)", 79.3, 93.7, 107.5),
    ("高盛", 42.0, 60.0, 83.0),
    ("中信证券", 40.0, 57.0, 78.0),
    ("中信建投", 48.0, 68.0, None),
    ("摩根士丹利", 50.0, 66.0, None),
    ("东兴证券", 52.3, 61.0, None),
]
RISK = [
    "预测为模型输出 [MODEL]：基于历史报表+公开研报假设外推，实际经营存在较大偏差可能",
    "光纤价格波动是最大变量：涨价不及预期则 2026 利润弹性大幅缩水（悲观情景 32 亿 vs 乐观 50 亿，差 56%）",
    "海缆交付节奏依赖全球地缘局势与海上风电装机进度，存在延期风险",
    "一致预期 2026E 归母 79 亿（+196%）分歧巨大（40-79 亿），含少数激进机构拉高，建议以 42-50 亿中枢参考",
    "2025 归母下滑含阶段性因素（光通信价格低谷/海缆确认节奏），若修复不及预期则拐点逻辑受挑战",
]
SUMMARY = [
    ("结论", "未来 3 年高成长：三情景中枢 2026E 归母 42-50 亿（+57%~+87%）、2028E 70-85 亿（较 2025 增长 1.6-2.2 倍）——AI 光纤+海缆双轮驱动，拐点已确认。"),
    ("历史", "营收 5 年 CAGR 12.8%（412.7→668.6 亿），2024 提速至 +26%；归母 2024 见顶 27.7 亿、2025 筑底 -3.2%——2026 起进入新增长周期。"),
    ("驱动", "AI 数据中心光纤（空芯/超低损）供不应求+光纤涨价、海缆在手订单 270 亿+、800G/1.6T 光模块放量——三重驱动下毛利结构向 18-21% 修复。"),
    ("券商", "分机构预测分歧大（2026E 40-79 亿）：高盛 42/中信 40/建投 48/大摩 50/东兴 52 亿——一致预期含激进机构，中性建议取 45 亿中枢。"),
    ("敏感性", "2028E 归母对营收×净利率敏感：区间 44.5-92.0 亿——乐观（1150 亿×8%）vs 悲观（890 亿×5%）差 107%，预测区间宽度大，重仓需跟踪季度兑现。"),
]
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，financials income annual/quarterly + indicators）；"
        "券商预测来自高盛/中信证券/中信建投/摩根士丹利/东兴证券公开研报与同花顺一致预期（2026-08）；"
        "三情景预测为模型输出 [MODEL]/[ASSUMED]，基于历史报表与公开研报假设外推，非公司指引。"
        "仅供研究参考，不构成个人投资建议。")

# ---- 模板占位默认值：skill 自带数据区（保证脚本可独立运行；平台渲染时本区被 caps 整体替换）----
CHG_TXT = ("+" if CFG["chg_pct"] >= 0 else "") + f"{CFG['chg_pct']:.2f}"
SCEN_YEARS = [2026, 2027, 2028]
SENS_HINT = "2028E 归母净利对营收 × 净利率 · 亿元"
HIST_INSIGHT = "💡 营收 5 年 CAGR 12.8%，2024 年提速至 +26%；归母 2024 见顶 27.7 亿后 2025 筑底 -3.2%——2026Q1 营收+34%/归母+98.5% 确认业绩拐点，进入新增长周期。"
DRIVER_HINT = "模型假设 · AI 光纤/海缆/光模块三重驱动"
DRIVER_INSIGHT = "💡 三重驱动共振下毛利率从 13.2%（2025）向 18-21% 修复——高毛利业务占比提升是净利弹性大于营收弹性的核心。"
SCEN_INSIGHT = "💡 三情景中枢 2026E 归母 42-50 亿、2028E 70-85 亿——乐观（1150×8%）vs 悲观（890×5%）2028E 差 107%，预测区间宽，重仓需跟踪季度兑现。"
SENS_INSIGHT = "💡 区间 44.5~92.0 亿（差 107%）——净利率每提升 1.5pct ≈ 归母 +16 亿；高毛利业务兑现进度是预测的核心敏感项。"
BROKER_INSIGHT = "💡 分机构预测 2026E 分歧巨大（40-79 亿）——一致预期含激进机构拉高，中性建议取 42-50 亿中枢；机构评级 100% 买入/增持，综合目标价 93.31 元（+50% 空间）。"

# ================= 渲染 =================
def hist_rows():
    rows = ""
    for y, rev, np_, ry, ny in HIST_YEARS:
        ryc = "var(--red)" if "+" in ry else "var(--green)"
        nyc = "var(--red)" if "+" in ny else "var(--green)"
        rows += (f'<tr><td class="num" style="color:var(--ink-3)">{y}</td>'
                 f'<td class="num">{rev:.1f}</td><td class="num" style="color:{ryc}">{ry}</td>'
                 f'<td class="num" style="font-weight:700">{np_:.2f}</td>'
                 f'<td class="num" style="color:{nyc}">{ny}</td></tr>')
    return rows

def hist_bar():
    """近5年营收/归母双柱状图"""
    W, H, P = 880, 260, 60
    maxv = max(r for _, r, _, _, _ in HIST_YEARS) * 1.15
    n = len(HIST_YEARS)
    bw = (W - 2 * P) / n
    parts = []
    for i, (y, rev, np_, _, _) in enumerate(HIST_YEARS):
        cx = P + bw * i + bw / 2
        hr = (rev / maxv) * (H - 70)
        hn = (np_ / maxv * 6) * (H - 70)  # 归母放大6倍便于对比（营收 vs 净利量级差）
        parts.append(f'<rect x="{cx-26:.1f}" y="{H-40-hr:.1f}" width="20" height="{hr:.1f}" rx="4" fill="#1f3a93"/>')
        parts.append(f'<rect x="{cx+6:.1f}" y="{H-40-hn:.1f}" width="20" height="{hn:.1f}" rx="4" fill="#c9a227"/>')
        parts.append(f'<text x="{cx-16:.1f}" y="{H-40-hr-6:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1f3a93">{rev:.0f}</text>')
        parts.append(f'<text x="{cx+16:.1f}" y="{H-40-hn-6:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="#b08d1c">{np_:.0f}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{H-14}" text-anchor="middle" font-size="12" fill="#6b7280">{y}</text>')
    parts.append(f'<text x="{P+6}" y="16" font-size="11.5" fill="#1f3a93">营收(亿·深蓝)</text>')
    parts.append(f'<text x="{P+110}" y="16" font-size="11.5" fill="#b08d1c">归母净利(亿·金，×6放大)</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="近五年营收与归母净利润">{"" .join(parts)}</svg>'

def scen_table():
    yrs = SCEN_YEARS
    rows = ""
    for sname, sd in SCENARIOS.items():
        cls = {"乐观": "sum-tag", "中性": "sum-tag2", "悲观": "sum-tag2"}[sname]
        cells = ""
        for i, y in enumerate(yrs):
            cells += f'<td class="num"><b>{sd["rev"][i]:.0f}</b> / <span style="color:var(--red);font-weight:700">{sd["np"][i]:.0f}亿</span></td>'
        rows += f'<tr><td><span class="{cls}">{sname}</span></td>{cells}<td style="font-size:11px;color:var(--ink-2)">{sd["desc"]}</td></tr>'
    return rows

def scen_bar():
    """三情景归母净利分组柱状图（2026-2028）"""
    W, H, P = 880, 280, 70
    yrs = SCEN_YEARS
    colors = {"乐观": "#e5484d", "中性": "#c9a227", "悲观": "#2fa36b"}
    maxv = max(max(SCENARIOS[s]["np"]) for s in SCENARIOS) * 1.2
    bw = (W - 2 * P) / 3
    parts = []
    for i, y in enumerate(yrs):
        cx = P + bw * i + bw / 2
        for j, sname in enumerate(["乐观", "中性", "悲观"]):
            v = SCENARIOS[sname]["np"][i]
            x = cx - 42 + j * 28
            h = (v / maxv) * (H - 60)
            parts.append(f'<rect x="{x:.1f}" y="{H-40-h:.1f}" width="20" height="{h:.1f}" rx="4" fill="{colors[sname]}" opacity="0.88"/>')
            parts.append(f'<text x="{x+10:.1f}" y="{H-40-h-5:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="{colors[sname]}">{v:.0f}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{H-14}" text-anchor="middle" font-size="12" fill="#6b7280">{y}E</text>')
    parts.append(f'<text x="{P+6}" y="16" font-size="11.5" fill="#e5484d">乐观</text>')
    parts.append(f'<text x="{P+60}" y="16" font-size="11.5" fill="#c9a227">中性</text>')
    parts.append(f'<text x="{P+114}" y="16" font-size="11.5" fill="#2fa36b">悲观</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="未来三年归母净利三情景预测（亿元）">{"" .join(parts)}</svg>'

def sens_table():
    rows = ""
    for i, r in enumerate(SENS_ROWS):
        cells = ""
        for j, c in enumerate(SENS_COLS):
            v = SENS[i][j]
            color = "var(--red)" if v >= 70 else ("var(--gold)" if v >= 55 else "var(--green)")
            cells += f'<td class="num" style="color:{color};font-weight:800">{v:.1f}</td>'
        rows += f'<tr><td style="color:var(--ink-2)">{r}</td>{cells}</tr>'
    return rows

def driver_rows():
    out = ""
    for icon, title, desc in DRIVERS:
        out += f'<div class="kv"><span class="k">{icon} {title}</span><span class="v" style="color:var(--ink-2);font-size:12px;max-width:62%;text-align:right">{desc}</span></div>'
    return out

def broker_rows():
    rows = ""
    for name, y26, y27, y28 in BROKERS:
        c28 = f'{y28:.1f}亿' if y28 else "--"
        rows += (f'<tr><td><b>{name}</b></td>'
                 f'<td class="num" style="font-weight:700">{y26:.1f}亿</td>'
                 f'<td class="num">{y27:.1f}亿</td>'
                 f'<td class="num">{c28}</td></tr>')
    return rows

def risk_rows():
    out = []
    for i, r in enumerate(RISK, 1):
        out.append(f'<div class="sum-row"><span class="sum-tag2">风险{i}</span><span style="color:var(--ink-2)">{r}</span></div>')
    return "".join(out)

def summary_rows():
    out = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag == "结论" else "sum-tag2"
        out.append(f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>')
    return "".join(out)

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>财务预测器_{NAME}_{DATE}</title>
<style>
  :root {
    --brand:#1f3a93; --brand-2:#2f56c9; --brand-soft:#eef1fa;
    --gold:#c9a227; --gold-soft:#faf5e3;
    --red:#e5484d; --green:#2fa36b;
    --bg:#f4f5f7; --surface:#ffffff; --border:#e8eaee;
    --ink:#18202f; --ink-2:#5b6470; --ink-3:#9aa1ad;
    --radius:14px;
    --shadow-sm:0 1px 3px rgba(24,32,47,.06);
    --shadow-md:0 6px 20px rgba(24,32,47,.08);
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--ink); font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; font-size:14px; line-height:1.6; }
  .wrap { max-width:960px; margin:0 auto; padding:24px 20px 60px; }
  .num { font-variant-numeric:tabular-nums; font-feature-settings:"tnum"; }
  .code-mini { font-size:11px; color:var(--ink-3); font-weight:400; }
  .pill { display:inline-block; font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px; }
  .pill.brand { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
  .pill.gold { background:var(--gold-soft); color:#8a6d12; border:1px solid #eddcab; }
  .vbadge { display:inline-block; font-size:15px; font-weight:800; padding:4px 18px; border-radius:24px; border:1px solid; color:var(--red); background:#fdeeee; border-color:#e5484d33; }
  .hero { background:linear-gradient(150deg,#ffffff 30%,#fbfcfe 100%); border:1px solid var(--border); border-radius:18px; box-shadow:var(--shadow-md); padding:24px 28px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px; position:relative; overflow:hidden; }
  .hero::before { content:""; position:absolute; right:-70px; top:-70px; width:240px; height:240px; border-radius:50%; background:radial-gradient(circle,rgba(201,162,39,.12),transparent 65%); }
  .hero::after { content:""; position:absolute; left:-50px; bottom:-90px; width:200px; height:200px; border-radius:50%; background:radial-gradient(circle,rgba(31,58,147,.06),transparent 70%); }
  .hero .big { position:relative; z-index:1; }
  .hero .title { font-size:24px; font-weight:800; letter-spacing:-.5px; }
  .hero .tcode { font-size:14px; color:var(--ink-3); font-weight:600; letter-spacing:.5px; margin-left:8px; vertical-align:3px; }
  .hero .sub { margin-top:8px; font-size:12.5px; color:var(--ink-3); }
  .hero .sub .pill { margin-right:6px; }
  .hero .kpis { display:flex; gap:24px; position:relative; z-index:1; flex-wrap:wrap; }
  .hero .kpi { text-align:right; }
  .hero .kpi .v { font-size:17px; font-weight:800; }
  .hero .kpi .v.up { color:var(--red); } .hero .kpi .v.dn { color:var(--green); } .hero .kpi .v.gd { color:var(--gold); }
  .hero .kpi .k { font-size:11.5px; color:var(--ink-3); margin-top:2px; }
  .sec { display:flex; align-items:center; justify-content:space-between; margin:30px 2px 12px; }
  .sec h2 { font-size:15px; font-weight:700; letter-spacing:.2px; display:flex; align-items:center; gap:9px; }
  .sec h2 .no { font-size:11px; font-weight:800; color:#fff; background:linear-gradient(180deg,var(--gold),#a8871d); border-radius:5px; padding:2px 6px; letter-spacing:0; }
  .sec h2::after { content:""; width:4px; height:16px; border-radius:2px; background:linear-gradient(180deg,var(--gold),var(--brand)); }
  .sec .hint { font-size:12px; color:var(--ink-3); font-weight:400; }
  .card { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px 18px; box-shadow:var(--shadow-sm); }
  .card h3 { font-size:13.5px; font-weight:700; margin-bottom:8px; display:flex; align-items:center; gap:8px; }
  .card h3 .unit { font-size:11px; color:var(--ink-3); font-weight:400; }
  .grid-2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { text-align:left; font-size:11.5px; color:var(--ink-3); font-weight:600; padding:6px 8px; border-bottom:2px solid var(--border); }
  td { padding:8px; border-bottom:1px dashed #f0f1f4; vertical-align:middle; }
  tbody tr:nth-child(even) { background:#fafbfc; }
  tbody tr:hover { background:var(--brand-soft); }
  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink); font-weight:600; }
  .insight { margin-top:12px; padding:10px 14px; border-radius:10px; background:linear-gradient(120deg,#fdf9ec,#faf3d8); border:1px solid #eddcab; font-size:12.5px; font-weight:600; color:#8a6d12; line-height:1.7; }
  .sum-row { display:flex; align-items:baseline; gap:8px; padding:9px 0; border-bottom:1px dashed #f0f1f4; font-size:13px; flex-wrap:wrap; }
  .sum-row:last-child { border-bottom:none; }
  .sum-tag { flex-shrink:0; font-size:11px; font-weight:800; color:#fff; background:linear-gradient(180deg,var(--gold),#a8871d); border-radius:5px; padding:2px 9px; white-space:nowrap; }
  .sum-tag2 { flex-shrink:0; font-size:11px; font-weight:800; color:var(--brand); background:var(--brand-soft); border:1px solid #d5def5; border-radius:5px; padding:2px 9px; ; white-space:nowrap; }
  .note { font-size:11px; color:var(--ink-3); margin-top:16px; line-height:1.8; border-top:1px dashed var(--border); padding-top:12px; }
  @media print { body{background:#fff} .card{box-shadow:none} }
  @media (max-width:760px) { .hero{flex-direction:column;align-items:flex-start} .hero .kpis{width:100%;justify-content:space-between} }
</style>
</head>
<body>
<div class="wrap">
  <!-- Hero -->
  <div class="hero">
    <div class="big">
      <div class="title">__NAME__ <span class="tcode">__CODE__</span></div>
      <div class="sub">
        <span class="pill gold">财务预测器 · 未来3年营收/利润</span>
        <span class="pill brand">__WEEKDAY__ · __DATE__</span>
        <span class="pill brand">__SECTOR_ICON__ __SECTOR__</span>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num up">¥__PX__</div><div class="k">最新价 (__CHG_TXT__%)</div></div>
      <div class="kpi"><div class="v num gd">__BASE_REV__亿</div><div class="k">__BASE_YEAR__营收</div></div>
      <div class="kpi"><div class="v num gd">__BASE_NP__亿</div><div class="k">__BASE_YEAR__归母</div></div>
      <div class="kpi"><div class="v num up">__Q_NP_YOY__</div><div class="k">__LATEST__归母</div></div>
    </div>
  </div>

  <!-- 01 预测综述 -->
  <div class="sec"><h2><span class="no">01</span>预测综述</h2><span class="hint">三情景 · 模型输出 [MODEL]</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      <span class="vbadge">__VERDICT__</span>
      <b style="font-size:15px">__VERDICT__</b>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
  </div>

  <!-- 02 历史业绩 -->
  <div class="sec"><h2><span class="no">02</span>历史业绩回顾</h2><span class="hint">近5年营收/归母 · 单位：亿元</span></div>
  <div class="card">
    __HIST_BAR__
    <table style="margin-top:10px">
      <tr><th>年份</th><th>营收</th><th>营收同比</th><th>归母净利</th><th>净利同比</th></tr>
      __HIST_ROWS__
    </table>
    <div class="insight">__HIST_INSIGHT__</div>
  </div>

  <!-- 03 成长驱动 -->
  <div class="sec"><h2><span class="no">03</span>成长驱动与假设</h2><span class="hint">__DRIVER_HINT__</span></div>
  <div class="card">__DRIVER_ROWS__
    <div class="insight">__DRIVER_INSIGHT__</div>
  </div>

  <!-- 04 未来三年预测 -->
  <div class="sec"><h2><span class="no">04</span>未来 3 年预测</h2><span class="hint">归母净利三情景 · 单位：亿元</span></div>
  <div class="card">
    __SCEN_BAR__
    <table style="margin-top:10px">
      <tr><th>情景</th>__SCEN_YEARS_TH__<th>假设</th></tr>
      __SCEN_TABLE__
    </table>
    <div class="insight">__SCEN_INSIGHT__</div>
  </div>

  <!-- 05 敏感性 -->
  <div class="sec"><h2><span class="no">05</span>敏感性分析</h2><span class="hint">__SENS_HINT__</span></div>
  <div class="card">
    <table>
      <tr><th>营收\净利率</th>__SENS_TH__</tr>
      __SENS_TABLE__
    </table>
    <div class="insight">__SENS_INSIGHT__</div>
  </div>
  <div class="card" style="margin-top:14px"><h3>券商预测对照 <span class="unit">公开研报 · 归母净利</span></h3>
    <table>
      <tr><th>来源</th><th>2026E</th><th>2027E</th><th>2028E</th></tr>
      __BROKER_ROWS__
    </table>
    <div class="insight">__BROKER_INSIGHT__</div>
  </div>

  <!-- 06 风险 -->
  <div class="sec"><h2><span class="no">06</span>风险提示</h2><span class="hint">预测不确定性</span></div>
  <div class="card">__RISK_ROWS__</div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
sens_th = "".join(f'<th>{c}</th>' for c in SENS_COLS)
html = (TPL
        .replace("__NAME__", CFG["name"]).replace("__CODE__", CFG["code"])
        .replace("__SECTOR__", CFG["sector"]).replace("__SECTOR_ICON__", CFG["sector_icon"])
        .replace("__DATE__", DATE).replace("__WEEKDAY__", WEEKDAY)
        .replace("__PX__", f"{CFG['px']:.2f}").replace("__CHG_TXT__", CHG_TXT)
        .replace("__BASE_YEAR__", str(CFG["base_year"]))
        .replace("__BASE_REV__", f"{CFG['base_rev']:.1f}").replace("__BASE_NP__", f"{CFG['base_np']:.1f}")
        .replace("__LATEST__", CFG["latest"]).replace("__Q_NP_YOY__", CFG["q_np_yoy"])
        .replace("__VERDICT__", CFG["verdict"]).replace("__VERDICT_NOTE__", CFG["verdict_note"])
        .replace("__SUMMARY_ROWS__", summary_rows())
        .replace("__HIST_BAR__", hist_bar()).replace("__HIST_ROWS__", hist_rows())
        .replace("__DRIVER_ROWS__", driver_rows())
        .replace("__SCEN_BAR__", scen_bar())
            .replace("__SCEN_INSIGHT__", SCEN_INSIGHT)
            .replace("__DRIVER_HINT__", DRIVER_HINT).replace("__SCEN_TABLE__", scen_table())
        .replace("__SCEN_YEARS_TH__", "".join(f"<th>{y}E 营收/归母</th>" for y in SCEN_YEARS))
        .replace("__SENS_HINT__", SENS_HINT)
        .replace("__HIST_INSIGHT__", HIST_INSIGHT).replace("__DRIVER_INSIGHT__", DRIVER_INSIGHT).replace("__SENS_INSIGHT__", SENS_INSIGHT).replace("__BROKER_INSIGHT__", BROKER_INSIGHT)
        .replace("__SENS_TH__", sens_th).replace("__SENS_TABLE__", sens_table())
        .replace("__BROKER_ROWS__", broker_rows())
        .replace("__RISK_ROWS__", risk_rows())
        .replace("{NAME}", CFG["name"]).replace("{DATE}", DATE.replace("-", ""))
        .replace("__NOTE__", NOTE))

out_path = os.path.join(BASE, f"财务预测器_{CFG['name']}_{DATE.replace('-', '')}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {out_path} | size: {len(html.encode('utf-8'))} bytes")
