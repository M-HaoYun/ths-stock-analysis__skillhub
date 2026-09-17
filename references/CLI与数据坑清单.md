# CLI 与数据坑清单（重要，生成报告前必读）

> 由 SKILL.md 迁移维护（2026-09-05）。SKILL.md 正文中「坑 N」（如坑 23/24/27/30）均指本文件对应编号条目。
>
> **本文件只收录「现在还成立、绕不开」的东西**：CLI/接口限制、数据口径、必须遵守的调用与编写规范。
> 🔴 **已在脚本/模板里改掉的缺陷不写进来**（改完代码坑就不存在了；修复过程记在 `.workbuddy/memory/` 工作日志，代码里也有注释）。
> 🔴 同理**不收「本机工具/历史副本的临时故障」**（路径失效、副本要参数化之类）——那些直接改脚本就行。
> ✅ **判断口径：这条的结论还依赖「某个文件里有个 bug」吗？依赖 → 去改代码；不依赖（是接口限制/口径/规范）→ 才写进来。**
> ⚠️ **编号是稳定 ID，不重排**——本文件出现「缺号」= 该条已因代码修复而删除，不是漏写。
> **新踩的坑追加到末尾并递增编号。**


### ✅ 已被脚本强约束的坑（不必再靠记忆）

| 坑 | 现在由什么强制 | 命令 |
|---|---|---|
| 42 / 44 / 54 / 60（数据区变量缺/漏 `NAME = ` 前缀/模板变量被整段替换） | `check_build.py` **S2 未绑定名** + **S4 变量集合比对** | `--script gen_xxx.py --template <skill>/scripts/gen_xxx.py` |
| 52（数据区 f-string 引用构建器变量） | 同上，S2 会把该名字报为未绑定 | 同上 |
| 53（`re.sub` 替换串非 lambda） | `check_build.py` **B1** | `--builder build_xxx.py` |
| 33（复制脚本后日期/文件名对不齐） | `check_build.py` **B2** 残留旧日期 | 同上 |
| 55（`DATE`/`WEEKDAY` 未替换、title 与文件名不同口径） | `check_build.py` **S5 + H1** | `--script … --expect-date` 或 `--html 产物.html` |
| 56（HIST 字段数、价格未 `round(2)`） | `check_build.py` **C1/C2** | `--hist hist.json` |
| 58（数据区裸 ASCII 双引号，含 `\"`） | `check_build.py` **S1 编译 + S3** | `--script gen_xxx.py` |
| 59（批量引号替换误伤 `", "`） | `check_build.py` **B4** | `--builder build_xxx.py` |
| 46（HTML 里残留 markdown `**`） | `check_build.py` **H3** | `--html 产物.html` |
| 61（近一年=252 交易日窗口） | `check_build.py` **H6/C3** + `ths_indicators.py`（口径唯一实现） | `--html … --expect-points 252` / `--hist …` |
| 28（喂 CLI 的清单带 `\r`） | `check_build.py` **K1** | `--codes codes.txt` |
| 45（复盘必须用最终交付版、名单必须可信） | `review_picks.py` **显式优先「验证版」+ 名单异常即拒绝**（不再静默取前 5 项） | `--pattern "精选*推荐_*.html"` |
| 35（短线指标自算口径） | `ths_indicators.py`（MA/RSI/MACD/布林/量比/乖离的唯一实现） | `--hist hist.json` |

> 其余条目属 **CLI/接口事实**（哪些接口没有、参数签名、返回结构差异），脚本无法约束，按条目照做即可。

### 获取数据类坑（优先级最高）

