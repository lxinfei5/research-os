---
status: canonical
as_of: 2026-07-29
---

# 可信度评估 / Credibility Guide (5 轴)

每条 L0–L3 证据行都必须携带一个可信度判断。社媒/私有情报**起点是高密度证据，不是自动低质噪音**——但你必须把过滤依据外化到 `filter_trace` 里，系统才允许写入。

## 5 个轴（综合成一个 level：low / medium / high）

1. **独立性 (independence)** — 是否多个互相独立的来源？还是同一信息的反复转发（回音室）？
2. **质量/密度 (quality_density)** — 信息密度高、可证伪、有细节，还是空泛口号？
3. **内部一致 (internal_consistency)** — 同一来源内部是否自洽？
4. **逻辑契合 (logic_fit)** — 是否与已确立的世界知识逻辑相容？相悖时是新信号还是错误？
5. **时效衰减 (recency_decay)** — 信息是否仍然有效？快变主题（如地缘政治）来源易过期。

## domain 可信度上限（单源 · 各域起点天花板）

不同来源域的**起点天花板**不同（5 轴在此之上微调）。本表是 domain 上限的**唯一源**；各域 playbook 只指过来，不复述：

| 域 | 起点天花板 | 升档条件 | 出处 |
|---|---|---|---|
| 社媒卡片（XHS/抖音列表卡片，详情因风控未取） | **medium**（单卡可压 low） | 多源独立 + 详情补齐 + 公网/结构化旁证 → high | `source_health_and_degradation.md` §三 |
| 单源 first-party / user_briefing（无公网旁证） | **medium**（至多） | 被公网/其它独立源印证 → 可升 high | `first_party_empirical_playbook.md` §Credibility notes |
| 多源独立收敛 / 升格 `[street-consensus]` | high（工作事实） | — | `knowledge_layering.md` 印证规则 |
| 单源软源 / 未过升格闸 | 线索（不单独驱动结论） | 过升格闸 → 升档 | `knowledge_layering.md` |

> **计数 ≠ 可信度**：独立源数喂 `independence` 轴，但回音室（同根转发链）按 1 源计——见下节 `echo_chamber_flag`。

## 输出（嵌在每个 stage 的 `credibility` 字段里）

```json
{
  "level": "low | medium | high",
  "rationale": "一句话说明为什么是这个 level（必填，永不留空）",
  "filter_trace": {"independence": "...", "quality_density": "...", "recency": "..."},
  "independence_note": "可选：独立性的具体说明",
  "echo_chamber_flag": false
}
```

## 回音室标记 (echo_chamber_flag)

如果你判断这是**回音室**（大量转发但缺乏独立来源），把 `echo_chamber_flag` 设为 `true`。
系统**不会**机械改写你的 `level`——可信度判断留给 agent。flag 会写入库，并在 rationale
前加 `[echo_chamber_flag]` 备忘（当 level 不是 low 时）。不要靠堆来源数抬高可信度；
若确属回音室，你自己应倾向标 `low`/`medium`。

`rationale` 为空、`filter_trace` 为空对象都会被网关拒绝。
