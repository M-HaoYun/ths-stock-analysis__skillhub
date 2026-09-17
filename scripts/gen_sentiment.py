# -*- coding: utf-8 -*-
"""A股市场情绪面扫描器 HTML 生成器 v3.4（模板，全参数化）
【模板使用说明】生成某交易日的情绪扫描：①用 hithink-finance CLI 拉取当日+一周数据
②替换下方 BASE/DATE/WEEKDAY 与数据区（TEMP/INDEX/WEEK_UP/SECTOR_TOP/PERSIST_STOCK/FOCUS/LHB/DIAG/SUMMARY/SECTOR_VIEW/NOTE
及 HERO_SUB/DIAG_EXTRA/WEEK_INSIGHT/FOCUS_INSIGHT/PERSIST_INSIGHT/WEEK_RANGE/SECTOR_RANGE）
③运行脚本 → 输出 `市场情绪扫描_{YYYYMMDD}.html`。
v3.4 相对 v3.3：模板 8 处当日叙事硬编码 → 占位符+数据区字段（换日期不再需要动 TPL，只改数据区）
【模板使用说明】生成某交易日的情绪扫描：①用 hithink-finance CLI 拉取当日+一周数据
②替换下方 BASE/DATE/WEEKDAY 与数据区（TEMP/INDEX/WEEK_UP/SECTOR_TOP/PERSIST_STOCK/FOCUS/LHB/DIAG/SUMMARY/SECTOR_VIEW/NOTE）
③运行脚本 → 输出 `市场情绪扫描_{YYYYMMDD}.html`。板块热度由涨停池 limit_up_reason 关键词统计得到。
v3.3 结构：01情绪综述 → 02市场温度(图表) → 03指数 → 04板块热度(热度vs走势双色) → 05一周持续关注 → 06龙虎榜资金 → 07情绪诊断
历史数据坑（务必遵守）：
- special.hot-stock-history 的 --date 参数无效（永远返回最近交易日）→ 历史日热榜标 [MISSING]，用龙虎榜净买替代为"资金关注焦点"
- special.limit-up-ladder 只返回最近30个交易日 → 历史日从涨停池 continue_day_cnt 重建连板梯队
- special.anomaly-list 为当日实时能力，历史日不可查
- 板块热度 strong 标记=热度高且走势好（真实主线），用金色条；其余深蓝条
风格：与速览卡一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、tabular-nums
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-01-05"
WEEKDAY = "周一"

# ================= 数据 =================
TEMP = {"limit_up": 107, "limit_down": 8, "break_board": 26, "seal_rate": 80.5,
        "max_lianban": 7, "max_lianban_name": "锋龙股份", "up_cnt": 3910, "down_cnt": 1407, "total_cnt": 5434}
up_ratio = TEMP["up_cnt"] / TEMP["total_cnt"] * 100
UD_RATIO = f"{TEMP['limit_up']/TEMP['limit_down']:.1f} : 1"   # 涨跌停比
# Hero/温度条当日叙事（v3.4 参数化，禁止硬编码进 TPL）
HERO_SUB = "一周涨停 72→53→56→107，节后首日放量、情绪升温"
DIAG_EXTRA = f"涨跌停比 {UD_RATIO} · 高度 7 板（锋龙股份）"
WEEK_INSIGHT = "💡 72→53→56→107：元旦前缩量整理，节后首日放量突破，情绪明显升温。"
FOCUS_INSIGHT = "💡 商业航天获机构大买（中国卫通/航天机电），机器人方向机构分歧（五洲新春净卖-2.21亿）。"
PERSIST_INSIGHT = "💡 锋龙股份/雷科防务 4 天最持续：机器人+商业航天双主线受资金反复关注。"
INDEX = [("上证指数", "1A0001", 4023.42, 1.38), ("深证成指", "399001", 13828.63, 2.24),
         ("创业板指", "399006", 3294.55, 2.85), ("沪深300", "1B0300", 4717.75, 1.90)]

# 一周窗口（副标用）
WEEK_RANGE = "12-29~01-05"
SECTOR_RANGE = "12-29~01-05"
# 一周每日涨停家数（12-29 ~ 01-05，元旦休市）
WEEK_UP = [("12-29", 72, "周一"), ("12-30", 53, "周二"), ("12-31", 56, "周三"),
           ("01-05", 107, "周一")]
# 板块热度（一周涨停原因关键词统计；strong=True=热度高且走势好）
SECTOR_TOP = [("航天/商业航天", 75, True), ("机器人", 67, False), ("AI", 38, True), ("国资", 31, False), ("央企", 25, False),
              ("人形机器人", 22, False), ("军工", 16, True), ("卫星", 14, True), ("电子", 14, True), ("芯片", 14, True),
              ("储能", 11, False), ("汽车", 11, False), ("扭亏", 10, False), ("算力", 10, True)]
# 持续涨停个股（一周涨停天数>=3）
PERSIST_STOCK = [("锋龙股份", 4, "机器人+优必选入主+业绩大增"), ("雷科防务", 4, "商业航天+卫星遥感+军工电子"),
                 ("大业股份", 3, "机器人+轮胎模具"), ("泰尔股份", 3, "机器人+冶金装备"), ("宏英智能", 3, "机器人+电气控制"),
                 ("御银股份", 3, "算力+金融机具"), ("勘设股份", 3, "低空+工程咨询"), ("五洲新春", 3, "机器人轴承+龙虎榜净买")]
# 当日关注焦点（热榜历史接口不可回溯，改用龙虎榜净买 TOP3 真实数据替代）
FOCUS = [("中国卫通", "601698", "+4.24亿", "机构净买", "商业航天+卫星通信"),
         ("航天机电", "600151", "+4.19亿", "机构净买", "商业航天+光伏"),
         ("五洲新春", "603667", "+2.84亿", "机构-2.21亿", "机器人轴承+减速器")]
# 龙虎榜资金（净买入 TOP6）
LHB = [("中国卫通", "601698", 4.24, "机构净买", "商业航天+卫星通信", 0.0998),
       ("航天机电", "600151", 4.19, "机构净买", "商业航天+光伏", 0.1002),
       ("五洲新春", "603667", 2.84, "机构-2.21", "机器人轴承+减速器", 0.1001),
       ("普冉股份", "688766", 2.72, "机构+0.76", "存储芯片+MCU", 0.2001),
       ("ST天际", "002759", 2.12, "机构-1.20", "摘帽预期+ST板块", 0.0498),
       ("锋龙股份", "002931", 1.85, "[MISSING]", "机器人+优必选入主", 0.1001)]
# 情绪诊断
DIAG = {
    "level": "偏热·情绪高涨", "badge": "热", "score": 82,
    "summary": ("01-05 市场情绪偏热：涨停107家 vs 跌停8家，封板率80.5%，上涨占比72%（3910涨/1407跌），四大指数全线上涨（创业板+2.85%）。"
                "连板高度7板（锋龙股份），商业航天+机器人双主线共振，情绪处于高位亢奋状态。"),
    "bull": ["涨停107家+封板率80.5%，赚钱效应极强", "商业航天主线梯队完整（中国卫通/航天机电/雷科防务领涨）",
             "机器人主线高度担当（锋龙股份7板领衔）", "四大指数齐涨、上涨占比72%普涨格局"],
    "bear": ["7板高度+107家涨停=情绪过热风险积聚", "炸板26家（江龙船艇/海阳科技）高位分歧初现",
             "新年首个交易日情绪易透支，警惕次日高开回落", "ST板块/低价股活跃（ST天际）投机氛围浓"],
    "watch": ["7板锋龙股份能否晋级8板打开空间", "商业航天（中国卫通/航天机电）能否承接次日",
              "高位连板股（雷科防务4板）分歧风险"],
}
# 综述段落（放页面顶部 Hero 之后）
SUMMARY = [
    ("整体", "01-05 市场情绪偏热：涨停107 vs 跌停8、封板率80.5%、上涨占比72%，四大指数齐涨（创业板+2.85%），元旦后首个交易日开门红、情绪亢奋。"),
    ("商业航天", "绝对主线：一周提及75次居首，中国卫通/航天机电/雷科防务梯队完整、龙虎榜净买居前，热度与走势双优。"),
    ("机器人", "高度担当：一周提及67次，锋龙股份7板领衔，但板块内部分化，属龙头个股带动。"),
    ("AI/算力", "热度第三（38次）：CPO/芯片方向承接资金，龙虎榜普冉股份（存储芯片）获机构净买，走势扎实。"),
    ("军工卫星", "与商业航天共振（16+14次）：雷科防务/中国卫星等轮动，防御与进攻属性兼具。"),
    ("锋龙股份", "全场最高7板（优必选入主+机器人+业绩大增），市场情绪风向标；但高位博弈风险极大，仅代表情绪强度不代表确定性。"),
]
# 板块解读（03区，修正表述）
SECTOR_VIEW = [("🚀 商业航天", "绝对主线 · 热度走势双优", "一周提及75次，中国卫通/航天机电龙虎榜净买居前"),
               ("🤖 机器人", "高度担当 · 龙头带动", "提及67次，锋龙7板领衔，板块内分化"),
               ("💻 AI/算力", "第三主线 · 走势扎实", "38次提及，CPO/芯片承接资金，普冉股份获机构净买"),
               ("🛰️ 军工卫星", "共振方向", "16+14次提及，与商业航天联动"),
               ("🏛️ 国资央企", "背景属性", "31+25次提及，多为题材叠加"),
               ("📈 业绩驱动", "三季报+扭亏", "20+10次提及，业绩为王逻辑")]
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，special.* 特色数据 + index 指数历史 + 本地DuckDB涨跌家数）；"
        "板块热度=一周(12-29~01-05)涨停原因关键词统计；热榜历史接口实测仅返回最近交易日数据（历史日不可回溯），01-05 当日热榜标 [MISSING]，资金关注焦点以龙虎榜净买替代；指数涨跌幅为收盘价对比前一交易日(12-31)。"
        "情绪诊断为主观综合判断（模型输出），涨跌家数基于本地库未复权日K收开盘比较。本报告仅供研究参考，不构成个人投资建议。")
# ================= SVG 图表 =================
# 01 市场温度：横向条形图（涨停/炸板/跌停 + 封板率仪表）
def temp_svg():
    BW, BH = 460, 210
    rows = [("涨停", TEMP["limit_up"], "#e5484d"), ("炸板", TEMP["break_board"], "#e8a020"),
            ("跌停", TEMP["limit_down"], "#2fa36b")]
    vmax = TEMP["limit_up"]
    parts = []
    for i, (name, v, color) in enumerate(rows):
        y = 26 + i * 46
        w = v / vmax * (BW - 150)
        parts.append(f'<text x="20" y="{y+18}" font-size="12.5" fill="#5b6470">{name}</text>')
        parts.append(f'<rect x="70" y="{y+6}" width="{BW-140}" height="20" rx="6" fill="#eef0f3"/>')
        parts.append(f'<rect x="70" y="{y+6}" width="{w:.1f}" height="20" rx="6" fill="{color}" opacity="0.85"/>')
        parts.append(f'<text x="{72+w:.1f}" y="{y+21}" font-size="13" font-weight="800" fill="{color}">{v}家</text>')
    # 封板率仪表
    parts.append(f'<text x="20" y="186" font-size="12.5" fill="#5b6470">封板率</text>')
    parts.append(f'<rect x="70" y="174" width="{BW-140}" height="14" rx="7" fill="#eef0f3"/>')
    parts.append(f'<rect x="70" y="174" width="{TEMP["seal_rate"]/100*(BW-140):.1f}" height="14" rx="7" fill="url(#gGold)"/>')
    parts.append(f'<text x="{72+TEMP["seal_rate"]/100*(BW-140):.1f}" y="185" font-size="12.5" font-weight="800" fill="#c9a227">{TEMP["seal_rate"]:.0f}%</text>')
    return f'''
<svg viewBox="0 0 {BW} {BH}" width="100%" role="img" aria-label="市场温度图表">
  <defs><linearGradient id="gGold" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#e8b83a"/><stop offset="100%" stop-color="#c9a227"/></linearGradient></defs>
  {''.join(parts)}
</svg>'''

# 02 一周涨停家数趋势折线
def week_trend_svg():
    BW, BH, PAD = 460, 210, 34
    vals = [v for _, v, _ in WEEK_UP]
    vmax = max(vals) * 1.15
    def px(i): return PAD + i * (BW - 2*PAD) / 4
    def py(v): return BH - 34 - (v / vmax) * (BH - 60)
    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, (_, v, _) in enumerate(WEEK_UP))
    parts = [f'<polyline points="{pts}" fill="none" stroke="#1f3a93" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>']
    for i, (d, v, wd) in enumerate(WEEK_UP):
        parts.append(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="4" fill="#fff" stroke="#1f3a93" stroke-width="2"/>')
        parts.append(f'<text x="{px(i):.1f}" y="{py(v)-10:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#1f3a93">{v}</text>')
        parts.append(f'<text x="{px(i):.1f}" y="{BH-14}" text-anchor="middle" font-size="11" fill="#98a1ad">{d}<tspan x="{px(i):.1f}" dy="13" font-size="10">{wd}</tspan></text>')
    return f'''
<svg viewBox="0 0 {BW} {BH}" width="100%" role="img" aria-label="一周涨停家数趋势">
  <line x1="{PAD}" y1="{BH-34}" x2="{BW-PAD}" y2="{BH-34}" stroke="#e8eaee"/>
  {''.join(parts)}
</svg>'''

# ================= HTML =================
TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>市场情绪面扫描 · __DATE__</title>
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
  .logo { width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg,#1f3a93,#2f56c9); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:14px; box-shadow:0 4px 14px -4px rgba(31,58,147,.5); }
  .brand .nm { font-size:21px; font-weight:700; line-height:1.3; }
  .pill { display:inline-block; font-size:11.5px; font-weight:600; padding:2px 10px; border-radius:20px; vertical-align:2px; }
  .pill.code { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
  .meta { text-align:right; font-size:12px; color:var(--ink-3); }
  .meta b { color:var(--ink-2); font-weight:600; }

  .diagbar { display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin:14px 0; padding:14px 18px; border-radius:12px; background:linear-gradient(120deg,#fdf9ec,#faf3d8); border:1px solid #eddcab; }
  .diagbar .lvl { font-size:15px; font-weight:800; color:#8a6d12; }
  .diagbar .badge { font-size:12px; font-weight:700; color:#fff; background:var(--gold); border-radius:8px; padding:3px 12px; }
  .diagbar .bar { flex:1; min-width:120px; height:10px; border-radius:5px; background:#eee7cf; overflow:hidden; }
  .diagbar .bar i { display:block; height:100%; border-radius:5px; background:linear-gradient(90deg,#e8b83a,#c9a227); }
  .diagbar .score { font-size:12px; color:#a8883a; }

  .intro-card { background:linear-gradient(150deg,#ffffff,#f8faff); border:1px solid var(--border); border-radius:var(--radius); box-shadow:var(--shadow-sm); padding:18px 22px; margin-bottom:4px; }
  .intro-card h3 { font-size:13.5px; font-weight:700; margin-bottom:8px; display:flex; align-items:center; gap:8px; }
  .intro-card h3::before { content:""; width:4px; height:14px; border-radius:2px; background:linear-gradient(180deg,var(--gold),var(--brand)); }
  .intro-card p { font-size:13px; color:var(--ink-2); line-height:1.8; }

  .hero { background:linear-gradient(150deg,#ffffff 30%,#fbfcfe 100%); border:1px solid var(--border); border-radius:18px; box-shadow:var(--shadow-md); padding:24px 28px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px; position:relative; overflow:hidden; }
  .hero::before { content:""; position:absolute; right:-70px; top:-70px; width:240px; height:240px; border-radius:50%; background:radial-gradient(circle,rgba(201,162,39,.12),transparent 65%); }
  .hero::after { content:""; position:absolute; left:-50px; bottom:-90px; width:200px; height:200px; border-radius:50%; background:radial-gradient(circle,rgba(31,58,147,.06),transparent 70%); }
  .hero .big { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; position:relative; z-index:1; }
  .hero .main { font-size:50px; font-weight:800; letter-spacing:-1.5px; }
  .hero .main .unit { font-size:22px; color:var(--ink-2); font-weight:600; margin-left:4px; }
  .hero .chg { font-size:17px; font-weight:700; color:var(--gold); }
  .hero .sub { margin-top:10px; font-size:12.5px; color:var(--ink-3); position:relative; z-index:1; }
  .hero .kpis { display:flex; gap:26px; position:relative; z-index:1; }
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
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }
  .grid-2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }
  .mcard { text-align:center; padding:16px 10px 14px; }
  .mcard .mv { font-size:24px; font-weight:800; letter-spacing:-.3px; }
  .mcard .mk { font-size:12px; color:var(--ink-3); margin-top:3px; }
  .mcard.hl .mv { color:var(--red); } .mcard.ll .mv { color:var(--green); } .mcard.gd .mv { color:var(--gold); }

  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink-2); }
  .kv .v { font-weight:650; }

  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { padding:7px 9px; text-align:right; border-bottom:1px solid var(--border); }
  th { color:var(--ink-3); font-weight:500; font-size:11.5px; background:var(--surface-2); }
  th:first-child, td:first-child { text-align:left; }
  tbody tr:nth-child(even) td { background:#fbfcfd; }
  tbody tr:last-child td { border-bottom:none; }
  tbody tr:hover td { background:#f4f6fb; }
  .pos { color:var(--red); } .neg { color:var(--green); }

  .note { font-size:11.5px; color:var(--ink-3); margin-top:10px; line-height:1.6; }
  .insight { margin-top:12px; padding:10px 14px; border-radius:10px; background:linear-gradient(120deg,#fdf9ec,#faf3d8); border:1px solid #eddcab; font-size:12.5px; font-weight:600; color:#8a6d12; line-height:1.7; }
  .lbar-legend { display:flex; gap:16px; font-size:11.5px; color:var(--ink-2); margin:0 0 10px; flex-wrap:wrap; }
  .sector-list { display:flex; flex-direction:column; gap:2px; }
  .srow { display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px dashed #f0f1f4; }
  .srow:last-child { border-bottom:none; }
  .srk2 { flex-shrink:0; width:20px; font-size:13px; color:var(--ink-2); text-align:center; }
  .srn2 { flex:1; font-size:13.5px; color:var(--ink-2); }
  .srp2 { flex-shrink:0; font-size:13.5px; font-weight:650; width:56px; text-align:right; }
  .srp2 em { font-style:normal; font-size:11px; color:var(--ink-3); font-weight:400; margin-left:2px; }
  .srbar { flex:1.2; min-width:80px; height:5px; border-radius:3px; background:#eef0f3; overflow:hidden; }
  .srbar i { display:block; height:100%; border-radius:3px; }
  .lbar-legend .lg { display:inline-block; width:14px; height:5px; border-radius:3px; margin-right:5px; vertical-align:2px; }
  .sum-row { display:flex; align-items:baseline; gap:8px; padding:9px 0; border-bottom:1px dashed #f0f1f4; font-size:13px; flex-wrap:wrap; }
  .sum-row:last-child { border-bottom:none; }
  .sum-tag { flex-shrink:0; font-size:11px; font-weight:800; color:#fff; background:linear-gradient(180deg,var(--gold),#a8871d); border-radius:5px; padding:2px 9px; }
  .sum-tag2 { flex-shrink:0; font-size:11px; font-weight:800; color:var(--brand); background:var(--brand-soft); border:1px solid #d5def5; border-radius:5px; padding:2px 9px; }
  .foot { margin-top:36px; padding:18px 4px 0; border-top:1px solid var(--border); color:var(--ink-3); font-size:11.5px; line-height:1.75; }
  .foot b { color:var(--ink-2); }
  a:focus-visible, button:focus-visible, [tabindex]:focus-visible { outline:2px solid var(--brand-2); outline-offset:2px; border-radius:4px; }

  @media (max-width:760px) {
    .hero .kpis { gap:18px; }
    .hero .main { font-size:38px; }
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
      <div class="logo">情绪</div>
      <div class="nm">A股市场情绪面扫描 <span class="pill code">__DATE__（__WEEKDAY__）</span></div>
    </div>
    <div class="meta">最近交易日 · 收盘后情绪快照<br>数据源 · 同花顺金融数据</div>
  </div>

  <div class="diagbar">
    <span class="badge">__DIAG_BADGE__</span>
    <span class="lvl">情绪温度 __DIAG_SCORE__ / 100 · 判定：__DIAG_LEVEL__</span>
    <span class="bar"><i style="width:__DIAG_PCT__%"></i></span>
    <span class="score">封板率 __SEAL__% · __DIAG_EXTRA__</span>
  </div>

  <div class="hero">
    <div>
      <div class="big">
        <span class="main num">__SEAL__<span class="unit">%</span></span>
        <span class="chg num">封板率</span>
        <span class="pill" style="background:#fdecec;color:var(--red)">涨停 __UP__</span>
        <span class="pill" style="background:#eaf6f0;color:var(--green)">跌停 __DOWN__</span>
        <span class="pill" style="background:var(--gold-soft);color:#9a7b14;border:1px solid #ead9a0">炸板 __BREAK__</span>
      </div>
      <div class="sub">封板率 = 涨停 ÷ (涨停+炸板) · 情绪核心指标 · __HERO_SUB__</div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num" style="color:var(--red)">__UP_CNT__</div><div class="k">上涨家数</div></div>
      <div class="kpi"><div class="v num" style="color:var(--green)">__DOWN_CNT__</div><div class="k">下跌家数</div></div>
      <div class="kpi"><div class="v num" style="color:var(--gold)">__UP_RATIO__%</div><div class="k">上涨占比</div></div>
    </div>
  </div>

  <!-- 综述 -->
  <div class="sec"><h2><span class="no">01</span>情绪综述</h2><span class="hint">整体 + 热门板块 + 高热度个股</span></div>
  <div class="card">
    __SUMMARY_ROWS__
  </div>

  <!-- 02 市场温度（图表） -->
  <div class="sec"><h2><span class="no">02</span>市场温度</h2><span class="hint">涨跌停对比 · 封板率仪表</span></div>
  <div class="grid-2">
    <div class="card" style="display:flex;align-items:center;">__TEMP_SVG__</div>
    <div class="card"><h3>市场宽度 <span class="unit">全市场 __TOTAL__ 只</span></h3>
      <div class="kv"><span class="k">上涨家数</span><span class="v num" style="color:var(--red)">__UP_CNT__</span></div>
      <div class="kv"><span class="k">下跌家数</span><span class="v num" style="color:var(--green)">__DOWN_CNT__</span></div>
      <div class="kv"><span class="k">平盘家数</span><span class="v num">__FLAT_CNT__</span></div>
      <div class="kv"><span class="k">上涨占比</span><span class="v num" style="color:var(--gold)">__UP_RATIO__%</span></div>
      <div class="kv"><span class="k">最高连板</span><span class="v num" style="color:var(--gold)">__MAXLB__ 板（__MAXLB_NAME__）</span></div>
      <div class="kv"><span class="k">涨跌停比</span><span class="v num" style="color:var(--red)">__UD_RATIO__</span></div>
    </div>
  </div>

  <!-- 02 指数印证 -->
  <div class="sec"><h2><span class="no">03</span>指数表现</h2><span class="hint">核心指数当日涨跌</span></div>
  <div class="grid">__INDEX_CARDS__</div>

  <!-- 03 板块热度（新增） -->
  <div class="sec"><h2><span class="no">04</span>板块热度</h2><span class="hint">一周涨停原因关键词统计 · __SECTOR_RANGE__</span></div>
  <div class="grid-2">
    <div class="card"><h3>热度 TOP10 <span class="unit">涨停股涉及次数</span></h3>
      <div class="lbar-legend">
        <span><i class="lg" style="background:linear-gradient(90deg,#e8b83a,#c9a227)"></i>热度高 + 走势好（主线）</span>
        <span><i class="lg" style="background:linear-gradient(90deg,#2f56c9,#1f3a93)"></i>热度高，走势一般</span>
      </div>
      <div class="sector-list">__SECTOR_TABLE__</div>
    </div>
    <div class="card"><h3>板块解读 <span class="unit">热度 vs 走势</span></h3>
      __SECTOR_VIEW__
    </div>
  </div>

  <!-- 04 一周持续关注（新增） -->
  <div class="sec"><h2><span class="no">05</span>一周持续关注</h2><span class="hint">__WEEK_RANGE__ · 持续性说明资金关注方向</span></div>
  <div class="grid-2">
    <div class="card"><h3>涨停家数趋势 <span class="unit">情绪温度计</span></h3>__WEEK_TREND_SVG__
      <div class="insight">__WEEK_INSIGHT__</div>
    </div>
    <div class="card"><h3>资金关注焦点 <span class="unit">热榜不可回溯 · 龙虎榜净买替代</span></h3>
      <table>
        <tr><th>股票</th><th>净买</th><th>资金性质</th><th>方向</th></tr>
        __FOCUS_ROWS__
      </table>
      <div class="insight">__FOCUS_INSIGHT__</div>
    </div>
  </div>
  <div class="card" style="margin-top:14px"><h3>持续涨停个股 <span class="unit">一周涨停天数 ≥3</span></h3>
    <table>
      <tr><th>股票</th><th>涨停天数</th><th>所属方向</th></tr>
      __PERSIST_ROWS__
    </table>
    <div class="insight">__PERSIST_INSIGHT__</div>
  </div>

  <!-- 05 龙虎榜资金 + 席位 -->
  <div class="sec"><h2><span class="no">06</span>龙虎榜资金</h2><span class="hint">净买入 TOP6 · 单位：亿元</span></div>
  <div class="card">
    <table>
      <tr><th>股票</th><th>代码</th><th>净买入</th><th>机构动向</th><th>上榜原因</th></tr>
      __LHB_ROWS__
    </table>
  </div>
  <!-- 06 情绪诊断 -->
  <div class="sec"><h2><span class="no">07</span>情绪诊断</h2><span class="hint">综合研判 · 模型输出</span></div>
  <div class="grid-2">
    <div class="card"><h3>多方论据 <span class="unit">支撑情绪</span></h3>__BULL__</div>
    <div class="card"><h3>空方风险 <span class="unit">压制情绪</span></h3>__BEAR__</div>
  </div>
  <div class="card" style="margin-top:14px"><h3>后市观察 <span class="unit">次日关键变量</span></h3>__WATCH__</div>

  <div class="foot">
    <b>数据口径与来源</b>：__NOTE__
  </div>

</div>
</body>
</html>"""

