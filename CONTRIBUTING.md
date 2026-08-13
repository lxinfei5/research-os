# Contributing

## Welcome

- Floor / protocol improvements with clear failure modes (silent empty slot, dual owner, semantic rewrite on fallback).
- Skill handbook clarity for the grow loop.
- `webbridge-mcp` reliability and tests (loopback bind must stay default).
- Docs and demo topics that stay **synthetic** (no private corpora).  
- New domain examples under `pillars/examples/` must include a user-surface skeleton; each first-screen line must say why it *is* the act (`pillars/examples/README.md`). Ship vs do-not-ship cards: `pillars/output/fixtures/`.

## Not welcome in PRs

- Scraped third-party full posts/media without rights.
- API keys, cookies, `xsec_token` values, personal quotas/P&L.
- Live investment holdings or target-price decision screens.

## Dev notes

```bash
# Go tool
cd tools/social_mcp/webbridge_mcp && go test ./...

# Public hygiene
./scripts/check-public.sh
```

## License

By contributing you agree contributions are MIT-licensed.
