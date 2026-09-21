# cool-skills

Agent 技能集合（Claude Code / Codex 通用）。每个目录是一个独立 skill，可直接放进 Agent 的 skills 目录使用。

| Skill | 说明 |
| --- | --- |
| [text2png](text2png/README.md) | 把一段文字变成有设计感的图表 PNG：15 种图表形式 × 9 种视觉主题 = 135 种组合，附全矩阵演示页 |

## 安装

skill 本体就是目录，软链到 Agent 的 skills 目录即可，改完立即生效：

```bash
git clone git@github.com:cosmowalkers/cool-skills.git
cd cool-skills
ln -sfn "$PWD/text2png" ~/.claude/skills/text2png   # Claude Code
ln -sfn "$PWD/text2png" ~/.codex/skills/text2png    # Codex
```

## text2png

装完后用自然语言描述要画什么即可，例如「帮我画一张下单流程的时序图」。

首次使用需要在 `text2png/` 下执行一次 `npm install`（唯一依赖 `puppeteer-core`），并要求系统已装 Google Chrome。看演示页不需要这些准备。

能画什么、怎么用、怎么看 demo：见 [text2png/README.md](text2png/README.md)。

## License

[MIT](LICENSE)
