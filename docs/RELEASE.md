# How to cut a release

## Preflight

1. `./scripts/check-public.sh` exits 0.
2. No personal topics under `topics/` except demos/templates.
3. `go test ./...` in `tools/social_mcp/webbridge_mcp`.
4. CHANGELOG section for the version exists.

## Tag

```bash
git tag -a v0.1.0 -m "ResearchOS v0.1.0 — public multi-agent research loop"
git push origin v0.1.0
```

## GitHub Release body (template)

```markdown
## ResearchOS v0.1.0

Multi-agent research loop for coding agents: Prime → Search → Capture → Distill → Condense → Grow.

### Highlights
- Markdown topic isolation (L0–L3 world knowledge)
- Epistemic floor rules (no analysis DB)
- Optional webbridge-mcp for sub-agent Chrome access

### Install
git clone … && open AGENTS.md in your coding agent

### Upgrade / private vaults
See docs/PRIVATE_VAULT.md
```

## Artifacts (optional)

This project is mostly markdown + a small Go module. A release tarball of the tree (without `.git`) is enough:

```bash
git archive --format=tar.gz --prefix=research-os-v0.1.0/ v0.1.0 -o dist/research-os-v0.1.0.tar.gz
```
