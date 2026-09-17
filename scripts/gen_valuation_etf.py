# -*- coding: utf-8 -*-
"""ETF 估值仪表盘 HTML 生成器 v1.1（模板，带 2026-09-03 红利质量ETF华夏 159758 示例数据）
【模板使用说明】生成某 ETF"现在贵不贵？"估值仪表盘——核心是【跟踪指数的估值分位】：
①hithink CLI 拉 ETF 交易面与基金档案：fund snapshot（现价/涨跌/换手/成交额）+ fund profile（规模/费率/经理/单位净值）
②fund history --thscode <代码> --source remote 拉净值历史（注意 fund.history 无 --fund-type，见坑 7）→ 区间收益 + 走势图
③【跟踪指数识别】fund profile 无跟踪指数字段 → WebSearch"<基金名> 跟踪指数 代码"确认（如 159758 → 中证红利质量 931468.CSI）
④【指数估值分位 = WebSearch 公开指数估值，hithink 不含 ETF/指数估值！】搜"<指数代码> <名称> 市盈率 分位 股息率"
   乌龟量化/中证官网/乐咕乐股/理杏仁等口径，取最近交易日；多源有差异时主源+辅助源并标注（如 931468：A股行情表口径 PE 16.24/5年分位 24.2% vs 理杏仁 PE 17.03 时点不同）
⑤10Y 国债收益率 WebSearch（如 2026-08-28 中国 10 年期国债 1.70%）→ 股息率利差 = 指数股息率 - 国债收益率（红利类 ETF 核心锚）
⑥替换 BASE/DATE/WEEKDAY 与数据区（CFG/IDX/DIV/SNAP/RET/RISK/SUMMARY/NOTE 各 *_NOTE + HIST 序列文件路径）
⑦运行 → 输出 `ETF估值仪表盘_{名称}_{YYYYMMDD}.html`；**换标的前必须 grep 旧标的名/旧指数名清理残留**
【v1.1 修复（2026-09-03 用户反馈）】①分位判定条 v2：标题独立顶行 + 三分位标签垂直分行（leader 虚线指引）——v1 标题与 10年标签共用 y=14 撞车、5年标签压圆点、分位接近时文字重叠；②区间收益表数值列补 text-align:right 与表头对齐；③表下方说明改 __RET_NOTE__ 动态拼接（数值取自 RET，消除硬编码）
【数据铁律】页面必须显式提示：①跟踪指数估值分位/股息率来自公开指数估值源（非 hithink，同花顺不含 ETF/指数估值接口，标注来源与时点）
②指数估值分位为公开披露口径（可能为成分股加权或指数公司披露，与个股估值口径不同，不可混比）
③多源分位数值不同属正常（时点/口径差异），页脚列全部来源
④折溢价为估算口径 [ASSUMED]（现价 vs 单位净值，非 IOPV）
风格：与其余能力一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、tabular-nums、.insight 金色结论条
"""
import json
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
HIST = os.path.join(BASE, ".workbuddy", "output", "etf_159758_series.json")
DATE = "2026-09-03"
WEEKDAY = "周四"

