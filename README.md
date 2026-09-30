# cool-skills

Agent 技能集合（Claude Code / Codex 通用）。每个目录是一个独立 skill，可直接放进 Agent 的 skills 目录使用。

| Skill | 说明 |
| --- | --- |
| [text2png](text2png/README.md) | 把一段文字变成有设计感的图表 PNG：15 种图表形式 × 9 种视觉主题 = 135 种组合，附全矩阵演示页 |
| [image-tools](image-tools/README.md) | 图片工具箱（已落地网页图片优化）：压尺寸、按需转 WebP/AVIF（默认保持原格式）、按显示比例裁剪，并用清晰度 + 解码内存指标验证"没压糊"；自带 87 个用例 |
| [commit-message](commit-message/README.md) | 提交规范：commit message 固定带修改目的 / 影响范围 / 改动范围 / 测试建议，并按"可独立回滚"把混合改动拆成多条提交 |

## 安装

skill 本体就是目录，软链到 Agent 的 skills 目录即可，改完立即生效（macOS / Linux）：

```bash
git clone git@github.com:cosmowalkers/cool-skills.git
cd cool-skills
for s in text2png image-tools commit-message; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"   # Claude Code
  ln -sfn "$PWD/$s" ~/.codex/skills/"$s"    # Codex
done
```

Windows（PowerShell）：建软链要管理员权限或开发者模式，直接复制更省事。

```powershell
git clone git@github.com:cosmowalkers/cool-skills.git
cd cool-skills
foreach ($s in 'text2png','image-tools','commit-message') {
  Copy-Item -Recurse -Force ".\$s" "$env:USERPROFILE\.codex\skills\$s"    # Codex
  Copy-Item -Recurse -Force ".\$s" "$env:USERPROFILE\.claude\skills\$s"   # Claude Code
}
```

代价是"改完不即时生效"，仓库更新后重跑一遍这段即可。

## text2png

装完后用自然语言描述要画什么即可，例如「帮我画一张下单流程的时序图」。

首次使用需要在 `text2png/` 下执行一次 `npm install`（唯一依赖 `puppeteer-core`），并要求系统已装 Google Chrome。看演示页不需要这些准备。

能画什么、怎么用、怎么看 demo：见 [text2png/README.md](text2png/README.md)。

## image-tools

定位是图片工具箱，第一条落地的流水线是网页图片优化；旋转、水印、目标体积等在 Roadmap 里。

装完后用一句话说需求即可，例如「商品列表页那个 banner 太大，帮我按实际显示尺寸压一下」。
它会量出图片在页面上的实际显示尺寸，据此重新出图，并对比原图的渲染效果确认压完没变糊；
默认保持原格式（只压尺寸、不动扩展名），明确说「转成 webp」才转格式；也能只转格式、只压尺寸或只裁剪。

产物默认导出到独立目录，不会覆盖源文件；同名冲突会在写入前整批中止。依赖 python3 与 Pillow（不需要 npm，
缺依赖时脚本会打印安装命令），仓库自带 87 个回归与可用性用例，macOS / Linux / Windows 通用。

能做什么、怎么用、常见问题：见 [image-tools/README.md](image-tools/README.md)。

## commit-message

提交规范和拆分方案。装完后一句话说需求即可，例如「把这次改动按规范拆一下提交了」。

产出的 message 固定包含四件套：修改目的、影响范围、改动范围、测试建议，配合 `perf` / `feat` / `fix` 类型前缀。
默认不提交、不 push——只有你明确说「提交」它才动 git，push 要单独再说一次。

它还会把混在一起的改动按「能否独立回滚」拆成多条提交；同一文件跨多类改动时按 hunk 拆，不会整文件带过去。

能做什么、怎么用：见 [commit-message/README.md](commit-message/README.md)。

## 本地开发辅助

`tools/` 下放着与 skill 内容无关的本地工具（介绍图生成、skill 前向测试），已在 `.gitignore` 中排除，不随仓库分发。

## License

[MIT](LICENSE)
