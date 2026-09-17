# -*- coding: utf-8 -*-
"""紫金矿业穿透分析（个股抱团版）——由 gen_penetration.py 模板派生
个股穿透：无"ETF重仓什么"正向区，聚焦机构抱团分层 + 前十大流通股东 + 抱团质量
结构：01 穿透总览(徽章+五维) 02 机构抱团分层(公募/北向/社保险资/全口径条形) 03 前十大流通股东表
      04 抱团质量与结构(解读卡) 05 解读与风险
数据：公募 1180 只/892.3亿/10.85%（头条复盘+渤海证券 2026Q2）；北向 9.21%；全口径机构 28-31%
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import io, os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-08-21"
WEEKDAY = "周五"

# ================= 数据 =================
CFG = {
    "out_tag": "紫金矿业",
    "name": "紫金矿业", "code": "601899.SH",
    "verdict": "内外资共振 · 全口径抱团 30%", "verdict_short": "抱团",
    "verdict_note": ("紫金矿业是公募有色板块第一重仓股：1180 只基金重仓（892.3 亿/占流通 10.85%）+ 北向 9.21% + 社保/保险/私募/QFII 约 8-11%——"
                     "全口径机构持仓占流通盘 28%-31%，近三成筹码被长线机构锁定，'价值抱团'典型。"),
    "kpis": [("1180 只", "公募重仓基金数", "gd"), ("892.3 亿", "公募持仓市值", ""),
             ("20.06%", "公募+北向合计", "up"), ("28-31%", "全口径机构占流通", "")],
}

# 行情与基本信息
STOCK = {
    "px": 34.74, "px_date": "2026-08-21", "chg_pct": 2.69, "px_note": "当日 XD 除息（派 0.42 元/股）",
    "sector": "工业金属·黄金铜", "market_cap": 8655, "market_cap_date": "2026-06-30",
}

# ===== 02 机构抱团分层（类型, 占比%, 说明）=====
LAYERS = [
    ("公募基金", 10.85, "1180 只基金重仓、892.3 亿——有色板块公募第一重仓股（渤海口径主动权益 912 只/5.37%）"),
    ("北向资金", 9.21, "756.8 亿、约 23.25 亿股——二季度延续稳健加仓，外资长线底仓"),
    ("社保险资/私募/QFII", 9.5, "社保常年底仓+保险底仓入驻+高毅/阿布达比/UBS 等——测算合计约 8-11%"),
    ("全口径机构合计", 30.0, "公募+北向+社保+保险+私募+券商自营 ≈ 流通盘 28%-31%，浮动筹码稀缺"),
]
LAYER_MAX = 31.0

# ===== 03 前十大流通股东（2026-06-30：名称, 性质, 占比%, 变动）=====
SHAREHOLDERS = [
    ("闽西兴杭国有资产投资经营有限公司", "国资实控人", 22.88, "持平"),
    ("香港中央结算(代理人)有限公司", "H股托管", 22.48, "-3.26万股"),
    ("香港中央结算有限公司", "北向资金", 4.94, "+2951万股"),
    ("中国人寿保险-传统-普通保险产品", "保险", 0.85, "+2575万股"),
    ("阿布达比投资局-自有资金", "QFII", 0.58, "+1366万股"),
    ("中国太平洋人寿-分红-个人分红", "保险", 0.46, "新进"),
    ("上杭县金山贸易有限公司", "关联方", 0.42, "持平"),
    ("UBS AG", "外资行", 0.41, "持平"),
    ("上海高毅资产-高毅晓峰2号", "私募", 0.35, "持平"),
    ("全国社保基金一零三组合", "社保", 0.30, "持平"),
]

# ===== 04 抱团质量与结构（键, 值, 是否num）=====
HERD_VIEW = [
    ("公募地位", "有色板块第一重仓股，位列公募前 20 大重仓（Q2 退出前五因科技霸榜，非减持所致）", ""),
    ("北向动向", "9.21% 占流通、二季度稳健加仓——外资长线底仓，锁仓稳定性强", ""),
    ("长线资金", "社保一零三组合+中国人寿/太保+高毅晓峰+阿布达比——价值配置盘扎堆", ""),
    ("Q2 变动", "公募环比 -70125 万股（兑现部分涨幅），北向+社保+保险反向增持——高低切换中的底仓博弈", ""),
    ("筹码特征", "国资 22.88% + H股托管 22.48% 高度锁定，自由流通筹码稀缺", ""),
]
HERD_INSIGHT = "💡 抱团质量优于抱团数量：公募有色第一+北向 9.21%+社保险资私募 QFII 全谱系配置——'内外资价值抱团'，筹码锁定近三成；Q2 公募小幅兑现但长线资金增持，属于获利了结而非瓦解。"
CLOSE_ROWS = [
    ("抱团主体", "公募（1180 只）> 北向（9.21%）> 社保险资私募 QFII（8-11%）——全谱系机构"),
    ("抱团质量", "有色第一重仓 + 内外资共振 + 长线资金锁仓——价值抱团，区别于纯主题炒作"),
    ("筹码结构", "国资+H股 45%+ 高度锁定，自由流通盘机构占比近三成，浮动筹码稀缺"),
    ("边际变化", "Q2 公募小幅兑现（-70125万股）vs 北向/社保/保险增持——高低切换，底仓未动"),
    ("数据含义", "公募有色第一 + 北向 9.21% + 社保险资长线=机构把紫金当顺周期核心底仓（价值抱团非主题炒作）；Q2 公募兑现但长线增持=底仓换手而非瓦解"),
    ("投资指导", "抱团托底中期估值，但铜金价格是最终变量：上行周期机构底仓托底、回调空间有限；价格反转则 28-31% 机构筹码集中抛压会放大回撤——顺周期择时重于个股选择"),
]
CLOSE_INSIGHT = "💡 抱团数据揭示的实战意义：紫金的机构持仓是「顺周期底仓」而非「趋势筹码」——判断持有/增持的关键是铜金价格周期而非机构动向本身；公募 Q2 兑现但北向/社保/保险反向增持，说明长线资金仍认可周期中枢上移，短期拥挤度风险主要来自商品价格而非筹码结构。"
RISK_ROWS = [
    "⚠️ 商品价格风险：铜金价格是核心变量，铜价-20%/金价-15% 情景下 ROE 或降至 12-14%、机构或集中调仓",
    "⚠️ 拥挤度与波动：28-31% 流通盘机构持有，一旦金属价格趋势反转，机构集体减仓会放大下跌",
    "⚠️ 估值高位：PE/PB 均处 5 年 96% 分位（周期景气高位），均值回归空间大",
    "⚠️ 报告期滞后：持仓为 2026Q2（6-30 数据），已滞后近 2 个月，期间机构可能已调仓",
    "⚠️ 口径差异：公募基金数 1180（主动偏股全口径）/912（渤海主动权益前十大）——统计范围不同",
]
SUMMARY = [
    ("结论", "内外资价值抱团：公募有色第一重仓（1180 只/占流通 10.85%）+北向 9.21%+社保险资私募 QFII 8-11%，全口径机构占流通盘 28-31%——近三成筹码被长线机构锁定。"),
    ("公募", "1180 只基金重仓 892.3 亿，有色板块第一重仓股（公募前 20 大重仓）；Q2 环比 -70125 万股为涨幅兑现，非抱团瓦解。"),
    ("北向", "持仓 756.8 亿、占流通 9.21%，二季度稳健加仓——外资有色核心底仓，锁仓稳定性极强。"),
    ("长线", "社保一零三组合+人寿/太保+高毅晓峰+阿布达比投资局+UBS——价值配置盘全谱系扎堆。"),
    ("筹码", "国资实控人 22.88% + H股托管 22.48% 高度锁定，自由流通筹码稀缺，机构进出对股价影响放大。"),
    ("数据含义", "公募有色第一 + 北向 9.21% + 社保险资长线=机构把紫金当顺周期核心底仓（价值抱团非主题炒作）；Q2 公募兑现但北向/社保/保险反向增持=底仓换手而非瓦解。"),
    ("投资指导", "机构托底中期估值，核心变量是铜金价格周期——上行周期回调空间有限、底仓提供支撑，价格反转则 28-31% 集中筹码放大回撤；顺周期择时重于个股选择。"),
]
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，行情快照）+ 公开披露交叉验证；"
        "机构持仓数据来自 2026Q2 公募季报公开披露（今日头条机构持仓复盘/渤海证券 2026Q2 基金季报/腾讯自选股十大流通股东，2026-06-30 口径）；"
        "公募基金数口径差异（主动偏股全口径 1180 只 vs 渤海主动权益前十大 912 只）已注明；社保险资私募占比为公开数据测算值 [ASSUMED]。"
        "穿透分析为模型综合判断（模型输出），仅供研究参考，不构成个人投资建议。")

# ---- 文本/口径占位（平台可覆写；默认值 = 本报告原值，保证 skill 单独运行字节一致）----
INST_PERIOD = '2026-06-30 口径'
INST_PUB = '<b class="num">1180 只基金 · 892.3 亿 · 占流通 10.85%（有色第一）</b>'
INST_NORTH = '<b class="num">756.8 亿 · 23.25 亿股 · 占流通 9.21%</b>'
INST_LONG = '<b class="num">社保一零三 + 人寿/太保 + 高毅晓峰 + 阿布达比 ≈ 8-11%</b>'
INST_TOTAL = '<b class="num" style="color:var(--red)">机构合计占流通 28%-31%，自由浮动筹码稀缺</b>'
INST_INSIGHT = "💡 公募+北向合计已超 20%，叠加社保险资长线底仓——'内外资价值抱团'，锁仓近三成；不同于主题炒作的短线抱团，紫金的抱团主体是配置盘与长线资金。"
SH_HINT = '2026-06-30 · 国资+H股 45%+ 高度锁定'
SH_INSIGHT = "💡 前三大股东锁定流通盘超 50%：国资实控人 22.88% + H股托管 22.48% + 北向 4.94%；中国人寿/阿布达比二季度增持、社保与高毅长线持有——筹码结构'国资托底 + 外资/长线增配'。"

# ================= 渲染 =================
def layer_svg():
    """机构抱团分层条形图"""
    W = 460
    pad_l, pad_t, row_h, gap = 150, 26, 46, 8
    H = pad_t + len(LAYERS) * (row_h + gap) - gap + 30
    parts = []
    colors = ["#2f56c9", "#e5484d", "#2fa36b", "#c9a227"]
    for i, (name, pct, desc) in enumerate(LAYERS):
        y = pad_t + i * (row_h + gap)
        pct_v = 0.0 if pct is None else pct
        w = max(pct_v / LAYER_MAX * (W - pad_l - 90), 6)
        is_total = i == len(LAYERS) - 1
        c = colors[i % len(colors)]
        fw = "800" if is_total else "700"
        pct_t = "[MISSING]" if pct is None else f"{pct}%"
        parts.append(f'<text x="{pad_l-10}" y="{y+row_h/2+4:.1f}" text-anchor="end" font-size="12" font-weight="{fw}" fill="#5b6470">{name}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+5:.1f}" width="{w:.1f}" height="20" rx="6" fill="{c}" opacity="{"1" if is_total else "0.85"}"/>')
        parts.append(f'<text x="{pad_l+w+6:.1f}" y="{y+row_h/2+4:.1f}" font-size="12.5" font-weight="800" fill="{c}">{pct_t}</text>')
    parts.append(f'<text x="{pad_l}" y="{H-14}" font-size="10.5" fill="#9aa1ad">全口径为测算值 [ASSUMED] · 基准 31%（全口径上限）</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="机构抱团分层">{"".join(parts)}</svg>'

def holder_rows():
    rows = []
    for i, (name, kind, pct, chg) in enumerate(SHAREHOLDERS, 1):
        chg_c = "var(--red)" if "+" in str(chg) else ("var(--green)" if "减" in str(chg) else "var(--ink-3)")
        hl = ' style="background:#fdf9ec"' if i <= 3 else ""
        pct_t = "[MISSING]" if pct is None else f"{pct:.2f}%"
        rows.append(f'<tr{hl}><td class="num" style="color:var(--ink-3);width:26px">{i}</td>'
                    f'<td><b>{name}</b></td>'
                    f'<td style="font-size:12px;color:var(--ink-2)">{kind}</td>'
                    f'<td class="num" style="font-weight:800;color:var(--brand)">{pct_t}</td>'
                    f'<td class="num" style="color:{chg_c}">{chg}</td></tr>')
    return "".join(rows)

def kv_rows(items, last_br=False):
    out = []
    n = len(items)
    for i, it in enumerate(items):
        k, v = it[0], it[1]
        cls = ' class="num"' if len(it) > 2 and it[2] == "num" else ""
        bd = "border-bottom:1px dashed #f0f1f4;" if i < n - 1 else ""
        out.append(f'<div class="kv" style="padding:6px 0;{bd}font-size:13px"><span style="color:var(--ink-2)">{k}</span><b{cls}>{v}</b></div>')
    return "".join(out)

def summary_rows():
    out = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag in ("结论",) else "sum-tag2"
        out.append(f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>')
    return "".join(out)

def risk_rows():
    out = []
    n = len(RISK_ROWS)
    for i, r in enumerate(RISK_ROWS):
        bd = "border-bottom:1px dashed #f0f1f4;" if i < n - 1 else ""
        out.append(f'<div class="kv" style="padding:6px 0;{bd}font-size:12.5px;color:var(--ink-2)">{r}</div>')
    return "".join(out)

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>穿透分析__DATE_SHOW__</title>
<style>
  :root{
    --brand:#1f3a93; --brand-soft:#eef2fb; --gold:#c9a227; --gold-soft:#fdf9ec;
    --red:#e5484d; --green:#2fa36b; --ink:#1d2433; --ink-2:#5b6470; --ink-3:#9aa1ad;
    --border:#e8eaee; --bg:#f4f5f7;
    --shadow-sm:0 1px 3px rgba(16,24,40,.06); --shadow-md:0 4px 14px rgba(16,24,40,.08);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;padding:28px 20px 40px}
  .num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum"}
  .wrap{max-width:960px;margin:0 auto}
  .card{background:#fff;border:1px solid var(--border);border-radius:14px;padding:18px 20px;margin-bottom:16px;box-shadow:var(--shadow-sm);transition:box-shadow .18s,transform .18s}
  .card:hover{box-shadow:var(--shadow-md);transform:translateY(-1px)}
  .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  @media(max-width:760px){.grid-2{grid-template-columns:1fr}}
  .sec{display:flex;align-items:baseline;gap:10px;margin:26px 0 12px;flex-wrap:wrap}
  .sec h2{font-size:17px;color:var(--ink);font-weight:800}
  .sec .no{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:22px;padding:0 6px;border-radius:6px;background:linear-gradient(135deg,#e8b83a,#c9a227);color:#fff;font-size:12px;font-weight:800}
  .sec .hint{font-size:11.5px;color:var(--ink-3);font-weight:400}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{background:#f7f8fa;color:var(--ink-2);font-weight:600;font-size:11.5px;padding:8px 10px;text-align:left;border-bottom:1px solid var(--border)}
  td{padding:8px 10px;border-bottom:1px dashed #f0f1f4}
  tbody tr:hover{background:#f7f9fd}
  .vbadge{display:inline-block;font-size:15px;font-weight:800;padding:4px 18px;border-radius:24px;color:#fff;background:linear-gradient(135deg,#e5484d,#d93a40);border:1px solid #d93a40;box-shadow:0 2px 8px rgba(229,72,77,.25)}
  .kpi{background:linear-gradient(180deg,#fff,#fbfcfe);border:1px solid var(--border);border-radius:12px;padding:12px 10px;text-align:center;min-width:0}
  .kpi .v{font-size:19px;font-weight:800;color:var(--brand)}
  .kpi .v.gd{color:var(--gold)}
  .kpi .v.up{color:var(--red)}
  .kpi .v.dn{color:var(--green)}
  .kpi .k{font-size:10.5px;color:var(--ink-3);margin-top:3px}
  .hero{background:linear-gradient(135deg,#1f3a93 0%,#2a4db8 60%,#3358c9 100%);border-radius:16px;padding:22px 24px;color:#fff;position:relative;overflow:hidden}
  .hero::after{content:"";position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(201,162,39,.35),transparent 70%)}
  .hero::before{content:"";position:absolute;left:-40px;bottom:-80px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.08),transparent 70%)}
  .hero .title{font-size:24px;font-weight:800;letter-spacing:.5px}
  .hero .tcode{font-size:14px;color:rgba(255,255,255,.65);font-weight:600;margin-left:8px}
  .hero .sub{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}
  .pill{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px}
  .pill.gold{background:rgba(201,162,39,.2);color:#f5d47a;border:1px solid rgba(201,162,39,.4)}
  .pill.brand{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.25)}
  .hero .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px;position:relative;z-index:1}
  .hero .kpi{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.15);backdrop-filter:blur(4px)}
  .hero .kpi .v{color:#fff}
  .hero .kpi .v.gd{color:#f5d47a}
  .hero .kpi .k{color:rgba(255,255,255,.7)}
  .insight{margin-top:12px;padding:10px 14px;border-radius:10px;background:linear-gradient(120deg,#fdf9ec,#faf3d8);border:1px solid #eddcab;font-size:12.5px;font-weight:600;color:#8a6d12;line-height:1.7}
  .sum-row{display:flex;align-items:baseline;gap:8px;padding:9px 0;border-bottom:1px dashed #f0f1f4;font-size:13px;flex-wrap:wrap}
  .sum-row:last-child{border-bottom:none}
  .sum-tag{flex-shrink:0;font-size:11px;font-weight:800;color:#fff;background:linear-gradient(180deg,var(--gold),#a8871d);border-radius:5px;padding:2px 9px}
  .sum-tag2{flex-shrink:0;font-size:11px;font-weight:800;color:var(--brand);background:var(--brand-soft);border:1px solid #d5def5;border-radius:5px;padding:2px 9px}
  .note{font-size:11px;color:var(--ink-3);margin-top:14px;line-height:1.7}
  @media print{body{background:#fff}.card{box-shadow:none;border-color:#ddd}}
</style>
</head>
<body>
<div class="wrap">

  <!-- Hero -->
  <div class="hero">
    <div class="title">穿透分析 · __NAME__ <span class="tcode">__CODE__</span></div>
    <div class="sub">
      <span class="pill gold">__WEEKDAY__ · __DATE__</span>
      <span class="pill brand">⛏️ __SECTOR__</span>
      <span class="pill brand">反向 · 股票被谁抱团</span>
    </div>
    <div class="kpis">__KPI_ROWS__</div>
  </div>

  <!-- 01 穿透总览 -->
  <div class="sec"><h2><span class="no">01</span>穿透总览</h2><span class="hint">反向穿透 · 模型输出</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      <span class="vbadge">__VERDICT__</span>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
  </div>

  <!-- 02 机构抱团分层 -->
  <div class="sec"><h2><span class="no">02</span>机构抱团分层</h2><span class="hint">公募 / 北向 / 长线资金 · 占流通盘比例</span></div>
  <div class="grid-2">
    <div class="card" style="display:flex;align-items:center">__LAYER_SVG__</div>
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:8px">抱团结构说明 <span style="font-size:11px;color:var(--ink-3)">__INST_PERIOD__</span></h3>
      <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">公募</span>__INST_PUB__</div>
      <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">北向</span>__INST_NORTH__</div>
      <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">社保险资私募QFII</span>__INST_LONG__</div>
      <div class="kv" style="padding:6px 0;font-size:13px"><span style="color:var(--ink-2)">全口径</span>__INST_TOTAL__</div>
      <div class="insight">__INST_INSIGHT__</div>
    </div>
  </div>

  <!-- 03 前十大流通股东 -->
  <div class="sec"><h2><span class="no">03</span>前十大流通股东</h2><span class="hint">__SH_HINT__</span></div>
  <div class="card">
    <table>
      <tr><th>#</th><th>股东</th><th>性质</th><th>持股比例</th><th>变动</th></tr>
      __HOLDER_ROWS__
    </table>
    <div class="insight">__SH_INSIGHT__</div>
  </div>

  <!-- 04 抱团质量与结构 -->
  <div class="sec"><h2><span class="no">04</span>抱团质量与结构</h2><span class="hint">数量之外看质量 · 模型输出</span></div>
  <div class="card">
    <h3 style="font-size:14px;margin-bottom:8px">抱团解读</h3>
    __HERD_VIEW_ROWS__
  </div>

  <!-- 05 解读与风险 -->
  <div class="sec"><h2><span class="no">05</span>解读与风险</h2><span class="hint">抱团结论 · 模型输出</span></div>
  <div class="card">
    <h3 style="font-size:14px;margin-bottom:8px">抱团结论</h3>
    __CLOSE_ROWS__
    <h3 style="font-size:14px;margin:12px 0 8px">风险提示</h3>
    __RISK_ROWS__
  </div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

def main():
    html = TPL
    html = (html.replace("__DATE_SHOW__", DATE.replace("-", ""))
            .replace("__WEEKDAY__", WEEKDAY)
            .replace("__DATE__", DATE)
            .replace("__NAME__", CFG["name"])
            .replace("__CODE__", CFG["code"])
            .replace("__SECTOR__", STOCK["sector"])
            .replace("__VERDICT__", CFG["verdict"])
            .replace("__VERDICT_NOTE__", CFG["verdict_note"])
            .replace("__KPI_ROWS__", kpi_rows())
            .replace("__SUMMARY_ROWS__", summary_rows())
            .replace("__LAYER_SVG__", layer_svg())
            .replace("__HOLDER_ROWS__", holder_rows())
            .replace("__HERD_VIEW_ROWS__", kv_rows(HERD_VIEW) + f'<div class="insight">{HERD_INSIGHT}</div>')
            .replace("__CLOSE_ROWS__", kv_rows(CLOSE_ROWS) + f'<div class="insight">{CLOSE_INSIGHT}</div>')
            .replace("__RISK_ROWS__", risk_rows())
                        .replace("__INST_PERIOD__", INST_PERIOD)
            .replace("__INST_PUB__", INST_PUB)
            .replace("__INST_NORTH__", INST_NORTH)
            .replace("__INST_LONG__", INST_LONG)
            .replace("__INST_TOTAL__", INST_TOTAL)
            .replace("__INST_INSIGHT__", INST_INSIGHT)
            .replace("__SH_HINT__", SH_HINT)
            .replace("__SH_INSIGHT__", SH_INSIGHT)
.replace("__NOTE__", NOTE))
    out_path = os.path.join(BASE, f"穿透分析_{CFG['out_tag']}_{DATE.replace('-', '')}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK ->", out_path, "| size:", len(html.encode("utf-8")))

def kpi_rows():
    out = []
    for v, k, cls in CFG["kpis"]:
        c = f" {cls}" if cls else ""
        out.append(f'<div class="kpi"><div class="v num{c}">{v}</div><div class="k">{k}</div></div>')
    return "".join(out)

if __name__ == "__main__":
    main()
