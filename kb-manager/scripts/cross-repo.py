#!/usr/bin/env python3
"""按功能 id 对比多个 Discovery，输出候选共性和仓库差异。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", action="append", required=True,
                        metavar="REPO=PATH")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repos: dict[str, dict] = {}
    for value in args.discovery:
        name, separator, filename = value.partition("=")
        if not separator:
            parser.error("--discovery 必须使用 REPO=PATH")
        if name in repos:
            parser.error(f"重复的仓库标识: {name}")
        data = json.loads(Path(filename).read_text())
        repos[name] = data

    by_feature: dict[str, list[dict]] = {}
    for repo, data in repos.items():
        for feature in data.get("features", []):
            by_feature.setdefault(feature.get("id", ""), []).append({
                "repository": repo,
                "name": feature.get("name"),
                "module": feature.get("module"),
                "evidence": feature.get("evidence", []),
                "candidates": feature.get("knowledge_candidates", []),
            })

    result = {"version": 1, "repositories": sorted(repos), "candidates": []}
    for feature_id, evidence in sorted(by_feature.items()):
        if not feature_id:
            continue
        repositories = sorted(item["repository"] for item in evidence)
        kinds = sorted({candidate.get("type") for item in evidence
                        for candidate in item["candidates"] if candidate.get("type")})
        if len(evidence) >= 2 and kinds:
            classification = "common_candidate"
        elif len(evidence) >= 2:
            classification = "similar_but_different"
        else:
            classification = "repository_only"
        result["candidates"].append({
            "feature": feature_id,
            "classification": classification,
            "repositories": repositories,
            "match_reason": (
                "多个 Discovery 使用相同 feature.id；仍需人工核对名称、模块和证据"
            ),
            "knowledge_types": kinds,
            "evidence": evidence,
            "review_required": True,
        })
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"已生成 {args.output}：{len(result['candidates'])} 条跨仓候选")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