# ================= 数据 =================
CFG = {
    "name": "红利质量ETF华夏", "code": "159758.SZ", "sector": "红利策略 · 股票型ETF",
    "idx_name": "中证红利质量指数", "idx_code": "931468.CSI", "idx_icon": "🧧",
    "px": 1.13, "chg_pct": 0.53, "dy": 3.06,              # dy=指数近1年股息率(公开口径)
    "verdict": "合理（红利中枢偏下）", "verdict_short": "合理",
    "verdict_note": ("跟踪指数 PE_TTM 16.2、10年分位 21.5%、5年分位 24.2%——估值处发布以来中低位，"
                     "股息率 3.06% 对 10Y 国债 1.70% 仍有 1.36pct 利差（红利资产的'安全垫'还在）；"
                     "但成分含医药/计算机/电子等成长（前 5 行业无银行），波动高于纯红利，'质量'因子决定其并非纯防御。"),
}
# 指数估值（公开指数估值源，非 hithink——多源标注）
IDX = {
    "pe": 16.24, "pb": 2.93,
    "p10": {"pe": 21.5, "pb": 24.1},   # 10年分位 %
    "p5": {"pe": 24.2, "pb": 27.4},    # 5年分位 %
    "p3": {"pe": 36.0, "pb": 45.6},    # 3年分位 %
    "src": "A股行情指标表(cs931468) 2026-08-28 收盘口径",
    "src2": "理杏仁 2026-08-14 口径：PE 17.03 / PB 2.95（时点不同，略高）",
    "src3": "中证指数官网新闻口径：近1年股息率 3.06%~3.09%（2026-05/06）",
    "pub_years": 10, "base_date": "2026-08-28",
}
DIV = {"dy": 3.06, "bond10": 1.70, "spread": 1.36, "bond_src": "中国 10 年期国债 1.70%（2026-08-28 债市收盘）"}
SNAP = {   # hithink fund snapshot（交易面）
    "open": 1.123, "high": 1.133, "low": 1.123, "prev": 1.124,
    "vol": "2910万份", "amount": "3287万元", "turnover": 2.23,
    "scale": "14.61亿", "rate": "0.20%/年", "nav": 1.1216,
    "premium": 0.75,   # 折溢价估算 % = (px-nav)/nav*100 [ASSUMED]
    "estab": "2021-12-20", "mgr": "杨斯琪 / 张金志", "mgmt": "华夏基金",
}
RET = [("近1周", -1.65), ("近1月", -1.82), ("近3月", 4.44), ("近6月", 2.91),
       ("近1年", 9.82), ("2025初至今", 23.77)]
RISK = [
    "跟踪指数含较高权重成长股（医药/计算机/电子）——'质量'红利非纯防御，市场杀成长时回撤高于中证红利/红利低波",
    "指数 PE 分位来自公开指数估值源，时点 2026-08-28（非实时）且口径与个股估值不同——估值判断应多源交叉、动态跟踪",
    "当前红利策略拥挤度上升（多只同策略 ETF 密集发行、华泰警示'估值历史较高需警惕交易拥挤'）——中低分位≠无回撤",
    "ETF 折溢价为估算口径 [ASSUMED]（现价 vs 单位净值，非 IOPV），大额申赎日折溢价可能扩大",
    "股息率随成分分红与价格波动，3.06% 为近 1 年口径；若股价上涨股息率被动下降，利差收窄则安全垫变薄",
]
SUMMARY = [
    ("结论", "指数 10 年分位 21.5%/5 年 24.2%=发布以来中低位，股息率利差 1.36pct 仍厚——估值合理偏下，红利资产的配置窗口未关闭。"),
    ("PE视角", "指数 PE_TTM 16.2，10年/5年/3年分位 21.5%/24.2%/36.0%——估值分位随窗口缩短上移，说明近 1-2 年指数成分盈利承压或股价修复，绝对估值不贵但趋势需盯。"),
    ("股息率视角", "近1年股息率 3.06%，对 10Y 国债（1.70%）利差 1.36pct——高于'1.0pct 以上具配置价值'的经验阈值，安全垫仍厚（对比：沪深300 股息率利差约 0.9pct）。"),
    ("成分结构", "'红利+质量'双因子：50 只连续分红+高盈利股，医药/计算机/电子等成长权重近 35%（无银行）——波动高于纯红利，是'进可攻退可守'的中间品种。"),
    ("交易面", "现价 1.13 较单位净值 1.1216 溢价约 0.75% [ASSUMED]；换手 2.23%、规模 14.61 亿——流动性充裕，溢价在正常区间。"),
]
PE_NOTE = "💡 指数 PE_TTM 16.2 处发布以来中低位（10年分位 21.5%）——但注意 3年分位 36% 已高于 10年分位，说明 2024-2026 估值中枢整体抬升（成分盈利修复+红利风格走强），'绝对不贵'≠'还能像过去两年那样涨'。"
PB_NOTE = "💡 PB 2.93、10年分位 24.1% 与 PE 分位基本一致——高 ROE（指数编制要求盈利质量）支撑下的合理估值，未见明显泡沫；若成分盈利下滑则 PB 分位将被动上升，风险在盈利端。"
DIV_NOTE = "💡 股息率 3.06% - 10Y国债 1.70% = 1.36pct 利差：红利资产相对债券的'超额现金流'仍厚，这是红利策略中期有效的核心支撑；利差若收窄至 <0.5pct 则配置性价比显著下降（参见 ETF 回测估值策略口径）。"
SUMMARY_ETFSNAP = "现价 1.130（+0.53%）· 规模 14.61亿 · 费率 0.20%/年 · 溢价约 +0.75% [ASSUMED]"
NOTE = ("数据来源：交易面/基金档案=同花顺金融数据（hithink-finance v0.1.7，fund.snapshot + fund.profile + fund.history，2026-09-03 收盘）；"
        "【跟踪指数估值分位/股息率 = WebSearch 公开指数估值源，同花顺不含 ETF/指数估值接口（valuation 仅 A 股个股，ETF 报 FUYAO_3001）】"
        "主口径=A股行情指标表 cs931468 红利质量 2026-08-28（PE 16.24 / PB 2.93 / 10年分位 21.5%/24.1%）；"
        "辅助口径=理杏仁 2026-08-14（PE 17.03/PB 2.95）与中证指数官网新闻（近1年股息率 3.06%~3.09%，2026-05/06）——多源数值差异属时点/口径不同；"
        "10Y 国债=1.70%（2026-08-28 债市收盘，新华财经/东方财富）；指数 2020-05 发布（发布以来 ~6 年），10 年分位为公开源外推口径 [ASSUMED]。"
        "折溢价为估算（现价 vs 单位净值，非 IOPV）[ASSUMED]；估值判定为模型综合判断（模型输出）。本报告仅供研究参考，不构成个人投资建议。")

