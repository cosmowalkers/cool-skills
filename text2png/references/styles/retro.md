# retro — 复古像素

**Tone**: Geek、复古、像素风、8-bit
**Best for**: 技术社区配图、独立开发宣传、黑客松、游戏化展示、Side Project 发布
**Layout**: Compact, symmetric, full (same as all styles)
**Background color**: `#1a1c2e`

---

## Font Stack

```css
font-family: 'Press Start 2P', 'Noto Sans SC', cursive;  /* titles */
font-family: 'VT323', 'Noto Sans SC', monospace;          /* body */
```

Display/title: `'Press Start 2P', cursive` — weight 400 (only weight available, inherently bold)
Body: `'VT323', 'Noto Sans SC', monospace` — weight 400
Numbers/stats: `'Press Start 2P', cursive` — weight 400

**Load via Google Fonts**:
```html
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&family=Noto+Sans+SC:wght@400;500&display=swap" rel="stylesheet">
```

---

## CSS Variables

```css
:root {
  --bg: #1a1c2e;
  --card-bg: #252840;
  --card-bg-alt: #1e2038;
  --text-primary: #e8e8e8;
  --text-secondary: #a0a0b0;
  --text-muted: #606078;
  --border-base: #3a3c5a;

  --pixel-green: #4af626;
  --pixel-amber: #ffb000;
  --pixel-pink: #ff2d95;
  --pixel-cyan: #00e5ff;
  --pixel-red: #ff3333;
  --pixel-blue: #4488ff;

  --s1: #4af626;
  --s2: #ffb000;
  --s3: #ff2d95;
  --s4: #00e5ff;
  --s5: #4488ff;
  --s6: #ff3333;
  --s7: #b366ff;

  --scanline-opacity: 0.03;
}
```

---

## Base Layout

```css
body {
  font-family: 'VT323', 'Noto Sans SC', monospace;
  background: var(--bg);
  /* CRT scanline effect */
  background-image: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, var(--scanline-opacity)) 2px,
    rgba(0, 0, 0, var(--scanline-opacity)) 4px
  );
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 24px 20px;
  color: var(--text-primary);
}
.wrap {
  width: 860px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
```

---

## Components

### Title
```css
.page-title {
  font-family: 'Press Start 2P', cursive;
  font-size: 16px;
  color: var(--pixel-green);
  text-shadow: 0 0 8px rgba(74, 246, 38, 0.4);
  letter-spacing: 1px;
  line-height: 1.6;
}
.page-sub {
  font-family: 'VT323', monospace;
  font-size: 18px;
  color: var(--text-secondary);
  margin-top: 4px;
}
```

### Card
```css
.card {
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 0;
  padding: 14px 16px;
}
```

### Pixel-Border Card (signature element)
```css
.card.pixel {
  border: 2px solid var(--pixel-green);
  box-shadow:
    4px 4px 0 0 rgba(74, 246, 38, 0.2),
    inset 0 0 0 1px rgba(74, 246, 38, 0.1);
}
```

### Terminal Card
```css
.card.terminal {
  background: #0a0c18;
  border: 1px solid var(--pixel-green);
  font-family: 'VT323', monospace;
  color: var(--pixel-green);
}
.card.terminal::before {
  content: '> ';
  opacity: 0.6;
}
```

### Stats
```css
.stat-num {
  font-family: 'Press Start 2P', cursive;
  font-size: 20px;
  color: var(--pixel-amber);
  text-shadow: 0 0 6px rgba(255, 176, 0, 0.3);
}
.stat-label {
  font-family: 'VT323', monospace;
  font-size: 16px;
  color: var(--text-secondary);
  margin-top: 4px;
}
```

### Badge / Tag
```css
.badge {
  display: inline-block;
  background: transparent;
  color: var(--pixel-cyan);
  border: 1px solid var(--pixel-cyan);
  border-radius: 0;
  padding: 2px 8px;
  font-family: 'VT323', monospace;
  font-size: 14px;
}
```

### Progress Bar (pixel style)
```css
.pixel-bar {
  height: 12px;
  background: var(--card-bg-alt);
  border: 1px solid var(--border-base);
  border-radius: 0;
  position: relative;
}
.pixel-bar::after {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: var(--pct);
  background: repeating-linear-gradient(
    90deg,
    var(--pixel-green) 0px,
    var(--pixel-green) 6px,
    transparent 6px,
    transparent 8px
  );
}
```

### Connectors
```css
.connector line {
  stroke: var(--border-base);
  stroke-width: 2;
  stroke-dasharray: 4 4;
}
.connector.highlight line {
  stroke: var(--pixel-green);
  stroke-width: 2;
}
```

### Arrow (pixel style)
```html
<div style="display:flex;align-items:center;justify-content:center;height:24px;">
  <svg width="16" height="20" viewBox="0 0 16 20" fill="none">
    <rect x="7" y="0" width="2" height="12" fill="#4af626"/>
    <rect x="5" y="10" width="6" height="2" fill="#4af626"/>
    <rect x="3" y="12" width="2" height="2" fill="#4af626"/>
    <rect x="11" y="12" width="2" height="2" fill="#4af626"/>
    <rect x="7" y="14" width="2" height="2" fill="#4af626"/>
    <rect x="5" y="16" width="2" height="2" fill="#4af626"/>
    <rect x="9" y="16" width="2" height="2" fill="#4af626"/>
  </svg>
</div>
```

### Banner
```css
.banner {
  background: var(--card-bg-alt);
  border: 1px solid var(--pixel-amber);
  border-radius: 0;
  padding: 12px 24px;
  text-align: center;
  font-family: 'VT323', monospace;
  font-size: 18px;
  color: var(--pixel-amber);
}
.banner em {
  color: var(--pixel-green);
  text-shadow: 0 0 6px rgba(74, 246, 38, 0.3);
  font-style: normal;
  font-weight: 400;
}
```

---

## Design Rules

- **Zero border-radius**: Hard pixel edges everywhere — no rounded corners
- **Pixel fonts**: Press Start 2P for titles (smaller font-size needed, 14-16px), VT323 for body (larger, 16-18px)
- **CRT scanlines**: Subtle repeating-linear-gradient on body simulates old monitor
- **Neon text glow**: `text-shadow` with accent color at 30-40% opacity for key elements
- **Pixelated elements**: Arrows use `<rect>` SVG blocks instead of smooth paths
- **Color palette**: Terminal green as primary, amber for numbers, pink/cyan for accents
- **Hard shadows**: `4px 4px 0` offset shadows (pixel-perfect, no blur)
- **Dashed connectors**: `stroke-dasharray: 4 4` gives connectors a bitmap feel
- **No gradients**: Solid colors only — gradients break the pixel aesthetic
- **Segmented progress bars**: Use repeating-linear-gradient for blocky fill effect

---

## Special Effects

- CRT scanline overlay via repeating-linear-gradient on body
- Neon text-shadow glow on titles and key numbers
- Hard pixel drop-shadows (4px offset, no blur)
- Pixelated SVG arrows using `<rect>` elements
- Segmented/blocky progress bars
- Terminal-style cards with green-on-black aesthetic
- Optional: screen flicker animation (CSS `@keyframes` with opacity pulse — use sparingly)
