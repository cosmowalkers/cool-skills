---
name: text2png
description: 将文字描述转化为有设计感的 HTML 可视化图表并自动截图输出 PNG，支持 15 种图表类型（流程、时序、泳道、对比、时间线、架构、数据看板、甘特图、组织、漏斗、思维导图、矩阵、看板、清单、金句）和 18 种视觉风格。两大触发场景看语义意图：① 生成图表——"画个图/做个图/出张图/可视化一下"或直接点名图表类型（流程图、时序图、泳道图、对比表、数据看板、思维导图等）；② 浏览预览——仅当表述明确指向本技能的 demo/风格目录时才触发，如"查看画图demo/打开text2png的demo/看看图表demo/demo里有什么风格/有哪些图表类型"；脱离上下文的泛化说法（单独的"查看demo/打开demo/看看效果/预览"等，未提及画图、图表、text2png、风格）不触发本技能，防止误触。注意：本技能只产出结构化图表/信息图，不处理照片、插画、艺术创作等创意位图。
metadata:
  short-description: 文字转结构化信息图并导出 PNG，含 demo 预览挑选
---

# text2png — 文字描述 → HTML 图表 → PNG 截图

将任意文字描述转化为有设计感的 HTML 可视化图表，自动截图输出 PNG。

## Usage

```bash
/text2png 帮我画一个 CI/CD 流程图
/text2png 对比 Redis 和 Memcached
/text2png  # 然后粘贴内容
```

## Options

**生成选项**（由你决定怎么写 HTML，不是传给脚本的参数）：

| Option | Values |
|--------|--------|
| `--style` | warm (default), editorial, macaron, brutalist, ocean, paper, art-nouveau, swiss, psychedelic, flat, glass, cyberpunk, midnight, dracula, neo-chinese, terminal, cosmic, industrial |
| `--chart` | auto (default), sequence, swimlane, flowchart, comparison, timeline, architecture, dashboard, gantt, org-chart, funnel, mind-map, matrix, kanban, checklist, quote-card |
| `--output` | 输出目录路径（默认当前目录） |

Style × Chart 可自由组合。风格只改配色/字体/质感，不改布局。

**脚本参数**（`scripts/screenshot.ts` 真正接受的参数，传其它参数会直接报错）：

| Arg | 说明 |
|-----|------|
| `--html <path>` | 输入 HTML（必填） |
| `--out <path>` | 输出图片（必填） |
| `--bg <color>` | 留白区背景色（可选：缺省自动读 HTML 的 `:root{--bg}`，读不到回退 `#ffffff`） |
| `--width <px>` | 视口宽度（默认 860；横向流程图可用 960） |
| `--padding <px>` | 四周留白（默认 32） |
| `--dpr <1-4>` | 截图倍率（默认 4） |
| `--format png\|webp` | 输出格式（默认 png） |

## Script Directory

**Important**: All scripts are located in the `scripts/` subdirectory of this skill.

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/<script-name>.ts`
3. Replace all `${SKILL_DIR}` in this document with the actual path

**Script Reference**:
| Script | Purpose |
|--------|---------|
| `scripts/screenshot.ts` | HTML → PNG 截图（puppeteer-core + 系统 Chrome，无需 Playwright） |

---

## Workflow

### Step 1: Collect Information

If the user hasn't provided the following, **ask these two questions in one go**（用当前环境可用的提问方式；没有专门的提问工具就直接在回复里问）:

**Question 1 — Style** (skip if user already specified):
```
风格偏好？18 套可选：
☀️ 亮色
  warm — 暖橙报告（默认）
  editorial — 杂志排版，冷白底 + 红黑高对比
  macaron — 马卡龙甜品，圆润粉彩
  brutalist — 新粗野主义，粗黑边框撞色
  ocean — 海洋微风，淡蓝清爽
  paper — 手绘涂鸦，歪斜卡片手写风
  art-nouveau — 新艺术运动，鼠尾草绿曲线
  swiss — 瑞士国际，极简格栅黑白
  psychedelic — 迷幻风格，渐变彩虹
  flat — 扁平设计，纯色块
  glass — 玻璃拟态，亮色毛玻璃

🌙 暗色
  cyberpunk — 赛博朋克，霓虹扫描线
  midnight — 午夜蓝调，蓝黑 + 金色
  dracula — 德古拉暗紫，荧光粉绿
  neo-chinese — 新中式，朱砂赤金黛蓝
  terminal — 终端黑客，CRT 绿字
  cosmic — 深空星云，太空紫蓝
  industrial — 工业金属，铁灰 + 橙色警示
