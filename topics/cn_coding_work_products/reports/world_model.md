# 国内互联网大厂Coding/Work类AI产品研究 — 世界模型 (world_model)
_自动生成 · 覆盖度: L0=1 L1=1 L2=6 L3=14 来源=3 · schema v2_

## 1. 主题概览 / Worldview
- **截至2026年7月，国内BAT三家（腾讯WorkBuddy、字节Trae Work、阿里Qoder）在AI Coding/Work工作台赛道已完成商业化起步，形成积分制（WorkBuddy/Qoder）vs 请求次数制（Trae Work国内版）的计费模式分化。积分/Credits制是主流方向，它通过抽象系数层在用户体验简单性和成本精确性之间取得平衡；请求次数制在产品早期/大众市场获客阶段有体验优势，但随着Agent能力增强和token成本上升将面临成本倒挂压力。三家产品均采用'基础功能免费+高阶功能收费'的freemium模式，国内定价约为全球版的40%，企业版在客户锁定后开始涨价变现。未来随着AI Agent从'辅助工具'向'AI员工'演进，计费模式将进一步向细粒度（Token/积分）和任务价值定价方向演化。**  _(confidence: medium)_

## 2. 开放问题 / Open Questions
- [ ] Trae Work国内版计费模式何时切换？触发条件是什么？
- [ ] 豆包MarsCode、文心快码(Comate)、CodeGeeX等其他国产产品的计费模式对比？
- [ ] GitHub Copilot、Cursor等国际产品在中国市场的策略如何？
- [ ] AI编程工具的计费终局是什么？按任务价值计费还是按算力消耗计费？
- [ ] 企业版定价权在客户深度集成后能提升到什么程度？
- [ ] 外接API Key（BYOK）模式的长期生态影响？
- [ ] 未来产品预留：其他待纳入的国内Coding/Work产品有哪些？

## 3. 分主题综合 / Themes (L1)
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

## 6. 待复核 / Needs Review
- ⚠ Trae Work国内版是三家之中唯一仍采用请求次数制的产品；其国际版已在2026年2月切换为Token制，国内版暂未切换。请求次数制在Agent长上下文时代…

## 7. Facet 覆盖
| facet | 问题 | 状态 |
|-------|------|------|
| `f_ai_coding_work_vs_vs_token` | 国内AI Coding/Work产品计费模式对比研究（积分制 vs 请求次数制 vs Token制） | survey |

---
_声明：本报告为信息关联与凝练，非投资/行动建议。每条主张均附来源链接与缓存路径，可回溯。_
