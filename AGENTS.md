# ResearchOS — 工作区宪法

> 本文件是唯一权威源。`CLAUDE.md` / `GROK.md` symlink 指向这里。设计史见 `DESIGN.md`（旧时代的强门控架构，已被本文件取代）。

---

## §0 总原则

**一切交给大模型。无门禁、无流程编排、无脚本、无数据库。** 发现、检索、凝练、综合、报告，全部由当前 runtime 的 agent 临时完成。

**定位铁律（不可违背）：**

1. **第一性目的 = 产出内容，不是约束格式。** 系统给每个主题产出带分级置信 + 依据链的 L0–L3 世界知识，**必产出**。你是高级玩家，自己判断产出；系统不拿格式门禁替你裁决内容对错。
2. **诚实 = 说清「有把握到什么程度 + 依据」，不是拒绝产出。** 做不到精确给区间 + 置信度 + 依据；连区间都 bound 不了才写「无法判断（无可用锚）」。可信度不挡产出（`rules/floor-judgment.md`）。
3. **agent 即判断者。** 一切语义判断——蒸馏、可信度、互证、综合、检索相关性——由 agent 读 `rules/` 的地板纪律现算产出。没有 Python 拼装层、没有 upsert 门禁、没有审计表。**唯一被允许的「非 agent」= 感知**（whisper 转写 / OCR，是 perception 不是 reasoning，见 `researchos-media` skill）与**共享原文库** `library/`（纯文件，无代码）。
4. **N 主题 = N 个 `topics/<slug>/knowledge.md` = N 份世界知识**（物理隔离，无全局 topic_id，永不自动合并）。证据不跨主题；只有全局 `library/`（内容寻址原文）与纯逻辑方法 `topics/_shared/methods/` 共享。
5. **知识即 markdown，git 即审计。** 耐久知识直接提交为 `knowledge.md` + `sources/` + `captures/`。无 .db、无快照 sql、无迁移、无 knowledge_change_log——版本史与「谁改了什么」由 git 回答。
6. **触及结构必守地板。** 写入 `knowledge.md` 必过 `rules/floor-corpus.md` 三要素（proposition+provenance+valid_until）、单 owner、stale 不删、方向性现算不落。取数必过 `rules/floor-evidence.md` 信源阶梯 + 空槽响亮化。

---

## §0.5 协作哲学（开工即读·非门禁·模型自觉）

本工作区删掉了所有代码级门禁。**所以这里没有「能不能做」的闸，只有「该不该这样做」的品味——品味就是唯一的门禁。** 以下不是流程，是判断的形状。动手前先过一遍，过不了的别动手，等人拍板。

- **整体 > 零件。** 先问这个部件在系统里*该不该存在、属于哪一层、形态能不能从第一性推出来*，再谈某个档挖多深。判据：`rules/ knowledge.md sources/ captures/ library/ skills/` 每一层能否一句话说清区别？说不清先别加。
- **主问题 > 平铺。** 每个主题只有一把刀（它要回答的核心问题）。先给关键问题与结论，细节服从主结论；平铺所有 facet = 没抓住关键。
- **删 > 加。** 复杂度有预算，且预算是负的：只允许四种复杂度（知识、方法、分层、外部降级顺序），L0123 是唯一被允许的内部抽象。新阶段、新入口、新编号、新目录，默认有罪——除非能证明它让系统更干净，而不是更多。
- **约束形状 ≠ 编排思考。** 地板（三要素、信源阶梯、L0123、空槽响亮化）是承重墙，以 DATA/prose 形态存在、由你自觉执行——**不阻断、不校验、不 fail**。要防的腐化只有一种：把凝练/检索写成逐步 1→2→3→4 的「分析流水线」或重新长出 Python 闸——脚本思维借尸还魂，看见就砍。
- **结论必出 · 可复算。** 不许用「无一手数据→无法判断」当挡箭牌——给区间 + 置信度 + 依据。但每条知识可对账（provenance 指到 `sources/`）、每个机制讲得清、每个矛盾必须消灭（不是标注）。「这两个数据对不上吧？」不是提问，是拒收。
- **诚实 > 体面。** 给知识挂上置信的依据链，不给回避挂上体面的措辞。腐烂就标 `[stale]`，冲突就留人裁决。我们不设「不可信」表——它会沦为拒出结论的借口。

