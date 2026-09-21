# 网页图片优化（image-optimize）

给前端研发的落地手册。这次沉淀的是"**屏上看不出差别的前提下，把图片像素数降下来**"的完整方法，
以及一个把裁剪 / 压尺寸 / 转格式一次做完的脚本。

## 先记住一件事：体积和解码内存是两回事

浏览器渲染一张图分两步：**下载**（看体积）和**解码**（看像素数）。真正把低端机拖卡的是后者——
一张 2848×1600 的图解码后占 17.4 MB 内存，跟它压缩得多小无关。

所以"图片优化"要同时看两个数字：

| 指标 | 决定因素 | 影响 |
| --- | --- | --- |
| 文件体积 | 像素数 + 编码质量 + 格式 | 首屏下载、流量 |
| 解码内存 | **只有像素数**（像素 × 4 字节） | 滚动流畅度、内存压力、闪退 |

## 什么时候用它

- 页面图片动辄几 MB，或者图片解码把内存吃满
- 图片压缩完被 QA / 设计说"发糊"
- 要把 PNG / JPEG 批量转 WebP 或 AVIF
- 要按 DPR 出多倍图，或评估某页图片体积
- 想确认"我的压缩到底有没有损失"

## 5 分钟上手

```bash
# 按实际安装位置改这一行：Codex 是 ~/.codex，Claude Code 换成 "$HOME/.claude/skills/image-optimize"
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/image-optimize"
S="$SKILL_DIR/scripts/optimize_images.py"
D="$SKILL_DIR/scripts"

# 0) 环境自检（缺依赖会告诉你装什么）
python3 "$S" doctor

# 0.5) 换机器 / 改过脚本后：跑自带用例（只依赖 python3 + Pillow，不联网、不动仓库素材）
python3 "$D/tests/test_optimize_images.py" -v

# 1) 体检：现有图片相对显示尺寸过采样多少、解码占多少内存
python3 "$S" analyze src/assets/img --box 240x108 --dpr 2

# 2) 导出：裁剪到显示比例 + 缩到合理尺寸 + 转 WebP（默认组合）
#    输出目录必须在源目录之外——脚本会拒绝把产物写回源目录，绝不原地覆盖原图
python3 "$S" export src/assets/img --out /tmp/img-out --box 240x108 --dpr 2

# 3) 验证：候选和"原图在浏览器里的渲染效果"比清晰度
python3 "$S" verify src/assets/img /tmp/img-out --box 240x108 --dpr 2

# 4) 目视确认后替换（输出目录复刻了源目录结构，可整目录覆盖），再重建产物
cp -R /tmp/img-out/. src/assets/img/ && npm run build
#    注意扩展名：默认转 WebP，hero.png 会变成 hero.webp，组件里的引用要一起改
```

`--box` 填图片在页面上的 **CSS 显示尺寸**，不知道怎么量就先在浏览器控制台里取：

```js
const im = document.querySelector('你的选择器'), r = im.getBoundingClientRect();
console.log(r.width, r.height, devicePixelRatio, im.naturalWidth, im.naturalHeight);
```

## 环境准备

脚本依赖 **python3 + Pillow**，一条命令：

```bash
python3 -m pip install --user Pillow
# 系统 Python 报 externally-managed 时：
python3 -m pip install --break-system-packages Pillow
```

装完跑 `python3 "$S" doctor`，四项格式（WebP / AVIF / JPEG / PNG）都打 ✓ 就能用。
如果 Pillow 缺失，脚本不会甩一堆 traceback，而是直接把上面的安装命令打给你。

AVIF 需要 Pillow ≥ 11 且编译了 libavif；不满足时脚本会明确提示，并建议本次先用 `--format webp`。

## 抄作业：五个常用配方（数字都是实测）

| 你要做的事 | 命令 | 实测效果 |
| --- | --- | --- |
| 只转 WebP，不动尺寸 | `export X --out O --no-crop --no-resize --quality 90` | JPEG 1208 KB → **259.8 KB**；PNG 11.1 MB → 660 KB |
| 只转 WebP 且零损失 | 同上 + `--lossless` | PNG 11.1 MB → 8.5 MB，像素完全一致 |
| 压尺寸 + 转 WebP | `export X --out O --no-crop --max-width 960` | JPEG 1208 KB → **42.5 KB**，解码 17.4 MB → 2.0 MB |
| **压尺寸 + 裁剪 + 转 WebP**（默认，推荐） | `export X --out O --box 240x108 --dpr 2` | JPEG 1208 KB → **40.3 KB**；六张图合计 341 KB → 195 KB，解码 59.9 MB → 9.5 MB |
| 保留原格式只压尺寸（例外） | 加 `--format keep` | 六张 341 KB → 208 KB |

