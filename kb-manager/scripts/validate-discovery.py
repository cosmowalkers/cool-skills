#!/usr/bin/env python3
"""校验 AI 生成的 _discovery.json 是否具备可审阅和可追溯结构。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CONFIDENCES = {"high", "medium", "low"}
TYPES = {"guide", "rules", "reference", "decisions", "gotchas"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("discovery", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.discovery.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"读取失败: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    if data.get("version") != 1:
        errors.append("version 必须为 1")
    if not data.get("repository"):
        errors.append("缺少 repository")
    if isinstance(data.get("root"), str) and Path(data["root"]).is_absolute():
        errors.append("root 不得使用本机绝对路径")
    modules = data.get("modules", [])
    features = data.get("features", [])
    if not isinstance(modules, list):
        errors.append("modules 必须是数组")
        modules = []
    if not isinstance(features, list):
        errors.append("features 必须是数组")
        features = []
    module_ids = [item.get("id") for item in modules]
    feature_ids = [item.get("id") for item in features]
    if len(module_ids) != len(set(module_ids)):
        errors.append("modules.id 必须唯一")
    if len(feature_ids) != len(set(feature_ids)):
        errors.append("features.id 必须唯一")
    module_set = set(module_ids)
    for kind, items in (("modules", modules), ("features", features)):
        for index, item in enumerate(items):
            prefix = f"{kind}[{index}]"
            if not item.get("id") or not item.get("name"):
                errors.append(f"{prefix} 缺少 id 或 name")
            if not item.get("evidence"):
                errors.append(f"{prefix} 缺少 evidence")
            elif any(
                not isinstance(path, str) or Path(path).is_absolute()
                for path in item.get("evidence", [])
            ):
                errors.append(f"{prefix}.evidence 必须是仓库相对路径")
            if item.get("confidence") not in CONFIDENCES:
                errors.append(f"{prefix}.confidence 无效")
            if kind == "features" and item.get("module") not in module_set:
                errors.append(f"{prefix}.module 未引用已存在模块")
            for candidate in item.get("knowledge_candidates", []):
                if candidate.get("type") not in TYPES:
                    errors.append(f"{prefix} 候选知识 type 无效")
                if not candidate.get("target") or not candidate.get("reason"):
                    errors.append(f"{prefix} 候选知识缺少 target 或 reason")
    if errors:
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"通过: {args.discovery}（{len(modules)} 个模块，{len(features)} 个功能）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