1. **`special hot-stock-history` 的 `--date` 参数无效**：实测查 2026-01-05 与 2026-08-21 返回完全相同（永远=最近交易日热榜）。**历史日热榜不可回溯** → 标 [MISSING]，用龙虎榜净买 TOP3 替代为"资金关注焦点"。（2026-08-23 实测：宇树科技未上市却在 01-05 热榜暴露）
2. **`special limit-up-ladder`（连板梯）只返回最近 30 个交易日** → 历史日的连板梯队从涨停池 `continue_day_cnt` 字段重建（分组统计各连板数家数）。
3. **`special anomaly-list`（异动列表）为当日实时能力**，历史日不可查 → 标 [MISSING]。
4. **热榜历史接口的 `heat`（热度值）字段为 None** → 只展示排名，页脚注明。
5. **龙虎榜接口无买卖席位明细**（仅汇总净额+机构/游资净额）→ 知名游资席位需 WebSearch 公开披露补充，**页面显式标注"WebSearch 公开披露"**（数据来源铁律）；机构分析用 `--board-type org` 版（有 org_net_value/org_buy_num/org_sell_num）。
6. **涨停池默认查当天**（非交易日返回空）→ 必须指定 `--date-ms <当日0点毫秒>`；`limit_up_reason` 含板块标签（板块热度数据源）、`continue_day_cnt` 含连板数。
7. **指数涨跌幅**：`index history` 拉包含目标日与前收的窗口，用目标日收盘 vs 前一交易日收盘计算（接口对远古窗口可能无数据，需从更早起点拉取）。
8. **龙虎榜数据坑**：`change` 为小数比例（0.10=+10%）；同股多次上榜需按 ticker 合并；`hot_money_net_value` 部分条目缺失用 `.get()`；Hero KPI 正负号必须 `{:+.2f}` 格式化（禁止硬编码"+"→ 负值会出现"+-"）；模板 insight 为当日叙事，换日期必须逐一替换硬编码。
9. **涨跌家数**：本地库 `db query` 用 `close > open` 统计（raw_kline_daily 列名为 `close/open/date`，无 close_price 列不会触发误判）；本地库无指数表。
10. **历史K双结构**：本地结构 `data`(list)+`date`/`close`；远端/ETF 结构 `data.item[]`+`date_ms`/`close_price`——解析必须兼容两种（个股用本地前复权，ETF 用 fund.history 远端）。
11. **数据交叉验证（方法论）**：接口返回"看起来合理"的数据时，用业务常识校验——次新股上市日期（名字带 C/-W 后缀=刚上市，历史日期不可能出现）、XD 除息标记（只出现在除息日）、与涨停池/龙虎榜名单交叉比对。发现可疑数据宁可标 [MISSING]。
12. **估值数据坑（能力 #4）**：①`valuation` 仅 A 股（港股/美股报错 CLI_BAD_ARGUMENT）且只有 snapshot——**无历史估值/行业估值接口，历史分位必须回溯法自建**（历史PE_i=当前PE_TTM×前复权价比例）②market snapshot 无市值字段（回溯法不需要股本）③**SVG fill 不支持 CSS linear-gradient 字符串**（会回退黑色）→ 一律纯色④**盈利高增股回溯法低估历史 PE**（按当前 TTM 净利回溯，净利翻倍+标的口径，页脚/风险注明）⑤行业对比公司必须按标的主营选同行（电网设备/黄金铜业等）。⑥**Hero KPI 标签曾硬编码「5年92%分位」（紫金矿业旧版残留）→ 已改为 __PERC_KPI__ 占位符由 PERC['p5']['pe'] 动态生成**（2026-08-24 汾酒验证暴露：汾酒实际 3% 分位却显示 92%）——**报告模板禁止把数值硬编码进 TPL，一律占位符+数据区驱动，生成后 grep 旧数值残留**
13. **财务预测器坑（能力 #3）**：①`financials income` 返回**倒序**（最新在前）且**无 yoy 字段需自算** ②最新报告期判断：先用 quarterly 确认（亨通最新=2026Q1 而非中报）③一致预期可能被激进机构拉高（亨通 2026E 79 亿 vs 分机构 40-50 亿）→ 中性取券商区间中枢并提示 ④三情景预测必须标 [MODEL]/[ASSUMED]（模型输出非公司指引），券商数据页脚标注来源 ⑤敏感性矩阵用"营收×净利率"而非单变量，表达预测区间宽度。 ⑦**03/04 区块 insight/hint 曾硬编码亨通文案**（'中性 45 亿/AI光纤+海缆'残留）→ 已改为 __SCEN_INSIGHT__/__DRIVER_HINT__ 占位符，新增变量用插入（模板无此行，replace 会静默失败）⑧**假设表第一列 sum-tag 标签窄列宽下换行成两行 → 已加 white-space:nowrap**（2026-08-24 汾酒验证暴露）——**所有模板区块级 hint/insight 必须占位符化，新变量插入而非替换，生成后 grep 旧标的名/旧行业词残留**。⑥**模板字段类型强约束（2026-08-24 汾酒验证）**：SCENARIOS 键必须是中文「乐观/中性/悲观」且含 desc 字段；BROKERS 值为数字（非字符串）；DRIVERS 为 3 元组（icon, 标题, 描述）——填错类型渲染时 ValueError，先看模板渲染函数再填数据。
14. **业绩前瞻日历坑（能力 #5）**：①**hithink 无业绩披露日历接口**（`market calendar` 仅交易日且返回一年窗口，窗口在年内可核对、超出需按 A 股规则推算）→ 披露安排/业绩预告必须 WebSearch 交易所预约+新闻报道，**页脚显式标注来源** ②披露量分布为新闻口径（各源有差异，取主源）③盲盒清单要标注统计时点（如"8-14 时未披露口径"）并提示可能已提前披露 ④披露日为预约制可调整，风险区注明 ⑤业绩预告为区间（上限/下限），实际披露可能落低位。
15. **板块轮动坑（能力 #7）**：①板块指数用 `index catalog --tag industry`（881xxx.TI 一级行业 90+，另有一批 884xxx 细分行业）②**板块指数历史含 turnover（成交额）**——量比（5日均成交/20日均成交）与动量可同源计算 ③行业指数代码带 .TI 后缀（同花顺专属），与指数快照 .SH/.SZ 不同 ④轮动表内"20日"数值列与"20日动量"进度条列为同一数据双列（非错误）→ 避免重复展示，进度条列与排名区二选一 ⑤`__VERDICT__` 等占位符在模板中只能替换一次（曾放 vbadge+粗体两处导致判定词重复）。
16. **穿透分析坑（能力 #9）**：①**hithink 无"个股被哪些基金持有"接口** → 反向穿透必须 WebSearch 公开披露（新浪基金持股页/巨丰/东吴等），页脚显式标注来源与口径（渤海=主动权益基金数、巨丰=全口径、东吴=占总市值比例）②`fund industry-allocation` 可能报 FUYAO_5003（status 9999 retryable）→ 行业分布用持仓股主营归类或标 [MISSING] ③持仓报告期（2026Q2 季报）与持有人报告期（2025-12-31 年报）不同需分别标注 ④**闭环验证**：正向持仓股应能在反向持有基金表中找到该 ETF 本身（换标的必查）⑤**抱团图双列布局**：右列起始 x2 固定并与图例对齐、左列条宽受限于 x2（值文本不越界）、右列条宽按可用宽度（曾公式负值→全 4px 条+重叠）⑥**占位符唯一性**：title 用 __DATE_SHOW__（曾 {DATE} 显示字面量）、闭环判断用 CFG["etf_code"] 动态取（曾硬编码 512480）⑦模板全参数化：KPI/档案/持有人/insight/解读/风险行必须在数据区，禁止 TPL 写死当日叙事 ⑧**layer_svg 颜色表只支持 4 层，LAYERS 超 4 层会 IndexError → 已修复为 `colors[i % len(colors)]` 取模循环**（2026-08-24 协鑫集成 5 层验证暴露）⑨**SHAREHOLDERS 占比列必须为数字**（模板 `{pct:.2f}%` 格式化，传 "8.89%" 字符串会 ValueError）。 ⑩**layer_svg 固定高度 H=260 是按 4 层设计，LAYERS 超 4 层（如 5 层）时底部行与图注超出 viewBox 被裁剪显示不全 → 已改为动态高度 `H = pad_t + len(LAYERS)*(row_h+gap) - gap + 30`**（2026-08-24 协鑫 5 层验证暴露）。
17. **组合风险坑（能力 #10）**：①**不同量纲资产不能直接加权**：ETF 价格（0.87）与指数点位（2500）混合加权会淹没收益 → 组合净值必须先各自归一化到 1 再按权重相加 ②`fund history` 为远端结构 `data.item[]`+`date_ms`/`close_price`，与本地 K 线结构不同（**个股组合改用本地 DuckDB v_daily_qfq 前复权日K**）③年化收益/波动按 252 交易日换算、相关系数基于日收益率（窗口对齐取交集）④最大回撤需记录峰值日~谷底日区间 ⑤分散模拟标 [MODEL]（历史窗口回测，红利在股灾时也大跌）⑥相关性着色约定：>0.7 红 / 0.4-0.7 橙 / 0-0.4 蓝 / <0 绿 ⑦kv_rows 渲染函数需兼容字符串列表（风险行）与 (k,v) 元组两种输入（DIAG 必须 2 元组）⑧**DIVERSIFY 行 ret/vol/dd 可为 None（定性建议行）→ div_rows 已加 None 保护显示 "--"**（曾 ret=None 崩溃）⑨**相关系数方差公式必须 `(sum/len)**0.5`**（曾写 sum/len**0.5 因运算符优先级导致方差算错、相关系数全部失真——2026-08-24 协鑫+汾酒验证时暴露）⑩**个股组合验证**：协鑫(+0.2%)+汾酒(-37.7%) 相关 0.089、组合 -19.2%——"分散波动 ≠ 分散行业下行"，文案必须基于真实数据（汾酒一年深跌 -37.7% 是白酒行业回调，不是个股偶发）。
18. **回测引擎坑（能力 #1）**：①**本地 v_symbol/dim_symbol 的 name 列全为 NULL** → 股票名称必须 `symbol list` 远端拉取（--limit 10000 一次全量，bt_name_map.json 可复用）②**策略五要素确认**：买入时机/卖出时机/买入仓位/卖出仓位缺任何一项必须提示用户补充（不擅自假设，假设标 [ASSUMED]）③**连板高度是最敏感参数且"越高越差"**：二连板 -18.8%（26 笔/26.9%/-61.4%）vs 三连板 -83.57%（33 笔/15.2%/-87.79%），三板次日收阴概率 64% 追高即接盘 ④market_strong dict 的 key 类型（datetime.date vs str）不匹配导致恒 False → 统一 str(date)；**date 列必须 CAST AS VARCHAR 再进 Python dict（否则 json.dump 报 date not serializable）** ⑤**总收益含期末未平仓持仓浮动**，与最后一笔平仓后 equity（落袋口径）不同 → 报告注明双口径 ⑥涨停判定必须用前复权相邻日收益率（主板 +9.8%/创业板科创板 +19.8%），连板 streak 用"非涨停日分组+组内行号-1"窗口技巧 ⑦前复权数据必须显式标注（未复权数据回测除权股会误判涨跌停）⑧**SQL 信号列必须用 LAG 预计算 prev 状态**（prev_ma5/prev_ma20/prev_close2/prev_is_limit_up/prev_boll_upper），Python 端只读当日字段即可判定金叉/突破（否则需跨日字典，内存翻倍）⑨`--all` 需要在 argparse 注册（store_true），否则报 unrecognized arguments ⑩**配色正红负绿**：总收益/收益率正=var(--red)、负=var(--green)（A股惯例，06 对比表曾写反被用户纠正）⑪**卖出日=触发日次日**：所有卖出规则均为"触发日收盘后次日开盘成交"（策略定义如此，非 bug），报告明细须展示触发日（signal_date）列并注明口径，避免用户误读为"延迟一天卖出"；trades 记 signal_date+cand_cnt 字段 ⑫**候选选择规则必须写明**：当日满足买入信号常达数十上百只（海龟均值 245/日、RSI 821/日），统一取"当日成交额最大 1 只"（热度代理 [ASSUMED]），策略说明区须有"候选选择"行 ⑬**重跑引擎会覆盖结果文件的 name 字段**（引擎 trades 初始 name=ticker）→ 每次 `--all`/`--strategy` 重跑后**必须重新回填名称**（bt_name_map.json 驱动）再渲染报告，否则明细股票列显示代码而非名称
19. **股票全面分析坑（能力 #8）**：①**模板 CSS 必须先对照既有模板抄骨架**——kv 行 span 写 `flex:0 0 76px` 依赖父容器 `.kv{display:flex}`，漏定义则标签与数值粘连（"开盘33.42"，2026-08-24 用户发现）②**forward PE 必须显式**：利润高增股 TTM PE 高≠贵，锚定券商一致预期算 forward（中天 PE 34.2 / fwd 15.4）③市值=股价×股本估算 [ASSUMED]④券商预测/机构持仓/订单 WebSearch 补充须页脚标注 ⑤结论必须五维（结论/数据含义/情景/操作/跟踪）。
20. **W底形态信号坑（能力 #1，2026-09-02 新增）**：①W底需跨日形态检测（双底+颈线突破），SQL 预计算做不了 → `find_w_bottom()` Python 实现：右底=最近20日内最低、左底=右底前至少5日最低、两底价差±5%、颈线=两底间最高（须高于两底≥2%）、当前收盘>颈线=突破确认 ②同一形态只触发一次：`prev_break` 记录上次颈线价，新颈线需比旧颈线高 ≥1% 才再触发（否则突破后天天满足、反复买入）③`w_info` 在触发日记录 (颈线,右底) 供卖出用，买入时写入 position.w_neck/w_low ④卖出 `w_fail`：先判跌破右底（形态失败）、再判跌回颈线（假突破）——右底低于颈线，若跌破右底必已跌破颈线，顺序不能反 ⑤W底买点=突破确认次日开盘，假突破 10/21 靠"跌回颈线即跑"控制损失（平均 -3.5%），这是策略正收益的关键。
21. **ETF 回测坑（能力 #1，2026-09-02）**：①本地 DuckDB parquet 仅 A 股无 ETF → `fund history` 远端拉取转格式（注意远端字段 open_price/close_price/date_ms、amount 用 turnover 元）②`--parquet` 相对路径基于 BASE（工作区根）拼接，需 `--parquet .workbuddy/output/xxx.parquet` ③ETF 无涨跌停 → 打板类（streak_2/limit_low_open）天然 0 笔属正常，报告应说明"该策略不适用 ETF"④基准用 ETF 自身买入持有收益而非沪深300 ⑤ETF 分红除息未复权口径 [ASSUMED]（年化分红 ~2% 量级，回测信号影响有限）⑥单标的池交易样本少（0-6 笔），结论偏"策略-品种适配性"而非统计显著性 ⑦**fund history 必须 `--source remote`**（默认 auto 走 local，本地库无 ETF → 静默返回空 item）；窗口上限 5 年（超限报错 "window must not exceed five years"），老 ETF 拉长历史须分段 ⑧**远端数据深度有限**：fund history 老 ETF（510880）3-5 年窗口实测空（仅近 ~1.5-2 年有数）、index history remote 也仅回近 ~2 年（2016-2021 空）→ ETF/指数长历史走**公开行情源**（腾讯 web.ifzq.gtimg.cn fqkline 可拉 ETF 全历史：159758 上市 1127 条；参数 count≤2000 否则空返回）⑨ETF/指数无 valuation（FUYAO_3001）、无历史估值接口、无国债收益率接口 → 估值类策略需公开披露锚点（乌龟量化/理杏仁/研报）拼接。
22. **CLI command not found 排查（2026-09-02 用户澄清）**：**CLI/npm 全局包不会"丢"**——npm 全局包装在当前 node 版本目录下（`node_modules/@hithink-tech`），`hithink-finance` 是该目录的 shim。command not found 的根因几乎都是 **PATH 环境变量里的 node 版本路径与实际安装不符**（版本目录升级如 22.22.2→22.22.2-2 后 PATH 未更新，或手工 export 了记忆中的旧路径）→ 排查顺序：`which node` → `node --version` → `which hithink-finance` → `npm root -g`（确认全局包实际位置）→ 修复=把 PATH 的 node 版本路径改成实际目录（用户级环境变量），**无需重装 CLI/node**。**教训：不要凭记忆里的旧 node 路径写死 export**（2026-09-02 曾 export 22.22.2 旧路径致 command not found，误判"CLI 丢失"触发重装），一律先 `which` 定位。
23. **交易日历/最新交易日判定坑（2026-09-03 实测）**：①`market calendar` 返回**过去一年窗口**（2025-09-03→2026-09-03 实测 243 交易日，**含最近交易日**）→ 判断目标日/最近交易日可用，但**必须完整解析 JSON 取最大日期，禁止 `head -c` 截断看开头**（2026-09-03 曾 head -c 2000 看到全 2025 条目，误判"窗口不含 09-02"白白绕路——实际含）②**当日日K收盘后晚间才由服务端发布**：盘中 `data sync` 停在上一交易日 release（实测 09-03 盘中 sync → release `20260902/...`）→ **"最新完整交易日"= calendar 中 < 今天的最大日期**，盘中别把当天当目标（否则每次盘中误报落后并触发无谓 sync）③`index history` 盘中会返回**当日实时K**（volume 明显偏小）→ 不能作"已发布交易日"依据 ④日历判断与涨跌家数/指数数据要区分"目标日数据已收盘发布"与"盘中实时"两种时态。
24. **DuckDB 内存限制坑（2026-09-03 实测，数据更新必读）**：CLI 默认 DuckDB 内存上限=`min(1GiB, 25% 物理内存)`（connection.js 硬编码），本地库 ~750MB 时 `data sync` 增量 commit 报 `CLI_INTERNAL_ERROR: failed to pin block ... (1023.7 MiB/1.0 GiB used)` 失败（下载成功但入库失败）→ **修复=设用户级环境变量 `HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT`（格式 `512MiB`/`2GiB`/`4GiB`，非法值报 DUCKDB_CONFIG_INVALID）**：`setx HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT 4GiB`（15.8GB 机器已设）；另有 `HITHINK_FINANCE_DUCKDB_THREADS`（1-64 整数）限线程。**增量同步包名 `daily-k-10d` = 只覆盖最近 10 自然日（≈7 交易日）→ 落后 >10 自然日必须全量重拉**（签 URL→下载 daily-k+adjustment-factors→`data init`→验证，见 ensure_data.py docstring 指引与 references/回测引擎指南.md 数据初始化章节）。
25. **涨跌家数与情绪 JSON 结构坑（能力 #6，2026-09-02/03 实测）**：①涨跌家数获取链：**先过数据门禁**（本地库落后→查询为空）→ 本地 `raw_kline_daily` 用 `close>open` 统计（列名 close/open/date，无 close_price 列不触发 DB_READ_ONLY 误判）；本地缺目标日时 **WebSearch 公开披露兜底且页脚显式标注**——**新闻口径涨停数常含未开板新股**（2026-09-02 新闻 54 家 vs hithink 涨停池 49 家），主体用 hithink 口径并注明差异 ②JSON 结构：limit-up/limit-down/limit-break-pool = `data.item[]`（或直接 list）；**dragon-tiger = `data.stock_items[]`**（与普通榜不同），同股可多条上榜**须按 ticker 合并净额**；**concept_list 为结构化 list**（`[{name:...}]` 非字符串），org 版字段 org_net_value/org_buy_num/org_sell_num；炸板池当日无炸板时为空数组要兼容。
26. **ETF 估值与 fund 命令签名坑（能力 #4 ETF 版，2026-09-03 实测）**：①**fund 家族命令签名不一致**——`fund snapshot`/`fund history` **无 `--fund-type`**（直接 `--thscode <代码>`，加会报 unknown option）；而 `fund profile`/`fund holdings`/`fund dividends` **必须 `--fund-type exchange`**；另 `fund snapshot` 单只用 `--thscode`（复数 `--thscodes` 是 market/valuation snapshot 用的）——**先 `--help` 确认再拼参数，勿凭记忆** ②**ETF/指数无估值接口**：`valuation snapshot --thscodes <ETF>` 报 `FUYAO_3001`（Target not found in A-share code table，ETF 不在 A 股代码表）→ ETF 估值**必须走公开指数估值源**（A股行情指标表 cs931468/乌龟量化/中证官网/理杏仁），页面显式标注"同花顺不含 ETF/指数估值接口" ③**`index` 接口正则白名单只认 `\d{6}\.(SH|SZ|BJ|TI)`**——中证指数（如红利质量 931468.CSI）不被覆盖，`index history` 报 Invalid string、`index snapshot` 报 FUYAO_1002 → 放弃 CLI 拉 CSI，指数估值/历史全走 WebSearch/公开源 ④**`fund profile` 无跟踪指数字段** → 跟踪指数识别靠 WebSearch"<基金名> 跟踪指数 代码"（159758 → 中证红利质量 931468.CSI）⑤**指数发布年数 vs 分位窗口**：931468.CSI 发布于 2020-05（约 6 年），公开源的"10 年分位"是外推口径 → 页面标 [ASSUMED] 并注明"发布以来" ⑥指数股息率口径（近1年/近12个月）与分位时点多源不一致（主源+辅助源并列标注，不硬取一个数）。
27. **板块轮动/指数历史与数据同步坑（能力 #7，2026-09-04/05 实测）**：①**`index history` 的 `data.item[]` 为时间升序**（item[0]=最早，**最新交易日=item[-1]**）——09-05 曾取 [0] 把窗口首日（6 月初）当最新，成交额/动量全错位；取最新务必 `item[-1]` 并校验 date_ms == 目标交易日 ②**gen_rotation v1.3 的 hero KPI/三处 insight/表格 hint 硬编码在 TPL**（docstring 谎称"insight 全在数据区"，换周期必留旧板块旧数值，新数据版仍输出旧 hero 值）→ **v1.4 已全占位符化**（KPI/TABLE_HINT/INSIGHT_TABLE/SIGNAL/FLOW/HL 进数据区）③**同文件多处 Edit 并行提交会互相覆盖**（后写赢、先写静默丢失且工具仍报 success）→ 同文件编辑必须串行，改完双查：占位符残留 + 旧特征值残留 ④**`ensure_data.py --check` 与 `--yes` 分支判定不一致**（check 报落后 1 天、yes 却打印全量重拉指引）→ 增量更新直接 `hithink-finance data sync`（CLI 内部自判增量/全量），记得显式注入 `HITHINK_FINANCE_DUCKDB_MEMORY_LIMIT=4GiB`（坑 24）⑤**`index catalog --tag industry` 返回 300+ 条**（含 884xxx 细分、部分 881xxx 名称与常识不符）——按关键词选板块须先查 catalog 实际名（881101=种植业与林业、881102=养殖业、881156=保险、881169=贵金属），勿凭记忆拼名 ⑥板块数可变（22→26+），数量表述/基准涨跌必须数据区驱动，禁止写死 TPL ⑦**轮动表资金列当日成交额**：取 idx json 最后一条 turnover/1e8（元→亿），与动量行一一对应。
28. **Windows 重定向/文本文件喂 CLI 参数带 \r（CRLF）坑（2026-09-07 实测，批量拉取必读）**：python `print('\n'.join(codes)) > codes.txt` 在 Windows 会把 stdout 的 `\n` 转成 `\r\n` → bash `while read c` 取出的每行带尾 `\r`，`index history --thscode 881101.TI\r` 报 `CLI_BAD_ARGUMENT Invalid string: must match pattern /^\d{6}\.(SH|SZ|BJ|TI)$/iu`——**26 板块批量循环全 FAIL、手动单条却 OK**（迷惑性极强，先误判为接口/网络问题）→ 排查：报错若是"正则白名单/Invalid string"类，先查变量行尾是否带 \r（`cat -A file` 看 `^M$`）；修复 `sed -i 's/\r$//'` 或 `c=$(echo "$c" | tr -d '\r')`。**规避**：python 写清单显式 `open(f,'w',newline='\n')`，或干脆不用"文件→while read"链路（bash 数组/直接内联循环）；文件名含代码后缀建议统一 `tr '.' '_'`（idx_881101_TI.json）避免层层 `%%.` 截断混乱。
29. **财务报表期数与口径坑（能力 #8/#12 验证关卡，2026-09-08 实测）**：①`financials income --period quarterly` 的 **Q2/Q3/Q4 行 = 年初至今累计**（茅台 Q2 行营收 907 亿=中报累计、Q1 行 539 亿=Q1 累计；单季须 Q2行−Q1行）——把"最新季行"当单季会高估营收/净利（用归母绝对值对照中报披露复核：中京电子 H1 行 -0.90 亿 = 中报亏 8985 万 ✓）②`financials indicators --report YYYY-N` 的 N=**报告期序号**（实测 N=2 → 中报 2026-06-30，N=4 → 年报；"最新已披露报告期"用 income quarterly 的 fiscal_year/fiscal_period 字段反推）③indicators 的 growth/ROE/毛利率/净利率 value **已是百分数**（茅台 H1 归母同比 "-1.95" 直接加 %）④字段名：扣非 ROE=`index_deduct_weighted_avg_roe`、加权 ROE=`index_weighted_avg_roe`；income 行内归母=`parent_holder_net_profit`、营收=`operating_income`。
30. **PE(TTM) 为负/极端 ≠ 基本面差，必须先查原因（能力 #8 验证关卡，2026-09-08 实测）**：①PE_TTM<0 = TTM 窗口亏损，**先 WebSearch 核实一次性还是经营性再判**——北大荒 H1 -5.37 亿系**一次性补缴 2021-25 所得税+滞纳金 14.1 亿**（6 月缴清、无行政处罚、扣非亏损同源于此、Q1 主业仍 +7.8%）→ 事件性利空出清=保留（谨慎档）；金正大 -4.97 亿系**经营性由盈转亏**（ROE -26.6%、流动比率 0.88、PB 5.09）→ 否决 ②**当日涨停/连板池 90% 是 PE<0 或 PE>50 的题材弹性票**（2026-09-08 PCB/存储/传媒方向实测：中京电子 H1 亏、盈发展 TTM 亏毛利率 3.3%、景旺 PE 90/归母 -7.4%、出版传媒 PE 47/归母 -26%、慈文营收 -90%、华盛昌 20日+54.5% 妖股位）→ 能力 #12 验证关卡批量筛法：`valuation snapshot`（PE_TTM/PB/PS）+ `financials indicators --report <最新期>`（营收/归母同比+ROE）双字段快筛，**同题材选基本面最强补位**（金正大 → 粤桂股份：同为磷肥首板，粤桂 H1 归母 +182.8%/ROE 15.8/PE 21.5 vs 金正大 -534%）③涨停池题材标签在 `limit_up_reason`（非 concept_list，坑 6）；valuation snapshot 返回带 name 字段（涨停池常缺 name，可交叉映射）。
### 其他已知坑

