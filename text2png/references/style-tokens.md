# Style Tokens（自动生成）

> 由 `tools/build-style-tokens.py` 从 `tools/_content.py` 的 `STYLES` 导出，共 18 套风格。
> **这是风格定义的唯一真源**：生成 HTML 时直接取对应风格的 `bg` / 字体 / `vars` / `css`，
> 截图 `--bg` 传同一色值（或省略，让 screenshot.ts 自动读取 HTML 的 `:root{--bg}`）。

## 速查表

| Style | 名称 | bg | 标题字体 | 正文字体 | 数字字体 |
|-------|------|----|----------|----------|----------|
| `warm` | 暖橙报告 | `#faf6ee` | 'Playfair Display','Noto Serif SC',serif | 'Noto Sans SC',sans-serif | 'Playfair Display',serif |
| `editorial` | 杂志排版 | `#f8f9fa` | 'Cormorant Garamond','Noto Serif SC',serif | 'Lora','Noto Serif SC',serif | 'Cormorant Garamond',serif |
| `macaron` | 马卡龙甜品 | `#fef9f9` | 'Quicksand','Noto Sans SC',sans-serif | 'Nunito','Noto Sans SC',sans-serif | 'Quicksand',sans-serif |
| `brutalist` | 新粗野主义 | `#ffffff` | 'Space Grotesk','Noto Sans SC',sans-serif | 'Space Grotesk','Noto Sans SC',sans-serif | 'Space Grotesk',sans-serif |
| `ocean` | 海洋微风 | `#f5f9fc` | 'Outfit','Noto Sans SC',sans-serif | 'Outfit','Noto Sans SC',sans-serif | 'Outfit',sans-serif |
| `paper` | 手绘涂鸦 | `#f3f5f9` | 'Caveat','ZCOOL XiaoWei',cursive | 'Nunito','Noto Sans SC',sans-serif | 'Caveat',cursive |
| `art-nouveau` | 新艺术运动 | `#f2f5f0` | 'Italiana','Noto Serif SC',serif | 'Cormorant Garamond','Noto Serif SC',serif | 'Italiana',serif |
| `swiss` | 瑞士国际主义 | `#ffffff` | 'Inter','Noto Sans SC',sans-serif | 'Inter','Noto Sans SC',sans-serif | 'Inter',sans-serif |
| `psychedelic` | 迷幻风格 | `#fafafe` | 'Righteous','Noto Sans SC',sans-serif | 'Ubuntu','Noto Sans SC',sans-serif | 'Righteous',sans-serif |
| `cyberpunk` | 赛博朋克 | `#0b0914` | 'Orbitron',sans-serif | 'Rajdhani','Noto Sans SC',sans-serif | 'Orbitron',sans-serif |
| `midnight` | 午夜蓝调 | `#080d1f` | 'Manrope','Noto Sans SC',sans-serif | 'DM Sans','Noto Sans SC',sans-serif | 'Manrope',sans-serif |
| `dracula` | 德古拉暗紫 | `#282a36` | 'Source Sans 3','Noto Sans SC',sans-serif | 'Source Sans 3','Noto Sans SC',sans-serif | 'Fira Code',monospace |
| `neo-chinese` | 新中式 | `#16162b` | 'ZCOOL XiaoWei','Noto Serif SC',serif | 'Noto Serif SC','Noto Sans SC',serif | 'ZCOOL XiaoWei',serif |
| `terminal` | 终端黑客 | `#0a0a0a` | 'VT323',monospace | 'Share Tech Mono','Noto Sans SC',monospace | 'VT323',monospace |
| `cosmic` | 深空星云 | `#06060f` | 'Orbitron',sans-serif | 'Exo 2','Noto Sans SC',sans-serif | 'Orbitron',sans-serif |
| `industrial` | 工业金属 | `#1a1a1c` | 'Bebas Neue','Noto Sans SC',sans-serif | 'Roboto Condensed','Noto Sans SC',sans-serif | 'Bebas Neue',sans-serif |
| `flat` | 扁平设计 | `#f5f5f5` | 'Nunito','Noto Sans SC',sans-serif | 'Nunito','Noto Sans SC',sans-serif | 'Nunito',sans-serif |
| `glass` | 玻璃拟态 | `#f0f2f7` | 'Outfit','Noto Sans SC',sans-serif | 'Outfit','Noto Sans SC',sans-serif | 'Outfit',sans-serif |

