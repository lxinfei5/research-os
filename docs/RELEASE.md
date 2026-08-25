# Release

```bash
./scripts/check-public.sh
# optional: go test in tools/social_mcp/webbridge_mcp
git tag -a v0.4.0 -m "ResearchOS v0.4 — five-innovation research capability; lowest cognitive load to act"
git push origin main --tags
gh release create v0.4.0 --notes-file CHANGELOG.md
```
