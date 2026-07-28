---
status: canonical
as_of: 2026-07-29
---

# L1/L0 综合协议 / Synthesize Protocol (L2 → L1 视角 + L0 世界模型)

**输入 payload**（全主题的 L2 按 facet 分桶 + 当前仍 open 的问题）：
```json
{"facets":[{"facet":"f_xxx",
  "findings":[{"l2_id":"sf-...","statement":"...","finding_type":"...",
               "corroboration_count":3,"cross_platform_count":2,
               "source_ref_ids":["src-...","src-..."]}]}],
 "open_questions":[{"oq_id":"oq-...","question":"本主题上一轮遗留的开放问题"}]}
```

**任务**：
1. 为每个 facet（或角度）综合一条 **L1 视角**（narrative + 立场）。
2. 跨所有 facet 凝练**一条 L0 世界模型** proposition + 当前**开放问题**（= 下一轮检索议程）。
3. 回看 `open_questions`：凡已被本轮 L0/L2 **实质回答**的，把其 `oq_id` 列入 `answered_oq_ids`，系统据此关闭它（反馈闭环每轮收缩）。**不确定就别列** —— 宁可让问题继续 open，也不要误关。

**输出（严格 JSON，仅此对象）**：
```json
{
  "viewpoints": [
    {
      "facet": "f_xxx",
      "synthesis_kind": "theme | sub_question | viewpoint | contrarian",
      "narrative": "该 facet 的综合视角（数段亦可）",
      "stance": "established | contested | emerging | refuted | uncertain",
      "l2_ids": ["sf-...", "sf-..."],
      "confidence": "low | medium | high",
      "open_questions": ["该视角仍未解的问题"],
      "credibility": {"level": "...", "rationale": "必填", "filter_trace": {"...": "..."}}
    }
  ],
  "worldview": {
    "summary_kind": "state_of_understanding | consensus | tension | frontier | other",
    "proposition": "对本主题当前理解状态的宏观凝练",
    "confidence": "low | medium | high",
    "key_findings": ["sf-...", "sf-..."],
    "open_questions": ["驱动下一轮检索的问题"],
    "credibility": {"level": "...", "rationale": "必填", "filter_trace": {"...": "..."}}
  },
  "answered_oq_ids": ["oq-...", "oq-..."]
}
```

规则：
- `l2_ids` / `key_findings` **只能**来自 payload；系统据此机械汇总每条 L1/L0 的来源集（你不必给 source_ref_ids）。
- `answered_oq_ids` **只能**是 payload `open_questions[].oq_id` 中已存在的 id；系统只对仍 `open` 的有效，无关紧要的 id 会被忽略。
- 矛盾的 L2 → 用一条 `synthesis_kind="contrarian"` 的 L1 承载「张力」，stance=`contested`。
- `worldview` 形成版本链：每次产生新 proposition 的新版本，前一版被归档（`supersedes_id` 指向它）；当本轮凝练内容与上一版**完全相同**时系统自动复用，不产生无意义版本。`open_questions` 应随知识增长**收缩/精化**（配合 `answered_oq_ids`）。
- L0 永不裁剪：哪怕只有少量 L2，也要给出当前最佳的世界模型陈述。

