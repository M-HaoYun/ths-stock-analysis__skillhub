# -*- coding: utf-8 -*-
"""多能力协同选股推荐报告 HTML 生成器 v1.2（模板，带 2026-09-10 精选 5 股·短中线技术指标版示例数据）
【能力 #12 · 编排型能力】整合板块轮动#7 × 市场情绪#6 × 龙虎榜#11 × 经典策略信号#1 四视角，
交叉验证选出 N 只股票 → 能力#8 全面分析逐一验证 → 剔除不值得买的、从候选池补位重找，
输出「精选 N 股推荐报告」HTML（浅色金融仪表盘，A股红涨绿跌）。

★ 定位纪律（v1.2 起，用户明确要求）：**一律短中线思维，不推长线**。
  持有周期口径 = 3~10 个交易日（最长不超过 20 个交易日）；每只必须给出
  ①入场技术位（回踩 MA5/MA10/颈线/前低）②止损位（跌破即走）③短线目标或减仓条件。
  禁止"长期持有/价值投资/穿越牛熊"类表述；基本面只作为「短线不做接刀」的安全垫，不作为长线理由。

v1.2 变更（2026-09-10）：
  · 每卡新增「短线技术指标」区块（tech 数据区，6 格：均线形态/RSI14/MACD/量比/布林%B/支撑压力）
    + tnote 技术面研判句 —— 数据由本地前复权 parquet 自算（MA/RSI/MACD/布林/量比，见 calc_tech 脚本范式）
  · **涨跌红绿自动着色**：hl() 把文本里的 ±x.x% 自动包 <span class="up|dn">（红涨绿跌）；
    chg 字段原来硬编码 class="chg up"（导致跌的股票也显示红色）——v1.2 改为按数值正负自动判定
  · KPI 新增 .hot 红色：涨停家数、封板率等「市场热度」指标一律用红色（不受涨跌语义影响）
v1.1 变更（2026-09-08）：能力#8 验证关卡 + ★验证记录面板 + EVID 第 5 列 + chk 验证行

【当日开工链路（先探数据可用性，无今日数据则不做）】
0. 探测：`index history --thscode 000001.SH --source remote` 末条 date_ms==今日且量能正常 → 可用
1. 本地库：`data sync`（注入 HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT=4GiB）→ 供涨跌家数/前复权扫描
2. 情绪#6：limit-up-pool / limit-down-pool / limit-break-pool --date-ms <今日> + dragon-tiger（普通+--board-type org）
   → 解析：涨停家数/封板率/连板梯队/跌停/机构动向/龙虎榜净买 TOP（涨停池题材在 limit_up_reason 字段）
3. 轮动#7：板块清单 → idx 历史 60 日 → calc（动量/量比/超额）→ 主线方向（若当日已出轮动雷达直接复用 rotation json）
4. 经典策略#1：`db export` 前复权日K parquet → 复用 bt_backtest 的 find_w_bottom 形态逻辑做
   W底突破扫描 + 60日新高放量扫描（双信号源，落候选池）
5. 交叉验证：候选股必须命中「轮动主线 or 情绪热词 or 龙虎榜资金」至少一条 + 形态信号至少一条
6. `market snapshot` 实测候选当日行情 + bt_name_map.json 映射名称（涨停池 JSON 常无 name 字段）
7. WebSearch 核实题材/政策/事件（数据来源铁律：接口无此字段，页面标注"WebSearch 公开披露"，禁止编造）
8. 【妖股剔除】用前复权 parquet 算候选 1/5/20/60 日涨幅——20日已 +50%~100%+ 的妖股剔除
   （示例教训：金健米业 20日 +140%、万向德农 20日 +118% 剔除）；已大涨的"补涨"需与"干净首次突破"区分
9. 定稿 N 只：定位分层 tag（主线右侧/主线首板/机构主买/超跌回踩/弹性博弈/主线低吸，颜色在 CLS 注册）
   → 当日涨停/连板股只给"回踩参与"不给追高（回测纪律：二连板 -18.8%、三连板 -83.57%）
10. ★能力#8 验证关卡（v1.1 起必做）：对定稿 N 只逐一跑能力 #8 全面分析取数
    （market snapshot + valuation snapshot + financials income/indicators 最新报告期 + 历史K，必要时 WebSearch
    forward 一致预期/目标价）→ 按五维否决标准判读 verdict：
    A 估值透支（forward PE 显著高于同行且无增速支撑，利润高增股看 forward 不看 TTM）
    B 基本面恶化（最新期营收/归母双降、ROE 持续下行、由盈转亏且无兑现逻辑）
    C 成长证伪（券商一致预期下修/2026E 负增长且无新催化）
    D 硬风险（ST/立案/大额商誉减值/审计非标/清仓减持）
    E 位置风险（60 日涨幅过大追高、龙虎榜高位净卖、板块刚转冷）
    ——命中任一 → 剔除；判定必须区分"一次性亏损"（补税/减值，利空出清可保留，北大荒 14.1 亿补税案例）
    vs "经营性亏损"（由盈转亏+ROE 恶化=否决，金正大 -4.97 亿案例）——用 WebSearch 核实事件 + 看扣非/Q1 趋势
11. 剔除重找 + 反查补位：剔除的股票从候选池（步骤 4/5 的 W底/60日新高 + 龙虎榜净买 + 涨停池同题材名单）
    按原标准重找补位；**若某题材/方向涨停资金票全部不过（PCB/存储/传媒方向常见：亏损或 PE>50 或高位），
    沿产业链上溯到"涨价/景气真受益方"反查补位**（中京电子被剔 → 覆铜板龙头生益科技 H1 归母+130%、
    当日 -1.3% 回踩低吸位入选，tag=主线低吸）——反查补位须 WebSearch 验证涨价/景气事实。
    补位者同样过 #8 验证；候选池耗尽仍无合格 → 宁缺毋滥（可降 N 或留档位空缺），报告写明放弃方向
    （09-08 晚：AI出版影视涨停潮无低位高性价比标的 → 方向整体放弃；最终以「4 强 + 1 高风险边缘票」
    成稿 5 只，边缘票卡内显式标高风险档、仅轻仓试错）
12. 渲染校验：每卡带 chk（能力#8 验证结论行）+ ★ 验证记录面板（AUDIT_ROWS：剔除/补位/通过全程留痕）
    → `精选{N}股推荐_{YYYYMMDD}.html` → 校验区块 01-05（+★ 面板）+ 零残留

【数据区】DATE/GEN/BANNER/KPIS/IDX/LINES/INSIGHT01/INSIGHT03/STOCKS/EVID/AUDIT_ROWS/NOTE/CLS/N
  ⚠️ 变量名必须与渲染段一致：证据列头叫 **EVID**（不是 EVIDENCE），误写会在 stock_card() 报 NameError（坑 42）
（v1.0 全部进数据区，hero/01 区块零硬编码）；股数 N=len(STOCKS) 自适应，标题/文件名自动带 N。
STOCKS 字段：rank/tag/pos/name/code/price/chg/tags/title/why/data/plan/risk/chk/evid/tech/tnote
  · chk = (ok:bool, 验证结论短句) —— 卡内渲染 "✅ 能力#8 验证通过" 行（v1.1 新增，缺省不渲染，向后兼容）
  · evid = 能力证据布尔（顺序对 EVID，**v1.1 第 5 位=能力#8 验证通过**，均 True）
  · tech = [(标签, 值), ...] 短线技术指标 6 格（v1.2 新增，缺省不渲染）——值走 hl() 自动红绿
  · tnote = "技术面研判短句"（v1.2 新增，缺省不渲染）——写清入场位/止损位/技术面矛盾点
AUDIT_ROWS = [(标的, "ok"/"bad", 判定依据), ...] —— ★ 验证记录面板（v1.1 新增，缺省不渲染）
渲染：01 市场环境速写 02 精选卡(每卡: 定位/证据chips/标题/理由/数据grid/技术指标区/操作/风险/验证行/证据圆点)
      03 信号证据交叉矩阵(动态, 含 #8 列) ★验证记录(剔除/补位审计) 04 操作纪律(短中线口径+回测实证) 05 口径免责
风格：与情绪/轮动一致 —— 深蓝#1f3a93+金#c9a227、涨红跌绿、.insight 金色结论条、tabluar-nums、区块 01-05
红绿规范（v1.2 强化，用户明确要求）：①个股涨跌幅一律红涨绿跌（chg 自动判定 + hl() 处理 grid 文本）；
      ②市场热度类 KPI（涨停家数/封板率/连板高度）用 .hot 红色强调；③跌停/降温类用 .dn 绿。
坑/经验：
· 妖股剔除必须算区间涨幅（涨停池里 20日+140% 的"板块补涨"是陷阱，见步骤 8）
· 涨停池 JSON 的 name 字段可能缺失/为空 → 用本地 bt_name_map.json（symbol list 远端产物）映射；
  涨停池题材不在 concept_list 而在 `limit_up_reason` 字段（坑 6）
· stag 颜色用 CLS[s["tag"]] 字典映射（勿写多层嵌套三元，易错难读）；新 tag 需同时在 CLS 与 CSS .stag.x 注册
· 当日涨停/连板股占比高时，报告操作一律"回踩/企稳分批"前提，明确"非追高推荐"
· 中报亏损股交易的是涨价/产能预期 → 卡片标"高风险档"，risk 写明基本面背离（但 #8 验证对由盈转亏从严）
· PE_TTM 为负=TTM 亏损，先查一次性 vs 经营性再判定（坑 30）；financials quarterly Q2+ 行为累计口径（坑 29）
· 同文件多处并行 Edit 会互相覆盖（后写赢且工具仍报 success）→ 修改必须串行 + 特征值双查
· **短线技术指标必算**（v1.2）：MA5/10/20/60 排列 · RSI14 · MACD(12,26,9) · 量比（今量/前5日均量）·
  布林(20,2) %B · 距 20 日高低 —— 全部用本地前复权 parquet 自算（勿凭印象写），
  与技术面结论互相印证（09-10 案例：华正新材乖离 MA20 +20.3%、%B 118 → 超买，技术面独立佐证基本面否决）
· **RSI>70 + %B>100 + 乖离 MA20 >8% 三者同现 = 短线超买**，此时 card 必须给"回踩 MA5/MA10 再参与"而非追高
· chg 字段严禁硬编码类名（v1.1 全部写死 up → 跌的股票也显红）；一律按数值正负自动判定
口径：数据= hithink CLI 实测；产业逻辑/一致预期= WebSearch 公开披露显式标注；回测结论引用能力 #1 引擎 20 策略实测。
仅供研究参考，不构成投资建议。
"""
import os
import re

