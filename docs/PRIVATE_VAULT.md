# Private vault workflow

When this repository is public, keep **personal research** in a separate private clone/fork.

## Recommended layout

```
research-os/              # public framework (this repo)
research-os-private/      # private vault: full topics + library + history
```

A full pre-clean backup of the original personal tree was prepared as:

- sibling directory: `../research-os-private` (complete clone before history rewrite)
- tag name used at split time: `archive/personal-full-corpus-2026-08-12` (on the private clone)

## Day-to-day

1. Do research **in the private vault** (write `topics/`, `library/`).
2. Propose framework improvements as PRs against the **public** repo (rules/skills/tools only).
3. Optionally vendor public as a submodule or remote:

```bash
cd research-os-private
git remote add upstream git@github.com:<org>/research-os.git   # public
git remote add origin  git@github.com:<you>/research-os-private.git
```

## Never copy back to public

- Live topic sources/captures/cache
- CAS library full text
- Session reports with personal spend / accounts
- Cookies, tokens, `.env`
