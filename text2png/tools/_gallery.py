#!/usr/bin/env python3
"""生成全矩阵画廊页：按形式/主题过滤 + 点击放大预览。

- 相对路径模式：index.html + img/<chart>__<style>.<ext>
- embed 模式：图片内联成 data URI，单文件可分发
"""
import base64
import html as htmllib
import pathlib

import _content as gen

charts = [c for c, _ in gen.CHARTS]
styles = list(gen.STYLES)
IMG_DIRNAME = "img"


def card_html(out_dir, chart_id, style_id, embed=False, img_ext="png"):
    name = f"{chart_id}__{style_id}.{img_ext}"
    path = out_dir / IMG_DIRNAME / name
    size_kb = path.stat().st_size // 1024 if path.exists() else 0
    if embed:
        if path.exists():
            mime = "image/webp" if img_ext == "webp" else "image/png"
            src = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
        else:
            src = ""
    else:
        stamp = f"?v={int(path.stat().st_mtime)}" if path.exists() else ""  # 缓存指纹
        src = f"{IMG_DIRNAME}/{name}{stamp}"
    prompt = (f"画成{gen.CHART_NAME[chart_id]}（{chart_id}），主题用 {style_id}"
              f"（{gen.STYLES[style_id]['label']}）：<把内容写在这里>")
    return f"""      <figure class="card" data-chart="{chart_id}" data-style="{style_id}">
        <img loading="lazy" src="{src}" alt="{gen.CHART_NAME[chart_id]} × {style_id}" title="点击放大预览">
        <figcaption><b>{gen.CHART_NAME[chart_id]}</b><span>{style_id} · {gen.STYLES[style_id]['label']}</span>
          <button class="copy" data-prompt="{htmllib.escape(prompt, quote=True)}">复制 prompt</button><em>{size_kb} KB</em></figcaption>
      </figure>"""


def build(out_dir, embed=False, img_ext="png"):
    sections = "\n".join(
        f"""  <section class="sec" data-chart="{chart_id}" id="chart-{chart_id}">
    <h2>{gen.CHART_NAME[chart_id]}<code>{chart_id}</code></h2>
    <div class="grid">
{chr(10).join(card_html(out_dir, chart_id, s, embed, img_ext) for s in styles)}
    </div>
  </section>""" for chart_id in charts)

    style_btns = "".join(f'<button data-filter-style="{s}">{s}</button>' for s in styles)
    chart_btns = "".join(f'<button data-filter-chart="{c}">{gen.CHART_NAME[c]}</button>' for c in charts)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>text2png：15 形式 × 9 主题 = {len(charts) * len(styles)}</title>
