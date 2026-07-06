# 国内互联网大厂Coding/Work类AI产品研究 — 世界模型 (world_model)
_自动生成 · 覆盖度: L0=1 L1=11 L2=45 L3=23 来源=13 · schema v2_

## 1. 主题概览 / Worldview
- **中国AI编程/工作台市场在2026年Q2–Q3进入商业化加速期：腾讯WorkBuddy、字节Trae Work、阿里Qoder三家形成寡头格局，均完成免费→收费转型，积分/Credits加权计量制成为主流计费范式。这一转型的结构性驱动力是Agent模式下算力成本的指数级跃升（大上下文窗口、多轮Agent调用、模型间5–10倍成本差），使传统请求次数制下的交叉补贴不可持续。Trae Work国内版是目前唯一的次数制坚守者——这是面向非技术用户的获客策略与成本现实之间的赌注。国内定价约为全球40%的低价策略在用户获取上有效，但与持续上升的Agent成本形成根本张力。关键信息缺口包括：社媒端用户反馈完全缺失（当前所有证据来自web）、企业端采纳与留存数据缺失、独立算力成本审计缺失、以及Trae Work国内版切换计量制的时间窗口和临界条件不明。**  _(confidence: medium)_

### 版本历史 / Version History
_世界模型随每次 condense 迭代；下方为已被取代的旧版本（当前版本见上）。_
- _[2026-07-06 13:29]_ 国内AI编程/工作台市场已形成腾讯WorkBuddy、字节Trae、阿里Qoder的BAT三足鼎立格局,三家均完成商业化并从'代码辅助补全'升级为'AI员工/…  _(supersedes: `wv-8843c7643785`)_
- _[2026-07-06 12:24]_ 截至2026年7月，国内BAT三家（腾讯WorkBuddy、字节Trae Work、阿里Qoder）在AI Coding/Work工作台赛道已完成商业化起步，…  _(supersedes: `—`)_

## 2. 开放问题 / Open Questions
- [ ] Trae Work国内版何时/是否切换Token/Credits制?其'免费够用'获客策略与单次Agent成本上升之间的临界点在哪?
- [ ] 重度用户在积分/Credits制下的真实月成本是否真的比次数制更贵/更省?缺用户实测账单与社媒对比数据
- [ ] 国产模型(GLM-5.2/DeepSeek/MiniMax)的算力基建差距(如GLM-5.2慢2倍)如何转化为各产品的系数定价与用户积分消耗?
- [ ] 三家B端企业市场(企业版¥99–199/席位)的采纳、留存与付费转化对比数据?
- [ ] 社媒(XHS/抖音/X)上开发者对各产品计费模式转换的真实反馈、抱怨与流失信号——当前证据全web,缺独立社媒验证
- [ ] 厂商'成本倒逼'叙事 vs 独立算力成本审计:涨价(如Qoder企业版+25%)与切制中含多少正当成本、多少趁机提价?
- [ ] 社媒（XHS/抖音/X）上开发者对三家产品计费模式转换的真实反馈、抱怨与流失信号——这是当前最关键的证据缺口（全web、零社媒），下一轮检索应优先用xiaohongshu-mcp搜索小红书、用webbridge-mcp搜索X/抖音获取活人评价
- [ ] Trae Work国内版从次数制切换Token/Credits制的触发条件与时间窗口：是Agent成本突破某个阈值？还是竞品市场压力？还是用户增长见顶后寻求ARPU提升？
- [ ] 重度用户在积分/Credits制下的真实月消费 vs 次数制下的历史消费——需要用户实测账单对比而非产品定价表推算
- [ ] 企业端市场（¥99-199/席位）的真实采纳：Qoder号称1万+企业客户，但留存率、付费转化率、与WorkBuddy/Trae Work的B端份额对比完全缺失
- [ ] 国产模型算力差距（GLM-5.2慢2倍）如何实际影响各平台的积分消耗和用户体验——这决定了'模型系数'设计是合理的成本分摊还是隐性的用户体验牺牲

## 3. 分主题综合 / Themes (L1)
### [established · high] theme _(facet: f_ai_coding_work_vs_vs_token)_
国内AI编程/工作台市场已形成BAT三足鼎立格局:腾讯云CodeBuddy团队的WorkBuddy(桌面AI智能体工作台,定位"能干活交付"而非聊天工具)、字节Trae产品线(国际版trae.ai + 国内版Trae Work)、阿里Qoder(原通义灵码,2026-05-20更名),三家均已完成从免费到商业化收费的转型。三家的共同演进方向是从"代码辅助补全"升级为"AI员工/Agent工作台":WorkBuddy的多专家Agent协作、QoderWake 7×24 AI员工、Trae Work的飞书自动化。这一Agent化演进是后续计费模式重构的根本前提——单次任务触发的token消耗量级跃升,使旧有粗粒度计费难以为继。

