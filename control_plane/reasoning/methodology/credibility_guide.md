# 可信度评估 / Credibility Guide (5 轴)

每条 L0–L3 证据行都必须携带一个可信度判断。社媒/私有情报**起点是高密度证据，不是自动低质噪音**——但你必须把过滤依据外化到 `filter_trace` 里，系统才允许写入。

## 5 个轴（综合成一个 level：low / medium / high）

1. **独立性 (independence)** — 是否多个互相独立的来源？还是同一信息的反复转发（回音室）？
2. **质量/密度 (quality_density)** — 信息密度高、可证伪、有细节，还是空泛口号？
3. **内部一致 (internal_consistency)** — 同一来源内部是否自洽？
4. **逻辑契合 (logic_fit)** — 是否与已确立的世界知识逻辑相容？相悖时是新信号还是错误？
5. **时效衰减 (recency_decay)** — 信息是否仍然有效？快变主题（如地缘政治）来源易过期。

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

## 断路器 (circuit breaker)

如果你判断这是**回音室**（大量转发但缺乏独立来源），把 `echo_chamber_flag` 设为 `true`。系统会**机械地把 level 封顶为 low**——「来源数量不能压过回音室嫌疑」。不要靠堆来源数把可信度抬高。

`rationale` 为空、`filter_trace` 为空对象都会被网关拒绝。
