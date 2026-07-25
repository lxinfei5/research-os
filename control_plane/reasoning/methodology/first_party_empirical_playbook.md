# First-party empirical evidence — intake & promote

## When this path applies

Use **first-party empirical** when the evidence is the researcher's own field measurement
(subscription quota tables, concurrency/RPM probes, lab notes) and **there is no public URL** by
nature. This is intentional retention, not a failed scrape.

Do **not** use this path for:
- XHS/X/web cards that lacked a URL (login wall / paywall / rate-limit) — those stay
  `restricted_reason` raw-only.
- Relabeling a social scrape as "first-party" to bypass the URL gate (platform must be `manual`).

## Capture shape

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

### Allowed `source_kind` values

| kind | use |
|------|-----|
| `first_party_empirical` | generic field measurement |
| `first_party_empirical_table` | structured comparison tables (quotas, prices, RPM) |
| `first_party_field_note` | free-form lab / diary notes |

`raw_metadata.provenance_class = "first_party_empirical"` is auto-stamped on capture when the item
is eligible; you may also set it explicitly.

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

- Single-source first-party evidence starts at **medium** credibility at most unless
  independently corroborated by public sources.
- Always keep the measurement premises in the claim (e.g. "93% cache hit rate", peak-hour RPM).
- Cross-check with public sources when available; first-party and public can co-exist as
  corroboration at L2.

## Iron rule

Python only checks **structure** (platform, source_kind, URL scheme). It does not judge whether
the measured numbers are true — that judgment stays in the agent + methodology layer.