# ================= 组装 =================
def idx_cards():
    out = []
    for name, code, price, pct in INDEX:
        color = "var(--red)" if pct >= 0 else "var(--green)"
        sign = "+" if pct >= 0 else ""
        out.append(f'<div class="card mcard"><div class="mv num" style="color:{color}">{price:.2f}</div><div class="mk">{name} {sign}{pct:.2f}%</div></div>')
    return "".join(out)

def sector_table():
    maxv = SECTOR_TOP[0][1]
    rows = []
    for i, (name, cnt, strong) in enumerate(SECTOR_TOP[:10], 1):
        pct = cnt / maxv * 100
        if strong:  # 热度高且走势好（AI算力主线）→ 金色
            bar = 'linear-gradient(90deg,#e8b83a,#c9a227)'
            tcolor = 'var(--gold)'
        else:       # 热度高但走势一般 → 深蓝
            bar = 'linear-gradient(90deg,#2f56c9,#1f3a93)'
            tcolor = 'var(--brand)'
        rows.append(f'''<div class="srow">
          <span class="srk2">{i}</span>
          <span class="srn2">{name}</span>
          <span class="srp2" style="color:{tcolor}">{cnt}<em>次</em></span>
          <span class="srbar"><i style="width:{pct:.0f}%;background:{bar}"></i></span>
        </div>''')
    return "".join(rows)

