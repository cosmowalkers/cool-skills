#!/usr/bin/env python3
"""图片工具箱：按显示尺寸导出 + 清晰度验证（依赖 Pillow）。

用法示例：
  # 1) 体检：相对显示框过采样多少、解码占多少内存
  python3 optimize_images.py analyze assets/img --box 240x108 --dpr 2

  # 2) 导出（默认组合：裁剪到显示比例 + 缩到合理尺寸 + 转 WebP）
  python3 optimize_images.py export assets/img --out /tmp/img-out \\
      --box 240x108 --dpr 2 --supersample 2 --quality 90

  # 2a) 只转格式：不动尺寸、不裁剪（PNG/JPG → WebP）
  python3 optimize_images.py export photo.png --out /tmp/out \\
      --format webp --no-crop --no-resize --quality 90

  # 2b) 只压缩：保持原格式，只缩尺寸（或只调质量）
  python3 optimize_images.py export assets/img --out /tmp/out --format keep --no-crop --max-width 960

  # 2c) 只裁剪：保持原格式与分辨率，只按显示比例裁掉多余部分
  python3 optimize_images.py export assets/img --out /tmp/out --format keep --no-resize --box 240x108

  # 3) 验证：候选文件与“原图在浏览器里的渲染效果”对比
  python3 optimize_images.py verify assets/img /tmp/img-out --box 240x108 --dpr 2

  Windows 上把 python3 换成 py -3，/tmp/out 换成 $env:TEMP\\out（cmd 里是 %TEMP%\\out），
  路径反斜杠或正斜杠都行，含空格的加引号。

安全与正确性约定（回归用例见 scripts/tests/test_optimize_images.py）：
  * 导出目录必须独立于源目录：目标路径与源文件重合时直接报错退出，绝不原地覆盖原图。
    路径比较先归一化（resolve + normcase），Windows 的大小写不敏感不会让这条护栏失效。
  * 目录输入会在输出目录里复刻子目录结构；重名冲突在写入前整体拒绝，不会写出半个批次。
  * EXIF 方向先转正再裁剪导出，ICC / EXIF 元数据随产物保留。
  * Pillow 的 AVIF 编码器不支持无损：--format avif --lossless 会报错，而不是静默降级成有损。
  * 清晰度强校验：export 逐图比对候选与源图的渲染效果，下降超过 4% 判失真，最多再换 2 个方案
    （先提质量、再提尺寸）；仍失真时在报告里用 ✗ 标出该图，打印原因并以退出码 4 结束
    （产物照常生成，但结论是保留原图）。
  * export 可加 --report-json 落一份机器可读的结论（每张图的档位链、掉多少、pass/keep、原因），
    CI 用退出码判、读原因用这个文件，不必解析控制台文本；里面的路径统一是解析后的绝对路径。
  * 跨平台：macOS / Linux / Windows 通用。启动时把控制台输出钉成 UTF-8，报告里的 ✗ / → 在
    cp936 这类编码下也不会抛 UnicodeEncodeError。
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2          # 用法 / 输入 / 安全护栏问题
EXIT_DEP = 3            # 依赖缺失
EXIT_FIDELITY = 4       # 有图没过清晰度强校验（产物已生成，但结论是保留原图）

# 清晰度强校验：export 内置，判据与 verify 同源（都把候选与源图渲染到屏上尺寸再比边缘能量）。
FIDELITY_DROP_LIMIT = -4.0         # 单图下降超过它就判失真，自动升档重压
FIDELITY_BATCH_LIMIT = -3.5        # 整批均值线，与 verify 的“偏糊”判定同口径
FIDELITY_QUALITY_CEILING = 95      # 重压阶梯第一级：先提质量（代价比提尺寸小）
FIDELITY_SUPERSAMPLE_CEILING = 3   # 阶梯第二级：尺寸最多提到 3 倍
FIDELITY_MAX_RETRIES = 2           # 首轮没过后最多再换 2 个方案；换完仍失真就在报告里标出来


def force_utf8_output() -> None:
    """把控制台输出钉成 UTF-8。

    Windows 的控制台/重定向默认不是 UTF-8（cp936、cp1252 等），而报告里有 ✗ / ✓ / → 这些符号，
    不换编码会直接抛 UnicodeEncodeError 崩在打印上。换成 UTF-8 + errors=replace 后，
    最差也只是个别符号变成问号，不会中断整批导出。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)   # StringIO 之类没有，跳过
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding='utf-8', errors='replace')
        except (ValueError, OSError, LookupError):
            pass


def path_key(p: Path) -> str:
    """路径比较用的归一化键。

    Windows 的盘符与路径不区分大小写，直接拿 Path 或字符串相等判断会漏掉"同一个文件"，
    那正是"绝不原地覆盖源图"那条护栏依赖的判断，所以统一走 normcase + resolve。
    """
    return os.path.normcase(str(p.resolve()))


def temp_example_dir() -> str:
    """提示语里的示例输出目录：Windows 用 %TEMP%\\img-out，其余平台用 /tmp/img-out。"""
    return r'%TEMP%\img-out' if os.name == 'nt' else '/tmp/img-out'


try:
    import PIL
    from PIL import Image, ImageChops, ImageColor, ImageFilter, ImageOps, features
except ModuleNotFoundError as exc:  # 依赖缺失时给可直接照做的安装指引
    force_utf8_output()
    sys.stderr.write(
        f'缺少依赖 Pillow（错误：{exc}）。\n'
        'analyze / export / verify 都依赖 Pillow（python3 图像库），安装方式任选其一：\n'
        '  python3 -m pip install --user Pillow\n'
        '  python3 -m pip install --break-system-packages Pillow   # 系统 Python 拒绝安装时用\n'
        '  brew install python3 && python3 -m pip install Pillow   # 想用 Homebrew Python\n'
        '  py -3 -m pip install Pillow                            # Windows（或 python -m pip）\n'
        '装完执行 `python3 optimize_images.py doctor`（Windows 用 `py -3 optimize_images.py doctor`）自检；'
        'AVIF 需要 Pillow ≥ 11 且编译了 libavif。\n'
        '不想装 Python 依赖时的替代路线（cwebp / avifenc / ImageMagick / sharp / CDN 实时转换）'
        '见 skill 目录下 README.md 的对应小节。\n'
    )
    raise SystemExit(EXIT_DEP) from exc

IMAGE_EXT = {'.webp', '.jpg', '.jpeg', '.png', '.avif'}
FORMAT_EXT = {'webp': '.webp', 'avif': '.avif', 'jpeg': '.jpg', 'png': '.png'}