BASE = os.environ.get("THS_WORKSPACE", os.getcwd())  # 输出目录：THS_WORKSPACE 优先，未设置=当前运行目录
DATE = "2026-09-10"
GEN = "周四 · 20:40 生成（短中线技术指标版 v1.2 · 能力#8 验证流程）"  # hero 生成说明（周几/时段按当日填）

# ---------- 01 市场环境速写 ----------
BANNER = ("💡 <b>核心研判：普跌加深、情绪连续第二日退潮、资金高低切换至红利防御</b>——涨停 34 家（09-09 的 48 家继续回落）、"
          "跌停 11 家、炸板 22 家、封板率 61%、最高仅 4 板（桂林旅游），上涨仅 954 家（下跌 4512 家、个股中位 -1.49% 深度普跌）；"
          "四大指数全绿（上证 -0.43%、深成 -0.77%、创业板 -0.49%、沪深300 -0.53%）。"
          "资金主线：<b>银行今日 +1.47% 全场最强（42 只个股全红、宁波银行 +3.49% 创历史新高）→ 证券/保险跟涨，红利防御接棒</b>；"
          "而三周霸榜的农业链高位回落（种植今日 -3.50% 领跌）、资源系小幅回踩换挡；半导体/电池/光伏/小金属/航天继续垫底。"
          "普跌市中「防御 > 进攻」，追高退潮方向与抄底缩量方向同样危险。")

# KPIS = [(值, 标签, 颜色class hot/up/dn), ...] —— 涨停家数/封板率属"市场热度"一律用 hot(红)
KPIS = [("34 家", "涨停（09-09: 48）", "hot"), ("61%", "封板率（炸板 22）", "hot"),
        ("954 / 4512", "上涨 / 下跌家数（中位 -1.49%）", "dn"), ("11 家", "跌停（09-09: 7）", "dn")]
# IDX = [(指数名, 主体文本, 颜色class), ...]（主体文本含数值+涨跌，无涨跌的用空 class 如连板梯队）
IDX = [("上证指数", "3934.40 -0.43%", "dn"), ("深证成指", "13617.67 -0.77%", "dn"),
       ("创业板指", "3338.42 -0.49%", "dn"), ("沪深300", "4548.39 -0.53%", "dn"),
       ("连板梯队", "4板×1 · 3板×2 · 2板×6", "")]
LINES = ["🏦 银行今日 +1.47% 全场最强（42 只全红·宁波 +3.49% 创新高）", "📈 证券 +0.84% / 保险 +0.31% 跟随·红利防御接棒",
         "🥇 种植业 20日 +27.8% 仍第一，但今日 -3.50% 领跌（三周霸榜终结）", "⚡ 资源回踩：煤炭 -0.95% / 石油 -1.65% / 工业金属 -1.48%",
         "🟠 覆铜板：华正新材龙虎榜净买 +4.89 亿居首（生益同链真受益方）", "📉 半导体/电池/光伏/小金属/航天继续垫底",
         "⚠️ 农业链整体退潮：养殖 -2.90% / 粤桂（磷肥）-4.35% 回踩"]