def focus_rows():
    out = []
    for name, code, net, fund, sector in FOCUS:
        out.append(f'<tr><td><b>{name}</b></td><td class="num" style="color:var(--red);font-weight:700">{net}</td>'
                   f'<td style="color:var(--ink-2)">{fund}</td><td style="color:var(--ink-2)">{sector}</td></tr>')
    return "".join(out)

def persist_rows():
    out = []
    for name, days, sector in PERSIST_STOCK:
        color = "var(--red)" if days >= 4 else "var(--ink)"
        out.append(f'<tr><td><b>{name}</b></td><td class="num" style="color:{color};font-weight:800">{days}天</td>'
                   f'<td style="color:var(--ink-2)">{sector}</td></tr>')
    return "".join(out)

def lhb_rows():
    out = []
    for name, code, net, org, reason, chg in LHB:
        ncolor = "var(--red)" if net >= 0 else "var(--green)"
        out.append(f'<tr><td><b>{name}</b></td><td class="num" style="color:var(--ink-3)">{code}</td>'
                   f'<td class="num" style="color:{ncolor};font-weight:800">{net:+.2f}</td>'
                   f'<td class="num" style="color:var(--ink-2)">{org}</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{reason}</td></tr>')
    return "".join(out)

def summary_rows():
    """情绪综述：整体 + 热门板块 + 高热度个股"""
    rows = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag in ("整体", "锋龙股份") else "sum-tag2"
        rows.append(f'<div class="sum-row"><span class="{cls}">{tag}</span>'
                    f'<span style="color:var(--ink-2)">{desc}</span></div>')
    return "".join(rows)

