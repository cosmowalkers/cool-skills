#!/usr/bin/env python3
"""image-optimize 的回归 + 可用性用例（只依赖 python3 + Pillow，不联网）。

跑法：
  python3 scripts/tests/test_optimize_images.py -v            # 全部（约 20~40 秒）
  python3 scripts/tests/test_optimize_images.py -v -k Safety  # 只跑某一组（unittest -k）

约定：
  * 夹具全部在临时目录里现造，不动仓库里的任何素材；
  * 用例在进程内调用 CLI（快），另有一个用例用子进程验证“能当命令跑”；
  * 设 WI_KEEP_FIXTURES=1 可保留临时目录，便于手工查看产物。
"""

import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFilter, features
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(f'用例依赖 Pillow：{exc}\n安装：python3 -m pip install --user Pillow\n')

SKILL_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = SKILL_ROOT / 'scripts' / 'optimize_images.py'
sys.path.insert(0, str(SCRIPT_PATH.parent))

import optimize_images as O  # noqa: E402  （路径注入后才能导入）

DEVICE_BOX = '240x108'
DEVICE_PX = (480, 216)


# --------------------------------------------------------------------------- #
# 夹具
# --------------------------------------------------------------------------- #
def _texture(size: tuple[int, int]) -> Image.Image:
    """造一张有高频细节的“照片”型素材（全部走 C 实现，够快）。"""
    noise = Image.effect_noise(size, 70)
    other = Image.effect_noise(size, 70)
    im = Image.merge('RGB', (noise, ImageChops.invert(noise), other))
    draw = ImageDraw.Draw(im)
    w, h = size
    for x in range(0, w, 37):
        draw.line([(x, 0), (x, h)], fill=(250, 250, 250), width=2)
    for y in range(0, h, 53):
        draw.line([(0, y), (w, y)], fill=(8, 8, 8), width=2)
    return im


def _chess(size: tuple[int, int], cell: int = 25) -> Image.Image:
    """高边缘能量素材（用来验证同名文件不会被错配）。"""
    im = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(im)
    for iy, y in enumerate(range(0, size[1], cell)):
        for ix, x in enumerate(range(0, size[0], cell)):
            if (ix + iy) % 2 == 0:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(0, 0, 0))
    return im


def _max_channel_diff(a: Image.Image, b: Image.Image) -> int:
    diff = ImageChops.difference(a.convert('RGBA'), b.convert('RGBA'))
    return max(hi for _lo, hi in diff.getextrema())


