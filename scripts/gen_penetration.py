# -*- coding: utf-8 -*-
"""A股基金持仓穿透分析 HTML 生成器 v2.0（模板，全面参数化）
【模板使用说明】回答"这基金重仓什么？这股票被谁抱团？"——正向（ETF→重仓股）+反向（个股→持有基金）穿透闭环：
①hithink CLI：`fund holdings --fund-type exchange --thscode <etf>` 取前十大持仓（hold_ratio 占净值%/position_capital 市值/period_increase_rate_pct 期间增减）
+ `fund holders` 取持有人结构（ins_position 机构占比/psnl_rate 个人占比/holder_amount 户数）
+ `fund profile` 取规模/经理 + `fund snapshot` 取行情
②反向：hithink 无"个股被哪些基金持有"接口 → WebSearch 新浪财经基金持股页/巨丰财经/东吴证券等公开披露（持仓基金数/占总市值比例/前十大持有基金）
③闭环验证：正向 ETF 前十大里的重仓股，应能在反向持有基金表中找到该 ETF 本身（561380 持亨通 7.82亿 ↔ 亨通持有基金表第 6 位=国泰恒生A股电网设备ETF）——闭环成立证据，换标的必须重新验证
④替换 BASE/DATE 与数据区（CFG[kpis]/ETF/ETF_HOLD/STOCK_CORE/STOCK_FUNDS/HERD[META/MAX2]/CONC_NOTES/FWD_NOTE/REV_NOTE/HERD_HINT/HERD_VIEW/HERD_INSIGHT/CLOSE_ROWS/CLOSE_INSIGHT/RISK_ROWS/SUMMARY/NOTE）
⑤运行 → `穿透分析_{CFG[out_tag]}_{YYYYMMDD}.html`
v2.0 经验（换标的必读）：
· 模板已全参数化（KPI/基金档案/持有人/所有 insight/解读/风险行都在数据区）——**禁止在 TPL 写死当日叙事**（估值模板 6 处硬编码教训）
· **占位符唯一性**：同一占位符只能出现一次；title 用 __DATE_SHOW__（曾用 {DATE} 显示字面量）
· **闭环 ETF 判断动态化**：stock_fund_rows 用 CFG["etf_code"] 取 6 位码（曾硬编码 512480）
· **抱团图双列布局**：右列起始 x2=pad_l+212 与图例对齐；col1_w=x2-pad_l-96（左列值文本不越界）；col2_w=W-x2-70（右列条按可用宽度，曾公式负值→全 4px 条+重叠）
· **结论加"数据含义"+"投资指导"行**（01 综述精炼版 + 05 详解版 + CLOSE_INSIGHT 金色 insight）——用户要求穿透报告必须有实战指导
· 个股抱团版（无 ETF 正向区）用独立模板 gen_penetration_zjky.py（机构分层/前十大流通股东）
数据坑：industry-allocation 接口可能报 FUYAO_5003（status 9999，retryable）→ 行业分布用持仓股主营归类或标 [MISSING]；
持仓与持有人报告期不同（持仓=季报 2026Q2，持有人=年报 2025-12-31）需分别标注；
反向数据为 WebSearch 公开披露，口径有差异（渤海=主动权益基金数、巨丰=全口径、东吴=占总市值比例）→ 页脚显式标注来源与口径；
占流通股比例/占净值比 hold_ratio 均为百分数（17.79 直接加%）；基金档案硬编码行必须由 archive_rows 生成
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-08-21"
WEEKDAY = "周五"

# ================= 数据 =================
CFG = {
    "out_tag": "电网设备ETF",
    "etf_name": "电网设备ETF国泰", "etf_code": "561380.SH",
    "stock_name": "亨通光电", "stock_code": "600487.SH",
    "kpis": [("65.31%", "ETF前十大持仓合计", "gd"), ("282 亿", "亨通公募持仓市值", ""),
             ("10.46%", "基金持仓占总市值", "up"), ("80.94%", "ETF机构持有人占比", "")],
    "verdict": "机构定制 · 高集中抱团", "verdict_short": "穿透",
    "verdict_note": ("正向看：561380 前十大持仓合计 65.31%（比半导体ETF 47.44% 更集中），中天科技/亨通光电/特变电工/思源电气/国电南瑞——电网设备全链条；"
                     "反向看：第二大重仓股亨通光电 2026Q2 公募持仓 282 亿（占总市值 10.46%），561380 本身即其第 6 大基金股东——穿透闭环成立。"),
}

# ===== 正向：ETF 行情/资料/持有人 =====
ETF = {
    "px": 0.750, "chg_pct": 1.63, "turnover": 0.60, "turnover_ratio": 1.17,
    "scale": 51.04, "unit_nav": 0.748, "mgmt": "国泰基金", "track": "恒生A股电网设备主题指数",
    "mgr1": ("吴中昊", 87.0), "mgr2": None,
    "fee": "0.50% + 0.10%",
    "ins_rate": 80.94, "psnl_rate": 19.06, "holder_cnt": 0.45, "holder_date": "2025-12-31",
}

# 前十大持仓（占净值%, 市值亿, 期间增减pct, 子板块归类）
ETF_HOLD = [
    ("中天科技", "600522", 13.98, 8.4, 5.74, "海缆+光通信"),
    ("亨通光电", "600487", 12.98, 7.8, 3.20, "海缆+光纤"),
    ("特变电工", "600089", 8.50, 5.1, -0.93, "输变电"),
    ("思源电气", "002028", 8.28, 5.0, -1.46, "开关+GIS"),
    ("国电南瑞", "600406", 7.45, 4.5, -2.03, "电网自动化"),
    ("宏发股份", "600885", 3.60, 2.2, 0.35, "继电器"),
    ("中国西电", "601179", 3.10, 1.9, -0.44, "输变电"),
    ("四方股份", "601126", 2.85, 1.7, 0.68, "电力自动化"),
    ("特锐德", "300001", 2.52, 1.5, None, "充电桩+箱变"),
    ("旭光电子", "600353", 2.05, 1.2, None, "真空开关"),
]

# ===== 反向：亨通光电被谁抱团 =====
STOCK_CORE = {
    "px": 62.18, "px_date": "2026-08-21",
    "fund_cnt": None, "float_pct": 10.46, "add_wan": None, "add_pct": -5.52,
    "note": ("2026Q2 公募持仓亨通光电 282.01 亿元、占总市值 10.46%（环比 -5.52pct）——基金二季度整体减仓兑现；"
             "前十大流通股东合计 36.37%（亨通集团 24.07%），公募+北向+信托多层持股，AI 算力光纤+海缆双主线核心标的。"),
}
# 前十大持有基金（名称, 代码, 类型, 持股市值亿, 占流通%, 占净值%）
STOCK_FUNDS = [
    ("国泰中证全指通信设备ETF", "515880", "被动ETF", 40.64, 1.52, 6.89),
    ("华夏中证电网设备主题ETF", "159326", "被动ETF", 36.44, 1.36, 15.01),
    ("华泰柏瑞质量成长A", "008528", "主动混合", 21.44, 0.80, 7.47),
    ("富国创新科技A", "002692", "主动混合", 17.49, 0.65, 6.28),
    ("广发远见智选A", "016873", "主动混合", 13.92, 0.52, 9.26),
    ("华夏中证5G通信ETF", "515050", "被动ETF", 9.83, 0.37, 3.93),
    ("天弘中证电网设备指数A", "025832", "被动指数", 9.45, 0.35, 14.54),
    ("国泰恒生A股电网设备ETF", "561380", "被动ETF", 7.82, 0.29, 12.98),
    ("宏利复兴伟业A", "001170", "主动混合", 5.56, 0.21, 4.63),
    ("富国互联科技A", "006751", "主动混合", 5.11, 0.19, 5.96),
]

# ===== 抱团全景：电网设备重仓股公募持仓（2026Q2，市值亿, 占总市值%）=====
HERD_META = ("公募持仓市值（亿）", "#2f56c9", "占总市值%", "#e5484d")
HERD_MAX2 = 15.0
HERD = [
    ("亨通光电", 282.01, 10.46), ("中天科技", 142.19, 6.87), ("思源电气", 75.83, 5.60),
    ("宏发股份", 45.87, 8.59), ("特变电工", None, None), ("国电南瑞", None, None),
    ("中国西电", None, None), ("四方股份", None, None), ("特锐德", None, None), ("旭光电子", None, None),
]

SUMMARY = [
    ("结论", "穿透闭环成立：561380 重仓什么（中天13.98%/亨通12.98%/特变8.5%/思源8.28%/南瑞7.45%…合计 65.31% 全电网设备）→ 反向重仓股被谁抱团（亨通 2026Q2 公募持仓 282 亿/占总市值 10.46%）——机构定制型电网设备指数基金。"),
    ("正向", "561380 前十大 65.31% 高集中：海缆（中天/亨通）+输变电（特变/西电）+电网自动化（南瑞/四方）+开关（思源/旭光）——全链条配置，双龙头中天/亨通合计 26.96% 接近三成。"),
    ("反向", "亨通光电被公募+北向+信托多层抱团：2026Q2 公募持仓 282 亿（占总市值 10.46%）、前十大流通股东 36.37%；但 Q2 基金环比 -5.52pct 减仓——AI 算力光纤主线的获利兑现。"),
    ("机构结构", "561380 持有人：机构 80.94% / 个人 19.06%（仅 4478 户）——典型机构定制/配置型 ETF，机构占比极高，申赎行为决定场内流动性。"),
    ("增减持", "ETF 内 Q2 加仓中天(+5.74)/亨通(+3.2)/四方(+0.68)、减仓国电南瑞(-2.03)/思源(-1.46)/特变(-0.93)——海缆双龙头获增配，电网自动化兑现。"),
    ("数据含义", "被动资金（ETF 配置盘）加仓海缆 vs 主动公募整体减仓=机构对电网设备的分歧：趋势资金兑现利润、配置盘承接底仓——海缆（亨通/中天）是两类资金唯一的共识交集。"),
    ("投资指导", "抱团结构提示：电网设备短期看被动资金承接力度（跟踪 561380 份额/申赎），中期看海缆订单兑现节奏——回调获 ETF 承接时配置性价比优于追高，主动减仓不等于趋势反转。"),
]

CONC_NOTES = ("满格基准 50%（前十大常见上限）· 行业分布：海缆2 + 输变电2 + 电网自动化2 + 开关2 + 继电器/充电桩",
             "数据口径：2026Q2 季报 · 全部为电网设备板块（行业配置接口 [MISSING]）")
FWD_NOTE = "💡 前十大合计 65.31%：海缆双龙头（中天13.98%/亨通12.98%）占 26.96% 近三成，+输变电（特变/西电）+电网自动化（南瑞/四方）+开关（思源/旭光）全链条——机构定制型高集中配置。"
CORE_BADGE = "公募持仓 282 亿 · 占总市值 10.46%"
REV_NOTE = "💡 前 3 大持有者均为被动指数基金（通信设备ETF/电网设备ETF/质量成长），主动基金（富国/广发）居后——亨通光电是「指数底仓 + 主动共识」的双层抱团；第 8 位国泰恒生A股电网设备ETF 正是本报告正向标的，穿透闭环成立。"
HERD_HINT = "561380 重仓股的公募持仓 · 2026Q2 · 东吴证券口径"
HERD_VIEW = [
    ("持仓市值TOP", "亨通 282 亿 > 中天 142 亿 > 思源 76 亿 > 宏发 46 亿——海缆双龙头占公募电网配置大头"),
    ("抱团度最高", "亨通占总市值 10.46% · 宏发 8.59% · 中天 6.87%——均高于半导体头部",
     "num"),
    ("Q2 减仓方向", "亨通 -5.52pct / 中天 -5.57pct / 思源 -6.63pct——电网设备 Q2 遭公募整体兑现"),
    ("结构性差异", "半导体 Q2 获增持（寒武纪+358只）vs 电网设备被减仓——公募 AI 算力方向内部切换"),
    ("未披露", "特变/南瑞/西电/四方/特锐德/旭光公募持仓口径 [MISSING]", ""),
]
HERD_INSIGHT = "💡 电网设备 Q2 公募整体减仓（亨通/中天/思源环比均降 5.5pct+），但 ETF 内海缆双龙头反获加仓——被动资金与主动资金方向背离，主动资金兑现、配置盘承接。"
CLOSE_ROWS = [
    ("正向", "561380 买什么 → 中天/亨通/特变/思源/南瑞（全电网设备，65.31%）"),
    ("反向", "这些股被谁抱团 → 亨通公募 282 亿 / 占总市值 10.46%"),
    ("闭环", "561380 本身即亨通光电第 6 大基金股东（7.82 亿，占净值 12.98%）——穿透成立，ETF 是被动抱团放大器"),
    ("资金属性", "机构 80.94% 持有人 + 被动指数化 → 机构定制型 ETF，申赎行为主导流动性"),
    ("数据含义", "被动资金（ETF 配置盘）加仓海缆 vs 主动公募减仓=预期分歧：机构把电网设备从「趋势进攻」降为「配置底仓」，海缆（亨通/中天）是保留的核心方向"),
    ("投资指导", "跟踪 561380 份额与申赎（配置盘风向）+ 亨通/中天海缆订单落地节奏；主动减仓后的回调若获 ETF 承接，是配置机会而非趋势反转"),
]
CLOSE_INSIGHT = "💡 抱团结构揭示的实战意义：被动资金是电网设备的「底部承接力量」，主动公募决定「趋势斜率」——当两者背离时，跟随配置盘（份额/申购）比跟随主动仓位更稳；海缆双龙头是两大资金唯一的共识交集，是板块内最强的确定性方向。"
RISK_ROWS = [
    "⚠️ 抱团拥挤 + 减仓背离：电网设备 Q2 遭公募整体兑现（亨通/中天/思源环比均降 5.5pct+），ETF 加仓与主动减仓背离，若海缆订单不及预期双重抛压",
    "⚠️ 高估值：亨通 PE_TTM 47.5 / 思源 41.6 / 中天 30+——AI 算力预期已部分定价，业绩兑现节奏决定估值消化",
    "⚠️ 报告期滞后：持仓为 2026Q2（6-30 数据），已滞后近 2 个月，期间机构可能已调仓",
    "⚠️ 机构定制结构：561380 机构持有人 80.94%、仅 4478 户——机构申赎行为直接决定场内流动性与折溢价",
    "⚠️ 反向数据为公开披露口径（新浪/东吴），基金持仓占总市值比例随披露时点与统计范围变动",
]
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，fund holdings/holders/profile/snapshot）+ 公开披露交叉验证；"
        "反向穿透（亨通光电持仓基金数/占总市值比例/前十大持有基金）来自新浪财经基金持股页、中财网与东吴证券 2026Q2 电力设备行业研报（口径：基金持仓占总市值比例）；"
        "抱团全景为东吴证券 2026Q2 基金持仓市值口径，前十大外未披露标 [MISSING]；ETF 持有人结构报告期为 2025-12-31（年报）、持仓为 2026Q2（季报）——报告期不同已分别标注。"
        "穿透分析为模型综合判断（模型输出），仅供研究参考，不构成个人投资建议。")

# ---- 文本/口径占位（平台可覆写；默认值 = 本报告原值，保证 skill 单独运行字节一致）----
REPORT_PERIOD = "2026Q2"                    # 持仓报告期标签
REV_PERIOD = "2026Q2"                       # 反向（个股持有基金）报告期
REV_SOURCE = "WebSearch 公开披露"            # 反向数据来源/口径
HERD_SCOPE = "公募前50大重仓股口径"           # 抱团全景口径说明

# ================= 渲染函数 =================
def hold_rows():
    rows = []
    for i, (name, code, ratio, cap, chg, sub) in enumerate(ETF_HOLD, 1):
        chg_c = "var(--red)" if chg is not None and chg >= 0 else ("var(--green)" if chg is not None else "var(--ink-3)")
        chg_t = f"{chg:+.2f}" if chg is not None else "[MISSING]"
        rows.append(f'<tr><td class="num" style="color:var(--ink-3);width:26px">{i}</td>'
                    f'<td><b>{name}</b> <span style="font-size:11px;color:var(--ink-3)">{code}</span></td>'
                    f'<td style="font-size:12px;color:var(--ink-2)">{sub}</td>'
                    f'<td class="num" style="font-weight:800;color:var(--brand)">{ratio:.2f}%</td>'
                    f'<td class="num" style="color:var(--ink-2)">{cap:.1f}亿</td>'
                    f'<td class="num" style="color:{chg_c}">{chg_t}</td></tr>')
    return "".join(rows)

def conc_svg():
    """前十大合计占比集中度横条（47.44% / 满格 100%）"""
    total = sum(r for _, _, r, _, _, _ in ETF_HOLD)
    W, H = 460, 120
    pad = 24
    xw = W - 2 * pad
    pct = total / 50.0 * 100  # 满格按 50%（前十常见上限）
    w = max(pct / 100 * xw, 4)
    parts = [
        f'<text x="{pad}" y="26" font-size="12.5" font-weight="700" fill="#1f3a93">前十大持仓合计占净值</text>',
        f'<text x="{W-pad}" y="26" text-anchor="end" font-size="15" font-weight="800" fill="#c9a227">{total:.2f}%</text>',
        f'<rect x="{pad}" y="40" width="{xw:.0f}" height="14" rx="7" fill="#eef0f3"/>',
        f'<rect x="{pad}" y="40" width="{w:.0f}" height="14" rx="7" fill="url(#gGold)" opacity="0.9"/>',
        f'<text x="{pad}" y="78" font-size="11.5" fill="#5b6470">{CONC_NOTES[0]}</text>',
        f'<text x="{pad}" y="98" font-size="11.5" fill="#5b6470">{CONC_NOTES[1]}</text>',
    ]
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="前十大持仓集中度"><defs><linearGradient id="gGold" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#e8b83a"/><stop offset="100%" stop-color="#c9a227"/></linearGradient></defs>{"".join(parts)}</svg>'

def _num_cell(value, suffix="", nd=2):
    """数值单元格：缺失（None）→ `[MISSING]`，否则按 skill 原格式渲染。"""
    if value is None:
        return "[MISSING]"
    return f"{value:.{nd}f}{suffix}"

def stock_fund_rows():
    rows = []
    for i, (name, code, ftype, cap, fpct, npct) in enumerate(STOCK_FUNDS, 1):
        close = CFG["etf_code"].split(".")[0]
        hl = ' style="background:#fdf9ec"' if code == close else ""
        tag = " · 闭环ETF" if code == close else ""
        rows.append(f'<tr{hl}><td class="num" style="color:var(--ink-3);width:26px">{i}</td>'
                    f'<td><b>{name}</b>{tag} <span style="font-size:11px;color:var(--ink-3)">{code}</span></td>'
                    f'<td style="font-size:12px;color:var(--ink-2)">{ftype}</td>'
                    f'<td class="num" style="font-weight:700">{_num_cell(cap, "亿")}</td>'
                    f'<td class="num" style="color:var(--red)">{_num_cell(fpct, "%")}</td>'
                    f'<td class="num" style="color:var(--ink-2)">{_num_cell(npct, "%")}</td></tr>')
    return "".join(rows)

def herd_svg():
    """抱团全景：双条形图（左列：基金数/市值，右列：占流通/占总市值%）
    布局要点：右列起始 x2 固定，左列条宽受限于 x2（值文本不越界），右列条宽按可用宽度计算"""
    W, H = 460, 330
    pad_l, pad_t, row_h, gap = 74, 22, 34, 5
    rows = [h for h in HERD if h[1] is not None]
    maxn = max(r[1] for r in rows)
    x2 = pad_l + 212          # 右列（百分比）起始 x，与图例文字对齐
    col1_w = x2 - pad_l - 96  # 左列条可用宽度（留值文本空间，不越过 x2）
    col2_w = W - x2 - 70      # 右列条可用宽度（留 % 文本空间）
    parts = []
    l1, c1, l2, c2 = HERD_META
    parts.append(f'<text x="{pad_l}" y="14" font-size="11" font-weight="700" fill="{c1}">{l1}</text>')
    parts.append(f'<text x="{x2}" y="14" font-size="11" font-weight="700" fill="{c2}">{l2}</text>')
    for i, (name, cnt, fpct) in enumerate(rows):
        y = pad_t + i * (row_h + gap)
        nw = max(cnt / maxn * col1_w, 4)
        parts.append(f'<text x="{pad_l-8}" y="{y+row_h/2+4:.1f}" text-anchor="end" font-size="12" fill="#5b6470">{name}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+5:.1f}" width="{nw:.1f}" height="12" rx="4" fill="{c1}" opacity="0.82"/>')
        parts.append(f'<text x="{pad_l+nw+5:.1f}" y="{y+row_h/2+4:.1f}" font-size="11" font-weight="700" fill="#1f3a93">{cnt}</text>')
        w2 = max(fpct / HERD_MAX2 * col2_w, 4)
        parts.append(f'<rect x="{x2}" y="{y+5:.1f}" width="{w2:.1f}" height="12" rx="4" fill="{c2}" opacity="0.8"/>')
        parts.append(f'<text x="{x2+w2+5:.1f}" y="{y+row_h/2+4:.1f}" font-size="11" font-weight="700" fill="#c0392b">{fpct:.1f}%</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="公募抱团度对比">{"".join(parts)}</svg>'

def kpi_rows():
    out = []
    for v, k, cls in CFG["kpis"]:
        c = f" {cls}" if cls else ""
        out.append(f'<div class="kpi"><div class="v num{c}">{v}</div><div class="k">{k}</div></div>')
    return "".join(out)

def archive_rows():
    m1 = f"{ETF['mgr1'][0]} +{ETF['mgr1'][1]:.1f}%" if ETF["mgr1"] else "[MISSING]"
    m2 = f" / {ETF['mgr2'][0]} +{ETF['mgr2'][1]:.1f}%" if ETF["mgr2"] else ""
    pxc = "var(--red)" if ETF["chg_pct"] >= 0 else "var(--green)"
    sign = "+" if ETF["chg_pct"] >= 0 else ""
    rows = [
        ("规模", f'{ETF["scale"]:.2f} 亿', "num"),
        ("跟踪指数", ETF["track"], ""),
        ("基金经理", m1 + m2, ""),
        ("费率", ETF["fee"], ""),
        ("最新价", f'{ETF["px"]:.3f} 元 <span style="color:{pxc}">{sign}{ETF["chg_pct"]:.2f}%</span>', "num"),
    ]
    out = []
    for i, (k, v, cls) in enumerate(rows):
        bd = "border-bottom:1px dashed #f0f1f4;" if i < len(rows) - 1 else ""
        out.append(f'<div class="kv" style="display:flex;justify-content:space-between;padding:5px 0;{bd}font-size:13px">'
                   f'<span style="color:var(--ink-2)">{k}</span><b class="{cls}">{v}</b></div>')
    return "".join(out)

def holder_bar():
    ins, psnl = ETF["ins_rate"], ETF["psnl_rate"]
    hc = ETF["holder_cnt"]
    hc_txt = f"{hc:.0f} 万" if hc >= 1 else f"{hc:.2f} 万"
    return (f'<h3 style="font-size:14px;margin-bottom:8px">持有人结构 <span style="font-size:11px;color:var(--ink-3)">报告期 {ETF["holder_date"]}</span></h3>'
            f'<div style="display:flex;align-items:center;gap:14px">'
            f'<div style="flex:1">'
            f'<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px"><span style="color:var(--ink-2)">机构 {ins:.2f}%</span><span style="color:var(--ink-2)">个人 {psnl:.2f}%</span></div>'
            f'<div style="height:12px;border-radius:6px;background:#eef0f3;overflow:hidden;display:flex">'
            f'<div style="width:{ins:.2f}%;background:linear-gradient(90deg,#2f56c9,#1f3a93)"></div>'
            f'<div style="width:{psnl:.2f}%;background:linear-gradient(90deg,#e8b83a,#c9a227)"></div>'
            f'</div></div>'
            f'<div style="text-align:center"><b class="num" style="font-size:18px;color:var(--brand)">{hc_txt}</b><div style="font-size:10.5px;color:var(--ink-3)">持有人户数</div></div>'
            f'</div>')

def herd_view_rows():
    out = []
    for it in HERD_VIEW:
        k, v = it[0], it[1]
        cls = ' class="num"' if len(it) > 2 and it[2] == "num" else ""
        out.append(f'<div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">{k}</span><b{cls}>{v}</b></div>')
    return "".join(out) + f'<div class="insight">{HERD_INSIGHT}</div>'

def close_rows():
    out = []
    n = len(CLOSE_ROWS)
    for i, (k, v) in enumerate(CLOSE_ROWS):
        bd = "border-bottom:1px dashed #f0f1f4;" if i < n - 1 else ""
        out.append(f'<div class="kv" style="padding:6px 0;{bd}font-size:13px"><span style="color:var(--ink-2)">{k}</span><b>{v}</b></div>')
    return "".join(out) + f'<div class="insight">{CLOSE_INSIGHT}</div>'

def risk_rows():
    out = []
    n = len(RISK_ROWS)
    for i, r in enumerate(RISK_ROWS):
        bd = "border-bottom:1px dashed #f0f1f4;" if i < n - 1 else ""
        out.append(f'<div class="kv" style="padding:6px 0;{bd}font-size:12.5px;color:var(--ink-2)">{r}</div>')
    return "".join(out)

def summary_rows():
    out = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag in ("结论",) else "sum-tag2"
        out.append(f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>')
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
  .hl{background:#fdf9ec}
  @media print{body{background:#fff}.card{box-shadow:none;border-color:#ddd}}
</style>
</head>
<body>
<div class="wrap">

  <!-- Hero -->
  <div class="hero">
    <div class="title">穿透分析 <span class="tcode">基金持仓 ↔ 个股抱团</span></div>
    <div class="sub">
      <span class="pill gold">__WEEKDAY__ · __DATE__</span>
      <span class="pill brand">正向 · __ETF_NAME__</span>
      <span class="pill brand">反向 · __STOCK_NAME__</span>
    </div>
    <div class="kpis">__KPI_ROWS__</div>
  </div>

  <!-- 01 穿透总览 -->
  <div class="sec"><h2><span class="no">01</span>穿透总览</h2><span class="hint">正向 × 反向 · 模型输出</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      <span class="vbadge">__VERDICT__</span>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
  </div>

  <!-- 02 正向穿透 -->
  <div class="sec"><h2><span class="no">02</span>正向穿透 · ETF 重仓什么</h2><span class="hint">__ETF_NAME__ 前十大持仓 · __REPORT_PERIOD__ 季报</span></div>
  <div class="grid-2">
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:10px">前十大持仓 <span style="font-size:11px;color:var(--ink-3)">占净值 / 市值 / 期间增减</span></h3>
      <table>
        <tr><th>#</th><th>股票</th><th>子板块</th><th>占净值</th><th>市值</th><th>增减</th></tr>
        __HOLD_ROWS__
      </table>
      <div class="insight">__FWD_NOTE__</div>
    </div>
    <div class="card" style="display:flex;flex-direction:column;gap:12px">
      <div>
        <h3 style="font-size:14px;margin-bottom:8px">基金档案 <span style="font-size:11px;color:var(--ink-3)">hithink fund.profile</span></h3>
        __ARCHIVE_ROWS__
      </div>
      <div>
        __HOLDER_BAR__
      </div>
      __CONC_SVG__
    </div>
  </div>

  <!-- 03 反向穿透 -->
  <div class="sec"><h2><span class="no">03</span>反向穿透 · 股票被谁抱团</h2><span class="hint">__STOCK_NAME__ 基金持仓 · __REV_PERIOD__ · __REV_SOURCE__</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:8px">
      <span class="vbadge" style="background:linear-gradient(135deg,#1f3a93,#2a4db8);border-color:#2a4db8;box-shadow:0 2px 8px rgba(31,58,147,.25)">__CORE_BADGE__</span>
      <span style="font-size:12.5px;color:var(--ink-2)">__STOCK_CORE_NOTE__</span>
    </div>
    <table>
      <tr><th>#</th><th>持有基金</th><th>类型</th><th>持股市值</th><th>占流通</th><th>占净值</th></tr>
      __STOCK_FUND_ROWS__
    </table>
    <div class="insight">__REV_NOTE__</div>
  </div>

  <!-- 04 抱团全景 -->
  <div class="sec"><h2><span class="no">04</span>抱团全景</h2><span class="hint">__HERD_HINT__</span></div>
  <div class="grid-2">
    <div class="card" style="display:flex;align-items:center">__HERD_SVG__</div>
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:8px">抱团解读 <span style="font-size:11px;color:var(--ink-3)">__HERD_SCOPE__</span></h3>
      __HERD_VIEW_ROWS__
    </div>
  </div>

  <!-- 05 解读与风险 -->
  <div class="sec"><h2><span class="no">05</span>穿透解读与风险</h2><span class="hint">闭环结论 · 模型输出</span></div>
  <div class="card">
    <h3 style="font-size:14px;margin-bottom:8px">穿透闭环结论</h3>
    __CLOSE_ROWS__
    <h3 style="font-size:14px;margin:12px 0 8px">风险提示</h3>
    __RISK_ROWS__
  </div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
def main():
    total = sum(r for _, _, r, _, _, _ in ETF_HOLD)
    html = TPL
    html = html.replace("__DATE__", DATE.replace("-", ""))
    html = html.replace("__WEEKDAY__", WEEKDAY).replace("__DATE_SHOW__", DATE.replace("-", ""))
    html = (html.replace("__WEEKDAY__", WEEKDAY)
            .replace("__ETF_NAME__", CFG["etf_name"])
            .replace("__STOCK_NAME__", CFG["stock_name"])
            .replace("__VERDICT__", CFG["verdict"])
            .replace("__VERDICT_NOTE__", CFG["verdict_note"])
            .replace("__KPI_ROWS__", kpi_rows())
            .replace("__SUMMARY_ROWS__", summary_rows())
            .replace("__HOLD_ROWS__", hold_rows())
            .replace("__FWD_NOTE__", FWD_NOTE)
            .replace("__ARCHIVE_ROWS__", archive_rows())
            .replace("__HOLDER_BAR__", holder_bar())
            .replace("__CONC_SVG__", conc_svg())
            .replace("__CORE_BADGE__", CORE_BADGE)
            .replace("__STOCK_CORE_NOTE__", STOCK_CORE["note"])
            .replace("__STOCK_FUND_ROWS__", stock_fund_rows())
            .replace("__REV_NOTE__", REV_NOTE)
            .replace("__HERD_HINT__", HERD_HINT)
            .replace("__HERD_SVG__", herd_svg())
            .replace("__HERD_VIEW_ROWS__", herd_view_rows())
            .replace("__CLOSE_ROWS__", close_rows())
            .replace("__RISK_ROWS__", risk_rows())
            .replace("__NOTE__", NOTE))
    html = (html.replace("__REPORT_PERIOD__", REPORT_PERIOD)
            .replace("__REV_PERIOD__", REV_PERIOD)
            .replace("__REV_SOURCE__", REV_SOURCE)
            .replace("__HERD_SCOPE__", HERD_SCOPE))
    out_path = os.path.join(BASE, f"穿透分析_{CFG['out_tag']}_{DATE.replace('-', '')}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK ->", out_path, "| size:", len(html.encode("utf-8")))

if __name__ == "__main__":
    main()
