#!/usr/bin/env python3
"""前向测试夹具：造一个真实感的 Web 前端图片项目。

目前只提供一种夹具（`web_image_project`），够覆盖图片处理类 skill 的场景。
要测别的类型，在这里加一个 build_* 函数，并在 BUILDERS 里注册。
"""
from __future__ import annotations

import shutil
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(f'夹具依赖 Pillow：{exc}\n安装：python3 -m pip install --user Pillow\n')


def texture(size: tuple[int, int]) -> Image.Image:
    """照片型素材：高频噪声 + 规则线条，用来暴露"压糊"和摩尔纹。"""
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


def build_web_image_project(dst: Path) -> None:
    """四张典型素材：大照片、横向 banner、透明 logo、小图标，外加引用它们的 Vue 组件。"""
    (dst / 'src/assets/img').mkdir(parents=True, exist_ok=True)
    (dst / 'src/components').mkdir(parents=True, exist_ok=True)
    (dst / 'src/styles').mkdir(parents=True, exist_ok=True)

    texture((2848, 1600)).save(dst / 'src/assets/img/hero.jpg', quality=92)
    texture((1200, 800)).save(dst / 'src/assets/img/banner.jpg', quality=90)

    logo = Image.new('RGBA', (600, 600), (0, 0, 0, 0))
    logo.paste((0, 128, 255, 255), (80, 80, 520, 520))
    ImageDraw.Draw(logo).ellipse((200, 200, 400, 400), fill=(255, 255, 255, 255))
    logo.save(dst / 'src/assets/img/logo.png')

    texture((64, 64)).save(dst / 'src/assets/img/icon.png')

    (dst / 'src/styles/main.css').write_text(
        '\n'.join([
            '.hero {',
            '  display: block;',
            '  width: 240px;',
            '  height: 108px;',
            '  object-fit: cover;',
            '}',
            '',
            '.banner {',
            '  width: 600px;',
            '  height: 200px;',
            '  object-fit: cover;',
            '}',
            '',
        ]),
        encoding='utf-8',
    )
    (dst / 'src/components/Hero.vue').write_text(
        '\n'.join([
            '<script setup lang="ts">',
            "import heroUrl from '@/assets/img/hero.jpg'",
            "import bannerUrl from '@/assets/img/banner.jpg'",
            "import logoUrl from '@/assets/img/logo.png'",
            '</script>',
            '',
            '<template>',
            '  <img class="hero" :src="heroUrl" alt="" />',
            '  <img class="banner" :src="bannerUrl" alt="" />',
            '  <img class="logo" :src="logoUrl" alt="" />',
            '</template>',
            '',
        ]),
        encoding='utf-8',
    )
    (dst / 'package.json').write_text(
        '{\n  "name": "fixture-shop",\n  "scripts": { "build": "echo build-ok" }\n}\n',
        encoding='utf-8',
    )


BUILDERS = {
    'web_image_project': build_web_image_project,
}


def build(kind: str, dst: Path) -> None:
    if kind not in BUILDERS:
        raise SystemExit(f'未知夹具类型 {kind}，可选：{sorted(BUILDERS)}')
    if dst.exists():
        shutil.rmtree(dst)
    BUILDERS[kind](dst)