转 AVIF：`--format avif --quality 60`（实测 JPEG 1.2 MB → 112.8 KB）。

## 输出格式：默认 WebP，也能明示转别的

下表数字来自同一个源（一张 1208 KB / 2848×1600 的 JPEG 照片，不裁不缩），便于横向比较：

| `--format` | 用途 | 无损 | 透明 | 实测（同一源） |
| --- | --- | --- | --- | --- |
| `webp`（默认） | 通用首选，照片/截图都合适 | ✓ `--lossless` | ✓ 保留 | 259.8 KB（q90） |
| `avif` | 想要最小体积 | ✗（Pillow 没有 lossless 开关，传了会被静默降级，脚本直接拒绝） | ✓ 保留 | **112.8 KB**（q60） |
| `jpeg` | 兼容老环境、对接只吃 JPEG 的接口 | ✗（传了会忽略并提示） | ✗（按 `--flatten-color` 合成底色并提示） | 356.8 KB（q85） |
| `png` | 需要无损或透明时 | ✓（本身无损，`--quality` 不生效） | ✓ 保留 | **2842.5 KB**——照片千万别转 PNG |
| `keep` | 只压尺寸/只裁剪，保持源格式 | 取决于源格式 | 取决于源格式 | 356.8 KB（jpeg 源重编码） |

一句话：**默认走 WebP；要更小用 AVIF；要兼容用 JPEG/PNG，但别拿 PNG 存照片。**
（裁剪与缩尺寸对任何格式都同样生效，上表刻意都关掉了，只看格式差异。）

## 参数速查

| 参数 | 说明 |
| --- | --- |
| `--box 240x108` / `--dpr 2` | 显示尺寸与目标设备像素比，决定"屏上像素" |
| `--supersample 2` | 宽度上限 = 屏上像素宽 × 该倍数（默认 2；1 偏省、3 最锐） |
| `--max-width 960` | 直接指定宽度上限，覆盖 supersample |
| `--quality 90` | 有损质量（webp / avif / jpeg 通用） |
| `--lossless` | 无损输出，**只有 webp 真正生效**（png 本身无损；avif 会被 Pillow 静默降级，脚本直接拒绝） |
| `--format webp\|avif\|jpeg\|png\|keep` | 输出格式，**默认 webp**；`keep` 保留源格式 |
| `--no-crop` | 不裁剪（只缩放 / 只转格式） |
| `--no-resize` | 不改尺寸（只裁剪 / 只转格式） |
| `--flatten-color '#000000'` | 透明图转 JPEG 时的合成底色 |

## 三个容易踩的坑

1. **导成 1:1 会显得更糊。** 浏览器把大图渲染到比自身小的尺寸时会做高质量降采样（等于超采样抗锯齿），只给 1:1 反而只剩放大插值。
   实测：2848×1600 压成 480×216 q80 后，高频细节（边缘能量）掉 5.7%，肉眼可辨；保留 2–3 倍超采样只掉 1.2–1.6%。
   **结论：目标不是 DPR×1，而是屏上像素的 2–3 倍。**
2. **只裁剪通常得不偿失。** 保持原分辨率裁剪，体积会因为重新编码变大（实测 +49%），解码内存也只降 23%。
   裁剪的价值在于"配合降到合理尺寸"。
3. **转格式不等于变小，也不省内存。** 纯色/线条/截图转 JPEG 会变大（实测 1.4 KB → 21 KB）；
   解码内存只跟像素数有关，换容器格式不会变。已经是 WebP 的再"转 WebP"没有意义。

## 替换与回滚

- 脚本**不会原地覆盖源文件**：`--out` 指向源目录会被直接拒绝；目录输入会复刻子目录结构，
  重名冲突（`a/same.png` + `a/same.jpg` 都转 WebP）在写入前整体拒绝，不会产出半个批次；
  一次传多个目录时用目录名做顶层前缀（`out/a/...`、`out/b/...`），避免跨目录同名互相覆盖
