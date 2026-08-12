---
status: canonical
as_of: 2026-07-29
---

# L3 蒸馏协议 / Distill Protocol (source → L3)

> L3 is the **fast / single-source** end of the half-life axis — see `knowledge_layering.md`.  
> Do not treat an L3 claim as world-model (L0) without a later, half-life-aware promotion.

**输入 payload**（一条已留存原文）：
```json
{"source_ref_id":"src-...","url":"...","platform":"web|x|douyin|xiaohongshu|...",
 "source_kind":"article|note|post|video|image|...","title":"...","author":"...",
 "content_hash":"...","cached_text":"<原文全文，视频/图片已转写为文本>"}
```

**任务**：读 `cached_text`，蒸馏出**这条原文在说的一条主张**。proposition 必须是论点/事实本身，**不是正文截断**。判断它的可信度（见 `floor-corroboration.md`）。

**输出（严格 JSON，仅此对象）**：
```json
{
  "proposition": "这条原文的核心主张（一句话，非截断）",
  "claim_kind": "fact | analysis | rumor | breaking | opinion | data | other",
  "facet": "f_xxx（若能归入某 facet）或 null",
  "analysis_note": "可选：你的分析备注",
  "verbatim_excerpt": "可选：支撑该主张的一句原文引用",
  "credibility": {
    "level": "low | medium | high",
    "rationale": "必填",
    "filter_trace": {"independence": "...", "quality_density": "...", "recency": "..."},
    "independence_note": "可选",
    "echo_chamber_flag": false
  }
}
```

规则：
- 一条原文 → **一条** L3。不要拆成多条。
- `proposition` 若只是把 `cached_text` 前几句复制过来 = 不合格。
- `facet` 用 payload 暗示或留 null；系统在 aggregate 阶段按 facet 分桶。
