# Quote Card — 金句卡

读书笔记、金句分享、社交媒体配图、演讲配图、名言摘录。

---

## Layout

```
         ❝
   "The best way to predict
    the future is to invent it."

         ——————
         Alan Kay
         Computer Scientist, 1971
```

Large centered quote text with decorative elements and attribution.

---

## HTML Structure

```html
<div class="wrap">
  <div class="quote-card">
    <!-- Decorative opening mark -->
    <div class="quote-mark">"</div>

    <!-- Main quote text -->
    <div class="quote-text">
      设计不是看起来怎么样、感觉怎么样，<br>
      设计是它怎么运作的。
    </div>

    <!-- Divider -->
    <div class="quote-divider"></div>

    <!-- Attribution -->
    <div class="quote-attr">
      <div class="quote-author">Steve Jobs</div>
      <div class="quote-source">Apple Inc. 创始人</div>
    </div>

    <!-- Optional context/note -->
    <div class="quote-note">
      摘自 2003 年《纽约时报》采访
    </div>
  </div>
</div>
```

---

## CSS

```css
.wrap {
  width: 860px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px;
}

.quote-card {
  width: 100%;
  background: var(--card-bg);
  border: 1.5px solid var(--border-base);
  border-radius: 12px;
  padding: 48px 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
}

/* Decorative quote mark */
.quote-mark {
  font-size: 72px;
  line-height: 0.6;
  color: var(--accent, var(--s1));
  opacity: 0.3;
  font-family: 'Georgia', serif;
  margin-bottom: 16px;
}

/* Main quote text */
.quote-text {
  font-size: 22px;
  font-weight: 600;
  line-height: 1.6;
  color: var(--text-primary);
  max-width: 620px;
  letter-spacing: -0.01em;
}

/* Divider */
.quote-divider {
  width: 60px;
  height: 2px;
  background: var(--accent, var(--s1));
  margin: 24px 0 20px;
  border-radius: 1px;
}

/* Attribution */
.quote-attr {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.quote-author {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}
.quote-source {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Optional note */
.quote-note {
  margin-top: 16px;
  font-size: 11px;
  color: var(--text-muted);
  font-style: italic;
}
```

---

## Variants

### Multiple Quotes (Collection)

For 2-3 quotes on one card:
```html
<div class="wrap">
  <div class="page-title">本周读书摘录</div>
  <div class="page-sub">《设计心理学》精华</div>

  <div class="quote-collection">
    <div class="quote-item" style="--accent: var(--s1);">
      <div class="qi-text">"好的设计让人一看就懂。"</div>
      <div class="qi-page">— p.42</div>
    </div>
    <div class="quote-item" style="--accent: var(--s2);">
      <div class="qi-text">"复杂性不可避免，但困惑是可以避免的。"</div>
      <div class="qi-page">— p.128</div>
    </div>
    <div class="quote-item" style="--accent: var(--s3);">
      <div class="qi-text">"设计必须反映产品的核心功能。"</div>
      <div class="qi-page">— p.203</div>
    </div>
  </div>

  <div class="banner">摘自 Don Norman《设计心理学》</div>
</div>
```
```css
.quote-collection { display: flex; flex-direction: column; gap: 10px; }
.quote-item {
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  padding: 14px 18px;
}
.qi-text { font-size: 15px; font-weight: 500; color: var(--text-primary); line-height: 1.5; }
.qi-page { font-size: 11px; color: var(--text-muted); margin-top: 6px; }
```

### Social Media Style (Square)

For Instagram/WeChat sharing:
```css
.wrap { width: 860px; }
.quote-card { aspect-ratio: 1; justify-content: center; }
```

### With Background Pattern

Add subtle decorative pattern behind quote:
```css
.quote-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,...");
  border-radius: 12px;
}
```

---

## Key Rules

1. **Center everything**: Quote cards are purely center-aligned — text, divider, attribution
2. **Large quote text**: 20-24px, the quote IS the content — make it dominant
3. **Decorative quote mark**: Large, semi-transparent, sets the tone
4. **Short divider line**: 60px colored line separates quote from attribution
5. **Attribution hierarchy**: Author name bold, source/title secondary, note muted
6. **Generous padding**: 48-64px internal padding — quote cards need breathing room (exception to compact rule because the content itself is sparse)
7. **Max 2-3 sentences**: If the quote is longer, reduce font size to 18px
8. **Width stays 860px**: But content is narrower (max-width: 620px on quote text)
9. **Single quote = standalone card**: No stats row or tagline needed — the quote speaks for itself
