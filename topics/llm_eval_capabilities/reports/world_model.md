# 大模型评测：能力维度分解与后训练流派假说 — 世界模型 (world_model)
_自动生成 · 覆盖度: L0=1 L1=5 L2=14 L3=19 来源=19 · schema v2_

## 1. 主题概览 / Worldview
- **本主题当前的理解状态围绕两条彼此关联的张力展开：(1) 能力来源——后训练（RL/RLHF/RLAIF，GRPO 为开源主流）已取代指令微调成为前沿模型最关键的差异化战场，DeepSeek-R1 更证明纯 RL 可激励推理涌现；但占主导的修正认识是，后训练放大的是预训练已播种的行为、高质量预训练是必要前提，'后训练可独立决定能力'已被推翻。(2) 能力评估——榜单单一总分既因数据污染、cherry-pick 与选择性报告而系统性失真，又因压缩了多维能力画像而与真实应用表现脱节，评测正转向按能力维度拆分；具体到 coding，GLM-4.6 已超过 Sonnet 4 并被视为最强开源权重 coding 模型，但'代码能力强 ≠ 最长程 agentic 任务登顶'，长程任务上 Anthropic 仍占优。综合判断：能力由'强预训练地基 + agentic RL 后训练放大'共同决定，而对能力的衡量必须抗污染、按维度、区分短程与长程。**  _(confidence: medium)_

## 2. 开放问题 / Open Questions
- [ ] 预训练地基与后训练放大对最终能力的贡献边界如何量化划分？
- [ ] 纯 RL 涌现推理（R1-Zero 路线）在多大程度上依赖预训练已播种的能力，其上限在哪？
- [ ] 按能力维度、抗数据污染的评测如何标准化以替代单一总分榜单？
- [ ] 指令遵从与指令泛化的冲突如何在后训练中被调和，避免退回预训练人设？
- [ ] 开源权重模型在最长程 agentic 任务上落后 Anthropic 的根因是规模、数据还是执行模式？

## 3. 分主题综合 / Themes (L1)
### [emerging · medium] sub_question _(facet: f_benchmark_gap)_
用户与开发者侧的调查证据指向一个系统性结论：LLM 评测榜单的单一总分与模型在真实应用中的表现之间存在结构性落差。这支持'单分不足以刻画能力、应当沿能力维度分别评估'的判断——榜单名次是被压缩的标量，掩盖了能力画像的多维分布。该视角与评测方法学层面的趋势（按维度拆分评分）相互印证，但当前仅有单一调查来源直接支撑'差距'本身。

### [established · high] theme _(facet: f_post_training)_
DeepSeek-R1 是后训练范式的里程碑：它证明大模型的推理能力可由纯强化学习（GRPO）激励涌现，而非必须经由人类标注的监督微调（SFT）。其中 R1-Zero 作为首个零 SFT、纯 RL 涌现推理的模型，确立了'RL 可直接激励推理'这一新的后训练路线。这一发现在主题内被多处复述（含 _unfileted 桶中的同义陈述），属于已较稳固的事实性认识。

### [emerging · medium] viewpoint _(facet: f_generalization)_
一个反直觉但重要的视角：奖励模型默认并不会把'指令遵从'或'诚实'泛化到训练分布之外，而是倾向于回退到'像互联网文本'的预训练人设。由此，'指令遵从'与'指令泛化'应被视为两个不同且可能彼此冲突的维度——在分布内学会服从，不等于在分布外仍保持服从或诚实。这为后训练对齐的脆弱性提供了机制性解释，是当前仍在成形的判断。

### [emerging · medium] theme _(facet: f_training_method)_
GLM-4.5 的 agentic/编码能力被归因于后训练：通过自生成探索经验迭代增强策略，强化学习被视为其 agentic 能力的关键来源。这与 DeepSeek 系将推理特化交由 RL 后训练的路线一致，共同构成'agentic 能力主要在后训练阶段被塑造'的方法学共识雏形。

### [contested · medium] contrarian _(facet: _unfileted)_
这一桶汇聚了两条相互交织的主线，并各自带有张力。其一是评测方法学：现代评测有多选题、验证器、榜单/竞技场、LLM-as-judge 四种范式，趋势是按能力维度拆分评分而非给单一总分；与此同时榜单分数被系统性质疑——测试题泄入训练集使模型背答案、叠加 cherry-pick 与选择性报告，导致排行榜失真。其二是能力来源之争：后训练（多轮 RLHF/RLAIF、RL，GRPO 已成开源主流算法）被视为前沿模型最关键的差异化战场，DeepSeek 按职责分层（V3 通用基座、R1 RL 推理特化、V3.1/V3.2 混合 thinking 统一）正体现这一点。但这里存在明确的反向修正：RL 后训练放大的是预训练已播种的行为而非凭空创造能力，高质量预训练是必要前提，'后训练可独立决定能力'被推翻——这是本主题最强印证（3 源）的张力点。能力评估层面同样有张力：GLM-4.6 在 74 个真实编程任务上超过 Claude Sonnet 4、被社区视为最强开源权重 coding 模型，但'代码能力强'不等于'最长程 agentic 任务登顶'，在最长程任务上 Anthropic 仍占优，GLM-5.2 才以更大规模的 agentic RL 后训练去追赶。综合：后训练是差异化主战场，但它是放大器而非凭空创造器；榜单分数需被按维度、抗污染地重读。

