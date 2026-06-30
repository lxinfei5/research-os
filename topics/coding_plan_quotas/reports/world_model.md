# 编程套餐实际可用额度与隐性限额规则研究（GLM 套餐优先） — 世界模型 (world_model)
_自动生成 · 覆盖度: L0=1 L1=13 L2=20 L3=14 来源=14 · schema v2_

## 1. 主题概览 / Worldview
- **GLM Coding Plan 当前的核心矛盾是『额度黑箱 + 高阶模型倍率 + 新增周限额』与官方营销话术之间的张力。可确立的事实是：套餐采用 5 小时滑动窗口资源池（滚动逐分钟回血），高阶模型按高峰约 3 倍/非高峰约 2 倍消耗，老 Pro 套餐已停售且新套餐额度缩水并加周限额；改版引发反弹后官方致歉，承认透明度不足并承诺退款/回滚。但各档位（Lite/Pro/Max）的确切额度数字始终无单一权威来源——官方不公布，社区/第三方估算（1:5:20 梯度、¥149/¥49/¥119、6 亿/18 亿 token 等）口径混乱且因多次改版相互冲突。在此黑箱下，Agentic 场景出现『2 prompt 80 秒吃掉 97% 额度』的 bug 级异常，性价比评价在实测用户间直接对立，且套餐还存在售罄/限购的供给约束。结论性判断：在官方公开确切额度口径前，GLM Coding Plan 的真实性价比无法被单一裁定，唯一可靠的测额路径是以账户官方用量看板/查询 API 为准、辅以 Retry-After 观测与控制变量压测。**  _(confidence: medium)_

### 版本历史 / Version History
_世界模型随每次 condense 迭代；下方为已被取代的旧版本（当前版本见上）。_
- _[2026-06-30 06:59]_ GLM Coding Plan 是一款以低价、兼容 Claude Code/Cline、1.5 倍配额为卖点的 AI 编程订阅，但其核心矛盾在于『名义配额可见…  _(supersedes: `—`)_

## 2. 开放问题 / Open Questions
- [ ] Lite/Pro/Max 各档位改版后的确切 5 小时与周限额（prompts/token）数字？
- [ ] Agentic 场景异常消耗是计费 bug 还是大上下文注入固有结果，是否已修复？
- [ ] 扣除倍率与周限额后，相对 Claude Pro/Max 的真实有效性价比？
- [ ] 退款与老套餐回滚的执行范围与时间表？
- [ ] Lite/Pro/Max 各档位改版后确切的 5 小时与周限额（prompts/token）数字？
- [ ] 售罄/限购与火山方舟等替代品的真实额度对比？

## 3. 分主题综合 / Themes (L1)
### [established · high] theme _(facet: coding_plan_quotas)_
智谱将 GLM Coding Plan 定位为面向 AI 编程的低价高配订阅，主打『1.5 倍配额、5 天免费、用量可视化』并兼容 Claude Code/Cline 等主流 Agentic 工具。但官方在营销层面强调卖点、却系统性回避各档位（Lite/Pro/Max）的具体额度数字——配额的『可见性』被刻意控制在名义层，真实可用量需用户自行试探。

### [established · high] sub_question _(facet: f_glm_429)_
官方致歉信构成本主题的关键转折事件：智谱公开承认规则透明度不足、GLM-5 灰度过慢、老用户升级机制粗糙三项错误，并首次量化披露 GLM-5 按原 4.7 版本 2 倍（高峰 3 倍）计费并新增周限额，同时承诺退款与老套餐回滚。这既印证了社区对『配额隐性缩水』的质疑，也表明计费倍率与周限额是真实存在的官方机制而非误读。

### [contested · medium] contrarian _(facet: f_glm_200k_128k_prompt)_
Lite 套餐在 Claude Code 场景下被实测出『bug 级』异常消耗：2 条 prompt、约 80 秒即吃掉 5 小时限额的 97%，而同等操作 Claude 仅消耗 4%。社区共识将根因指向隐式大上下文注入与激进缓存计费。这与官方『1.5 倍配额、用量可视化』的卖点形成直接张力——名义配额结构（共享 prompt 资源池 + 倍率）无法解释实际场景下的数量级偏差，可见量与实际消耗严重脱节。