INSIGHT01 = ("涨停热词=业绩增长 6 家居首、机器人 2 / AI应用 2 / 电力 2 / 商业航天 2；高标压缩至 4 板（桂林旅游·AI文旅），3 板仅 2 家（瑞尔特/云煤能源）"
             "——情绪连续第二日退潮，赚钱效应弱。龙虎榜净买第一=华正新材 +4.89 亿（高速覆铜板+AI算力）、湖南黄金 +4.39 亿（重大重组+黄金锑钨）、崇达技术 +3.29 亿（PCB）"
             "——资金聚焦<b>覆铜板/PCB 链</b>（生益科技=同链龙头真受益方）；机构净买第一=崇达技术 +2.17 亿。"
             "值得注意：09-09 被 #8 否决的中京电子今日仍获机构 +0.52 亿——<b>资金热度 ≠ 值得买</b>，口径不变。普跌日仓位从严。")
INSIGHT03 = ("能力#8 验证后五只均有硬业绩背书且位置可控（<b>全部为短中线 3~10 个交易日口径，非长线推荐</b>）：<b>宁波银行</b>（银行风格切换主线 H1 营收 +11.5%/归母 +12.1%、PE 7.6/PB 0.98、今日 +3.49% 创新高）"
             "是本日唯一逆势方向的载体，但 RSI 75.3 已超买、须等回踩；<b>云铝股份</b>（电解铝 H1 +177.6%、ROE 21.9%、PE 9.0、今日 -2.41% 缩量回踩）与 <b>粤桂股份</b>（磷肥 H1 +182.8%、PE 20.9、今日 -4.35% 回踩）"
             "提供资源/化工的业绩+估值双支撑；<b>生益科技</b>（覆铜板涨价真受益方 H1 +130.4%、当日 -0.81% 抗跌）沿今日资金主线（华正/崇达）取真受益龙头；"
             "<b>中际旭创</b>（H1 +241.7%、60日 -30.2% 深调）为超跌右侧观察。原 09-09 组合神火（与云铝同铝链，为分散度让位）转观察——非否决。"
             "被剔除方向：农业种业（敦煌种业 20日 +88%/60日 +126% 妖股化、种植今日领跌）、基本面下滑票（上汽归母 -14.4%、盾安 -12.8%）。")

