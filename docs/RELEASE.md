# Release

```bash
./scripts/check-public.sh
# fenced webbridge tests live in the sibling / user-level runtime, not this repo
# (cd ~/.webbridge-mcp && go test ./...)
git tag -a v0.4.0 -m "ResearchOS v0.4 — five-innovation research capability; lowest cognitive load to act"
git push origin main --tags
gh release create v0.4.0 --notes-file CHANGELOG.md
```