- `financials indicators --report` 若无当期数据会报 `FUYAO_5003`（空结果）→ 换相邻报告期重试。
- 本地 raw_kline_daily 未复权；复权用 `market history --adjust forward --source local`。
- 个别百分数指标（growth 同比等）值本身就是百分数。
- 模板换日期后必须 grep 旧日期/旧个股名，清理硬编码残留。

## 2026-09-09 追加（31-33）

31. **db export parquet 的 date 列类型不定（坑，2026-09-09 实测）**：`db export --file-format parquet` 导出的 date 列可能是 **datetime.date 对象**（09-09 实测）也可能是 str（09-08 导出版）——W底/新高扫描脚本 `last["date"] != "2026-09-09"` 字符串比较对 date 对象**恒 False → 全部股票被跳过 → 扫描 0 只假阴性**（先误判"当日无信号"，实为类型 bug）。**修复：pd.read_parquet 后一律 `df["date"] = df["date"].astype(str)` 兜底**（脚本内写死，不依赖导出端）。排查法：发现扫描 0 触发先查 dtype 与首行比较。
32. **market/valuation snapshot 与指数的兼容性（2026-09-09 实测）**：①`market snapshot` 不支持指数代码（000001.SH → FUYAO_1002 Unknown A-share thscode）→ 指数涨跌收盘用 `index history` 拉含目标日与前收的窗口自算（坑 7）②`valuation snapshot --thscodes` 批量有上限（38 只报 CLI_BAD_ARGUMENT，20 只/批可过）→ 大批量候选分 20 内一批 ③`fund snapshot` 返回**无 name 字段**（只有价格/量/额）→ ETF 名称用 `fund profile --fund-type exchange` 补（512400=有色金属ETF南方 已核）或公开口径。
33. **calc/build 脚本 sed 复制后硬编码文件名对不齐（2026-09-09 实测）**：`sed 's/reco_0908/reco_0909/g'` 不会命中 `rotation_0908.json` 这类**非 reco_ 前缀的 _0908** → 复制脚本落盘名仍是旧目录名（打印 "Saved rotation_20260909.json" 实际写 rotation_0908.json，TARGET 变量打印与实际 open() 不一致）→ **sed 批量改造后必须 grep 全部 open()/json.dump 目标文件名逐一核对**；日期替换同样要显式 `s/2026-09-08/2026-09-09/g`（教训：calc 脚本 open 名与打印名不一致拖慢 2 轮 debug）。