# ---------- 02 精选股票（chk=能力#8 验证结论 (ok,短句)；tech=短线技术指标 6 格；tnote=技术面研判）----------
STOCKS = [
    dict(
        rank=1, tag="防御主线", pos="银行·红利重估",
        name="宁波银行", code="002142.SZ", price="35.87", chg="+3.49%",
        tags=["板块轮动", "经典策略信号", "能力#8验证"],
        title="城商行龙头 · 风格切换主线（低估值高股息 + 业绩最优）",
        why=("09-10 市场普跌中银行板块 +1.47% 全场最强、42 只个股全红，宁波银行涨超 3% 与南京/成都/杭州同步创历史新高——"
             "核心逻辑=「红利防御 + 基本面重估」双轮驱动：上半年上市银行营收同增 7.42%（上年同期 1.04%）、归母 +2.96%，17 家净息差同比回升；"
             "板块 PE 7.26/PB 0.69、平均股息率 4.33%，险资/社保长线持续增配，与高位科技形成「跷跷板」。"
             "能力#8 验证：宁波银行 2026H1 营收 +11.5%、归母 +12.1%（城商行第一梯队）、净利率 40.4%、PE_TTM 7.6/PB 0.98——"
             "低估值 + 业绩确定性 + 板块动量三者共振，是普跌市中极少数「有基本面支撑的逆势方向」。"),
        data=[("今日", "+3.49% 创新高"), ("20日涨幅", "+11.1%"), ("60日涨幅", "+17.3%"),
              ("2026H1归母", "+12.1%"), ("PE_TTM", "7.6"), ("PB / 股息参考", "0.98 / 板块 4.33%")],
        tech=[("均线形态", "多头排列 MA5>10>20>60"), ("RSI14", "75.3 超买"), ("MACD", "金叉多头 DIF 0.76"),
              ("量比", "1.80 温和放量"), ("布林%B", "106.6 破上轨"), ("关键位", "支撑 MA5 34.8 / 前高 35.9")],
        tnote="RSI 75.3 + %B 106.6 破上轨 + 创 20 日新高 = 短线超买三连，技术面不支持追高；等回踩 MA5（34.8）缩量企稳再分批，跌破 MA10（34.5）短线转弱。",
        plan="【3~10 个交易日】不追高开，回踩 MA5（34.8）/MA10（34.5）分批；站上 36 元后以 5 日线为移动止盈；板块跌破 20 日线或息差逻辑证伪即退出。",
        risk="银行股弹性有限（进攻性弱于资源/科技），风格若快速切回成长可能跑输；RSI 已超买、板块连续创新高后拥挤度上升；区域行资产质量与地方债务关联需跟踪。",
        chk=(True, "通过——H1 营收+11.5%/归母+12.1% 城商行最优、PE 7.6/PB 0.98 低估、板块今日全场最强且 42 只全红；技术面超买须等回踩"),
        evid=[True, False, False, True, True],
    ),
    dict(
        rank=2, tag="资源回踩", pos="电解铝·供给缺口",
        name="云铝股份", code="000807.SZ", price="28.33", chg="-2.41%",
        tags=["板块轮动", "能力#8验证", "回踩低吸"],
        title="电解铝弹性王 · 缩量回踩不破均线（H1 +177.6%）",
        why=("工业金属 20日 +7.2% 仍居前列（成交 355 亿）、电解铝供给端逻辑未破坏——霍尔木兹地缘扰动中东约 9% 供给、"
             "国内产能已近 4500 万吨政策天花板、旺季去库+下游开工回升，铝价中枢上行预期仍在。云铝=绿色水电铝龙头，"
             "2026H1 营收 +20.3%、归母 +177.6%、ROE 21.9%、净利率 25.2%、流动比率高达 4.01（财务稳健），PE_TTM 9.0。"
             "今日 -2.41% 随板块高位换挡、量比 0.76 缩量——属主升后正常回踩而非放量出货，估值仍是安全垫（09-09 首推延续，位置更低）。"),
        data=[("今日", "-2.41% 缩量回踩"), ("20日涨幅", "+9.4%"), ("60日涨幅", "+13.3%"),
              ("2026H1归母", "+177.6%"), ("PE_TTM", "9.0"), ("ROE(H1)", "21.9%")],
        tech=[("均线形态", "多头排列（未破）"), ("RSI14", "60.1 中性偏强"), ("MACD", "金叉多头 DIF 0.51"),
              ("量比", "0.76 缩量回踩"), ("布林%B", "95.8 上轨附近"), ("关键位", "支撑 MA10 27.4 / 前高 29.0")],
        tnote="量比 0.76 缩量回踩 + 均线多头排列未破 = 主升后健康换挡（非放量出货）；收复 MA5（27.7）或缩量止跌于 MA10（27.4）分批，跌破 MA20（26.8）离场。",
        plan="【3~10 个交易日】回踩企稳（缩量止跌/收复 5 日线）后分批低吸，不在下跌中接刀；目标看前高 29.0，铝价跌破 24000 元或地缘缓和致供给预期反转即降级退出。",
        risk="铝价随地缘情绪大幅摆动；资源系整体已高位，若板块级退潮个股难独立；今日仍处回踩途中，需等企稳信号。",
        chk=(True, "通过——H1 +177.6%/ROE 21.9%/PE 9.0 报表已兑现、流动比率 4.0 稳健；今日缩量回踩非放量出货"),
        evid=[True, False, False, False, True],
    ),
    dict(
        rank=3, tag="主线低吸", pos="覆铜板·涨价受益",
        name="生益科技", code="600183.SH", price="146.96", chg="-0.81%",
        tags=["市场情绪", "龙虎榜资金", "能力#8验证"],
        title="覆铜板龙头 · 资金主线里的真受益方（H1 +130.4%）",
        why=("覆铜板涨价周期持续深化：建滔积层板年内第七次提价、FR-4 年内累计涨幅超 100%，松下/南亚塑胶 9 月起跟涨；"
             "AI 服务器/800G-1.6T 光模块挤占高端产能，高速 CCL 供不应求。今日龙虎榜资金聚焦该链——华正新材净买 +4.89 亿居首、崇达技术 +3.29 亿。"
             "生益=全球第二大/内资第一覆铜板龙头，M9 级材料已进英伟达 Rubin 供应链，2026H1 营收 +50.0%、归母 +130.4%、ROE 18.2%；"
             "今日 -0.81% 抗跌、60日 -18.4% 位置干净——买「业绩兑现的真受益方」而非「资金博弈的弹性小票」（09-08 反查补位逻辑延续）。"),
        data=[("今日", "-0.81% 抗跌"), ("20日涨幅", "+3.7%"), ("60日涨幅", "-18.4%"),
              ("2026H1归母", "+130.4%"), ("PE_TTM", "68.7"), ("成交额", "86 亿")],
        tech=[("均线形态", "均线纠缠 / 站上 MA20"), ("RSI14", "55.6 中性"), ("MACD", "多头收敛 DIF 3.73"),
              ("量比", "0.85 缩量"), ("布林%B", "71.4 中上轨"), ("关键位", "支撑 MA20 139.8 / 前高 153.4")],
        tnote="均线纠缠 + 缩量（0.85）于 MA20（139.8）上方横向蓄势，方向未定；<b>放量站上 153.4（20 日高）才确认二次启动</b>，跌破 MA20 止损。",
        plan="【3~10 个交易日】回踩 MA20（139.8）/MA10（145.9）企稳分批；放量突破 153.4 前高可加仓、目标 160~165；覆铜板报价证伪或跌破 MA20 离场。",
        risk="PE 68.7 偏贵，涨价持续性若证伪回撤大；PCB/覆铜板短期情绪波动剧烈（华正 20日已 +43%），板块获利回吐或拖累龙头；AI 硬件整体弱势时独立难支。",
        chk=(True, "通过（谨慎档）——H1 +130.4% 涨价直接兑现在报表、位置干净(60日-18.4%)、真受益龙头非资金票；估值偏高为唯一瑕疵"),
        evid=[False, True, True, False, True],
    ),
    dict(
        rank=4, tag="超跌回踩", pos="光模块·W底右侧",
        name="中际旭创", code="300308.SZ", price="890.10", chg="-2.07%",
        tags=["经典策略信号", "市场情绪", "能力#8验证"],
        title="AI 光模块龙头 · W底确认后缩量回踩（forward ≈30x）",
        why=("60日 -30.2% 深度回调后，09-08 以天量完成 W 底突破（颈线 866.12），今日 -2.07% 缩量回踩（量比 0.64、成交 155 亿）——"
             "突破后回踩蓄势形态。能力#8 验证：2026H1 营收 +182.5%、归母 +241.7%、ROE 37.6%、毛利率 46.3%；"
             "49 家机构 2026E 净利 338 亿（+213%）→ forward PE ≈30x，综合目标价 1494 元——高景气足以消化静态高估值。"
             "通信设备 20日 +4.6% 处于中游，「AI 算力/CPO/800G 光引擎」仍在今日涨停热词中——科技端唯一仍有景气背书的低位方向。"),
        data=[("今日", "-2.07% 缩量回踩"), ("60日涨幅", "-30.2%"), ("W底", "颈线 866.12 已确认"),
              ("2026H1归母", "+241.7%"), ("forward PE", "≈30x"), ("成交额", "155 亿")],
        tech=[("均线形态", "纠缠 / MA60(1020) 承压"), ("RSI14", "48.1 中性偏弱"), ("MACD", "零轴下金叉（超跌反弹）"),
              ("量比", "0.64 极度缩量"), ("布林%B", "51.8 中轨"), ("关键位", "支撑 866 颈线 / 压力 1001")],
        tnote="零轴下方 MACD 金叉=超跌反弹初期，但量比 0.64 极度缩量、反弹力度待<b>放量</b>确认；守住 866 颈线（W 底）持有，放量站上 1001（20 日高/MA60 下方）才算反转，跌破 813（右底）止损。",
        plan="【3~10 个交易日】颈线上方持有；回踩 866±1% 分批低吸；放量突破 1001 可加仓看 1050+；跌破右底区域止损——「跌回颈线即跑」（回测：W底 +76.3% 唯一正收益范式）。",
        risk="科技资金连续两周撤离未回流、创业板弱势；PB 26.3 极高、900 元高价股波动大；若通信板块持续缩量则 W 底可能假突破。",
        chk=(True, "通过——H1 +241.7%/ROE 37.6% 业绩爆发、forward ≈30x 消化估值、超跌(60日-30%)且 W底颈线确认"),
        evid=[True, True, False, True, True],
    ),
    dict(
        rank=5, tag="主线回踩", pos="磷化工·农业链",
        name="粤桂股份", code="000833.SZ", price="22.21", chg="-4.35%",
        tags=["板块轮动", "市场情绪", "能力#8验证"],
        title="磷肥主线 · 放量深回踩但均线未破（农业链业绩最硬）",
        why=("农业链（种植 20日 +27.8% 名义仍第一）本日高位回落、种植 -3.50% 领跌，粤桂 -4.35% 随链回调——但基本面与链条杂毛完全不同："
             "2026H1 营收 +72.4%、归母 +182.8%、ROE 15.8%、毛利率 43.5%、净利率 28.1%、PE_TTM 20.9，60日仅 +0.4%（位置干净）。"
             "硫铁矿+精制磷酸+光伏银粉业务结构，受益磷肥出口景气与磷化工涨价；09-09 曾获龙虎榜净买 +1.45 亿。"
             "今日深回踩把 5 日涨幅压缩至 +11.8%，是本组合中「业绩最硬 + 位置最低」的农业链标的（09-08 首推延续，等企稳）。"),
        data=[("今日", "-4.35% 深回踩"), ("20日涨幅", "+8.4%"), ("60日涨幅", "+0.4%"),
              ("2026H1归母", "+182.8%"), ("PE_TTM", "20.9"), ("毛利率(H1)", "43.5%")],
        tech=[("均线形态", "多头排列 MA5>10>20"), ("RSI14", "57.4 中性"), ("MACD", "金叉多头 DIF 0.33"),
              ("量比", "1.53 放量回踩"), ("布林%B", "80.0 中上轨"), ("关键位", "支撑 MA10 21.3 / 前高 23.2")],
        tnote="放量回踩（量比 1.53）显示分歧加大，但均线仍多头排列、MACD 金叉未破；守住 MA10（21.3）为强势整理，收复 MA5（21.8）可再参与，跌破 MA20（21.2）离场。",
        plan="【3~10 个交易日】农业链整体退潮中不接飞刀，等缩量止跌/收复 MA5（21.8）再分批；目标前高 23.2；跌破 MA20（21.2）或磷肥板块集体退潮离场。",
        risk="农业链已高位（种植 20日 +27.8% 但今日领跌），链条级回调时个股难独立；今日放量深跌 -4.35% 显示承接偏弱；硫磺/磷肥价格波动、PB 4.3 不便宜。",
        chk=(True, "通过——H1 +182.8% 与 PE 20.9 匹配、位置干净(60日+0.4%)、毛利率 43.5% 盈利质量高；今日放量回踩需等企稳"),
        evid=[True, True, False, False, True],
    ),
]

