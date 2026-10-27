#!/usr/bin/env bash
set -euo pipefail

target="${1:-}"
if [[ -z "$target" ]]; then
  echo "用法: check-name.sh <path>" >&2
  exit 2
fi

if [[ ! -e "$target" ]]; then
  echo "路径不存在: $target" >&2
  exit 1
fi

invalid=0
while IFS= read -r -d '' path; do
  name="${path##*/}"
  [[ "$name" == "README.md" || "$name" == "log.md" ]] && continue
  [[ "$name" == _* ]] && continue
  [[ "$name" == *.md ]] || continue
  stem="${name%.md}"
  if [[ ! "$stem" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "文件名不符合 kebab-case: $path" >&2
    invalid=1
  fi
done < <(find "$target" -type f -print0)

exit "$invalid"