## 2026-09-10 追加（34-35）

34. **市场热度类指标必须按「温度」配色，不按当日涨跌**（能力 #12，2026-09-10 用户明确要求）：**个股涨跌看方向（红涨绿跌），市场热度看温度（涨停家数/封板率等恒红 `.hot`）**。09-10 深度普跌日曾把热度指标误填 `dn`（绿）——热度是「有多少股在涨」，不是「指数涨还是跌」。
    改完须 `grep 'class="chg' ` 统计 up/dn 分布核对（只看「有没有颜色」是查不出来的），并确认涨跌方向的类名是按数值正负判定的（不是写死）。
35. **短线技术指标自算口径（能力 #12 v1.2，2026-09-10 实测）**：技术指标一律用**本地前复权** `v_daily_qfq` 导出的 parquet 自算（`market history` 远端复权在早期历史有 ~2pct 精度差，坑 5），**禁止凭印象填数**。口径：MA 用简单均值（`np.mean(close[-n:])`）；**RSI14 用 Wilder 平滑**（首值取前 14 日涨跌幅均值，之后 `(prev*(n-1)+cur)/n`，全跌时 ad=0 → 返回 100 需特判）；MACD 用 EMA12/EMA26/DEA9（`k=2/(n+1)`，初值取首收盘，柱 `(DIF-DEA)*2`）；量比 = 今量 ÷ 前 5 日均量（**注意：与交易所口径"5 日同期分钟量"不同，报告须用"自算"标注**）；布林 %B = `(收盘-下轨)/(上轨-下轨)*100`（20 日 ±2σ）；关键位 = MA5/10/20/60 或 20 日高低/颈线。判读阈值：**RSI>70 + %B>100 + 乖离 MA20>8% = 短线超买（操作只给回踩位）**；%B<0 或 RSI<30 = 超卖。注意 parquet 的 date 列类型先 `astype(str)`（坑 31）。

