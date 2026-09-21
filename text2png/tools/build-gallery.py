#!/usr/bin/env python3
"""text2png 全矩阵构建：生成 HTML → 用 scripts/screenshot.ts 截图 → 汇总画廊页。

用法（在仓库根或任意位置执行均可）：
  python3 tools/build-gallery.py all   --out /tmp/t2h-gallery      # 15 形式 × 9 主题 2x PNG + 画廊
  python3 tools/build-gallery.py light                             # 1x webp 轻量版 → <skill>/demo（随 skill 分发）
  python3 tools/build-gallery.py embed --out ~/Downloads/t2h-gallery.html --src /tmp/t2h-gallery

可选参数：
  --only sequence swimlane   只处理指定形式（局部重建，秒级）
  --dpr N                    截图倍率（默认 2，轻量版用 1）
  --format png|webp          图片格式（默认 png）
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _content as content  # noqa: E402
import _gallery as gallery  # noqa: E402
import _shots as shots  # noqa: E402

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
REPO_DIR = SKILL_DIR.parent
DEFAULT_OUT = pathlib.Path("/tmp/t2h-gallery")


def setup(out: pathlib.Path) -> pathlib.Path:
    content.ROOT = out
    content.HTML_DIR = out / "html"
    content.PNG_DIR = out / gallery.IMG_DIRNAME
    return out


def pick_charts(only):
    all_charts = [c for c, _ in content.CHARTS]
    if not only:
        return all_charts
    unknown = [c for c in only if c not in all_charts]
    if unknown:
        raise SystemExit(f"未知形式: {', '.join(unknown)}\n可选: {', '.join(all_charts)}")
    return [c for c in all_charts if c in only]


def write_html(charts_list):
    content.HTML_DIR.mkdir(parents=True, exist_ok=True)
    for chart_id in charts_list:
        for style_id in content.STYLES:
            path = content.HTML_DIR / f"{chart_id}__{style_id}.html"
            path.write_text(content.build_html(chart_id, style_id), encoding="utf-8")
    print(f"HTML  {len(charts_list) * len(content.STYLES)} 个 → {content.HTML_DIR}")


def shoot(charts_list, dpr, fmt, padding):
    ok, total, fails = shots.shoot(charts_list, list(content.STYLES), content.PNG_DIR,
                                   dpr=dpr, fmt=fmt, padding=padding)
    print(f"截图  {ok}/{total}（dpr={dpr}, {fmt}）→ {content.PNG_DIR}")
    for chart_id, style_id, err in fails[:5]:
        print(f"  失败 {chart_id}__{style_id} {err}")


def write_gallery(dest=None):
    dest = dest or (content.ROOT / "index.html")
    img_ext = "webp" if any(content.PNG_DIR.glob("*.webp")) else "png"
    path, mb = gallery.write(content.ROOT, dest, embed=False, img_ext=img_ext)
    print(f"画廊  {path}（{mb:.1f} MB，图片 {gallery.img_dir_size_mb(content.ROOT):.1f} MB）")


def main():
    ap = argparse.ArgumentParser(description="text2png 全矩阵构建")
    ap.add_argument("mode", choices=["all", "html", "shots", "gallery", "light", "embed"])
    ap.add_argument("--out", default=None, help="输出目录（embed 模式为目标 .html）")
    ap.add_argument("--src", default=None, help="embed 模式图片来源目录（默认 /tmp/t2h-gallery）")
    ap.add_argument("--only", nargs="*", default=None, help="只处理指定形式")
    ap.add_argument("--dpr", type=int, default=2)
    ap.add_argument("--format", default="png", choices=["png", "webp"])
    ap.add_argument("--padding", type=int, default=28)
    args = ap.parse_args()

    if args.mode == "embed":
        src = pathlib.Path(args.src).expanduser() if args.src else DEFAULT_OUT
        setup(src)
        dest = pathlib.Path(args.out).expanduser() if args.out else pathlib.Path.home() / "Downloads/t2h-gallery.html"
        img_ext = "webp" if any(content.PNG_DIR.glob("*.webp")) else "png"
        path, mb = gallery.write(src, dest, embed=True, img_ext=img_ext)
        print(f"单文件 {path}（{mb:.1f} MB，已内联 {len(gallery.charts) * len(gallery.styles)} 张 {img_ext}）")
        return

    if args.mode == "light":
        # 轻量演示随 skill 分发，放在 skill 内的 demo/，方便使用者先看全览再决定形式与主题
        out = pathlib.Path(args.out).expanduser() if args.out else SKILL_DIR / "demo"
        args.dpr, args.format = 1, "webp"
    else:
        out = pathlib.Path(args.out).expanduser() if args.out else DEFAULT_OUT

    out = out.resolve()
    setup(out)
    charts_list = pick_charts(args.only)

    if args.mode in ("all", "light"):
        content.prepare_dirs(clean_png=True)
    else:
        content.HTML_DIR.mkdir(parents=True, exist_ok=True)
        content.PNG_DIR.mkdir(parents=True, exist_ok=True)

    if args.mode in ("all", "light", "html"):
        write_html(charts_list)
    if args.mode in ("all", "light", "shots"):
        shoot(charts_list, args.dpr, args.format, args.padding)
    if args.mode in ("all", "light", "gallery"):
        write_gallery()


if __name__ == "__main__":
    main()