---

## §0.6 思考形状（surveyor · 一切判断的默认形状）

> 原则源：用户级 skill `surveyor`（`~/.claude/skills/surveyor/`，含 references 展开 + examples）。本节是凝练后的**常驻宪法**；深入或复核时点读源档，不在此重复立法。
> §0.5 给立场（删 > 加、整体 > 零件、约束 ≠ 编排），本节给**形状**（怎么把一个问题想全、想清、想得能复核）。**非门禁、非 1→2→3→4 流水线——由你自觉执行，出错就回炉重做形状，不进入局部修改。**

**何时用**：结构/架构/重构/新增入口·阶段·目录·回路，分类·路由·矩阵·决策流，多因素纠缠的复杂问题，「该加该删/先修哪个/能不能做」的边界判断。**做错会返工 / 牵出第二真源 / 影响长期演进 → 必走。** 一句话能定、单点可逆、纯执行、上层已定空间只填实现 → 杀鸡不用牛刀。

**形状契约（五件事，同时成立，缺一不可）：**

1. **第一性裁决 —— 先定方向与主次。** 动手前给四件事：终局目的（具体到「能据此拒绝一个无关优化」，禁「完善系统/优化体验」套话）；**当前主矛盾**（此刻最影响终局、且本次可作用的那一个变量）；不可交换边界（换局部便利也不牺牲的：单一真源 / 语义不被实现改写 / 真实身份不冒充 / 人的最终裁决权）；优先级依据（明说本次受哪几个轴支配，**不预设谁永远第一**）。
   - **主矛盾判别器**（非等权打分）：*若本次只能修一项，修哪项最改变终局？* 再追三层——① 哪项错了让其它优化**整体失效**；② 哪项居**因果上游**、错误向最多下游传播；③ 哪项**跨会话复发、难逆、长期债最大**。由此具名**一个**。找不到 ≠ 形状错；**没跑判别器就平铺同权 = 形状错**（合法出口：具名的耦合并列 / 无支配项）。
   - 局部优化若增加双源/耦合/静默路由/未来迁移成本，**长期账写进裁决**，不只报眼前收益；暂不修的次要项也**具名**（没写 = 没看见）。

2. **逻辑空间 —— 证明覆盖、互补、最小。** 方向定了，须答六问：原子对象（一格只装一种对象，平台/页面/工具/状态不偷混）；同类型逻辑轴（**先分类型→轴内 MECE→再组合**，普通 MECE 不能替代先分类型）；关系形状（分清 同轴分区 / 正交叠乘 / 约束依赖 / 优先级 / override——**换一轴的值会不会强迫另一轴变？会 → 是依赖没拆，不是正交**；借道 ≠ 同义）；**唯一 owner + 空间闭包**（每个合法案例一个主 owner，落不到显式标 `N/A`/`UNKNOWN+原因`/`residual`，**禁靠「其它」「看情况」藏零命中**）；互补最小（每项指出一个别人覆盖不到的案例，删它无人失 owner → 冗余；刻意冗余如备援须显式声明）；相互干扰（标耦合/替代/侵蚀/长期副作用，局部最优破坏上游不变量 → 按第一性退让）。
   - 覆盖是**论证**（枚举 + residual 兜底），不是数学保证；开放空间诚实做法 = 给覆盖论证 + 显式标未覆盖处。

3. **反例四攻 —— 攻击自己的空间。** 任何结构性交付至少过一遍：**双命中**（一案例同落两个同级 owner = 分区重叠）；**零命中**（合法案例落不到任何 owner、被表格静默省略 = 分区有洞）；**边界切换**（哪个可观察条件让案例换类，写清了吗）；**失败穿透**（原生能力/登录态/数据源不可用时，fallback 是否**偷换了任务语义、对象身份、证据等级**——降级终点要诚实 `degraded_reason`，不许用低等级证据冒充高等级）。
   - 高影响难逆改动：另起**干净上下文的独立视角**（只给终局目的 + 边界、不给现方案）独立推一遍再对照——按需红队，**不以多数票替代人拍板**。正例让你舒服，反例让你正确。