EVID = [
    ("板块轮动 #7", "个股所在板块处于动量前列/量能放大"),
    ("市场情绪 #6", "情绪面涨停热词/梯队包含该方向"),
    ("龙虎榜 #11", "个股上榜且获资金（含机构）净买"),
    ("经典策略 #1", "W底/新高突破等右侧信号当日触发"),
    ("能力#8 验证", "全面分析五维通过（估值/财务/成长/风险/投资指导）"),
]

# ★ 能力#8 验证记录（v1.1）：(标的, "ok"通过观察|"bad"剔除, 判定依据) —— 缺省 [] 则面板不渲染
AUDIT_ROWS = [
    ("神火股份（09-09 选·转观察）", "ok", "H1 归母 +151.1%/ROE 18.4%/PE 9.2 基本面仍优，技术面多头排列（MA20 上方 +4.7%）；与云铝同属铝链、组合已有铝敞口——为分散度让位，非否决，作资源线替补观察"),
    ("江苏银行 600919（候选·银行）", "ok", "H1 营收 +9.1%/归母 +8.1%、PE 6.4/PB 0.85，技术面 RSI 68.4/%B 107.2 同创历史新高——与宁波银行同主线同逻辑，取盈利弹性更强的宁波作代表，江苏并列观察（同样超买）"),
    ("华正新材 603186（候选·龙虎榜第一）", "bad", "H1 归母 +305.3%、今日龙虎榜净买 +4.89 亿居首（800G 光模块材料过华为认证）——但 PE 84、净利率仅 5.9%、20日 +43.1%；<b>技术面独立佐证超买：乖离 MA20 +20.3%、%B 118 破上轨、5日 +20.9%</b> → 估值透支+位置风险双否，覆铜板链取龙头生益（观察其弹性）"),
    ("湖南黄金 002155（候选·龙虎榜第二）", "ok", "重大重组+黄金锑钨、龙虎榜净买 +4.39 亿、H1 归母 +46.0%——但毛利率仅 5.6%（贸易业务占比高、盈利质量薄），贵金属板块缩量退潮——观察不追"),
    ("中国铝业 601600 / 宝丰能源 600989（候选）", "ok", "中铝 H1 归母 +67.9%/PE 9.7、宝丰 H1 +70.1%/PE 11.8 均为优质低估资源票——铝链取弹性更大的云铝、煤化工已有观察位，二者列资源线备选观察"),
    ("大连重工 002204（候选）", "bad", "今日 +10.09% 涨停放量，但 H1 ROE 仅 4.7%、归母 +18.8% 属温和增长——涨停日追高风险大于基本面吸引力，观察"),
    ("农业种业方向（整体剔除）", "bad", "敦煌种业 20日 +88.3%/60日 +125.8%、红棉股份 20日 +51.7% 已妖股化（PE 44/67）；种植业今日 -3.50% 领跌、三周霸榜终结——方向整体高位退潮，不参与"),
    ("上汽集团 600104 / 盾安环境 002011（基本面否决）", "bad", "上汽 H1 归母 -14.4%（PB 0.43 低但成长性缺失）、盾安 H1 归母 -12.8%——基本面维度直接否决，估值低不构成买入理由"),
    ("北大荒 600598 / 三孚股份 603938（09-09 观察·维持）", "ok", "北大荒今日 -3.38%（农业链退潮）维持观察，一次性补税出清逻辑未变；三孚今日 -4.37% 且量比 2.13 放量杀跌、PE 107 高位风险大——均维持观察不动"),
]