（不确定的话我根据内容推荐）
```

**Question 2 — Output path** (skip if user already specified):
```
截图保存到哪？（直接回车默认当前目录）
```

If user content is clear enough and no style/path preference given, use inferred values and proceed directly.

### Step 2: Analyze Content & Select Chart Type

1. **Identify chart type** using `references/chart-types.md` auto-selection matrix
2. **Extract structured content** from user description:
   - Nodes, steps, metrics, or entities
   - Core description for each (refine to 1-2 lines)
   - Highlight priorities
3. **Enrich content**: When user only provides skeleton info, proactively add details to make the chart complete and professional
4. **Decide tagline/banner**: Based on content richness — if content has a clear "intro → conclusion" structure, use both (with different content); if there's only one core message, use only one. Never repeat the same text in tagline and banner.

**Reference**: `references/chart-types.md`

### Form vs Style: who decides what

Split the two decisions — they have different owners:

- **Form is inferred by you.** The user describes content, not chart types; most people cannot name `swimlane` or `sequence`. Infer the form from their content, state your choice in one short line ("我按时序图 + midnight 主题画，因为…"), and only ask back when two forms are genuinely plausible.
- **Style is the user's taste.** When the request doesn't imply one, don't silently lock in the first style you thought of. Either propose 2-3 candidate combos, or show the catalogue (below) and let them pick.

### Showing the catalogue (the bundled demo)

`demo/index.html` is the full 15 forms × 18 styles matrix (270 previews, filterable by form or style, click any image to zoom). Open it when the user asks what styles/forms exist, wants to pick a look, or when you're unsure about their taste:

 **Auto-open rule:** Only when the user's request explicitly points at this skill's demo or style catalogue — e.g. `查看画图demo`、`打开text2png的demo`、`看看图表demo`、`demo里有什么风格`、`有哪些图表类型`，or the session context is already clearly about text2png chart generation — **directly execute** `open "${SKILL_DIR}/demo/index.html"` (or `xdg-open` on Linux) without asking for confirmation. A generic `查看demo`/`打开demo`/`看看效果` with no drawing/chart/text2png/style context is NOT a trigger: it most likely refers to something else in the user's project — don't open this demo for it.

```bash
open "${SKILL_DIR}/demo/index.html"        # macOS
xdg-open "${SKILL_DIR}/demo/index.html"    # Linux
```

Rules that keep this helpful instead of annoying:

1. **On demand, not by default.** Don't launch a browser for every request — only when they ask, or when you're genuinely uncertain about the style.
2. **用户明确指向画图 demo 时自动打开。** 只有带指向性的表述（「查看画图demo」「打开text2png的demo」「看看图表demo/风格」，或当前会话上下文明确在做 text2png 图表）才算显式请求——直接执行 `open` 命令，然后告诉用户 demo 已打开。无上下文的泛化「查看demo/打开demo」不适用本条，不要据此打开 demo，以免误触。
3. **Always pair it with text.** Say in one line what you opened, and list the 18 styles with a 3-5 word trait each (e.g. `warm` 暖色报告 / `midnight` 午夜蓝调 / `editorial` 杂志排版). Remote shells and headless environments have no browser — the flow must still work.
4. **Prefer 2-3 candidates over the full menu.** The 270-grid answers "what exists", not "what should I use". Recommend first, expand only if they want to browse.
5. **Anchor the style.** Once a style is chosen (by the user or by your recommendation), keep it for the rest of the session/document so a set of charts looks consistent — switch only when asked.
6. **Never block on it.** If they don't care about style, pick the recommended one for that form (see the auto-selection matrix) and move on.

**Each card also has a 「复制 prompt」 button** (no server involved — it only copies text) that yields a ready-to-paste line such as `画成时序图（sequence），主题用 warm（暖色报告）：<把内容写在这里>`. When you open the demo, tell the user they can browse, hit that button on whatever they like, and paste it back with their content.

### Step 3: Generate HTML

Based on confirmed style + chart type + structured content, generate complete HTML.

**Design process**:
1. Read `references/design-philosophy.md` for aesthetic principles
2. Read `references/style-tokens.md` for the chosen style's bg / fonts / CSS vars / 专属 CSS（由 `tools/_content.py` 的 STYLES 自动生成，风格定义唯一真源）
3. Read `references/charts/<chart-type>.md` for layout rules and HTML structure
4. Generate HTML with all CSS inlined；`:root` 必须定义 `--bg`（取 style-tokens 的 bg 值，截图脚本靠它自动匹配留白底色）

**First Principle — Compact, Symmetric, Full**:
- **Compact**: Use minimum spacing that maintains readability. When 8px works, don't use 12px.
- **Symmetric**: All cards in a row equal width (`flex:1`). No unequal column splits unless content semantics demand it.
- **Full**: Every area carries content. If content is sparse, proactively enrich (add descriptions, stats, summary banners).
- Style does NOT change layout — styles only control colors, fonts, textures, effects.

**Spacing targets** (prefer the lower end):
- body padding: 20-24px (max 28px)
- Card gap: 8px (max 12px)
- Card internal padding: 12-14px (max 18px)
- Arrow/connector height: 20-24px (max 28px)
- Title → content: 10-12px (max 14px)

**Width**: Fixed at 860px (portrait) or 960px (landscape/horizontal charts).
**Visual coherence**: Uniform border-radius, font sizes follow hierarchy, colors restrained (≤ 3-4 primary colors).

**Output filename**: `<content-keyword>-<timestamp>.html`, saved to user-specified directory.

**Reference**: `references/design-philosophy.md`, `references/style-tokens.md`, `references/charts/*.md`

### Step 4: Screenshot

HTML 生成后，运行截图脚本（首次检查依赖是否已安装）：

```bash
[ -d "${SKILL_DIR}/node_modules" ] || (cd "${SKILL_DIR}" && npm install)
```

```bash
bun "${SKILL_DIR}/scripts/screenshot.ts" \
  --html <html_path> \
  --out <output_dir>/<filename>.png \
  --width 860 \
  --padding 32 \
  --dpr 4 \
  --format png
```

**工作原理**（脚本内部两阶段）：
1. **测量**：用 puppeteer-core 连接系统 Chrome，在 4000px 高 viewport 中渲染 HTML，测量 `.wrap` 元素的实际尺寸
2. **截图**：调整 viewport 到精确高度，用 `clip` 按内容 + padding 精确裁切，输出 4x 印刷级清晰度 PNG

**依赖**：
- `puppeteer-core`（npm install 自动安装，会带若干传递依赖）
- 系统已安装的 Google Chrome（Mac/Linux/Windows 开发者基本都有）
- HTML 里若用 Google Fonts 外链需要能访问外网；内网/离线时字体会静默回退，中文排版会变，建议关键场景改本地字体
- 无需 ImageMagick，无需 Playwright，无需额外下载浏览器

**默认 padding**：32px 四周均匀留白。

**Background color**：不需要手动传 `--bg` —— 脚本自动读取 HTML `:root{--bg}` 作为留白底色（生成 HTML 时务必写入该变量，值见 `references/style-tokens.md` 的 bg 列）。仅当需要覆盖自动值时才传 `--bg <color>`。


For horizontal flowcharts (≤ 7 steps, short descriptions), use `--width 960`.

**Completion output**:
```
Done!
   HTML: <path>.html
   PNG:  <path>.png
```

---

## Auto Selection Matrix

| Content Signals | Chart Type | Style |
|-----------------|------------|-------|
| 步骤、操作、流程、工作流 | flowchart | warm |
| 对比、PK、vs、优劣 | comparison | swiss |
| 时间、历史、里程碑、路线图 | timeline | editorial |
| 系统、服务、架构、组件 | architecture | midnight |
| 数字、指标、统计、报表 | dashboard | glass |
| 计划、排期、进度、甘特 | gantt | warm |
| 团队、汇报、层级、组织 | org-chart | swiss |
| 转化、漏斗、筛选、销售 | funnel | dracula |
| 思维导图、脑图、发散、分支 | mind-map | paper |
| 矩阵、象限、SWOT、优先级 | matrix | swiss |
| 看板、状态、待办、进行中 | kanban | glass |
| 清单、checklist、打勾、核查 | checklist | warm |
| 金句、引用、名言、摘录 | quote-card | editorial |
| 时序、调用链、请求响应、接口交互、回调 | sequence | midnight |
| 泳道、跨角色、责任分工、交接、谁负责 | swimlane | ocean |

When unable to determine chart type, default to **flowchart**.
When unable to determine style, default to **warm**.

**Reference**: `references/chart-types.md`

---

## Style Overview

18 套风格的色调与视觉要点见上文 Step 1 的风格菜单（正文只保留那一份）；每套风格的 bg / 字体 / CSS vars / 专属 CSS 见 `references/style-tokens.md`。

**All styles share the same layout principle**: compact, symmetric, full. Style only controls visual appearance (colors, fonts, textures, effects).

**Reference**: `references/style-tokens.md`

---

## Chart Types Overview

15 种图表类型的适用场景、关键布局、选择决策树与风格兼容表，统一维护在 `references/chart-types.md`（Step 2 必读），此处不重复。

**Reference**: `references/charts/*.md`

---

## Notes

- User descriptions can be rough — you refine them; don't dump raw text into the chart
- **Proactively enrich content**: Add details like node descriptions, scenario notes, summary banners to make charts look complete and professional
- If content is dense, group/merge items to maintain readability
- Each chart should have a distinct visual identity — no two charts should look the same
- **Font rule**: Never use Inter, Roboto, Arial, or system default fonts. Each style has its own font stack.

---

## Extension Support

Custom styles and configurations via EXTEND.md.

**Check paths** (priority order):
1. `.text2png/EXTEND.md` (project)
2. `~/.text2png/EXTEND.md` (user)

If found, load before Step 1. Extension content overrides defaults.

---

## References

Detailed templates and guidelines in `references/` directory:
- `design-philosophy.md` — Aesthetic principles and design rules
- `chart-types.md` — Chart type selection framework
- `style-tokens.md` — 18 套风格的 token 速查（bg / fonts / CSS vars / 专属 CSS），由 `tools/build-style-tokens.py` 从 `tools/_content.py` 自动生成
- `charts/` — Detailed chart type layouts (HTML structure, CSS patterns)

Preview & tooling:
- `demo/index.html` — 15 forms × 18 styles full-matrix preview (270 张, filterable, click to zoom); open on demand, not for every request
- `tools/build-gallery.py` — regenerate the demo / any matrix (`all` / `light` / `embed` / `--only`)
- `tools/build-style-tokens.py` — 修改 `_content.py` 的 STYLES 后重新生成 `references/style-tokens.md`