def sector_view():
    """板块解读：热度 vs 走势"""
    rows = []
    for icon, title, desc in SECTOR_VIEW:
        color = "var(--red)" if "真实主线" in title else ("var(--gold)" if "最高热度" in title else "var(--ink-2)")
        rows.append(f'<div class="kv"><span class="k">{icon} {title}</span>'
                    f'<span class="v" style="color:{color};font-size:12.5px">{desc}</span></div>')
    return "".join(rows)

def kv_li(items):
    return "".join(f'<div class="kv"><span class="k">{k}</span><span class="v" style="color:var(--red)">{v}</span></div>'
                   for k, v in items)

html = (TPL
        .replace("__DATE__", DATE).replace("__WEEKDAY__", WEEKDAY)
        .replace("__DIAG_BADGE__", DIAG["badge"])
        .replace("__DIAG_SCORE__", str(DIAG["score"]))
        .replace("__DIAG_PCT__", str(DIAG["score"]))
        .replace("__DIAG_LEVEL__", DIAG["level"])
        .replace("__SEAL__", f"{TEMP['seal_rate']:.0f}")
        .replace("__UP__", str(TEMP["limit_up"]))
        .replace("__DOWN__", str(TEMP["limit_down"]))
        .replace("__BREAK__", str(TEMP["break_board"]))
        .replace("__MAXLB__", str(TEMP["max_lianban"]))
        .replace("__UP_CNT__", str(TEMP["up_cnt"]))
        .replace("__DOWN_CNT__", str(TEMP["down_cnt"]))
        .replace("__FLAT_CNT__", str(TEMP["total_cnt"] - TEMP["up_cnt"] - TEMP["down_cnt"]))
        .replace("__UP_RATIO__", f"{up_ratio:.1f}")
        .replace("__TEMP_SVG__", temp_svg())
        .replace("__INDEX_CARDS__", idx_cards())
        .replace("__SECTOR_TABLE__", sector_table())
        .replace("__WEEK_TREND_SVG__", week_trend_svg())
        .replace("__FOCUS_ROWS__", focus_rows())
        .replace("__PERSIST_ROWS__", persist_rows())
        .replace("__LHB_ROWS__", lhb_rows())
        .replace("__SUMMARY_ROWS__", summary_rows())
        .replace("__SECTOR_VIEW__", sector_view())
        .replace("__BULL__", kv_li([(f"✅ {x}", "+") for x in DIAG["bull"]]))
        .replace("__BEAR__", kv_li([(f"⚠️ {x}", "风险") for x in DIAG["bear"]]))
        .replace("__WATCH__", kv_li([(f"👀 {x}", "关注") for x in DIAG["watch"]]))
        .replace("__DIAG_EXTRA__", DIAG_EXTRA)
        .replace("__HERO_SUB__", HERO_SUB)
        .replace("__TOTAL__", str(TEMP["total_cnt"]))
        .replace("__MAXLB_NAME__", TEMP["max_lianban_name"])
        .replace("__UD_RATIO__", UD_RATIO)
        .replace("__SECTOR_RANGE__", SECTOR_RANGE)
        .replace("__WEEK_RANGE__", WEEK_RANGE)
        .replace("__WEEK_INSIGHT__", WEEK_INSIGHT)
        .replace("__FOCUS_INSIGHT__", FOCUS_INSIGHT)
        .replace("__PERSIST_INSIGHT__", PERSIST_INSIGHT)
        .replace("__NOTE__", NOTE))

out = os.path.join(BASE, f"市场情绪扫描_{DATE.replace('-', '')}.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("OK ->", out, "| size:", os.path.getsize(out), "bytes")
