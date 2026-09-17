# -*- coding: utf-8 -*-
"""A股 ETF 组合风险管理 HTML 生成器 v1.0（模板）
【模板使用说明】回答"我的持仓风险集中吗？"——相关性/回撤/仓位集中度/分散建议：
①hithink CLI：`fund history` 拉组合内各 ETF 同期日线（远端结构 data.item[] + date_ms/close_price）
+ `index history` 拉候选分散资产（沪深300 000300.SH/贵金属板块 881169.TI/红利指数 000015.SH）
②计算：各自年化收益/波动、日收益率相关系数（组合内部 + 组合 vs 候选资产）、最大回撤（含区间）、50/50 组合净值回测
③分散模拟：组合 × 红利/黄金 不同权重（归一化净值加权，注意不同量纲必须先各自归一化到 1 再加权！）
④替换 BASE/DATE 与数据区（CFG[kpis]/ASSETS/CORR/DIAG/MONTHLY/DIVERSIFY/SUMMARY/NOTE）⑤运行 → `组合风险管理_{YYYYMMDD}.html`
数据坑：ETF 历史与指数点位量纲不同（0.87 vs 2500）→ 加权组合必须先归一化，否则收益被点位淹没；
fund history 为远端结构 data.item[]+date_ms/close_price；相关性>0.7 高/0.4-0.7 中/0-0.4 低/<0 负相关；
模拟为历史窗口回测 [MODEL]，不代表未来
风格：与情绪扫描一致 —— 浅色金融仪表盘、深蓝#1f3a93+金#c9a227、红涨绿跌、区块编号01-NN、insight金色结论条
"""
import os

# ⚠️ 模板默认输出目录 = 本机开发工作区。分发/换环境：设置环境变量 THS_WORKSPACE 覆盖，或直接改本行。
BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-08-21"
WEEKDAY = "周五"

# ================= 数据 =================
CFG = {
    "out_tag": "组合561380+512480",
    "name": "半仓 561380（电网设备）+ 半仓 512480（半导体）",
    "verdict": "高集中 · 中高相关", "verdict_short": "风险",
    "verdict_note": ("组合近 1 年收益 +83%（年化 81%）但波动 39.3%、最大回撤 -32%——名义两只 ETF 分散，实质同为「AI 算力链」高 beta 成长："
                     "内部相关系数 0.545、与沪深300 相关 0.829（纯 A 股 beta 无对冲）、波动是宽基 2.2 倍。分散建议：加入红利（相关性 -0.149）构建哑铃。"),
    "kpis": [("0.545", "组合内部相关系数", "gold"), ("39.3%", "组合年化波动", "up"),
             ("-32.0%", "最大回撤", "dn"), ("0.829", "与沪深300相关", "up")],
}

# 窗口说明
WINDOW = "2025-08-01 ~ 2026-08-21 · 256 个交易日"

# 各资产指标：(名称, 代码, 区间收益%, 年化%, 年化波动%, 最大回撤%, 回撤区间)
ASSETS = [
    ("561380 电网设备ETF", "561380.SH", 68.2, 66.8, 36.7, -29.6, "2026-06-22~07-17"),
    ("512480 半导体ETF", "512480.SH", 95.5, 93.5, 49.5, -38.7, "2026-06-30~08-03"),
    ("组合 50/50", "561380+512480", 83.0, 81.3, 39.3, -32.0, "2026-06-30~08-03"),
]

# 相关性：(标签A, 标签B, 相关系数, 解读)
CORR = [
    ("组合", "沪深300", 0.829, "高 · 纯A股beta，无对冲", "high"),
    ("561380", "512480", 0.545, "中高 · 同属AI算力链（海缆互联+半导体核心）", "mid"),
    ("组合", "贵金属板块", 0.371, "低 · 黄金有分散价值", "low"),
    ("组合", "红利指数", -0.149, "负相关 · 最佳分散工具", "neg"),
]
CORR_NOTE = "💡 组合内部 0.545 中高相关是「名义分散」：561380 重仓海缆/光纤（AI 算力互联）、512480 重仓半导体（算力核心）——本质都是 AI 算力链，2026-07 双双回撤（组合 -32%）。与沪深300 相关 0.829 说明组合只是「高波动版宽基」；真正有分散价值的是红利（-0.149 负相关）与贵金属（0.371）。"