### [established · high] viewpoint _(facet: f_glm_glm_4_5_vs_glm_4_6)_
套餐代际更替带来实质性额度缩水：老 Pro 套餐（5 小时约 60–80M token、无周限额）已于 2026 年初停售，新套餐下调 5 小时限额并新增周限额，实测可用额度大幅缩水。这与致歉信披露的 GLM-5 倍率计费、新增周限额相互印证，构成『改版即缩水』的连贯证据链。

### [contested · medium] contrarian _(facet: f_claude_pro_maxchatgpt_plus_procu)_
第三方横向对照（如 codingplan.org）给出 GLM『代码能力国内领先、支持大上下文、¥149/¥49/¥119 对应 6 亿/18 亿 token/月』的高性价比叙事，但这些价格与额度均为不同时点抓取、且历经多次改版导致严重冲突的非官方估算，未扣除高阶模型倍率与周限额。结合异常消耗与缩水证据，标称『极致性价比』与实际可用价值之间存在巨大缺口——第三方横评应被视为方向性参考而非可信报价。

### [established · medium] theme _(facet: coding_plan_quotas)_
智谱将 GLM Coding Plan 定位为面向 AI 编程的订阅套餐，对外主打三大卖点——订阅用户 1.5 倍配额、新用户 5 天免费体验、用量可视化——并强调兼容 Claude Code / Cline 等主流工具及 Anthropic 端点。但官方营销页始终回避一个关键事实：各档位的具体额度数字从未公开。这是整个主题的张力起点：官方话术强调『配额优势』与『可视化』，却把真正决定性价比的额度口径留在黑箱里。

### [established · high] sub_question _(facet: f_glm_quota_structure)_
官方 FAQ 披露的是『名义配额结构』而非数字：所有套餐共享一个 5 小时滑动窗口的『最大 prompt 资源池』，高阶模型（GLM-5/5.2/5-Turbo）按高峰约 3 倍、非高峰约 2 倍系数消耗额度，且仅限官方支持的编程工具内使用、禁止 curl/Postman 直连。该倍率机制与小红书用户『强但费』的实测互相印证（sf-0256172be355 跨平台 corroboration=2），是本主题少数有真正跨源印证的发现。但 FAQ 系统性回避了两件事：各档位（Lite/Pro/Max）的具体 prompts/token 数字，以及触顶后是降级还是拒绝。额度结构『可见』，额度数字『不可见』。

### [contested · medium] sub_question _(facet: f_coding_plan_quotas)_
各档位（Lite/Pro/Max）的确切额度没有单一权威来源：官方不列数字，社区据用量看板与实测推算，口径在『prompts 次数』与『token 数』间不一致，三档大致呈 1:5:20 的 5 小时额度梯度（sf-66ff101fbda0），但这只是估算，须以账户实际用量看板为准。第三方横向对照（codingplan.org）给出的 ¥149/¥49/¥119 价格与 6 亿/18 亿 token/月额度更不可靠——不同时点抓取、套餐多次改版导致严重冲突，且未扣除高阶模型倍率与周限额，标称价值远高于实际可用价值。因此可靠的测额路径应以官方用量看板/查询 API 直读为主、Retry-After 观测与控制变量压测为辅、跨平台多源交叉印证，单帖实测与第三方『每档 X 次 prompts』估算不可直接采信。

### [established · medium] sub_question _(facet: f_glm_window_recovery)_
5 小时额度采用滚动恢复（滑动窗口）机制：系统每分钟自动释放恰好 5 小时前消耗的额度，分次使用则分次逐步恢复，而非到固定时间点一次性重置。这解释了为何额度体感是『缓慢回血』而非『整点清零』，也是 Retry-After 压测能作为测额辅助手段的机制基础。