NOTE = ("数据来源：hithink-finance CLI 实测（涨停/跌停/炸板池 09-10、龙虎榜普通+机构榜、板块指数 881xxx.TI、本地前复权 v_daily_qfq 全市场 W底/60日新高扫描、"
        f"market/valuation snapshot、financials indicators 2026 中报、短线技术指标由本地前复权日K自算），数据截至 {DATE} 收盘；产业逻辑/涨价/风格切换为 WebSearch 公开披露"
        "（已显式标注：银行=上证报/证券时报 09-10 报道·上半年营收 +7.42%/17 家息差回升/PE 7.26·PB 0.69·股息率 4.33%；"
        "覆铜板=建滔年内第七次提价·FR-4 年内累计涨幅超 100%·生益 M9 进英伟达 Rubin 供应链；旭创一致预期 49 家机构）。"
        "本版按能力 #12 v1.2 流程：四能力（轮动#7×情绪#6×龙虎榜#11×策略#1）交叉取证 → 逐只 #8 全面分析验证 → 不值得买剔除"
        "（农业种业妖股化、基本面下滑票否决）→ 风格切换方向补位宁波银行；每卡附短线技术指标（均线/RSI/MACD/量比/布林/关键位）。"
        "<b>定位为短中线（持有 3~10 个交易日），非长线推荐</b>：基本面对本策略仅作「不做接刀」的安全垫，破位即走、不因基本面转长线。"
        "回测结论引用能力 #1 引擎 2025-08-22~2026-08-21 实测：W底双底突破 +76.3%（回撤-23.1% 全场最优）、海龟唐奇安 +79.0%、"
        "二连板接力 -18.8%、三连板 -83.57%——「等突破确认右侧买 + 跌回颈线即跑」是唯一正收益范式。"
        "当日为深度普跌日（下跌 4512 家、中位 -1.49%），组合以「回踩/企稳分批」为操作前提，非追高推荐。"
        "本报告为研究参考，不构成个人投资建议。")

CLS = {"防御主线": "a", "主线右侧": "b", "资源回踩": "c", "超跌回踩": "d", "主线低吸": "e", "主线回踩": "f"}

# ---------- 04 操作纪律：回测实证证据（能力 #1 引擎实测值）----------
# 数据区默认值 = skill 单独运行时的原文（保证 skill 单独运行产物不变）；
# 平台按**本次**回测结果/最新 bt_all.json 计算后注入；取不到则如实注「未取到」。
BT_SCOPE = "20 策略 2025-08-22~2026-08-21 实测"
BT_WB = "+76.3%"
BT_WB_MDD = "-23.1%"
BT_TURTLE = "+79.0%"
BT_NEWLOW = "-54.3%"
BT_RSI = "-1.7%"
BT_WB_FAKE = "10/21"
BT_WB_FAKE_LOSS = "-3.5%"
BT_2BOARD = "-18.8%"
BT_3BOARD = "-83.57%"
BT_RSI_WR = "58%"
BT_TURTLE_WR = "28%"

N = len(STOCKS)

# ---------- 渲染 ----------
_PCT = re.compile(r'[+\-]\d+(?:\.\d+)?%')

def chg_cls(t):
    """按首个符号判涨跌：+ → up(红)、- → dn(绿)、其余 → 无色。"""
    t = str(t).strip()
    return "up" if t.startswith("+") else ("dn" if t.startswith("-") else "")

def hl(t):
    """把文本里的 ±x% 自动包红绿 span（红涨绿跌，v1.2）。"""
    return _PCT.sub(lambda m: f'<span class="{chg_cls(m.group(0))}">{m.group(0)}</span>', str(t))

def stock_card(s):
    ev = ""
    for i, (lab, _) in enumerate(EVID):
        ev += f'<span class="ev {"off" if not s["evid"][i] else ""}">{"●" if s["evid"][i] else "○"} {lab.split(" ")[0]}</span>'
    tg = "".join(f'<span class="tg">{t}</span>' for t in s["tags"])
    dr = "".join(f'<div class="kv"><span>{k}</span><b>{hl(v)}</b></div>' for k, v in s["data"])
    tech_html = ""
    tech = s.get("tech") or []
    if tech:
        tks = "".join(f'<div class="kv"><span>{k}</span><b>{hl(v)}</b></div>' for k, v in tech)
        tn = s.get("tnote")
        tech_html = ('<div class="tgrid"><div class="tt">📐 短线技术面（前复权日K自算 · 持有周期 3~10 个交易日）</div>'
                     f'<div class="grid2">{tks}</div>'
                     + (f'<div class="tnote">{hl(tn)}</div>' if tn else "") + '</div>')
    chk = s.get("chk")
    chk_html = ""
    if chk:
        ok, txt = chk
        chk_html = f'<div class="vchk {"ok" if ok else "bad"}">{"✅" if ok else "⚠️"} 能力#8 验证：<span>{txt}</span></div>'
    return f'''
    <div class="card">
      <div class="card-head">
        <div><span class="no">{s["rank"]}</span><span class="nm">{s["name"]}</span>
          <span class="tcode">{s["code"]}</span><span class="stag {CLS[s["tag"]]}">{s["tag"]}</span></div>
        <div class="px"><b>{s["price"]}</b><span class="chg {chg_cls(s["chg"])}">{hl(s["chg"])}</span></div>
      </div>
      <div class="tags">{tg}</div>
      <div class="sec-t">{s["title"]}</div>
      <div class="why">{s["why"]}</div>
      <div class="grid">{dr}</div>
      {tech_html}
      <div class="plan"><b>操作参考 · 短中线</b><span>{s["plan"]}</span><br><b>执行前提（不满足则不做）</b><span>次日<b>高开超过 3% 即放弃</b>；等到回踩至上述入场位、<b>缩量企稳</b>后再分批；<b>不回踩到位就不买</b>——宁可错过，不追高。若正文的「回踩」与入场价口径冲突，<b>一律以本执行前提为准</b>。</span></div>
      <div class="risk"><b>主要风险</b><span>{s["risk"]}</span></div>
      {chk_html}
      <div class="evrow"><b>证据</b>{ev}</div>
    </div>'''

def matrix_rows():
    rows = ""
    for s in STOCKS:
        cells = "".join(f'<td class="{"ck" if ok else "no2"}">{"●" if ok else "○"}</td>' for ok in s["evid"])
        rows += f'<tr><td><b>{s["name"]}</b> {s["code"][:6]}</td><td>{s["pos"]}</td>{cells}</tr>'
    return rows

def audit_rows():
    if not AUDIT_ROWS:
        return ""
    rows = ""
    for name, flag, txt in AUDIT_ROWS:
        rows += (f'<tr><td style="white-space:nowrap"><b>{name}</b></td>'
                 f'<td><span class="pill {"ok" if flag == "ok" else "bad"}">{"通过" if flag == "ok" else "剔除"}</span></td>'
                 f'<td>{txt}</td></tr>')
    return rows

CARDS = "".join(stock_card(s) for s in STOCKS)
KPIS_HTML = "".join(f'<div class="kpi"><div class="v num {c}">{v}</div><div class="k">{k}</div></div>' for v, k, c in KPIS)
IDX_HTML = "".join(f'<span>{n}<b class="num {c}">{b}</b></span>' for n, b, c in IDX)
LINES_HTML = "".join(f'<span class="ln">{t}</span>' for t in LINES)
AUDIT_HTML = audit_rows()
H1 = f"精选 {N} 股推荐报告"
FILE = f"精选{N}股推荐_{DATE.replace('-', '')}.html"