### [established · high] theme _(facet: f_ai_coding_work_vs_vs_token)_
中国主流AI编程/工作台正经历行业性的计费模式重构,从"请求/对话次数制"转向"按Token/积分(Credit)的细粒度计量":WorkBuddy自2026-07-01起实行积分制(标准版4000积分/月,按模型系数消耗,MiniMax系数0.18、DeepSeek 0.30);Trae国际版2026-02-24由次数制切Token五档(Free/Lite/Pro/Pro+/Ultra,用户测算Pro权益缩水至原约1/5);Qoder以Credits统一计量(代码补全与Next Edits全版本免费、其余功能消耗Credits、模型调用失败不扣费)。早期采用次数制的逻辑被清晰解释:Token对非技术用户难理解、"X次/月"契合SaaS订阅心智利于获客、2025年初上下文小且Agent弱可借鉴Cursor/Copilot惯例、规避Token焦虑。唯Trae Work国内版仍保留对话次数制(近期由每日限额改为每周限额),其暂留被归因为目标用户更广(非技术用户对Token接受度低)+主打"免费够用"获客策略。

### [established · medium] theme _(facet: f_ai_coding_work_vs_vs_token)_
AI编程工具计费存在一个结构性产品-成本矛盾:用户体验要求计费单位简单易懂(次数/积分),成本结构却要求精确匹配token消耗。积分/Credits制是主流折中——用抽象系数层(WorkBuddy按模型系数、Qoder按任务复杂度+模型)在两极间取平衡。转型不可持续的根本驱动是成本倒逼:上下文窗口由8k/32k扩至128k–1M+、Agent模式单请求触发10+次模型调用、不同模型成本差5–10倍、重度用户单会话token是轻度用户数十倍,使次数制下"重度对轻度的交叉补贴"不可持续——这是Trae国际版、Cursor改Token制、以及Qoder 2026-05更名后企业版涨价约25%(标准版¥79→¥99、VPC版¥159→¥199、个人版由限时免费转¥59/月)的共同根因。由此可凝练一条贯穿全行业的因果链:Agent化演进 → token成本跃升 → 次数制交叉补贴崩塌 → 细粒度计量/涨价。

### [established · high] theme _(facet: f_ai_coding_work_vs_vs_token)_
三家产品均采取国内国际双轨,且国内定价显著低于全球(约为后者40%):Qoder国内Pro ¥59/月≈全球$20的40%、Pro+ ¥169≈$60的40%;WorkBuddy、Trae Work均主打免费可用+低价Pro。双轨不仅体现在价格,也体现在计费模式分化(Trae国际版已转Token制、国内版仍次数制),反映中国AI工具市场的购买力水平与竞争烈度,以及"免费代码补全为钩子+低价Pro变现"的获客心智。资源包设计进一步体现精细变现策略:Qoder个人¥40/1000 Credits(1个月有效)、企业¥80/2000 Credits(3个月有效)、到期清零、单价高于套餐内以鼓励订阅、Credits跨产品共享(Desktop/JetBrains/QoderWork/CLI/Mobile),非高峰期Qwen 3.7享最高80%折扣。

### [emerging · medium] theme _(facet: _unfileted)_
在模型能力层,国产模型已逼近第一梯队但仍有基建短板:智谱2026-06-13向GLM Coding Plan全量用户开放的GLM-5.2(MIT,迄今最强开源)支持真正可用1M上下文、400–500K下指令遵循接近Claude、幻觉极低,实测在10万行代码项目结果与Claude Opus 4.8几乎一致但慢2倍多(21 vs 6分钟),作者判定为算力基建差距而非模型能力差距,最大短板是不支持多模态、Coding Plan配额仍需每天抢。在产品集成侧,TRAE Work的上下文窗口由平台内部管理、对用户不透明——含GLM-5.2在内的预置模型窗口大小官方未公开,仅桌面端自定义模型允许手配Token上限;运行时为每个SOLO Agent会话维护独立窗口,累计超限自动触发上下文压缩而非报错。这种"上下文不透明"与积分/Credits制形成呼应:产品都在用抽象计量层屏蔽底层token差异,把上下文/模型选择封装在平台内部。

