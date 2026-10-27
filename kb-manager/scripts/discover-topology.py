#!/usr/bin/env python3
"""扫描工作区中的 Git 仓库和 .gitmodules，输出仓库关系图。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SECTION = re.compile(r'^\[submodule "([^"]+)"\]$')
KEY_VALUE = re.compile(r"^\s*(path|url|branch)\s*=\s*(.+?)\s*$")


def git_repositories(root: Path) -> list[Path]:
    return sorted({
        marker.parent for marker in root.rglob(".git")
        if marker.is_dir() or marker.is_file()
    })


def parse_gitmodules(filename: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in filename.read_text(errors="replace").splitlines():
        section = SECTION.match(line.strip())
        if section:
            if current:
                items.append(current)
            current = {"name": section.group(1)}
            continue
        if current:
            pair = KEY_VALUE.match(line)
            if pair:
                current[pair.group(1)] = pair.group(2).strip()
    if current:
        items.append(current)
    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    repositories = git_repositories(root)
    edges = []
    referenced_paths: set[Path] = set()
    for repository in repositories:
        filename = repository / ".gitmodules"
        if not filename.exists():
            continue
        for item in parse_gitmodules(filename):
            if not item.get("path"):
                continue
            child = (repository / item["path"]).resolve()
            referenced_paths.add(child)
            edges.append({
                "parent": repository.relative_to(root).as_posix()
                if repository != root else ".",
                "child": child.relative_to(root).as_posix()
                if child.is_relative_to(root) else child.name,
                "child_name": child.name,
                "name": item.get("name", child.name),
                "url": item.get("url", ""),
                "branch": item.get("branch", ""),
            })

    repo_rows = []
    for repository in repositories:
        repository_id = repository.relative_to(root).as_posix() if repository != root else "."
        children = [edge for edge in edges if edge["parent"] == repository_id]
        incoming = [edge for edge in edges if edge["child"] == repository_id]
        common = [edge for edge in children if edge["child_name"] in {"aui-common", "su-common"}]
        repo_rows.append({
            "path": repository_id,
            "name": repository.name,
            "has_gitmodules": bool(children),
            "parent_count": len(incoming),
            "child_count": len(children),
            "common_dependencies": sorted({edge["child_name"] for edge in common}),
            "classification": (
                "main-with-common" if common else
                "main-with-submodules" if children else
                "standalone" if not incoming else
                "submodule"
            ),
        })

    result = {
        "version": 1,
        "root": ".",
        "repositories": repo_rows,
        "edges": edges,
        "independent_repositories": [
            row["path"] for row in repo_rows
            if row["classification"] == "standalone"
        ],
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"已生成 {args.output}：{len(repositories)} 个仓库，{len(edges)} 条子仓引用")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