# ---- 兜底：脚本自带示例序列（真实数据降采样），无外部序列文件时自建，保证脚本可独立运行 ----
if not os.path.exists(HIST):
    os.makedirs(os.path.dirname(HIST), exist_ok=True)
    with open(HIST, "w", encoding="utf-8") as _hf:
        json.dump([["2024-01-02", 0.838], ["2024-01-09", 0.817], ["2024-01-16", 0.823], ["2024-01-23", 0.792], ["2024-01-30", 0.788], ["2024-02-06", 0.81], ["2024-02-21", 0.851], ["2024-02-28", 0.858], ["2024-03-06", 0.885], ["2024-03-13", 0.897], ["2024-03-20", 0.899], ["2024-03-27", 0.875], ["2024-04-03", 0.898], ["2024-04-12", 0.88], ["2024-04-19", 0.895], ["2024-04-26", 0.902], ["2024-05-08", 0.933], ["2024-05-15", 0.932], ["2024-05-22", 0.921], ["2024-05-29", 0.905], ["2024-06-05", 0.891], ["2024-06-13", 0.875], ["2024-06-20", 0.849], ["2024-06-27", 0.83], ["2024-07-04", 0.796], ["2024-07-11", 0.813], ["2024-07-18", 0.817], ["2024-07-25", 0.775], ["2024-08-01", 0.784], ["2024-08-08", 0.782], ["2024-08-15", 0.774], ["2024-08-22", 0.755], ["2024-08-29", 0.747], ["2024-09-05", 0.756], ["2024-09-12", 0.721], ["2024-09-23", 0.729], ["2024-09-30", 0.948], ["2024-10-14", 0.907], ["2024-10-21", 0.903], ["2024-10-28", 0.912], ["2024-11-04", 0.896], ["2024-11-11", 0.955], ["2024-11-18", 0.902], ["2024-11-25", 0.889], ["2024-12-02", 0.924], ["2024-12-09", 0.915], ["2024-12-16", 0.918], ["2024-12-23", 0.91], ["2024-12-30", 0.925], ["2025-01-07", 0.88], ["2025-01-14", 0.89], ["2025-01-21", 0.898], ["2025-02-05", 0.899], ["2025-02-12", 0.914], ["2025-02-19", 0.901], ["2025-02-26", 0.895], ["2025-03-05", 0.895], ["2025-03-12", 0.905], ["2025-03-19", 0.919], ["2025-03-26", 0.91], ["2025-04-02", 0.917], ["2025-04-10", 0.88], ["2025-04-17", 0.889], ["2025-04-24", 0.893], ["2025-05-06", 0.891], ["2025-05-13", 0.903], ["2025-05-20", 0.916], ["2025-05-27", 0.909], ["2025-06-04", 0.923], ["2025-06-11", 0.938], ["2025-06-18", 0.914], ["2025-06-25", 0.936], ["2025-07-02", 0.942], ["2025-07-09", 0.955], ["2025-07-16", 0.971], ["2025-07-23", 0.997], ["2025-07-30", 1.015], ["2025-08-06", 1.026], ["2025-08-13", 1.042], ["2025-08-20", 1.074], ["2025-08-27", 1.098], ["2025-09-03", 1.088], ["2025-09-10", 1.092], ["2025-09-17", 1.12], ["2025-09-24", 1.118], ["2025-10-09", 1.127], ["2025-10-16", 1.092], ["2025-10-23", 1.082], ["2025-10-30", 1.079], ["2025-11-06", 1.065], ["2025-11-13", 1.058], ["2025-11-20", 1.022], ["2025-11-27", 1.016], ["2025-12-04", 1.013], ["2025-12-11", 1.008], ["2025-12-18", 1.01], ["2025-12-25", 1.032], ["2026-01-05", 1.053], ["2026-01-12", 1.087], ["2026-01-19", 1.098], ["2026-01-26", 1.11], ["2026-02-02", 1.081], ["2026-02-09", 1.123], ["2026-02-24", 1.109], ["2026-03-03", 1.083], ["2026-03-10", 1.095], ["2026-03-17", 1.083], ["2026-03-24", 1.049], ["2026-03-31", 1.054], ["2026-04-08", 1.082], ["2026-04-15", 1.089], ["2026-04-22", 1.115], ["2026-04-29", 1.139], ["2026-05-11", 1.168], ["2026-05-18", 1.12], ["2026-05-25", 1.12], ["2026-06-01", 1.073], ["2026-06-08", 1.047], ["2026-06-15", 1.084], ["2026-06-23", 1.074], ["2026-06-30", 1.084], ["2026-07-07", 1.082], ["2026-07-14", 1.078], ["2026-07-21", 1.093], ["2026-07-28", 1.081], ["2026-08-04", 1.116], ["2026-08-11", 1.15], ["2026-08-18", 1.152], ["2026-08-25", 1.128], ["2026-09-01", 1.136]], _hf, ensure_ascii=False)