### [emerging · medium] viewpoint _(facet: f_glm_429)_
改版引发反弹后智谱发出致歉信，官方承认三项错误：规则透明度不足、GLM-5 灰度节奏过慢、老用户升级机制设计粗糙；并首次披露 GLM-5 消耗按原 4.7 版本 2 倍计算、高峰期达 3 倍，且新增周限额，承诺退款与老套餐回滚等补偿。一个关键的行为细节是：套餐触顶后系统不返回硬拒绝（429），而是静默降级到 GLM-4.5-Air 等低规格模型继续服务——这意味着宣称的高阶模型并非全程保证，重负载/触顶时用户感知到能力下降却收不到报错。『不报错的降级』与『致歉信承认的透明度问题』指向同一根因：计费与服务规则对用户不透明。

### [emerging · medium] viewpoint _(facet: f_glm_200k_128k_prompt)_
在 Agentic Coding（Claude Code）场景下，GLM Coding Lite 套餐出现『bug 级』额度异常：仅 2 条 prompt、约 80 秒即消耗 38M token，干满 5 小时限额的 97%，而相同操作在 Claude 仅消耗约 4%。社区共识把根因指向隐式大上下文注入与激进缓存计费。这与官方披露的倍率机制叠加，构成了『token 快速蒸发』体感的技术解释，但『是计费 bug 还是大上下文固有结果、是否已修复』仍未有定论。

### [established · medium] viewpoint _(facet: f_glm_glm_4_5_vs_glm_4_6)_
改版的实质是额度缩水：老 Pro 套餐（5 小时限额约 60-80M token、无周限额）已于 2026 年初停售；新套餐显著下调 5 小时用量限额并新增周限额，实测可用额度大幅缩水。这是用户反弹与致歉信的直接背景——『老套餐回滚』之所以成为补偿诉求，正因为新老套餐的可用价值落差被实测确认。

### [contested · low] contrarian _(facet: f_glm_coding_plan_value)_
性价比评价在实测用户间直接对立，构成本主题最尖锐的张力：一方实测后认为 GLM Coding Pro『谁买谁傻子』、性价比极差、不值得购买（sf-5c7da748a704）；另一方实测后认为 Pro 套餐性价比高、省钱、值得购买（sf-dc1896a6b36e）。两条均为单源主观实测，结论相反。这种分裂并非简单噪音——它恰恰反映了额度黑箱与高阶模型倍率/周限额的存在：在不同使用强度、是否触发倍率与降级、买的是新套餐还是老套餐的情况下，同一套餐的真实性价比可以天差地别。在官方公开确切额度口径前，性价比无法被裁定为单一结论。