## 2026-09-10 追加（36-40）· 9 大短线策略回测

36. **回测一律直接用 skill 里的脚本跑**（用户 2026-09-10 晚确立，仍生效）：`python <skill>/scripts/bt_backtest.py --all`——**不要把脚本复制到工作区后再跑**，保证「能跑的永远是 skill 内版本」。策略定义也以 skill 内 `strategies.json` 为准（同目录解析，可用环境变量 `THS_STRATEGIES` 覆盖）。
38. **DuckDB 窗口函数不能嵌套**（能力 #1 SQL，2026-09-10 实测）：写 `AVG((high-low)/NULLIF(LAG(close) OVER (...), 0)) OVER (...)` 报 `Binder Error: window function calls cannot be nested`。**窗口函数内不能再套窗口函数**——解法=用同一 SELECT 里已算好的普通列（如 k2 阶段已算的 `prev_close`）替代内层 `LAG(...)`，或在更早的 CTE 层先物化该列。
39. **连续 N 根阳线不能用累计 SUM 代替（真实连续长度的正确算法）**（能力 #1 SQL，2026-09-10 实测，隐蔽性高）：`SUM(CASE WHEN close>open THEN 1 ELSE 0 END) OVER (PARTITION BY thscode ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` 得到的是**全历史累计收阳数（实测高达 168）**，不是"截至当日的连续长度"→ 使 `cnt_up>=3` 类条件**恒不成立**、`first_red_pullback` 策略 0 笔交易（**且不报错、静默返回 0 笔，极易漏检**）。正确算法=**「收阴日分组 + 组内行号」**：`ROW_NUMBER() OVER (PARTITION BY thscode, grp ORDER BY date)`，其中 `grp = SUM(CASE WHEN close>open THEN 0 ELSE 1 END) OVER (PARTITION BY thscode ORDER BY date)`，并对阴线日置 0。**同类陷阱**：判断"昨日是否长阳"必须取 `LAG(cnt_up)`（`prev_cnt_up`）——阴线当日 `cnt_up` 恒为 0，用当日值判断"前有长阳"永远失败。**排查经验：策略返回 0 笔时先查该信号依赖的字段分布（`GROUP BY 字段` 看取值范围），而不是先怀疑数据。**
40. **单笔驱动型"高收益策略"必须做剔除最大单笔的稳健性检验**（能力 #1 方法论，2026-09-10 实测，最重要的一条）：`strong_pullback_ma20` 回测总收益 **+161.2%（20 策略排名第 1）**，但**剔除单笔 +143.41%（688820.SH，2026-04-29 买入、16 个交易日 +143%、该股 92.5→229 元含多板）后仅剩 +0.8%**，35 笔中位数单笔 **-1.05%**、平均 +4.41% 全由极值拉动（前 4 大单笔 +143.4/+26.1/+21.0/+20.2%，其余 31 笔合计近零）。**教训：单标的满仓 + 短样本期（242 交易日）+ A 股极端个股行情 = 极易产出"幸存者偏差"式漂亮曲线**。**通用做法：①任何策略排名先算"剔除最大单笔/前 3 大单笔"后的收益 ②报告中对该类策略显式标注"表面第 N · 实为单笔驱动"并给出剔除后数值 ③横向对比表的排序结论不得只看总收益。** 交叉验证：该笔数据已核（688820.SH 真实 K 线确为 92.5→229 元），属真实行情而**非**数据错误——即"数据无误的假优势"更难识别。
42. **数据版脚本「数据区变量名」必须与模板渲染段完全一致**（能力 #7 / #12 通用，2026-09-11 实测）：日更做法是「读 skill 模板 → 正则替换数据区 → 写出 `gen_xxx_日期.py` → 运行」。替换区由标记界定（`# ================= 数据 =================` … `# ================= 渲染 =================` 或 `DATE = "…"` … `# ---------- 渲染 ----------`），因此**模板渲染段引用的每一个变量名都必须在数据区被定义**。09-11 踩坑：`gen_reco_picks.py` 渲染段用 `EVID`（第 5 列=能力#8 验证），数据区误写 `EVIDENCE` → 运行即 `NameError: name 'EVID' is not defined`（在 `stock_card()` 内、报错行号远离数据区，易误判为渲染 bug）。**排查口诀：数据版运行报 `NameError` → 立刻把模板渲染段用到的变量名全部 grep 一遍，逐一对齐数据区**（数据区变量清单在各模板 docstring【数据区】行，如 reco = DATE/GEN/BANNER/KPIS/IDX/LINES/INSIGHT01/INSIGHT03/STOCKS/EVID/AUDIT_ROWS/NOTE/CLS）。
43. **报告中描述个股当日涨跌必须回读快照确认是否「涨停」，禁止凭印象/凭板块热度写**（能力 #12，2026-09-11 实测）：当日 PCB/覆铜板为资金主线，撰写时把资金榜第一的**金安国纪写成「涨停」**，实际其收盘 **+7.86%（未封板）**——`market snapshot` 的 `price_change_ratio_pct` = 7.86 已明确。**通用做法：①凡文字里出现「涨停/封板/连板」字样，必须与该股 snapshot 的涨幅、涨停池名单、`limit-up-ladder` 三处交叉核对 ②主板涨停≈+10.0%（封板价四舍五入后可能显示 9.93%/9.98%/10.00% 等，属正常）③科创/创业板 20%、北交所 30% ④用词分级：「涨停」「封板」「涨 X%」不可混用。** 另：`special *-pool` 与 `limit-up-ladder` 均以 `data.item[]` 返回（**不是** `stock_items`），而 `dragon-tiger` 用 `data.stock_items`——同期命令结构不统一，取值前先探结构。

