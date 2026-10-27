#!/usr/bin/env bash
set -euo pipefail

root="${1:-}"
shift || true
if [[ -z "$root" || "$#" -eq 0 ]]; then
  echo "用法: find-existing.sh <docs-root> <keyword> [keyword...]" >&2
  exit 2
fi

[[ -d "$root" ]] || { echo "目录不存在: $root" >&2; exit 1; }

pattern="$*"
rg -l -i --glob '*.md' --glob '!node_modules/**' "$pattern" "$root" 2>/dev/null | sort -u || true