# 集中度诊断
DIAG = [
    ("行业集中", "561380=电网设备（海缆/光通信/输变电）+ 512480=半导体——两者交集是「AI 算力链」，行业实质未分散"),
    ("风格集中", "两只 ETF 均为高 beta 成长（波动 36.7%/49.5%），无低波/价值/防御对冲——风格单一"),
    ("波动水平", "组合年化波动 39.3% = 沪深300（18.1%）的 2.2 倍——高波动要求高回撤承受力"),
    ("回撤风险", "组合最大回撤 -32%（2026-06-30~08-03），单月 2026-07 曾 -29.6%——极端行情下净值回撤近 1/3"),
    ("对冲缺失", "与沪深300 相关 0.829 = 纯 A 股 beta 组合，无债券/黄金/红利等对冲资产"),
]

# 月度收益（组合 50/50）：(月份, 收益%)
MONTHLY = [
    ("2025-08", 27.7), ("2025-09", 11.2), ("2025-10", -2.6), ("2025-11", -3.5),
    ("2025-12", 6.5), ("2026-01", 15.7), ("2026-02", 5.6), ("2026-03", -11.8),
    ("2026-04", 16.5), ("2026-05", 12.5), ("2026-06", 22.9), ("2026-07", -29.6),
    ("2026-08", 5.4),
]

# 分散模拟：(配置名, 区间收益%, 年化波动%, 最大回撤%, 说明)
DIVERSIFY = [
    ("原组合 50/50", 83.0, 39.3, -32.0, "基准 · 高收益高波动"),
    ("70组合+30红利", 59.4, 30.4, -25.2, "稳健哑铃 · 波动降 9pct 回撤收窄 7pct"),
    ("60组合+40红利", 51.9, 27.3, -22.5, "均衡 · 波动降至宽基 1.5 倍"),
    ("80组合+20黄金", 85.3, 37.1, -26.2, "收益增强 · 回撤对冲，波动略降"),
    ("70组合+20红利+10黄金", 63.2, 29.8, -23.9, "哑铃+黄金 · 兼顾收益与稳健"),
]
DIVERSIFY_NOTE = "💡 模拟显示：红利是「降波动」主力（相关性 -0.149，加 30% 波动 -9pct、回撤 -7pct，代价是收益弹性）；黄金是「收益增强+回撤对冲」（近 1 年 +99% 但波动 55.8% 自身偏高，对组合降波有限）。推荐 70组合+30红利（哑铃）或 70组合+20红利+10黄金（增强版）——用 30% 仓位换一半回撤，性价比最高。"
DIVERSIFY_RISK = [
    "模拟为近 1 年历史窗口回测 [MODEL]，红利/黄金的分散效果随市场环境变化（2015 年股灾时红利也大跌）",
    "红利指数近 1 年波动 15.6% 但 2026-03 也回撤 -15.4%——分散是降低而非消除风险",
    "贵金属板块波动 55.8% 高于组合，加黄金需承受其自身高波动（2026-01~07 曾回撤 -51.8%）",
    "加红利/黄金会摊薄组合收益弹性（70组合+30红利 收益 +83%→+59%），需在收益与稳健间取舍",
    "单一 ETF 组合仅 2 个标的，再平衡依赖主观判断；规模超 200 亿的 ETF 需关注折溢价与跟踪误差",
]

