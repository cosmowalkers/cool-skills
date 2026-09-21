# corporate — 商务正式

**Tone**: 专业、权威、值得信赖
**Best for**: 向上汇报、客户方案、投标文档、正式报告、商业计划书
**Layout**: Compact, symmetric, full (same as all styles)
**Background color**: `#f4f6f9`

---

## Font Stack

```css
font-family: 'Manrope', 'Noto Sans SC', sans-serif;
```

Display/title: `'Manrope', 'Noto Sans SC', sans-serif` — weight 700-800
Body: `'Manrope', 'Noto Sans SC', sans-serif` — weight 400-500
Numbers: `'Manrope', sans-serif` — weight 800
Labels: `'Manrope', sans-serif` — weight 600, uppercase

**Load via Google Fonts**:
```html
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
```

---

## CSS Variables

```css
:root {
  --bg: #f4f6f9;
  --card-bg: #ffffff;
  --text-primary: #1e2a3b;
  --text-secondary: #4a5568;
  --text-muted: #8a95a5;
  --border-base: #e2e8f0;
  --border-strong: #1e3a5f;

  --corp-navy: #1e3a5f;
  --corp-blue: #2563eb;
  --corp-light-blue: #dbeafe;
  --corp-gold: #b8860b;
  --corp-green: #059669;
  --corp-red: #dc2626;

  --s1: #1e3a5f;
  --s2: #2563eb;
  --s3: #059669;
  --s4: #b8860b;
  --s5: #6366f1;
  --s6: #0891b2;
  --s7: #7c3aed;
}
```

---

## Base Layout

```css
body {
  font-family: 'Manrope', 'Noto Sans SC', sans-serif;
  background: var(--bg);
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
  font-size: 22px;
  font-weight: 800;
  color: var(--corp-navy);
  letter-spacing: -0.02em;
}
.page-sub {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}
```

### Card
```css
.card {
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 6px;
  padding: 14px 16px;
}
```

### Left-Accent Card (signature element)
```css
.card.accent-left {
  border-left: 3px solid var(--corp-navy);
}
```

### Table Header Style
```css
.table-header {
  background: var(--corp-navy);
  color: #ffffff;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 14px;
  border-radius: 6px 6px 0 0;
}
```

### Stats
```css
.stat-card {
  flex: 1;
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 6px;
  padding: 14px 16px;
  text-align: center;
  border-top: 3px solid var(--accent, var(--corp-navy));
}
.stat-num {
  font-size: 28px;
  font-weight: 800;
  color: var(--corp-navy);
}
.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-top: 2px;
}
.stat-trend {
  font-size: 11px;
  font-weight: 600;
  margin-top: 4px;
}
.stat-trend.up { color: var(--corp-green); }
.stat-trend.down { color: var(--corp-red); }
```

### Badge
```css
.badge {
  display: inline-block;
  background: var(--corp-light-blue);
  color: var(--corp-navy);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
}
```

### Connectors
```css
.connector line {
  stroke: var(--border-base);
  stroke-width: 1.5;
}
.connector.highlight line {
  stroke: var(--corp-navy);
  stroke-width: 1.5;
}
```

### Banner
```css
.banner {
  background: var(--corp-navy);
  border-radius: 6px;
  padding: 14px 24px;
  text-align: center;
  color: #e8eef5;
  font-size: 13px;
  font-weight: 600;
}
.banner em { color: var(--corp-gold); font-style: normal; font-weight: 700; }
```

---

## Design Rules

- **Navy as anchor color**: `#1e3a5f` dominates headers, borders, numbers — conveys authority
- **Minimal decoration**: No shadows, no gradients on cards, no textures — pure clean corporate
- **Thin borders**: 1px base borders (not 1.5px), 3px only for left-accent cards
- **Small border-radius**: 6px maximum — sharp enough to feel business-formal
- **Table-like headers**: Dark navy backgrounds with white text for section labels
- **Gold accent sparingly**: Only for emphasis in banners or key metrics
- **High contrast text**: Dark navy on white, easy to read in any context (projected, printed)
- **No emoji in titles**: Use text labels instead — corporate context demands formality
- **Uppercase labels**: 10-11px, letter-spacing 0.5px, for section headers and categories

---

## Special Effects

None. Corporate style derives authority from restraint:
- Clean white cards on subtle blue-gray background
- Navy top-border on stat cards (3px accent line)
- Left-accent borders for highlighted cards
- Table-style dark headers for structured data
- No shadows, no blur, no glow — pure typographic hierarchy
