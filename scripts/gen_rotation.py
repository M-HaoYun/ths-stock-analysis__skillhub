# -*- coding: utf-8 -*-
"""A股板块轮动雷达 HTML 生成器 v1.6（模板）
【模板使用说明】回答"钱在流向哪个板块？"：
①hithink CLI：`index catalog --tag industry` 取板块代码（881xxx.TI 一级行业）→ `index history` 拉 60 日
收盘+成交额（板块指数历史含 turnover）→ `index history` 拉上证 000001.SH 做基准
②计算动量：1日/5日/20日/60日涨幅 + 5日均成交/20日均成交量比 + 相对上证 20 日超额
③轮动信号：5日 vs 20日 动量比较（加速/减速）+ 成交放量/缩量
④替换 BASE/DATE 与数据区（CFG/SECTORS/SIGNALS/FLOW/SUMMARY/ETF_ROWS/KPI/INSIGHT_*/HL/NOTE）
⑤运行 → 输出 `板块轮动雷达_{YYYYMMDD}.html`
结构（v1.5）：01 轮动综述(徽章+五维+**主线→ETF 映射小节**) 02 板块轮动表(N板块×60/20/5/1日矩阵+成交+量比+超额) 03 轮动信号 04 资金流向
数据坑/经验：
· 板块指数历史含 turnover（成交额）→ 可算量比=5日均成交额/20日均成交额（>1 放量），动量+资金双维度一源搞定
· 轮动表内"20日"数值列与"20日动量"进度条列=同一数据双列展示（确认非数据错误）→ 已删进度条列，避免与排名区重复
· 综述徽章 __VERDICT__ 只替换一次（模板曾把同一占位符放 vbadge+<b> 两处导致文字重复）——占位符在模板中只能出现一次，需重复显示时改用不同占位符
· v1.4：hero KPI（最强板块/正收益家数/最大资金池）、02 表格 hint（板块数+上证基准）、三处 insight 全部占位符化进数据区
· v1.5：01 区新增「主线→ETF 映射」小节（ETF_ROWS 数据区驱动）
· v1.6：KPI 第 2 格标签占位符化（原硬编码"20日正收益板块"）→ 数据区 pos_cnt_k 可自定义（如普跌日写"今日红盘板块"）
  （v1.3 曾硬编码在 TPL，换周期必留旧数值残留——换周期前仍要 grep 旧日期/旧板块名复核）
· v1.5：①hero 判定格用 __VERDICT_SHORT__（短版），01 综述徽章用 __VERDICT__（长版带板块名）——用户反馈"轮动总数里没写清哪个板块低位反弹/高位退潮"，判定词必须含具体板块
  ②01 综述卡新增"主线→ETF 映射"小节（ETF_ROWS 数据驱动）：轮动报告直接给出最关联 ETF 及覆盖口径
  （ETF 名称/代码须 `fund profile/snapshot` 实测验证 + 跟踪指数 WebSearch 公开披露核对——板块行业指数≠ETF 成分，口径差必须在说明列写明，
   如"中证农业含种植仅~9%"、"931160 20日 vs 881129.TI 动量不同"）
· data.item 为时间升序，最新交易日取 item[-1]（勿取 [0]）；校验 date_ms 是否为目标交易日
口径：板块指数为同花顺行业指数（881xxx.TI）；动量=收盘价涨跌幅；量比=5日均成交额/20日均成交额（>1 放量）；
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-08-21"
# ================= 数据 =================
CFG = {
    "name": "板块轮动雷达", "code": "22 个一级行业 · 2026-06-01~08-21",
    "verdict": "贵金属独强 · 通信/软件中期强短期回调 · 大金融垫底", "verdict_short": "贵金属独强",
    "verdict_note": ("钱在流向：贵金属（金价新高，20日+35.2% 加速放量）与顺周期资源（工业金属/化学原料/煤炭）；"
                     "科技（通信设备/软件开发）中期强但短期回调=获利回吐；大金融（证券/保险）垫底。"
                     "市场处'涨价资源+AI 科技'双主线轮动期，贵金属是最强轮动信号。"),
}
# 22 板块轮动数据：(名称, 1日%, 5日%, 20日%, 60日%, 当日成交亿, 5日量比, 20日超额%)
SECTORS = [
    ("贵金属", 5.3, 13.4, 35.2, 21.4, 471, 1.06, 32.8),
    ("通信设备", 1.4, -0.9, 15.4, -7.4, 1661, 1.00, 13.0),
    ("工业金属", 2.6, 2.3, 13.5, -5.4, 387, 0.92, 11.1),
    ("消费电子", 1.3, -0.5, 13.3, -11.9, 475, 0.98, 10.9),
    ("软件开发", -0.2, -3.9, 13.2, -10.5, 292, 0.79, 10.8),
    ("食品加工制造", -1.5, -0.8, 12.0, -6.7, 108, 1.15, 9.6),
    ("计算机设备", 0.8, -2.1, 11.9, -7.2, 212, 0.84, 9.5),
    ("化学制药", -3.7, -2.0, 11.3, 4.4, 686, 1.19, 8.9),
    ("光伏设备", 1.2, -0.3, 11.1, -17.9, 210, 0.97, 8.7),
    ("电池", 1.3, -1.9, 10.8, -19.1, 545, 0.93, 8.4),
    ("化学原料", 0.4, 2.4, 9.6, -3.9, 144, 1.08, 7.2),
    ("煤炭开采加工", 0.2, 1.2, 9.0, -6.3, 130, 1.04, 6.6),
    ("军工电子", 0.9, -4.1, 7.6, -13.5, 150, 0.95, 5.2),
    ("工程机械", 0.0, -0.8, 6.5, -9.2, 46, 0.82, 4.1),
    ("半导体", 0.4, -1.9, 5.0, -0.1, 2361, 0.93, 2.6),
    ("钢铁", 0.1, 0.3, 4.6, -8.5, 68, 0.86, 2.2),
    ("白酒", -1.7, -5.0, 4.0, -9.0, 87, 0.79, 1.6),
    ("油气开采及服务", 1.2, 2.9, 3.4, -0.2, 80, 0.95, 1.0),
    ("银行", -0.4, 2.2, 1.8, 2.9, 229, 0.91, -0.6),
    ("电力", -0.4, -3.2, 0.2, -21.2, 230, 0.72, -2.2),
    ("证券", -0.1, -2.1, -1.5, 0.5, 159, 0.82, -3.9),
    ("保险", 1.0, 1.7, -4.5, 4.2, 100, 0.86, -6.9),
]
# 轮动信号（板块, 信号类型, 描述）
SIGNALS = [
    ("贵金属", "加速 · 放量", "20日+35.2%/5日+13.4%/1日+5.3% 全维度走强，量比1.06——金价新高主线资金加速流入，最强轮动信号"),
    ("工业金属/化学原料/煤炭", "资源回暖", "20日 +9.6~13.5%，5日仍正——顺周期补涨，量比>1 温和放量"),
    ("通信设备/软件开发", "中期强 · 短期回调", "20日 +13~15% 但 5日转负——AI 算力主线获利回吐，中期趋势未破"),
    ("化学制药", "放量上攻", "20日+11.3%，量比 1.19 全市场最高——创新药资金流入明显"),
    ("银行/油气/保险", "低波动补涨", "5日转正、20日低位——防御资金小幅回流，非主攻方向"),
    ("证券/保险", "垫底滞涨", "20日 -1.5%/-4.5%——大金融未获资金青睐，券商行情缺席"),
]
# 资金流向（板块, 当日成交亿, 量比, 资金状态）
FLOW = [
    ("半导体", 2361, 0.93, "最大资金池 · 略缩量"), ("通信设备", 1661, 1.00, "科技主战场 · 平量"),
    ("化学制药", 686, 1.19, "放量流入（最高量比）"), ("电池", 545, 0.93, "缩量整理"),
    ("贵金属", 471, 1.06, "放量流入 · 金价新高"), ("消费电子", 475, 0.98, "平量"),
]
SUMMARY = [
    ("结论", "钱流向=贵金属（加速）+顺周期资源（回暖）+创新药（放量）；科技中期强但短期回吐；大金融垫底——'涨价资源+AI科技'双主线轮动，贵金属是 8-21 最强信号。"),
    ("最强", "贵金属 20日+35.2% 断层第一、5日+13.4% 加速、量比 1.06——金价新高驱动的独立主线（与龙虎榜山东黄金涨停派发呼应，资金高位集中）。"),
    ("科技", "通信设备/软件开发/计算机设备 20日 +11.9~15.4% 但 5日 -0.9~-3.9%——AI 算力主线获利回吐，半导体 20日仅+5.0% 跑输（资金池最大但动量中性）。"),
    ("资源", "工业金属+13.5%/化学原料+9.6%/煤炭+9.0% 5日仍正——顺周期补涨启动，量比 1.04-1.08 温和放量。"),
    ("滞后", "证券/保险 20日 -1.5%/-4.5%、电力 60日 -21.2%——大金融与公用事业垫底，市场风险偏好仍偏成长与涨价资源。"),
]
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.7，index catalog/history 行业指数 881xxx.TI + 上证 000001.SH 基准）；"
        "动量=板块指数收盘价涨跌幅（1/5/20/60 交易日）；量比=5日均成交额/20日均成交额（>1 放量）；超额=板块 20 日涨幅-上证同期；"
        "轮动信号为模型综合判断（模型输出）。仅供研究参考，不构成个人投资建议。")
# Hero KPI 与 insight（v1.4 全部进数据区，换周期只改这里）
KPI = {"strong": "+35.2%", "strong_k": "最强板块(贵金属 20日)", "pos_cnt": "11 个", "pos_cnt_k": "20日正收益板块", "pool": "2361 亿", "pool_k": "最大资金池(半导体)"}
TABLE_HINT = "22 板块 × 多窗口动量矩阵 · 红强绿弱 · 上证基准 20日+2.4%"
INSIGHT_TABLE = "💡 贵金属断层第一（20日+35.2%、5日+13.4% 加速）；科技 20日强但 5日转负（回调）；半导体资金池最大（2361亿）但动量中性——钱从科技高位流向贵金属与顺周期资源。"
INSIGHT_SIGNAL = "💡 核心轮动信号：贵金属（加速+放量）→ 资源（回暖）→ 科技（中期强短期回调）；若贵金属见顶回落，资金或回流科技或切向创新药（放量 1.19）——跟踪金价与 AI 主线成交。"
INSIGHT_FLOW = "💡 资金池集中在半导体/通信（科技存量博弈、量比≈1 无增量），增量资金流向贵金属（1.06）与化学制药（1.19）——\"存量科技 + 增量资源医药\"的结构。"
HL = "贵金属"  # 轮动表高亮行（最强板块）

# ETF 映射（板块定位, ETF 名称+代码, 覆盖口径说明）——渲染在 01 综述"主线→ETF 映射"小节
# ETF 名称/代码必须 fund profile/snapshot 实测；跟踪指数与成分口径 WebSearch 公开披露核对后写清差异
ETF_ROWS = [
    ("（示例占位）", "按当日主线填写关联 ETF", "本行仅占位验证布局——实际使用时按当日主线/信号板块填写，ETF 名称代码须 `fund profile/snapshot` 实测，跟踪指数与成分口径 WebSearch 公开披露核对后再写说明"),
]
# ETF 小节副标题（模板 etf_rows() 里以 __ETF_ETL_SUBTITLE__ 占位）：skill 单独运行=下方原文（产物不变）；
# 平台注入数据区时会覆盖为与实际做法一致的文案（占位符机制：数据区变量驱动模板文本，避免写死）。
ETF_ETL_SUBTITLE = "ETF 名称/代码经 hithink fund 实测 · 跟踪指数为公开披露口径（WebSearch 核对）"

# ================= 渲染 =================
def rot_table():
    rows = ""
    for i, (name, d1, d5, d20, d60, tv, ratio, ex) in enumerate(SECTORS, 1):
        # 动量色（红强绿弱，20日为主）
        def c(v):
            if v >= 10: return "color:#e5484d;font-weight:800"
            if v >= 5: return "color:#e5484d"
            if v >= 0: return "color:#b04a30"
            if v >= -5: return "color:#2fa36b"
            return "color:#2fa36b;font-weight:800"
        ratio_c = "var(--red)" if ratio >= 1.05 else ("var(--gold)" if ratio >= 1.0 else "var(--ink-2)")
        hl = ' style="background:#fdf9ec"' if name == HL else ""
        rows += (f'<tr{hl}><td class="num" style="color:var(--ink-3);width:26px">{i}</td>'
                 f'<td><b>{name}</b></td>'
                 f'<td class="num" style="{c(d60)}">{d60:+.1f}%</td>'
                 f'<td class="num" style="{c(d20)}">{d20:+.1f}%</td>'
                 f'<td class="num" style="{c(d5)}">{d5:+.1f}%</td>'
                 f'<td class="num" style="{c(d1)}">{d1:+.1f}%</td>'
                 f'<td class="num" style="color:var(--ink-2)">{tv:.0f}</td>'
                 f'<td class="num" style="color:{ratio_c};font-weight:700">{ratio:.2f}</td>'
                 f'<td class="num" style="color:var(--ink-2)">{ex:+.1f}%</td></tr>')
    return rows

def signal_rows():
    out = ""
    for name, tag, desc in SIGNALS:
        out += (f'<div class="kv"><span class="k" style="flex:0 0 150px">{name}</span>'
                f'<span class="sig-tag">{tag}</span>'
                f'<span class="v" style="color:var(--ink-2);font-size:12px;flex:1;text-align:right">{desc}</span></div>')
    return out

def flow_rows():
    rows = ""
    for name, tv, ratio, state in FLOW:
        rc = "var(--red)" if ratio >= 1.05 else "var(--gold)"
        rows += (f'<tr><td><b>{name}</b></td><td class="num" style="font-weight:700">{tv:.0f}亿</td>'
                 f'<td class="num" style="color:{rc};font-weight:700">{ratio:.2f}</td>'
                 f'<td style="color:var(--ink-2);font-size:12px">{state}</td></tr>')
    return rows

def summary_rows():
    out = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag == "结论" else "sum-tag2"
        out.append(f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>')
    return "".join(out)

def etf_rows():
    """主线 → ETF 映射小节（v1.5）：ETF_ROWS = [(板块定位, ETF 名称+代码, 覆盖口径说明), ...]"""
    rows = ""
    for sec, etf, note in ETF_ROWS:
        rows += (f'<div class="kv"><span class="k" style="flex:0 0 218px;font-size:12.5px">{sec}</span>'
                 f'<span style="flex:1;font-size:13px;text-align:right"><b>{etf}</b>'
                 f' <span style="color:var(--ink-3);font-weight:400;font-size:12px">｜ {note}</span></span></div>')
    block = ('<div style="margin-top:14px;border-top:1px dashed #eddcab;padding-top:8px">'
             '<div style="display:flex;align-items:baseline;gap:8px;margin-bottom:4px">'
             '<span style="font-size:12px;font-weight:800;color:#8a6d12;letter-spacing:.5px">🎯 主线 → ETF 映射</span>'
             '<span style="font-size:11px;color:var(--ink-3)">__ETF_ETL_SUBTITLE__</span>'
             '</div>' + rows + '</div>')
    return block

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>板块轮动雷达_{DATE}</title>
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
  .pill { display:inline-block; font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px; }
  .pill.brand { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
  .pill.gold { background:var(--gold-soft); color:#8a6d12; border:1px solid #eddcab; }
  .vbadge { display:inline-block; font-size:15px; font-weight:800; padding:4px 18px; border-radius:24px; border:1px solid; color:var(--red); background:#fdeeee; border-color:#e5484d33; }
  .sig-tag { flex:0 0 132px; text-align:center; font-size:10.5px; font-weight:700; color:var(--brand); background:var(--brand-soft); border:1px solid #d5def5; border-radius:4px; padding:1px 8px; }
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
  .hero .kpi .v.up { color:var(--red); } .hero .kpi .v.dn { color:var(--green); } .hero .kpi .v.gd { color:var(--gold); } .hero .kpi .v.hot { color:var(--red); }
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
  th { text-align:left; font-size:11.5px; color:var(--ink-3); font-weight:600; padding:6px 8px; border-bottom:2px solid var(--border); white-space:nowrap; }
  td { padding:7px 8px; border-bottom:1px dashed #f0f1f4; vertical-align:middle; }
  tbody tr:nth-child(even) { background:#fafbfc; }
  tbody tr:hover { background:var(--brand-soft); }
  .kv { display:flex; justify-content:space-between; align-items:baseline; gap:8px; padding:7px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
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
      <div class="title">板块轮动雷达</div>
      <div class="sub">
        <span class="pill gold">钱在流向哪个板块？</span>
        <span class="pill brand">__DATE__</span>
        <span class="pill brand">__CODE__</span>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num up">__KPI_STRONG__</div><div class="k">__KPI_STRONG_K__</div></div>
      <div class="kpi"><div class="v num up">__KPI_POS__</div><div class="k">__KPI_POS_K__</div></div>
      <div class="kpi"><div class="v num gd">__KPI_POOL__</div><div class="k">__KPI_POOL_K__</div></div>
      <div class="kpi"><div class="v num">__VERDICT_SHORT__</div><div class="k">轮动判定</div></div>
    </div>
  </div>

  <!-- 01 轮动综述 -->
  <div class="sec"><h2><span class="no">01</span>轮动综述</h2><span class="hint">五维总结 · 模型输出</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      <span class="vbadge">__VERDICT__</span>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
    __ETF_BLOCK__
  </div>

  <!-- 02 板块轮动表 -->
  <div class="sec"><h2><span class="no">02</span>板块轮动表</h2><span class="hint">__TABLE_HINT__</span></div>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>#</th><th>板块</th><th>60日</th><th>20日</th><th>5日</th><th>1日</th><th>成交(亿)</th><th>量比</th><th>超额20日</th></tr>
      __ROT_TABLE__
    </table>
    <div class="insight">__INSIGHT_TABLE__</div>
  </div>

  <!-- 03 轮动信号 -->
  <div class="sec"><h2><span class="no">03</span>轮动信号</h2><span class="hint">动量切换 · 5日 vs 20日</span></div>
  <div class="card">__SIGNAL_ROWS__
    <div class="insight">__INSIGHT_SIGNAL__</div>
  </div>

  <!-- 04 资金流向 -->
  <div class="sec"><h2><span class="no">04</span>资金流向</h2><span class="hint">成交额池 + 量比 · 亿</span></div>
  <div class="card">
    <table>
      <tr><th>板块</th><th>当日成交</th><th>量比</th><th>资金状态</th></tr>
      __FLOW_ROWS__
    </table>
    <div class="insight">__INSIGHT_FLOW__</div>
  </div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
html = (TPL
        .replace("__DATE__", DATE).replace("__CODE__", CFG["code"])
        .replace("__VERDICT__", CFG["verdict"]).replace("__VERDICT_SHORT__", CFG["verdict_short"]).replace("__VERDICT_NOTE__", CFG["verdict_note"])
        .replace("__SUMMARY_ROWS__", summary_rows()).replace("__ETF_BLOCK__", etf_rows())
        .replace("__ETF_ETL_SUBTITLE__", ETF_ETL_SUBTITLE)
        .replace("__ROT_TABLE__", rot_table())
                .replace("__SIGNAL_ROWS__", signal_rows())
        .replace("__FLOW_ROWS__", flow_rows())
        .replace("__KPI_STRONG__", KPI["strong"]).replace("__KPI_STRONG_K__", KPI["strong_k"])
        .replace("__KPI_POS__", KPI["pos_cnt"]).replace("__KPI_POS_K__", KPI["pos_cnt_k"])
        .replace("__KPI_POOL__", KPI["pool"]).replace("__KPI_POOL_K__", KPI["pool_k"])
        .replace("__TABLE_HINT__", TABLE_HINT)
        .replace("__INSIGHT_TABLE__", INSIGHT_TABLE)
        .replace("__INSIGHT_SIGNAL__", INSIGHT_SIGNAL)
        .replace("__INSIGHT_FLOW__", INSIGHT_FLOW)
        .replace("{DATE}", DATE.replace("-", ""))
        .replace("__NOTE__", NOTE))

out_path = os.path.join(BASE, f"板块轮动雷达_{DATE.replace('-', '')}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {out_path} | size: {len(html.encode('utf-8'))} bytes")
