# -*- coding: utf-8 -*-
"""A股业绩前瞻日历 HTML 生成器 v1.0（模板）
【模板使用说明】回答"未来两周谁要发财报？市场在期待什么？"：
①hithink CLI 确认当前日期与交易日（market calendar，注意仅返回一年窗口）
②WebSearch 查披露预约时间表/披露高峰分布/重点公司业绩预告（交易所公开数据）——hithink 无披露日历接口，披露安排为公开披露信息（页脚标注来源）
③拉重点披露股估值（valuation snapshot 批量）→ 填盲盒权重清单
④替换 BASE/DATE 与数据区（CFG/WINDOW/DAILY_COUNT/KEY_DISCLOSURE/BLIND_BOX/EXPECT_LINES/STRATEGY/RISK/SUMMARY/NOTE）⑤运行 → 输出 `业绩前瞻日历_{YYYYMMDD}.html`
口径：披露日期/预告区间为交易所预约与业绩预告公开披露（WebSearch，非 hithink 接口）；披露量分布为新闻报道口径（各源略有差异取主源）；
换周期前 grep 旧日期/旧公司名清理残留；insight 全部在数据区
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-08-21"
# ================= 数据 =================
CFG = {
    "name": "A股业绩前瞻日历", "code": "2026 中报冲刺期",
    "window": "2026-08-24（周一）~ 2026-09-04（周五）", "deadline": "2026-08-31（中报披露截止）",
    "verdict": "披露高峰 · 期待兑现", "verdict_short": "高峰",
    "verdict_note": ("未来两周是 2026 中报披露最后冲刺：8/24-8/28 五天 3643 家集中交卷、8/31 截止；"
                     "市场在期待 AI 算力链（中际旭创）、存储（长鑫科技+2244%）与非银（中国人寿+215%）的兑现；"
                     "8 家万亿权重股仍处'盲盒'状态，披露结果或成 9 月行情方向标。"),
}
# 未来两周逐日披露量（新闻口径）
DAILY = [
    ("8-24 周一", 757, True), ("8-25 周二", 746, True), ("8-26 周三", 733, True),
    ("8-27 周四", 717, True), ("8-28 周五", 690, True), ("8-31 周一", 400, True),
    ("9-01~04", 0, False),
]
# 未来两周重点披露（名称/披露日/业绩预告/关注点）
KEY_DISCLOSURE = [
    ("新华保险", "8-27", "净利 207~237 亿（+40~60%）", "非银高景气，权益市场受益", "保险"),
    ("中国人寿", "8-28", "净利 1289~1371 亿（+215~235%）", "保费+投资收益双击，保险龙头", "保险"),
    ("长鑫科技", "8-29", "净利 500~570 亿（+2244~2544%）", "存储涨价周期，AI 需求爆发", "半导体存储"),
    ("中国神华", "8-31", "净利 263~298 亿（-4.7~+8%）", "煤价回落，能源防御属性", "煤炭"),
    ("贵州茅台", "8-31前", "[盲盒] 中报待披露", "消费龙头，市场期待批价企稳", "白酒"),
    ("中际旭创", "8-31前", "[盲盒] 中报待披露", "CPO/光模块，AI 算力链兑现关键验证", "光模块"),
]
# 万亿市值"盲盒"权重股（8-14 时未披露，8-31 前必须披露）
BLIND_BOX = [
    ("工商银行", "601398", 7.5, 0.70, "银行·万亿阵营"), ("农业银行", "601288", 8.1, 0.84, "银行·万亿阵营"),
    ("建设银行", "601939", 8.1, 0.78, "银行·万亿阵营"), ("中国银行", "601988", 7.9, 0.71, "银行·万亿阵营"),
    ("中国石油", "601857", 13.0, 1.26, "能源·万亿阵营"), ("中国海油", "600938", 12.9, 1.92, "能源·万亿阵营"),
    ("贵州茅台", "600519", 19.5, 6.33, "消费·万亿阵营"), ("中际旭创", "300308", 53.9, 27.67, "科技·万亿阵营"),
]
# 市场期待主线（已披露参照 → 待披露看点）
EXPECT_LINES = [
    ("🧠 AI 算力兑现", "已披露：工业富联归母 237 亿（+96%）、寒武纪 23.1 亿（+123%）——AI 算力从预期走向报表兑现",
     "待验证：中际旭创（盲盒）光模块/CPO 业绩能否延续高增，AI 链确定性核心观察点"),
    ("💾 存储爆发", "已披露：江波龙归母 105.8 亿（同比 +715 倍）领跑全市场，存储涨价周期全面兑现",
     "最大看点：长鑫科技 8-29 预告 500~570 亿（+2244~2544%）——存储国产替代+涨价双击"),
    ("🏦 非银高景气", "已披露：中国平安归母 1075 亿居首、中信证券 239 亿（+70%）——权益市场活跃度推高非银",
     "待验证：中国人寿（+215%）、新华保险（+40~60%）8-27/28 披露，保险板块高景气确认"),
]
# 财报周策略提示
STRATEGY = [
    ("光大证券", "8 月中报密集披露期有望成为市场从'估值消化'切换至'盈利驱动'的拐点"),
    ("已披露结构", "截至 8/20：899 家披露，66.5% 净利正增长、199 家增速超 100%——盈利面整体健康"),
    ("行业结构", "钢铁/石化/军工/电子/有色盈利高增；房地产降幅仍大——上游周期+科技兑现、地产承压"),
    ("披露节奏", "8-24~8-31 日均 700+ 家披露，市场波动或加大；9-01 起进入财报真空期（三季报 10 月）"),
]
RISK = [
    "盲盒权重股不及预期风险：茅台（消费疲弱）、中际旭创（高 PE 53.9 倍高预期）等披露低于预期或引发板块调整",
    "集中披露流动性冲击：日均 700+ 家财报，财报周个股波动显著放大，避免财报前重仓押注",
    "预告≠实际：部分公司业绩预告为区间上限/下限，实际披露可能落在区间低位",
    "披露安排为预约制：交易所预约时间可能调整，个别公司存在延期披露风险",
    "9 月初财报真空期缺乏业绩催化，市场或重回主题轮动，注意风格切换",
]
SUMMARY = [
    ("结论", "未来两周=2026 中报最后冲刺：5 天 3643 家集中披露、8/31 截止；最大看点=中际旭创（AI 光模块）与长鑫科技（存储+2244%）——财报周是'盈利驱动'拐点验证窗口。"),
    ("披露高峰", "8/24-8/28 日均 700+ 家（757→690 只），8/31 截止收尾；9/1-9/4 进入财报真空期——节奏前密后疏。"),
    ("AI 算力", "工业富联+96%/寒武纪+123% 已验证高景气，中际旭创盲盒披露是 AI 链下半年确定性核心验证。"),
    ("存储", "江波龙+715 倍后，长鑫科技 8-29 预告 500-570 亿（+2244%）——存储涨价周期最强兑现，关注产业链扩散。"),
    ("非银金融", "平安 1075 亿/中信+70% 后，人寿+215%/新华+40-60% 8 月底披露——非银高景气延续，市场活跃度支撑。"),
]
NOTE = ("数据来源：披露时间表与业绩预告来自交易所预约披露安排及上海证券报/新浪财经等公开披露（2026-08-23 检索）；"
        "披露量分布为新闻报道口径（各源略有差异）；重点股估值来自同花顺金融数据（hithink-finance v0.1.5，valuation.snapshot）；"
        "盲盒清单为 8-14 时未披露口径，部分公司可能已提前披露或调整预约时间。"
        "本日历为事件梳理（模型输出），仅供研究参考，不构成个人投资建议。")

KPI_DISCLOSE = '3643'
KPI_DISCLOSE_K = '8/24-28 披露家数'
KPI_BLIND = '8 家'
KPI_POSITIVE = '66.5%'
HINT_BLIND = '8-31 前必须披露 · 估值快照'
INSIGHT_CALENDAR = '💡 8/24-8/31 是 2026 中报披露最后冲刺（5 天 3643 家、日均 700+），8/31 为法定截止；9/1 起进入财报真空期——未来两周节奏"前密后疏"。'
INSIGHT_KEY = '💡 最大看点：长鑫科技 8-29 预告 500~570 亿（+2244%）——存储涨价周期最强兑现；中际旭创 8-31 前盲盒披露是 AI 算力链确定性核心验证。'
INSIGHT_EXPECT = '💡 三条主线从"产业预期"走向"报表兑现"：AI 算力（工业富联+96%）、存储（江波龙+715倍）、非银（平安 1075 亿）——本周披露结果决定"盈利驱动"能否接棒"估值驱动"。'
INSIGHT_BLIND = '💡 8 家万亿权重中，银行 4 家（PE 7.5-8.1 低估值）与能源 2 家（PE 13 附近）披露对指数影响大但预期平稳；中际旭创 PE 53.9/PB 27.7 高预期+茅台 19.5 倍消费疲弱——科技与消费是盲盒分歧最大方向。'
INSIGHT_STRATEGY = '💡 光大证券：密集披露期或成"估值消化→盈利驱动"拐点——财报周避免重仓押注个股披露，关注超预期方向（AI/存储/非银）的低吸机会；9 月初真空期警惕风格切换。'

# ================= 渲染 =================
def daily_bar():
    W, H, P = 880, 220, 50
    maxv = max(c for _, c, _ in DAILY) * 1.2
    n = len(DAILY)
    bw = (W - 2 * P) / n
    parts = []
    for i, (lab, cnt, is_peak) in enumerate(DAILY):
        cx = P + bw * i + bw / 2
        h = (cnt / maxv) * (H - 60) if cnt else 6
        color = "#e5484d" if is_peak else "#9aa1ad"
        parts.append(f'<rect x="{cx-22:.1f}" y="{H-40-h:.1f}" width="30" height="{max(h,4):.1f}" rx="4" fill="{color}" opacity="0.85"/>')
        if cnt:
            parts.append(f'<text x="{cx:.1f}" y="{H-40-h-5:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{color}">{cnt}</text>')
        else:
            parts.append(f'<text x="{cx:.1f}" y="{H-40-h-5:.1f}" text-anchor="middle" font-size="10" fill="#9aa1ad">真空</text>')
        parts.append(f'<text x="{cx:.1f}" y="{H-14}" text-anchor="middle" font-size="10.5" fill="#6b7280">{lab}</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="未来两周每日披露量">{"" .join(parts)}</svg>'

def key_rows():
    rows = ""
    for name, day, fc, note, sector in KEY_DISCLOSURE:
        blind = "盲盒" in fc
        fc_c = "var(--ink-2)" if blind else "var(--red)"
        rows += (f'<tr><td><b>{name}</b></td>'
                 f'<td class="num" style="color:var(--brand);font-weight:700">{day}</td>'
                 f'<td class="num" style="color:{fc_c};font-weight:600">{fc}</td>'
                 f'<td style="color:var(--ink-2);font-size:12px">{note}</td>'
                 f'<td><span class="sector-chip">{sector}</span></td></tr>')
    return rows

def blind_rows():
    rows = ""
    for name, code, pe, pb, grp in BLIND_BOX:
        rows += (f'<tr><td><b>{name}</b> <span class="code-mini">{code}</span></td>'
                 f'<td class="num">{pe:.1f}</td><td class="num">{pb:.2f}</td>'
                 f'<td style="color:var(--ink-2);font-size:12px">{grp}</td></tr>')
    return rows

def expect_rows():
    out = ""
    for icon, done, todo in EXPECT_LINES:
        out += (f'<div class="kv"><span class="k" style="flex:0 0 130px">{icon}</span>'
                f'<span style="color:var(--ink-2);font-size:12px">✅ {done}</span></div>'
                f'<div class="kv"><span class="k" style="flex:0 0 130px"></span>'
                f'<span style="color:var(--red);font-size:12px;font-weight:600">👀 {todo}</span></div>')
    return out

def strategy_rows():
    out = ""
    for title, desc in STRATEGY:
        out += f'<div class="kv"><span class="k" style="flex:0 0 100px">{title}</span><span class="v" style="color:var(--ink-2);font-size:12.5px;max-width:70%;text-align:right">{desc}</span></div>'
    return out

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
<title>业绩前瞻日历_{DATE}</title>
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
  .sector-chip { font-size:10.5px; color:var(--brand); background:var(--brand-soft); border-radius:4px; padding:1px 7px; white-space:nowrap; }
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
  .sum-tag { flex-shrink:0; font-size:11px; font-weight:800; color:#fff; background:linear-gradient(180deg,var(--gold),#a8871d); border-radius:5px; padding:2px 9px; }
  .sum-tag2 { flex-shrink:0; font-size:11px; font-weight:800; color:var(--brand); background:var(--brand-soft); border:1px solid #d5def5; border-radius:5px; padding:2px 9px; }
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
      <div class="title">业绩前瞻日历</div>
      <div class="sub">
        <span class="pill gold">未来两周谁要发财报？</span>
        <span class="pill brand">__WINDOW__</span>
        <span class="pill brand">截止 __DEADLINE__</span>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num up">__KPI_DISCLOSE__</div><div class="k">__KPI_DISCLOSE_K__</div></div>
      <div class="kpi"><div class="v num gd">__KPI_BLIND__</div><div class="k">万亿盲盒权重</div></div>
      <div class="kpi"><div class="v num up">__KPI_POSITIVE__</div><div class="k">已披露净利正增长</div></div>
      <div class="kpi"><div class="v num">__VERDICT__</div><div class="k">财报周判定</div></div>
    </div>
  </div>

  <!-- 01 披露日历总览 -->
  <div class="sec"><h2><span class="no">01</span>披露日历总览</h2><span class="hint">未来两周每日披露量 · 家</span></div>
  <div class="card">
    __SUMMARY_ROWS__
    __DAILY_BAR__
    <div class="insight">__INSIGHT_CALENDAR__</div>
  </div>

  <!-- 02 重点披露 -->
  <div class="sec"><h2><span class="no">02</span>未来两周重点披露</h2><span class="hint">业绩预告 + 盲盒权重</span></div>
  <div class="card">
    <table>
      <tr><th>公司</th><th>披露日</th><th>业绩预告/预期</th><th>关注点</th><th>板块</th></tr>
      __KEY_ROWS__
    </table>
    <div class="insight">__INSIGHT_KEY__</div>
  </div>

  <!-- 03 市场在期待什么 -->
  <div class="sec"><h2><span class="no">03</span>市场在期待什么</h2><span class="hint">已披露参照 → 待披露看点</span></div>
  <div class="card">__EXPECT_ROWS__
    <div class="insight">__INSIGHT_EXPECT__</div>
  </div>

  <!-- 04 盲盒权重清单 -->
  <div class="sec"><h2><span class="no">04</span>万亿"盲盒"权重清单</h2><span class="hint">__HINT_BLIND__</span></div>
  <div class="card">
    <table>
      <tr><th>公司</th><th>PE_TTM</th><th>PB</th><th>阵营</th></tr>
      __BLIND_ROWS__
    </table>
    <div class="insight">__INSIGHT_BLIND__</div>
  </div>

  <!-- 05 财报周策略 -->
  <div class="sec"><h2><span class="no">05</span>财报周策略提示</h2><span class="hint">券商观点 + 节奏</span></div>
  <div class="card">__STRATEGY_ROWS__
    <div class="insight">__INSIGHT_STRATEGY__</div>
  </div>

  <!-- 06 风险 -->
  <div class="sec"><h2><span class="no">06</span>风险提示</h2><span class="hint">财报周不确定性</span></div>
  <div class="card">__RISK_ROWS__</div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
html = (TPL
        .replace("__DATE__", DATE)
        .replace("__WINDOW__", CFG["window"]).replace("__DEADLINE__", CFG["deadline"])
        .replace("__VERDICT__", CFG["verdict"]).replace("__VERDICT_NOTE__", CFG["verdict_note"])
        .replace("__DAILY_BAR__", daily_bar())
        .replace("__KEY_ROWS__", key_rows())
        .replace("__EXPECT_ROWS__", expect_rows())
        .replace("__BLIND_ROWS__", blind_rows())
        .replace("__STRATEGY_ROWS__", strategy_rows())
        .replace("__RISK_ROWS__", risk_rows())
        .replace("__SUMMARY_ROWS__", summary_rows())
        .replace("__KPI_DISCLOSE__", KPI_DISCLOSE).replace("__KPI_DISCLOSE_K__", KPI_DISCLOSE_K)
        .replace("__KPI_BLIND__", KPI_BLIND).replace("__KPI_POSITIVE__", KPI_POSITIVE)
        .replace("__HINT_BLIND__", HINT_BLIND)
        .replace("__INSIGHT_CALENDAR__", INSIGHT_CALENDAR)
        .replace("__INSIGHT_KEY__", INSIGHT_KEY)
        .replace("__INSIGHT_EXPECT__", INSIGHT_EXPECT)
        .replace("__INSIGHT_BLIND__", INSIGHT_BLIND)
        .replace("__INSIGHT_STRATEGY__", INSIGHT_STRATEGY)
        .replace("{DATE}", DATE.replace("-", ""))
        .replace("__NOTE__", NOTE))

out_path = os.path.join(BASE, f"业绩前瞻日历_{DATE.replace('-', '')}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {out_path} | size: {len(html.encode('utf-8'))} bytes")