# 显示框宽高比的合理区间：太极端会把图裁成 1px 细条（libwebp 会直接 MemoryError）
MIN_BOX_RATIO = 0.05
MAX_BOX_RATIO = 20.0

AVIF_LOSSLESS_HINT = (
    'Pillow 无法输出无损 AVIF：它的 AVIF 编码器没有 lossless 开关，'
    '传 lossless 会被静默忽略并回落到默认 quality=75（等于标着“无损”的有损文件）。\n'
    '可用的选择：\n'
    '  * 真无损：--format webp --lossless\n'
    '  * 更小体积：--format avif --quality 60~90（有损）\n'
    '  * 确需无损 AVIF：在外部用 avifenc --lossless 转换'
)


def parse_box(value: str) -> tuple[int, int]:
    try:
        w, h = value.lower().replace(' ', '').split('x')
        box = (int(w), int(h))
    except Exception:
        raise argparse.ArgumentTypeError('显示尺寸应写成 宽x高，例如 240x108')
    if box[0] <= 0 or box[1] <= 0:
        raise argparse.ArgumentTypeError('显示尺寸必须为正数')
    ratio = box[0] / box[1]
    if not MIN_BOX_RATIO <= ratio <= MAX_BOX_RATIO:
        raise argparse.ArgumentTypeError(
            f'显示尺寸比例过于极端（{box[0]}:{box[1]}）：'
            f'宽高比请落在 1:{int(1 / MIN_BOX_RATIO)} ~ {int(MAX_BOX_RATIO)}:1 之间，'
            '否则裁剪后会只剩几像素高的细条'
        )
    return box


DEFAULT_BOX = (240, 108)


def resolve_box(args: argparse.Namespace) -> tuple[int, int]:
    """--box 未显式给出时退回占位尺寸，但要提醒：默认值不是量出来的显示尺寸。"""
    if args.box is not None:
        return args.box
    print(
        f'注意：--box 未指定，正按默认 {DEFAULT_BOX[0]}x{DEFAULT_BOX[1]} 计算。'
        '默认值只是占位，不是量出来的显示尺寸——先按工作流第 1 步量出真实尺寸（或让用户明确给出），'
        '再拿结果去出图。',
        file=sys.stderr,
    )
    return DEFAULT_BOX


def positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError('应为数字')
    if number <= 0:
        raise argparse.ArgumentTypeError('必须大于 0')
    return number


def quality_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('应为整数')
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError('质量取值范围是 1~100')
    return number


def max_width_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('应为整数')
    if number < 0:
        raise argparse.ArgumentTypeError('宽度上限不能为负（0 表示不限制）')
    return number


def flatten_color_arg(value: str) -> str:
    try:
        ImageColor.getrgb(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f'无法识别的颜色：{value}（例如 #000000 或 white）')
    return value


def collect_images(targets: list[str]) -> list[tuple[Path, Path]]:
    """展开目标为 (文件, 归属根目录) 列表；目录递归，单文件以所在目录为根。

    保留归属根目录是为了让下游能拿到“相对路径”：
    1) 导出时在输出目录里复刻同样的相对路径，避免不同子目录的同名文件互相覆盖；
    2) verify 时按相对路径配对，避免只按文件名配对而配错。

    一次传多个目录时，以各目录的父目录为根，等于用目录名做一层前缀
    （`export a b --out out` → `out/a/...`、`out/b/...`），否则两个目录里的同名图会互相撞。
    """
    found: list[tuple[Path, Path]] = []
    multi_dirs = len([t for t in targets if Path(t).is_dir()]) > 1
    for raw in targets:
        p = Path(raw)
        if p.is_dir():
            root = p.parent if multi_dirs else p
            found += [
                (f, root)
                for f in sorted(p.rglob('*'))
                if f.is_file() and f.suffix.lower() in IMAGE_EXT
            ]
        elif p.is_file():
            found.append((p, p.parent))
        else:
            print(f'跳过不存在的路径：{p}', file=sys.stderr)
    return found


def kb(n: int) -> str:
    return f'{n / 1024:.1f} KB'


def display_name(p: Path) -> str:
    try:
        rel = p.relative_to(Path.cwd())
    except ValueError:
        rel = p
    text = str(rel)
    return text if len(text) <= 42 else text[:19] + '…' + text[-22:]


def attempt_label(src: Path, dst: Path) -> str:
    """产物名与源名不同（转格式）时写成 hero.jpg→hero.webp，便于对上 verify 的表。"""
    return dst.name if src.name == dst.name else f'{src.name}→{dst.name}'


def decoded_mb(pixels: int) -> str:
    return f'{pixels * 4 / 1024 / 1024:.1f} MB'


def is_within(child: Path, parent: Path) -> bool:
    """child 是否在 parent 目录之内（含相等）。走 path_key，Windows 上大小写不同也算同一个目录。"""
    child_key, parent_key = path_key(child), path_key(parent)
    return child_key == parent_key or child_key.startswith(parent_key + os.sep)


def source_format(src: Path) -> str:
    ext = src.suffix.lower().lstrip('.')
    return 'jpeg' if ext in ('jpg', 'jpeg') else ext


def resolve_format(fmt: str, src: Path) -> str:
    """--format keep 时沿用源格式。"""
    if fmt != 'keep':
        return fmt
    ext = source_format(src)
    if ext in ('jpeg', 'webp', 'avif', 'png'):
        return ext
    raise SystemExit(f'无法识别源格式 {src.suffix}，请显式指定 --format')


def edge_energy(im: Image.Image) -> float:
    """边缘能量：高频细节的粗略度量，用来判断“有没有发糊”。"""
    gray = im.convert('L').filter(ImageFilter.FIND_EDGES)
    hist = gray.histogram()
    total = sum(i * hist[i] for i in range(256))
    return total / (gray.size[0] * gray.size[1])


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a, b)
    hist = diff.histogram()
    total = sum(i * (hist[i] + hist[256 + i] + hist[512 + i]) for i in range(256))
    return total / (a.size[0] * a.size[1] * 3)


def oriented_size(im: Image.Image) -> tuple[int, int]:
    """浏览器实际显示的像素尺寸（考虑 EXIF 方向）。"""
    try:
        orientation = im.getexif().get(0x0112)
    except Exception:
        orientation = None
    if orientation in (5, 6, 7, 8):
        return (im.size[1], im.size[0])
    return im.size


