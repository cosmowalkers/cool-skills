---
name: text2png
description: 将文字描述转化为有设计感的 HTML 可视化图表并自动截图输出 PNG。支持 15 种图表类型（时序图、泳道图、流程图、对比表、时间线、架构拓扑、数据看板、甘特图、组织架构、漏斗图、思维导图、矩阵图、看板、清单卡、金句卡）和 9 种视觉风格（warm、dark、minimal、editorial、neon、paper、glass、corporate、retro）。当用户想要把文字内容变成图表、可视化展示任何结构化信息时，都应该使用此 skill。典型触发场景包括但不限于：画图、可视化、出个图、做成图、画张图、画个时序图、泳道图、画个流程图、对比一下、帮我做个架构图、数据看板、甘特图、组织架构图、转化漏斗、思维导图、优先级矩阵、看板、清单、金句卡、text2png、生成报告图。
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
| `--style` | warm (default), dark, minimal, editorial, neon, paper, glass, corporate, retro |
| `--chart` | auto (default), sequence, swimlane, flowchart, comparison, timeline, architecture, dashboard, gantt, org-chart, funnel, mind-map, matrix, kanban, checklist, quote-card |
| `--output` | 输出目录路径（默认当前目录） |

Style x Chart 可自由组合。风格只改配色/字体/质感，不改布局。

**脚本参数**（`scripts/screenshot.ts` 真正接受的参数，传其它参数会直接报错）：

| Arg | 说明 |
|-----|------|
| `--html <path>` | 输入 HTML（必填） |
| `--out <path>` | 输出图片（必填） |
| `--bg <color>` | 留白区背景色（默认 `#ffffff`，按 style 的 bg 传） |
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
风格偏好？
1. warm — 暖色系，米白背景，彩色边框，适合报告/流程 (Recommended)
2. dark — 深色科技感，适合架构/技术方案
3. minimal — 极简黑白，适合向领导汇报
4. editorial — 杂志排版风，大号衬线字体，适合内容展示
5. neon — 赛博霓虹，适合技术分享/演讲配图
6. paper — 手绘纸质感，适合教学/说明
7. glass — 玻璃拟态，适合现代产品展示
8. corporate — 商务正式，深蓝主色，适合客户方案/汇报
9. retro — 复古像素，CRT 扫描线，适合技术社区/Side Project
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

- **Form is inferred by you.** The user describes content, not chart types; most people cannot name `swimlane` or `sequence`. Infer the form from their content, state your choice in one short line ("我按时序图 + dark 主题画，因为…"), and only ask back when two forms are genuinely plausible.
- **Style is the user's taste.** When the request doesn't imply one, don't silently lock in the first style you thought of. Either propose 2-3 candidate combos, or show the catalogue (below) and let them pick.

### Showing the catalogue (the bundled demo)

`demo/index.html` is the full 15 forms × 9 styles matrix (135 previews, filterable by form or style, click any image to zoom). Open it when the user asks what styles/forms exist, wants to pick a look, or when you're unsure about their taste:

```bash
open "${SKILL_DIR}/demo/index.html"        # macOS
xdg-open "${SKILL_DIR}/demo/index.html"    # Linux
```

Rules that keep this helpful instead of annoying:

1. **On demand, not by default.** Don't launch a browser for every request — only when they ask, or when you're genuinely uncertain about the style.
2. **Always pair it with text.** Say in one line what you opened, and list the 9 styles with a 3-5 word trait each (e.g. `warm` 暖色报告 / `dark` 深色科技 / `editorial` 杂志排版). Remote shells and headless environments have no browser — the flow must still work.
3. **Prefer 2-3 candidates over the full menu.** The 135-grid answers "what exists", not "what should I use". Recommend first, expand only if they want to browse.
4. **Anchor the style.** Once a style is chosen (by the user or by your recommendation), keep it for the rest of the session/document so a set of charts looks consistent — switch only when asked.
5. **Never block on it.** If they don't care about style, pick the recommended one for that form (see the auto-selection matrix) and move on.

**Each card also has a 「复制 prompt」 button** (no server involved — it only copies text) that yields a ready-to-paste line such as `画成时序图（sequence），主题用 warm（暖色报告）：<把内容写在这里>`. When you open the demo, tell the user they can browse, hit that button on whatever they like, and paste it back with their content.

### Step 3: Generate HTML

Based on confirmed style + chart type + structured content, generate complete HTML.

**Design process**:
1. Read `references/design-philosophy.md` for aesthetic principles
2. Read `references/styles/<style>.md` for style-specific CSS variables and components
3. Read `references/charts/<chart-type>.md` for layout rules and HTML structure
4. Generate HTML with all CSS inlined

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

**Reference**: `references/design-philosophy.md`, `references/styles/*.md`, `references/charts/*.md`