<style>
  :root {{ --line:#e5e7eb; --muted:#6b7280; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.6 -apple-system,"PingFang SC",system-ui,sans-serif; background:#fafafa; color:#111827; }}
  header {{ position:sticky; top:0; z-index:10; background:#fff; border-bottom:1px solid var(--line); padding:12px 20px; }}
  header h1 {{ margin:0 0 8px; font-size:18px; }}
  header p {{ margin:0; color:var(--muted); font-size:12.5px; }}
  .bar {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }}
  .bar button {{ font:12.5px/1 inherit; padding:6px 10px; border:1px solid var(--line); border-radius:999px; background:#fff; cursor:pointer; }}
  .bar button.on {{ background:#111827; color:#fff; border-color:#111827; }}
  .bar .sep {{ width:1px; background:var(--line); margin:0 4px; }}
  main {{ padding:20px; }}
  .sec {{ margin-bottom:28px; }}
  .sec h2 {{ font-size:15px; margin:0 0 10px; display:flex; align-items:center; gap:8px; }}
  .sec h2 code {{ font-size:12px; color:var(--muted); background:#f3f4f6; padding:1px 6px; border-radius:4px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:14px; }}
  .card {{ margin:0; background:#fff; border:1px solid var(--line); border-radius:10px; overflow:hidden; }}
  .card img {{ display:block; width:100%; height:auto; background:#fff; cursor:zoom-in; }}
  .card img:hover {{ outline:2px solid #2563eb; outline-offset:-2px; }}
  .card figcaption {{ display:flex; align-items:center; gap:8px; padding:8px 10px; font-size:12px; border-top:1px solid var(--line); }}
  .card figcaption b {{ font-weight:600; }}
  .card figcaption span {{ color:var(--muted); }}
  .card figcaption em {{ margin-left:auto; color:#9ca3af; font-style:normal; }}
  .card figcaption .copy {{ font:11.5px/1 inherit; padding:4px 8px; border:1px solid var(--line); border-radius:999px;
    background:#fff; color:#374151; cursor:pointer; }}
  .card figcaption .copy:hover {{ background:#111827; color:#fff; border-color:#111827; }}
  .card figcaption .copy.ok {{ background:#16a34a; color:#fff; border-color:#16a34a; }}
  .hidden {{ display:none !important; }}
  /* ── 放大预览 ── */
  #lb {{ position:fixed; inset:0; z-index:50; background:rgba(9,11,16,.92); display:none; flex-direction:column; }}
  #lb.open {{ display:flex; }}
  #lb-bar {{ display:flex; align-items:center; gap:8px; padding:10px 14px; color:#e5e7eb; font-size:13px;
    background:#0b0e14; border-bottom:1px solid rgba(255,255,255,.12); flex:0 0 auto; }}
  #lb-bar b {{ color:#fff; font-weight:600; }}
  #lb-bar .sp {{ flex:1; }}
  #lb-bar button {{ font:12.5px/1 inherit; padding:6px 10px; border:1px solid rgba(255,255,255,.24); border-radius:6px;
    background:rgba(255,255,255,.06); color:#e5e7eb; cursor:pointer; }}
  #lb-bar button:hover {{ background:rgba(255,255,255,.16); }}
  #lb-stage {{ flex:1; overflow:auto; padding:16px; display:flex; align-items:flex-start; justify-content:center; }}
  #lb-img {{ display:block; background:#fff; box-shadow:0 12px 40px rgba(0,0,0,.5); }}
  #lb-img.fit {{ max-width:100%; max-height:calc(100vh - 96px); width:auto; height:auto; }}
  #lb-img.zoom {{ max-width:none; max-height:none; }}
</style>
</head>
<body>
<header>
  <h1>text2png 全矩阵：{len(charts)} 种形式 × {len(styles)} 种主题 = {len(charts) * len(styles)} 张</h1>
  <p>选择器用法：挑中喜欢的组合 → 点「复制 prompt」→ 把内容替换进占位符，整行发给我即可。点图片可放大（适应 / 1:1 / 200% / 300%，←→ 翻页），上方按钮按形式或主题过滤。形式决定布局，主题决定配色、字体与质感。</p>
  <div class="bar">
    <button data-filter-all class="on">全部</button>
    <div class="sep"></div>
    {chart_btns}
    <div class="sep"></div>
    {style_btns}
  </div>
</header>
<main>
{sections}
</main>
<div id="lb" aria-hidden="true">
  <div id="lb-bar">
    <b id="lb-title">—</b>
    <span id="lb-count" style="color:#9ca3af"></span>
    <span id="lb-zoom-label" style="color:#9ca3af;min-width:38px">适应</span>
    <span class="sp"></span>
    <button data-zoom-out title="缩小（-）">−</button>
    <button data-zoom-in title="放大（+）">＋</button>
    <button data-zoom-fit title="适应屏幕（0）">适应</button>
    <button data-zoom-actual title="原始像素（1）">1:1</button>
    <button data-prev title="上一张（←）">←</button>
    <button data-next title="下一张（→）">→</button>
    <button data-copy-current title="复制当前组合的 prompt">复制 prompt</button>
    <button data-close title="关闭（Esc）">✕</button>
  </div>
  <div id="lb-stage"><img id="lb-img" class="fit" alt=""></div>
</div>
<script>
const cards = [...document.querySelectorAll('.card')];

function applyFilter(type, value) {{
  cards.forEach(card => {{
    const match = !value || card.dataset[type] === value;
    card.classList.toggle('hidden', !match);
  }});
  document.querySelectorAll('.sec').forEach(sec => {{
    const anyVisible = [...sec.querySelectorAll('.card')].some(c => !c.classList.contains('hidden'));
    sec.classList.toggle('hidden', !anyVisible);
  }});
}}

document.querySelectorAll('.bar button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.bar button').forEach(b => b.classList.remove('on'));
    btn.classList.add('on');
    if (btn.dataset.filterAll !== undefined) return applyFilter(null, null);
    if (btn.dataset.filterChart) return applyFilter('chart', btn.dataset.filterChart);
    if (btn.dataset.filterStyle) return applyFilter('style', btn.dataset.filterStyle);
  }});
}});

// ── 放大预览 ──
const lb = document.querySelector('#lb');
const lbImg = document.querySelector('#lb-img');
const lbTitle = document.querySelector('#lb-title');
const lbCount = document.querySelector('#lb-count');
const lbZoomLabel = document.querySelector('#lb-zoom-label');
const lbStage = document.querySelector('#lb-stage');
const ZOOMS = ['fit', 'actual', 2, 3];
let lbIndex = 0;
let zoomIdx = 0;
let currentPrompt = '';

const visibleCards = () => cards.filter(c => !c.classList.contains('hidden'));

function applyZoom() {{
  const mode = ZOOMS[zoomIdx];
  if (mode === 'fit') {{
    lbImg.className = 'fit';
    lbImg.style.width = '';
    lbZoomLabel.textContent = '适应';
  }} else if (mode === 'actual') {{
    lbImg.className = 'zoom';
    lbImg.style.width = 'auto';
    lbZoomLabel.textContent = '1:1';
  }} else {{
    lbImg.className = 'zoom';
    lbImg.style.width = `${{mode * 100}}%`;
    lbZoomLabel.textContent = `${{mode * 100}}%`;
  }}
}}

function showAt(index) {{
  const list = visibleCards();
  if (!list.length) return closeLb();
  lbIndex = (index + list.length) % list.length;
  const card = list[lbIndex];
  const img = card.querySelector('img');
  currentPrompt = card.querySelector('.copy')?.dataset.prompt || '';
  lbImg.src = img.getAttribute('src');
  lbImg.alt = img.alt;
  lbTitle.textContent = img.alt;
  lbCount.textContent = `${{lbIndex + 1}} / ${{list.length}}`;
  zoomIdx = 0;
  applyZoom();
  lbStage.scrollTop = 0;
  lbStage.scrollLeft = 0;
}}

function openLb(card) {{
  const index = visibleCards().indexOf(card);
  if (index < 0) return;
  lb.classList.add('open');
  lb.setAttribute('aria-hidden', 'false');
  showAt(index);
}}

function closeLb() {{
  lb.classList.remove('open');
  lb.setAttribute('aria-hidden', 'true');
  lbImg.removeAttribute('src');
}}

cards.forEach(card => card.querySelector('img').addEventListener('click', () => openLb(card)));

// 复制 prompt：优先用 Clipboard API，失败（file:// 或无权限）时退化为 textarea + execCommand
async function copyPrompt(text, btn) {{
  if (!text) return;
  const flash = () => {{
    const old = btn.textContent;
    btn.textContent = '已复制 ✓';
    btn.classList.add('ok');
    setTimeout(() => {{ btn.textContent = old; btn.classList.remove('ok'); }}, 1600);
  }};
  try {{
    if (navigator.clipboard && window.isSecureContext) {{
      await navigator.clipboard.writeText(text);
      flash();
      return;
    }}
    throw new Error('clipboard unavailable');
  }} catch (e) {{
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    ta.remove();
    if (ok) flash();
    else window.prompt('自动复制失败，请手动复制这行：', text);
  }}
}}

cards.forEach(card => {{
  const btn = card.querySelector('.copy');
  if (btn) btn.addEventListener('click', e => {{
    e.stopPropagation();          // 别触发图片的放大预览
    copyPrompt(btn.dataset.prompt || '', btn);
  }});
}});

lb.querySelector('[data-copy-current]').addEventListener('click', e => {{
  copyPrompt(currentPrompt, e.currentTarget);
}});

lb.querySelector('[data-close]').addEventListener('click', closeLb);
lb.querySelector('[data-prev]').addEventListener('click', () => showAt(lbIndex - 1));
lb.querySelector('[data-next]').addEventListener('click', () => showAt(lbIndex + 1));
lb.querySelector('[data-zoom-in]').addEventListener('click', () => {{ zoomIdx = Math.min(ZOOMS.length - 1, zoomIdx + 1); applyZoom(); }});
lb.querySelector('[data-zoom-out]').addEventListener('click', () => {{ zoomIdx = Math.max(0, zoomIdx - 1); applyZoom(); }});
lb.querySelector('[data-zoom-fit]').addEventListener('click', () => {{ zoomIdx = 0; applyZoom(); }});
lb.querySelector('[data-zoom-actual]').addEventListener('click', () => {{ zoomIdx = 1; applyZoom(); }});
lb.addEventListener('click', e => {{ if (e.target === lb || e.target === lbStage) closeLb(); }});
document.addEventListener('keydown', e => {{
  if (!lb.classList.contains('open')) return;
  if (e.key === 'Escape') closeLb();
  else if (e.key === 'ArrowRight') showAt(lbIndex + 1);
  else if (e.key === 'ArrowLeft') showAt(lbIndex - 1);
  else if (e.key === '+' || e.key === '=') {{ zoomIdx = Math.min(ZOOMS.length - 1, zoomIdx + 1); applyZoom(); }}
  else if (e.key === '-') {{ zoomIdx = Math.max(0, zoomIdx - 1); applyZoom(); }}
  else if (e.key === '0') {{ zoomIdx = 0; applyZoom(); }}
  else if (e.key === '1') {{ zoomIdx = 1; applyZoom(); }}
}});
</script>
</body>
</html>
"""


def write(out_dir, dest, embed=False, img_ext="png"):
    """把画廊页写到 dest，返回 (路径, 大小 MB)。"""
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(out_dir, embed=embed, img_ext=img_ext), encoding="utf-8")
    return dest, dest.stat().st_size / 1024 / 1024


def img_dir_size_mb(out_dir):
    d = pathlib.Path(out_dir) / IMG_DIRNAME
    return sum(f.stat().st_size for f in d.glob("*")) / 1024 / 1024 if d.exists() else 0.0