- 默认输出 WebP，扩展名会变（`hero.png` → `hero.webp`），组件里的 import / 引用要一起改；
  想代码零改动就用 `--format keep`（只压尺寸 / 只裁剪），或者源本来就是 WebP
- 替换前把原图复制到临时目录备份（`cp -a` ），并在提交信息里写清备份位置
- 替换后必须重建产物（`npm run build`），确认产物里的哈希与体积已更新
- 回滚就是把备份复制回去再重建；原图建议同时保留在高清源图仓库里

## 替代路线（不想装 Python 依赖时）

| 路线 | 适用 | 注意 |
| --- | --- | --- |
| Node：`sharp` / `vite-imagetools` / `@nuxt/image` | 构建期自动转 WebP/AVIF、出多倍图 | 推荐长期方案，缺点是要改构建配置 |
| CLI：`cwebp` / `avifenc`（`brew install webp libavif`） | 批量转换、跑得比 Pillow 快 | 只能转格式，裁剪/多倍图还得自己串命令 |
| 阿里云 OSS 图片处理：`?x-oss-process=image/format,webp` | 不想改产物，源图仍存原格式 | 转换在 CDN 侧，记得确认缓存与回源策略 |
| `sips`（macOS 自带） | 只改尺寸 / 转 JPEG、PNG | **不支持 WebP** |
| `ffmpeg` | 视频抽帧 | Mac 常见构建**没有 libwebp 编码器**，转 WebP 会静默失败 |

## FAQ

**提示 `No module named 'PIL'`？** 脚本会把安装命令打出来，照抄即可；装完先跑 `doctor`。

**转出来反而更大了？** 说明源图是纯色/线条/截图类内容，或者你用了 `--format keep` 只裁剪不降尺寸。
换成默认组合（转 WebP + 降尺寸），或对这类图改用 SVG。

**透明图转 JPEG 出现黑边？** JPEG 不支持 alpha，脚本按 `--flatten-color` 合成底色（默认黑）；
需要别的底色就显式传，比如 `--flatten-color '#0a0a0a'`。透明图更推荐留在 WebP/PNG。

**被说发糊怎么办？** 按顺序试：`--supersample` 提到 3 → `--quality` 提到 95 → 换更高清的源图。
经验值：整批平均边缘能量掉到 −4% 左右就会被看出来，掉 1~2% 基本没人能察觉。

**`verify` 报"临界"，但我觉得没差别？** 这个指标是拿"源图单步降采样到屏上尺寸"的理想结果做参考，
**偏保守**：源图越是高清高细节（比如 2848×1600 的棚拍图），导出后要经历两次重采样，指标天然吃亏。
均值在 −2.5% 以内就可以用，实在不放心再用真实浏览器截图目视比一次。反之，如果均值超过 −3.5%，
别硬上，直接升 `--supersample`。

**怎么确认无损？** 用 `--lossless` 导出后逐字节比对像素（Pillow 里对比原图与产物的像素数组），
或者在交付说明里写清"无损"和"有损（q90）"的区别，别含糊。

**能直接跑在 CI 里吗？** 可以，脚本只用标准库 + Pillow：用法 / 输入错误、原地覆盖、重名冲突、
AVIF 假无损都会以退出码 2 失败。但 `verify` 的清晰度结论目前只以文本给出（恒返回 0），别拿它当 CI 门禁；
CI 里也没有图形界面，`view_image` 这类目视确认要放到本地做。

## 已知限制（用之前先知道）

- **裁剪只支持居中**：主体不在中心时先 `view_image` 看图，或退回 `--no-crop` 只压尺寸
- **一次 `--box` 套整批目录**：hero、缩略图、图标比例不同时要分目录跑；`--box` 默认值就是 `240x108`，别忘显式传
- **`verify` 的判据以文本为准**：边缘能量对压缩振铃不敏感（"变锐"也可能是伪影），它也不检查平均像素差的阈值，
  结论是"可以替换"时仍建议目视确认一次
- **`verify` 必须与 `export` 用同一组 `--box / --dpr`**：不一致会算出无意义的差值，脚本目前无法自动发现