def _digest(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def _columns(line: str) -> list[float]:
    """取 verify 表格数据行的数值列：参考边缘 / 候选边缘 / 变化% / 像素差 / 体积KB。"""
    return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', line[34:])]


def _row(output: str, prefix: str) -> str:
    rows = [line for line in output.splitlines() if line.startswith(prefix)]
    if not rows:
        raise AssertionError(f'输出里没有 {prefix!r} 这一行：\n{output}')
    return rows[0]


def build_fixtures(root: Path) -> None:
    """造一套覆盖面够用的素材：尺寸 / 格式 / 透明 / ICC / EXIF 方向 / 重名。"""
    assets = root / 'assets'
    (assets / 'nested' / 'a').mkdir(parents=True)
    (assets / 'nested' / 'b').mkdir(parents=True)
    (root / 'empty').mkdir()
    (root / 'clash').mkdir()

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    exif = Image.Exif()
    exif[0x010F] = 'image-optimize-tests'  # Make
    exif[0x0112] = 1                           # Orientation

    _texture((1200, 675)).save(assets / 'hero.jpg', quality=92, exif=exif, icc_profile=icc)
    _texture((2000, 1125)).save(assets / 'huge.jpg', quality=92)   # 相对 480 屏上像素过采样 4 倍以上
    Image.new('RGB', (400, 400), (220, 40, 60)).save(assets / 'icon.png')
    logo = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
    ImageDraw.Draw(logo).ellipse([60, 60, 340, 340], fill=(30, 120, 220, 255))
    logo.save(assets / 'logo.png')
    _texture((800, 450)).save(assets / 'already.webp', quality=80)

    # 同名但内容天差地别：a 是棋盘（高频），b 是纯灰（低频）
    _chess((500, 500)).save(assets / 'nested' / 'a' / 'tile.png')
    Image.new('RGB', (500, 500), (128, 128, 128)).save(assets / 'nested' / 'b' / 'tile.png')

    # 像素 900x1600 + EXIF 方向 6：浏览器会显示成 1600x900
    rotated = Image.Exif()
    rotated[0x0112] = 6
    _texture((900, 1600)).save(root / 'rotated.jpg', quality=90, exif=rotated)

    Image.new('RGB', (800, 800), (200, 60, 60)).save(root / 'clash' / 'same.png')
    Image.new('RGB', (800, 800), (60, 60, 200)).save(root / 'clash' / 'same.jpg')


TMP_ROOT = Path(tempfile.mkdtemp(prefix='wi-tests-'))
ASSETS = TMP_ROOT / 'assets'
FIXTURE_SNAPSHOT: dict[str, str] = {}


def _snapshot_fixtures() -> dict[str, str]:
    """夹具目录里所有素材的指纹（不含用例自己的临时目录）。"""
    return {
        str(p.relative_to(TMP_ROOT)): _digest(p)
        for p in sorted(TMP_ROOT.rglob('*'))
        if p.is_file() and not p.relative_to(TMP_ROOT).parts[0].startswith('case-')
    }


def setUpModule() -> None:
    if not features.check('webp'):
        raise unittest.SkipTest('当前 Pillow 没有 WebP 支持，默认工作流（PNG/JPEG → WebP）无法验证')
    build_fixtures(TMP_ROOT)
    FIXTURE_SNAPSHOT.update(_snapshot_fixtures())
    print(f'\n夹具目录：{TMP_ROOT}')


def tearDownModule() -> None:
    """跑完所有用例后核对：任何用例都不得改动夹具素材（护栏用例的兜底断言）。"""
    current = _snapshot_fixtures()
    keep = bool(os.environ.get('WI_KEEP_FIXTURES'))
    if not keep:
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
    if current != FIXTURE_SNAPSHOT:
        missing = sorted(set(FIXTURE_SNAPSHOT) - set(current))
        added = sorted(set(current) - set(FIXTURE_SNAPSHOT))
        changed = sorted(k for k in current.keys() & FIXTURE_SNAPSHOT.keys()
                         if current[k] != FIXTURE_SNAPSHOT[k])
        raise AssertionError(
            f'夹具素材被用例改动了：缺失={missing} 新增={added} 内容变化={changed}\n'
            '（这条断言就是为了保证“导出绝不原地覆盖源文件”）'
        )
    if keep:
        print(f'保留夹具：{TMP_ROOT}')


# --------------------------------------------------------------------------- #
# 公用基类
# --------------------------------------------------------------------------- #
class CliTest(unittest.TestCase):
    """进程内调用 CLI，并给每个用例一个干净的输出目录。"""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix='case-', dir=str(TMP_ROOT)))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.out_dir = self.tmp / 'out'

    def cli(self, *args) -> tuple[int, str, str]:
        """返回 (退出码, stdout, stderr)；SystemExit 也算退出码。"""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = O.main([str(a) for a in args])
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        return code, out.getvalue(), err.getvalue()

    def ok(self, *args) -> tuple[str, str]:
        code, out, err = self.cli(*args)
        self.assertEqual(0, code, msg=f'期望成功，实际退出码 {code}\n命令：{args}\n{out}\n{err}')
        self.assertNotIn('Traceback', err, '成功路径不该有 traceback')
        return out, err

    def fails(self, *args, code: int = 2) -> tuple[str, str]:
        got, out, err = self.cli(*args)
        self.assertEqual(code, got, msg=f'期望退出码 {code}，实际 {got}\n命令：{args}\n{out}\n{err}')
        self.assertNotIn('Traceback', err, f'不该把 traceback 甩给用户：\n{err}')
        return out, err

    def export(self, *args, out_dir: Path | None = None) -> tuple[str, str]:
        return self.ok('export', *args, '--out', out_dir or self.out_dir)


