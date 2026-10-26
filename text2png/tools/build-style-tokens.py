#!/usr/bin/env python3
"""从 _content.py 的 STYLES/FONTS 导出 references/style-tokens.md（唯一真源，勿手改产物）。

用法：python3 tools/build-style-tokens.py
风格定义变更后重新运行即可同步文档。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _content import FONTS, STYLES  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "references" / "style-tokens.md"


def main() -> None:
    lines = [
        "# Style Tokens（自动生成）",
        "",
        f"> 由 `tools/build-style-tokens.py` 从 `tools/_content.py` 的 `STYLES` 导出，共 {len(STYLES)} 套风格。",
        "> **这是风格定义的唯一真源**：生成 HTML 时直接取对应风格的 `bg` / 字体 / `vars` / `css`，",
        "> 截图 `--bg` 传同一色值（或省略，让 screenshot.ts 自动读取 HTML 的 `:root{--bg}`）。",
        "",
        "## 速查表",
        "",
        "| Style | 名称 | bg | 标题字体 | 正文字体 | 数字字体 |",
        "|-------|------|----|----------|----------|----------|",
    ]
    for sid, s in STYLES.items():
        lines.append(
            f"| `{sid}` | {s['label']} | `{s['bg']}` | {s['head']} | {s['body']} | {s['num']} |"
        )
    lines += ["", "## 风格定义明细", ""]
    for sid, s in STYLES.items():
        lines += [
            f"### {sid} — {s['label']}",
            "",
            f"- **bg**: `{s['bg']}`",
            f"- **fonts**: head `{s['head']}` / body `{s['body']}` / num `{s['num']}`",
            f"- **Google Fonts**: `{FONTS.get(sid, '（无外链，使用本地字体栈）')}`",
            f"- **CSS vars**:",
            "",
            "```css",
            f":root {{ {s['vars']} }}",
            "```",
        ]
        if s.get("css"):
            lines += ["", "- **风格专属 CSS**:", "", "```css", s["css"], "```"]
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {OUT} ({len(STYLES)} styles)")


if __name__ == "__main__":
    main()