### [established · high] theme _(facet: f_ai_coding_work_vs_vs_token)_
中国AI编程/工作台市场已形成腾讯WorkBuddy、字节Trae Work、阿里Qoder三足鼎立格局，三家均于2026年完成从免费到商业化的转型。三者在产品定位上形成差异化：WorkBuddy定位'能干活交付的AI工作台'，强调本地文件操作、手机远程操控和多专家Agent协作；Trae Work国际版面向海外开发者、国内版面向全场景知识工作者（产品/运营/市场/设计/开发），按Work/Code双模式组织模型；Qoder产品矩阵最广，从IDE桌面端到CLI、JetBrains插件、办公套件到7×24 AI员工QoderWake全覆盖。三家共同趋势是从'AI辅助补全'向'AI员工/Agent工作台'演进，这一演进带来的token成本跃升正是计费模式变革的根本驱动力。

### [established · high] viewpoint _(facet: f_ai_coding_work_vs_vs_token)_
积分/Credits制已成为国内AI编程工具的主流计费范式，WorkBuddy和Qoder均采用'加权积分制'——用抽象单位（积分/Credits）屏蔽底层模型token差异，不同模型/任务类型有不同消耗系数。这一设计的本质是在用户体验（简单易懂）与成本精确性（Token制）之间取折中：代码补全作为最高频功能普遍免费（获客钩子），Agent/高阶功能才消耗积分。Qoder更进一步，引入非高峰期折扣（Qwen 3.7最高80%折扣）和模型调用失败不扣费的精细化设计。与此形成对比的是Trae国际版已转向纯Token制，且用户测算Pro实际权益缩水至约1/5——这暴露了计量制的一个内在张力：计费越精确，用户感知的'性价比'可能越低，尤其在模型切换时（便宜模型可能无法胜任复杂任务）。

### [established · high] theme _(facet: f_ai_coding_work_vs_vs_token)_
AI编程工具正经历行业性的'请求次数制→Token/Credits制'计费转型，其结构性驱动力是Agent模式下算力成本的指数级跃升：上下文窗口从8k/32k扩至128K–1M+、Agent模式单请求触发10+次模型调用、不同模型成本差5–10倍、重度用户单次会话token量是轻度用户数十倍。这些因素叠加使次数制下重度用户对轻度用户的交叉补贴不可持续——这正是Trae国际版（2026年2月）和Cursor改Token制的共同触发因素。Qoder 2026年5月更名后企业版涨价约25%、个人版由免费转¥59/月的调价动作独立印证了同一成本上升逻辑。早期采用次数制的产品逻辑也值得理解：Token对非技术用户是陌生概念、2025年初Agent能力弱单次消耗差异小、'X次/月'契合SaaS订阅心智利于获客、粗粒度计费避免迭代期频繁调价。这些早期优势正被Agent时代的技术现实所瓦解。

### [contested · medium] contrarian _(facet: f_ai_coding_work_vs_vs_token)_
国内AI编程工具定价显著低于全球水平（Qoder国内Pro ¥59/月约为全球版$20的~40%，WorkBuddy和Trae Work也主打免费可用+低价Pro），这反映了中国AI工具市场的购买力水平和竞争烈度。但这一低价策略与Agent时代成本上升的趋势构成根本张力：三家同时经历免费→收费的转型阵痛（Qoder企业版涨价25%、WorkBuddy 2026年7月刚启动收费、Trae Work国内版仍以免费用为主），而Agent能力的持续增强意味着单次服务成本仍在上升。这一张力在Trae Work国内版上尤为突出——其'免费够用'的获客策略是次数制暂留的理由之一，但与Agent成本上升的方向相悖。关键问题是：中国市场的低价惯性是否可持续？还是会迫使产品在'限制免费额度'（如Trae Work从日限额改周限额）和'悄悄涨价'（如Qoder的资源包到期清零设计）之间反复博弈？

### [emerging · medium] viewpoint _(facet: _unfileted)_
TRAE Work在模型生态上采用预置模型+自定义模型双轨策略，预置模型按Work/Code双模式组织了丰富的国产模型阵容（Doubao Seed 2.1系列、MiniMax、GLM-5.2、DeepSeek V4、Kimi K2.7等）。但存在一个关键的不透明问题：预置模型的上下文窗口大小在官方文档中未公开，配额由平台内部管理且不对用户暴露（仅自定义模型允许用户手动配置Token上限）。TRAE Work采用自动上下文压缩机制（当累积上下文超过上限时自动移除冗余、保留关键内容，而非抛错中断）来管理这一不透明窗口。与此同时，GLM-5.2作为国产开源旗舰模型展现了令人瞩目的能力（1M上下文、指令遵循接近Claude、实测10万行代码结果与Claude Opus 4.8几乎一致但慢2倍多），其MIT开源协议和可通过REAP量化在本地运行的特点，为'自定义模型'场景提供了有竞争力的选择。这一模型生态的不透明性（平台内部管理的上下文窗口）与GLM-5.2等开源模型的透明性（MIT协议、可本地运行）之间形成有趣对比，也间接解释了为何'自定义API Key免费用'成为WorkBuddy和Trae Work的共同卖点——用户用自己购买的模型API可以绕过平台的不透明配额限制。

