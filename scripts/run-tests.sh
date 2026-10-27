#!/usr/bin/env bash
#
# run-tests.sh -- run the whole stackhidden.com suite with one command.
#
#   scripts/run-tests.sh
#
# The static module runs under the system python3 (it uses only the
# standard library). The browser modules run under the Playwright venv
# at /tmp/pwenv when it exists, and fall back to python3 with a warning
# otherwise. Tests load the site from the local files; no server, no
# build step, no network.
#
# The script prints one line per module and a final total, and exits
# non-zero if any module fails, so a pre-push check or CI job can gate
# on it.

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$ROOT/tests"
BROWSER_MODULES="test_theme test_palette test_cases test_carousel test_explorer test_layout test_motion"

if [ -x /tmp/pwenv/bin/python ]; then
  BROWSER_PY=/tmp/pwenv/bin/python
else
  BROWSER_PY=python3
  echo "note: /tmp/pwenv/bin/python not found; browser modules will run"
  echo "      under python3, which needs Playwright installed."
  echo
fi

passed=0
failed=0
ran_tests=0
failures=""

run_module() {
  label="$1"
  py="$2"
  module="$3"
  out="$(cd "$TESTS_DIR" && "$py" -m unittest "$module" 2>&1)"
  status=$?
  count="$(printf '%s\n' "$out" | sed -n 's/^Ran \([0-9][0-9]*\) test.*/\1/p' | head -1)"
  count="${count:-0}"
  ran_tests=$((ran_tests + count))
  if [ "$count" -eq 1 ]; then unit="test"; else unit="tests"; fi
  if [ "$status" -eq 0 ]; then
    printf 'PASS  %-14s %s %s\n' "$label" "$count" "$unit"
    passed=$((passed + 1))
  else
    printf 'FAIL  %-14s %s %s\n' "$label" "$count" "$unit"
    printf '%s\n' "$out" | tail -n 30
    failed=$((failed + 1))
    failures="$failures $label"
  fi
}

echo "stackhidden.com test suite"
echo "repo: $ROOT"
echo

run_module "static" python3 test_static
for module in $BROWSER_MODULES; do
  run_module "$module" "$BROWSER_PY" "$module"
done

echo
total=$((passed + failed))
if [ "$failed" -eq 0 ]; then
  echo "All $total modules passed ($ran_tests tests)."
  exit 0
fi
echo "$failed of $total modules failed ($ran_tests tests):$failures"
exit 1
