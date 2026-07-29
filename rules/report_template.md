---
status: canonical
as_of: 2026-07-29
---

# 报告契约 / Report Template

ResearchOS 产出两类 markdown，都可回溯（每条主张附来源链接 + 缓存路径）：

## 1. `reports/world_model.md` — 活文档（覆盖重生）

由 agent 从 `knowledge.md` 重排。固定段落：
1. 主题概览 / Worldview（当前 L0 proposition + confidence）
2. 开放问题 / Open Questions（= 下一轮检索议程）
3. 分主题综合 / Themes（每条 L1 narrative + stance + confidence）
4. 已证实发现 / Corroborated Findings（L2 表：发现 + 印证数 + 跨平台 + 可信度 + 冲突）
5. 来源索引 / Source Index（L3 表：主张 + 平台 + 链接 + 可信度 + 缓存路径）
6. 待复核 / Needs Review
7. Facet 覆盖
8. 声明（信息关联非建议）

这是主题不断累积、越来越完整的图景。

## 2. `reports/sessions/<date>_<facet>.md` — 会话报告（不可变追加，Phase 2）

单轮检索的三段式：核心要点 / 论点与证据逻辑链（每条带 provenance）/ 来源索引 + 待人工复核 + 声明。

## 累积规则

`world_model.md` 覆盖重生（当前真相）；`sessions/` 追加（历史）。每个 claim 携带 provenance（url + 缓存路径 + 可信度），永远可回溯到留存的原文。