### [established · medium] sub_question _(facet: f_ai_coding_work_vs_vs_token)_
## 国内AI Coding/Work产品计费模式对比分析

### 一、市场格局与产品定位

2026年中，国内互联网大厂在AI Coding/Work赛道已形成BAT三足鼎立：腾讯WorkBuddy（CodeBuddy品牌）、字节Trae Work、阿里Qoder（原通义灵码）。三家产品均已从早期免费抢用户阶段进入商业化变现阶段，但计费策略选择出现了有趣分化。

### 二、三种计费模式的本质差异

**1. 积分/Credits制（WorkBuddy、Qoder——主流选择）**
积分制本质是一种"加权token抽象层"：用户看到的是统一的"积分"或"Credits"，底层按模型和任务复杂度乘以不同系数扣减。这种设计的好处是：
- 用户无需理解token、上下文窗口等技术概念
- 平台可以灵活调整不同模型的成本权重而不改变定价结构
- 代码补全作为最高频功能普遍免费（降低获客门槛），Agent等高价值功能才消耗积分
- Qoder和WorkBuddy都支持外接自定义API Key，给重度用户提供"自带算力"的逃生通道

**2. 请求次数制（Trae Work国内版——少数派）**
Trae Work国内版是唯一仍坚持对话次数制的产品。这种设计在产品早期有明显的用户体验优势："每周N次"像网盘容量一样直观，不会产生"每句话都在花钱"的Token焦虑。但它的致命缺陷是成本倒挂——在Agent时代，一次"对话"背后可能触发10+次模型调用，消耗几十万token，但用户只付了一次的钱。Trae国际版已经在2026年2月被迫切换到Token制（据用户实测权益缩水到约1/5），Cursor也经历了同样的转变。

**3. 为什么Trae Work国内版还坚持次数制？**
这是一个阶段性的商业策略选择而非技术决策：
- **目标用户更广**：Trae Work面向产品/运营/市场/设计/开发全场景，非技术用户对Token接受度极低
- **成本暂时可控**：Work/Design模式比纯Code模式的token消耗更可控，且字节有豆包自有模型的成本优势
- **国内竞争策略**：主打"免费够用"快速做用户规模，Pro版Fast Pass优先队列是体验差异化而非次数差异化
- **风险**：随着Agent能力增强（自动处理飞书文档、多步自动化），单次"对话"成本会快速上升，这是一颗定时炸弹

### 三、定价策略的中国特色

三家产品都体现了明显的"中国定价"特征：
- Qoder国内Pro ¥59/月仅为全球版$20的约40%
- 普遍提供 generous 的免费额度（代码补全无限免费）
- 资源包有效期短（到期清零），鼓励持续订阅
- 企业版在客户锁定后开始涨价（Qoder企业版涨25%），利用迁移成本变现

### 四、核心矛盾与趋势预测

AI编程工具计费面临一个根本矛盾：**用户体验要求简单（次数/积分），成本结构要求精确（Token）**。积分/Credits制是目前的最优折中——用系数层屏蔽底层复杂性，同时保持成本匹配度。

**趋势判断**：
1. 随着Agent能力增强和上下文窗口继续扩大，请求次数制将越来越难以为继，Trae Work国内版大概率会在未来切换到积分/Credits制或Token制
2. "代码补全免费+Agent功能收费"将成为行业标准分层模式
3. 支持外接自定义API Key会成为标配——既是对重度用户的让利，也是平台成本风险的释放阀
4. 企业版定价将持续走高，因为代码库深度集成后的迁移成本是极强的护城河