def render_like_browser(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """模拟浏览器渲染结果：先按 EXIF 方向转正，再等价 object-fit: cover 居中裁剪 + 高质量缩放。"""
    oriented = ImageOps.exif_transpose(im) or im
    return ImageOps.fit(oriented.convert('RGB'), size, Image.LANCZOS, centering=(0.5, 0.5))


def crop_to_ratio(im: Image.Image, ratio: float) -> Image.Image:
    """按目标宽高比居中裁剪，不缩放。"""
    w, h = im.size
    target_h = max(1, round(w / ratio))
    if target_h <= h:
        top = (h - target_h) // 2
        return im.crop((0, top, w, top + target_h))
    target_w = max(1, round(h * ratio))
    left = (w - target_w) // 2
    return im.crop((left, 0, left + target_w, h))


def load_for_edit(src: Path) -> tuple[Image.Image, dict[str, object], bool]:
    """读取图片：按 EXIF 方向转正、保留透明通道，并收集需要随产物保留的元数据。

    返回 (图像, 元数据, 是否发生过方向转正)。
    """
    with Image.open(src) as raw:
        raw.load()
        im = ImageOps.exif_transpose(raw)
        if im is None:  # 老版本 Pillow 在没有方向信息时会返回 None
            im = raw.copy()
        has_alpha = im.mode in ('RGBA', 'LA') or 'transparency' in im.info
        meta: dict[str, object] = {
            key: im.info[key]
            for key in ('icc_profile', 'exif', 'xmp')
            if im.info.get(key)
        }
        transposed = im.size != raw.size
    exif = meta.get('exif')
    if isinstance(exif, Image.Exif):
        meta['exif'] = exif.tobytes()
    return im.convert('RGBA' if has_alpha else 'RGB'), meta, transposed


def save_variant(
    im: Image.Image,
    dst: Path,
    fmt: str,
    args: argparse.Namespace,
    meta: dict[str, object],
    quality: int | None = None,
) -> None:
    """按目标格式落盘；JPEG 不支持 alpha，会合成 --flatten-color 底色；ICC/EXIF 随产物保留。

    quality 用于清晰度强校验的升档重压（先提质量、再提尺寸），不传就用 --quality。
    """
    quality = args.quality if quality is None else quality
    if fmt == 'webp':
        kwargs: dict[str, object] = {'method': 6, **meta}
        if args.lossless:
            kwargs['lossless'] = True
        else:
            kwargs['quality'] = quality
        im.save(dst, 'WEBP', **kwargs)
    elif fmt == 'avif':
        if not features.check('avif'):
            raise SystemExit(
                '当前 Pillow 没有 AVIF 支持（需要 Pillow ≥ 11 且编译了 libavif）。\n'
                '解决：python3 -m pip install --upgrade Pillow，或本次改用 --format webp。'
            )
        if args.lossless:
            raise SystemExit(AVIF_LOSSLESS_HINT)
        im.save(dst, 'AVIF', quality=quality, **meta)
    elif fmt == 'jpeg':
        if im.mode == 'RGBA':
            bg = Image.new('RGB', im.size, args.flatten_color)
            bg.paste(im, mask=im.split()[-1])
            im = bg
        im.convert('RGB').save(
            dst, 'JPEG', quality=quality, optimize=True, progressive=True, **meta
        )
    elif fmt == 'png':
        im.save(dst, 'PNG', optimize=True, compress_level=9, **meta)
    else:
        raise SystemExit(f'不支持的输出格式：{fmt}')


def plan_outputs(
    images: list[tuple[Path, Path]], out_dir: Path, args: argparse.Namespace
) -> tuple[list[tuple[Path, Path, str]], list[str]]:
    """写入前算出全部目标路径。

    两类问题会让整批直接中止（blocked），保证不原地覆盖源文件、也不静默丢图：
    * 目标路径与某个源文件重合（--out 指向源目录，或导出成同名同格式）；
    * 两个源文件会写成同一个目标路径（同名不同扩展名，或同一文件被输入两次）。
    """
    plans: list[tuple[Path, Path, str]] = []
    blocked: list[str] = []
    taken: dict[str, Path] = {}
    for src, root in images:
        fmt = resolve_format(args.format, src)
        rel = src.relative_to(root)
        name = rel.name if fmt == source_format(src) else rel.stem + FORMAT_EXT[fmt]
        dst = (out_dir / rel.parent / name).resolve()
        src_key, dst_key = path_key(src), path_key(dst)
        if fmt == 'avif' and args.lossless:
            blocked.append(
                f'{src}：Pillow 的 AVIF 编码器不支持无损，需要真无损请改用 --format webp --lossless'
            )
            continue
        if fmt == 'avif' and not features.check('avif'):
            blocked.append(f'{src}：当前 Pillow 没有 AVIF 支持，改用 --format webp 或升级 Pillow')
            continue
        if dst_key == src_key:
            blocked.append(f'{src} 的导出目标与源文件重合：{dst}')
            continue
        if dst_key in taken:
            blocked.append(f'{taken[dst_key]} 与 {src} 会写成同一个文件：{dst}')
            continue
        taken[dst_key] = src
        plans.append((src, dst, fmt))
    return plans, blocked


# --------------------------------------------------------------------------- #
# 清晰度强校验：导出后逐图比对，失真就升档重压，到顶仍失真就说明原因
# --------------------------------------------------------------------------- #
def cap_width_for(box: tuple[int, int], args: argparse.Namespace, supersample: float) -> int:
    """这一档的宽度上限（0 表示不缩放）。"""
    if args.no_resize:
        return 0
    return args.max_width or round(box[0] * args.dpr * supersample)


def bake_variant(
    im: Image.Image,
    dst: Path,
    fmt: str,
    args: argparse.Namespace,
    meta: dict[str, object],
    ratio: float,
    cap_w: int,
    quality: int,
) -> tuple[int, int]:
    """按一套参数出图：裁剪 → 缩到宽度上限（不放大）→ 落盘，返回输出尺寸。"""
    work = im if args.no_crop else crop_to_ratio(im, ratio)
    if cap_w and work.width > cap_w:
        work = work.resize((cap_w, max(1, round(work.height * cap_w / work.width))), Image.LANCZOS)
    save_variant(work, dst, fmt, args, meta, quality=quality)
    return work.size


def compare_render(ref: Path, cand: Path, device: tuple[int, int]) -> tuple[float, float, float]:
    """把两张图各自按“浏览器会怎么渲染”重采样到屏上尺寸。

    返回 (参考边缘能量, 候选边缘能量, 平均像素差)。export 的强校验与 verify 用的是同一段逻辑，
    两边的数字才是同一口径。
    """
    with Image.open(ref) as r, Image.open(cand) as c:
        ref_render = render_like_browser(r, device)
        cand_render = render_like_browser(c, device)
    return (edge_energy(ref_render), edge_energy(cand_render),
            mean_abs_diff(ref_render, cand_render))


def drop_pct(e_ref: float, e_cand: float) -> float:
    """边缘能量变化百分比；源图没有边缘（纯色）时按 0 处理，否则会除零。"""
    return (e_cand - e_ref) / e_ref * 100 if e_ref else 0.0


def fidelity_drop(ref: Path, cand: Path, device: tuple[int, int]) -> float:
    e_ref, e_cand, _diff = compare_render(ref, cand, device)
    return drop_pct(e_ref, e_cand)


def next_escalation(
    supersample: float, quality: int, fmt: str, args: argparse.Namespace, tried: int
) -> tuple[float, int] | None:
    """失真后的下一个替代方案：先提质量（体积代价小），质量到顶再提尺寸；没得换就返回 None。

    tried 是已经换过的方案数，最多换 FIDELITY_MAX_RETRIES 个。上限是 supersample 3 + q95
    —— 这也是 SKILL.md 里“被反馈发糊”时的推荐档位。
    """
    if tried >= FIDELITY_MAX_RETRIES:
        return None
    lossy = fmt == 'jpeg' or (fmt in ('webp', 'avif') and not args.lossless)
    if lossy and quality < FIDELITY_QUALITY_CEILING:
        return supersample, FIDELITY_QUALITY_CEILING
    # --no-resize / --max-width 已经把尺寸钉住了，提 supersample 不会有任何效果
    if not args.no_resize and not args.max_width and supersample < FIDELITY_SUPERSAMPLE_CEILING:
        return FIDELITY_SUPERSAMPLE_CEILING, quality
    return None


def export_with_fidelity(
    im: Image.Image,
    src: Path,
    dst: Path,
    fmt: str,
    args: argparse.Namespace,
    meta: dict[str, object],
    ratio: float,
    box: tuple[int, int],
    device: tuple[int, int],
) -> list[dict[str, object]]:
    """导出单张图并做清晰度强校验：失真就换方案重压（最多 FIDELITY_MAX_RETRIES 次），

    返回每次尝试的记录，最后一条即交付的产物。
    """
    attempts: list[dict[str, object]] = []
    supersample, quality = args.supersample, args.quality
    while True:
        cap_w = cap_width_for(box, args, supersample)
        size = bake_variant(im, dst, fmt, args, meta, ratio, cap_w, quality)
        attempts.append({
            'supersample': supersample,
            'quality': quality,
            'cap_w': cap_w,
            'size': size,
            'bytes': dst.stat().st_size,
            'drop': fidelity_drop(src, dst, device),
        })
        if attempts[-1]['drop'] >= FIDELITY_DROP_LIMIT:
            break
        nxt = next_escalation(supersample, quality, fmt, args, len(attempts) - 1)
        if nxt is None:
            break
        supersample, quality = nxt
    return attempts


def describe_attempt(attempt: dict[str, object], fmt: str, args: argparse.Namespace) -> str:
    """把一次尝试写成 "ss1/q95 960px 宽 -0.3%（通过）" 这样的一行。"""
    lossless = fmt == 'png' or args.lossless
    quality = '无损' if lossless else f'q{attempt["quality"]}'
    state = '通过' if attempt['drop'] >= FIDELITY_DROP_LIMIT else '仍失真'
    size = attempt['size']
    return (f'ss{attempt["supersample"]:g}/{quality} {size[0]}px 宽 '
            f'{attempt["drop"]:+.1f}%（{state}）')


def fidelity_diagnosis(
    src_size: tuple[int, int],
    attempts: list[dict[str, object]],
    fmt: str,
    args: argparse.Namespace,
    device: tuple[int, int],
) -> list[str]:
    """没通过强校验时，用已有证据说清“为什么压不成功”，而不是只丢一个百分数。"""
    first, final = attempts[0], attempts[-1]
    cap_w = first['cap_w']
    reasons: list[str] = []
    if len(attempts) > 1:
        reasons.append(f'已换过 {len(attempts) - 1} 个方案（先提质量、再提尺寸）仍不达标')
    if cap_w and src_size[0] < cap_w:
        reasons.append(f'源图比目标还窄（源宽 {src_size[0]}px < 目标 {cap_w}px），脚本不放大，'
                       '这一档拿不回清晰度')
    if src_size[0] < device[0]:
        reasons.append(f'源图像素不足：源宽 {src_size[0]}px < 屏上像素宽 {device[0]}px，'
                       f'浏览器要放大 {device[0] / src_size[0]:.1f} 倍，该换更大的素材')
    if fmt == 'png' or args.lossless:
        reasons.append(f'{fmt.upper()} 是无损输出，质量档不适用，只能靠提尺寸')
    if args.no_resize or args.max_width:
        limit = '--no-resize' if args.no_resize else f'--max-width {args.max_width}'
        reasons.append(f'尺寸被 {limit} 钉住，没法用提尺寸换清晰度，只能提质量')
    if final['supersample'] >= FIDELITY_SUPERSAMPLE_CEILING:
        reasons.append(f'已到最稳妥档（supersample {FIDELITY_SUPERSAMPLE_CEILING} + '
                       f'q{FIDELITY_QUALITY_CEILING}）仍下降 {abs(final["drop"]):.1f}%')
    elif len(attempts) == 1:
        reasons.append(f'没有可再升的档位（当前 supersample {final["supersample"]:g} '
                       f'+ q{final["quality"]}）')
    if len(attempts) > 1 and final['drop'] <= first['drop']:
        reasons.append(f'升档没有改善（{first["drop"]:+.1f}% → {final["drop"]:+.1f}%），'
                       '说明掉的不是这一个变量，别继续调参数了')
    return reasons


def write_json_report(path: Path, payload: dict[str, object]) -> None:
    """落一份机器可读的导出结论：CI 读退出码判生死，读这个文件拿原因和逐图结果。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def cmd_analyze(args: argparse.Namespace) -> int:
    images = collect_images(args.paths)
    if not images:
        print('没有找到图片', file=sys.stderr)
        return EXIT_USAGE
    box = resolve_box(args)
    device = (round(box[0] * args.dpr), round(box[1] * args.dpr))
    print(f'显示框 {box[0]}x{box[1]} CSS px，DPR {args.dpr} → 屏上像素 {device[0]}x{device[1]}'
          f'（推荐导出宽度 {device[0] * 2}~{device[0] * 3}）')
    print(f'{"文件":<40}{"格式":<7}{"尺寸":<12}{"体积":>10}{"解码内存":>10}{"倍率(宽)":>10}  建议')
    total_bytes = total_px = 0
    rotated = 0
    for src, _root in images:
        with Image.open(src) as im:
            shown = oriented_size(im)
            raw_size = im.size
        size = src.stat().st_size
        px = raw_size[0] * raw_size[1]
        total_bytes += size
        total_px += px
        fmt = source_format(src)
        convert = '' if fmt == 'webp' else f'{fmt}→WebP（默认），'
        ratio = shown[0] / device[0]
        if ratio >= 4:
            advice = '过采样严重，可降到 2~3 倍'
        elif ratio >= 2:
            advice = '推荐区间（2~3 倍）'
        elif ratio >= 1.2:
            advice = '偏保守，发糊就提到 2 倍'
        else:
            advice = '像素不足，可能发糊（换更高清源图）'
        mark = ' *' if shown != raw_size else ''
        if mark:
            rotated += 1
        print(f'{display_name(src):<40}{fmt:<7}{f"{shown[0]}x{shown[1]}{mark}":<12}{kb(size):>10}'
              f'{decoded_mb(px):>10}{ratio:>9.1f}x  {convert}{advice}')
    print(f'{"合计":<40}{"":<7}{"":<12}{kb(total_bytes):>10}{decoded_mb(total_px):>10}')
    if rotated:
        print(f'* {rotated} 张带 EXIF 方向标记：表中按浏览器显示方向给出尺寸，'
              '导出时会先转正再裁剪，不会导出成躺倒的图。')
    return EXIT_OK


def cmd_export(args: argparse.Namespace) -> int:
    images = collect_images(args.paths)
    if not images:
        print('没有找到图片', file=sys.stderr)
        return EXIT_USAGE
    if args.format == 'avif' and args.lossless:
        print(AVIF_LOSSLESS_HINT, file=sys.stderr)
        return EXIT_USAGE
    report_path = Path(args.report_json) if args.report_json else None
    if report_path is not None and report_path.is_dir():
        print(f'--report-json 要的是文件路径，这个位置是目录：{report_path}', file=sys.stderr)
        return EXIT_USAGE

    out_dir = Path(args.out)
    plans, blocked = plan_outputs(images, out_dir, args)
    if blocked:
        print('导出已中止，源文件没有任何改动：', file=sys.stderr)
        for line in blocked:
            print(f'  - {line}', file=sys.stderr)
        print(f'处理：把 --out 指到源目录之外的独立目录（例如 {temp_example_dir()}）；'
              '源图同名冲突时可用 --format keep 保留各自扩展名，或把它们分开导出。', file=sys.stderr)
        return EXIT_USAGE
    for raw in args.paths:
        p = Path(raw)
        base = p if p.is_dir() else p.parent
        if is_within(out_dir, base):
            print(
                f'警告：输出目录 {out_dir} 位于输入目录 {base} 之内，再次导出会把上一次的产物当成输入重新处理；'
                f'建议换成源目录之外的独立目录（例如 {temp_example_dir()}）。',
                file=sys.stderr,
            )
            break

    out_dir.mkdir(parents=True, exist_ok=True)
    box = resolve_box(args)
    ratio = box[0] / box[1]
    device = (round(box[0] * args.dpr), round(box[1] * args.dpr))
    cap_w = cap_width_for(box, args, args.supersample)
    steps = []
    if not args.no_crop:
        steps.append(f'裁剪到 {ratio:.3f}:1')
    if cap_w:
        steps.append(f'宽度上限 {cap_w}px')
    if args.format == 'png':
        quality_text = '无损（PNG 固定无损，--quality 不生效）'
    elif args.lossless:
        quality_text = '无损（Pillow 只支持 webp / png 无损；jpeg 会忽略）'
    else:
        quality_text = f'q{args.quality}'
    print('处理：' + ('、'.join(steps) or '仅重新编码') + f'；输出 {args.format} {quality_text}')
    if args.format == 'keep':
        print('提示：默认输出是 WebP（PNG/JPEG/AVIF 一律转）；--format keep 只在明确要求保留原格式时使用')
    print(f'清晰度强校验：候选与源图都按浏览器渲染到屏上尺寸比边缘能量，单图下降超过 '
          f'{abs(FIDELITY_DROP_LIMIT):.1f}% 判失真，最多再换 {FIDELITY_MAX_RETRIES} 个方案'
          f'（先提 --quality 到 {FIDELITY_QUALITY_CEILING}，再提 --supersample 到 '
          f'{FIDELITY_SUPERSAMPLE_CEILING}）；换完仍不达标的会在下面的报告里标 ✗')
    print(f'{"文件":<40}{"原尺寸":<12}{"新尺寸":<12}{"格式":<10}{"原体积":>10}{"新体积":>10}{"解码内存":>18}')
    before_bytes = after_bytes = before_px = after_px = 0
    flattened = 0
    grew: list[str] = []
    undersized: list[str] = []
    same_format_lossy = 0
    transposed = 0
    retried: list[tuple[Path, Path, str, list[dict[str, object]]]] = []
    failed: list[tuple[Path, Path, str, list[str], list[dict[str, object]]]] = []
    records: list[dict[str, object]] = []
    clean_drops: list[float] = []
    all_drops: list[float] = []
    for src, dst, fmt in plans:
        im, meta, was_transposed = load_for_edit(src)
        if was_transposed:
            transposed += 1
        src_size = im.size  # 已按 EXIF 方向转正
        src_bytes = src.stat().st_size
        if fmt == 'jpeg' and im.mode == 'RGBA':
            flattened += 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        attempts = export_with_fidelity(im, src, dst, fmt, args, meta, ratio, box, device)
        final = attempts[-1]
        dst_bytes = final['bytes']
        drop = final['drop']
        all_drops.append(drop)
        if len(attempts) > 1:
            retried.append((src, dst, fmt, attempts))
        else:
            clean_drops.append(drop)
        reasons = (fidelity_diagnosis(src_size, attempts, fmt, args, device)
                   if drop < FIDELITY_DROP_LIMIT else [])
        if reasons:
            failed.append((src, dst, fmt, reasons, attempts))
        out_w, out_h = final['size']
        out_px = out_w * out_h
        grew_this = dst_bytes > src_bytes
        undersized_this = bool(final['cap_w']) and src_size[0] < final['cap_w']
        same_format_this = (not args.lossless and fmt == source_format(src)
                            and fmt in ('webp', 'jpeg', 'avif'))
        if dst_bytes > src_bytes:
            grew.append(display_name(src))
        if undersized_this:
            undersized.append(display_name(src))
        if same_format_this:
            same_format_lossy += 1
        records.append({
            'src': str(src.resolve()),
            'dst': str(dst),
            'label': attempt_label(src, dst),
            'src_format': source_format(src),
            'out_format': fmt,
            'src_size': [src_size[0], src_size[1]],
            'out_size': [out_w, out_h],
            'src_bytes': src_bytes,
            'out_bytes': dst_bytes,
            'src_px': src_size[0] * src_size[1],
            'out_px': out_px,
            'drop': round(drop, 2),
            'passed': not reasons,
            'retries': len(attempts) - 1,
            'reasons': reasons,
            'grew': grew_this,
            'undersized': undersized_this,
            'same_format_lossy': same_format_this,
            'attempts': [
                {
                    'supersample': a['supersample'],
                    'quality': a['quality'],
                    'cap_w': a['cap_w'],
                    'size': [a['size'][0], a['size'][1]],
                    'bytes': a['bytes'],
                    'drop': round(a['drop'], 2),
                }
                for a in attempts
            ],
        })
        before_bytes += src_bytes
        after_bytes += dst_bytes
        before_px += src_size[0] * src_size[1]
        after_px += out_px
        print(f'{display_name(src):<40}{f"{src_size[0]}x{src_size[1]}":<12}'
              f'{f"{out_w}x{out_h}":<12}'
              f'{source_format(src) + "→" + fmt:<10}'
              f'{kb(src_bytes):>10}{kb(dst_bytes):>10}'
              f'{decoded_mb(src_size[0] * src_size[1]) + " → " + decoded_mb(out_px):>18}')
    saved = (1 - after_bytes / before_bytes) * 100 if before_bytes else 0
    print(f'{"合计":<40}{"":<12}{"":<12}{"":<10}{kb(before_bytes):>10}{kb(after_bytes):>10}')
    print(f'体积下降 {saved:.0f}%；解码内存 {decoded_mb(before_px)} → {decoded_mb(after_px)}')
    mean_drop = sum(all_drops) / len(all_drops) if all_drops else 0.0
    print()
    print(f'清晰度强校验（单图失真线 {abs(FIDELITY_DROP_LIMIT):.1f}%，整批均值线 '
          f'{abs(FIDELITY_BATCH_LIMIT):.1f}%，与 verify 同一口径；单图没过会依次换方案，'
          f'最多 {FIDELITY_MAX_RETRIES} 次）')
    for src, dst, fmt, attempts in retried:
        chain = ' → '.join(describe_attempt(a, fmt, args) for a in attempts)
        print(f'  {attempt_label(src, dst)}：{chain}')
    if clean_drops:
        print(f'  其余 {len(clean_drops)} 张首轮即通过（最大下降 {max(clean_drops):+.1f}%）')
    for src, dst, fmt, _reasons, attempts in failed:
        print(f'  ✗ {attempt_label(src, dst)}：{describe_attempt(attempts[-1], fmt, args)}'
              f'｜已换过 {len(attempts) - 1} 个方案仍不达标，建议保留原图')
    print(f'  整批平均边缘能量变化：{mean_drop:+.1f}%')
    if failed:
        print(f'  结论：{len(plans) - len(failed)} 张可替换；{len(failed)} 张建议保留原图（上面标 ✗ 的），'
              '原因见下方说明')
    elif mean_drop < FIDELITY_BATCH_LIMIT:
        print(f'  结论：单图都在失真线以内，但整批均值 {mean_drop:+.1f}% 落进偏糊区间，建议整体保留原图')
    else:
        print(f'  结论：{len(plans)} 张都在失真线以内，可进入交付前的目视确认')
    if report_path is not None:
        keep = bool(failed) or mean_drop < FIDELITY_BATCH_LIMIT
        payload: dict[str, object] = {
            'version': 1,
            'command': 'export',
            # 路径统一成解析后的规范形态（macOS 上 /tmp 会展开成 /private/tmp），
            # 免得下游拿到 out_dir 与 images[].dst 两种写法对不上。
            'out_dir': str(out_dir.resolve()),
            'target': {
                'box': [box[0], box[1]],
                'dpr': args.dpr,
                'device_px': [device[0], device[1]],
                'crop_ratio': round(ratio, 4),
                'format': args.format,
                'quality': args.quality,
                'lossless': bool(args.lossless),
                'supersample': args.supersample,
                'max_width': args.max_width or None,
                'no_crop': bool(args.no_crop),
                'no_resize': bool(args.no_resize),
            },
            'summary': {
                'images': len(records),
                'replaceable': len(records) - len(failed),
                'keep_original': len(failed),
                'src_bytes': before_bytes,
                'out_bytes': after_bytes,
                'saved_pct': round(saved, 1),
                'src_px': before_px,
                'out_px': after_px,
                'grew': grew,
                'undersized': undersized,
                'same_format_lossy': same_format_lossy,
                'transposed': transposed,
                'flattened': flattened,
            },
            'fidelity': {
                'drop_limit': FIDELITY_DROP_LIMIT,
                'batch_limit': FIDELITY_BATCH_LIMIT,
                'max_retries': FIDELITY_MAX_RETRIES,
                'quality_ceiling': FIDELITY_QUALITY_CEILING,
                'supersample_ceiling': FIDELITY_SUPERSAMPLE_CEILING,
                'mean_drop': round(mean_drop, 2),
                'passed': not keep,
                'action': 'keep_original' if keep else 'replace',
                'keep_original': [r['label'] for r in records if not r['passed']],
            },
            'images': records,
        }
        write_json_report(report_path, payload)
        print(f'  报告：{report_path}（机器可读；CI 用退出码判、读这个文件拿原因，不用解析上面的文本）')
    if failed:
        print(f'清晰度强校验没通过：{len(failed)} 张。产物已生成，但这几张的结论是保留原图、不要替换。',
              file=sys.stderr)
        for src, dst, fmt, reasons, attempts in failed:
            print(f'  - {attempt_label(src, dst)}：{describe_attempt(attempts[-1], fmt, args)}',
                  file=sys.stderr)
            print('      压缩不成功的原因：' + '；'.join(reasons), file=sys.stderr)
        print('  处理：先别替换这几张；要更清晰只能把导出尺寸再往上抬、换更大的素材，'
              '或用真实浏览器截图目视复核一次（这个指标对高细节素材偏保守）。', file=sys.stderr)
    elif mean_drop < FIDELITY_BATCH_LIMIT:
        print(f'清晰度强校验没通过：整批均值 {mean_drop:+.1f}% 落进 verify 的偏糊区间'
              f'（低于 {FIDELITY_BATCH_LIMIT:.1f}%），各图都已升到上限，建议整体保留原图。',
              file=sys.stderr)
    if undersized:
        shown = '、'.join(undersized[:3]) + (' 等' if len(undersized) > 3 else '')
        print(f'注意：{len(undersized)} 张图源分辨率不足（{shown}）：宽度小于目标 {cap_w}px，'
              '脚本不会放大，输出会停在源图分辨率。这类图压缩救不了，只能换更大的素材。',
              file=sys.stderr)
    if same_format_lossy and saved < 15:
        print(f'注意：{same_format_lossy} 张图的源格式就是 {args.format}，本次属于有损重编码：'
              f'整批只省了 {saved:.0f}%，却要多掉一次画质。建议保留原图，或改用 --lossless 再评估。',
              file=sys.stderr)
    if grew:
        shown = '、'.join(grew[:3]) + (' 等' if len(grew) > 3 else '')
        print(f'注意：{len(grew)} 张图压缩后反而变大（{shown}）。这些文件应保留原图，不要替换。',
              file=sys.stderr)
    if saved < 0:
        print(
            f'警告：产物总体积比源文件大 {abs(saved):.0f}%，这批图不该按当前参数处理，请如实告诉用户而不是交付。\n'
            '  常见原因：源图已经是 WebP（重复编码会变大）、纯色 / 线条 / 截图类转成了有损格式、'
            '或"保持原格式"只做裁剪。\n'
            '  建议：换参数（去掉 --format keep、只降尺寸不裁剪、改用 --lossless），'
            '或直接保留原图并把原因说明白。',
            file=sys.stderr,
        )
    elif saved < 5:
        print(
            f'注意：体积只降了 {saved:.0f}%，收益很小。若源图已是 WebP、像素数又已经贴着显示尺寸，'
            '继续压没有意义——告诉用户现状，不要为了交差而替换。',
            file=sys.stderr,
        )
    if transposed:
        print(f'注意：{transposed} 张带 EXIF 方向标记，已按浏览器显示方向转正后再裁剪（产物不再带方向标记）')
    if flattened:
        print(f'注意：{flattened} 张带透明通道，转 JPEG 已按 --flatten-color（{args.flatten_color}）合成底色')
    if args.format == 'jpeg' and args.lossless:
        print('注意：JPEG 不支持无损，--lossless 已忽略（用 --format webp 才能无损；'
              'Pillow 的 AVIF 也不支持无损）')
    if failed or mean_drop < FIDELITY_BATCH_LIMIT:
        print(f'退出码 {EXIT_FIDELITY}：清晰度强校验没通过——这不是命令失败，产物已在 {out_dir} 里生成，'
              '只是结论为"保留原图"（报告里标 ✗ 的那几张）；别靠猜参数反复重跑，把原因说明白即可。',
              file=sys.stderr)
        print(f'输出目录：{out_dir}（子目录结构已复刻；替换前先备份原图，并重建产物）')
        return EXIT_FIDELITY
    print(f'输出目录：{out_dir}（子目录结构已复刻；替换前先备份原图，并重建产物）')
    return EXIT_OK


def cmd_doctor(args: argparse.Namespace) -> int:
    """检查运行环境：Pillow 与各格式编解码器是否可用。"""
    print(f'系统 {platform.system()} {platform.release()}（{platform.machine()}）')
    print(f'Python {platform.python_version()}')
    print(f'解释器 {sys.executable}')
    print(f'Pillow {PIL.__version__}')
    print('图像格式支持：')
    for label, key, hint in (
        ('WebP', 'webp', ''),
        ('AVIF', 'avif', '（需要 Pillow ≥ 11 且带 libavif；可 pip3 install --upgrade Pillow）'),
        ('JPEG', 'jpg', ''),
        ('PNG(zlib)', 'zlib', ''),
    ):
        ok = features.check(key)
        version = features.version(key) if ok else '—'
        print(f'  {"✓" if ok else "✗"} {label:<10} {version} {hint if not ok else ""}')
    print('能力提示：无损只有 webp / png 可用；Pillow 的 AVIF 编码器不支持无损（确需无损请用外部 avifenc）。')
    print('可选的外部工具（本脚本不依赖，仅作替代实现参考）：')
    for tool, note in (
        ('cwebp', 'libwebp 官方 CLI，批量转 WebP 更快'),
        ('avifenc', 'libavif 官方 CLI，能真正做无损 AVIF'),
        ('magick', 'ImageMagick，批量处理方便'),
        ('ffmpeg', '注意：macOS 上的常见构建不含 libwebp 编码器'),
        ('sips', 'macOS 自带，但不支持 WebP（Windows 上没有这个工具）'),
    ):
        path = shutil.which(tool)
        print(f'  {"✓" if path else "✗"} {tool:<9} {path or "未安装":<28} {note}')
    print()
    print('结论：上面四项格式都 ✓ 即可正常使用 analyze / export / verify；缺 Pillow 时按启动提示安装。')
    print('提示：脚本本身跨平台（macOS / Linux / Windows 都行）；Windows 上用 py -3 代替 python3，')
    print('      路径写反斜杠或正斜杠都可以，含空格的路径用引号包起来。')
    return EXIT_OK


def cmd_verify(args: argparse.Namespace) -> int:
    # 按“相对路径（不含扩展名）”配对：转格式后 a.jpeg → a.webp 能配上，
    # 不同子目录的同名文件也不会互相配错。
    refs: dict[str, Path] = {}
    duplicate_refs: list[str] = []
    for path, root in collect_images([args.reference]):
        key = str(path.relative_to(root).with_suffix(''))
        if key in refs:
            duplicate_refs.append(f'{display_name(refs[key])} 与 {display_name(path)}')
        else:
            refs[key] = path
    candidates = collect_images([args.candidate])
    cand_keys: dict[str, Path] = {}
    for path, root in candidates:
        cand_keys.setdefault(str(path.relative_to(root).with_suffix('')), path)

    pairs = [(refs[key], path) for key, path in cand_keys.items() if key in refs]
    unpaired_refs = [str(p) for key, p in refs.items() if key not in cand_keys]
    unpaired_cands = [str(p) for key, p in cand_keys.items() if key not in refs]
    if not pairs:
        print('两边没有可配对的文件（按相对路径配对，例如 assets/hero.jpg ↔ out/hero.webp）', file=sys.stderr)
        return EXIT_USAGE
    if duplicate_refs:
        print('注意：参考侧存在同名不同扩展名的文件，只取第一个参与比对：'
              + '、'.join(duplicate_refs), file=sys.stderr)
    if unpaired_refs:
        print('注意：以下参考图没有对应候选，未参与统计：' + '、'.join(unpaired_refs), file=sys.stderr)
    if unpaired_cands:
        print('注意：以下候选没有对应参考（可能是上一次导出的陈旧产物或手工放进去的文件），未参与统计：'
              + '、'.join(unpaired_cands), file=sys.stderr)

    box = resolve_box(args)
    device = (round(box[0] * args.dpr), round(box[1] * args.dpr))
    print(f'渲染尺寸 {device[0]}x{device[1]}（= 显示框 × DPR）；边缘能量越接近参考越清晰')
    print(f'{"文件":<34}{"参考边缘":>9}{"候选边缘":>9}{"变化":>8}{"像素差":>8}{"候选体积":>12}')
    deltas: list[float] = []
    total_ref_bytes = total_cand_bytes = 0
    total_ref_px = total_cand_px = 0
    for ref_path, cand_path in pairs:
        with Image.open(ref_path) as r, Image.open(cand_path) as c:
            ref_px = r.size[0] * r.size[1]
            cand_px = c.size[0] * c.size[1]
        e_ref, e_cand, diff = compare_render(ref_path, cand_path, device)
        total_ref_bytes += ref_path.stat().st_size
        total_cand_bytes += cand_path.stat().st_size
        total_ref_px += ref_px
        total_cand_px += cand_px
        delta = drop_pct(e_ref, e_cand)
        deltas.append(delta)
        if delta < -5:
            flag = '  ← 有发糊风险'
        else:
            flag = ''
        label = attempt_label(ref_path, cand_path)
        print(f'{label:<34}{e_ref:>9.2f}{e_cand:>9.2f}{delta:>7.1f}%{diff:>8.2f}'
              f'{kb(cand_path.stat().st_size):>12}{flag}')
    mean_delta = sum(deltas) / len(deltas)
    saved = (1 - total_cand_bytes / total_ref_bytes) * 100 if total_ref_bytes else 0.0
    print()
    print(f'体积合计：参考 {kb(total_ref_bytes)} → 候选 {kb(total_cand_bytes)}（下降 {saved:.0f}%）；'
          f'解码内存合计：{decoded_mb(total_ref_px)} → {decoded_mb(total_cand_px)}')
    print(f'整批平均边缘能量变化：{mean_delta:+.1f}%（逐图噪声约 ±1.5%，结论看均值）')
    print('说明：该指标是与“源图单步降采样”的理想结果比，偏保守；均值达标但个别图偏软时，')
    print('      再用真实浏览器截图目视比对一次即可放心。export 已内置同一套判据'
          f'（逐图下降超过 {abs(FIDELITY_DROP_LIMIT):.1f}% 会当场升档重压），此处用于复核或比对已有产物。')
    if mean_delta < -3.5:
        print('结论：候选偏糊，回到 export 提高 --supersample 或 --quality 后重验。')
    elif mean_delta < -2.5:
        print('结论：临界区间，细节丰富的图片可能被看出差别，建议升一档再比对。')
    else:
        print('结论：清晰度与参考基本一致，可以替换。')
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='图片工具箱：按显示尺寸导出并验证清晰度')
    sub = parser.add_subparsers(dest='command', required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument('paths', nargs='+', help='图片文件或目录（目录递归，保留子目录结构）')
        p.add_argument('--box', type=parse_box, default=None,
                       help='显示尺寸（CSS px），例如 240x108；不指定会按 240x108 占位并提示')
        p.add_argument('--dpr', type=positive_float, default=2, help='目标设备像素比，默认 2')

    p_doctor = sub.add_parser('doctor', help='检查运行环境与依赖（缺依赖时先跑这个）')
    p_doctor.set_defaults(func=cmd_doctor)

    p_analyze = sub.add_parser('analyze', help='体检现有图片')
    add_common(p_analyze)
    p_analyze.set_defaults(func=cmd_analyze)

    p_export = sub.add_parser(
        'export', help='按显示尺寸导出候选',
        epilog=f'清晰度强校验：导出后逐图比对候选与源图的渲染效果，单图边缘能量下降超过 '
               f'{abs(FIDELITY_DROP_LIMIT):.1f}% 判失真，最多再换 {FIDELITY_MAX_RETRIES} 个方案'
               f'（--quality 提到 {FIDELITY_QUALITY_CEILING}，再提 --supersample 到 '
               f'{FIDELITY_SUPERSAMPLE_CEILING}）；换完仍失真时在报告里标 ✗、打印原因并以退出码 '
               f'{EXIT_FIDELITY} 结束（产物保留，结论是保留原图）。',
    )
    add_common(p_export)
    p_export.add_argument('--out', required=True,
                          help='输出目录（必须独立于源目录；子目录结构会被复刻，绝不原地覆盖源图）')
    p_export.add_argument('--supersample', type=positive_float, default=2,
                          help='屏上像素宽的倍数：1 偏省、2 稳妥（默认）、3 最锐；体积随倍率上升')
    p_export.add_argument('--max-width', type=max_width_int, default=0,
                          help='直接指定宽度上限，覆盖 supersample')
    p_export.add_argument('--quality', type=quality_int, default=90,
                          help='有损质量 1~100（webp/avif/jpeg 通用），默认 90')
    p_export.add_argument('--lossless', action='store_true',
                          help='无损输出：只有 webp 有效（png 本身无损；avif 会被 Pillow 静默降级，故直接拒绝）')
    p_export.add_argument('--no-crop', action='store_true', help='不裁剪到显示比例，只缩放')
    p_export.add_argument('--no-resize', action='store_true', help='不改尺寸（只裁剪和/或转格式）')
    p_export.add_argument('--format', choices=['webp', 'avif', 'jpeg', 'png', 'keep'], default='webp',
                          help='输出格式，默认 webp；keep 表示保持源格式（只压缩/只裁剪时用）')
    p_export.add_argument('--flatten-color', type=flatten_color_arg, default='#000000',
                          help='透明图转 JPEG 时合成的底色，默认黑色')
    p_export.add_argument('--report-json', default=None, metavar='PATH',
                          help='把导出结论写成机器可读的 JSON（逐图档位链 / 掉多少 / pass 或 keep / 原因），'
                               '给 CI 读；目录不存在会自动创建')
    p_export.set_defaults(func=cmd_export)

    p_verify = sub.add_parser('verify', help='对比候选与参考的清晰度')
    p_verify.add_argument('reference', help='参考：原图文件或目录')
    p_verify.add_argument('candidate', help='候选：导出目录')
    p_verify.add_argument('--box', type=parse_box, default=None)
    p_verify.add_argument('--dpr', type=positive_float, default=2)
    p_verify.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    force_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