## 2026-09-16 追加（44-49）

44. **数据版脚本的数据区是「整段替换」→ 模板数据区里定义的变量必须自己重新定义**（能力 #7/#12 通用，2026-09-16 实测）：日更链路的 `build_reco_html_日期.py` 以 `src.index('DATE = "…"')` → `src.index("# ---------- 渲染 ----------")` 为锚点**整段替换**模板数据区。该区间里模板自己定义的东西（`BT_SCOPE`/`BT_WB`/`BT_TURTLE` 等 **12 个 `__BT_*__` 回测数值**、`GEN`、`CLS`、`N` 等）**会被一并覆盖** → 渲染段引用时报 `NameError: name 'BT_SCOPE' is not defined`。**对策**：自己的数据区必须**重新定义该区间内的每一个变量**；改完先 `python gen_xxx_日期.py` 干跑一遍，报错即补。

45. **⚠️ 复盘必须用「最终交付版」报告，且解析名单必须匹配「推荐卡结构」**（能力 #12 复盘，2026-09-16 实测，**曾导致整份复盘结论偏移**）：同一日期可能有多份报告——`精选5股推荐_20260908.html` 是**跑能力#8 验证之前**的版本（含后被剔除的金正大/上海电影/中京电子），**最终交付版是 `精选5股推荐_20260908_验证版.html`**。若用「抓全文所有代码」的方式取名单，会把**正文/证据矩阵里提到的未入选标的**当成推荐。**正确做法**：匹配推荐卡标记 `class="nm"` + `class="tcode"`，并**容许额外属性**（历史报告被注入过 `data-page-node-id="…"`，插在 `class="no"` 与 `class="nm"` 之间，正则一严就匹配不到）。**用错名单的后果**：平均收益 −1.73% 被算成 −2.61%、最差 −13.65% 被算成 −25.54%，并据此得出「止损 −5% 最优」的错误结论。**复盘统一改用 `scripts/review_picks.py`，不再手写解析。**

