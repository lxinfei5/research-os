---
status: canonical
as_of: 2026-07-29
---

# floor-corpus — 知识与语料地板（写入纪律唯一源）

> 这是 ResearchOS 删掉全部代码门禁后，**唯一**约束「知识怎么写进 knowledge.md」的地板。
> 它不是 gate——不阻断、不校验、不 fail。它是承重墙：由你和子 agent 自觉执行，人复核兜底。
> 要防的腐化只有一种：**把 markdown 知识重新长出 schema/id/受控词表/引擎/lint/DB——那是 V1 复活，见即砍。**

## L0 · 本域恒真（一次蒸馏）

知识只以 `topics/<slug>/knowledge.md` 单档存在，L0–L3 是 markdown heading 标签（按半衰期分，**从不**分准不准/看多看空）。每条知识带三要素（proposition + provenance + valid_until）。过期标 `[stale since]` 不删。方向性状态现算不落。发现 = grep + 读单档。删代码门禁后，**结构的地板由这篇 prose + 人的品味守住**，不再由触发器/受控词表/审计表守。

## 本域会怎么腐（这些原则在防什么）

- **schema 复活**：给 knowledge.md 加 frontmatter enum、给 L 层加 id/受控词表/迁移/lint/DB。→ V1 绑死那套。**break_condition：出现任何 `CREATE TABLE`、`.db`、受控词表、迁移编号 = 腐化，砍。**
- **双源腐化**：同一事实在两处各写一份，各自漂移。→ 单 owner + 指针不复制。
- **方向落库**：把「该买/退潮/目标价/结论性裁决」当客观事实写进档。→ 现算不落。
- **无源知识**：写一条没有 provenance 的「我记得」。→ 三要素强制。
- **僵尸新鲜**：写了 `valid_until` 却无人回读，过期事实仍当现值。→ stale 自觉 + 读时判。

## L0–L3 是 heading 标签（纯度护栏）

1. L-level 只以 markdown heading 出现（`## L0/L1/L2/L3`）；发现 = grep。**禁** frontmatter enum / id / schema / 受控词表。
2. **无 promote 引擎**：L3→L2→L1→L0 的上浮由 agent 读档现算，或人触发子 agent 产 markdown 提议、改不改人定。绝不自动/不 gate/不落库状态机。
3. **无 L-level lint**：放错层只是「读着别扭」，永不阻断写入。
4. **L3 零存值**；禁任何 L 层设对错/命中率/看多看空/verdict 列；**禁存方向性状态**（现算不落）。
5. L-level ⊥ 可信度（层级=半衰期；可信度=inline 前缀标签 T0–T4 / S/A/B/C，见 `floor-judgment.md`）。
6. **不 mandate 四层**：只在内容真跨到某半衰期才写那层 heading。加层=敲一行，删=删 heading。零 enum、零迁移、零 gate。

## 写入三要素（每条知识必带）

1. **proposition**：一句可证伪的完整陈述（主语 + 谓词 + 可核细节）——是真主张，**不是 verbatim 截断**。
2. **provenance**：平台/作者/时间/链接，指到 `sources/<hash>.md`，原文在 `library/sources/<hash>.json`。**url 必须可核**（http(s) 或 `researchos://first-party/<hash>`）；**platform 标签须与 url host 一致**（xiaohongshu.com 的链接就标 xiaohongshu，不标 web）。
3. **valid_until**：自然寿命——政策/订单/产能 → 至下一披露；盘口/资金 → 至当日；情绪/叙事 → 约 N 天。「长期成立」不算时效。

## 单 owner + 指针不复制

一事实一 owner：按 proposition 的主语实体归唯一档（同一主题内归到对应 facet 节）。跨档/跨主题引用只走相对路径 + 锚 heading，**绝不转述目标数字**（转述 = 双源腐化）。原文一律共享 `library/sources/<hash>.json`，主题内只留 provenance。

## stale 不删 · 读时判

- 过 valid_until → 标 `[stale since YYYY-MM-DD]`，**不物理删**。
- stale 条不再作主判据，只作历史对照/反推原料。
- 被新源重新印证 → merge 更新时效、清 stale、留「曾过期 · YYYY-MM-DD 复活」一行。
- **没有过期检查器，没有 cron 闹钟**（V1 死闹钟判例，不复活）。新鲜度靠读时自觉：「未标 stale」不等于「未过期」。

## 周期浓缩（人触发，非自动）

某 facet 节堆积近重/大量过期时，**人触发**子 agent 对该节：① 合并近重条 ② 标 stale/superseded ③ 把反复出现的 L2 结晶上 L1。子 agent **只产 markdown 提议，绝不自动改方法论/不落库/不 gate**。改不改人定。非常驻、不 cron、不自动跑。

## L0 版本链（git 即历史）

`## L0` 首段为 active；更新世界观时把旧段下沉为 `### archived · <date> · [superseded]`，新段置首。**版本链 = git 历史 + 段内日期**，无需 supersedes_id 列、无需「恰好一个 active」lint——首段即 active 是约定，人一眼可查。

## 信源索引与覆盖快照（派生，以正文为准）

`## 信源索引` 每源一行（content_hash/platform/kind/url/captured/valid_to），`## facet 覆盖` 是派生快照。二者都可能漂移，**以正文 L 条为准**。`topics/_index.yaml` 的 coverage 同理——派生快照，可 grep 重算。

## 指针

- 可信度判断与分级：`floor-judgment.md`
- 取数、信源阶梯、升格闸、降级：`floor-evidence.md` 及 `rules/*playbook.md`
- 方法车道 M0/M1：`method-shape-rule.md` + `method_lane_protocol.md`
- 凝练三环契约：`l3_distill_protocol.md` / `l2_aggregate_protocol.md` / `l1l0_synthesize_protocol.md`