SUMMARY = [
    ("结论", "组合收益亮眼但风险集中：+83% 收益 / 39.3% 波动 / -32% 回撤 / 内部相关 0.545——名义两只 ETF，实质单押「AI 算力链」，波动是宽基 2.2 倍。"),
    ("相关性", "内部 0.545（海缆互联+半导体核心同属算力链）· 与沪深300 0.829（纯 beta 无对冲）· 与红利 -0.149（负相关=最佳分散工具）"),
    ("集中度", "行业（算力链）+风格（高 beta 成长）双集中——无低波/价值/防御对冲，极端行情净值回撤近 1/3"),
    ("分散方案", "70组合+30红利：波动 39.3%→30.4%（-9pct）、回撤 -32%→-25.2%，收益 83%→59%——用 30% 仓位换一半回撤"),
    ("数据含义", "高相关≠高收益必然：组合的高收益来自 AI 算力 beta，0.545 相关意味着两者回调时几乎同步，分散收益有限"),
    ("投资指导", "若为长期持有：建议改「哑铃」配置（60-70% 组合 + 30-40% 红利，可加 10% 黄金）；若为趋势交易：保持但严格止损（-15% 触发）；单一科技 ETF 组合不宜满仓"),
]

NOTE = ("数据来源：同花顺金融数据（hithink-finance v0.1.5，fund history 日线 + index history 沪深300/贵金属板块/红利指数）；"
        "窗口=2025-08-01~2026-08-21（256 交易日）；年化收益/波动按 252 交易日换算；相关系数基于日收益率；最大回撤为收盘价口径；"
        "分散配置模拟为历史窗口回测 [MODEL]，归一化净值加权（561380+512480 各 50% 为组合基准），不代表未来表现；"
        "风险诊断与分散建议为模型综合判断（模型输出）。仅供研究参考，不构成个人投资建议。")

# ---- 文本/口径占位（平台可覆写；默认值 = 本报告原值，保证 skill 单独运行字节一致）----
INSIGHT_ASSETS = '💡 组合 50/50 收益 +83% 处两者之间，但波动 39.3% 更接近高波动的半导体（49.5%）——最大回撤 -32% 由两者同步回调造成（2026-07 单月 -29.6%）：高收益来自高 beta，回撤时几乎无缓冲。'
CORR_R1 = '<b class="num" style="color:var(--gold)">0.545 中高</b>——海缆互联+半导体核心同属 AI 算力链，回调同步'
CORR_R2 = '<b class="num" style="color:var(--red)">0.829 高</b>——纯 A 股 beta 组合，无对冲资产'
CORR_R3 = '<b class="num" style="color:var(--green)">红利 -0.149</b>·<b class="num" style="color:var(--brand)">贵金属 0.371</b>——有真实分散价值'
CORR_R4 = '<b>两只 ETF「名义分散、实质集中」——分散需跨资产，而非跨同链标的</b>'
INSIGHT_MONTHLY = '💡 月度收益两极分化：2025-08 +27.7% / 2026-06 +22.9% vs 2026-07 -29.6%——单月回撤吃掉近 3 个月涨幅，「高 beta 双刃剑」。'
ADV_SAFE = '<b>60 组合 + 40 红利：波动 27.3% / 回撤 -22.5%——长期持有者首选</b>'
ADV_BAL = '<b>70 组合 + 30 红利：波动 30.4% / 回撤 -25.2%——收益与稳健平衡（推荐）</b>'
ADV_AGG = '<b>80 组合 + 20 黄金：收益 +85% / 回撤 -26.2%——不愿牺牲收益者的回撤对冲</b>'
ADV_REBAL = '<b>季度再平衡（偏离 5pct 触发）；单只科技 ETF 单一持仓不宜超总仓位 40%</b>'
MONTHLY_TITLE = '组合月度收益 · 2026-07 单月 -29.6%（回撤主因）'

# ================= 渲染 =================
def asset_rows():
    rows = []
    for name, code, ret, ann, vol, dd, dr in ASSETS:
        hl = ' style="background:#fdf9ec"' if "组合" in name else ""
        rc = "var(--red)" if ret >= 0 else "var(--green)"
        dc = "var(--red)" if dd < -30 else "var(--gold)"
        rows.append(f'<tr{hl}><td><b>{name}</b></td>'
                    f'<td class="num" style="color:{rc};font-weight:800">{ret:+.1f}%</td>'
                    f'<td class="num">{ann:+.1f}%</td>'
                    f'<td class="num" style="color:var(--ink-2)">{vol:.1f}%</td>'
                    f'<td class="num" style="color:{dc};font-weight:700">{dd:.1f}%</td>'
                    f'<td style="font-size:11.5px;color:var(--ink-3)">{dr}</td></tr>')
    return "".join(rows)

