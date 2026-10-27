#!/usr/bin/env python3
"""根据代码变更和页面正文中的验证来源生成知识库变更影响计划。"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path

PAGE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".py", ".go",
                 ".java", ".kt", ".rs", ".rb", ".php", ".cs", ".css", ".scss",
                 ".less", ".json", ".yaml", ".yml", ".toml", ".xml", ".sh",
                 ".bash", ".md", ".mdx"}
STATUS_VALUES = {"A", "M", "D", "R", "C", "T", "U"}
PATH_EXTENSIONS = (
    "js|jsx|ts|tsx|vue|svelte|py|go|java|kt|rs|rb|php|cs|css|scss|less|json|"
    "yaml|yml|toml|xml|sh|bash"
)
PATH_TOKEN = re.compile(
    rf"(?<![\w./:-])(?:[A-Za-z0-9_.-]+:)?"
    rf"(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:{PATH_EXTENSIONS})"
    r"(?:/\*\*)?(?![\w./-])"
)
CODE_SPAN = re.compile(r"`([^`\n]+)`")
MARKDOWN_TARGET = re.compile(r"\]\(([^)#\s]+)")
NON_PATH_PREFIXES = ("http://", "https://", "mailto:")


def git_changes(repo: Path, revision: str) -> list[dict[str, str]]:
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-status", "--find-renames", revision],
        check=True,
        capture_output=True,
        text=True,
    )
    changes: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        code = fields[0][0]
        if code == "R" and len(fields) >= 3:
            changes.append({"status": "R", "path": fields[2], "old_path": fields[1]})
        else:
            changes.append({"status": code, "path": fields[1]})
    return changes


def explicit_changes(values: list[str]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for value in values:
        if ":" in value and value.split(":", 1)[0] in STATUS_VALUES:
            status, path = value.split(":", 1)
            changes.append({"status": status, "path": path})
        else:
            changes.append({"status": "M", "path": value})
    return changes


def normalize(value: str) -> str:
    return value.strip().strip("`'\"").removeprefix("./")


def parse_evidence_maps(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        name, separator, target = value.partition("=")
        if not separator or not name or not target:
            raise ValueError("--evidence-map 必须使用 NAME=PATH")
        result[name] = Path(target).expanduser().resolve()
    return result


def local_evidence_token(token: str, repo: Path,
                         evidence_maps: dict[str, Path]) -> str | None:
    """把当前仓库证据转换为可匹配 git 变更的相对路径。"""
    token = normalize(token)
    prefix, separator, relative = token.partition(":")
    if separator:
        return relative if prefix == repo.name else None
    slash_prefix, slash, slash_relative = token.partition("/")
    if slash and slash_prefix == repo.name:
        return slash_relative
    if slash and slash_prefix in evidence_maps:
        return None
    return token


def evidence_path(token: str, repo: Path,
                  evidence_maps: dict[str, Path]) -> Path | None:
    token = normalize(token)
    prefix, separator, relative = token.partition(":")
    if separator:
        if prefix == repo.name:
            return repo / relative
        mapped_root = evidence_maps.get(prefix)
        return mapped_root / relative if mapped_root else None
    slash_prefix, slash, slash_relative = token.partition("/")
    if slash and slash_prefix == repo.name:
        return repo / slash_relative
    if slash and slash_prefix in evidence_maps:
        return evidence_maps[slash_prefix] / slash_relative
    return repo / token


def matches(token: str, path: str) -> bool:
    token = normalize(token)
    path = normalize(path)
    if token.startswith("http://") or token.startswith("https://"):
        return False
    if token.endswith("/**"):
        prefix = token[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return (
        fnmatch.fnmatch(path, token)
        or path == token
        or path.startswith(token.rstrip("/") + "/")
        or token in path
    )


def evidence_for(page: Path) -> list[str]:
    """从正文提取代码路径；页面链接只用于追踪代码文件，不作为证据本身。"""
    source = page.read_text(errors="replace")
    evidence = set(PATH_TOKEN.findall(source))
    for match in CODE_SPAN.findall(source):
        evidence.update(PATH_TOKEN.findall(match))
    for target in MARKDOWN_TARGET.findall(source):
        if target.startswith(NON_PATH_PREFIXES):
            continue
        evidence.update(PATH_TOKEN.findall(target))
    return sorted(evidence)


def page_files(docs: Path) -> list[Path]:
    return sorted(
        page for page in docs.rglob("*.md")
        if page.name not in {"README.md", "log.md"} and not page.name.startswith("_")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--docs", required=True, type=Path)
    parser.add_argument("--diff", help="git diff revision, 例如 HEAD~1..HEAD")
    parser.add_argument("--changed", action="append", default=[],
                        help="变更文件，可写 STATUS:path；可重复")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--evidence-map",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="为跨仓 evidence 提供仓库根目录映射，可重复传入",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()
    docs = args.docs.resolve()
    if not repo.is_dir() or not docs.is_dir():
        parser.error("--repo 和 --docs 必须是目录")
    if not args.diff and not args.changed:
        parser.error("必须提供 --diff 或至少一个 --changed")
    try:
        evidence_maps = parse_evidence_maps(args.evidence_map)
    except ValueError as exc:
        parser.error(str(exc))

    changes = git_changes(repo, args.diff) if args.diff else explicit_changes(args.changed)
    pages = []
    for page in page_files(docs):
        evidence = evidence_for(page)
        pages.append({
            "page": page.relative_to(docs).as_posix(),
            "evidence": evidence,
        })

    affected: list[dict] = []
    matched_paths: set[str] = set()
    deleted = {item["path"] for item in changes if item["status"] == "D"}
    for page in pages:
        hits = []
        for change in changes:
            candidates = [change["path"]]
            if change.get("old_path"):
                candidates.append(change["old_path"])
            if any(
                any(
                    local_token is not None and matches(local_token, path)
                    for local_token in (
                        local_evidence_token(token, repo, evidence_maps)
                        for token in page["evidence"]
                    )
                )
                for path in candidates
            ):
                hits.append(change)
                matched_paths.update(candidates)
        if not hits:
            continue
        action = "update"
        if page["evidence"] and all(
            any(
                local_token is not None and matches(local_token, deleted_path)
                for local_token in (
                    local_evidence_token(token, repo, evidence_maps)
                    for token in page["evidence"]
                )
                for deleted_path in deleted
            )
            for token in page["evidence"]
        ):
            action = "delete"
        affected.append({
            "action": action,
            "page": page["page"],
            "changed_files": hits,
            "evidence": page["evidence"],
            "requires_review": action == "delete",
        })

    stale = []
    for page in pages:
        missing = []
        for token in page["evidence"]:
            if any(char in token for char in "*?["):
                continue
            path = evidence_path(token, repo, evidence_maps)
            if path is not None and not path.exists():
                missing.append(token)
        if missing:
            stale.append({"page": page["page"], "missing_evidence": missing,
                          "action": "stale_evidence"})

    unmapped = [
        change for change in changes
        if change["path"] not in matched_paths
        and not (change.get("old_path") and change["old_path"] in matched_paths)
    ]
    output = {
        "version": 1,
        "repository": repo.name,
        "docs": docs.relative_to(repo).as_posix()
        if docs.is_relative_to(repo) else docs.name,
        "diff": args.diff or None,
        "changed_files": changes,
        "affected_pages": affected,
        "stale_pages": stale,
        "unmapped_changes": unmapped,
        "summary": {
            "changed": len(changes),
            "affected": len(affected),
            "stale": len(stale),
            "unmapped": len(unmapped),
        },
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(
        f"已生成 {args.output}：{len(changes)} 个变更，"
        f"{len(affected)} 个受影响页面，{len(unmapped)} 个未映射变更"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
