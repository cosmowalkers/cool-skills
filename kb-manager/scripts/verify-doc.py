#!/usr/bin/env python3
"""校验 docs 知识页的正文结构、目录一致性、索引收录和本地链接。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


TYPES = {"guide", "rules", "reference", "decisions", "gotchas"}


def parse_common_maps(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        name, separator, target = value.partition("=")
        if not separator or not name or not target:
            raise ValueError("--common-map 必须使用 NAME=PATH")
        path = Path(target).expanduser().resolve()
        result[name] = path if path.name == "docs" else path / "docs"
    return result


def remap_common_target(target: Path, common_maps: dict[str, Path]) -> Path:
    parts = target.parts
    for name, docs_root in common_maps.items():
        marker = ("submodules", name, "docs")
        for index in range(len(parts) - len(marker) + 1):
            if parts[index:index + len(marker)] == marker:
                suffix = Path(*parts[index + len(marker):])
                return (docs_root / suffix).resolve()
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--check-links", action="store_true")
    parser.add_argument(
        "--common-map",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="把主仓 submodules/NAME/docs 映射到 canonical common",
    )
    parser.add_argument(
        "--include-artifacts",
        action="store_true",
        help="校验 _discovery_review.md 等中间产物",
    )
    parser.add_argument(
        "--strict-associations",
        action="store_true",
        help="要求知识页存在 ## 关联 且至少包含一个 Markdown 链接",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"目录不存在: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    try:
        common_maps = parse_common_maps(args.common_map)
    except ValueError as exc:
        parser.error(str(exc))
    pages = sorted(
        p for p in root.rglob("*.md")
        if "node_modules" not in p.parts
        and p.name not in {"README.md", "log.md"}
        and (args.include_artifacts or not p.name.startswith("_"))
    )
    index_text = (root / "README.md").read_text() if (root / "README.md").exists() else ""
    index_links = {
        match.group(1)
        for match in re.finditer(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", index_text)
    }

    for page in pages:
        text = page.read_text()
        body = text
        is_artifact = page.name.startswith("_")
        if text.startswith("---\n"):
            errors.append(f"{page}: 禁止使用 YAML frontmatter")
        if not body.strip():
            errors.append(f"{page}: 正文为空")
        if not is_artifact and page.parent.name not in TYPES:
            errors.append(f"{page}: 页面必须位于 guide/rules/reference/decisions/gotchas 目录")
        if not is_artifact and re.search(
            r"(?:来源|source)\s*[:：]\s*(?:code-scan|扫描结果|跨仓扫描|skill-catalog)\b",
            body,
            re.IGNORECASE,
        ):
            errors.append(f"{page}: 验证来源不能使用扫描过程占位符")
        relative = page.relative_to(root).as_posix()
        if not is_artifact and relative not in index_links:
            errors.append(f"{page}: 未在 README.md 中找到精确索引链接")
        if args.strict_associations and not is_artifact:
            association = body.split("## 关联", 1)[1] if "## 关联" in body else ""
            if not association or not re.search(
                r"\]\([^)]+\.md(?:#[^)]+)?\)", association
            ):
                errors.append(f"{page}: 缺少有效的 ## 关联 链接")
        if args.check_links:
            for match in re.finditer(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", body):
                link = match.group(1)
                if urlparse(link).scheme:
                    continue
                target = remap_common_target(
                    (page.parent / link).resolve(),
                    common_maps,
                )
                if not target.exists():
                    errors.append(f"{page}: 链接不存在: {link}")

    if errors:
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"通过: {root}（{len(pages)} 个知识页面）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