## 风格定义明细

### warm — 暖橙报告

- **bg**: `#faf6ee`
- **fonts**: head `'Playfair Display','Noto Serif SC',serif` / body `'Noto Sans SC',sans-serif` / num `'Playfair Display',serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#2e2410;--text2:#6a5a40;--muted:#a08060;--line:#e2d8c4;--arrow:#c0a06a;--a1:#c0622a;--a2:#b08830;--a3:#8a6a2a;--a4:#a04a2a;--radius:12px; }
```

- **风格专属 CSS**:

```css
.wrap{background-image:url("data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E")}.card{border:1px solid var(--line);box-shadow:0 1px 2px rgba(120,90,50,.06)}.card.hi{border-color:var(--a1);box-shadow:0 3px 10px rgba(192,98,42,.16)}.kicker{color:var(--a2)}
```

### editorial — 杂志排版

- **bg**: `#f8f9fa`
- **fonts**: head `'Cormorant Garamond','Noto Serif SC',serif` / body `'Lora','Noto Serif SC',serif` / num `'Cormorant Garamond',serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Lora:wght@400;500;600&family=Libre+Franklin:wght@400;500;600&family=Noto+Serif+SC:wght@500;700&family=Noto+Sans+SC:wght@400;500&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#1a1a1a;--text2:#555;--muted:#999;--line:#dee2e6;--rule:#c0392b;--arrow:#222;--a1:#c0392b;--a2:#2c3e50;--a3:#8e7c3a;--a4:#567;--radius:2px; }
```

- **风格专属 CSS**:

```css
.title{font-size:34px;font-weight:700;letter-spacing:-.01em}.card{border:0;border-top:2px solid var(--rule);border-radius:0;padding:14px 16px}.card.hi{border-top-width:4px}.kicker,.tag{font-family:'Libre Franklin',sans-serif;font-size:10px;text-transform:uppercase;letter-spacing:.18em;color:var(--rule)}.badge{background:transparent;color:var(--rule);border:1px solid var(--rule);font-family:'Libre Franklin',sans-serif}
```

### macaron — 马卡龙甜品

- **bg**: `#fef9f9`
- **fonts**: head `'Quicksand','Noto Sans SC',sans-serif` / body `'Nunito','Noto Sans SC',sans-serif` / num `'Quicksand',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Nunito:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#4a3f3f;--text2:#8d7b7b;--muted:#c4b5b5;--line:#f0e0e0;--arrow:#ffaaa5;--a1:#ffaaa5;--a2:#a8e6cf;--a3:#ffd3b6;--a4:#ffefa1;--radius:22px; }
```

- **风格专属 CSS**:

```css
.title{font-size:30px;font-weight:700;color:#6b5a5a}.card{border:2px solid var(--line);box-shadow:0 3px 12px rgba(255,170,165,.15);padding:16px 18px}.card.hi{border-color:var(--a1);background:#fff0f0;box-shadow:0 4px 18px rgba(255,170,165,.25)}.kicker,.tag{font-size:12px;text-transform:none;letter-spacing:.04em;color:var(--a1);font-weight:700}.badge{background:var(--a2);color:#4a7c6b;border-radius:99px;font-weight:700}.num{color:var(--a1)}
```

### brutalist — 新粗野主义

- **bg**: `#ffffff`
- **fonts**: head `'Space Grotesk','Noto Sans SC',sans-serif` / body `'Space Grotesk','Noto Sans SC',sans-serif` / num `'Space Grotesk',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#111;--text2:#555;--muted:#999;--line:#111;--arrow:#111;--a1:#ff3b00;--a2:#0047ff;--a3:#ffd700;--a4:#00c040;--radius:0px; }
```

- **风格专属 CSS**:

```css
.title{font-size:38px;font-weight:800;letter-spacing:-.02em;text-transform:uppercase}.card{border:4px solid var(--line);box-shadow:8px 8px 0 #111;padding:14px 18px}.card.hi{border-color:var(--a1);box-shadow:8px 8px 0 var(--a1)}.kicker,.tag{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:.02em;background:#111;color:#fff;display:inline-block;padding:2px 10px}.badge{background:var(--a2);color:#fff;border-radius:0;font-weight:800}
```

### ocean — 海洋微风