## 4. 已证实发现 / Corroborated Findings (L2)
| # | 发现 | 印证数 | 跨平台 | 可信度 | 冲突 |
|---|------|--------|--------|--------|------|
| 1 | 智谱官方将 GLM Coding Plan 定位为面向 AI 编程的订阅套餐，主打『订阅用户1.5倍配额』『新用户5天免费体验』『用量可视化』三大卖点，兼容 … | 1 | 1 | medium |  |
| 2 | 智谱官方在 GLM Coding Plan 改版致歉信中承认三项错误（规则透明度不足、GLM-5 灰度节奏过慢、老用户升级机制设计粗糙），披露 GLM-5 消… | 1 | 1 | high |  |
| 3 | 智谱 GLM Coding Lite 套餐在 Agentic Coding（Claude Code）场景下出现异常 token 消耗：仅 2 条 prompt… | 1 | 1 | medium |  |
| 4 | 智谱 GLM Coding Plan 官方 FAQ 仅披露名义配额结构：所有套餐共享 5 小时滑动窗口的「最大 prompt 资源池」，高阶模型（GLM-5.… | 1 | 1 | medium |  |
| 5 | 智谱 GLM Coding Pro 老套餐（5小时限额约60-80M token、无周限额）已于2026年初停售；新套餐显著下调5小时用量限额并新增周限额，实… | 1 | 1 | medium |  |
| 6 | 社区维护的第三方横向对照（如 codingplan.org）显示 GLM Coding Plan 在代码能力上国内领先并支持大上下文，但其标称价格（¥149/… | 1 | 1 | low |  |
| 7 | 测 GLM Coding Plan 真实额度的可靠路径应以官方用量看板/用量查询 API 直读为主，以 Retry-After 响应头观测与控制变量压测为辅，… | 1 | 1 | medium |  |
| 8 | GLM Coding Plan 各档位（Lite/Pro/Max）的具体额度没有单一权威来源：官方页面不直接列数字，社区/第三方据用量看板与实测推算的口径不一… | 1 | 1 | medium |  |
| 9 | 2026-06 下旬 X 平台多名用户实测：GLM Coding Plan 个人套餐长期售罄/限购（购买页临时关闭、抢不到），且 5 小时额度触顶是真实约束，… | 1 | 1 | medium |  |
| 10 | 智谱将 GLM Coding Plan 定位为面向 AI 编程的订阅套餐，主打『订阅用户1.5倍配额』『新用户5天免费体验』『用量可视化』三大卖点，兼容 Cl… | 1 | 1 | medium |  |
| 11 | GLM Coding Plan 的每5小时额度采用滚动恢复(滑动窗口)机制:系统每分钟自动释放恰好5小时前消耗的额度,分次使用则分次逐步恢复,而非到固定时间点… | 1 | 1 | medium |  |
| 12 | 智谱官方在 GLM Coding Plan 致歉信中承认改版的三个错误（规则透明度不足、GLM-5 灰度节奏过慢、老用户升级机制设计粗糙），并披露 GLM-5… | 1 | 1 | high |  |
| 13 | GLM Coding Plan 在套餐触顶后不返回硬拒绝（429），而是静默降级到 GLM-4.5-Air 等低规格模型继续服务，意味着宣称的高阶模型（如 G… | 1 | 1 | medium |  |
| 14 | 智谱 GLM coding Pro Plan 的性价比被实测用户评价为极差、不值得购买（吐槽其「谁买谁傻子」） | 1 | 1 | low |  |
| 15 | 智谱 GLM Coding Lite 套餐在 Agentic Coding（Claude Code）场景下出现「bug 级」额度异常：仅 2 条 prompt… | 1 | 1 | medium |  |
| 16 | 智谱 GLM Coding Plan Pro 套餐被作者实测后认为性价比高、省钱、值得购买。 | 1 | 1 | low |  |
| 17 | GLM 高阶模型（GLM-5/GLM-5.2/GLM-5-Turbo）按倍率消耗 Coding Plan 额度（高峰约 3 倍、非高峰约 2 倍），导致「强但… | 2 | 2 | medium |  |
| 18 | 智谱 GLM Coding Plan 官方 FAQ 仅披露名义配额结构——各套餐共享 5 小时滑动窗口的最大 prompt 资源池、仅限官方支持的编程工具（C… | 1 | 1 | medium |  |
| 19 | 智谱 GLM Coding Pro 老套餐（5小时限额约60-80M token、无周限额）已于2026年初停售，新套餐显著下调5小时用量限额并新增周限额，实… | 1 | 1 | medium |  |
| 20 | 社区维护的第三方横向对照（如 codingplan.org）显示 GLM Coding Plan 在代码能力上国内领先且支持大上下文，但其引用的价格（¥149… | 1 | 1 | low |  |