def corr_svg():
    """相关性条形图：按相关性强弱着色"""
    W, H = 460, 260
    pad_l, pad_t, row_h, gap = 130, 26, 44, 6
    parts = []
    for i, (a, b, c, note, level) in enumerate(CORR):
        y = pad_t + i * (row_h + gap)
        # 相关性 -0.2 ~ 1.0 映射
        x0 = pad_l + (0 - (-0.2)) / 1.2 * (W - pad_l - 40)
        w = abs(c) / 1.2 * (W - pad_l - 40)
        color = {"high": "#e5484d", "mid": "#e8a13a", "low": "#2f56c9", "neg": "#2fa36b"}[level]
        xx = x0 if c >= 0 else x0 - w
        parts.append(f'<text x="{pad_l-8}" y="{y+row_h/2+4:.1f}" text-anchor="end" font-size="12" fill="#5b6470">{a} × {b}</text>')
        # 0 轴
        parts.append(f'<line x1="{x0:.1f}" y1="{y+2:.1f}" x2="{x0:.1f}" y2="{y+row_h-2:.1f}" stroke="#c9c4b8" stroke-width="1" stroke-dasharray="3 2"/>')
        parts.append(f'<rect x="{xx:.1f}" y="{y+6:.1f}" width="{max(w,5):.1f}" height="16" rx="5" fill="{color}" opacity="0.85"/>')
        parts.append(f'<text x="{xx+w+6 if c>=0 else xx-6:.1f}" y="{y+row_h/2+4:.1f}" font-size="12" font-weight="800" fill="{color}">{c:+.3f}</text>')
    # 图例
    parts.append(f'<text x="{pad_l}" y="{H-12}" font-size="10.5" fill="#9aa1ad">红=高相关(>0.7) 橙=中高(0.4~0.7) 蓝=低(0~0.4) 绿=负相关(&lt;0)</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="相关性矩阵">{"".join(parts)}</svg>'

def monthly_svg():
    """组合月度收益柱状图"""
    W, H = 460, 240
    pad_l, pad_t, pad_r = 46, 24, 16
    vals = [v for _, v in MONTHLY]
    vmax = max(max(vals), 30)
    vmin = min(min(vals), -30)
    span = vmax - vmin
    bw = (W - pad_l - pad_r) / len(MONTHLY)
    zero_y = pad_t + (vmax / span) * (H - pad_t - 30)
    parts = []
    parts.append(f'<line x1="{pad_l}" y1="{zero_y:.1f}" x2="{W-pad_r}" y2="{zero_y:.1f}" stroke="#c9a227" stroke-width="1.2" stroke-dasharray="4 3"/>')
    for i, (m, v) in enumerate(MONTHLY):
        x = pad_l + i * bw + bw * 0.18
        w = bw * 0.64
        y1 = zero_y
        y2 = zero_y - (v / span) * (H - pad_t - 30)
        c = "#e5484d" if v >= 0 else "#2fa36b"
        parts.append(f'<rect x="{x:.1f}" y="{min(y1,y2):.1f}" width="{w:.1f}" height="{abs(y2-y1):.1f}" rx="3" fill="{c}" opacity="0.85"/>')
        if i % 2 == 0:
            parts.append(f'<text x="{x+w/2:.1f}" y="{H-10}" text-anchor="middle" font-size="9.5" fill="#9aa1ad">{m[2:]}</text>')
    parts.append(f'<text x="{pad_l}" y="14" font-size="11.5" font-weight="700" fill="#1f3a93">{MONTHLY_TITLE}</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="组合月度收益">{"".join(parts)}</svg>'

def div_rows():
    rows = []
    for i, (name, ret, vol, dd, note) in enumerate(DIVERSIFY):
        hl = ' style="background:#fdf9ec"' if "70组合+30红利" in name or "哑铃" in note else ""
        if ret is None:
            rows.append(f'<tr{hl}><td><b>{name}</b></td>'
                        f'<td class="num" style="color:var(--ink-3)">--</td>'
                        f'<td class="num" style="color:var(--ink-3)">--</td>'
                        f'<td class="num" style="color:var(--ink-3)">--</td>'
                        f'<td style="font-size:11.5px;color:var(--ink-2)">{note}</td></tr>')
            continue
        rc = "var(--red)" if ret >= 0 else "var(--green)"
        rows.append(f'<tr{hl}><td><b>{name}</b></td>'
                    f'<td class="num" style="color:{rc};font-weight:800">{ret:+.1f}%</td>'
                    f'<td class="num" style="color:{"var(--green)" if vol < 35 else "var(--gold)"}">{vol:.1f}%</td>'
                    f'<td class="num" style="color:{"var(--red)" if dd < -30 else "var(--gold)"};font-weight:700">{dd:.1f}%</td>'
                    f'<td style="font-size:11.5px;color:var(--ink-2)">{note}</td></tr>')
    return "".join(rows)

def kv_rows(items):
    out = []
    n = len(items)
    for i, it in enumerate(items):
        bd = "border-bottom:1px dashed #f0f1f4;" if i < n - 1 else ""
        if isinstance(it, str):
            out.append(f'<div class="kv" style="padding:6px 0;{bd}font-size:12.5px;color:var(--ink-2)">{it}</div>')
        else:
            k, v = it
            out.append(f'<div class="kv" style="padding:6px 0;{bd}font-size:13px"><span style="color:var(--ink-2)">{k}</span><b>{v}</b></div>')
    return "".join(out)

def summary_rows():
    out = []
    for tag, desc in SUMMARY:
        cls = "sum-tag" if tag in ("结论",) else "sum-tag2"
        out.append(f'<div class="sum-row"><span class="{cls}">{tag}</span><span style="color:var(--ink-2)">—— {desc}</span></div>')
    return "".join(out)

def kpi_rows():
    out = []
    for v, k, cls in CFG["kpis"]:
        c = f" {cls}" if cls else ""
        out.append(f'<div class="kpi"><div class="v num{c}">{v}</div><div class="k">{k}</div></div>')
    return "".join(out)

# ================= 模板 =================
TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>组合风险管理___DATE_SHOW__</title>
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
  .hero .title{font-size:21px;font-weight:800;letter-spacing:.5px;line-height:1.4}
  .hero .tcode{font-size:13px;color:rgba(255,255,255,.65);font-weight:600;margin-left:8px}
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
    <div class="title">组合风险管理 <span class="tcode">我的持仓风险集中吗？</span></div>
    <div class="sub">
      <span class="pill gold">__WEEKDAY__ · __DATE__</span>
      <span class="pill brand">__NAME__</span>
      <span class="pill brand">窗口 · __WINDOW__</span>
    </div>
    <div class="kpis">__KPI_ROWS__</div>
  </div>

  <!-- 01 组合总览 -->
  <div class="sec"><h2><span class="no">01</span>组合总览</h2><span class="hint">风险诊断 · 模型输出</span></div>
  <div class="card">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px">
      <span class="vbadge">__VERDICT__</span>
      <span style="font-size:12.5px;color:var(--ink-2)">__VERDICT_NOTE__</span>
    </div>
    __SUMMARY_ROWS__
  </div>

  <!-- 02 风险指标 -->
  <div class="sec"><h2><span class="no">02</span>风险指标对比</h2><span class="hint">__WINDOW__ · 收盘价口径</span></div>
  <div class="card">
    <table>
      <tr><th>标的</th><th>区间收益</th><th>年化收益</th><th>年化波动</th><th>最大回撤</th><th>回撤区间</th></tr>
      __ASSET_ROWS__
    </table>
    <div class="insight">__INSIGHT_ASSETS__</div>
  </div>

  <!-- 03 相关性分析 -->
  <div class="sec"><h2><span class="no">03</span>相关性分析</h2><span class="hint">日收益率相关系数 · 近 1 年</span></div>
  <div class="grid-2">
    <div class="card" style="display:flex;align-items:center">__CORR_SVG__</div>
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:8px">相关结构解读</h3>
      <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">内部相关</span>__CORR_R1__</div>
      <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">市场相关</span>__CORR_R2__</div>
      <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">分散候选</span>__CORR_R3__</div>
      <div class="kv" style="padding:6px 0;font-size:13px"><span style="color:var(--ink-2)">分散结论</span>__CORR_R4__</div>
      <div class="insight">__CORR_NOTE__</div>
    </div>
  </div>

  <!-- 04 集中度诊断 -->
  <div class="sec"><h2><span class="no">04</span>集中度诊断</h2><span class="hint">行业 / 风格 / 波动 / 对冲</span></div>
  <div class="grid-2">
    <div class="card">
      <h3 style="font-size:14px;margin-bottom:8px">五维诊断</h3>
      __DIAG_ROWS__
    </div>
    <div class="card" style="display:flex;align-items:center;flex-direction:column">
      __MONTHLY_SVG__
      <div class="insight" style="width:100%">__INSIGHT_MONTHLY__</div>
    </div>
  </div>

  <!-- 05 分散建议 -->
  <div class="sec"><h2><span class="no">05</span>分散建议</h2><span class="hint">配置模拟 · 历史窗口回测 [MODEL]</span></div>
  <div class="card">
    <table>
      <tr><th>配置方案</th><th>区间收益</th><th>年化波动</th><th>最大回撤</th><th>说明</th></tr>
      __DIV_ROWS__
    </table>
    <div class="insight">__DIVERSIFY_NOTE__</div>
  </div>

  <!-- 06 操作建议与风险 -->
  <div class="sec"><h2><span class="no">06</span>操作建议与风险</h2><span class="hint">分散执行 · 模型输出</span></div>
  <div class="card">
    <h3 style="font-size:14px;margin-bottom:8px">操作建议（三档）</h3>
    <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">稳健档</span>__ADV_SAFE__</div>
    <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">均衡档</span>__ADV_BAL__</div>
    <div class="kv" style="padding:6px 0;border-bottom:1px dashed #f0f1f4;font-size:13px"><span style="color:var(--ink-2)">进攻档</span>__ADV_AGG__</div>
    <div class="kv" style="padding:6px 0;font-size:13px"><span style="color:var(--ink-2)">再平衡</span>__ADV_REBAL__</div>
    <h3 style="font-size:14px;margin:12px 0 8px">风险提示</h3>
    __DIV_RISK__
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
            .replace("__WINDOW__", WINDOW)
            .replace("__VERDICT__", CFG["verdict"])
            .replace("__VERDICT_NOTE__", CFG["verdict_note"])
            .replace("__KPI_ROWS__", kpi_rows())
            .replace("__SUMMARY_ROWS__", summary_rows())
            .replace("__ASSET_ROWS__", asset_rows())
            .replace("__CORR_SVG__", corr_svg())
            .replace("__CORR_NOTE__", CORR_NOTE)
            .replace("__DIAG_ROWS__", kv_rows(DIAG))
            .replace("__MONTHLY_SVG__", monthly_svg())
            .replace("__DIV_ROWS__", div_rows())
            .replace("__DIVERSIFY_NOTE__", DIVERSIFY_NOTE)
            .replace("__DIV_RISK__", kv_rows(DIVERSIFY_RISK))
                        .replace("__INSIGHT_ASSETS__", INSIGHT_ASSETS)
            .replace("__CORR_R1__", CORR_R1)
            .replace("__CORR_R2__", CORR_R2)
            .replace("__CORR_R3__", CORR_R3)
            .replace("__CORR_R4__", CORR_R4)
            .replace("__INSIGHT_MONTHLY__", INSIGHT_MONTHLY)
            .replace("__ADV_SAFE__", ADV_SAFE)
            .replace("__ADV_BAL__", ADV_BAL)
            .replace("__ADV_AGG__", ADV_AGG)
            .replace("__ADV_REBAL__", ADV_REBAL)
.replace("__NOTE__", NOTE))
    out_path = os.path.join(BASE, f"组合风险管理_{DATE.replace('-', '')}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("OK ->", out_path, "| size:", len(html.encode("utf-8")))

if __name__ == "__main__":
    main()