- **bg**: `#f5f9fc`
- **fonts**: head `'Outfit','Noto Sans SC',sans-serif` / body `'Outfit','Noto Sans SC',sans-serif` / num `'Outfit',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#1a3a4a;--text2:#5a7a8a;--muted:#8aaaba;--line:#d5e5f0;--arrow:#2a8ab0;--a1:#2a8ab0;--a2:#4ac0c0;--a3:#ff7b5a;--a4:#6ab0e0;--radius:12px; }
```

- **风格专属 CSS**:

```css
body{background:linear-gradient(180deg,#f0f7fb 0%,#f5f9fc 40%,#e8f2f8 100%)}.card{border:1px solid var(--line);box-shadow:0 2px 8px rgba(42,138,176,.08)}.card.hi{border-color:var(--a1);box-shadow:0 4px 16px rgba(42,138,176,.14)}.kicker,.tag{font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:var(--a2)}.badge{background:var(--a1);color:#fff}.num{color:var(--a1)}
```

### paper — 手绘涂鸦

- **bg**: `#f3f5f9`
- **fonts**: head `'Caveat','ZCOOL XiaoWei',cursive` / body `'Nunito','Noto Sans SC',sans-serif` / num `'Caveat',cursive`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Nunito:wght@400;500;600;700&family=ZCOOL+XiaoWei&family=Noto+Sans+SC:wght@400;500&display=swap`
- **CSS vars**:

```css
:root { --card:#fdfdfe;--text:#2a2830;--text2:#5a6070;--muted:#8890a0;--line:#d0d4e0;--sketch:#6b7280;--arrow:#e08850;--a1:#e08850;--a2:#5a9e6f;--a3:#8b6aad;--a4:#d8a830;--radius:8px; }
```

- **风格专属 CSS**:

```css
.title,.card h3{font-family:'Caveat','ZCOOL XiaoWei',cursive}.title{font-size:34px}.card{border:2px dashed var(--sketch);transform:rotate(-.35deg)}.card:nth-child(even){transform:rotate(.4deg)}.card.hi{border-style:solid;border-color:var(--a1)}.kicker{font-family:'Caveat',cursive;font-size:15px;letter-spacing:0;color:var(--a1)}.badge{background:var(--a2);color:#fff;transform:rotate(-2deg)}
```

### art-nouveau — 新艺术运动

- **bg**: `#f2f5f0`
- **fonts**: head `'Italiana','Noto Serif SC',serif` / body `'Cormorant Garamond','Noto Serif SC',serif` / num `'Italiana',serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Italiana&family=Cormorant+Garamond:wght@300;400;600;700&family=Noto+Serif+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#fcfdfa;--text:#283020;--text2:#6a7050;--muted:#9a9a78;--line:#d4dcd0;--curve:#6a8a48;--arrow:#7a8a40;--a1:#7a8a40;--a2:#c8a050;--a3:#8868a0;--a4:#5090a0;--radius:16px 4px 16px 4px; }
```

- **风格专属 CSS**:

```css
.title{font-size:34px;font-weight:400;font-style:italic;color:#5a7a38}.card{border:0;border-left:3px solid var(--curve);border-radius:0 20px 20px 0;padding:14px 18px}.card.hi{border-left-width:6px;border-left-color:var(--a3)}.kicker,.tag{font-family:'Italiana',serif;font-size:12px;text-transform:none;font-style:italic;letter-spacing:.06em;color:var(--a2)}.wrap{background-image:url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M10 30 Q30 5 50 30' fill='none' stroke='%237a8a40' stroke-width='.5' opacity='.08'/%3E%3Cpath d='M10 35 Q30 55 50 35' fill='none' stroke='%23c8a050' stroke-width='.5' opacity='.08'/%3E%3C/svg%3E")}.badge{background:transparent;color:var(--a3);border:1px solid var(--a3)}
```

### swiss — 瑞士国际主义

- **bg**: `#ffffff`
- **fonts**: head `'Inter','Noto Sans SC',sans-serif` / body `'Inter','Noto Sans SC',sans-serif` / num `'Inter',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#fafafa;--text:#111;--text2:#666;--muted:#aaa;--line:#e5e5e5;--strong:#111;--arrow:#111;--a1:#111;--a2:#e03a3a;--a3:#1a6ab5;--a4:#666;--radius:0px; }
```

- **风格专属 CSS**:

```css
.title{font-size:40px;font-weight:300;letter-spacing:-.03em}.card{border:0;border-top:1px solid var(--line);padding:14px 0}.card:last-child{border-bottom:1px solid var(--line)}.card.hi{border-top:3px solid var(--a2);border-bottom:0}.kicker,.tag{font-family:'Inter',sans-serif;font-size:9px;text-transform:uppercase;letter-spacing:.3em;font-weight:700}.badge{background:var(--a3);color:#fff;border-radius:0;font-weight:600}
```

### psychedelic — 迷幻风格

- **bg**: `#fafafe`
- **fonts**: head `'Righteous','Noto Sans SC',sans-serif` / body `'Ubuntu','Noto Sans SC',sans-serif` / num `'Righteous',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Righteous&family=Ubuntu:wght@300;400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#2a1a4a;--text2:#6a5a8a;--muted:#9a8aba;--line:#e8e4f0;--arrow:#d04090;--a1:#e04080;--a2:#40a0e0;--a3:#e0a020;--a4:#40c060;--radius:20px 5px 20px 5px; }
```

- **风格专属 CSS**:

```css
.title{font-size:36px;letter-spacing:.04em;background:linear-gradient(90deg,var(--a1),var(--a2),var(--a3),var(--a4),var(--a1));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}.card{border:0;background:linear-gradient(135deg,var(--card) 0%,color-mix(in srgb,var(--a1) 1%,var(--card)) 100%);box-shadow:0 2px 8px rgba(120,60,100,.08)}.card.hi{box-shadow:0 4px 16px rgba(224,64,128,.18)}.kicker,.tag{font-size:11px;text-transform:uppercase;letter-spacing:.14em;color:var(--a2)}.wrap{background:conic-gradient(from 0deg at 10% 10%,rgba(224,64,128,.03) 0 90deg,rgba(64,160,224,.03) 90deg 180deg,rgba(224,160,32,.03) 180deg 270deg,rgba(64,192,96,.03) 270deg)}.badge{background:var(--a1);color:#fff}
```

### cyberpunk — 赛博朋克

- **bg**: `#0b0914`
- **fonts**: head `'Orbitron',sans-serif` / body `'Rajdhani','Noto Sans SC',sans-serif` / num `'Orbitron',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:rgba(18,14,32,.92);--text:#d8d0ff;--text2:#8b88a0;--muted:#4a4760;--line:rgba(0,255,255,.22);--arrow:#00ffff;--a1:#00ffff;--a2:#ff00ff;--a3:#ffff00;--a4:#00ff88;--radius:4px; }
```

- **风格专属 CSS**:

```css
body{background:linear-gradient(180deg,#0b0914 0%,#121025 100%)}.wrap{background-image:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,255,.03) 2px,rgba(0,255,255,.03) 4px)}.title{text-transform:uppercase;letter-spacing:.08em;text-shadow:0 0 20px rgba(0,255,255,.45),0 0 60px rgba(0,255,255,.15)}.card{border:1px solid var(--line);box-shadow:0 0 16px rgba(0,255,255,.1),inset 0 0 20px rgba(0,255,255,.04)}.card.hi{border-color:var(--a1);box-shadow:0 0 24px rgba(0,255,255,.25)}.kicker,.tag{font-family:'Share Tech Mono',monospace;color:var(--a2);text-transform:uppercase;letter-spacing:.1em}.badge{color:#000;background:var(--a1)}
```

### midnight — 午夜蓝调

- **bg**: `#080d1f`
- **fonts**: head `'Manrope','Noto Sans SC',sans-serif` / body `'DM Sans','Noto Sans SC',sans-serif` / num `'Manrope',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=DM+Sans:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#0f1830;--text:#e2e0f0;--text2:#8a8daa;--muted:#5a5d7a;--line:#1a2440;--arrow:#c9a84c;--a1:#c9a84c;--a2:#5b8dd9;--a3:#e8c97a;--a4:#4a6fa5;--radius:8px; }
```

- **风格专属 CSS**:

```css
.title{font-weight:300;letter-spacing:.06em;color:#f0e6c8}.card{border:1px solid var(--line);box-shadow:0 2px 8px rgba(0,0,0,.3)}.card.hi{border-color:var(--a1);box-shadow:0 0 0 1px var(--a1),0 4px 16px rgba(201,168,76,.15)}.kicker,.tag{font-size:10px;text-transform:uppercase;letter-spacing:.16em;color:var(--a1);font-weight:600}.badge{background:var(--a1);color:#080d1f;font-weight:700}.num{color:var(--a1)}
```

### dracula — 德古拉暗紫

- **bg**: `#282a36`
- **fonts**: head `'Source Sans 3','Noto Sans SC',sans-serif` / body `'Source Sans 3','Noto Sans SC',sans-serif` / num `'Fira Code',monospace`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Source+Sans+3:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#343746;--text:#f8f8f2;--text2:#6272a4;--muted:#44475a;--line:#44475a;--arrow:#bd93f9;--a1:#bd93f9;--a2:#50fa7b;--a3:#ff79c6;--a4:#f1fa8c;--radius:8px; }
```

- **风格专属 CSS**:

```css
.card{border:0;box-shadow:0 1px 3px rgba(0,0,0,.35)}.card.hi{box-shadow:0 0 0 2px var(--a1)}.kicker,.tag{font-family:'Fira Code',monospace;font-size:10px;color:var(--a3);text-transform:uppercase;letter-spacing:.06em}.title{color:var(--a3)}
```

### neo-chinese — 新中式

- **bg**: `#16162b`
- **fonts**: head `'ZCOOL XiaoWei','Noto Serif SC',serif` / body `'Noto Serif SC','Noto Sans SC',serif` / num `'ZCOOL XiaoWei',serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei&family=Noto+Serif+SC:wght@400;500;700;900&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#22203a;--text:#e8d5b7;--text2:#a09888;--muted:#6a6258;--line:#2a2838;--arrow:#c73e3a;--a1:#c73e3a;--a2:#d4a853;--a3:#2d5a87;--a4:#8b5e3c;--radius:6px; }
```

- **风格专属 CSS**:

```css
.title{font-size:32px;font-weight:400;color:var(--a2);letter-spacing:.06em}.card{border:1px solid var(--line);border-left:3px solid var(--a1);padding:14px 18px}.card.hi{border-left-color:var(--a2);border-left-width:5px;background:rgba(212,168,83,.06)}.kicker,.tag{font-family:'ZCOOL XiaoWei',serif;font-size:12px;letter-spacing:.12em;color:var(--a1)}.num{color:var(--a2)}
```

### terminal — 终端黑客

- **bg**: `#0a0a0a`
- **fonts**: head `'VT323',monospace` / body `'Share Tech Mono','Noto Sans SC',monospace` / num `'VT323',monospace`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=VT323&family=Noto+Sans+SC:wght@400;500&display=swap`
- **CSS vars**:

```css
:root { --card:#121212;--text:#33ff33;--text2:#22cc22;--muted:#116611;--line:#1a3a1a;--arrow:#ffaa00;--a1:#33ff33;--a2:#ffaa00;--a3:#ff3333;--a4:#33ccff;--radius:0px; }
```

- **风格专属 CSS**:

```css
.wrap{background-image:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(51,255,51,.03) 2px,rgba(51,255,51,.03) 4px)}.title{font-size:22px;color:var(--a2);text-shadow:0 0 8px rgba(255,170,0,.5)}.title::before{content:'> ';color:var(--a1)}.card{border:1px solid var(--line);box-shadow:inset 0 0 12px rgba(51,255,51,.06)}.card.hi{border-color:var(--a1);box-shadow:inset 0 0 16px rgba(51,255,51,.1),0 0 8px rgba(51,255,51,.15)}.kicker,.tag{font-family:'VT323',monospace;font-size:14px;color:var(--a2);text-transform:uppercase}.badge{background:var(--a2);color:#000}
```

### cosmic — 深空星云

- **bg**: `#06060f`
- **fonts**: head `'Orbitron',sans-serif` / body `'Exo 2','Noto Sans SC',sans-serif` / num `'Orbitron',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Exo+2:wght@200;300;400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:rgba(14,10,30,.9);--text:#d0d8ff;--text2:#8888cc;--muted:#444466;--line:rgba(100,120,220,.2);--arrow:#88aaff;--a1:#88aaff;--a2:#dd88ff;--a3:#ff88aa;--a4:#aaddff;--radius:12px; }
```

- **风格专属 CSS**:

```css
body{background:linear-gradient(180deg,#06060f 0%,#0a0a22 30%,#0f0f2e 60%,#0a0a1a 100%)}.wrap{background:radial-gradient(600px 400px at 10% 20%,rgba(136,170,255,.06),transparent),radial-gradient(500px 350px at 80% 70%,rgba(221,136,255,.05),transparent),radial-gradient(400px 300px at 40% 40%,rgba(255,136,170,.04),transparent)}.title{font-weight:300;letter-spacing:.12em;text-transform:uppercase;text-shadow:0 0 30px rgba(136,170,255,.3)}.card{border:1px solid var(--line);box-shadow:0 0 20px rgba(100,120,220,.08),inset 0 0 20px rgba(100,120,220,.03)}.card.hi{border-color:var(--a2);box-shadow:0 0 24px rgba(221,136,255,.15)}.kicker,.tag{font-family:'Orbitron',sans-serif;font-size:9px;text-transform:uppercase;letter-spacing:.2em;color:var(--a2)}.badge{background:var(--a2);color:#06060f}
```

### industrial — 工业金属

- **bg**: `#1a1a1c`
- **fonts**: head `'Bebas Neue','Noto Sans SC',sans-serif` / body `'Roboto Condensed','Noto Sans SC',sans-serif` / num `'Bebas Neue',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#242428;--text:#e0e0e0;--text2:#888;--muted:#555;--line:#333;--arrow:#ff6600;--a1:#ff6600;--a2:#ffaa00;--a3:#cc3300;--a4:#888;--radius:2px; }
```

- **风格专属 CSS**:

```css
.wrap{background-image:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,.015) 3px,rgba(255,255,255,.015) 4px)}.title{font-size:44px;font-weight:400;letter-spacing:.04em;text-transform:uppercase;color:var(--a1);border-bottom:4px solid var(--a1);padding-bottom:6px}.card{border:2px solid var(--line);box-shadow:inset 0 0 0 1px rgba(255,255,255,.03)}.card.hi{border-color:var(--a1);background:rgba(255,102,0,.04)}.kicker,.tag{font-family:'Roboto Condensed',sans-serif;font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--a2)}.badge{background:var(--a1);color:#000;font-weight:700;border-radius:0}
```

### flat — 扁平设计

- **bg**: `#f5f5f5`
- **fonts**: head `'Nunito','Noto Sans SC',sans-serif` / body `'Nunito','Noto Sans SC',sans-serif` / num `'Nunito',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:#ffffff;--text:#333;--text2:#777;--muted:#aaa;--line:#e8e8e8;--arrow:#3498db;--a1:#3498db;--a2:#2ecc71;--a3:#e74c3c;--a4:#f39c12;--radius:0px; }
```

- **风格专属 CSS**:

```css
.title{font-size:32px;font-weight:800;letter-spacing:-.02em}.card{border:0;border-top:4px solid var(--a1);box-shadow:none;padding:16px 20px}.card:nth-child(2n){border-top-color:var(--a2)}.card:nth-child(3n){border-top-color:var(--a3)}.card.hi{background:var(--a1)}.card.hi h3,.card.hi p{color:#fff}.kicker,.tag{font-size:12px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--a1)}.badge{background:var(--a2);color:#fff;border-radius:0;font-weight:800}
```

### glass — 玻璃拟态

- **bg**: `#f0f2f7`
- **fonts**: head `'Outfit','Noto Sans SC',sans-serif` / body `'Outfit','Noto Sans SC',sans-serif` / num `'Outfit',sans-serif`
- **Google Fonts**: `https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap`
- **CSS vars**:

```css
:root { --card:rgba(255,255,255,.62);--card2:rgba(255,255,255,.85);--text:#1a1c2a;--text2:#5a6080;--muted:#8890a8;--line:rgba(0,0,0,.08);--arrow:#5b80f0;--a1:#5b80f0;--a2:#38a068;--a3:#d07050;--a4:#8850d0;--radius:18px; }
```

- **风格专属 CSS**:

```css
body{background:radial-gradient(600px 400px at 10% 20%,rgba(91,128,240,.12),transparent),radial-gradient(500px 350px at 85% 75%,rgba(136,80,208,.08),transparent),var(--bg)}.card{border:1px solid var(--line);backdrop-filter:blur(14px);box-shadow:0 4px 16px rgba(0,0,0,.06),0 1px 3px rgba(0,0,0,.04)}.card.hi{background:var(--card2);border-color:rgba(91,128,240,.2);box-shadow:0 6px 24px rgba(91,128,240,.1)}
```
