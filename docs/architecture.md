# Architecture (current)

## Form

- **Knowledge** = `topics/<slug>/knowledge.md` (L0–L3 headings, not schemas)
- **Intake** = `captures/*.json` + `sources/<hash>.md`
- **Optional originals** = `library/sources/<sha256>.json`
- **Method** = `rules/*` + `.agents/skills/*`
- **Tools** = optional MCP/daemons under `tools/` (no semantic judgment)

## Loop ownership

| Stage | Handbook |
|---|---|
| Prime | `rules/prime_brief_protocol.md` + grow skill |
| Search | `researchos-search` / `multi-search-engine` / `researchos-xhs` |
| Media | `researchos-media` |
| Distill / condense | `researchos-condense` + l3/l2/l1l0 protocols |
| Report | `rules/report_template.md` |

## What was removed for the public release

- Personal multi-topic corpora and CAS dumps
- Historical SQL snapshots from the pre-markdown engine era
- Embedded third-party full-text caches

Design archaeology of the old gate/DB engine (if needed) lives only in private vaults — not required to run v0.1.
