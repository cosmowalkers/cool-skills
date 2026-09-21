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

给前端同学收口图片用的：先在页面里量出**真实显示尺寸**（显示宽高 × DPR），据此决定导出多大，
再转 WebP/AVIF、按显示比例裁剪，最后用「边缘能量 + 解码内存」两个指标验证"屏上看不出差别"。
转格式、压尺寸、裁剪三个维度可以单用也可以组合。

```bash
S=image-optimize/scripts/optimize_images.py
python3 "$S" doctor                        # 环境自检（缺 Pillow 会打印安装命令）
python3 "$S" analyze src/assets/img --box 240x108 --dpr 2   # 体检：过采样多少、解码占多少内存
python3 "$S" export  src/assets/img --out /tmp/img-out --box 240x108 --dpr 2
python3 "$S" verify  src/assets/img /tmp/img-out --box 240x108 --dpr 2
```

两条别人踩过的坑，脚本已经挡掉：**导出绝不原地覆盖源文件**（目标路径与源文件重合会直接报错退出），
**重名冲突在写入前整体拒绝**（不会产出半个批次，目录输入会复刻子目录结构）。

- 依赖：`python3` + `Pillow`（不需要 npm；缺依赖时脚本会直接打印安装命令）
- 自带 58 个回归 + 可用性用例，改脚本后先跑：`python3 image-optimize/scripts/tests/test_optimize_images.py -v`
  （只依赖 python3 + Pillow，不联网、不动仓库素材，约 5 秒）
- 用法、五个常用配方、FAQ 与已知限制：见 [image-optimize/README.md](image-optimize/README.md)

## License

[MIT](LICENSE)
