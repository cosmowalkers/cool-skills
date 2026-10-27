#!/usr/bin/env python3
"""确定性采集仓库文件上下文，供 kb Discovery 使用。"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "dist", "build", "coverage",
    ".next", ".nuxt", ".turbo", ".cache", "vendor", "__pycache__",
}
GENERATED_FILES = {
    "_scan_context.json",
    "_discovery.json",
    "_discovery_review.md",
    "_tasks_export.json",
    "_cross_repo.json",
    "_repository_topology.json",
}
TEXT_SUFFIXES = {
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".py", ".go", ".java",
    ".kt", ".rs", ".rb", ".php", ".cs", ".css", ".scss", ".less", ".json",
    ".yaml", ".yml", ".toml", ".xml", ".md", ".mdx", ".sh", ".bash",
}
IMPORTANT_NAMES = {
    "package.json", "pnpm-workspace.yaml", "turbo.json", "vite.config.ts",
    "vite.config.js", "nuxt.config.ts", "nuxt.config.js", "tsconfig.json",
    "Dockerfile", "docker-compose.yml", "Makefile", "README.md",
}


def files_under(root: Path, include_docs: bool = False) -> list[Path]:
    result = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root)
        if path.name in GENERATED_FILES:
            continue
        if not include_docs and "docs" in relative.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in IMPORTANT_NAMES:
            result.append(path)
    return sorted(result)


def module_for(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.parts
    for marker in ("src", "app", "packages", "modules", "components", "pages", "server"):
        if marker in parts:
            index = parts.index(marker)
            if len(parts) > index + 1:
                return parts[index + 1]
    return parts[0] if len(parts) > 1 else "."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--max-bytes", type=int, default=120_000)
    parser.add_argument(
        "--include-docs",
        action="store_true",
        help="迁移模式下把旧 docs 纳入证据；普通 build/reconcile 默认排除",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"仓库目录不存在: {root}")

    files = []
    modules: dict[str, dict] = {}
    for path in files_under(root, include_docs=args.include_docs):
        rel = path.relative_to(root).as_posix()
        stat = path.stat()
        item = {
            "path": rel,
            "bytes": stat.st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "text_readable": stat.st_size <= args.max_bytes,
        }
        if item["text_readable"]:
            try:
                item["preview"] = path.read_text(errors="replace")[:4000]
            except OSError:
                item["text_readable"] = False
        files.append(item)
        module = module_for(root, path)
        modules.setdefault(module, {"id": module, "file_count": 0, "sample_paths": []})
        modules[module]["file_count"] += 1
        if len(modules[module]["sample_paths"]) < 12:
            modules[module]["sample_paths"].append(rel)

    output = {
        "version": 1,
        "repository": root.name,
        "root": ".",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {"file_count": len(files), "module_count": len(modules)},
        "modules": sorted(modules.values(), key=lambda item: item["id"]),
        "files": files,
    }
    target = args.output or root / "_scan_context.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"已生成 {target}：{len(files)} 个文件，{len(modules)} 个候选模块")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
