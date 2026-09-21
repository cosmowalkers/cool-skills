# cool-skills

Agent 技能集合（Claude Code / Codex 通用）。每个目录是一个独立 skill，可直接放进 Agent 的 skills 目录使用。

| Skill | 说明 |
| --- | --- |
| [text2png](text2png/README.md) | 把一段文字变成有设计感的图表 PNG：15 种图表形式 × 9 种视觉主题 = 135 种组合，附全矩阵演示页 |
| [image-optimize](image-optimize/README.md) | 网页图片优化：压尺寸、转 WebP/AVIF、按显示比例裁剪，并用清晰度 + 解码内存指标验证"没压糊"；自带 58 个用例 |

## 安装

skill 本体就是目录，软链到 Agent 的 skills 目录即可，改完立即生效：

```bash
git clone git@github.com:cosmowalkers/cool-skills.git
cd cool-skills
for s in text2png image-optimize; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"   # Claude Code
  ln -sfn "$PWD/$s" ~/.codex/skills/"$s"    # Codex
done
```

## text2png

装完后用自然语言描述要画什么即可，例如「帮我画一张下单流程的时序图」。

首次使用需要在 `text2png/` 下执行一次 `npm install`（唯一依赖 `puppeteer-core`），并要求系统已装 Google Chrome。看演示页不需要这些准备。

能画什么、怎么用、怎么看 demo：见 [text2png/README.md](text2png/README.md)。

## image-optimize

装完后用一句话说需求即可，例如「商品列表页那个 banner 太大，帮我按实际显示尺寸压一下」。
它会量出图片在页面上的实际显示尺寸，据此重新出图、转 WebP/AVIF，并对比原图的渲染效果确认压完没变糊；
也能只转格式、只压尺寸或只裁剪。

产物默认导出到独立目录，不会覆盖源文件；同名冲突会在写入前整批中止。依赖 python3 与 Pillow（不需要 npm，
缺依赖时脚本会打印安装命令），仓库自带 59 个回归与可用性用例。

能做什么、怎么用、常见问题：见 [image-optimize/README.md](image-optimize/README.md)。

## License

[MIT](LICENSE)
