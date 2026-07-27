# First-party empirical & user briefing — intake & promote

## When this path applies

Use the **no-public-URL promote** path when evidence has no public URL **by nature**:

1. **First-party empirical** — researcher's own field measurement (quota tables, RPM probes, lab notes)
2. **User briefing** — background the user told the agent in conversation (facts, premises, constraints)
   that should enter the topic's evidence lane (then condense → L3), not stay only in chat context

This is intentional retention, not a failed scrape.

Do **not** use this path for:
- XHS/X/web cards that lacked a URL (login wall / paywall / rate-limit) — those stay
  `restricted_reason` raw-only.
- Relabeling a social scrape as "first-party" / "user_briefing" to bypass the URL gate
  (**platform must be `manual`**).

## Capture shapes

### A) Field measurement

```json
{
  "query": "…一手实测…",
  "source": "manual",
  "collector": "first_party_field_test",
  "capture_kind": "manual",
  "captured_by": "researcher",
  "raw_tool_status": {
    "data_origin": "researcher_first_party_empirical",
    "corroboration": "none_yet"
  },
  "items": [{
    "platform": "manual",
    "source_kind": "first_party_empirical_table",
    "title": "…",
    "author": "researcher",
    "content": "完整实测正文 / 表格 Markdown",
    "needs_review": false,
    "raw_metadata": {
      "facet": "f_…",
      "data_type": "comparative_quota_table"
    }
  }]
}
```

### B) User briefing (conversation knowledge)

```json
{
  "query": "用户口述背景",
  "source": "manual",
  "collector": "user_briefing",
  "capture_kind": "manual",
  "captured_by": "researcher",
  "items": [{
    "platform": "manual",
    "source_kind": "user_briefing",
    "title": "用户告知：…",
    "author": "user",
    "content": "完整口述内容（可分条）",
    "needs_review": false,
    "raw_metadata": {"facet": "f_…"}
  }]
}
```

### Allowed `source_kind` values

| kind | use | auto `provenance_class` |
|------|-----|-------------------------|
| `first_party_empirical` | generic field measurement | `first_party_empirical` |
| `first_party_empirical_table` | structured tables (quotas, prices, RPM) | `first_party_empirical` |
| `first_party_field_note` | free-form lab / diary notes | `first_party_empirical` |
| `user_briefing` | user-told background from chat | `user_briefing` |
| `user_briefing_note` / `briefing` | alias for short notes | `user_briefing` |

`provenance_class` is auto-stamped on capture when the item is eligible; you may also set it explicitly.

## Promote

```bash
ros capture payload.json --topic <slug> --auto-promote
# or later:
ros promote --topic <slug>
```

Promote mints:

```
researchos://first-party/<content_hash>
```

The SQLite URL gate accepts this scheme alongside `http(s)://…`. The retained `source_ref` enters
`knowledge.db` and is eligible for `ros condense` distill → L3 like any other source.

## Credibility notes (for the condense agent)

- Single-source first-party / user_briefing evidence starts at **medium** credibility at most unless
  independently corroborated by public sources. User briefing is intentional evidence, not automatic low quality.
- Always keep measurement premises / who said what in the claim (e.g. "93% cache hit rate", "per user 2026-07").
- Cross-check with public sources when available; first-party and public can co-exist as
  corroboration at L2.

## Iron rule

Python only checks **structure** (platform, source_kind, URL scheme). It does not judge whether
the measured numbers or briefing content are true — that judgment stays in the agent + methodology layer.