46. **报告是 HTML，数据区里禁止写 markdown `**加粗**`**（能力 #7/#12，2026-09-16 实测）：HTML 不解析 markdown，页面上会**原样显示星号**。一律用 `<b>…</b>`。**验收清单必须加一项「残留 `**` 计数 = 0」**。

47. **"垫底"必须区分「今日涨跌」与「N 日动量」**（能力 #7，2026-09-16 实测）：普涨日里 20 日动量垫底的板块当天也可能是红的。混着写会产出「化学制药 +0.58%（20日 -5.28% 垫底）」这种自相矛盾句，读者无法判断到底在跌还是在涨。**写法**：「今日唯一下跌的 5 个方向是 …；另一组是 20 日动量垫底（今日随大盘小涨）的 …」。

48. **CLI 参数与返回结构的五个易错点**（2026-09-16 实测，一次踩齐）：
    - `special limit-up-pool --size` **上限 200**（>200 报 `CLI_BAD_ARGUMENT: Too big: expected number to be <=200`）；
    - 龙虎榜返回结构是 **`data.stock_items`**（不是 `data.item`），字段含 `thscode/net_value/org_net_value/concept_list`；`data.hot_money_items` 常为空；
    - **`valuation snapshot` 用 `--thscodes`（复数、逗号分隔、最多 100 个）**，而 **`financials income` 用 `--thscode`（单数）**——两者签名不一致，用错会静默返回空；
    - `financials income` 的营收/归母字段是 **`operating_income` / `parent_holder_net_profit`**（不是 `revenue`/`net_profit_atsopc`），且 **Q2/Q3/Q4 行＝年初至今累计**（同比须与**上年同 `fiscal_period`** 比）；
    - 需要 `duckdb` 读写 parquet 时，**`versions/3.13.12` 的 python 没有 duckdb**，要用带 duckdb 的解释器（如 `envs/default/Scripts/python.exe`）。

49. **`index history` 的 `--start-ms` 必须回溯足够长**（能力 #7 日更链路，2026-09-16 实测）：算 60 日动量至少要 **61 个交易日**，只回溯 1 个月拿不到 60 根 → `calc_rotation_*.py` 的 `problems` 必非空、动量列大面积 `[MISSING]`。**经验值：`--start-ms` 取目标日前约 4 个月**（≈85~92 个交易日，与 `reco_0911` 窗口一致）。

### 方法论补记（不是 CLI 坑，但同样重要）
- **「事后归因」不等于「可执行规则」**：复盘时若按"结果"给标的贴标签（如"左侧标的""退潮链"），分组差异会非常好看；但换成**事前可算的特征**（动量/涨跌/均线位置/距高点距离）再分组，往往全部失效——2026-09-16 首次复盘实测就是如此（20 日动量甚至**反向**）。**判据：一个分组如果只在事后成立、换成事前可算特征就消失，它就不是规则。**
- **任何策略排名/评价先做「剔除最大单笔」检验**（与坑 40 同源）：首个复盘样本"剔除最大盈利单笔后 −2.43% 比原 −1.73% 更差"→ 说明**不存在靠一笔撑起来的假优势**。

## 2026-09-17 追加（50-56）· 单标的批量跑能力时实测

50. **`financials indicators --report` 必须用 `YYYY-Q` 格式**（如 `2026-2`）：传 `2025-FY` / `2025` 等会**返回空且不报错**（`ok:true` 但无数据），静默失败。**排查口诀**：indicators 取不到就先换成 `2026-2` 试。另注意 `--report` 的季度号是**自然季度**（2 = 中报）。

51. **`db export --file-format json` 不可用**（导出输出为空、目标文件 0 字节，不报错）。要拿本地库数据为 JSON 用 **`db query --sql "..." --format json`** 直接取（结果在 `data` 数组里）；`--file-format parquet` 正常。

52. **数据区里不能写引用构建器变量的 f-string**：把 `f"市值约 {mcap:.0f} 亿"` 当**字面量文本**写进数据区时，生成的脚本里 `mcap` 不存在 → `NameError: name 'mcap' is not defined`。**数据区必须是纯字面量**：先在构建器里算好、把数字直接写死进去。

