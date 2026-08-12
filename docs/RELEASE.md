# Release

```bash
./scripts/check-public.sh
# optional: go test in tools/social_mcp/webbridge_mcp
git tag -a v0.2.0 -m "ResearchOS v0.2 — four-pillar research capability"
git push origin main --tags
gh release create v0.2.0 --notes-file CHANGELOG.md
```
