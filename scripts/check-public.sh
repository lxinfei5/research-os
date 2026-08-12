#!/usr/bin/env bash
# Fail if tracked tree looks like a personal vault or secret dump.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0

echo "== secret-ish patterns in tracked files =="
if git grep -nIE 'xsec_token=[A-Za-z0-9_-]{10,}|sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*=\s*["\x27][^"\x27]{6,}' -- . \
  ':(exclude)docs/*' ':(exclude)CHANGELOG.md' ':(exclude)scripts/check-public.sh' 2>/dev/null; then
  echo "FAIL: possible live secrets"
  fail=1
else
  echo "ok"
fi

echo "== absolute home paths =="
if git grep -nE '/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/' -- . \
  ':(exclude)scripts/check-public.sh' 2>/dev/null; then
  echo "FAIL: absolute home path"
  fail=1
else
  echo "ok"
fi

echo "== forbidden personal corpus paths (tracked) =="
if git ls-files | grep -E '^(library/sources/.+\.json|topics/[^_].+/sources/|topics/[^_].+/cache/|topics/[^_].+/captures/)' \
  | grep -v 'topics/_templates/' | grep -v 'examples/' | grep -v 'demo_hello'; then
  echo "FAIL: live corpus paths tracked"
  fail=1
else
  echo "ok"
fi

echo "== license =="
test -f LICENSE || { echo "FAIL: no LICENSE"; fail=1; }

if [[ "$fail" -ne 0 ]]; then
  echo "check-public: FAILED"
  exit 1
fi
echo "check-public: PASSED"