53. **用 `re.sub` 做数据区替换时，替换内容必须用 lambda**：`pat.subn(txt, src)` 会把 `txt` 里的 `\` 当转义 → 路径含反斜杠时报 `re.error: bad escape \o`。正确写法：`pat.subn(lambda _m, _t=txt: _t + "\n", src, count=1)`。（旧 `build_*_verify.py` 因替换内容不含反斜杠而侥幸没暴露。）

54. **⚠️ 数据区替换必须带 `NAME = ` 前缀（本项目排查成本最高的一条）**：模板里数据区是「`NAME = 值`」整体被匹配替换，若替换内容只给「值」而不带 `NAME = `，赋值会**静默退化成裸表达式**（`{...}` 或 `[...]` 单独一行）——**不报任何错**，直到后面某处引用该变量才 `NameError: name 'DIVS' is not defined`，而报错行与真正出错的数据区相隔很远。**口诀**：替换后先 `grep "^[A-Z_]* ="` 数一遍变量个数，比模板原版少了就是漏了前缀。

55. **只替换数据区不够：`DATE` / `WEEKDAY` 必须一起替换**（各模板顶部有定义）——它们决定**产物文件名**（`{comp_name}_{DATE 去连字符}.html`）。不替换会产出 `估值仪表盘_冠盛股份_20260821.html` 这种「数据是今天、文件名是模板日期」的错配。
    - **`<title>` 必须与产物文件名同口径**（`名称_主体_日期`，如 `穿透分析_冠盛股份_20260917`）——**新增/改模板时逐项核对**；title 缺主体名/缺日期会让浏览器标签、书签、多报告对比时分不清是哪只标的（文件名对、title 错）。默认数据区里的 `title 样例` 也要一起对。

56. **`HIST`（传模板的历史K文件）两个硬要求**：
    ① **只保留 6 个字段** `date/open/high/low/close/volume`（与旧 `build_*_verify.py` 的 `bars.append` 一致）——本地 `db query` 直出的行还带 `thscode/ticker/amount/batch_id`，多余字段会进 JSON 甚至 SVG；
    ② **前复权价必须 `round(x, 2)`** —— `v_daily_qfq` 的复权价是**未 round 的浮点**（实测 `32.28948721977792`，17 位），会显著加长数值文本与图表坐标（实测同一窗口 JSON 34.2 KB → 25.5 KB）。
    **另**（2026-09-17 更新，原结论已作废）：速览卡的走势图**现在恒为 252 个点**，与传入 HIST 的根数**无关**——实测喂 255 根与 1223 根，成品体积 101230 / 101229 字节（差 1 字节，属随机波动）。所以**不存在「给多了把图表撑大」的问题**，多喂的历史 K 只用于**指标预热**（窗口左端 MA20/MACD/KDJ 才是有效值）。原「只需 250~320 根」的说法来自修复前的实现。**速览卡成品体积正常量级 ≈ 96~100 K 字符**（对标 `山西汾酒_20260821.html` 96,172 / `紫金矿业_20260821.html` 100,311；**不要拿 `估值仪表盘_*.html` 的 30 KB 做基准，那是另一个能力**）。

## 2026-09-17 追加（58-60）· 批量跑 #2/#3/#4/#5/#9 时实测

58. **数据区（`'''...'''` 块）里禁止出现裸 ASCII 双引号**：中文引号必须写成 `「」`（或全角 “”）。写 `不是"有没有增长"，而是` → 生成脚本 `SyntaxError: invalid syntax. Perhaps you forgot a comma?`。**更隐蔽的一点**：写成**转义形式** `\"有没有增长\"` 在 `'''...'''` 里会被还原成裸 `"`，**同样报错**；而排查时搜未转义形式**搜不到**（因为文件里是 `\"`）——**这是本轮最费时的一处**。

59. **⚠️ 批量用正则替换中文引号时极易误伤 `", "` 元组分隔符**：本项目曾用「汉字 + `"…"` + 汉字」的正则批量把裸引号换成 `「」`，结果**把 18 处合法的 `", "` 分隔符也改了**（因为 `段", "下` 两侧都是汉字），把构建器写坏。**安全判据**：加一条排除「引号内内容为纯 `,` / 空白」的条件；或者干脆不要批量改，只按报错行逐个精确修。

60. **各模板的数据区变量集并不一致，别凭一个模板的清单去套另一个**：
    - `gen_penetration_zjky.py` 的 `CFG` 除 `out_tag/name/code/verdict/verdict_short/verdict_note` 外**还有 `kpis`**（`[(值, 标签, class)]`，class 如 `gd`/`up`/`dn`/`""`）——只看前几行会漏掉，触发 `KeyError: 'kpis'`；
    - `gen_earnings_calendar.py` **没有 `WEEKDAY` 变量**（替换时未命中属正常，不是错误）；
    - `gen_tearsheet_stock.py` 的 `HIST` 指文件路径、`CONFIG` 键最多（含 `report_label/report_hint/rpt_*_lab/xd/div_amt/quote_date`）。
    **做法**：动手前先把该模板「渲染段之前的全部顶层赋值」列一遍（含跨行块要看清全貌，不要只看前 5 行）。

## 2026-09-17 追加（61-62）· 指标口径与模板契约（不是坑，是必须遵守的规则）

61. **「近1年涨幅 / 52周高 / 52周低」统一口径 = 最后交易日回溯 252 个交易日**（能力 #2 / #8 / #4）
    - **速览卡模板（#2 个股 + ETF）已内置该窗口**：喂多少根 K 线都不改变口径，多喂的历史 K 只用于**指标预热**；数据不足 252 根时按区间值算并打 `⚠️ [WARN]`。
    - **但 #8 全面分析 / #4 估值 等模板的这三个字段是「数据区输入」，由调用方自己算** → 必须显式取最后 252 个交易日再算首尾涨幅与高/低。
    - ⚠️ **不要直接把一段 K 线的首尾/极值填进去**：喂多长它就变成「近多长」（喂 5 年 → 页面标着「近1年涨幅」却是 5 年涨幅，且 X 轴也画成 5 年），**全程无告警、数字看起来正常**，属最难发现的静默错误。

62. **两个速览卡模板的数据区只放「原始 K 线」**（个股 `bars` / ETF `items`），**窗口、指标、52周口径一律在渲染区**
    - 消费者若用「**整段替换数据区**」的方式复用模板（如量化平台 `backend/app/render/caps/*.py`），**只需提供 `bars`/`items`**，其余由渲染区自算。
    - ⚠️ **不要把数据派生/窗口逻辑写回数据区**：写在那里会被替换掉（等于没改），而且渲染区一旦引用数据区里不存在的新变量，消费者侧会直接 `NameError`（本次实测踩到）。
    - 判断口诀：**「渲染区保留、数据区被替换」——能被替换掉的地方，就不是放修复的地方。**
