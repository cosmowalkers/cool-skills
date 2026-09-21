#!/usr/bin/env python3
"""text2png 形式 × 主题矩阵生成器：15 chart × 9 style = 135 个 HTML。"""
import pathlib
import shutil
import sys

ROOT = pathlib.Path("/tmp/t2h-gallery")
HTML_DIR = ROOT / "html"
PNG_DIR = ROOT / "png"


def prepare_dirs(clean_png: bool = False) -> None:
    """重新生成 HTML 时只清 HTML；PNG 仅在显式要求时才清（避免误删已截好的图）。"""
    shutil.rmtree(HTML_DIR, ignore_errors=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    if clean_png:
        shutil.rmtree(PNG_DIR, ignore_errors=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)

FONTS = {
    "warm": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Sans+SC:wght@400;500;700&display=swap",
    "dark": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500&display=swap",
    "editorial": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Lora:wght@400;500;600&family=Libre+Franklin:wght@400;500;600&family=Noto+Serif+SC:wght@500;700&display=swap",
    "neon": "https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Noto+Sans+SC:wght@400;500&display=swap",
    "paper": "https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Nunito:wght@400;500;600;700&family=ZCOOL+XiaoWei&family=Noto+Sans+SC:wght@400;500&display=swap",
    "glass": "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap",
    "corporate": "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap",
    "minimal": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@500;600&family=Noto+Sans+SC:wght@400;500;700&display=swap",
    "retro": "https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&family=Noto+Sans+SC:wght@400;500&display=swap",
}

STYLES = {
    "warm": dict(
        label="暖色报告", bg="#faf6ee",
        vars="--card:#ffffff;--text:#2e2410;--text2:#6a5a40;--muted:#a08060;--line:#e2d8c4;--arrow:#c0a06a;--a1:#c0622a;--a2:#b08830;--a3:#8a6a2a;--a4:#a04a2a;--radius:12px;",
        head="'Playfair Display','Noto Serif SC',serif", body="'Noto Sans SC',sans-serif", num="'Playfair Display',serif",
        css=".wrap{background-image:url(\"data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E\")}"
            ".card{border:1px solid var(--line);box-shadow:0 1px 2px rgba(120,90,50,.06)}"
            ".card.hi{border-color:var(--a1);box-shadow:0 3px 10px rgba(192,98,42,.16)}"
            ".kicker{color:var(--a2)}",
    ),
    "dark": dict(
        label="深色科技", bg="#0d1117",
        vars="--card:#161b22;--card2:#1c2128;--text:#e6edf3;--text2:#8b949e;--muted:#484f58;--line:#30363d;--arrow:#58a6ff;--a1:#58a6ff;--a2:#3fb950;--a3:#d29922;--a4:#bc8cff;--radius:10px;",
        head="'Space Grotesk','DM Sans',sans-serif", body="'DM Sans','Noto Sans SC',sans-serif", num="'Space Grotesk',sans-serif",
        css=".card{border:1px solid var(--line);box-shadow:inset 0 1px 0 rgba(255,255,255,.03)}"
            ".card.hi{border-color:var(--a1);box-shadow:0 0 0 1px var(--a1),0 0 18px rgba(88,166,255,.18)}"
            ".kicker,.tag,.bar-label{font-family:'JetBrains Mono',monospace}"
            ".badge{color:#0d1117}",
    ),
    "editorial": dict(
        label="杂志排版", bg="#f8f5f0",
        vars="--card:#ffffff;--text:#1c1714;--text2:#5a4e42;--muted:#9a8e82;--line:#d8d0c4;--rule:#c8bca8;--arrow:#a0522d;--a1:#a0522d;--a2:#2c3e5a;--a3:#b8860b;--a4:#7a6a52;--radius:4px;",
        head="'Cormorant Garamond','Noto Serif SC',serif", body="'Lora','Noto Serif SC',serif", num="'Cormorant Garamond',serif",
        css=".card{border:0;border-top:1px solid var(--rule);border-radius:0;padding:12px 14px}"
            ".kicker,.tag{font-family:'Libre Franklin',sans-serif;text-transform:uppercase;letter-spacing:.14em}"
            ".title{font-size:32px}.badge{background:transparent;color:var(--a1);border:1px solid var(--a1)}",
    ),
    "neon": dict(
        label="赛博霓虹", bg="#0a0015",
        vars="--card:rgba(20,10,40,.82);--card2:#140a28;--text:#f0e8ff;--text2:#a090c0;--muted:#605080;--line:rgba(140,100,255,.3);--arrow:#22d3ee;--a1:#a855f7;--a2:#22d3ee;--a3:#ec4899;--a4:#facc15;--radius:8px;",
        head="'Orbitron',sans-serif", body="'Rajdhani','Noto Sans SC',sans-serif", num="'Orbitron',sans-serif",
        css=".title{text-transform:uppercase;letter-spacing:.06em;text-shadow:0 0 14px rgba(168,85,247,.55)}"
            ".card{border:1px solid var(--line);box-shadow:0 0 16px rgba(168,85,247,.14),inset 0 0 22px rgba(34,211,238,.05)}"
            ".card.hi{border-color:var(--a2);box-shadow:0 0 22px rgba(34,211,238,.35)}"
            ".kicker,.tag{font-family:'Share Tech Mono',monospace;color:var(--a2)}"
            ".badge{color:#0a0015}",
    ),
    "paper": dict(
        label="手绘纸质", bg="#f5f0e6",
        vars="--card:#fffdf7;--text:#3a3228;--text2:#6a5e50;--muted:#a09480;--line:#d0c4aa;--sketch:#8a7e68;--arrow:#8a7e68;--a1:#c0392b;--a2:#2e6da4;--a3:#27864a;--a4:#d4820a;--radius:6px;",
        head="'Caveat','ZCOOL XiaoWei',cursive", body="'Nunito','Noto Sans SC',sans-serif", num="'Caveat',cursive",
        css=".title,.card h3{font-family:'Caveat','ZCOOL XiaoWei',cursive}.title{font-size:34px}"
            ".card{border:2px dashed var(--sketch);background:var(--card);transform:rotate(-.35deg)}"
            ".card:nth-child(even){transform:rotate(.4deg)}"
            ".card.hi{border-style:solid;border-color:var(--a1)}"
            ".kicker{font-family:'Caveat',cursive;font-size:15px;letter-spacing:0}",
    ),
    "glass": dict(
        label="玻璃拟态", bg="#e8eaf0",
        vars="--card:rgba(255,255,255,.55);--card2:rgba(255,255,255,.75);--text:#1e2030;--text2:#555a70;--muted:#8a8fa5;--line:rgba(255,255,255,.65);--arrow:#0ea5e9;--a1:#7c3aed;--a2:#0ea5e9;--a3:#10b981;--a4:#f59e0b;--radius:16px;",
        head="'Outfit','Noto Sans SC',sans-serif", body="'Outfit','Noto Sans SC',sans-serif", num="'Outfit',sans-serif",
        css="body{background:radial-gradient(900px 500px at 12% -10%,rgba(124,58,237,.22),transparent),radial-gradient(800px 460px at 92% 6%,rgba(14,165,233,.22),transparent),var(--bg)}"
            ".card{border:1px solid var(--line);backdrop-filter:blur(12px);box-shadow:0 8px 24px rgba(31,41,70,.10)}"
            ".card.hi{background:var(--card2)}"
            ".badge{color:#fff}",
    ),
    "corporate": dict(
        label="商务正式", bg="#f4f6f9",
        vars="--card:#ffffff;--text:#1e2a3b;--text2:#4a5568;--muted:#8a95a5;--line:#e2e8f0;--strong:#1e3a5f;--arrow:#2563eb;--a1:#1e3a5f;--a2:#2563eb;--a3:#059669;--a4:#b8860b;--radius:6px;",
        head="'Manrope','Noto Sans SC',sans-serif", body="'Manrope','Noto Sans SC',sans-serif", num="'Manrope',sans-serif",
        css=".card{border:1px solid var(--line);box-shadow:0 1px 2px rgba(30,58,95,.05)}"
            ".card.hi{border-color:var(--strong);border-left:4px solid var(--strong)}"
            ".kicker,.tag{text-transform:uppercase;letter-spacing:.12em;font-weight:600}"
            ".thead{background:var(--strong);color:#fff;font-weight:600}",
    ),
    "minimal": dict(
        label="极简黑白", bg="#ffffff",
        vars="--card:#ffffff;--text:#1a1a1a;--text2:#555555;--muted:#999999;--line:#e0e0e0;--strong:#1a1a1a;--arrow:#1a1a1a;--a1:#1a1a1a;--a2:#555555;--a3:#888888;--a4:#bbbbbb;--radius:2px;",
        head="'IBM Plex Sans','Noto Sans SC',sans-serif", body="'IBM Plex Sans','Noto Sans SC',sans-serif", num="'IBM Plex Mono',monospace",
        css=".card{border:1px solid var(--line);box-shadow:none}"
            ".card.hi{border-color:var(--strong);border-width:2px}"
            ".kicker,.tag{font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:.1em}"
            ".badge{background:#1a1a1a;color:#fff}",
    ),
    "retro": dict(
        label="复古像素", bg="#1a1c2e",
        vars="--card:#252840;--card2:#1e2038;--text:#e8e8e8;--text2:#a0a0b0;--muted:#606078;--line:#3a3c5a;--arrow:#4af626;--a1:#4af626;--a2:#ffb000;--a3:#ff2d95;--a4:#29adff;--radius:0px;",
        head="'Press Start 2P',cursive", body="'VT323','Noto Sans SC',monospace", num="'Press Start 2P',cursive",
        css=".wrap{background-image:repeating-linear-gradient(0deg,rgba(255,255,255,.045) 0 1px,transparent 1px 3px)}"
            ".title{font-size:20px;line-height:1.5;color:var(--a1);text-shadow:2px 2px 0 #0d0e1a}"
            ".card{border:3px solid var(--line);box-shadow:4px 4px 0 #0d0e1a}"
            ".card.hi{border-color:var(--a1);box-shadow:4px 4px 0 var(--a1)}"
            ".kicker,.tag{font-family:'VT323',monospace;color:var(--a2);letter-spacing:.08em}"
            ".badge{background:var(--a3);color:#12131f}",
    ),
}

BASE_CSS = """
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg)}
body{font-family:var(--font-body);color:var(--text);-webkit-font-smoothing:antialiased}
.wrap{width:860px;margin:0 auto;padding:24px}
.head{margin-bottom:16px}
.kicker{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.title{font-family:var(--font-head);font-size:28px;line-height:1.25;margin:0}
.subtitle{font-size:13px;color:var(--text2);margin-top:8px;line-height:1.6}
.row{display:flex;gap:10px;align-items:stretch}
.g2{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.card{background:var(--card);border-radius:var(--radius);padding:12px 14px}
.card h3{margin:0 0 6px;font-size:15px;font-family:var(--font-head);line-height:1.35}
.card p{margin:0;font-size:12.5px;line-height:1.6;color:var(--text2)}
.num{font-family:var(--font-num);font-size:26px;font-weight:800;line-height:1}
.tag{font-size:11px;color:var(--muted)}
.badge{display:inline-block;font-size:11px;padding:2px 8px;border-radius:99px;background:var(--a1);color:#fff}
.arrow{align-self:center;color:var(--arrow);font-size:15px;flex:0 0 auto}
.foot{margin-top:14px;display:flex;justify-content:space-between;font-size:11px;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--a1);flex:0 0 auto}
"""

CHART_NAME = {
    "flowchart": "流程图", "comparison": "对比表", "timeline": "时间线",
    "architecture": "架构拓扑", "dashboard": "数据看板", "gantt": "甘特图",
    "org-chart": "组织架构", "funnel": "漏斗图", "mind-map": "思维导图",
    "matrix": "矩阵图", "kanban": "看板", "checklist": "清单卡", "quote-card": "金句卡",
    "sequence": "时序图", "swimlane": "泳道图",
}


def head_block(theme: str, title: str, subtitle: str) -> str:
    title_html = f'<h1 class="title">{title}</h1>' if title else ""
    sub_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
    return f"""<div class="head">
  <div class="kicker">{CHART_NAME[theme]}</div>
  {title_html}
  {sub_html}
</div>"""


def card(title: str, desc: str, hi: bool = False, extra: str = "") -> str:
    cls = "card hi" if hi else "card"
    body = f"<h3>{title}</h3><p>{desc}</p>" if desc else f"<h3>{title}</h3>"
    return f'<div class="{cls}">{body}{extra}</div>'


def foot(note: str, style_id: str, chart_id: str) -> str:
    return f'<div class="foot"><span>{note}</span><span>{chart_id} · {style_id}</span></div>'


# ───────────────────────── 13 种图表内容 + 布局 ─────────────────────────

def chart_flowchart(style_id):
    steps = [
        ("开局", "3 节蛇身，随机食物落点"),
        ("吃到食物", "蛇身 +1，分数 +10"),
        ("提速", "每吃 5 个，移动间隔 -8ms"),
        ("撞墙 / 咬到自己", "判定条件：越界或占用自身格"),
        ("结算", "分数入库，重开一局"),
    ]
    cards = '<div class="arrow">→</div>'.join(card(t, d, i == 2) for i, (t, d) in enumerate(steps))
    extra_css = """
.flow{display:flex;align-items:stretch;gap:6px}
.flow .card{flex:1;min-width:0}
.note{display:flex;gap:8px;align-items:center;margin-top:10px}
"""
    note = ('<div class="note"><span class="dot"></span>'
            '<p>分支判断：吃到食物 → 变长；越界或撞到自身 → 结算。一局平均 42 秒、约 11 次进食。</p></div>')
    head_html = head_block("flowchart", "贪吃蛇一局的生命周期", "从开局到结算的 5 个阶段，以及唯一的两个分支出口")
    body = f'<div class="flow">{cards}</div>{note}'
    return head_html, body, extra_css


def chart_comparison(style_id):
    rows = [
        ("单程时间", "28 分钟", "41 分钟", "19 分钟"),
        ("日成本", "¥6", "¥38", "¥0"),
        ("受天气影响", "小", "大", "中"),
        ("可支配时间", "可读书 22 分钟", "需全神贯注", "可听播客"),
        ("准点率", "96%", "71%", "88%"),
    ]
    body = ["<div class='g4 thead'><div>维度</div><div>地铁</div><div>自驾</div><div>骑行</div></div>"]
    for name, a, b, c in rows:
        body.append(f"<div class='g4 line-row'><div class='dim'>{name}</div><div>{a}</div><div>{b}</div><div>{c}</div></div>")
    verdict = ('<div class="card hi" style="margin-top:10px">'
               '<h3>推荐：地铁 + 骑行接驳</h3>'
               '<p>时间最稳、成本最低，路上还能读 22 分钟书；自驾只在需要搬运设备时更划算。</p></div>')
    extra_css = """
.thead{padding:8px 14px;color:var(--text2);font-size:12px}
.line-row{padding:9px 14px;border-top:1px solid var(--line);font-size:13px;color:var(--text2)}
.line-row:nth-child(odd){background:color-mix(in srgb, var(--card) 92%, var(--a2))}
.dim{color:var(--text);font-weight:600}
.thead div:nth-child(2),.line-row div:nth-child(2){color:var(--a2);font-weight:700}
"""
    return head_block("comparison", "三种通勤方式怎么选", "同样 12 公里的上班路，地铁 / 自驾 / 折叠车骑行对比"), "".join(body) + verdict, extra_css


def chart_timeline(style_id):
    events = [
        ("07:20", "出门", "步行 6 分钟到地铁站"),
        ("07:32", "进站", "刷卡进闸，等车 90 秒"),
        ("07:46", "换乘", "2 号线 → 8 号线，走 200 米"),
        ("08:03", "出站", "B 口出，顺路买早餐"),
        ("08:12", "到工位", "打卡，泡咖啡"),
    ]
    rows = "".join(
        f'<div class="tl-item"><div class="tl-time">{t}</div><div class="tl-dot"></div>'
        f'<div class="card{" hi" if i == 2 else ""}"><h3>{k}</h3><p>{d}</p></div></div>'
        for i, (t, k, d) in enumerate(events))
    extra_css = """
.tl{position:relative;padding-left:0}
.tl-item{display:grid;grid-template-columns:64px 22px 1fr;align-items:center;gap:6px;padding:5px 0}
.tl-time{font-size:12px;color:var(--a1);font-weight:700;text-align:right}
.tl-dot{width:10px;height:10px;border-radius:50%;background:var(--a1);justify-self:center;
  box-shadow:0 0 0 4px color-mix(in srgb, var(--a1) 18%, transparent)}
"""
    return head_block("timeline", "一次早高峰通勤的时序", "07:20 出门 → 08:12 到工位，全程 52 分钟"), f'<div class="tl">{rows}</div>', extra_css


def chart_architecture(style_id):
    body = """
<div class="arch">
  <div class="card wide"><h3>光猫（桥接）</h3><p>运营商入户，千兆下行</p></div>
  <div class="link">↓ 千兆网线</div>
  <div class="card wide hi"><h3>主路由</h3><p>Wi-Fi 6，NAT + DHCP，访客网络隔离</p></div>
  <div class="link">↓ 千兆交换机 / Wi-Fi</div>
  <div class="g4">
    <div class="card"><h3>笔记本</h3><p>有线 · 10.0.0.12</p></div>
    <div class="card"><h3>手机 ×3</h3><p>Wi-Fi 5G · DHCP</p></div>
    <div class="card"><h3>电视盒子</h3><p>有线 · 4K 直连</p></div>
    <div class="card"><h3>NAS</h3><p>有线 · 备份 + 影音库</p></div>
  </div>
  <div class="legend"><span class="tag">实线 = 有线千兆</span><span class="tag">虚线 = Wi-Fi</span><span class="tag">访客网络独立 VLAN</span></div>
</div>"""
    extra_css = """
.arch .wide{width:100%}
.link{text-align:center;color:var(--arrow);font-size:12px;padding:6px 0}
.legend{display:flex;gap:14px;margin-top:10px}
"""
    return head_block("architecture", "家庭网络拓扑", "光猫桥接 → 主路由 → 终端设备，以及访客网络隔离"), body, extra_css


def chart_dashboard(style_id):
    kpis = [
        ("步数", "8,420", "↑ 12%", "日均目标 8,000"),
        ("睡眠", "7h 12m", "↓ 18m", "深睡 1h 46m"),
        ("专注", "4h 05m", "↑ 35m", "番茄 9 个"),
        ("久坐", "5 次", "↓ 2 次", "最长 78 分钟"),
    ]
    cards = "".join(
        f'<div class="card{" hi" if i == 1 else ""}"><div class="tag">{k}</div>'
        f'<div class="num" style="margin:6px 0 4px">{v}</div>'
        f'<div class="delta">{d}</div><p>{s}</p></div>'
        for i, (k, v, d, s) in enumerate(kpis))
    bars = [("周一", 62), ("周二", 78), ("周三", 41), ("周四", 88), ("周五", 71), ("周六", 95), ("周日", 54)]
    bars_html = "".join(
        f'<div class="bar"><div class="bar-track"><div class="bar-fill" style="height:{h}%"></div></div>'
        f'<div class="bar-label">{d}</div></div>' for d, h in bars)
    extra_css = """
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.delta{font-size:12px;color:var(--a3);font-weight:700}
.chart{margin-top:12px}
.bars{display:flex;gap:12px;align-items:flex-end;height:96px;margin-top:8px}
.bar{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px}
.bar-track{width:100%;height:76px;background:color-mix(in srgb, var(--line) 55%, transparent);border-radius:4px;
  display:flex;align-items:flex-end;overflow:hidden}
.bar-fill{width:100%;background:linear-gradient(180deg,var(--a2),var(--a1));border-radius:4px 4px 0 0}
.bar-label{font-size:11px;color:var(--muted)}
"""
    body = (f'<div class="kpis">{cards}</div>'
            f'<div class="card chart"><h3>本周活动量（步数指数）</h3><div class="bars">{bars_html}</div></div>')
    return head_block("dashboard", "一周身体与专注数据", "步数、睡眠、专注时长与久坐次数的周报视图"), body, extra_css


def chart_gantt(style_id):
    tasks = [
        ("买菜 + 备菜", 0, 22, "09:00-10:30"),
        ("厨房深度清洁", 18, 30, "10:00-12:00"),
        ("吸尘 + 拖地", 30, 26, "11:30-13:00"),
        ("卫生间除垢", 40, 24, "12:30-14:00"),
        ("晾晒 + 收纳", 60, 20, "14:00-15:10"),
        ("倒垃圾 + 复盘", 78, 12, "15:20-16:00"),
    ]
    rows = "".join(
        f'<div class="g-row"><div class="g-name">{n}</div>'
        f'<div class="g-track"><div class="g-bar{" hi" if i == 1 else ""}" style="left:{s}%;width:{w}%">'
        f'<span>{tm}</span></div></div></div>'
        for i, (n, s, w, tm) in enumerate(tasks))
    ticks = "".join(f'<span>{t}</span>' for t in ["09:00", "11:00", "13:00", "15:00", "16:00"])
    body = f'<div class="card"><div class="g-head"><div class="g-name">任务</div><div class="g-axis">{ticks}</div></div>{rows}</div>'
    extra_css = """
.g-head,.g-row{display:grid;grid-template-columns:150px 1fr;align-items:center;gap:10px}
.g-name{font-size:12.5px;color:var(--text2)}
.g-axis{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);padding-bottom:6px}
.g-row{padding:5px 0}
.g-track{position:relative;height:22px;background:color-mix(in srgb, var(--line) 40%, transparent);border-radius:4px}
.g-bar{position:absolute;top:0;height:22px;background:var(--a2);border-radius:4px;display:flex;align-items:center;
  justify-content:center;color:#fff;font-size:11px}
.g-bar.hi{background:var(--a1)}
"""
    return head_block("gantt", "周六上午的大扫除排期", "6 个任务、约 7 小时，含并行段与缓冲"), body, extra_css


def chart_org(style_id):
    body = """
<div class="org">
  <div class="card wide hi"><h3>家庭 CEO · 妈妈</h3><p>总协调：排班、预算审批、对外沟通</p></div>
  <div class="connector">↓</div>
  <div class="g3">
    <div class="card"><h3>后勤 · 爸爸</h3><p>采购、维修、接送；预算 ¥2,000/月</p></div>
    <div class="card"><h3>学习 · 姐姐</h3><p>作业辅导、图书馆借还、家长会</p></div>
    <div class="card"><h3>环境 · 弟弟</h3><p>倒垃圾、浇花、遛狗</p></div>
  </div>
  <div class="connector">↓</div>
  <div class="g4">
    <div class="card"><h3>采买组</h3><p>每周日清单制</p></div>
    <div class="card"><h3>厨房组</h3><p>轮值做饭 3 天/人</p></div>
    <div class="card"><h3>清洁组</h3><p>周六上午集中</p></div>
    <div class="card"><h3>外联组</h3><p>快递、缴费、访客</p></div>
  </div>
</div>"""
    extra_css = """
.org .wide{width:100%}
.connector{text-align:center;color:var(--arrow);font-size:16px;padding:6px 0}
"""
    return head_block("org-chart", "家务分工组织架构", "谁负责什么、预算多少、轮值规则一并写清"), body, extra_css


def chart_funnel(style_id):
    stages = [("打开 App", 1000, 100), ("浏览菜单", 620, 62), ("加入购物车", 310, 41),
              ("提交订单", 180, 33), ("送达完成", 165, 30)]
    rows = "".join(
        f'<div class="f-row"><div class="f-label">{n}</div>'
        f'<div class="f-bar" style="width:{w}%;background:linear-gradient(90deg,var(--a1),var(--a2))">'
        f'<span>{v}</span></div><div class="f-pct">{p}%</div></div>'
        for n, v, w, p in [(n, v, w, int(v * 100 / 1000)) for n, v, w in stages])
    extra_css = """
.f-row{display:grid;grid-template-columns:110px 1fr 46px;align-items:center;gap:10px;margin-bottom:8px}
.f-label{font-size:12.5px;color:var(--text2)}
.f-bar{height:30px;border-radius:4px;display:flex;align-items:center;justify-content:flex-end;
  padding-right:8px;color:#fff;font-size:12px;font-weight:700;min-width:60px}
.f-pct{font-size:12px;color:var(--a1);font-weight:700;text-align:right}
"""
    hint = ('<div class="card hi" style="margin-top:8px"><h3>最大流失：浏览 → 加购（-50%）</h3>'
            '<p>菜单首屏只有 6 个 SKU，且「起送价」提示不显眼；建议前置热销榜与凑单提示。</p></div>')
    return head_block("funnel", "一次外卖下单的转化漏斗", "从打开 App 到送达，5 个阶段的留存与流失"), f'<div class="card">{rows}</div>{hint}', extra_css


def chart_mindmap(style_id):
    body = """
<div class="mm">
  <div class="mm-side left">
    <div class="mm-branch"><h3>证件</h3><p>身份证 · 护照 · 驾照 · 签证复印件</p></div>
    <div class="mm-branch"><h3>电子</h3><p>充电宝 · 转换插头 · 数据线 ×2 · 耳机</p></div>
    <div class="mm-branch"><h3>行程</h3><p>机票值机 · 酒店确认单 · 离线地图</p></div>
  </div>
  <div class="mm-center"><b>出发前<br>48 小时</b><span>清单式核对</span></div>
  <div class="mm-side right">
    <div class="mm-branch"><h3>衣物</h3><p>按天气 3 套 · 外套 · 舒适鞋</p></div>
    <div class="mm-branch"><h3>应急</h3><p>常用药 · 创可贴 · 保险单号</p></div>
    <div class="mm-branch"><h3>其他</h3><p>现金少量 · 折叠袋 · 锁具</p></div>
  </div>
</div>"""
    extra_css = """
.mm{display:grid;grid-template-columns:1fr 150px 1fr;gap:12px;align-items:center}
.mm-center{background:var(--a1);color:#fff;border-radius:14px;padding:16px 12px;text-align:center;
  font-family:var(--font-head);box-shadow:0 6px 18px color-mix(in srgb, var(--a1) 35%, transparent)}
.mm-center b{display:block;font-size:16px;line-height:1.4}
.mm-center span{font-size:11px;opacity:.85}
.mm-side{display:flex;flex-direction:column;gap:8px}
.mm-branch{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:10px 12px}
.mm-branch h3{margin:0 0 4px;font-size:13.5px}
.mm-branch p{margin:0;font-size:11.5px;color:var(--text2);line-height:1.5}
.mm-side.left{text-align:right}
"""
    return head_block("mind-map", "出发前 48 小时要准备什么", "中心节点 + 6 个分支，覆盖证件、电子、衣物、应急等"), body, extra_css


def chart_matrix(style_id):
    quads = [
        ("🔥 重要且紧急", ["线上支付回调失败", "明天的客户演示", "服务器磁盘告警"], "今天必须做完", True),
        ("📅 重要不紧急", ["季度技术规划", "重构登录模块", "补自动化测试"], "排进下周日程", False),
        ("⚡ 紧急不重要", ["临时数据导出", "同事的接口答疑", "周报催收"], "委托或批量处理", False),
        ("🗑 不重要不紧急", ["清理下载目录", "整理书签", "换桌面壁纸"], "有空再说", False),
    ]
    cells = "".join(
        f'<div class="card{" hi" if hi else ""}"><h3>{t}</h3><ul>' +
        "".join(f"<li>{i}</li>" for i in items) +
        f'</ul><div class="tag">{note}</div></div>'
        for t, items, note, hi in quads)
    extra_css = """
.mx{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.mx .card ul{margin:6px 0 8px;padding-left:16px}
.mx .card li{font-size:12.5px;color:var(--text2);line-height:1.7}
.axis{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin:0 2px 6px}
"""
    body = ('<div class="axis"><span>← 紧急</span><span>不紧急 →</span></div>'
            f'<div class="mx">{cells}</div>')
    return head_block("matrix", "本周待办的四象限", "横轴紧急度、纵轴重要度，四格各放 3 件事"), body, extra_css


def chart_kanban(style_id):
    cols = [
        ("待办 3", ["换季衣物收纳", "预约牙医", "给车做保养"], ["#tag"]),
        ("进行中 2", ["周末菜单规划", "清理邮箱订阅"], []),
        ("已完成 4", ["交水电费", "换净水器滤芯", "阳台花草换盆", "整理药箱"], []),
    ]
    col_html = ""
    for title, items, _ in cols:
        cards = "".join(f'<div class="k-card"><b>{i}</b><span class="tag">{COL_TAG.get(i, "家务")}</span></div>' for i in items)
        col_html += f'<div class="k-col"><div class="k-head">{title}</div>{cards}</div>'
    extra_css = """
.kb{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.k-col{background:color-mix(in srgb, var(--line) 35%, transparent);border-radius:var(--radius);padding:10px;display:flex;flex-direction:column;gap:8px}
.k-head{font-size:12px;font-weight:700;color:var(--text);letter-spacing:.04em}
.k-card{background:var(--card);border:1px solid var(--line);border-radius:calc(var(--radius) - 2px);padding:9px 10px;display:flex;flex-direction:column;gap:4px}
.k-card b{font-size:12.5px;font-weight:600}
"""
    return head_block("kanban", "家务看板", "待办 / 进行中 / 已完成三列，卡片带分类标签"), f'<div class="kb">{col_html}</div>', extra_css


COL_TAG = {
    "换季衣物收纳": "收纳", "预约牙医": "健康", "给车做保养": "车辆",
    "周末菜单规划": "饮食", "清理邮箱订阅": "数字清理",
    "交水电费": "账单", "换净水器滤芯": "维护", "阳台花草换盆": "植物", "整理药箱": "健康",
}


def chart_checklist(style_id):
    groups = [
        ("出门前必查", [("关燃气", True), ("关窗", True), ("拔充电器", True), ("带钥匙", True), ("带工牌", True)]),
        ("包里确认", [("笔记本电脑", True), ("充电宝", False), ("水杯", False)]),
    ]
    rows = ""
    done = total = 0
    for gname, items in groups:
        rows += f'<div class="tag" style="margin:10px 0 6px">{gname}</div>'
        for label, ok in items:
            total += 1
            done += 1 if ok else 0
            rows += (f'<div class="ck"><span class="box{" ok" if ok else ""}">{"✓" if ok else ""}</span>'
                     f'<span class="ck-label">{label}</span></div>')
    pct = int(done * 100 / total)
    progress = (f'<div class="prog"><div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>'
                f'<span>{done}/{total} · {pct}%</span></div>')
    extra_css = """
.ck{display:flex;align-items:center;gap:8px;padding:5px 0;font-size:13px;color:var(--text2)}
.box{width:16px;height:16px;border:1.5px solid var(--line);border-radius:3px;display:flex;align-items:center;
  justify-content:center;font-size:11px;color:#fff}
.box.ok{background:var(--a3);border-color:var(--a3)}
.prog{display:flex;align-items:center;gap:10px;margin-top:10px}
.prog-track{flex:1;height:8px;background:color-mix(in srgb, var(--line) 60%, transparent);border-radius:99px;overflow:hidden}
.prog-fill{height:8px;background:linear-gradient(90deg,var(--a3),var(--a2))}
.prog span{font-size:12px;color:var(--a3);font-weight:700}
"""
    body = f'<div class="card">{rows}{progress}</div>'
    return head_block("checklist", "出门前检查清单", "8 项核对，已完成 5 项；出门前扫一眼即可"), body, extra_css


def chart_quote(style_id):
    body = """
<div class="card qc">
  <div class="qmark">“</div>
  <blockquote>生活就像骑自行车，<br>想保持平衡，就得往前走。</blockquote>
  <div class="qdiv"></div>
  <div class="qwho">—— 阿尔伯特·爱因斯坦</div>
  <div class="qctx">出处：1930 年给儿子的信；原文 “Life is like riding a bicycle. To keep your balance, you must keep moving.”</div>
</div>"""
    extra_css = """
.qc{padding:34px 40px;text-align:center}
.qmark{font-family:var(--font-head);font-size:72px;line-height:.6;color:var(--a1);opacity:.55}
.qc blockquote{margin:10px 0 0;font-family:var(--font-head);font-size:30px;line-height:1.5}
.qdiv{width:64px;height:2px;background:var(--a1);margin:20px auto}
.qwho{font-size:14px;color:var(--text)}
.qctx{margin-top:8px;font-size:12px;color:var(--muted);line-height:1.7}
"""
    return head_block("quote-card", "", ""), body, extra_css


def chart_sequence(style_id):
    actors = [("乘客", "发起方"), ("进站闸机", "设备"), ("列车", "承运"), ("出站闸机", "设备")]
    msgs = [
        (0, 1, "req", "刷卡 / 刷码 · NFC 0.3s"),
        (1, 0, "res", "闸门开启 · 行程开始"),
        (0, 2, "req", "上车 · 3 号车厢"),
        (2, 3, "async", "到站广播 · 位置同步"),
        (0, 3, "req", "出站刷码"),
        (3, 0, "res", "扣费 ¥6 · 行程结束"),
    ]
    acts = [(1, 0, 1), (2, 2, 2), (3, 4, 2), (1, 5, 1)]
    head = "".join(f'<div class="actor"><b>{n}</b><span>{r}</span></div>' for n, r in actors)
    lives = "".join(f'<i class="life" style="--i:{i}"></i>' for i in range(len(actors)))
    act_html = "".join(f'<i class="act" style="--i:{i};--top:{t};--h:{h}"></i>' for i, t, h in acts)
    msg_html = ""
    for idx, (f, t, kind, label) in enumerate(msgs):
        cls = f"msg {kind}" + (" rtl" if t < f else "")
        msg_html += (f'<div class="{cls}" style="--left:{min(f, t) + 0.5};--w:{abs(t - f)};--row:{idx}">'
                     f'<span class="lbl">{label}</span><i class="head"></i></div>')
    body = f"""<div class="seq" style="--actors:{len(actors)};--rows:{len(msgs)}">
  <div class="seq-head">{head}</div>
  <div class="seq-body">{lives}{act_html}{msg_html}</div>
  <div class="seq-foot"><span>实线 = 请求</span><span>虚线 = 响应</span><span>点线 = 异步通知</span><span>竖条 = 设备处理中</span></div>
</div>"""
    extra_css = """
.seq{--row-h:32px}
.seq-head{display:flex;gap:8px;margin-bottom:10px}
.actor{flex:1;text-align:center;background:var(--card);border:1.5px solid var(--line);border-radius:var(--radius);padding:8px 6px}
.actor b{font-size:13px}
.actor span{display:block;font-size:11px;color:var(--muted);margin-top:2px}
.seq-body{position:relative;height:calc(var(--rows) * var(--row-h))}
.life{position:absolute;top:0;bottom:0;border-left:1px dashed var(--line);
  left:calc((var(--i) + .5) * (100% / var(--actors)))}
.act{position:absolute;width:9px;border-radius:3px;background:var(--a2);opacity:.9;
  left:calc((var(--i) + .5) * (100% / var(--actors)) - 4.5px);
  top:calc(var(--top) * var(--row-h));height:calc(var(--h) * var(--row-h))}
.msg{position:absolute;height:0;border-top:2px solid var(--a1);
  left:calc(var(--left) * (100% / var(--actors)));width:calc(var(--w) * (100% / var(--actors)));
  top:calc((var(--row) + .5) * var(--row-h))}
.msg.res{border-top-style:dashed;border-top-color:var(--a3)}
.msg.async{border-top-style:dotted;border-top-color:var(--a2)}
.msg .lbl{position:absolute;left:50%;top:-20px;transform:translateX(-50%);white-space:nowrap;font-size:11.5px;color:var(--text2)}
.msg .head{position:absolute;right:-1px;top:-5px;width:0;height:0;
  border-left:7px solid var(--a1);border-top:4px solid transparent;border-bottom:4px solid transparent}
.msg.res .head{border-left-color:var(--a3)}
.msg.async .head{border-left-color:var(--a2)}
.msg.rtl .head{left:-1px;right:auto;transform:scaleX(-1)}
.seq-foot{display:flex;gap:16px;margin-top:12px;font-size:11px;color:var(--muted)}
"""
    return head_block("sequence", "一次地铁乘车里的时序", "乘客 / 闸机 / 列车之间 6 次交互，含一次异步到站通知"), body, extra_css


def chart_swimlane(style_id):
    stages = ["① 下单", "② 履约", "③ 送达"]
    lanes = [
        ("用户", "发起方", [("提交订单", "10:02", ""), ("等待出餐", "阻塞 19 分钟", "ghost"), ("确认收货 · 评价", "10:46", "")]),
        ("商家", "供给", [None, ("接单 → 出餐", "10:05-10:22", "hi"), None]),
        ("骑手", "配送", [None, ("到店取餐", "10:24", ""), ("送达", "10:41", "")]),
        ("平台", "调度", [("派单给骑手", "10:03", ""), ("路径规划 · 超时提醒", "", "ghost"), ("订单结算", "10:47", "")]),
    ]
    head_cells = "".join(f'<div class="stage">{s}</div>' for s in stages)
    lane_html = ""
    for name, role, cells in lanes:
        cell_html = ""
        for item in cells:
            if item is None:
                cell_html += '<div class="cell"></div>'
            else:
                title, note, cls = item
                note_html = f"<em>{note}</em>" if note else ""
                cell_html += f'<div class="cell"><div class="task {cls}">{title}{note_html}</div></div>'
        lane_html += (f'<div class="lane"><div class="lane-label">{name}<span>{role}</span></div>{cell_html}</div>')
    body = f"""<div class="lane-wrap" style="--stages:{len(stages)}">
  <div class="lane-head"><div class="lane-corner"></div>{head_cells}</div>
  {lane_html}
</div>
<div class="note"><span class="dot"></span><p>瓶颈在「② 履约」：商家出餐 17 分钟，用户与骑手都在等；平台侧只有超时提醒，没有重派机制。</p></div>"""
    extra_css = """
.lane-head,.lane{display:grid;grid-template-columns:104px repeat(var(--stages),1fr);gap:8px;align-items:stretch}
.stage{font-size:11px;letter-spacing:.1em;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:4px}
.lane-label{display:flex;flex-direction:column;justify-content:center;font-size:12.5px;font-weight:700;
  border-left:3px solid var(--a1);padding-left:8px;background:color-mix(in srgb, var(--line) 28%, transparent);border-radius:4px}
.lane-label span{font-size:11px;font-weight:400;color:var(--muted)}
.cell{min-height:54px;display:flex;align-items:center;justify-content:center;padding:6px;
  background:color-mix(in srgb, var(--line) 22%, transparent);border-radius:6px}
.task{width:100%;background:var(--card);border:1px solid var(--line);border-left:3px solid var(--a2);
  border-radius:6px;padding:6px 8px;font-size:12px}
.task em{display:block;font-style:normal;font-size:11px;color:var(--muted);margin-top:2px}
.task.hi{border-color:var(--a1);border-left-width:3px;background:color-mix(in srgb, var(--a1) 12%, var(--card))}
.task.ghost{opacity:.65;border-style:dashed}
.note{display:flex;gap:8px;align-items:center;margin-top:10px}
"""
    return head_block("swimlane", "外卖从下单到送达，谁在哪一步", "4 条泳道 × 3 个阶段，瓶颈与空档一眼可见"), body, extra_css


CHARTS = [
    ("sequence", chart_sequence),
    ("swimlane", chart_swimlane),
    ("flowchart", chart_flowchart),
    ("comparison", chart_comparison),
    ("timeline", chart_timeline),
    ("architecture", chart_architecture),
    ("dashboard", chart_dashboard),
    ("gantt", chart_gantt),
    ("org-chart", chart_org),
    ("funnel", chart_funnel),
    ("mind-map", chart_mindmap),
    ("matrix", chart_matrix),
    ("kanban", chart_kanban),
    ("checklist", chart_checklist),
    ("quote-card", chart_quote),
]


def build_html(chart_id, style_id):
    style = STYLES[style_id]
    head_html, body_html, extra_css = dict(CHARTS)[chart_id](style_id)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<link href="{FONTS[style_id]}" rel="stylesheet">
<style>
{BASE_CSS}
:root{{--bg:{style['bg']};{style['vars']}--font-head:{style['head']};--font-body:{style['body']};--font-num:{style['num']}}}
{style['css']}
{extra_css}
</style>
</head>
<body>
  <div class="wrap">
    {head_html}
    {body_html}
    {foot('内容示例：日常生活场景，用于评估形式 × 主题的搭配效果', style_id, chart_id)}
  </div>
</body>
</html>
"""


if __name__ == "__main__":
    prepare_dirs(clean_png="--clean-png" in sys.argv)
    count = 0
    for chart_id, _ in CHARTS:
        for style_id in STYLES:
            html = build_html(chart_id, style_id)
            (HTML_DIR / f"{chart_id}__{style_id}.html").write_text(html, encoding="utf-8")
            count += 1
    print(f"生成 {count} 个 HTML → {HTML_DIR}")
