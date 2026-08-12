# Security

## Report

If you find a way for webbridge-mcp or docs to encourage non-loopback binds, secret leakage into git, or forged “clean” existence checks, open a private security report.

## Hard rules

1. **webbridge-mcp** re-exposes a real logged-in browser. Default bind is loopback only. Do not change defaults to `0.0.0.0` in examples.
2. Never commit `.env`, cookies, or signed CDN tokens.
3. Captured social content is the user’s responsibility under platform ToS and copyright law.
