# L2 聚合协议 / Aggregate Protocol (L3 → 印证的 L2)

**输入 payload**（一个 facet 下的全部 L3）：
```json
{"facet":"f_xxx 或 _unfileted",
 "claims":[{"l3_id":"sc-...","proposition":"...","claim_kind":"...",
            "source_ref_id":"src-...","platform":"web|x|xiaohongshu|..."}]}
```

**任务**：把在说**同一件事**的 L3 聚合成 L2 发现。一条 L2 = 一个被（潜在）多源印证的事实/发现。

**输出（严格 JSON，仅此对象）**：
```json
{
  "findings": [
    {
      "statement": "被印证的发现（综合表述）",
      "finding_type": "fact | event | figure | claim | trend",
      "l3_ids": ["sc-...", "sc-..."],
      "conflict_note": "可选：若引用的 L3 之间有矛盾，在此说明",
      "credibility": {
        "level": "low | medium | high",
        "rationale": "必填",
        "filter_trace": {"independence": "...", "quality_density": "..."},
        "echo_chamber_flag": false
      }
    }
  ]
}
```

规则：
- `l3_ids` **只能**来自 payload 的 `claims`；系统丢弃 payload 之外的 id。
- **不要**提供印证数。`corroboration_count`（独立来源数）与 `cross_platform_count`（不同平台数）由系统从你引用的 `l3_ids` 机械算出。你只决定**哪些 L3 构成同一发现**。
- 单条 L3 也可成一条 L2（印证数=1）；但优先把同主题的多条合并。
- 来源相左 → 保留并写 `conflict_note`，不要二选一。