# --------------------------------------------------------------------------- #
# doctor
# --------------------------------------------------------------------------- #
class TestDoctor(CliTest):
    def test_自检给出四种格式的支持情况(self) -> None:
        out, _ = self.ok('doctor')
        self.assertIn('Pillow', out)
        for label in ('WebP', 'AVIF', 'JPEG', 'PNG'):
            self.assertIn(label, out)
        self.assertRegex(out, r'[✓✗]')

    def test_说明无损能力边界(self) -> None:
        out, _ = self.ok('doctor')
        self.assertIn('无损', out)
        self.assertIn('avifenc', out)


# --------------------------------------------------------------------------- #
# analyze
# --------------------------------------------------------------------------- #
class TestAnalyze(CliTest):
    def test_给出屏上像素与推荐导出宽度(self) -> None:
        out, _ = self.ok('analyze', ASSETS, '--box', DEVICE_BOX, '--dpr', '2')
        self.assertIn('480x216', out)
        self.assertIn('960~1440', out)

    def test_过采样严重的图建议降档(self) -> None:
        out, _ = self.ok('analyze', ASSETS / 'huge.jpg', '--box', DEVICE_BOX)
        self.assertIn('过采样严重', out)

    def test_落在推荐区间的图给推荐结论(self) -> None:
        out, _ = self.ok('analyze', ASSETS / 'hero.jpg', '--box', DEVICE_BOX)
        self.assertIn('推荐区间', out)

    def test_接近一比一的图给保守提示(self) -> None:
        out, _ = self.ok('analyze', ASSETS / 'already.webp', '--box', DEVICE_BOX)
        self.assertIn('偏保守', out)

    def test_像素不足的图建议换源(self) -> None:
        out, _ = self.ok('analyze', ASSETS / 'icon.png', '--box', DEVICE_BOX)
        self.assertIn('像素不足', out)

    def test_解码内存按像素数计算(self) -> None:
        out, _ = self.ok('analyze', ASSETS / 'huge.jpg', '--box', DEVICE_BOX)
        self.assertIn('8.6 MB', out)  # 2000x1125x4 字节

    def test_递归扫描子目录并给合计(self) -> None:
        out, _ = self.ok('analyze', ASSETS, '--box', DEVICE_BOX)
        self.assertIn('nested', out)
        self.assertIn('合计', out)

    def test_空目录直接报错(self) -> None:
        _out, err = self.fails('analyze', TMP_ROOT / 'empty', '--box', DEVICE_BOX)
        self.assertIn('没有找到图片', err)

    def test_不存在的路径会提示跳过(self) -> None:
        _out, err = self.ok('analyze', ASSETS / 'icon.png', TMP_ROOT / '不存在', '--box', DEVICE_BOX)
        self.assertIn('跳过不存在的路径', err)

    def test_带EXIF方向的图按浏览器显示尺寸报告(self) -> None:
        out, _ = self.ok('analyze', TMP_ROOT / 'rotated.jpg', '--box', DEVICE_BOX)
        self.assertIn('1600x900', out)   # 像素是 900x1600，方向 6 之后显示为 1600x900
        self.assertIn('EXIF 方向', out)

    def test_非法dpr给出中文错误而不是traceback(self) -> None:
        _out, err = self.fails('analyze', ASSETS, '--dpr', '0')
        self.assertIn('必须大于 0', err)