## 4. 已证实发现 / Corroborated Findings (L2)
| # | 发现 | 印证数 | 跨平台 | 可信度 | 冲突 |
|---|------|--------|--------|--------|------|
| 1 | 用户/开发者调查显示 LLM 评测榜单分数与真实应用表现之间存在系统性差距，支持'单一总分不足以反映能力、需按能力维度分别评估'的判断 | 1 | 1 | medium |  |
| 2 | DeepSeek-R1 证明大模型的推理能力可通过纯强化学习(GRPO)激励涌现，而无需依赖人类标注的监督微调(SFT)；R1-Zero 是首个以纯 RL、零… | 1 | 1 | high |  |
| 3 | 奖励模型默认不会把指令遵从或诚实泛化到训练分布之外，而是倾向于回退到'像互联网文本'的人设；因此指令遵从与指令泛化是两个不同且可能冲突的维度。 | 1 | 1 | medium |  |
| 4 | LLM 评测主要有四种范式——多选题、验证器、榜单/竞技场、LLM-as-judge——且现代评测趋势是按能力维度拆解评分而非给单一总分。 | 1 | 1 | medium |  |
| 5 | 榜单/排行榜分数无法等同于模型真实能力：测试题泄入训练集导致模型背答案而非推理，叠加 cherry-pick 与选择性报告，使排行榜系统性失真。 | 1 | 1 | high |  |
| 6 | DeepSeek 模型按职责分层：V3 是通用基座（架构+预训练），R1 是 RL 后训练特化的推理模型，V3.1/V3.2 用混合 thinking 模式统… | 2 | 1 | high |  |
| 7 | DeepSeek-V3 的基础能力来自架构创新（671B MoE / 37B 激活、MLA、无辅助损失负载均衡、FP8 混合精度）与 14.8T token … | 2 | 1 | high |  |
| 8 | DeepSeek-R1 证明 LLM 的推理能力可通过纯强化学习（GRPO）激励而无需人类标注的 SFT，其中 R1-Zero 是首个不依赖 SFT、纯 RL… | 1 | 1 | high |  |
| 9 | 推理模型的 RL 训练正从 SFT→RLHF 标准管线演进，DeepSeek-R1 提出的 GRPO 已成为开源社区主流的 RL 算法。 | 1 | 1 | medium |  |
| 10 | 后训练（多轮 RLHF/RLAIF、RL）已取代指令微调成为前沿模型间最关键的差异化竞争轴，可扩展性远超指令微调，即'后训练成为核心战场'；但同时有观点修正：… | 3 | 1 | high | ⚠ |
| 11 | 在 Claude Code 环境下用 74 个真实编程任务实测，GLM-4.6 的代码能力超过 Claude Sonnet 4 并领先其他国产模型，较 GLM… | 2 | 1 | medium |  |
| 12 | 社区共识认为 GLM-4.6 是当前最强的开源权重 coding 模型，但'代码能力强'不等于'最长程任务登顶'——在最长程 agentic 任务上 Anth… | 1 | 1 | medium |  |
| 13 | GLM-5.2 的长程任务能力源于规模更大、领域更广、执行模式更复杂的 agentic RL 后训练。 | 1 | 1 | medium |  |
| 14 | GLM-4.5 的 agentic/编码能力主要来自后训练（post-training）：通过自生成探索经验迭代增强策略，强化学习（RL）是其 agentic… | 1 | 1 | medium |  |