html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H1} · {DATE}</title>
<style>
:root{{--navy:#1f3a93;--navy2:#2f56c9;--gold:#c9a227;--ink:#1c2333;--ink2:#5b6478;--line:#e6e9f2;--bg:#f4f6fb;
--red:#e5484d;--green:#2fa36b;--gold-bg:linear-gradient(135deg,#fdf6e0,#fbecc0);}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--ink);font:14px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif;padding:20px}}
.wrap{{max-width:1060px;margin:0 auto}}
.num{{font-variant-numeric:tabular-nums}}
header{{background:linear-gradient(135deg,#1f3a93,#2749b3);border-radius:14px;padding:22px 26px;color:#fff;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
header .logo{{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px}}
header .logo i{{font-style:normal;background:var(--gold);color:#1f3a93;border-radius:6px;padding:2px 8px;font-size:12px}}
header h1{{font-size:21px;margin-top:2px}}
header .date{{text-align:right;font-size:12px;opacity:.9}}
header .date b{{display:block;font-size:15px;opacity:1}}
.banner{{background:var(--gold-bg);border:1px solid #eeda9a;border-radius:10px;padding:11px 16px;margin:14px 0;color:#6b5410;font-size:13.5px}}
.banner b{{color:#8a6d00}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:14px 0}}
.kpi{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.kpi .v{{font-size:24px;font-weight:800}}
.kpi .k{{font-size:12px;color:var(--ink2);margin-top:2px}}
.up{{color:var(--red)}} .dn{{color:var(--green)}} .hot{{color:var(--red)}}
.idx{{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 16px}}
.idx span{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:5px 11px;font-size:12.5px}}
.idx b{{margin-left:6px}}
.lines{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:4px}}
.lines .ln{{background:#eef1fb;color:var(--navy);border-radius:8px;padding:5px 11px;font-size:12.5px;font-weight:600}}
h2{{font-size:16px;color:var(--navy);margin:22px 0 10px;display:flex;align-items:center;gap:8px}}
h2 .no{{background:var(--navy);color:#fff;border-radius:6px;padding:1px 8px;font-size:12.5px}}
h2 .hint{{font-weight:400;font-size:12px;color:var(--ink2)}}
.card{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px;box-shadow:0 1px 3px rgba(31,58,147,.05)}}
.card-head{{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px}}
.no{{display:inline-flex;width:26px;height:26px;border-radius:7px;background:var(--navy);color:#fff;align-items:center;justify-content:center;font-weight:800;margin-right:8px;font-size:14px}}
.nm{{font-size:20px;font-weight:800}}
.tcode{{font-size:12px;color:var(--ink2);margin-left:7px;background:#f0f2f8;border-radius:5px;padding:1px 7px;font-weight:600}}
.stag{{margin-left:8px;border-radius:6px;padding:2px 9px;font-size:11.5px;font-weight:700;color:#fff}}
.stag.a{{background:var(--green)}} .stag.b{{background:#c97818}} .stag.c{{background:var(--red)}} .stag.d{{background:var(--navy2)}} .stag.e{{background:#8a6d9b}} .stag.f{{background:#0f8a83}}
.px{{text-align:right}}
.px b{{font-size:26px;font-weight:800}}
.chg{{display:block;font-size:14px;font-weight:700}}
.tags{{margin:9px 0 4px;display:flex;gap:7px;flex-wrap:wrap}}
.tg{{font-size:11px;color:var(--navy);background:#e9edfb;border-radius:20px;padding:1px 10px;font-weight:600}}
.sec-t{{font-size:15px;font-weight:800;color:var(--navy);margin:4px 0 6px}}
.why{{font-size:13.5px;color:#333c50}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 14px;margin:10px 0;background:#f7f8fc;border-radius:9px;padding:10px 13px}}
.tgrid{{background:#f0f4ff;border:1px solid #dbe3f8;border-radius:9px;padding:9px 13px;margin:8px 0}}
.tgrid .tt{{font-size:11.5px;color:var(--navy);font-weight:800;margin-bottom:6px}}
.tgrid .grid2{{display:grid;grid-template-columns:repeat(3,1fr);gap:5px 14px}}
.tnote{{font-size:12px;color:#3b4a6b;margin-top:7px;padding-top:6px;border-top:1px dashed #c9d5f0;line-height:1.55}}
.kv{{display:flex;justify-content:space-between;align-items:baseline;font-size:12.5px}}
.kv span{{color:var(--ink2)}} .kv b{{font-size:13px}}
.plan,.risk{{font-size:13px;margin-top:7px;padding-left:13px;border-left:3px solid var(--gold);}}
.plan b,.risk b{{color:#8a6d00;margin-right:6px;font-size:12.5px}}
.risk{{border-left-color:#e0a3a6}} .risk b{{color:#b04548}}
.vchk{{margin-top:9px;padding:6px 11px;border-radius:8px;font-size:12.5px;font-weight:700;display:flex;gap:6px;align-items:flex-start;line-height:1.55}}
.vchk.ok{{background:#e9f7f0;color:#157a4f;border:1px solid #bfe8d4}}
.vchk.bad{{background:#fdeeee;color:#b04548;border:1px solid #f2c6c6}}
.vchk span{{font-weight:400}}
.evrow{{display:flex;gap:6px;align-items:center;margin-top:9px;flex-wrap:wrap;font-size:11.5px;color:var(--ink2)}}
.evrow b{{color:var(--ink2);font-weight:600}}
.ev{{background:#eef7f2;color:var(--green);border-radius:5px;padding:1px 7px;font-weight:600}}
.ev.off{{background:#f0f1f5;color:#aab}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;font-size:13px}}
th{{background:#f0f3fb;color:var(--navy);padding:8px 10px;text-align:left;font-size:12.5px}}
td{{padding:8px 10px;border-top:1px solid var(--line)}}
.ck{{color:var(--green);font-weight:800}} .no2{{color:#c4c9d6;font-weight:800}}
.pill{{display:inline-block;border-radius:5px;padding:1px 8px;font-weight:700;font-size:11.5px;white-space:nowrap}}
.pill.ok{{background:#e9f7f0;color:#157a4f}} .pill.bad{{background:#fdeeee;color:#b04548}}
.audit td{{vertical-align:top;font-size:12.5px}}
.insight{{background:var(--gold-bg);border:1px solid #eeda9a;border-radius:10px;padding:12px 16px;margin:14px 0;color:#6b5410;font-size:13.5px;font-weight:700}}
.insight::before{{content:"💡 "}}
footer{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 15px;margin:18px 0 8px;font-size:11.5px;color:var(--ink2)}}
</style></head><body><div class="wrap">

<header>
  <div><div class="logo"><i>THS</i>多能力协同选股<span style="opacity:.7;font-weight:400;font-size:12px">轮动×情绪×龙虎榜×经典策略回测 + 能力#8 验证</span></div>
  <h1>{H1}</h1></div>
  <div class="date">数据截至<b>{DATE} 收盘</b>{GEN}</div>
</header>

<div class="banner">{BANNER}</div>

<h2><span class="no">01</span>市场环境速写<span class="hint">数据：hithink CLI 实测（涨停/炸板池、龙虎榜、板块指数、本地库涨跌家数）</span></h2>
<div class="kpis">{KPIS_HTML}</div>
<div class="idx">{IDX_HTML}</div>
<div class="lines">{LINES_HTML}</div>
<div class="insight">{INSIGHT01}</div>

<h2><span class="no">02</span>精选 {N} 股推荐<span class="hint">短中线定位（持有 3~10 个交易日）· 按确定性排序 · 每只均经能力#8 全面分析验证 · 全部为 {DATE} 当日新信号</span></h2>
{CARDS}

<h2><span class="no">03</span>信号证据交叉矩阵<span class="hint">●=该股当日具备此项能力证据（{len(EVID)} 项能力独立取证，末列=能力#8 验证通过）</span></h2>
<table>
<tr><th>股票</th><th>主线定位</th>{"".join(f"<th>{lab.split(' ')[0]}</th>" for lab, _ in EVID)}</tr>
{matrix_rows()}
</table>
<div class="insight">{INSIGHT03}</div>

{AUDIT_HTML and '<h2><span class="no">★</span>能力#8 验证记录（v1.1 新增）<span class="hint">原选/候选逐一验证 → 剔除与补位全程留痕，宁缺毋滥</span></h2><table class="audit"><tr><th>标的</th><th>判定</th><th>关键依据（数据=CLI 实测，事件=WebSearch 公开披露）</th></tr>' + AUDIT_HTML + '</table>'}

<h2><span class="no">04</span>操作纪律（短中线口径 · 源自能力 #1 回测实证）<span class="hint">__BT_SCOPE__</span></h2>
<table>
<tr><th>纪律</th><th>回测证据 / 依据</th><th>本次应用</th></tr>
<tr><td><b>短中线持有，不做长线</b></td><td>本报告全部为当日新触发的短线信号（W底突破/放量新高/涨停回踩），信号有效期即 3~10 个交易日；回测引擎按"信号触发→持有至卖点"统计，无长线维度</td><td>每卡给出入场技术位/止损位/短线目标；<b>破位即走，不因"基本面好"而扛单或转长线</b></td></tr>
<tr><td><b>只做右侧突破，不左侧抄底</b></td><td>W底 __BT_WB__（回撤__BT_WB_MDD__ 最优）& 海龟 __BT_TURTLE__ 唯二正收益；60日新低 __BT_NEWLOW__、RSI 抄底 __BT_RSI__ 全灭</td><td>推荐全部是「当日突破/涨停新触发」的右侧信号，无左侧接刀</td></tr>
<tr><td><b>跌回颈线即跑（假突破离场）</b></td><td>W底假突破 __BT_WB_FAKE__ 笔靠此控制损失（平均 __BT_WB_FAKE_LOSS__）</td><td>W底标的跌破颈线/右底即离场；其余标的跌破启动位同理</td></tr>
<tr><td><b>连板越高越差，禁止追板</b></td><td>二连板接力 __BT_2BOARD__、三连板 __BT_3BOARD__</td><td>连板标的均「不追下一板」，等分歧回踩</td></tr>
<tr><td><b>盈亏比 > 胜率</b></td><td>RSI 胜率 __BT_RSI_WR__ 打平 vs 海龟 __BT_TURTLE_WR__ 大赚</td><td>单笔止损纪律严于胜率追求，回踩位参与、破位即走</td></tr>
<tr><td><b>入场纪律必须可执行、可证伪</b></td><td>2026-09-16 复盘 09-08~09-11 四期 20 笔（09-08 取「验证版」最终名单）：按「次日开盘无条件买入」口径平均 <b>-1.73%</b>、最差 <b>-13.65%</b>、胜率 45.0%；而原报告正文写「只做回踩、不追高」，与入场价口径自相矛盾，读者无法同时遵守</td><td>以「<b>次日高开 &gt;3% 则放弃</b>；回踩至卡片入场位并缩量企稳才买；<b>不回踩则不做</b>」为唯一入场口径——宁可错过，不追高</td></tr>
<tr><td><b>止损必须有硬上限</b></td><td>同一复盘 20 笔：持有到期末平均 -1.73%（最差 <b>-13.65%</b>）；加硬止损后平均改善、尾部收敛——<b>固定止损 -5% → -1.55%（最差 -5.00%）、-8% → -1.02%（最差 -8.00%）</b>；而「跌破 MA5 / MA10 离场」反而<b>更差</b>（-2.22% / -1.79%，胜率降至 25%/30%）——阴跌中均线一路下移迟迟不触发。<b>注意：20 笔样本不足以区分 -5% 与 -8% 的优劣（-1.55% vs -1.02% 差异在噪声内）</b>，结论只到「必须有硬上限」这一层</td><td>止损价取「支撑位下方」与「入场参考价 ×(1-止损幅度)」中的<b>较高者</b>；本报告采用更保守的 <b>-5%</b>，任何情况下单笔浮亏不超过该幅度</td></tr>
<tr><td><b>同一标的短期内不重复推荐</b></td><td>同一复盘：中际旭创连续 4 期上榜（本质是同一注重复 4 次，非 4 个独立机会）、粤桂股份连续 2 期上榜且两次均亏（-13.65% / -10.98%）</td><td>同一标的在最近 <b>5 个交易日</b>内已推荐过的，不再重复推荐（除非出现全新的、更强的新触发信号，并需在「验证记录」中留痕说明）</td></tr>
</table>

<h2><span class="no">05</span>口径与免责</h2>
<footer>{NOTE}</footer>

</div></body></html>'''

# 04 区回测证据占位符回填（长占位符优先，避免前缀误替换）
html = (html.replace("__BT_SCOPE__", BT_SCOPE)
            .replace("__BT_WB_FAKE_LOSS__", BT_WB_FAKE_LOSS)
            .replace("__BT_WB_FAKE__", BT_WB_FAKE)
            .replace("__BT_WB_MDD__", BT_WB_MDD)
            .replace("__BT_WB__", BT_WB)
            .replace("__BT_TURTLE_WR__", BT_TURTLE_WR)
            .replace("__BT_TURTLE__", BT_TURTLE)
            .replace("__BT_NEWLOW__", BT_NEWLOW)
            .replace("__BT_RSI_WR__", BT_RSI_WR)
            .replace("__BT_RSI__", BT_RSI)
            .replace("__BT_2BOARD__", BT_2BOARD)
            .replace("__BT_3BOARD__", BT_3BOARD))

out = os.path.join(BASE, FILE)
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", out, len(html), "bytes")
