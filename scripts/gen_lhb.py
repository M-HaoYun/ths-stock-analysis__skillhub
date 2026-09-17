# -*- coding: utf-8 -*-
"""A股龙虎榜事件解读 HTML 生成器 v1.1（模板）
【模板使用说明】生成某交易日龙虎榜事件解读：①用 hithink-finance CLI 拉取当日龙虎榜
（special dragon-tiger --date <YYYY-MM-DD> 普通榜 + --board-type org 机构榜）
②WebSearch 补充知名游资席位动向与复盘框架（接口无席位明细，页面必须标注"WebSearch 公开披露"）
③替换下方 BASE/DATE/WEEKDAY 与数据区（OVERVIEW/NET_TOP/ORG_BUY/ORG_SELL/HM_BUY/HM_SELL/SEATS/DIVERGE/THEME/FOCUS/SCENARIO/WARN/SUMMARY）
④运行脚本 → 输出 `龙虎榜事件解读_{YYYYMMDD}.html`
【数据来源铁律】hithink 能取到的一律走 CLI；接口没有的字段（如买卖席位明细）宁可用公开披露补齐并显式标注来源，也不编造
数据坑：change 为小数比例(0.10=+10%)；同股多次上榜需合并；hot_money_net_value 部分条目缺失用 .get()；
机构榜才有 org_net_value/org_buy_num/org_sell_num 字段；Hero KPI 正负号必须用 {:+.2f} 格式化（禁止硬编码"+"，否则负值显示"+-"）；
模板 insight/副标等当日叙事换日期必须逐一检查硬编码残留（副标日期用 __DATE__ 占位符）
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-01-28"
WEEKDAY = "周三"

# ================= 数据 =================
OVERVIEW = {
    "count": 83, "stock_cnt": 73, "org_cnt": 53, "org_stock": 49,
    "net_total": -3.97, "limit_up": 41, "limit_down": 12, "up_cnt": 50, "down_cnt": 23,
}
NET_TOP = [
    ("网宿科技", "300017", 20.34, 9.40, 15.1, "云计算·多模态AI·AI智能体"),
    ("宏景科技", "301396", 5.56, 1.56, 7.0, "ChatGPT·财税数字化·云计算"),
    ("康强电子", "002119", 2.55, 2.72, 10.0, "芯片·存储·先进封装"),
    ("燕东微", "688172", 1.98, -0.24, 17.6, "大基金持股·第三代半导体"),
    ("英方软件", "688435", 1.78, 0.59, 17.8, "华为鲲鹏·华为欧拉·云计算"),
    ("章源钨业", "002378", 1.74, 0.00, 7.8, "小金属·钨"),
    ("普冉股份", "688766", 1.72, -3.58, 14.6, "芯片·MCU·存储"),
    ("可川科技", "603052", 1.61, -0.06, 10.0, "CPO·OLED·芯片"),
]
ORG_BUY = [
    ("普冉股份", "688766", 3.67, 2, 0, "存储芯片，机构2家买入0卖出"),
    ("燕东微", "688172", 3.12, 4, 1, "第三代半导体，4家机构买入"),
    ("宏景科技", "301396", 2.99, 3, 2, "算力租赁，三家机构布局"),
    ("网宿科技", "300017", 2.35, 1, 2, "AI算力/CDN，机构参与"),
    ("可川科技", "603052", 1.45, 2, 0, "CPO封装材料，机构买入"),
    ("英方软件", "688435", 1.37, 2, 0, "华为鲲鹏生态，机构买入"),
]
ORG_SELL = [
    ("赤峰黄金", "600988", -5.04, "涨停派发，机构大额出逃"),
    ("好想你", "002582", -1.07, "高位兑现"),
    ("红宝丽", "002165", -0.99, "化工高位"),
    ("豫光金铅", "600531", -0.83, "有色涨停兑现"),
    ("三维通信", "002115", -0.65, "AI应用冲高回落"),
]
HM_BUY = [
    ("网宿科技", "300017", 9.40, "小鳄鱼/量化/成都系合力"),
    ("康强电子", "002119", 2.72, "中山东路+6020万"),
    ("宏景科技", "301396", 1.56, "短线资金"),
    ("锦鸡股份", "300798", 1.48, "20cm染料，游资打板"),
    ("星环科技", "688031", 1.46, "股价-15.1%游资逆势抄底"),
    ("豫光金铅", "600531", 1.44, "量化基金+1.23亿"),
]
HM_SELL = [
    ("中金黄金", "600489", -5.17, "涨停派发，量化一致性抛售"),
    ("普冉股份", "688766", -3.58, "游资离场，机构吸筹"),
    ("浙文互联", "600986", -1.44, "AI应用回落"),
    ("三维通信", "002115", -1.01, "成都系卖出"),
    ("湖南白银", "002716", -0.59, "有色涨停兑现"),
]
SEATS = [
    ("小鳄鱼", "网宿科技", "+3.37亿", "东方证券上海源深路，大游资回归算力主线"),
    ("量化基金", "网宿科技", "+2.05亿", "开源证券西安太华路，算力扫货"),
    ("成都系", "铜陵有色/网宿", "+2.07亿/+1.07亿", "买资源+买算力，多线布局"),
    ("佛山系", "网宿科技", "-2.31亿", "国泰海通三亚迎宾路，高位兑现"),
    ("中山东路", "康强电子/宏景", "+6020万/-5982万", "存储买入、算力减仓"),
    ("深南东路", "盛达资源", "+1.01亿", "有色低位承接"),
    ("思明南路", "志特新材", "-5997万", "高位止损离场"),
    ("徐晓", "四川黄金", "+4697万", "黄金方向小仓位试探"),
    ("紫阳东路", "巨力索具", "[MISSING]", "商业航天涨停参与"),
    ("机构", "普冉/燕东微/宏景", "+3.67/+3.12/+2.99亿", "半导体+算力主线主力"),
]
DIVERGE = [
    ("赤峰黄金", -5.04, 0.24, "涨停派发 · 机构出逃", "金价新高涨停但机构-5.04亿大额出逃、北向同步卖出——利好兑现型派发，'边拉边出货'典型"),
    ("普冉股份", 3.67, -3.58, "机构吸筹 · 游资离场", "存储芯片机构2家买入0卖出+3.67亿 vs 游资-3.58亿——国产替代主线筹码结构改善"),
    ("中金黄金", 1.31, -5.17, "机构接盘 · 游资出逃", "涨停股机构净买+1.31亿 vs 游资/量化-5.17亿——高位分歧剧烈"),
    ("网宿科技", 2.35, 9.40, "机构游资合力", "AI算力新主线，小鳄鱼+3.37亿/量化+2.05亿/成都系共振，资金做多信号明确"),
    ("燕东微", 3.12, -0.24, "机构主导", "4家机构买入1家卖出+3.12亿，+17.6%放量，半导体设备材料国产替代"),
    ("星环科技", -0.42, 1.46, "游资逆势抄底", "股价-15.1%但游资+1.46亿进场，短线博弈风险大（机构小额净卖）"),
]
THEME = [
    ("黄金概念", 19, False), ("金属铅", 10, False), ("金属锌", 9, False), ("金属铜", 8, False),
    ("云计算", 8, True), ("小金属", 6, False), ("国企改革", 5, False), ("存储芯片", 5, True),
    ("ST板块", 5, False), ("芯片概念", 4, True), ("钙钛矿电池", 4, False), ("IP经济", 4, False),
]
FOCUS = [
    ("网宿科技", "+20.34亿 · 新主线", "AI算力/CDN龙头。谷歌/亚马逊云涨价打破20年惯例→算力租赁逻辑爆发；小鳄鱼+3.37亿/量化+2.05亿/成都系合力，三天龙虎榜净买12亿+，资金押注产业逻辑新主线。", "游资 · 主线"),
    ("赤峰黄金", "-10.92亿 · 涨停派发", "金价新高涨停但机构-5.04亿大额出逃、北向同步卖出——利好兑现型派发，'边拉边出货'典型，高位补跌风险需警惕。", "机构 · 派发"),
    ("普冉股份", "机构+3.67亿 · 筹码换手", "存储芯片，机构2家买入0卖出+3.67亿 vs 游资-3.58亿——机构吸筹游资离场，国产替代主线筹码结构改善。", "机构 · 吸筹"),
    ("燕东微", "机构+3.12亿 · 机构主导", "第三代半导体/大基金持股，4家机构买入+3.12亿，+17.6%放量上攻——半导体设备材料国产替代趋势资金。", "机构 · 趋势"),
    ("白银有色", "-6.92亿 · 涨停净卖", "黄金+白银+铜冶炼，涨停但净卖-6.92亿，北向/游资派发——有色高位分歧信号，追高需谨慎。", "派发 · 风险"),
    ("宏景科技", "机构+2.99亿 · 算力租赁", "ChatGPT/财税数字化/云计算，三家机构买入1.45亿，机构逆势布局算力新方向。", "机构 · 算力"),
]
SCENARIO = [
    (25, "算力接力走强", "网宿+半导体承接黄金主线，AI算力产业逻辑延续，春季行情斜率放缓但结构性机会突出"),
    (55, "高位震荡轮动", "资源/科技/油气快速轮动，春节前避险情绪压制，指数高位横盘、板块切换加速"),
    (20, "高位补跌", "妖股涨停出货后集体补跌，量化一致性抛售，商业航天退潮拖累情绪"),
]
WARN = [
    "黄金股'边拉边出货'（赤峰机构-5.04亿/白银有色-6.92亿），高位妖股补跌风险需警惕",
    "北向净卖15.69亿+QFII净卖9.95亿，外资从资源高位撤离",
    "量化基金一致性抛售（中金黄金-5.17亿），高位股波动显著放大",
    "商业航天深度调整（套牢盘+监管高度压制），反弹阻力大",
    "春节临近避险资金出逃，高位个股注意减仓止盈",
    "指数涨但市场下跌3637家，结构分化极致，重个股轻指数",
]
SUMMARY = [
    ("整体", "01-28 龙虎榜 83 条/73 股，合计净买 -3.97 亿（净流出），涨停 41 vs 跌停 12——指数高位（上证 4151 +0.27%）但资金分歧加大，'边拉边出货'特征明显。"),
    ("黄金有色", "'金价新高'涨停潮（黄金概念 19 次居首、有色涨停 45 只）但集体派发：赤峰机构-5.04亿、中金黄金游资-5.17亿、北向净卖 15.69 亿——利好兑现型出货。"),
    ("AI算力", "网宿科技 +20.34 亿（游资+9.40亿），小鳄鱼 3.37 亿回归+量化/成都系合力，谷歌亚马逊云涨价催化——算力租赁成新主线。"),
    ("半导体", "存储/先进封装机构主导（普冉+3.67/燕东微+3.12亿），机构吸筹游资离场，国产替代逻辑持续。"),
    ("网宿科技", "三天龙虎榜净买 12 亿+，大游资+量化多路共振——资金从有色高位妖股切换到产业逻辑新主线的风向标。"),
]
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，special.dragon-tiger 普通榜+机构榜）；知名游资席位与后市复盘来自东方财富/中金在线/韭研公社等公开披露（2026-01-28）；"
        "change 为小数比例（0.10=+10%）；同股多次上榜已合并；机构净买=机构专用席位净额（org_net_value）。"
        "机构/游资/题材/推演为模型综合判断（模型输出），仅供研究参考，不构成个人投资建议。")

INSIGHT_NET = '💡 净买 TOP 呈现资金切换：AI 算力（网宿科技+20.34亿）暴力吸金，半导体存储（康强/燕东微/普冉）机构主导，而黄金有色虽涨停潮却集体净卖——一进一退，主线切换清晰。'
INSIGHT_ORG = '💡 机构内部撕裂：加仓贵金属+疫苗中军，兑现高位医药/半导体——中报窗口的攻守切换。'
INSIGHT_HM = '💡 小鳄鱼 3.37 亿回归网宿科技 + 量化 2.05 亿 + 成都系多线布局——大游资与量化合力押注 AI 算力新主线；黄金方向仅徐晓小仓位试探，游资整体回避高位有色。'
INSIGHT_THEME = '💡 医药（创新药/CRO/流感/医药电商）占据前五——仍是龙虎榜最大资金池但高位分歧；CPO/黄金/机器人三条线获资金共识，是当日实际强势方向。'
INSIGHT_SCENARIO = '💡 基准判断（55%）：缩量存量市场，资金在医药/通信/贵金属三线来回切换，无持续性强主线——轮动时代快进快出，分歧高位不赌修复。'
CHIP = [
    ('普冉股份', '机构2买0卖+3.67亿 vs 游资-3.58亿——机构吸筹游资离场，筹码结构改善'),
    ('网宿科技', '三天龙虎榜净买12亿+，深股通/机构/游资/量化多路参与——主线级别资金合力'),
    ('赤峰黄金', '机构-5.04亿+北向同步卖出、游资小仓承接——涨停板派发，筹码向高位散户转移'),
    ('指数背离', '上证+0.27%但全市场下跌3637家——权重护盘、个股普跌，结构分化极致'),
]

# ================= 渲染函数 =================
def pct_str(v, sign=True):
    return f"{v:+.1f}%" if sign else f"{v:.1f}%"

def net_rows():
    out = []
    for i, (name, code, net, hm, chg, con) in enumerate(NET_TOP, 1):
        c = "var(--red)" if chg >= 0 else "var(--green)"
        out.append(f'<tr><td class="num" style="color:var(--ink-3);width:30px">{i}</td>'
                   f'<td><b>{name}</b> <span class="code-mini">{code}</span></td>'
                   f'<td class="num" style="color:var(--red);font-weight:800">{net:+.2f}</td>'
                   f'<td class="num" style="color:{c}">{pct_str(chg)}</td>'
                   f'<td class="num" style="color:var(--ink-2)">{hm:+.2f}</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{con}</td></tr>')
    return "".join(out)

def org_buy_rows():
    out = []
    for name, code, net, b, s, desc in ORG_BUY:
        out.append(f'<tr><td><b>{name}</b></td>'
                   f'<td class="num" style="color:var(--red);font-weight:800">{net:+.2f}</td>'
                   f'<td class="num" style="color:var(--ink-2)">{b}买/{s}卖</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{desc}</td></tr>')
    return "".join(out)

def org_sell_rows():
    out = []
    for name, code, net, desc in ORG_SELL:
        out.append(f'<tr><td><b>{name}</b></td>'
                   f'<td class="num" style="color:var(--green);font-weight:800">{net:+.2f}</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{desc}</td></tr>')
    return "".join(out)

def hm_buy_rows():
    out = []
    for name, code, net, desc in HM_BUY:
        out.append(f'<tr><td><b>{name}</b></td>'
                   f'<td class="num" style="color:var(--red);font-weight:800">{net:+.2f}</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{desc}</td></tr>')
    return "".join(out)

def hm_sell_rows():
    out = []
    for name, code, net, desc in HM_SELL:
        out.append(f'<tr><td><b>{name}</b></td>'
                   f'<td class="num" style="color:var(--green);font-weight:800">{net:+.2f}</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{desc}</td></tr>')
    return "".join(out)

def seat_rows():
    out = []
    for name, stock, amt, note in SEATS:
        buy = "+" in amt
        out.append(f'<tr><td><b>{name}</b></td><td style="font-size:12.5px">{stock}</td>'
                   f'<td class="num" style="color:var(--{"red" if buy else "green"});font-weight:700">{amt}</td>'
                   f'<td style="color:var(--ink-2);font-size:12px">{note}</td></tr>')
    return "".join(out)

def diverge_cards():
    out = []
    for name, org, hm, tag, desc in DIVERGE:
        orgc = "var(--red)" if org > 0 else "var(--green)"
        hmc = "var(--red)" if hm > 0 else "var(--green)"
        out.append(f'''<div class="card">
          <h3>{name} <span class="unit">{tag}</span></h3>
          <div class="kv"><span class="k">机构净买</span><span class="v num" style="color:{orgc};font-weight:800">{org:+.2f}亿</span></div>
          <div class="kv"><span class="k">游资净买</span><span class="v num" style="color:{hmc};font-weight:800">{hm:+.2f}亿</span></div>
          <div class="dnote">{desc}</div>
        </div>''')
    return "".join(out)

def theme_list():
    maxv = THEME[0][1]
    rows = []
    for i, (name, cnt, strong) in enumerate(THEME[:10], 1):
        pct = cnt / maxv * 100
        bar = "linear-gradient(90deg,#e8b83a,#c9a227)" if strong else "linear-gradient(90deg,#2f56c9,#1f3a93)"
        tcolor = "var(--gold)" if strong else "var(--brand)"
        rows.append(f'''<div class="srow">
          <span class="srk2">{i}</span>
          <span class="srn2">{name}</span>
          <span class="srp2" style="color:{tcolor}">{cnt}<em>次</em></span>
          <span class="srbar"><i style="width:{pct:.0f}%;background:{bar}"></i></span>
        </div>''')
    return "".join(rows)

def focus_cards():
    out = []
    for name, tag, desc, who in FOCUS:
        who_cls = "who who-o" if "机构" in who else "who who-y"
        out.append(f'''<div class="card">
          <h3>{name} <span class="unit">{tag}</span></h3>
          <p class="fdesc">{desc}</p>
          <div class="ftag"><span class="{who_cls}">{who}</span></div>
        </div>''')
    return "".join(out)

def scenario_rows():
    out = []
    for prob, title, desc in SCENARIO:
        color = {"25": "var(--green)", "55": "var(--gold)", "20": "var(--red)"}.get(str(prob), "var(--ink-2)")
        out.append(f'''<div class="srow">
          <span class="srk2" style="width:30px;font-size:13.5px;color:{color};font-weight:800">{prob}%</span>
          <span class="srn2" style="flex:0 0 auto;font-weight:700;color:var(--ink)">{title}</span>
          <span class="srbar" style="flex:2;min-width:100px"><i style="width:100%;height:100%;background:{color};opacity:.18;border-radius:5px"></i></span>
        </div>
        <div style="font-size:12.5px;color:var(--ink-2);line-height:1.7;margin:2px 0 12px 30px;">{desc}</div>''')
    return "".join(out)

def warn_rows():
    out = []
    for i, w in enumerate(WARN, 1):
        out.append(f'<div class="sum-row"><span class="sum-tag2">警示{i}</span><span style="color:var(--ink-2)">{w}</span></div>')
    return "".join(out)

def summary_rows():
    out = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag in ("整体", "网宿科技") else "sum-tag2"
        out.append(f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>')
    return "".join(out)

def chip_rows():
    """筹码结构提示行（数据区 CHIP 驱动）。"""
    return "\n".join(f'    <div class="kv"><span class="k">{k}</span><span class="v" style="color:var(--ink-2);font-size:12.5px">{v}</span></div>' for k, v in CHIP)

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>龙虎榜事件解读_{DATE}</title>
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
  .goldbar { height:3px; background:linear-gradient(90deg,var(--gold),var(--brand),var(--gold)); border-radius:2px; margin-bottom:18px; }
  .code-mini { font-size:11px; color:var(--ink-3); font-weight:400; }
  .pill { display:inline-block; font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px; }
  .pill.brand { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
  .pill.gold { background:var(--gold-soft); color:#8a6d12; border:1px solid #eddcab; }
  .hero { background:linear-gradient(150deg,#ffffff 30%,#fbfcfe 100%); border:1px solid var(--border); border-radius:18px; box-shadow:var(--shadow-md); padding:24px 28px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px; position:relative; overflow:hidden; }
  .hero::before { content:""; position:absolute; right:-70px; top:-70px; width:240px; height:240px; border-radius:50%; background:radial-gradient(circle,rgba(201,162,39,.12),transparent 65%); }
  .hero::after { content:""; position:absolute; left:-50px; bottom:-90px; width:200px; height:200px; border-radius:50%; background:radial-gradient(circle,rgba(31,58,147,.06),transparent 70%); }
  .hero .big { position:relative; z-index:1; }
  .hero .title { font-size:24px; font-weight:800; letter-spacing:-.5px; }
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
  .grid-3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { text-align:left; font-size:11.5px; color:var(--ink-3); font-weight:600; padding:6px 8px; border-bottom:2px solid var(--border); }
  td { padding:8px; border-bottom:1px dashed #f0f1f4; vertical-align:middle; }
  tbody tr:nth-child(even) { background:#fafbfc; }
  tbody tr:hover { background:var(--brand-soft); }
  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink-2); }
  .dnote { font-size:12px; color:var(--ink-2); line-height:1.7; margin-top:8px; }
  .fdesc { font-size:12.5px; color:var(--ink-2); line-height:1.8; min-height:54px; }
  .ftag { margin-top:10px; }
  .who { display:inline-block; font-size:11px; font-weight:700; padding:2px 10px; border-radius:20px; }
  .who-o { background:var(--brand-soft); color:var(--brand); border:1px solid #d5def5; }
  .who-y { background:var(--gold-soft); color:#8a6d12; border:1px solid #eddcab; }
  .insight { margin-top:12px; padding:10px 14px; border-radius:10px; background:linear-gradient(120deg,#fdf9ec,#faf3d8); border:1px solid #eddcab; font-size:12.5px; font-weight:600; color:#8a6d12; line-height:1.7; }
  .sum-row { display:flex; align-items:baseline; gap:8px; padding:9px 0; border-bottom:1px dashed #f0f1f4; font-size:13px; flex-wrap:wrap; }
  .sum-row:last-child { border-bottom:none; }
  .sum-tag { flex-shrink:0; font-size:11px; font-weight:800; color:#fff; background:linear-gradient(180deg,var(--gold),#a8871d); border-radius:5px; padding:2px 9px; }
  .sum-tag2 { flex-shrink:0; font-size:11px; font-weight:800; color:var(--brand); background:var(--brand-soft); border:1px solid #d5def5; border-radius:5px; padding:2px 9px; }
  .lbar-legend { display:flex; gap:16px; font-size:11.5px; color:var(--ink-2); margin:0 0 10px; flex-wrap:wrap; }
  .lbar-legend .lg { display:inline-block; width:14px; height:5px; border-radius:3px; margin-right:5px; vertical-align:2px; }
  .sector-list { display:flex; flex-direction:column; gap:2px; }
  .srow { display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px dashed #f0f1f4; }
  .srow:last-child { border-bottom:none; }
  .srk2 { flex-shrink:0; width:20px; font-size:13px; color:var(--ink-2); text-align:center; }
  .srn2 { flex:1; font-size:13.5px; color:var(--ink-2); }
  .srp2 { flex-shrink:0; font-size:13.5px; font-weight:650; width:56px; text-align:right; }
  .srp2 em { font-style:normal; font-size:11px; color:var(--ink-3); font-weight:400; margin-left:2px; }
  .srbar { flex:1.2; min-width:80px; height:5px; border-radius:3px; background:#eef0f3; overflow:hidden; }
  .srbar i { display:block; height:100%; border-radius:3px; }
  .note { font-size:11px; color:var(--ink-3); margin-top:16px; line-height:1.8; border-top:1px dashed var(--border); padding-top:12px; }
  @media print { body{background:#fff} .card{box-shadow:none} .goldbar{display:none} }
  @media (max-width:760px) { .hero{flex-direction:column;align-items:flex-start} .hero .kpis{width:100%;justify-content:space-between} }
</style>
</head>
<body>
<div class="wrap">
  <div class="goldbar"></div>
  <!-- Hero -->
  <div class="hero">
    <div class="big">
      <div class="title">龙虎榜事件解读</div>
      <div class="sub">
        <span class="pill gold">__WEEKDAY__ · __DATE__</span>
        <span class="pill brand">上榜 __COUNT__ 条 / __STOCK_CNT__ 股</span>
        <span class="pill brand">机构榜 __ORG_CNT__ 条 / __ORG_STOCK__ 股</span>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num __NET_CLS__">__NET_TOTAL__亿</div><div class="k">合计净买入</div></div>
      <div class="kpi"><div class="v num up">__LIMIT_UP__</div><div class="k">涨停家数</div></div>
      <div class="kpi"><div class="v num dn">__LIMIT_DOWN__</div><div class="k">跌停家数</div></div>
      <div class="kpi"><div class="v num gd">__UP_CNT__/__DOWN_CNT__</div><div class="k">上涨/下跌</div></div>
    </div>
  </div>

  <!-- 01 综述 -->
  <div class="sec"><h2><span class="no">01</span>龙虎榜综述</h2><span class="hint">资金生态 · 四大阵营</span></div>
  <div class="card">__SUMMARY_ROWS__</div>

  <!-- 02 资金净买榜 -->
  <div class="sec"><h2><span class="no">02</span>资金净买榜</h2><span class="hint">全资金口径 · 单位：亿元</span></div>
  <div class="card">
    <table>
      <tr><th>#</th><th>股票</th><th>净买入</th><th>涨跌幅</th><th>游资净买</th><th>题材</th></tr>
      __NET_ROWS__
    </table>
    <div class="insight">__INSIGHT_NET__</div>
  </div>

  <!-- 03 机构动向 -->
  <div class="sec"><h2><span class="no">03</span>机构动向</h2><span class="hint">机构专用席位 · 单位：亿元 · 研究型资金</span></div>
  <div class="grid-2">
    <div class="card"><h3>机构净买入 TOP6 <span class="unit">买X家/卖X家</span></h3>
      <table><tr><th>股票</th><th>净买</th><th>席位</th><th>解读</th></tr>__ORG_BUY_ROWS__</table>
    </div>
    <div class="card"><h3>机构净卖出 TOP3 <span class="unit">兑现方向</span></h3>
      <table><tr><th>股票</th><th>净买</th><th>解读</th></tr>__ORG_SELL_ROWS__</table>
      <div class="insight">__INSIGHT_ORG__</div>
    </div>
  </div>

  <!-- 04 游资动向 -->
  <div class="sec"><h2><span class="no">04</span>游资动向</h2><span class="hint">热钱净买 + 知名席位 · 单位：亿元</span></div>
  <div class="grid-2">
    <div class="card"><h3>游资净买入 TOP6</h3>
      <table><tr><th>股票</th><th>净买</th><th>解读</th></tr>__HM_BUY_ROWS__</table>
    </div>
    <div class="card"><h3>游资净卖出 TOP5</h3>
      <table><tr><th>股票</th><th>净买</th><th>解读</th></tr>__HM_SELL_ROWS__</table>
    </div>
  </div>
  <div class="card" style="margin-top:14px"><h3>知名游资席位 <span class="unit">WebSearch 公开披露 · __DATE__</span></h3>
    <table><tr><th>席位</th><th>个股</th><th>金额</th><th>风格/逻辑</th></tr>__SEAT_ROWS__</table>
    <div class="insight">__INSIGHT_HM__</div>
  </div>

  <!-- 05 分歧与筹码交换 -->
  <div class="sec"><h2><span class="no">05</span>分歧与筹码交换</h2><span class="hint">机构 vs 游资对手盘</span></div>
  <div class="grid-3">__DIVERGE_CARDS__</div>
  <div class="card" style="margin-top:14px"><h3>筹码结构提示 <span class="unit">隐藏盘口信号</span></h3>
__CHIP_ROWS__
  </div>

  <!-- 06 题材热度 -->
  <div class="sec"><h2><span class="no">06</span>题材热度</h2><span class="hint">概念上榜次数 TOP10</span></div>
  <div class="card">
    <div class="lbar-legend">
      <span><i class="lg" style="background:linear-gradient(90deg,#e8b83a,#c9a227)"></i>资金共识主线（多股上榜+持续流入）</span>
      <span><i class="lg" style="background:linear-gradient(90deg,#2f56c9,#1f3a93)"></i>热度一般</span>
    </div>
    <div class="sector-list">__THEME_LIST__</div>
    <div class="insight">__INSIGHT_THEME__</div>
  </div>

  <!-- 07 重点个股解读 -->
  <div class="sec"><h2><span class="no">07</span>重点个股解读</h2><span class="hint">资金行为 + 事件驱动</span></div>
  <div class="grid-3">__FOCUS_CARDS__</div>

  <!-- 08 后市推演 -->
  <div class="sec"><h2><span class="no">08</span>后市推演</h2><span class="hint">情景概率 · 模型输出</span></div>
  <div class="card">
    __SCENARIO_ROWS__
    <div class="insight">__INSIGHT_SCENARIO__</div>
  </div>
  <div class="card" style="margin-top:14px"><h3>操作警示 <span class="unit">风险清单</span></h3>__WARN_ROWS__</div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
html = (TPL
        .replace("__DATE__", DATE).replace("__WEEKDAY__", WEEKDAY)
        .replace("__COUNT__", str(OVERVIEW["count"])).replace("__STOCK_CNT__", str(OVERVIEW["stock_cnt"]))
        .replace("__ORG_CNT__", str(OVERVIEW["org_cnt"])).replace("__ORG_STOCK__", str(OVERVIEW["org_stock"]))
        .replace("__NET_TOTAL__", f"{OVERVIEW['net_total']:+.2f}")
        .replace("__NET_CLS__", "up" if OVERVIEW["net_total"] >= 0 else "dn")
        .replace("__LIMIT_UP__", str(OVERVIEW["limit_up"])).replace("__LIMIT_DOWN__", str(OVERVIEW["limit_down"]))
        .replace("__UP_CNT__", str(OVERVIEW["up_cnt"])).replace("__DOWN_CNT__", str(OVERVIEW["down_cnt"]))
        .replace("__SUMMARY_ROWS__", summary_rows())
        .replace("__NET_ROWS__", net_rows())
        .replace("__ORG_BUY_ROWS__", org_buy_rows())
        .replace("__ORG_SELL_ROWS__", org_sell_rows())
        .replace("__HM_BUY_ROWS__", hm_buy_rows())
        .replace("__HM_SELL_ROWS__", hm_sell_rows())
        .replace("__SEAT_ROWS__", seat_rows())
        .replace("__DIVERGE_CARDS__", diverge_cards())
        .replace("__THEME_LIST__", theme_list())
        .replace("__FOCUS_CARDS__", focus_cards())
        .replace("__SCENARIO_ROWS__", scenario_rows())
        .replace("__WARN_ROWS__", warn_rows())
        .replace("__INSIGHT_NET__", INSIGHT_NET)
        .replace("__INSIGHT_ORG__", INSIGHT_ORG)
        .replace("__INSIGHT_HM__", INSIGHT_HM)
        .replace("__CHIP_ROWS__", chip_rows())
        .replace("__INSIGHT_THEME__", INSIGHT_THEME)
        .replace("__INSIGHT_SCENARIO__", INSIGHT_SCENARIO)
        .replace("__NOTE__", NOTE))

out_path = os.path.join(BASE, f"龙虎榜事件解读_{DATE.replace('-', '')}.html")
html = html.replace("{DATE}", DATE.replace("-", ""))
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {out_path} | size: {len(html.encode('utf-8'))} bytes")