# --------------------------------------------------------------------------- #
# export —— 功能
# --------------------------------------------------------------------------- #
class TestExportBasics(CliTest):
    def test_默认组合_裁剪加缩尺寸加转webp(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--box', DEVICE_BOX)
        dst = self.out_dir / 'hero.webp'
        self.assertTrue(dst.exists())
        with Image.open(dst) as im:
            self.assertEqual('WEBP', im.format)
            self.assertEqual((960, 432), im.size)  # 480 x supersample 2

    def test_默认按显示框比例裁剪(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--box', DEVICE_BOX)
        with Image.open(self.out_dir / 'hero.webp') as im:
            self.assertAlmostEqual(240 / 108, im.size[0] / im.size[1], places=2)

    def test_比目标窄的源图不会被放大(self) -> None:
        self.export(ASSETS / 'icon.png', '--box', DEVICE_BOX)
        with Image.open(self.out_dir / 'icon.webp') as im:
            self.assertEqual((400, 180), im.size)  # 400x400 裁到 2.222:1，不放大

    def test_只转格式时尺寸不变(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--no-crop', '--no-resize')
        with Image.open(self.out_dir / 'hero.webp') as im:
            self.assertEqual((1200, 675), im.size)
            self.assertEqual('WEBP', im.format)

    def test_只压尺寸时不裁剪(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--no-crop', '--max-width', '600')
        with Image.open(self.out_dir / 'hero.webp') as im:
            self.assertEqual((600, 338), im.size)  # 比例保持，round(675*600/1200)

    def test_只裁剪时分辨率不变(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--no-resize', '--box', DEVICE_BOX)
        with Image.open(self.out_dir / 'hero.webp') as im:
            self.assertEqual((1200, 540), im.size)

    def test_format_keep保留源扩展名与格式(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--format', 'keep', '--no-crop', '--max-width', '600')
        dst = self.out_dir / 'hero.jpg'
        self.assertTrue(dst.exists())
        with Image.open(dst) as im:
            self.assertEqual('JPEG', im.format)

    def test_输出jpeg与png格式正确(self) -> None:
        for fmt, ext, expected in (('jpeg', '.jpg', 'JPEG'), ('png', '.png', 'PNG')):
            with self.subTest(fmt=fmt):
                out_dir = self.out_dir / fmt
                self.export(ASSETS / 'hero.jpg', '--format', fmt,
                            '--no-crop', '--max-width', '320', out_dir=out_dir)
                with Image.open(out_dir / f'hero{ext}') as im:
                    self.assertEqual(expected, im.format)

    @unittest.skipUnless(features.check('avif'), '当前 Pillow 没有 AVIF 支持')
    def test_输出avif格式正确(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--format', 'avif', '--quality', '60',
                    '--no-crop', '--max-width', '320')
        with Image.open(self.out_dir / 'hero.avif') as im:
            self.assertEqual('AVIF', im.format)

    def test_无损webp逐像素一致(self) -> None:
        self.export(ASSETS / 'logo.png', '--lossless', '--no-crop', '--no-resize')
        with Image.open(ASSETS / 'logo.png') as src, Image.open(self.out_dir / 'logo.webp') as dst:
            self.assertEqual('WEBP', dst.format)
            self.assertEqual(0, _max_channel_diff(src, dst), '--lossless 必须是真正的无损')

    def test_质量参数影响体积(self) -> None:
        for quality in ('30', '90'):
            self.export(ASSETS / 'hero.jpg', '--quality', quality,
                        '--no-crop', '--no-resize', out_dir=self.out_dir / f'q{quality}')
        small = (self.out_dir / 'q30' / 'hero.webp').stat().st_size
        big = (self.out_dir / 'q90' / 'hero.webp').stat().st_size
        self.assertLess(small, big)

    def test_透明图转jpeg会合成底色并提示(self) -> None:
        out, _ = self.export(ASSETS / 'logo.png', '--format', 'jpeg', '--no-crop', '--no-resize')
        self.assertIn('--flatten-color', out)
        with Image.open(self.out_dir / 'logo.jpg') as im:
            self.assertEqual('RGB', im.mode)

    def test_输出目录会被自动创建(self) -> None:
        deep = self.tmp / 'deep' / 'deeper'
        self.export(ASSETS / 'icon.png', out_dir=deep)
        self.assertTrue((deep / 'icon.webp').exists())

    def test_打印体积与解码内存收益(self) -> None:
        out, _ = self.export(ASSETS / 'hero.jpg', '--box', DEVICE_BOX)
        self.assertIn('体积下降', out)
        self.assertIn('解码内存', out)

    def test_子目录结构被复刻(self) -> None:
        self.export(ASSETS / 'nested')
        self.assertTrue((self.out_dir / 'a' / 'tile.webp').exists())
        self.assertTrue((self.out_dir / 'b' / 'tile.webp').exists())

    def test_保留icc色彩描述(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--no-crop', '--no-resize')
        with Image.open(ASSETS / 'hero.jpg') as src, Image.open(self.out_dir / 'hero.webp') as dst:
            self.assertTrue(src.info.get('icc_profile'), '夹具本身要带 ICC')
            self.assertEqual(src.info['icc_profile'], dst.info.get('icc_profile'),
                             '丢 ICC 会让 Display-P3 素材在浏览器里偏色')

    def test_保留exif元数据(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--format', 'jpeg', '--no-crop', '--no-resize')
        with Image.open(self.out_dir / 'hero.jpg') as dst:
            self.assertEqual('image-optimize-tests', dst.getexif().get(0x010F))

    def test_带EXIF方向的图先转正再导出(self) -> None:
        out, _ = self.export(TMP_ROOT / 'rotated.jpg', '--no-crop', '--no-resize')
        with Image.open(self.out_dir / 'rotated.webp') as dst:
            self.assertEqual((1600, 900), dst.size, '方向 6 的 900x1600 素材要按显示方向转正')
            self.assertIsNone(dst.getexif().get(0x0112), '转正后不能再留方向标记')
        self.assertIn('EXIF 方向', out)

    def test_带EXIF方向的图按转正后的比例裁剪(self) -> None:
        self.export(TMP_ROOT / 'rotated.jpg', '--box', DEVICE_BOX)
        with Image.open(self.out_dir / 'rotated.webp') as dst:
            self.assertEqual((960, 432), dst.size)  # 未转正会得到 900x405


# --------------------------------------------------------------------------- #
# export —— 安全护栏（这四条是回归用例）
# --------------------------------------------------------------------------- #
class TestExportSafety(CliTest):
    def test_拒绝把产物写回源目录(self) -> None:
        for name, extra in (
            ('hero.jpg', ['--format', 'keep', '--no-crop', '--no-resize']),
            ('already.webp', []),  # 默认 webp + 已 webp 源：以前会原地重编码
        ):
            with self.subTest(name=name):
                src = ASSETS / name
                before, before_size = _digest(src), src.stat().st_size
                _out, err = self.fails('export', src, '--out', ASSETS, *extra)
                self.assertIn('重合', err)
                self.assertEqual(before, _digest(src), '源文件内容必须一字不改')
                self.assertEqual(before_size, src.stat().st_size)

    def test_拒绝整目录导出到自身(self) -> None:
        before = {p: _digest(p) for p in ASSETS.rglob('*') if p.is_file()}
        _out, err = self.fails('export', ASSETS, '--out', ASSETS)
        self.assertIn('源文件没有任何改动', err)
        self.assertEqual(before, {p: _digest(p) for p in ASSETS.rglob('*') if p.is_file()})

    def test_同名冲突整体中止且不留半个批次(self) -> None:
        _out, err = self.fails('export', TMP_ROOT / 'clash', '--out', self.out_dir)
        self.assertIn('同一个文件', err)
        self.assertFalse(self.out_dir.exists(), '预检失败时不该创建输出目录')

    def test_不同子目录的同名图各自保留(self) -> None:
        self.export(ASSETS / 'nested')
        a, b = self.out_dir / 'a' / 'tile.webp', self.out_dir / 'b' / 'tile.webp'
        self.assertTrue(a.exists() and b.exists(), '同名不同目录必须各自输出')
        with Image.open(a) as ia, Image.open(b) as ib:
            self.assertGreater(_max_channel_diff(ia, ib), 50, '两张图的像素不该互相覆盖')

    def test_一次传多个目录时用目录名做前缀(self) -> None:
        self.export(ASSETS / 'nested' / 'a', ASSETS / 'nested' / 'b')
        a, b = self.out_dir / 'a' / 'tile.webp', self.out_dir / 'b' / 'tile.webp'
        self.assertTrue(a.exists() and b.exists(), '两个目录目标不该因为同名而互相撞')
        with Image.open(a) as ia, Image.open(b) as ib:
            self.assertGreater(_max_channel_diff(ia, ib), 50)

    def test_输出目录在源目录之内会警告(self) -> None:
        inside = ASSETS / 'optimized'
        self.addCleanup(shutil.rmtree, inside, ignore_errors=True)
        _out, err = self.export(ASSETS / 'icon.png', out_dir=inside)
        self.assertIn('位于输入目录', err)

    def test_avif无损被拒绝而不是静默降级(self) -> None:
        _out, err = self.fails('export', ASSETS / 'hero.jpg', '--out', self.out_dir,
                               '--format', 'avif', '--lossless')
        self.assertIn('无损', err)
        self.assertIn('avifenc', err)
        self.assertFalse(self.out_dir.exists())

    @unittest.skipUnless(features.check('avif'), '当前 Pillow 没有 AVIF 支持')
    def test_avif有损输出仍然可用(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--format', 'avif', '--quality', '70',
                    '--no-crop', '--max-width', '320')
        self.assertTrue((self.out_dir / 'hero.avif').exists())

    def test_参数越界都给中文错误且不建目录(self) -> None:
        cases = (
            ('--dpr', '0'),
            ('--quality', '200'),
            ('--quality', '0'),
            ('--supersample', '0'),
            ('--max-width', '-1'),
            ('--box', '4000x1'),
            ('--box', 'wide'),
            ('--flatten-color', '不是颜色'),
            ('--format', 'bmp'),
        )
        for flag, value in cases:
            with self.subTest(flag=flag, value=value):
                _out, err = self.fails('export', ASSETS / 'icon.png',
                                       '--out', self.out_dir, flag, value)
                self.assertTrue(err.strip(), '必须给出人能看懂的提示')
                self.assertFalse(self.out_dir.exists(), '参数非法时不该产出任何文件')

# --------------------------------------------------------------------------- #
# verify
# --------------------------------------------------------------------------- #
class TestVerify(CliTest):
    def test_跨扩展名按相对路径配对(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--box', DEVICE_BOX)
        out, err = self.ok('verify', ASSETS / 'hero.jpg', self.out_dir, '--box', DEVICE_BOX)
        self.assertIn('hero.jpg→hero.webp', out)
        self.assertIn('结论', out)
        self.assertNotIn('没有对应', err)

    def test_子目录同名文件不会错配(self) -> None:
        self.export(ASSETS / 'nested', '--box', DEVICE_BOX)
        out, err = self.ok('verify', ASSETS / 'nested', self.out_dir, '--box', DEVICE_BOX)
        self.assertNotIn('没有对应', err)
        rows = [line for line in out.splitlines() if line.startswith('tile.png→tile.webp')]
        self.assertEqual(2, len(rows), f'两张同名图都要参与比对：\n{out}')
        self.assertLess(max(_columns(line)[3] for line in rows), 50,
                        '配错对（棋盘 vs 纯灰）会得到上百的像素差')

    def test_未配对的候选会被点名(self) -> None:
        self.export(ASSETS / 'icon.png', '--box', DEVICE_BOX)
        shutil.copyfile(ASSETS / 'already.webp', self.out_dir / 'stale.webp')
        _out, err = self.ok('verify', ASSETS / 'icon.png', self.out_dir, '--box', DEVICE_BOX)
        self.assertIn('stale.webp', err)
        self.assertIn('没有对应参考', err)

    def test_未配对的参考图会被点名(self) -> None:
        self.export(ASSETS / 'icon.png', '--box', DEVICE_BOX)
        _out, err = self.ok('verify', ASSETS, self.out_dir, '--box', DEVICE_BOX)
        self.assertIn('没有对应候选', err)

    def test_毫无交集时直接报错(self) -> None:
        other = self.tmp / 'other'
        other.mkdir()
        shutil.copyfile(ASSETS / 'already.webp', other / 'nothing.webp')
        _out, err = self.fails('verify', ASSETS / 'icon.png', other, '--box', DEVICE_BOX)
        self.assertIn('没有可配对', err)

    def test_发糊候选被标出来(self) -> None:
        blur = self.tmp / 'blur'
        blur.mkdir()
        with Image.open(ASSETS / 'hero.jpg') as im:
            im.resize((960, 432), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6)).save(
                blur / 'hero.webp', quality=30)
        out, _ = self.ok('verify', ASSETS / 'hero.jpg', blur, '--box', DEVICE_BOX)
        self.assertIn('有发糊风险', out)
        self.assertIn('候选偏糊', out)

    def test_无损候选判定为基本一致(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--lossless', '--no-crop', '--no-resize')
        out, _ = self.ok('verify', ASSETS / 'hero.jpg', self.out_dir, '--box', DEVICE_BOX)
        self.assertEqual(0.0, _columns(_row(out, 'hero.jpg→hero.webp'))[3])
        self.assertIn('基本一致', out)

    def test_带EXIF方向的图不会被误判(self) -> None:
        self.export(TMP_ROOT / 'rotated.jpg', '--lossless', '--no-crop', '--max-width', '600')
        out, _ = self.ok('verify', TMP_ROOT / 'rotated.jpg', self.out_dir, '--box', DEVICE_BOX)
        self.assertLess(_columns(_row(out, 'rotated.jpg→rotated.webp'))[3], 5.0,
                        '源图有 EXIF 方向时必须按浏览器显示方向比对，否则会算出巨大差异')
        self.assertNotIn('有发糊风险', out)

    def test_渲染尺寸跟随参数(self) -> None:
        self.export(ASSETS / 'hero.jpg', '--box', '300x150', '--dpr', '3')
        out, _ = self.ok('verify', ASSETS / 'hero.jpg', self.out_dir, '--box', '300x150', '--dpr', '3')
        self.assertIn('900x450', out)


# --------------------------------------------------------------------------- #
# CLI 可用性
# --------------------------------------------------------------------------- #
class TestCliUsability(CliTest):
    def test_主帮助列出全部子命令(self) -> None:
        out, _ = self.ok('-h')
        for name in ('analyze', 'export', 'verify', 'doctor'):
            self.assertIn(name, out)

    def test_导出帮助写明安全约束与无损边界(self) -> None:
        out, _ = self.ok('export', '-h')
        self.assertIn('独立于源目录', out)
        self.assertIn('无损', out)

    def test_不带子命令时给用法而不是traceback(self) -> None:
        _out, err = self.fails()
        self.assertIn('usage', err.lower())

    def test_错误提示是中文且指明写法(self) -> None:
        _out, err = self.fails('export', ASSETS / 'icon.png', '--out', self.out_dir, '--box', 'wide')
        self.assertIn('宽x高', err)

    def test_脚本可以直接当命令跑(self) -> None:
        proc = subprocess.run([sys.executable, str(SCRIPT_PATH), 'doctor'],
                              capture_output=True, text=True, timeout=180)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn('Pillow', proc.stdout)


# --------------------------------------------------------------------------- #
# 文档与实现一致（发给别人用之前别让文档漂移）
# --------------------------------------------------------------------------- #
class TestDocs(unittest.TestCase):
    def _text(self, name: str) -> str:
        return (SKILL_ROOT / name).read_text(encoding='utf-8')

    def test_不再宣传avif无损(self) -> None:
        # 允许的写法是“明说 AVIF 不行 / 只能靠外部 avifenc / 真无损仅 webp+png”；
        # 命中即视为“还在宣传 AVIF 无损”。
        allowed = ('不支持', '无法', '拒绝', 'avifenc', '假无损', '仅 WebP')
        for name in ('SKILL.md', 'README.md'):
            for lineno, line in enumerate(self._text(name).splitlines(), 1):
                if 'avif' in line.lower() and ('无损' in line or 'lossless' in line.lower()):
                    self.assertTrue(
                        any(word in line for word in allowed),
                        f'{name}:{lineno} 仍在宣传 AVIF 无损：{line.strip()}',
                    )

    def test_脚本路径按可复用写法给出(self) -> None:
        for name in ('SKILL.md', 'README.md'):
            self.assertNotIn('python3 scripts/optimize_images.py', self._text(name),
                             f'{name} 里的脚本路径是相对路径，换到宿主项目就会指错文件')

    def test_文档提到这套用例(self) -> None:
        self.assertIn('test_optimize_images.py', self._text('SKILL.md'))

    def test_文档里没有业务或内部标识(self) -> None:
        """这是通用功能 skill：对外分发前不得出现公司 / 项目 / 内部系统标识。"""
        ascii_tokens = ('sugon', 'zentao', 'su-common', 'aui-common', 'console-ui',
                        'admin-ui', 'seller-ui', '@common', 'mall')
        cjk_tokens = ('曙光', '中科', '禅道', '公司', '部门', '内部系统', '本项目', '我们项目')
        for name in ('SKILL.md', 'README.md', 'evals/evals.json'):
            text = self._text(name)
            lowered = text.lower()
            for token in ascii_tokens:
                self.assertIsNone(
                    re.search(rf'(?<![a-z0-9-]){re.escape(token)}(?![a-z0-9-])', lowered),
                    f'{name} 里出现了业务/内部标识：{token}',
                )
            for token in cjk_tokens:
                self.assertNotIn(token, text, f'{name} 里出现了业务/内部标识：{token}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