# ================= 图表 =================
def nav_series():
    """读净值历史序列（[[date, close], ...]），画走势线"""
    seq = json.load(open(HIST, encoding='utf-8'))
    return seq

def nav_svg():
    """净值走势折线图（含 MA20 简化：直接用序列 + 当前值标注）"""
    seq = nav_series()
    W, H = 880, 260
    pad_l, pad_r, pad_t, pad_b = 52, 16, 24, 28
    closes = [x[1] for x in seq]
    cur = closes[-1]
    lo, hi = min(closes), max(closes)
    pad = (hi - lo) * 0.08 or 0.01
    lo -= pad; hi += pad
    span = hi - lo
    def X(i): return pad_l + i / (len(seq) - 1) * (W - pad_l - pad_r)
    def Y(v): return pad_t + (1 - (v - lo) / span) * (H - pad_t - pad_b)
    parts = []
    for g in [0.25, 0.5, 0.75]:
        y = pad_t + g * (H - pad_t - pad_b)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{W-pad_r}" y2="{y:.1f}" stroke="#eef0f3" stroke-width="1"/>')
    pts = " ".join(f"{X(i):.1f},{Y(c):.1f}" for i, (_, c) in enumerate(seq))
    area = f"{pad_l},{H-pad_b} " + pts + f" {W-pad_r},{H-pad_b}"
    parts.append(f'<polygon points="{area}" fill="url(#gradNav)"/>')
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#1f3a93" stroke-width="1.8"/>')
    parts.append(f'<circle cx="{X(len(seq)-1):.1f}" cy="{Y(cur):.1f}" r="4.5" fill="#e5484d" stroke="#fff" stroke-width="2"/>')
    parts.append(f'<text x="{pad_l}" y="14" font-size="12" font-weight="700" fill="#1f3a93">场内收盘价 {cur:.3f}（{DATE}）</text>')
    n = len(seq)
    for idx, lab in [(0, seq[0][0]), (n//2, seq[n//2][0]), (n-1, seq[-1][0])]:
        parts.append(f'<text x="{X(idx):.1f}" y="{H-8}" text-anchor="middle" font-size="10.5" fill="#9aa1ad">{lab}</text>')
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="净值走势">
      <defs>
        <linearGradient id="gradNav" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#1f3a93" stop-opacity="0.13"/><stop offset="100%" stop-color="#1f3a93" stop-opacity="0"/>
        </linearGradient>
      </defs>
      {''.join(parts)}
    </svg>'''

def perc_bar(kind):
    """指数估值分位判定条 v2：标题独立顶行，三分位标签垂直分行 + leader 虚线指引，杜绝文字重叠（v1 曾把标题与 10年标签共用 y=14 撞车、5年标签压圆点）"""
    W, H = 880, 128
    pad_l, pad_r = 20, 14
    key = "pe" if kind == "pe" else "pb"
    p10 = IDX["p10"][key]; p5 = IDX["p5"][key]; p3 = IDX["p3"][key]
    cur = IDX[key]
    xw = W - pad_l - pad_r
    def X(p): return pad_l + p / 100 * xw
    bar_y, bar_h = 30, 16
    parts = [f'<rect x="{X(0):.1f}" y="{bar_y}" width="{X(50)-X(0):.1f}" height="{bar_h}" rx="3" fill="#2fa36b" opacity="0.22"/>',
             f'<rect x="{X(50):.1f}" y="{bar_y}" width="{X(80)-X(50):.1f}" height="{bar_h}" rx="3" fill="#c9a227" opacity="0.28"/>',
             f'<rect x="{X(80):.1f}" y="{bar_y}" width="{X(100)-X(80):.1f}" height="{bar_h}" rx="3" fill="#e5484d" opacity="0.28"/>']
    # 标题：独立顶行（x=pad_l 起），不与任何标签共用 y
    parts.append(f'<text x="{pad_l}" y="13" font-size="12" font-weight="700" fill="#1f3a93">当前 {"PE" if kind=="pe" else "PB"} {cur}（{IDX["base_date"]} 公开口径）</text>')
    # 两端横轴注释（左端 start / 右端 end 对齐，避免溢出 viewBox）
    ann_y = bar_y + bar_h + 14
    parts.append(f'<text x="{X(0):.1f}" y="{ann_y}" text-anchor="start" font-size="10" fill="#9aa1ad">0% 便宜</text>')
    parts.append(f'<text x="{X(100):.1f}" y="{ann_y}" text-anchor="end" font-size="10" fill="#9aa1ad">100% 贵</text>')
    # 圆点 + 三分位标签：每标签占一条独立水平行（垂直错开 20px），leader 虚线从条下缘引到文字——分位点再接近也不重叠
    marks = [("10年", p10, "#e5484d"), ("5年", p5, "#c9a227"), ("3年", p3, "#2f56c9")]
    y0 = ann_y + 16
    step = 20
    for i, (lab, p, color) in enumerate(marks):
        cx, line_y = X(p), y0 + i * step
        parts.append(f'<circle cx="{cx:.1f}" cy="{bar_y + bar_h / 2:.1f}" r="4.5" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        if 0.5 <= p <= 99.5:
            parts.append(f'<line x1="{cx:.1f}" y1="{bar_y + bar_h / 2 + 4:.1f}" x2="{cx:.1f}" y2="{line_y - 9}" stroke="{color}" stroke-width="1" stroke-dasharray="3,3" opacity="0.5"/>')
        parts.append(f'<text x="{cx:.1f}" y="{line_y}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{color}">{lab} {p:.0f}%</text>')
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{"PE" if kind=="pe" else "PB"} 分位判定条">{''.join(parts)}</svg>'''

def ret_rows():
    """区间收益表行：数值列与表头一致右对齐（v1 曾漏 text-align 导致列内左对齐、与右对齐表头错位）"""
    rows = ""
    for k, v in RET:
        rows += (f'<tr><td>{k}</td><td class="num" '
                 f'style="text-align:right;font-weight:800;color:var(--{"red" if v > 0 else "green"})">{v:+.2f}%</td></tr>')
    return rows

def ret_note():
    """区间收益表下方说明：数值从 RET 动态拼接（v1 曾硬编码 '+9.82%/+23.77%'，与表内数据同源防不一致）"""
    m = dict(RET)
    s1 = f"{m['近1年']:+.2f}%" if "近1年" in m else "[MISSING]"
    s2 = f"{m['2025初至今']:+.2f}%" if "2025初至今" in m else "[MISSING]"
    return (f'<div style="margin-top:8px;font-size:12px;color:var(--ink-2)">'
            f'近1年 {s1} / 2025 初至今 {s2}——红利质量在 2025-2026 跑赢多数纯红利（高 ROE 成分进攻性）。</div>')

def kv_rows_snap():
    kv = [("开盘", f"{SNAP['open']:.3f}"), ("最高", f"{SNAP['high']:.3f}"), ("最低", f"{SNAP['low']:.3f}"), ("昨收", f"{SNAP['prev']:.3f}"),
          ("成交量", SNAP["vol"]), ("成交额", SNAP["amount"]), ("换手率", f"{SNAP['turnover']:.2f}%"),
          ("基金规模", SNAP["scale"]), ("综合费率", SNAP["rate"]), ("单位净值", f"{SNAP['nav']:.4f}"),
          ("估算溢价", f"+{SNAP['premium']:.2f}% [ASSUMED]"), ("成立日期", SNAP["estab"])]
    out = []
    for k, v in kv:
        out.append(f'<div class="kv"><span class="k">{k}</span><span class="num" style="font-weight:600">{v}</span></div>')
    return "".join(out)

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
<title>ETF估值仪表盘_{NAME}_{DATE}</title>
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
  .kv { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0; font-size:13px; border-bottom:1px dashed #f0f1f4; }
  .kv:last-child { border-bottom:none; }
  .kv .k { color:var(--ink-2); }
  .src-banner { margin-top:10px; padding:9px 13px; border-radius:10px; background:#fdf3ec; border:1px solid #f0d5c2; font-size:12px; color:#9a5b21; line-height:1.7; }
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
        <span class="pill brand">__IDX_ICON__ 跟踪 __IDX_NAME__（__IDX_CODE__）</span>
        <span class="pill gold">__SECTOR__</span>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v num up">¥__PX__</div><div class="k">最新价 (__CHG__%)</div></div>
      <div class="kpi"><div class="v num gd">__IDX_PE__</div><div class="k">指数 PE_TTM</div></div>
      <div class="kpi"><div class="v num gd">__DY__%</div><div class="k">股息率(近1年)</div></div>
      <div class="kpi"><div class="v num">__VERDICT__</div><div class="k">指数 10年分位 __PERC_KPI__</div></div>
    </div>
  </div>

  <!-- 01 估值判定 -->
  <div class="sec"><h2><span class="no">01</span>估值判定</h2><span class="hint">指数估值分位 + 股息率利差 + 成分结构</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      __VERDICT_BADGE__
      <b style="font-size:15px">__VERDICT__</b>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
  </div>

  <!-- 02 跟踪指数估值分位 -->
  <div class="sec"><h2><span class="no">02</span>跟踪指数估值分位</h2><span class="hint">__IDX_NAME__ · 公开指数估值口径</span></div>
  <div class="card">
    <h3>PE(TTM) 历史分位 <span class="unit">10年/5年/3年窗口</span></h3>
    __PERC_BAR_PE__
    <div class="insight">__PE_NOTE__</div>
  </div>
  <div class="card" style="margin-top:14px">
    <h3>PB(MRQ) 历史分位 <span class="unit">10年/5年/3年窗口</span></h3>
    __PERC_BAR_PB__
    <div class="insight">__PB_NOTE__</div>
  </div>
  <div class="src-banner">⚠️ 同花顺数据不含 ETF/指数估值接口（valuation 仅 A 股个股，ETF 报 FUYAO_3001）——本区 PE/PB 及分位为<u>公开指数估值源</u>数据：主源 __IDX_SRC__；辅助源 __IDX_SRC2__；__IDX_SRC3__。多源数值差异属时点/口径不同，估值判断请以页脚完整口径为准。</div>

  <!-- 03 股息率利差 -->
  <div class="sec"><h2><span class="no">03</span>股息率利差</h2><span class="hint">红利资产 vs 债券的安全垫</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:26px;flex-wrap:wrap;padding:4px 2px">
      <div style="text-align:center"><div class="num" style="font-size:26px;font-weight:800;color:var(--red)">__DY__%</div><div style="font-size:11.5px;color:var(--ink-3);margin-top:2px">指数股息率（近1年）</div></div>
      <div style="font-size:20px;color:var(--ink-3)">−</div>
      <div style="text-align:center"><div class="num" style="font-size:26px;font-weight:800;color:var(--brand)">__BOND10__%</div><div style="font-size:11.5px;color:var(--ink-3);margin-top:2px">10年期国债收益率</div></div>
      <div style="font-size:20px;color:var(--ink-3)">=</div>
      <div style="text-align:center"><div class="num" style="font-size:26px;font-weight:800;color:var(--gold)">__SPREAD__pct</div><div style="font-size:11.5px;color:var(--ink-3);margin-top:2px">股息率利差（安全垫）</div></div>
    </div>
    <div class="insight">__DIV_NOTE__</div>
  </div>

  <!-- 04 ETF 交易面 -->
  <div class="sec"><h2><span class="no">04</span>ETF 交易面与档案</h2><span class="hint">fund.snapshot + fund.profile · hithink 数据</span></div>
  <div class="grid-2">
    <div class="card"><h3>交易明细 <span class="unit">__DATE__ 收盘</span></h3>__KV_SNAP__</div>
    <div class="card"><h3>区间收益 <span class="unit">场内收盘价口径</span></h3>
      <table><tr><th>区间</th><th style="text-align:right">涨跌幅</th></tr>__RET_ROWS__</table>
      __RET_NOTE__
    </div>
  </div>
  <div class="card" style="margin-top:14px"><h3>净值走势 <span class="unit">__NAV_RANGE__ · 场内收盘价</span></h3>__NAV_SVG__
    <div style="margin-top:8px;font-size:12px;color:var(--ink-2)">区间收益与走势仅供估值参考的"价格位置"视角——贵不贵的判断以 02/03 区指数估值为准。</div>
  </div>

  <!-- 05 风险提示 -->
  <div class="sec"><h2><span class="no">05</span>风险提示</h2><span class="hint">高分位回撤 / 数据口径 / 拥挤度</span></div>
  <div class="card">__RISK_ROWS__</div>

  <div class="note">__NOTE__</div>
</div>
</body>
</html>'''

# ================= 组装 =================
NAV_RANGE = "2024-01 ~ 2026-09 · 648 个交易日" if os.path.exists(HIST) else "序列文件缺失 [MISSING]"
html = (TPL
        .replace("__NAME__", CFG["name"]).replace("__CODE__", CFG["code"])
        .replace("__SECTOR__", CFG["sector"])
        .replace("__IDX_NAME__", CFG["idx_name"]).replace("__IDX_CODE__", CFG["idx_code"])
        .replace("__IDX_ICON__", CFG["idx_icon"])
        .replace("__DATE__", DATE).replace("__WEEKDAY__", WEEKDAY)
        .replace("__PX__", f"{CFG['px']:.3f}").replace("__CHG__", f"{CFG['chg_pct']:+.2f}")
        .replace("__IDX_PE__", f"{IDX['pe']:.1f}").replace("__DY__", f"{CFG['dy']:.2f}")
        .replace("__BOND10__", f"{DIV['bond10']:.2f}").replace("__SPREAD__", f"{DIV['spread']:.2f}")
        .replace("__VERDICT__", CFG["verdict"]).replace("__VERDICT_BADGE__", verdict_badge())
        .replace("__VERDICT_NOTE__", CFG["verdict_note"])
        .replace("__PERC_KPI__", f"{IDX['p10']['pe']:.1f}%")
        .replace("__SUMMARY_ROWS__", summary_rows())
        .replace("__PERC_BAR_PE__", perc_bar("pe")).replace("__PERC_BAR_PB__", perc_bar("pb"))
        .replace("__PE_NOTE__", PE_NOTE).replace("__PB_NOTE__", PB_NOTE).replace("__DIV_NOTE__", DIV_NOTE)
        .replace("__KV_SNAP__", kv_rows_snap()).replace("__RET_ROWS__", ret_rows()).replace("__RET_NOTE__", ret_note())
        .replace("__NAV_SVG__", nav_svg()).replace("__NAV_RANGE__", NAV_RANGE)
        .replace("__IDX_SRC__", IDX["src"]).replace("__IDX_SRC2__", IDX["src2"]).replace("__IDX_SRC3__", IDX["src3"])
        .replace("__RISK_ROWS__", risk_rows())
        .replace("{NAME}", CFG["name"]).replace("{DATE}", DATE.replace("-", ""))
        .replace("__NOTE__", NOTE))

out_path = os.path.join(BASE, f"ETF估值仪表盘_{CFG['name']}_{DATE.replace('-', '')}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {out_path} | size: {len(html.encode('utf-8'))} bytes")
