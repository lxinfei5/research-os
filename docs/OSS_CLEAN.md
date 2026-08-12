# OSS clean record (2026-08-12)

## Intent

Ship ResearchOS as a reusable multi-agent research framework while preserving a private personal vault.

## Actions taken

1. **Private backup** before rewrite: sibling `research-os-private` full clone + tags.
2. **History rewrite** (`git filter-repo`): removed `library/`, `topics/` (all live corpora), `*.sql` snapshots, local settings from all commits; replaced `lxinfei` module path strings.
3. **Working tree rebuild**: templates, synthetic demo topic, MIT packaging, release docs.
4. **Product framing**: multi-agent research loop (not a personal knowledge dump).

## Commit history note

Framework commits remain (refactor, skills, MCP, constitution). Hashes changed because of filter-repo. Personal corpus commits’ **file payloads** were stripped; messages may still *mention* old topics by name — content is gone.

## Residual risk

Playbooks document platform parameter names such as `xsec_token` (not secret values). Users must still avoid committing live tokens.