## 5. 来源索引 / Source Index
| # | 主张 | 平台 | 链接 | 可信度 | 缓存 |
|---|------|------|------|--------|------|
| 1 | GLM-4.5 的 agentic/编码能力主要来自后训练（post-training）：通过自生成探索经验迭代增强策略，RL 是 agentic 能力的关键。 | web | [link](https://z.ai/blog/glm-4.5) | medium | `topics/llm_eval_capabilities/cache/6287419fa6e1d92642825c7c05b0ced90732c8b5b95f0dd3dbeb9f4feebddd2f.md` |
| 2 | LLM 评测主要有四种范式——多选题、验证器、榜单/竞技场、LLM-as-judge——且现代评测趋势是按能力维度拆解评分而非给单一总分。 | web | [link](https://magazine.sebastianraschka.com/p/llm-evaluation-4-approaches) | high | `topics/llm_eval_capabilities/cache/e5c6214da596f902a48aaf2bd6bd13d43bda8b3f178c7ccadb7972188d835eec.md` |
| 3 | DeepSeek 各模型按职责分层：V3 是通用基座（架构+预训练），R1 是 RL 推理特化（后训练），V3.1/V3.2 用混合 thinking 统一两… | web | [link](https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond) | medium | `topics/llm_eval_capabilities/cache/0d85aee7dd785ea5476fed76af3df69f99db82e70e91c972665a008857eae5f4.md` |
| 4 | 榜单分数无法等同于模型真实能力：测试题泄入训练集导致模型背答案而非推理，叠加 cherry-pick/选择性报告，使排行榜系统性失真。 | web | [link](https://www.digitalapplied.com/blog/llm-benchmark-methodology-2026-contamination-leaderboard-guide) | medium | `topics/llm_eval_capabilities/cache/6a5dbce3009eca92e07b224e6dc7893abfc257de98a72fb716f584cc9dfdeb89.md` |
| 5 | RL 后训练放大的是预训练阶段已播种的行为而非凭空创造能力，预训练与后训练深度耦合，高质量预训练是必要前提、后训练负责解锁价值，因此'后训练可独立决定能力'的… | web | [link](https://arxiv.org/html/2504.07912v2) | high | `topics/llm_eval_capabilities/cache/83c038cf956a5848e51bc1c26c86ccda815fbe806996f33e71265c7b057c79f1.md` |
| 6 | DeepSeek-R1 证明大模型的推理能力可以通过纯强化学习(GRPO)激励涌现，而无需依赖人类标注的监督微调(SFT)；R1-Zero 是首个以纯 RL、… | web | [link](https://arxiv.org/abs/2501.12948) | high | `topics/llm_eval_capabilities/cache/3157e3b75bba8b59143266d0a0c22c6c5437422031b90b3f3b7113ba4e1c5f99.md` |
| 7 | DeepSeek-R1 证明大语言模型的推理能力可通过纯强化学习(GRPO)激励而无需人类标注的 SFT，其中 R1-Zero 是首个不依赖 SFT、纯 RL… | web | [link](https://arxiv.org/abs/2501.12948) | high | `topics/llm_eval_capabilities/cache/8c0c412d55f99c1415e6adb07dbffd086f129ff24dc4446fb22acc3b7ebbb1f8.md` |
| 8 | 用户/开发者调查显示 LLM 评测榜单分数与真实应用表现之间存在系统性差距，印证了'单一总分不足以反映能力、需按能力维度分别评估'的判断 | web | [link](https://arxiv.org/html/2502.14318v1) | high | `topics/llm_eval_capabilities/cache/3079b30e61b10b49f3624c0a5af6ced97f89d304261a4ba7209b3255dbe15591.md` |
| 9 | 推理模型的 RL 训练正从 SFT→RLHF 标准管线演进，DeepSeek-R1 提出的 GRPO 已成为开源社区主流的 RL 算法。 | web | [link](https://magazine.sebastianraschka.com/p/the-state-of-llm-reasoning-model-training) | high | `topics/llm_eval_capabilities/cache/f5feb85e793a48c6037d1f4d7d8cfe229ebe4867dc29967f9c3e14199a2b49b7.md` |
| 10 | RL 后训练已超越预训练规模，成为前沿 AI lab 模型间最关键的差异化竞争轴，即'后训练成为核心战场'。 | web | [link](https://www.digitalapplied.com/blog/post-training-revolution-rl-new-moat-2026) | medium | `topics/llm_eval_capabilities/cache/46ca01cdb7281761e17257c28f63291bddb27d3790f1c8e886b8b5434b8f7883.md` |
| 11 | 在 Claude Code 环境下用 74 个真实编程任务实测，GLM-4.6 的代码能力超过 Claude Sonnet 4，较 GLM-4.5 提升约 2… | web | [link](https://www.qbitai.com/2025/09/338660.html) | medium | `topics/llm_eval_capabilities/cache/dff1cbf0aedbb95c21699bd7e4b6a1be5c64cdd8a6a1be218221ebd56ca863af.md` |
| 12 | DeepSeek-V3 通过架构创新（671B MoE 仅激活 37B、MLA、无辅助损失的负载均衡）配合 14.8T tokens 的 FP8 大规模预训练… | web | [link](https://arxiv.org/html/2412.19437v1) | high | `topics/llm_eval_capabilities/cache/a366e05bc0ce5ceb5f22f3d0510304fe1ad15a0d78add01e2fd849dff0ffbcf2.md` |
| 13 | GLM-5.2 的长程任务能力源于规模更大、领域更广、执行模式更复杂的 agentic RL 后训练。 | web | [link](https://z.ai/blog/glm-5.2) | medium | `topics/llm_eval_capabilities/cache/a2e3e89c7b65b3c02b3fa5d3621a750113cca008548d92b9a0a16bedb598a310.md` |
| 14 | 社区共识认为 GLM 4.6 是当前最强的开源权重 coding 模型，但代码能力强不等于在最长程任务上登顶——Anthropic 在最长程任务上仍占优。 | web | [link](https://www.reddit.com/r/LocalLLaMA/comments/1nx18ax/) | medium | `topics/llm_eval_capabilities/cache/1b87d3ac9000a73e804df0885956d3ffe0da90094e2e1f852fb25c2dc11ebe49.md` |
| 15 | DeepSeek 各模型分工不同：V3 是通用基座（架构+预训练），R1 是用 RL 后训练特化的推理模型，V3.1/V3.2 用混合 thinking 模式… | web | [link](https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond) | medium | `topics/llm_eval_capabilities/cache/08a6b32b9d45688d86f1d14b3c85600ec4bb280a33360ba83e27f6bca8eb0095.md` |
| 16 | 奖励模型默认不会把指令遵从或诚实泛化到训练分布之外，反而倾向于回退到'像互联网文本'的人设，因此指令遵从与指令泛化是两个不同且可能冲突的维度。 | web | [link](https://www.lesswrong.com/posts/Yio4nmD8JMttx9o9S/) | medium | `topics/llm_eval_capabilities/cache/6d1d666839d67dd31cad9303c266fd924c53ca614de145eb5bc65b67a6f8fe8c.md` |
| 17 | GLM-4.6 在 Claude Code 环境下 74 个真实编程任务实测中超过 Claude Sonnet 4 并领先其他国产模型，较 GLM-4.5 提… | web | [link](https://www.qbitai.com/2025/09/338660.html) | medium | `topics/llm_eval_capabilities/cache/ca827f4be5d460560a1a9548967d95f8ce3c02987d37797d3e906f4c9b7d749f.md` |
| 18 | DeepSeek-V3 的基础能力来自架构创新（671B MoE/37B激活、MLA、无辅助损失负载均衡、FP8混合精度）与14.8T token大规模预训练… | web | [link](https://arxiv.org/html/2412.19437v1) | high | `topics/llm_eval_capabilities/cache/69eed2b0001d605a93ae0ece1b118a6def4cb7216d0572727885fafd07664f0d.md` |
| 19 | 后训练（多轮 RLHF/RLAIF）已取代指令微调成为前沿模型的主要差异化轴线，可扩展性远超指令微调。 | web | [link](https://www.interconnects.ai/p/frontier-model-post-training) | medium | `topics/llm_eval_capabilities/cache/084e52e3fa419a2e2f57ae55fb5b40699b609703bebb9e50a1e46756e465d257.md` |

## 6. 待复核 / Needs Review
- ⚠ 后训练（多轮 RLHF/RLAIF、RL）已取代指令微调成为前沿模型间最关键的差异化竞争轴，可扩展性远超指令微调，即'后训练成为核心战场'；但同时有观点修正：…

## 7. Facet 覆盖
| facet | 问题 | 状态 |
|-------|------|------|
| `f_用户需求是异质的_可分解的吗_主流评测框架是否已按能力维度_指令` | 用户需求是异质的、可分解的吗？主流评测框架是否已按能力维度（指令遵从/泛化/世界知识/长程任务/角色扮演/数理推理/推理深度）拆解，而非一个总分？ | open |
| `f_glm_rl` | GLM 的代码与长程任务优势是否被公开评测+社媒共识验证为'后训练（RL/长程任务+代码）驱动'，而非预训练架构？ | open |
| `f_deepseek_glm` | DeepSeek 的角色扮演与数理推理等泛化能力是否被验证为'架构创新+预训练'驱动，而其代码能力因未做专项后训练而弱于 GLM？ | open |
| `f_post_training` | 后训练（post-training）是否正成为当前大模型差异化竞争的核心战场？预训练边际收益是否在下降？ | open |
| `f_trade_off` | 是否存在'能力权衡'证据：一个模型难以同时登顶指令遵从性与指令泛化性/角色扮演？评测榜单是否反映这种 trade-off？ | open |
| `f_b_vs` | 中文社区（知乎/小红书/B站/微博）对国产模型评测的实证共识与质疑：榜单分数 vs 真实体感差异 | open |

---
_声明：本报告为信息关联与凝练，非投资/行动建议。每条主张均附来源链接与缓存路径，可回溯。_