### Step 4: Screenshot

HTML 生成后，运行截图脚本（首次检查依赖是否已安装）：

```bash
[ -d "${SKILL_DIR}/node_modules" ] || (cd "${SKILL_DIR}" && npm install)
```

```bash
bun "${SKILL_DIR}/scripts/screenshot.ts" \
  --html <html_path> \
  --out <output_dir>/<filename>.png \
  --bg "<bg_color>" \
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

**Background color by style**:

| Style | bg_color | Width |
|-------|----------|-------|
| warm | `#faf6ee` | 860 |
| dark | `#0d1117` | 860 |
| minimal | `#ffffff` | 860 |
| editorial | `#f8f5f0` | 860 |
| neon | `#0a0015` | 860 |
| paper | `#f5f0e6` | 860 |
| glass | `#e8eaf0` | 860 |
| corporate | `#f4f6f9` | 860 |
| retro | `#1a1c2e` | 860 |

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
| 对比、PK、vs、优劣 | comparison | minimal |
| 时间、历史、里程碑、路线图 | timeline | editorial |
| 系统、服务、架构、组件 | architecture | dark |
| 数字、指标、统计、报表 | dashboard | glass |
| 计划、排期、进度、甘特 | gantt | warm |
| 团队、汇报、层级、组织 | org-chart | minimal |
| 转化、漏斗、筛选、销售 | funnel | neon |
| 思维导图、脑图、发散、分支 | mind-map | paper |
| 矩阵、象限、SWOT、优先级 | matrix | minimal |
| 看板、状态、待办、进行中 | kanban | glass |
| 清单、checklist、打勾、核查 | checklist | warm |
| 金句、引用、名言、摘录 | quote-card | editorial |
| 时序、调用链、请求响应、接口交互、回调 | sequence | dark |
| 泳道、跨角色、责任分工、交接、谁负责 | swimlane | corporate |

When unable to determine chart type, default to **flowchart**.
When unable to determine style, default to **warm**.

**Reference**: `references/chart-types.md`

---

## Style Overview

| Style | Tone | Key Visual |
|-------|------|------------|
| **warm** | 暖色报告 | 米白底，暖色边框，虚线箭头 |
| **dark** | 科技感 | 深色底，蓝绿发光，glow 效果 |
| **minimal** | 极简正式 | 纯白底，黑白无色彩 |
| **editorial** | 杂志排版 | 大号衬线字体，横线分割，category 标签 |
| **neon** | 赛博朋克 | 深紫/黑底，霓虹描边，发光字 |
| **paper** | 手绘纸质 | 米黄纸质感，铅笔线条风 |
| **glass** | 玻璃拟态 | 毛玻璃卡片，渐变底，光晕 |
| **corporate** | 商务正式 | 深蓝主色，极细边框，表头深色底 |
| **retro** | 复古像素 | CRT 扫描线，像素字体，硬边角 |

**All styles share the same layout principle**: compact, symmetric, full. Style only controls visual appearance (colors, fonts, textures, effects).

**Reference**: `references/styles/*.md`

---

## Chart Types Overview

| Type | Use Case | Key Layout |
|------|----------|------------|
| **flowchart** | 步骤、操作流程 | 横版(≤7步)/竖版，步骤卡+箭头 |
| **comparison** | 方案对比 | 双列并排，配色区分 |
| **timeline** | 里程碑、历史 | 竖轴，左右交错 |
| **architecture** | 系统组件 | 分层布局，节点+连线 |
| **dashboard** | 指标汇总 | 大数字卡横排+详情区 |
| **gantt** | 项目排期 | 横轴时间+横向条形 |
| **org-chart** | 团队结构 | 树形层级，上下连线 |
| **funnel** | 转化漏斗 | 梯形递减，百分比标注 |
| **mind-map** | 知识整理、发散 | 中心节点+放射分支，左右展开 |
| **matrix** | 优先级/SWOT | 2×2 网格+轴标签+象限卡片 |
| **kanban** | 任务看板 | 多列横排，状态分组+任务卡 |
| **checklist** | 清单确认 | 勾选列表+进度条+分组 |
| **quote-card** | 金句分享 | 大号引文居中+来源标注 |
| **sequence** | 调用链、请求响应 | 参与者+生命线+消息箭头 |
| **swimlane** | 跨角色流程 | 泳道×阶段网格+任务卡 |

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
- `styles/` — Detailed style definitions (CSS variables, components, effects)
- `charts/` — Detailed chart type layouts (HTML structure, CSS patterns)

Preview & tooling:
- `demo/index.html` — 15 forms × 9 styles full-matrix preview (filterable, click to zoom); open on demand, not for every request
- `tools/build-gallery.py` — regenerate the demo / any matrix (`all` / `light` / `embed` / `--only`)
