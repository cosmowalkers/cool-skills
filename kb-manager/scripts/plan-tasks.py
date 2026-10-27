#!/usr/bin/env python3
"""把人工确认后的候选共性转换为独立知识页任务。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_ACTIONS = {
    "create",
    "update",
    "delete",
    "move",
    "link_shared_page",
    "remove_repository_difference",
    "ignore",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", default="kb")
    args = parser.parse_args()
    data = json.loads(args.analysis.read_text())
    tasks = []
    for index, item in enumerate(data.get("candidates", []), 1):
        action = item.get("action")
        if action is None:
            if item.get("classification") != "common_candidate":
                continue
            action = "create"
        if action not in ALLOWED_ACTIONS or not item.get("approved", False):
            continue
        kind = (item.get("knowledge_types") or ["reference"])[0]
        slug = item.get("feature", f"task-{index:03d}")
        evidence = item.get("evidence", [])
        if evidence and isinstance(evidence[0], dict):
            evidence = [
                f"{entry.get('repository', '')}:{path}"
                for entry in evidence
                for path in entry.get("evidence", [])
            ]
        else:
            evidence = [str(path) for path in evidence]
        tasks.append({
            "id": f"{args.prefix}-{index:03d}",
            "action": action,
            "repository": item.get("repository", "shared"),
            "source_repositories": item.get("repositories", []),
            "type": kind,
            "target": item.get("target", f"common/{kind}/{slug}.md"),
            "evidence": evidence,
            "prompt": item.get(
                "prompt",
                "依据证据完成知识页变更，明确适用范围、例外、影响和验证方式",
            ),
            "depends_on": item.get("depends_on", []),
        })
    output = {"version": 1, "tasks": tasks}
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"已生成 {args.output}：{len(tasks)} 个已确认任务")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
