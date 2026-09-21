#!/usr/bin/env python3
"""批量调用 scripts/screenshot.ts 截图（并发 4），供 build-gallery.py 使用。"""
import concurrent.futures as cf
import pathlib
import subprocess

import _content as content

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = SKILL_DIR / "scripts" / "screenshot.ts"
BUN = str(pathlib.Path.home() / ".bun/bin/bun")

# 横向流程图用 960 宽，其余 860（与 SKILL.md 的宽度约定一致）
WIDE_CHARTS = {"flowchart"}


def _shot(job):
    chart_id, style_id, out_dir, dpr, fmt, padding = job
    ext = "webp" if fmt == "webp" else "png"
    out = out_dir / f"{chart_id}__{style_id}.{ext}"
    cmd = [
        BUN, str(SCRIPT),
        "--html", str(content.HTML_DIR / f"{chart_id}__{style_id}.html"),
        "--out", str(out),
        "--bg", content.STYLES[style_id]["bg"],
        "--width", "960" if chart_id in WIDE_CHARTS else "860",
        "--padding", str(padding), "--dpr", str(dpr), "--format", ext,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SKILL_DIR))
    ok = out.exists() and out.stat().st_size > 500
    return chart_id, style_id, ok, (r.stderr or "").strip()[-120:]


def shoot(charts, styles, out_dir, dpr=2, fmt="png", padding=28, workers=4):
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(c, s, out_dir, dpr, fmt, padding) for c in charts for s in styles]
    fails = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for chart_id, style_id, ok, err in ex.map(_shot, jobs):
            if not ok:
                fails.append((chart_id, style_id, err))
    return len(jobs) - len(fails), len(jobs), fails