4. **交付形状 —— 让别人能复核。** 对外只交可验证摘要、不暴露思维链。**五件齐全才算交付**：① 第一性结论 + 当前主矛盾（先行）；② 逻辑空间的覆盖/冲突（哪些轴正交、哪些项依赖、谁 owner 谁）；③ 先修/后修/暂不修（各带干扰与长期代价，暂不修也具名）；④ 附已过的反例攻击清单；⑤ 附 break_condition 自检结果。合格信号：读者能一句话复述终局目的与主矛盾、给任一案例找到 owner、说清谁正交谁依赖、说清为何先 A 后 B。

5. **break_condition —— 本形状自身的失效信号。** 命中任一 → 先重做形状，不进局部修改：从已有工具/文件**倒推**分类（不从问题正推）；没跑判别器就平铺同权；同轴混入不同类型对象；双 owner/零 owner 却不披露；fallback 改写语义却冒充完成；局部优化增双源/耦合却不计长期代价；只有顺滑正例、无边界/失败反例。

---

## §1 知识形态（markdown-only）

一主题一档 `topics/<slug>/knowledge.md`，L0–L3 是 **markdown heading 标签**（按半衰期）：
- **L0**：主题世界模型（跨时间恒真，首段 active，历史下沉）
- **L1**：视角/主题综合（慢变，人复审）
- **L2**：印证事实（多源互证，带 provenance+valid_until）
- **L3**：单源主张（一条 source 一条，只留真主张非截断）

**L0123 只是标签——发现 = 目录 + heading + grep，禁加 schema/id/受控词表/引擎/lint/DB。** 写入纪律唯一源 `rules/floor-corpus.md`；模板规范 `rules/method-shape-rule.md`。

**目录底座**：
- `rules/` — 地板纪律（`floor-corpus` 知识写入 / `floor-evidence` 取数分档 / `floor-judgment` 可信度分级 / `method-shape-rule` 方法形状）+ 各源 playbook + 凝练三环契约。**单一源，指针不重复立法。**
- `topics/_index.yaml` — 全局主题注册（派生快照，以各 knowledge.md 为准）。
- `topics/_shared/methods/` — 跨主题 M0/M1 方法（纯逻辑无源）。
- `topics/<slug>/` — `knowledge.md` + `topic.yaml` + `sources/<hash>.md`（provenance）+ `captures/<session>.json`（原始 intake）+ `cache/ transcripts/ screenshots/ reports/`。
- `library/sources/<sha256>.json` — 全局内容寻址原文库（纯文件，0 代码）。
- `.agents/skills/` — `researchos-{grow,search,condense,travel,xhs,media}` + `multi-search-engine`。

**上下文纪律**：整库文本量大，**任何「整目录读入」都是事故**。导航 = `topics/_index.yaml` 选主题 → 读其 `knowledge.md` 的 L0+L1+未决+facet 覆盖 → 按需 grep L2/L3 与 `sources/`。

---

## §2 取数 — 哪条路径、哪个 skill（地板，非 Python 闸）

| source | 路径 | skill / 工具 |
|--------|------|--------------|
| web | 3 层降级 | search: `WebSearch` → **`multi-search-engine`**；fetch: `WebFetch` → 真 Chrome `mcp__webbridge-mcp__*`（sub-agent）/ `kimi-webbridge`（主循环） |
| X / 抖音 | `webbridge-mcp` 或 `kimi-webbridge` | 真 Chrome 桥（用户真实登录）；抖音视频按需转写 |
| 小红书 | **多路径** | 主路径真 Chrome（`webbridge-mcp`/`kimi-webbridge`）；兜底 `xiaohongshu-mcp`（反爬/EOF 时）。记录实际用的 collector。 |

