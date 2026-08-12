# Content-addressed originals

Optional. Store one JSON per content hash:

```json
{
  "content_hash": "<sha256>",
  "url": "https://…",
  "platform": "web",
  "title": "…",
  "cached_full_text": "…",
  "referenced_by": ["topics/my_topic"]
}
```

**Do not** commit third-party full text you do not have rights to redistribute.  
For public forks, prefer link + short quote + provenance in `topics/*/sources/` only.