## 5. 来源索引 / Source Index
| # | 主张 | 平台 | 链接 | 可信度 | 缓存 |
|---|------|------|------|--------|------|
| 1 | 智谱 GLM Coding Pro 老套餐（5小时限额约60-80M token、无周限额）已于2026年初停售，新套餐显著下调5小时用量限额并新增周限额，实… | web | [link](https://www.v2ex.com/t/1221377) | medium | `topics/coding_plan_quotas/cache/1594b8253400766b01c4b1cedca72ee8520418ab993b606e2f34fdf8e31221b1.md` |
| 2 | 智谱官方将 GLM Coding Plan 定位为面向 AI 编程的订阅套餐，主打『订阅用户1.5倍配额』『新用户5天免费体验』『用量可视化』三大卖点，兼容 … | web | [link](https://docs.bigmodel.cn/cn/coding-plan/overview) | medium | `topics/coding_plan_quotas/cache/0d37af5494c7132bebb941674c1006826e1d01bf0f1a106f910e6b4001bd43f7.md` |
| 3 | 智谱官方在 GLM Coding Plan 致歉信中承认改版犯了三个错误（规则透明度不够、GLM-5灰度节奏太慢、老用户升级机制设计粗糙），并披露 GLM-5… | web | [link](https://www.ithome.com/0/922/755.htm) | high | `topics/coding_plan_quotas/cache/37f37eb0ed36ef3c2d4c0321b716caa53ba2fbbe2f85a1469590300a2ffb34ee.md` |
| 4 | 智谱 GLM Coding Lite 套餐在 Agentic Coding（Claude Code）场景下，仅 2 条 prompt、80 秒就消耗 38M … | web | [link](https://www.v2ex.com/t/1184019) | high | `topics/coding_plan_quotas/cache/52db4a62d467d4be5de80aac0dfbdb77d9c37f918651460383e2984cfb826d06.md` |
| 5 | 社区维护的第三方横向对照（codingplan.org 等）显示 GLM Coding Plan 在代码能力上国内领先且支持大上下文，但其价格数字（¥149/… | web | [link](https://github.com/mahonzhan/awesome-coding-plan) | medium | `topics/coding_plan_quotas/cache/45039a65d5e80dfaee58399f901b5572677936cf4c99424ebb41c5356a66a6b7.md` |
| 6 | 智谱 GLM Coding Plan 官方 FAQ 只披露名义配额结构——所有套餐共享5小时滑动窗口的「最大prompt资源池」、高阶模型（GLM-5.2/G… | web | [link](https://docs.bigmodel.cn/cn/coding-plan/faq) | high | `topics/coding_plan_quotas/cache/2246af5783fba7c6a4583efbe1a51214c9997b3dc8fa8e45eab14d65c9eb3b09.md` |
| 7 | GLM Coding Plan 的每5小时额度采用滚动恢复(滑动窗口)机制——系统每分钟自动释放恰好5小时前消耗的额度,分次使用则分次逐步恢复,而非到固定时间… | web | [link](https://help.aliyun.com/zh/model-studio/coding-plan) | high | `topics/coding_plan_quotas/cache/a0ed7ed6f08b80d8cbfc08421f289dade09432ce34d36af93e14c64bc2cd87f7.md` |
| 8 | GLM Coding Plan 触顶后不硬拒绝(429)而是静默降级到 GLM-4.5-Air 等低规格模型继续服务,意味着套餐宣称的高阶模型(如 GLM-5… | web | [link](https://docs.bigmodel.cn/cn/coding-plan/faq) | high | `topics/coding_plan_quotas/cache/2bf4f9c4a6315de96f6855dfc06af07f44977cbc5abed481c2435b996d4a1e33.md` |
| 9 | 测 GLM Coding Plan 真实额度的有效路径是以官方用量看板/用量查询 API 直读为主、Retry-After 响应头观测与控制变量压测为辅，并跨… | web | [link](https://docs.bigmodel.cn/cn/coding-plan/faq) | high | `topics/coding_plan_quotas/cache/cc992c762025620b30baed03c8e38499bb0ab3a5d0067c11bf499ac69f4d8c47.md` |
| 10 | GLM Coding Plan 各档位的具体额度数字没有单一权威来源,官方页面不直接列数字,社区/第三方据用量看板与实测推算的数字口径不一(prompts次数… | web | [link](https://jia.je/kb/software/coding_plan.html) | medium | `topics/coding_plan_quotas/cache/8bdead555eba2b6f24f77a3ec2cb1c2af17964244a2ab037668269e85d621c51.md` |
| 11 | 智谱 GLM 的 coding Pro Plan 性价比极差、不值得购买（实测吐槽其为「谁买谁傻子」） | xiaohongshu | [link](https://www.xiaohongshu.com/discovery/item/6a2d3f18000000002103f2f5?xsec_token=AB3D4tyDVm6JtDia1X0L4PRQPWMc9LPThUAqOS0Z9zUn4=) | low | `topics/coding_plan_quotas/cache/2015b83f28a87be43b344a3534bc6471ab034100ff8bd30f9331bff604d13e36.md` |
| 12 | X 平台多名用户的 2026-06 下旬实测显示：GLM Coding Plan 个人套餐长期处于售罄/限购状态（购买页面被临时关闭、抢不到），且 5 小时额… | x | [link](https://x.com/search?q=GLM%20Coding%20Plan%20%E9%A2%9D%E5%BA%A6) | medium | `topics/coding_plan_quotas/cache/db9f3d821ee3d3d2bb7394e560aae80c8810a04eec091efebf2edbe84ddbe242.md` |
| 13 | 智谱 GLM Coding Plan Pro 套餐性价比高，作者实测后认为很省、很值。 | xiaohongshu | [link](https://www.xiaohongshu.com/discovery/item/6a07517d0000000035033c0d?xsec_token=ABfd7CztO0VJDnpQZoXbgX0cUu6F6QyBaPxdT7RnAl48c=) | low | `topics/coding_plan_quotas/cache/206bffa272b84271a97bb9d22ece1720d5b6d2d08308b76130c3fe1919303f98.md` |
| 14 | 某大模型(指向GLM-5)能力强但token额度消耗极快,实测体感为「强但费」,与V2EX报告的38M token异常消耗及官方高阶倍率(2-3倍)机制相互印证 | xiaohongshu | [link](https://www.xiaohongshu.com/discovery/item/6a3575fc000000002003b2f9?xsec_token=ABc9HraA6wfvir3w10ycxSM6PN_HiHR_Rg2wx0jB7u0Kg=) | low | `topics/coding_plan_quotas/cache/2314939c2ce18a86a0b53aaf847fbe6a8631ff4e884bf20e3b3e0c2e15fba48d.md` |

## 7. Facet 覆盖
| facet | 问题 | 状态 |
|-------|------|------|
| `f_glm_glm_coding_plan_lite_pro_max` | GLM 编程套餐（GLM Coding Plan，含 Lite/Pro/Max 及包年版）有哪些档位？官方页面标称的 prompts/消息数、5h 窗口、每周额度各是多少？这是后续实测对照的基线。 | open |
| `f_glm_5` | GLM 各套餐的「5 小时滚动窗口」实际如何运作：窗口是请求时间起算的滑动窗口还是固定窗口？额度恢复的真实节奏是什么？跨窗口是否有残留计数？ | open |
| `f_glm_429` | GLM 编程套餐的隐性限额规则：达到上限后是硬拒绝(429)、降级到更弱模型、还是排队等待？是否区分「重活/大上下文请求」单独限流？社区报错文案与触发条件是什么？ | open |
| `f_glm_pro_max_glm_4_6_glm_4_5_glm` | GLM 各套餐所含「可用模型」的真实映射：Pro/Max 是否真的全程跑 GLM-4.6/GLM-4.5，还是在重负载时静默降级到 GLM-4.5-Air/Flash？套餐名宣称的模型与实际触发模型是否一致？ | open |
| `f_glm_glm_4_5_vs_glm_4_6` | GLM「老套餐」与「新套餐」的额度规则差异：是否存在改版前后的额度缩水/扩容？老用户续费是否被迁移到新规则？历史定价与额度对照（如旧的 GLM-4.5 体系 vs 现行 GLM-4.6 体系）。 | open |
| `f_glm_retry_after` | 社区是怎么实测出 GLM 套餐真实额度的？有效的探测方法有哪些（脚本压测、多人协作计数、观测响应头 retry-after）？哪些方法可信、哪些有偏差？这是元方法。 | open |
| `f_glm_200k_128k_prompt` | GLM 各套餐的单请求上下文长度上限（200K? 128K?）是否被隐性收窄？大上下文请求是否消耗更多「prompt 配额」或更快触顶？长上下文下实际可用轮次是否远低于标称？ | open |
| `f_claude_pro_maxchatgpt_plus_procu` | 横向对照：Claude Pro/Max、ChatGPT Plus/Pro、Cursor、Codex 等编程套餐的额度规则，GLM 编程套餐的额度密度与隐性限制处于什么水平？谁更透明、谁更坑？ | open |

---
_声明：本报告为信息关联与凝练，非投资/行动建议。每条主张均附来源链接与缓存路径，可回溯。_