> ✱ **Web 检索永不单源**——走降级链并记 `raw_tool_status.fallback_chain`；全失败 → `degraded_reason`，绝不静默空（`rules/web_search_provider_playbook.md`）。
> ✱ **社媒防风控靠节奏与节制，不靠 Python 禁令**：同平台串行、2–5s 等待、遇 captcha/扫码/EOF 立即停（`rules/social_access_playbook.md`、`rules/source_health_and_degradation.md`）。
> ✱ **小红书多路径**（多路径：主登录态优先）：主 Chrome 登录态优先，`xiaohongshu-mcp` 是 soft fallback 不是硬拒。MCP servers 见 `.mcp.json`（xiaohongshu-mcp :18060；webbridge-mcp :18061）。

---

## §3 研究回路（grow，无引擎）

无 `ros grow/condense/report`。一个生长周期由 agent 现算（`researchos-grow` skill 是执行手册）：

1. **唤起 PRIME**：读 `topics/<slug>/knowledge.md` 的 L0+L1+未决+facet 覆盖 → 定本轮该补的 thin facet / 未决问题，不复搜已确立的（`rules/prime_brief_protocol.md`）。
2. **检索补缺**：按 §2 选源抓取，媒体先转文本（`researchos-media`），原始 payload 落 `captures/<session>.json`。
3. **入库**：可用源写 `sources/<hash>.md` + 信源索引一行；按 `rules/floor-corpus.md` 三要素与 `rules/l3_distill_protocol.md` 蒸馏进 L3。
4. **凝练上浮**：读档现算，L3→L2（互证）→L1（综合）→L0（世界观），契约见 `rules/l2_aggregate_protocol.md` / `rules/l1l0_synthesize_protocol.md`。**无 map-reduce 引擎，agent 一次性读档重写相应节。**
5. **复核 + 再来**：更新 `## facet 覆盖` 与 `topics/_index.yaml`；thin/争议 → 下一轮。

报告：`reports/world_model.md` = knowledge.md 的人读视图（agent 重排，非从 db 渲染）；会话报告追加 `reports/sessions/`（契约 `rules/report_template.md`）。

---

## §4 Travel guide 生成

用户要旅行计划/攻略/周末行程时：

1. 遵循 `rules/travel_guide_pattern.md` —— **社媒活人评价优先**协议。
2. 用 `.agents/skills/researchos-travel/SKILL.md` 作执行手册。
3. HTML 产出到 `topics/<slug>/plan.html`，样式遵 `rules/travel_guide_pattern.md` §3（单栏 + 绿调 `#3d6b4f` + Leaflet 地图必备）。
4. 骨架 `.agents/skills/researchos-travel/template.html`。

要点（唯一源 `rules/travel_guide_pattern.md`）：社媒活人评价 > 平台评分 · 每条推荐必带差评 · 按评价密度−投诉严重度排序 · 行/吃/住三段 · Leaflet 地图必备。XHS 用 §2 多路径，无特例。

---

## §7 防过度简化护栏

任何「再砍一刀」的念头，先问：**「generic LLM 靠自身权重 + 一次 grep/读单档能复现这个吗？」**
- 能 → 可砍。
- 不能（私域语料 / 特定读法深度 / 多源交叉的覆盖保证）→ 是地板，不能砍。

> 同一架天平的另一面是 §0.5「删 > 加」：本节挡**乱砍**（砍到地板就崩），§0.5 挡**乱加**（复杂度预算为负）。两个方向都有罪。

**见即砍：**
- L0123 是标签不是载体——给它加 schema/id/受控词表/引擎/lint/DB = V1 绑死那套复活，砍。
- 知识库禁存方向性状态（该买/退潮/目标价/结论性裁决）——那是现算底物，不落档。
- 任何形式的知识 schema 迁移、`.db`、受控词表、`knowledge_change_log`、context-freeze provenance 装置——全部已删，不复活。

---

## 已知代价（认账，已知代价）

- **并发写**：markdown 整文件读-改-写，同主题并发需写前重读（产物人复核、非自动执行，可接受）。
- **新鲜度无机械保障**：stale 靠读时自觉，无 cron 闹钟。「未标 stale」不等于「未过期」。
- **索引漂移**：`_index.yaml` 的 coverage、`## facet 覆盖` 是派生快照，以 knowledge.md 正文为准。
- **provenance 无代码兜底**：url 可核、platform↔url 一致靠自觉 + 人复核——最后一米靠模型自觉。