## 4. 已证实发现 / Corroborated Findings (L2)
| # | 发现 | 印证数 | 跨平台 | 可信度 | 冲突 |
|---|------|--------|--------|--------|------|
| 1 | 国内BAT三家AI Coding/Work产品已形成三足鼎立格局：腾讯WorkBuddy(CodeBuddy)、字节Trae Work、阿里Qoder(原通义… | 3 | 1 | high |  |
| 2 | 积分/Credits制是国内AI编程工具的主流计费模式：WorkBuddy用积分（按模型系数消耗）、Qoder用Credits（统一计量单位），两者本质都是'… | 2 | 1 | high |  |
| 3 | Trae Work国内版是三家之中唯一仍采用请求次数制的产品；其国际版已在2026年2月切换为Token制，国内版暂未切换。请求次数制在Agent长上下文时代… | 3 | 1 | high | ⚠ |
| 4 | 国内定价显著低于全球定价：Qoder国内Pro ¥59/月约为全球版$20的40%，WorkBuddy和Trae Work也主打免费可用+低价Pro；这反映了… | 3 | 1 | medium |  |
| 5 | AI编程工具计费模式存在一个核心产品-成本矛盾：用户体验要求计费单位简单易懂（次数/积分），但成本结构要求精确匹配token消耗（Token制）。积分/Cre… | 3 | 1 | medium |  |
| 6 | AI编程工具正在从'辅助补全'向'AI员工/Agent工作台'演进（WorkBuddy的多专家协作、QoderWake 7×24 AI员工、Trae Work… | 3 | 1 | medium |  |
| 7 | WorkBuddy是腾讯云CodeBuddy团队推出的桌面AI智能体工作台(非字节跳动产品),定位为'能干活交付'的AI工作台而非聊天工具,核心能力包括本地文… | 1 | 1 | medium |  |
| 8 | WorkBuddy于2026年7月1日起正式收费,采用积分制:标准版4000积分/月、加量包50元/1000积分、新用户首月5000积分体验,支持外接自定义A… | 1 | 1 | medium |  |
| 9 | Trae产品线分国际版(trae.ai,2025年1月发布,面向海外开发者)与国内版Trae Work(work.trae.cn,2026年6月9日由Trae… | 1 | 1 | medium |  |
| 10 | Trae计费模式双轨分化:国际版已于2026年2月24日从请求次数制切换为Token计费(Free/Lite/Pro/Pro+/Ultra五档),用户测算Pr… | 1 | 1 | medium |  |
| 11 | Trae Work国内版免费提供Doubao Seed 2.1 Pro/2.1 Turbo、MiniMax、GLM等模型,Pro版享有Fast Pass优先队… | 1 | 1 | medium |  |
| 12 | AI编程工具计费正经历行业性的'请求次数制→Token/Credits制'转型。早期采用次数制的逻辑:Token是技术概念普通用户难理解、'X次/月'契合Sa… | 1 | 1 | medium |  |
| 13 | Qoder是阿里巴巴推出的AI智能编程平台,采用国内国际双轨运营;国内版于2026年5月20日由'通义灵码'更名为Qoder CN,产品矩阵包括Qoder D… | 1 | 1 | medium |  |
| 14 | Qoder定价国内外双轨:全球版Pro $20/月(2000 Credits)、Pro+ $60/月(6000 Credits)、新用户2周Pro试用+100… | 1 | 1 | medium |  |
| 15 | Qoder以Credits为统一计量单位:代码补全与Next Edits全版本无限免费(获客钩子),Inline Chat/Ask/Agent/Quest/E… | 1 | 1 | medium |  |
| 16 | Qoder于2026年5月更名后上调企业版价格约25%(标准版¥79→¥99、VPC版¥159→¥199),个人专业版由限时免费转为¥59/月;涨价逻辑为:通… | 1 | 1 | medium |  |
| 17 | Qoder资源包设计:个人¥40/1000 Credits(1个月有效)、企业¥80/2000 Credits(3个月有效),到期清零;资源包单价比套餐内Cr… | 1 | 1 | medium |  |
| 18 | TRAE Work 同时提供预置模型与桌面端本地环境专属的自定义模型；预置模型按 Work/Code 双模式组织——Work 模式含 TRAE Auto Mo… | 1 | 1 | medium |  |
| 19 | TRAE Work 的上下文窗口由平台内部管理且对用户不透明:预置模型(含 GLM-5.2)的窗口大小在官方文档未公开,仅桌面端自定义模型允许手配输入/输出 … | 2 | 1 | medium |  |
| 20 | 智谱于 2026-06-13 向全部 GLM Coding Plan 用户(Lite/Pro/Max/团队版)开放 GLM-5.2(MIT,其迄今最强开源模型… | 1 | 1 | medium |  |
| 21 | 中国主流AI编程/工作台产品（腾讯WorkBuddy、字节Trae国际版、阿里Qoder）已普遍转向按Token/积分(Credit)的细粒度计量计费：Wor… | 3 | 1 | high |  |
| 22 | AI编程工具从请求次数制转向计量计费的结构性驱动力是算力成本倒逼：上下文窗口由8k/32k扩至128k–1M+、Agent模式单请求触发10+次模型调用、不同… | 2 | 1 | medium |  |
| 23 | WorkBuddy是腾讯云CodeBuddy团队（非字节跳动）推出的桌面AI智能体工作台，核心能力包括本地文件操作、Claw手机远程操控、Skills技能生态… | 1 | 1 | medium |  |
| 24 | Trae产品线分为国际版（trae.ai，2025年1月发布、面向海外开发者）与国内版Trae Work（work.trae.cn，2026年6月9日由Tra… | 1 | 1 | medium |  |
| 25 | Qoder是阿里巴巴推出的AI智能编程平台，采用国内国际双轨运营；国内版于2026年5月20日由"通义灵码"更名为Qoder CN，产品矩阵包括Qoder D… | 1 | 1 | medium |  |
| 26 | Qoder资源包采用到期清零设计：个人¥40/1000 Credits（1个月有效）、企业¥80/2000 Credits（3个月有效）；资源包单价高于套餐内… | 1 | 1 | medium |  |
| 27 | TRAE Work 提供预置模型与自定义模型两类：预置模型按 Work/Code 两套模式划分（Work 模式含 TRAE Auto Model、Doubao… | 1 | 1 | medium |  |
| 28 | TRAE Work（仅 SOLO Agent）为每个对话维护独立上下文窗口，当累积上下文超过平台上限时自动触发（亦可手动触发）上下文压缩——通过移除冗余、保留… | 1 | 1 | medium |  |
| 29 | 智谱于 2026-06-13 向 GLM Coding Plan 全量用户（Lite/Pro/Max/团队版）开放其迄今最强开源模型 GLM-5.2（MIT … | 1 | 1 | medium |  |
| 30 | WorkBuddy是腾讯云CodeBuddy团队推出的桌面AI智能体工作台（非字节跳动产品），核心能力包括本地文件操作、Claw手机远程操控、Skills技能… | 1 | 1 | medium |  |
| 31 | WorkBuddy于2026年7月1日起正式收费，采用积分制计费：标准版4000积分/月，加量包50元/1000积分，新用户首月5000积分体验，支持外接自定… | 1 | 1 | medium |  |
| 32 | Trae产品线分为国际版(trae.ai)和国内版Trae Work(work.trae.cn)：国际版2025年1月发布面向海外开发者，国内版2026年6月… | 1 | 1 | medium |  |
| 33 | Trae国际版已于2026年2月24日从请求次数制切换为Token计费（五档套餐Free/Lite/Pro/Pro+/Ultra），用户测算Pro用户实际权益… | 1 | 1 | medium |  |
| 34 | AI编程工具早期采用请求次数制而非Token制的核心设计逻辑包括：(1)Token是技术概念普通用户难理解，'X次/月'符合SaaS订阅心智，获客转化率更高；… | 1 | 1 | medium |  |
| 35 | 请求次数制不可持续的根本原因是成本倒逼：上下文窗口从8k/32k扩展到128k-1M+、Agent模式下单请求触发10+次模型调用、不同模型成本差5-10倍、… | 1 | 1 | medium |  |
| 36 | Trae Work国内版暂时保留次数制的原因：目标用户更广泛含非技术用户（对Token接受度低）、Work/Design模式单次token消耗比Code模式可… | 1 | 1 | medium |  |
| 37 | Qoder是阿里巴巴推出的AI智能编程平台，采用国内国际双轨运营；国内版2026年5月20日从'通义灵码'更名为Qoder CN，产品矩阵包括Qoder De… | 1 | 1 | medium |  |
| 38 | Qoder定价体系：全球版Pro $20/月(2000 Credits)、Pro+ $60/月(6000 Credits)，国内版约为全球版40%（个人Pro… | 1 | 1 | medium |  |
| 39 | Qoder采用Credits统一计量单位：代码补全和Next Edits全版本无限免费（作为获客钩子），Inline Chat/Ask/Agent/Quest… | 1 | 1 | medium |  |
| 40 | Qoder 2026年5月更名后企业版涨价约25%（标准版¥79→¥99，VPC版¥159→¥199），个人专业版从限时免费转为¥59/月；涨价逻辑为通义灵码… | 1 | 1 | medium |  |
| 41 | TRAE Work（SOLO Agent）为每个对话维护独立的上下文窗口，当累积上下文超过平台允许的上限时自动触发上下文压缩（移除冗余、保留关键内容）以维持输… | 1 | 1 | medium |  |
| 42 | TRAE Work 同时支持预置模型与自定义模型，预置模型按 Work/Code 两套模式划分（Work 含 TRAE Auto Model、Doubao-S… | 1 | 1 | medium |  |
| 43 | TRAE 国际版即将升级计费方案，可能涉及上下文配额调整 | 1 | 1 | low |  |
| 44 | GLM-5.2 是智谱 AI 的开源旗舰模型，采用 MoE 架构（总参数约 744B–750B，每 token 激活约 40B），以 MIT 许可证开放权重；… | 3 | 1 | high | ⚠ |
| 45 | GLM-5.2 可通过 REAP 量化方案（自定义 llama.cpp 分支，约 3.6 bpw）在本地硬件上运行，实测约 13 decode tok/s，借… | 1 | 1 | medium |  |

## 5. 来源索引 / Source Index
| # | 主张 | 平台 | 链接 | 可信度 | 缓存 |
|---|------|------|------|--------|------|
| 1 | WorkBuddy是腾讯云CodeBuddy团队推出的桌面AI智能体工作台，非字节跳动产品；核心能力包括本地文件操作、Claw手机远程操控、Skills技能生… | web | [link](https://www.codebuddy.cn/workbuddy) | medium | `topics/cn_coding_work_products/cache/5fbbf592a4b545bb140afbf775245d48515537bff6abf19a51080348ca8c7f33.md` |
| 2 | WorkBuddy于2026年7月1日起正式收费，采用积分制计费：标准版4000积分/月，加量包50元/1000积分，新用户首月5000积分体验，支持外接自定… | web | [link](https://www.codebuddy.cn/workbuddy) | high | `topics/cn_coding_work_products/cache/5fbbf592a4b545bb140afbf775245d48515537bff6abf19a51080348ca8c7f33.md` |
| 3 | WorkBuddy积分按模型系数消耗：MiniMax模型系数0.18（最低），DeepSeek模型系数0.30；简单对话约2-3积分，PDF/PPT/批量处理… | web | [link](https://www.codebuddy.cn/workbuddy) | medium | `topics/cn_coding_work_products/cache/5fbbf592a4b545bb140afbf775245d48515537bff6abf19a51080348ca8c7f33.md` |
| 4 | Trae产品线分为国际版(trae.ai)和国内版Trae Work(work.trae.cn)：国际版2025年1月发布面向海外开发者，国内版2026年6月… | web | [link](https://work.trae.cn/pricing) | high | `topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md` |
| 5 | Trae国际版已于2026年2月24日从请求次数制切换为Token计费（五档套餐Free/Lite/Pro/Pro+/Ultra），据用户测算Pro用户实际权… | web | [link](https://work.trae.cn/pricing) | medium | `topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md` |
| 6 | Trae Work国内版免费提供Doubao Seed 2.1 Pro/2.1 Turbo、MiniMax、GLM等模型，Pro版有Fast Pass优先队列… | web | [link](https://work.trae.cn/pricing) | high | `topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md` |
| 7 | AI编程工具早期采用请求次数制的核心设计逻辑：(1)Token是技术概念普通用户难以理解，'X次/月'符合SaaS订阅心智获客转化率更高；(2)2025年初模… | web | [link](https://work.trae.cn/pricing) | medium | `topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md` |
| 8 | 请求次数制不可持续的根本原因（成本倒逼）：上下文窗口从8k/32k扩展到128k-1M+、Agent模式下单请求触发10+次模型调用、不同模型成本差5-10倍… | web | [link](https://work.trae.cn/pricing) | medium | `topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md` |
| 9 | Trae Work国内版暂时保留次数制的原因：目标用户更广泛（非技术用户对Token接受度低）、Work/Design模式单次token消耗比Code模式可控… | web | [link](https://work.trae.cn/pricing) | medium | `topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md` |
| 10 | Qoder是阿里巴巴推出的AI智能编程平台，采用国内国际双轨运营；国内版2026年5月20日从'通义灵码'更名为Qoder CN，产品矩阵包括Qoder De… | web | [link](https://qoder.com.cn/pricing) | high | `topics/cn_coding_work_products/cache/2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98.md` |
| 11 | Qoder全球版定价：Pro $20/月(2000 Credits)，Pro+ $60/月(6000 Credits)，新用户2周Pro试用+1000 Cre… | web | [link](https://qoder.com.cn/pricing) | high | `topics/cn_coding_work_products/cache/2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98.md` |
| 12 | Qoder采用Credits统一计量单位：代码补全和Next Edits全版本无限免费（获客钩子），Inline Chat/Ask/Agent/Quest/E… | web | [link](https://qoder.com.cn/pricing) | high | `topics/cn_coding_work_products/cache/2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98.md` |
| 13 | Qoder 2026年5月更名后企业版涨价约25%（标准版¥79→¥99，VPC版¥159→¥199），个人专业版从限时免费转为¥59/月；涨价逻辑为通义灵码… | web | [link](https://qoder.com.cn/pricing) | medium | `topics/cn_coding_work_products/cache/2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98.md` |
| 14 | Qoder资源包设计：个人¥40/1000 Credits(1个月有效)，企业¥80/2000 Credits(3个月有效)，到期清零；资源包单价比套餐内Cr… | web | [link](https://qoder.com.cn/pricing) | high | `topics/cn_coding_work_products/cache/2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98.md` |
| 15 | TRAE Work 同时支持预置模型与自定义模型；预置模型按 Work/Code 两套模式划分（Work 含 TRAE Auto Model、Doubao-S… | web | [link](https://docs.trae.cn/work_models.md) | high | `topics/cn_coding_work_products/cache/19e4b778919c6fbd2e1732bbf7e0448498c30725aec2496c28d63f8e5aff8afc.md` |
| 16 | TRAE Work（仅 SOLO Agent）为每个对话维护独立的上下文窗口，当累积上下文超过平台允许的上限时自动触发（亦可手动触发）上下文压缩，通过移除冗余… | web | [link](https://docs.trae.cn/ide_context-compaction.md) | high | `topics/cn_coding_work_products/cache/5c6989a24555f530cd50edb30c6adfaefecab6977afb441cc8ff314eb98871fd.md` |
| 17 | 智谱于2026年6月13日向GLM Coding Plan全量用户(Lite/Pro/Max/团队版)开放GLM-5.2——其迄今最强开源模型(MIT协议):… | web | [link](http://m.toutiao.com/group/7650866693463409187/) | medium | `topics/cn_coding_work_products/cache/945818fc55f83b5ed0f9330db78ecdd6fcb07aeeecf0bf2641b9450bc354be64.md` |
| 18 | TRAE 国际版即将升级计费方案，可能涉及上下文配额调整 | xiaohongshu | [link](https://www.xiaohongshu.com/discovery/item/698e8766000000001a02fe29) | medium | `topics/cn_coding_work_products/cache/745c457e7eacd722ecfac5908cb098046876a8fc59f3eaae689568e9158f2d98.md` |
| 19 | 智谱 AI 开源模型 GLM-5.2（750B 参数、1M token 上下文窗口）在关键 agentic benchmark 上表现接近 Anthropic… | x | [link](https://x.com/AaronRossPreIPO/status/2074093514926006493) | medium | `topics/cn_coding_work_products/cache/b48c9f17b97aa22f043a6c53650fe0bd4c98f6e1fd8930ee93abd74ddff40d3d.md` |
| 20 | 智谱AI的GLM-5.2模型采用744B总参数/40B每token激活的MoE架构，支持256K上下文窗口和131K输出上限，在多项编程基准上超越Claude… | x | [link](https://x.com/HazardKrypto/status/2073840034336141363) | medium | `topics/cn_coding_work_products/cache/c31e687f8758c39eda53a4b304f55ed0d7090b2ec25d23ec7322ea262f353a9e.md` |
| 21 | GLM 5.2 REAP 模型经自定义 llama.cpp 分支量化为约3.6 bpw后，可在本地硬件上以约13 decode tok/s速度运行并支持约10… | x | [link](https://x.com/myanvoos/status/2073933187651420316) | medium | `topics/cn_coding_work_products/cache/c5c866d49be0f27f89aa823098d4afe6a1e7ff9097d801c3a8755fbf2938783e.md` |
| 22 | GLM 5.2 在真实前端工程长链路任务中经过编程实测（具体表现结论因正文风控未取，仅有列表卡片标题） | xiaohongshu | [link](https://www.xiaohongshu.com/discovery/item/6a325313000000000f030d61) | low | `topics/cn_coding_work_products/cache/ea808360ea1ef2b72d32c13cb43d34a908c0b8b4d3f9ef2ed766d5232c11b29b.md` |
| 23 | GLM-5.2 作为 Z.ai 的开源旗舰模型，具备真正可用的 1M token 上下文窗口、长程 agentic 工程能力，编码性能接近 Claude Op… | x | [link](https://x.com/Nuzanthra/status/2073770838021804506) | medium | `topics/cn_coding_work_products/cache/e05a6442f3433f4555865e9c172fee665f3c820a6c0bc736880fca5c9c4380b4.md` |

## 6. 待复核 / Needs Review
- ⚠ Trae Work国内版是三家之中唯一仍采用请求次数制的产品；其国际版已在2026年2月切换为Token制，国内版暂未切换。请求次数制在Agent长上下文时代…
- ⚠ GLM-5.2 是智谱 AI 的开源旗舰模型，采用 MoE 架构（总参数约 744B–750B，每 token 激活约 40B），以 MIT 许可证开放权重；…

## 7. Facet 覆盖
| facet | 问题 | 状态 |
|-------|------|------|
| `f_ai_coding_work_vs_vs_token` | 国内AI Coding/Work产品计费模式对比研究（积分制 vs 请求次数制 vs Token制） | survey |
| `f_trae_work_glm_5_2_1m` | Trae Work 预置模型上下文窗口限制研究（GLM-5.2 是否为 1M 上下文版本？各预置模型实际上下文配额） | open |

---
_声明：本报告为信息关联与凝练，非投资/行动建议。每条主张均附来源链接与缓存路径，可回溯。_
