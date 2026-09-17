# -*- coding: utf-8 -*-
"""A股个股估值仪表盘 HTML 生成器 v1.1（模板，带 2026-08-21 紫金矿业示例数据）
【模板使用说明】生成某股票"贵还是便宜？"估值仪表盘：
①hithink CLI 拉当前估值快照(valuation snapshot) + 5年前复权日K(market history --adjust forward) + 行业可比公司估值快照
②历史 PE/PB 分位用【回溯法】计算：历史PE_i = 当前PE_TTM × (前复权收盘_i / 当前收盘)（口径标 [ASSUMED]，见 NOTE）
③WebSearch 查最新业绩/券商一致预期做"动态估值"锚点（forward PE）
④替换 BASE/DATE/WEEKDAY 与数据区（CFG/PERC/INDUSTRY/IND_MED/EARN/H1/FC/RISK/SUMMARY/NOTE/PE_NOTE/PB_NOTE/IND_NOTE/FC_NOTE + HIST 路径）
⑤运行 → 输出 `估值仪表盘_{名称}_{YYYYMMDD}.html`；**换标的前必须 grep 旧标的名清理残留**（模板已参数化，但数据区全部要换）
数据坑：valuation 只有 snapshot（无历史估值/行业估值接口）→ 分位必须回溯法自建；market snapshot 无市值字段（回溯法不需要股本）；
PE/PB 分位=当前值在历史序列中的百分位；行业对比用可比公司中位数（按标的主营选同行）；
【SVG 坑】fill 不支持 CSS linear-gradient 字符串（会回退黑色）→ 一律纯色；
【口径坑】盈利高增股（净利5年翻倍+）回溯法按当前 TTM 净利回溯会低估历史 PE → 页脚/风险区必须注明；
【数据来源铁律】hithink 能取到的一律走 CLI；券商预测/目标价等接口无 → WebSearch 公开披露补齐并在页脚标注来源
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import json
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
HIST = os.path.join(BASE, ".workbuddy", "output", "zjky_val_history.json")
DATE = "2026-08-21"
WEEKDAY = "周五"

# ================= 数据 =================
CFG = {
    "name": "紫金矿业", "code": "601899.SH", "sector": "工业金属·黄金铜", "sector_icon": "⛏️",
    "px": 34.74, "chg_pct": 2.69, "pe": 13.65, "pb": 4.57, "ps": 5.19, "pcf": 9.05,
    "verdict": "中性（结构分化）", "verdict_short": "中",
    "verdict_note": ("自身历史看偏贵：PE/PB 均处 5 年 96% 高分位（周期景气高位）；但相对同行与动态看便宜："
                     "PE 仅为黄金/铜业中位的 6 成，2026E forward PE 11.4 倍、机构 100% 买入——'PE 低、PB 高'的结构分化，"
                     "估值是否合理关键看铜金价格能否维持。"),
}
PERC = {
    "p5": {"pe": 96, "pb": 96, "pe_avg": 6.3, "pe_med": 4.8, "pe_rng": (2.7, 16.6),
           "pb_avg": 2.11, "pb_med": 1.62, "pb_rng": (0.90, 5.57)},
    "p3": {"pe": 94, "pb": 94},
    "p1": {"pe": 83, "pb": 83},
}
INDUSTRY = [
    ("紫金矿业", "601899", 13.65, 4.57, True),
    ("山东黄金", "600547", 33.11, 5.34, False),
    ("中金黄金", "600489", 20.99, 4.02, False),
    ("赤峰黄金", "600988", 26.19, 6.57, False),
    ("湖南黄金", "002155", 21.45, 4.46, False),
    ("江西铜业", "600362", 19.86, 1.89, False),
    ("铜陵有色", "000630", 33.60, 2.36, False),
]
IND_MED = (23.82, 4.24)
EARN = [
    ("2022", "2703.29", "200.42", "0.76"), ("2023", "2934.03", "211.19", "0.80"),
    ("2024", "3036.40", "320.51", "1.21"), ("2025", "3490.79", "517.77", "1.95"),
]
H1 = {"rev": 1941.78, "rev_yoy": "+15.78%", "np": 391.70, "np_yoy": "+68.17%", "gm": 37.75, "roe": 19.60,
      "note": "盈利高增靠金属价格：铜金涨价+新矿并表驱动归母+68%；但成本上升（入选品位下降/运输/税金），Q2 归母环比微降是预警信号——金属价格是核心变量"}
FC = [("2026E", 810, 11.4), ("2027E", 955, 9.7), ("2028E", 1052, 8.8)]
RISK = [
    "5 年 PE/PB 分位 96%——历史中枢仅 4.8/1.6 倍，当前处周期景气高位，均值回归空间大",
    "高 PB（4.57）靠 ROE 19.6% 支撑，而 ROE 靠高金属价格：铜-20%/金-15% 情景下 ROE 或降至 12-14%、PB 中枢下移至 3-3.5 倍",
    "金属价格回调是最大风险（2015 年铜价暴跌时归母降 60%）；Q2 归母环比微降+高盛下调今明两年盈利预测 1-3%",
    "历史分位为回溯口径 [ASSUMED]：紫金净利 5 年增 3.3 倍（156→518 亿），按当前 TTM 净利回溯会低估历史 PE——实际分位更高、当前更贵",
]
SUMMARY = [
    ("结论", "结构分化：5 年 96% 分位=自身历史偏贵（周期高位）；但 PE 仅行业 6 成 + 2026E forward PE 11.4 倍 + 机构 100% 买入=相对便宜——中性偏合理，核心变量是铜金价格。"),
    ("PE视角", "PE_TTM 13.7，5 年分位 96%（均值 6.3/中位 4.8）——紫金历史 PE 常年 4-8 倍，当前处高位；但回溯口径未计盈利增长，实际分位更高。"),
    ("PB视角", "PB_MRQ 4.57，5 年分位 96%——高 PB 由 ROE 19.6% 支撑，金属价格回落则 PB 中枢下移（敏感性：回落至 3-3.5 倍）。"),
    ("行业对比", "PE 为黄金/铜业 6 家中位（23.8）的 0.57 倍、PB 1.08 倍——龙头体量与盈利稳定性享受折价，相对同行显著便宜。"),
    ("动态视角", "一致预期 2026E 归母 810 亿（+56%）、forward PE 11.4 倍；86 家机构 100% 买入/增持，A股目标价 44.26 元——动态估值不贵。"),
]
PE_NOTE = "💡 5 年 PE 区间 2.7~16.6，当前 13.7 处于 96% 高位——紫金历史 PE 常年 4-8 倍，2024 年以来铜金涨价+业绩爆发（归母 5 年增 3.3 倍）推动估值中枢上移，当前处周期景气高位。"
PB_NOTE = "💡 5 年 PB 区间 0.90~5.57，当前 4.57 接近历史最高——高 PB 由 ROE 19.6% 支撑，金属价格回落则 PB 中枢下移（敏感性：铜-20%/金-15% → 3-3.5 倍）。"
IND_NOTE = "💡 紫金 PE 13.7 仅为黄金/铜业中位（23.8）的 0.57 倍、PB 1.08 倍——龙头体量与盈利稳定性（2026H1 归母 392 亿、ROE 19.6%）享受折价，相对同行显著便宜；但历史分位已高，估值合理性取决于铜金价格能否维持。"
FC_NOTE = "💡 一致预期 2026E 归母 810 亿（+56%）对应 forward PE 11.4 倍——动态估值不贵；86 家机构 100% 买入/增持、A股目标价 44.26 元，高盈利增长正在消化周期高位。"
NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，valuation.snapshot + market history 前复权 5 年 + financials income）；"
        "历史 PE/PB 分位为【回溯法】计算（历史PE_i=当前PE_TTM×(前复权收盘_i/当前收盘)，口径假设当前 TTM 净利与股本不变，标 [ASSUMED]——紫金净利高速增长下该口径低估历史 PE）；"
        "行业对比=黄金/铜业 6 家可比公司估值快照中位数；一致预期与目标价来自同花顺一致预期/券商公开研报（2026-08）。"
        "估值判定为模型综合判断（模型输出），仅供研究参考，不构成个人投资建议。")

# ---- 模板占位默认值：skill 自带数据区（保证脚本可独立运行；平台渲染时本区被 caps 整体替换）----
CHG_TXT = ("+" if CFG["chg_pct"] >= 0 else "") + f"{CFG['chg_pct']:.2f}"
SELF_HL_NAME = ""                       # 默认不高亮；平台注入被分析标的名（取不到则取消高亮）
IND_HINT = "电网设备可比公司 · 2026-08-21"
H1_LABEL = "2026H1"
H1_REVYOY_TXT = "+" + H1["rev_yoy"]     # 保留模板示例原输出（含模板原有的重复 +）
H1_NPYOY_TXT = "+" + H1["np_yoy"]       # 保留模板示例原输出（含模板原有的重复 +）
# ---- 兜底：脚本自带示例序列（真实数据降采样），无外部序列文件时自建，保证脚本可独立运行 ----
if not os.path.exists(HIST):
    os.makedirs(os.path.dirname(HIST), exist_ok=True)
    with open(HIST, "w", encoding="utf-8") as _hf:
        json.dump({"_demo": "skill 自带示例日K序列（降采样）", "data": [{"date": "2021-08-02", "close": 9.704}, {"date": "2021-08-13", "close": 10.135}, {"date": "2021-08-26", "close": 9.327}, {"date": "2021-09-08", "close": 9.74}, {"date": "2021-09-23", "close": 9.497}, {"date": "2021-10-13", "close": 9.614}, {"date": "2021-10-26", "close": 10.153}, {"date": "2021-11-08", "close": 9.435}, {"date": "2021-11-19", "close": 9.363}, {"date": "2021-12-02", "close": 9.013}, {"date": "2021-12-15", "close": 9.022}, {"date": "2021-12-28", "close": 8.716}, {"date": "2022-01-11", "close": 8.465}, {"date": "2022-01-24", "close": 9.237}, {"date": "2022-02-11", "close": 9.928}, {"date": "2022-02-24", "close": 9.874}, {"date": "2022-03-09", "close": 10.117}, {"date": "2022-03-22", "close": 10.144}, {"date": "2022-04-06", "close": 10.413}, {"date": "2022-04-19", "close": 10.772}, {"date": "2022-05-05", "close": 9.731}, {"date": "2022-05-18", "close": 8.788}, {"date": "2022-05-31", "close": 9.031}, {"date": "2022-06-14", "close": 9.164}, {"date": "2022-06-27", "close": 8.505}, {"date": "2022-07-08", "close": 8.303}, {"date": "2022-07-21", "close": 7.937}, {"date": "2022-08-03", "close": 7.772}, {"date": "2022-08-16", "close": 8.267}, {"date": "2022-08-29", "close": 8.258}, {"date": "2022-09-09", "close": 8.413}, {"date": "2022-09-23", "close": 7.809}, {"date": "2022-10-13", "close": 7.177}, {"date": "2022-10-26", "close": 7.269}, {"date": "2022-11-08", "close": 8.294}, {"date": "2022-11-21", "close": 8.624}, {"date": "2022-12-02", "close": 9.256}, {"date": "2022-12-15", "close": 9.393}, {"date": "2022-12-28", "close": 9.155}, {"date": "2023-01-11", "close": 10.519}, {"date": "2023-01-31", "close": 10.794}, {"date": "2023-02-13", "close": 10.345}, {"date": "2023-02-24", "close": 10.647}, {"date": "2023-03-09", "close": 10.583}, {"date": "2023-03-22", "close": 10.748}, {"date": "2023-04-04", "close": 11.306}, {"date": "2023-04-18", "close": 12.689}, {"date": "2023-05-04", "close": 11.837}, {"date": "2023-05-17", "close": 10.07}, {"date": "2023-05-30", "close": 9.805}, {"date": "2023-06-12", "close": 10.574}, {"date": "2023-06-27", "close": 10.885}, {"date": "2023-07-10", "close": 10.746}, {"date": "2023-07-21", "close": 11.667}, {"date": "2023-08-03", "close": 11.863}, {"date": "2023-08-16", "close": 11.351}, {"date": "2023-08-29", "close": 11.248}, {"date": "2023-09-11", "close": 12.105}, {"date": "2023-09-22", "close": 12.04}, {"date": "2023-10-13", "close": 11.193}, {"date": "2023-10-26", "close": 11.248}, {"date": "2023-11-08", "close": 11.006}, {"date": "2023-11-21", "close": 11.304}, {"date": "2023-12-04", "close": 11.546}, {"date": "2023-12-15", "close": 10.895}, {"date": "2023-12-28", "close": 11.547}, {"date": "2024-01-11", "close": 11.351}, {"date": "2024-01-24", "close": 10.958}, {"date": "2024-02-06", "close": 11.398}, {"date": "2024-02-27", "close": 12.305}, {"date": "2024-03-11", "close": 13.894}, {"date": "2024-03-22", "close": 14.39}, {"date": "2024-04-08", "close": 16.176}, {"date": "2024-04-19", "close": 17.419}, {"date": "2024-05-07", "close": 16.316}, {"date": "2024-05-20", "close": 18.205}, {"date": "2024-05-31", "close": 16.279}, {"date": "2024-06-14", "close": 16.161}, {"date": "2024-06-27", "close": 15.982}, {"date": "2024-07-10", "close": 17.381}, {"date": "2024-07-23", "close": 15.622}, {"date": "2024-08-05", "close": 14.781}, {"date": "2024-08-16", "close": 15.107}, {"date": "2024-08-29", "close": 15.164}, {"date": "2024-09-11", "close": 13.517}, {"date": "2024-09-26", "close": 16.535}, {"date": "2024-10-16", "close": 16.611}, {"date": "2024-10-29", "close": 16.392}, {"date": "2024-11-11", "close": 15.716}, {"date": "2024-11-22", "close": 15.002}, {"date": "2024-12-05", "close": 14.736}, {"date": "2024-12-18", "close": 14.745}, {"date": "2024-12-31", "close": 14.393}, {"date": "2025-01-14", "close": 15.621}, {"date": "2025-01-27", "close": 15.459}, {"date": "2025-02-17", "close": 15.707}, {"date": "2025-02-28", "close": 14.612}, {"date": "2025-03-13", "close": 16.145}, {"date": "2025-03-26", "close": 17.325}, {"date": "2025-04-09", "close": 15.155}, {"date": "2025-04-22", "close": 17.61}, {"date": "2025-05-08", "close": 16.906}, {"date": "2025-05-21", "close": 17.601}, {"date": "2025-06-04", "close": 17.22}, {"date": "2025-06-17", "close": 18.225}, {"date": "2025-06-30", "close": 18.833}, {"date": "2025-07-11", "close": 18.244}, {"date": "2025-07-24", "close": 19.432}, {"date": "2025-08-06", "close": 19.471}, {"date": "2025-08-19", "close": 19.635}, {"date": "2025-09-01", "close": 23.547}, {"date": "2025-09-12", "close": 24.773}, {"date": "2025-09-25", "close": 26.338}, {"date": "2025-10-16", "close": 29.655}, {"date": "2025-10-29", "close": 30.132}, {"date": "2025-11-11", "close": 28.828}, {"date": "2025-11-24", "close": 27.251}, {"date": "2025-12-05", "close": 30.482}, {"date": "2025-12-18", "close": 30.142}, {"date": "2025-12-31", "close": 33.548}, {"date": "2026-01-15", "close": 37.227}, {"date": "2026-01-28", "close": 41.169}, {"date": "2026-02-10", "close": 37.772}, {"date": "2026-03-03", "close": 37.821}, {"date": "2026-03-16", "close": 33.821}, {"date": "2026-03-27", "close": 31.602}, {"date": "2026-04-10", "close": 32.847}, {"date": "2026-04-23", "close": 33.48}, {"date": "2026-05-11", "close": 33.354}, {"date": "2026-05-22", "close": 30.132}, {"date": "2026-06-04", "close": 29.529}, {"date": "2026-06-17", "close": 29.616}, {"date": "2026-07-01", "close": 24.802}, {"date": "2026-07-14", "close": 28.704}, {"date": "2026-07-27", "close": 31.38}, {"date": "2026-08-07", "close": 34.719}, {"date": "2026-08-20", "close": 33.83}]}, _hf, ensure_ascii=False)

# ================= 图表 =================
def hist_series():
    """读历史K，抽样生成 PE/PB 序列（前复权收盘 → 回溯 PE/PB）"""
    bars = json.load(open(HIST, encoding='utf-8'))['data']
    step = max(1, len(bars) // 120)
    out = []
    for b in bars[::step]:
        pe = CFG["pe"] * b['close'] / CFG["px"]
        pb = CFG["pb"] * b['close'] / CFG["px"]
        out.append((b['date'], pe, pb))
    return out

def line_svg(kind):
    """PE/PB 5年折线图；kind='pe'|'pb'"""
    series = hist_series()
    W, H = 880, 300
    pad_l, pad_r, pad_t, pad_b = 46, 14, 20, 30
    cur = CFG["pe"] if kind == "pe" else CFG["pb"]
    lo = min(s[1] if kind == "pe" else s[2] for s in series)
    hi = max(s[1] if kind == "pe" else s[2] for s in series)
    lo = min(lo, cur); hi = max(hi, cur)
    span = hi - lo or 1
    def X(i): return pad_l + i / (len(series) - 1) * (W - pad_l - pad_r)
    def Y(v): return pad_t + (1 - (v - lo) / span) * (H - pad_t - pad_b)
    # 网格 + 当前值线 + 均值线
    parts = []
    for g in [0.2, 0.4, 0.6, 0.8]:
        y = pad_t + g * (H - pad_t - pad_b)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{W-pad_r}" y2="{y:.1f}" stroke="#eef0f3" stroke-width="1"/>')
    # 当前值水平线（红）+ 均值线（金）+ 中位线（蓝虚）
    avg = PERC["p5"]["pe_avg"] if kind == "pe" else PERC["p5"]["pb_avg"]
    med = PERC["p5"]["pe_med"] if kind == "pe" else PERC["p5"]["pb_med"]
    parts.append(f'<line x1="{pad_l}" y1="{Y(cur):.1f}" x2="{W-pad_r}" y2="{Y(cur):.1f}" stroke="#e5484d" stroke-width="1.6" stroke-dasharray="6 4"/>')
    parts.append(f'<line x1="{pad_l}" y1="{Y(avg):.1f}" x2="{W-pad_r}" y2="{Y(avg):.1f}" stroke="#c9a227" stroke-width="1.2" stroke-dasharray="4 4"/>')
    parts.append(f'<line x1="{pad_l}" y1="{Y(med):.1f}" x2="{W-pad_r}" y2="{Y(med):.1f}" stroke="#2f56c9" stroke-width="1" stroke-dasharray="3 4" opacity="0.7"/>')
    # 折线 + 渐变面积
    vals = [s[1] if kind == "pe" else s[2] for s in series]
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
    area = f"{pad_l},{H-pad_b} " + pts + f" {W-pad_r},{H-pad_b}"
    color = "#1f3a93" if kind == "pb" else "#2f56c9"
    parts.append(f'<polygon points="{area}" fill="url(#grad{kind})"/>')
    parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.8"/>')
    # 当前值点
    parts.append(f'<circle cx="{X(len(series)-1):.1f}" cy="{Y(cur):.1f}" r="4.5" fill="#e5484d" stroke="#fff" stroke-width="2"/>')
    # 图例
    pct = PERC["p5"]["pe"] if kind == "pe" else PERC["p5"]["pb"]
    dec = 1 if kind == "pe" else 2
    parts.append(f'<text x="{pad_l}" y="14" font-size="12" font-weight="700" fill="#e5484d">当前 {cur:.{dec}f}（5年分位 {pct}%）</text>')
    parts.append(f'<text x="{pad_l+190}" y="14" font-size="11" fill="#c9a227">均值 {avg:.{dec}f}</text>')
    parts.append(f'<text x="{pad_l+280}" y="14" font-size="11" fill="#2f56c9">中位 {med:.{dec}f}</text>')
    parts.append(f'<text x="{pad_l+360}" y="14" font-size="11" fill="#9aa1ad">5年区间 {lo:.{dec}f} ~ {hi:.{dec}f}</text>')
    # 时间轴刻度（首/中/尾）
    n = len(series)
    for idx, lab in [(0, series[0][0][:7]), (n//2, series[n//2][0][:7]), (n-1, series[-1][0][:7])]:
        parts.append(f'<text x="{X(idx):.1f}" y="{H-8}" text-anchor="middle" font-size="10.5" fill="#9aa1ad">{lab}</text>')
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{kind.upper()} 5年走势">
      <defs>
        <linearGradient id="grad{kind}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.14"/><stop offset="100%" stop-color="{color}" stop-opacity="0"/>
        </linearGradient>
      </defs>
      {''.join(parts)}
    </svg>'''

def perc_bar(kind):
    """分位判定条：0-100 刻度，当前分位处标记"""
    W, H = 880, 64
    pad_l, pad_r = 70, 14
    p5 = PERC["p5"]["pe"] if kind == "pe" else PERC["p5"]["pb"]
    p3 = PERC["p3"]["pe"] if kind == "pe" else PERC["p3"]["pb"]
    p1 = PERC["p1"]["pe"] if kind == "pe" else PERC["p1"]["pb"]
    xw = W - pad_l - pad_r
    def X(p): return pad_l + p / 100 * xw
    # 分段色带：0-50 便宜(绿淡) 50-80 中性(黄) 80-100 贵(红淡)
    parts = [f'<rect x="{X(0):.1f}" y="18" width="{X(50)-X(0):.1f}" height="16" rx="3" fill="#2fa36b" opacity="0.25"/>',
             f'<rect x="{X(50):.1f}" y="18" width="{X(80)-X(50):.1f}" height="16" rx="3" fill="#c9a227" opacity="0.3"/>',
             f'<rect x="{X(80):.1f}" y="18" width="{X(100)-X(80):.1f}" height="16" rx="3" fill="#e5484d" opacity="0.3"/>']
    # 三个窗口的当前分位标记
    marks = [("5年", p5, "#e5484d", 12), ("3年", p3, "#c9a227", 30), ("1年", p1, "#2f56c9", 48)]
    for lab, p, color, dy in marks:
        parts.append(f'<circle cx="{X(p):.1f}" cy="26" r="4.5" fill="{color}" stroke="#fff" stroke-width="1.6"/>')
        parts.append(f'<text x="{X(p):.1f}" y="{dy}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{color}">{lab} {p}%</text>')
    parts.append(f'<text x="{X(50):.1f}" y="52" text-anchor="middle" font-size="10" fill="#9aa1ad">便宜 ← 0%</text>')
    parts.append(f'<text x="{X(100):.1f}" y="52" text-anchor="middle" font-size="10" fill="#9aa1ad">贵 → 100%</text>')
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{kind.upper()} 历史分位判定条">{''.join(parts)}</svg>'''

def ind_chart(kind):
    """行业对比横向条形图：PE 蓝系 / PB 绿系，被分析标的名（SELF_HL_NAME）行金色高亮（SVG fill 必须纯色，不支持 CSS 渐变字符串）"""
    W, H = 420, 320
    pad_l, pad_t, row_h, gap = 88, 18, 32, 6
    vals = [(n, (pe if kind == "pe" else pb)) for n, c, pe, pb, me in INDUSTRY]
    vmax = max(v for _, v in vals)
    xw = W - pad_l - 70
    bar_c = "#2f56c9" if kind == "pe" else "#2fa36b"   # 非高亮行：PE 蓝 / PB 绿
    txt_c = "#1f3a93" if kind == "pe" else "#1e7a4d"
    parts = []
    for i, (name, v) in enumerate(vals):
        y = pad_t + i * (row_h + gap)
        w = max(v / vmax * xw, 4)
        is_self = bool(SELF_HL_NAME) and name == SELF_HL_NAME
        color = "#c9a227" if is_self else bar_c
        fw = "800" if is_self else "600"
        fc = "#8a6d12" if is_self else txt_c
        parts.append(f'<text x="{pad_l-8}" y="{y+row_h/2+4:.1f}" text-anchor="end" font-size="11.5" font-weight="{fw}" fill="{"var(--ink)" if is_self else "#5b6470"}">{name}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+5:.1f}" width="{w:.1f}" height="{row_h-10}" rx="5" fill="{color}"/>')
        parts.append(f'<text x="{pad_l+w+6:.1f}" y="{y+row_h/2+4:.1f}" font-size="11" font-weight="{fw}" fill="{fc}">{v:.1f}</text>')
    # 行业中位线
    med = IND_MED[0] if kind == "pe" else IND_MED[1]
    mx = pad_l + med / vmax * xw
    parts.append(f'<line x1="{mx:.1f}" y1="{pad_t-6}" x2="{mx:.1f}" y2="{pad_t+7*(row_h+gap)-8}" stroke="#9aa1ad" stroke-width="1.4" stroke-dasharray="5 3"/>')
    parts.append(f'<text x="{mx:.1f}" y="12" text-anchor="middle" font-size="10" fill="#9aa1ad">行业中位 {med}</text>')
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="行业{kind.upper()}对比">{''.join(parts)}</svg>'''

def earn_rows():
    rows = ""
    for y, rev, np_, eps in EARN:
        rows += f'<tr><td class="num" style="color:var(--ink-3)">{y}</td><td class="num">{rev}</td><td class="num" style="font-weight:700">{np_}</td><td class="num" style="color:var(--ink-2)">{eps}</td></tr>'
    return rows

def fc_rows():
    rows = ""
    for y, np_, pe in FC:
        rows += f'<tr><td>{y}</td><td class="num" style="font-weight:700">{np_}亿</td><td class="num" style="color:var(--red);font-weight:800">{pe}倍</td></tr>'
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

def verdict_badge():
    """判定徽章：贵/中性/便宜"""
    v = CFG["verdict_short"]
    if v in ("贵", "偏贵"):
        color, bg = "#e5484d", "#fdeeee"
    elif v in ("便宜", "低估"):
        color, bg = "#2fa36b", "#eaf6f0"
    else:
        color, bg = "#c9a227", "#faf5e3"
    return f'<span class="vbadge" style="color:{color};background:{bg};border-color:{color}33">{v}</span>'

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>估值仪表盘_{NAME}_{DATE}</title>
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
  .vbadge { display:inline-block; font-size:15px; font-weight:800; padding:4px 18px; border-radius:24px; border:1px solid; }
  .tcode { font-size:14px; color:var(--ink-3); font-weight:600; letter-spacing:.5px; margin-left:8px; vertical-align:3px; }
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
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { text-align:left; font-size:11.5px; color:var(--ink-3); font-weight:600; padding:6px 8px; border-bottom:2px solid var(--border); }
  td { padding:8px; border-bottom:1px dashed #f0f1f4; vertical-align:middle; }
  tbody tr:nth-child(even) { background:#fafbfc; }
  tbody tr:hover { background:var(--brand-soft); }
  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13.5px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink-2); }
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
      <div class="title">__NAME__ <span class="tcode">__CODE__</span></div>
      <div class="sub">
        <span class="pill brand">__WEEKDAY__ · __DATE__</span>
        <span class="pill brand">__SECTOR_ICON__ __SECTOR__</span>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num up">¥__PX__</div><div class="k">最新价 (__CHG_TXT__%)</div></div>
      <div class="kpi"><div class="v num gd">__PE__</div><div class="k">PE_TTM</div></div>
      <div class="kpi"><div class="v num gd">__PB__</div><div class="k">PB_MRQ</div></div>
      <div class="kpi"><div class="v num">__VERDICT__</div><div class="k">__PERC_KPI__</div></div>
    </div>
  </div>

  <!-- 01 判定总览 -->
  <div class="sec"><h2><span class="no">01</span>估值判定</h2><span class="hint">历史分位 + 行业对比 + 动态视角</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      __VERDICT_BADGE__
      <b style="font-size:15px">__VERDICT__</b>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
  </div>

  <!-- 02 历史分位 -->
  <div class="sec"><h2><span class="no">02</span>历史估值分位</h2><span class="hint">回溯法 · 当前TTM口径 [ASSUMED]</span></div>
  <div class="card">
    <h3>PE(TTM) 5年走势 <span class="unit">前复权回溯口径 [ASSUMED]</span></h3>
    __PERC_BAR_PE__
    __LINE_PE__
    <div class="insight">__PE_NOTE__</div>
  </div>
  <div class="card" style="margin-top:14px">
    <h3>PB(MRQ) 5年走势 <span class="unit">前复权回溯口径 [ASSUMED]</span></h3>
    __PERC_BAR_PB__
    __LINE_PB__
    <div class="insight">__PB_NOTE__</div>
  </div>

  <!-- 03 行业对比 -->
  <div class="sec"><h2><span class="no">03</span>行业对比</h2><span class="hint">__IND_HINT__</span></div>
  <div class="grid-2">
    <div class="card"><h3>PE(TTM) 对比 <span class="unit">金色=__NAME__</span></h3>__IND_PE_CHART__</div>
    <div class="card"><h3>PB(MRQ) 对比 <span class="unit">金色=__NAME__</span></h3>__IND_PB_CHART__
    </div>
  </div>
  <div class="card" style="margin-top:14px"><h3>行业对比解读</h3>
    <div class="insight">__IND_NOTE__</div>
  </div>

  <!-- 04 估值锚点 -->
  <div class="sec"><h2><span class="no">04</span>估值锚点</h2><span class="hint">盈利增长能否消化高估值</span></div>
  <div class="grid-2">
    <div class="card"><h3>近4年业绩 <span class="unit">营收/归母/亿</span></h3>
      <table>
        <tr><th>年份</th><th>营收</th><th>归母净利</th><th>EPS</th></tr>
        __EARN_ROWS__
      </table>
      <div class="kv" style="margin-top:8px"><span class="k">__H1_LABEL__</span><span class="v" style="font-size:12.5px;color:var(--ink-2)">营收 {H1_REV}亿({H1_REVYOY_TXT}) · 归母 {H1_NP}亿({H1_NPYOY_TXT}) · 毛利率 {H1_GM}%</span></div>
      <div class="insight">{H1_NOTE}</div>
    </div>
    <div class="card"><h3>动态估值（券商预测） <span class="unit">forward PE</span></h3>
      <table>
        <tr><th>年度</th><th>预测归母净利</th><th>对应PE</th></tr>
        __FC_ROWS__
      </table>
      <div class="insight">__FC_NOTE__</div>
    </div>
  </div>

  <!-- 05 风险提示 -->
  <div class="sec"><h2><span class="no">05</span>风险提示</h2><span class="hint">高分位下的回撤风险</span></div>
  <div class="card">__RISK_ROWS__</div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
html = (TPL
        .replace("__NAME__", CFG["name"]).replace("__CODE__", CFG["code"])
        .replace("__SECTOR__", CFG["sector"]).replace("__SECTOR_ICON__", CFG["sector_icon"])
        .replace("__DATE__", DATE).replace("__WEEKDAY__", WEEKDAY)
        .replace("__PX__", f"{CFG['px']:.2f}").replace("__CHG_TXT__", CHG_TXT)
        .replace("__PE__", f"{CFG['pe']:.1f}").replace("__PB__", f"{CFG['pb']:.2f}")
        .replace("__VERDICT__", CFG["verdict"]).replace("__VERDICT_BADGE__", verdict_badge())
        .replace("__VERDICT_NOTE__", CFG["verdict_note"])
            .replace("__PERC_KPI__", f"5年{PERC['p5']['pe']}%分位")
        .replace("__IND_HINT__", IND_HINT).replace("__H1_LABEL__", H1_LABEL)
        .replace("__SUMMARY_ROWS__", summary_rows())
        .replace("__PERC_BAR_PE__", perc_bar("pe")).replace("__PERC_BAR_PB__", perc_bar("pb"))
        .replace("__LINE_PE__", line_svg("pe")).replace("__LINE_PB__", line_svg("pb"))
        .replace("__IND_PE_CHART__", ind_chart("pe")).replace("__IND_PB_CHART__", ind_chart("pb"))
                .replace("__EARN_ROWS__", earn_rows())
        .replace("__FC_ROWS__", fc_rows())
        .replace("__RISK_ROWS__", risk_rows())
        .replace("__PE_NOTE__", PE_NOTE)
        .replace("__PB_NOTE__", PB_NOTE)
        .replace("__IND_NOTE__", IND_NOTE)
        .replace("__FC_NOTE__", FC_NOTE)
        .replace("{H1_REV}", f"{H1['rev']:.2f}").replace("{H1_REVYOY_TXT}", H1_REVYOY_TXT)
        .replace("{H1_NP}", f"{H1['np']:.2f}").replace("{H1_NPYOY_TXT}", H1_NPYOY_TXT)
        .replace("{H1_GM}", f"{H1['gm']:.2f}").replace("{H1_NOTE}", H1["note"])
        .replace("{NAME}", CFG["name"]).replace("{DATE}", DATE.replace("-", ""))
        .replace("__NOTE__", NOTE))

out_path = os.path.join(BASE, f"估值仪表盘_{CFG['name']}_{DATE.replace('-', '')}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {out_path} | size: {len(html.encode('utf-8'))} bytes")
