# Matrix — 矩阵图

优先级矩阵、SWOT 分析、技能矩阵、二维分类、象限图。

---

## Layout

```
         ← Low Impact →        ← High Impact →
┌──────────────────────┬──────────────────────┐
│                      │                      │  ↑
│   Quick Wins         │   Major Projects     │  High
│   • Item A           │   • Item D           │  Effort
│   • Item B           │   • Item E           │  ↓
│                      │                      │
├──────────────────────┼──────────────────────┤
│                      │                      │  ↑
│   Fill-ins           │   Strategic Bets     │  Low
│   • Item C           │   • Item F           │  Effort
│                      │                      │  ↓
└──────────────────────┴──────────────────────┘
```

2×2 grid with axis labels, each quadrant contains categorized items.

---

## HTML Structure

```html
<div class="wrap">
  <div class="page-title">优先级矩阵</div>
  <div class="page-sub">Impact × Effort 二维决策</div>

  <div class="matrix-container">
    <!-- Y-axis label -->
    <div class="matrix-y-axis">
      <span class="axis-label-top">高收益</span>
      <span class="axis-label-bottom">低收益</span>
    </div>

    <div class="matrix-body">
      <!-- X-axis label (top) -->
      <div class="matrix-x-axis">
        <span class="axis-label-left">低成本</span>
        <span class="axis-label-right">高成本</span>
      </div>

      <!-- 2x2 Grid -->
      <div class="matrix-grid">
        <div class="matrix-cell q1" style="--cell-color: var(--s1);">
          <div class="cell-title">🎯 优先做</div>
          <div class="cell-items">
            <div class="cell-item">优化首页加载速度</div>
            <div class="cell-item">修复支付页 Bug</div>
            <div class="cell-item">添加搜索联想</div>
          </div>
        </div>
        <div class="matrix-cell q2" style="--cell-color: var(--s2);">
          <div class="cell-title">📋 规划做</div>
          <div class="cell-items">
            <div class="cell-item">重构用户系统</div>
            <div class="cell-item">国际化支持</div>
          </div>
        </div>
        <div class="matrix-cell q3" style="--cell-color: var(--s3);">
          <div class="cell-title">💡 填充做</div>
          <div class="cell-items">
            <div class="cell-item">暗色模式</div>
            <div class="cell-item">邮件模板美化</div>
          </div>
        </div>
        <div class="matrix-cell q4" style="--cell-color: var(--s4);">
          <div class="cell-title">🚫 暂不做</div>
          <div class="cell-items">
            <div class="cell-item">自建推荐引擎</div>
            <div class="cell-item">多端同步重构</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="banner">聚焦 <em>Q1（优先做）</em>，Q2 列入下季度规划</div>
</div>
```

---

## CSS

```css
.matrix-container {
  display: flex;
  gap: 8px;
}

/* Y-axis */
.matrix-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 32px 0;
  width: 20px;
}
.matrix-y-axis .axis-label-top,
.matrix-y-axis .axis-label-bottom {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.matrix-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* X-axis */
.matrix-x-axis {
  display: flex;
  justify-content: space-between;
  padding: 0 8px;
}
.matrix-x-axis .axis-label-left,
.matrix-x-axis .axis-label-right {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 1px;
}

/* 2x2 Grid */
.matrix-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 8px;
}

.matrix-cell {
  background: var(--card-bg);
  border: 1.5px solid var(--cell-color);
  border-radius: 10px;
  padding: 14px 16px;
  min-height: 120px;
}
.cell-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--cell-color);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-base);
}
.cell-items {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.cell-item {
  font-size: 12px;
  color: var(--text-secondary);
  padding-left: 8px;
  border-left: 2px solid var(--cell-color);
  line-height: 1.4;
}
```

---

## Variants

### SWOT Analysis

Labels change to Strengths/Weaknesses/Opportunities/Threats:
```html
<div class="matrix-cell q1" style="--cell-color: #4a8c5c;">
  <div class="cell-title">💪 Strengths</div>
  ...
</div>
<div class="matrix-cell q2" style="--cell-color: #b83232;">
  <div class="cell-title">⚠️ Weaknesses</div>
  ...
</div>
<div class="matrix-cell q3" style="--cell-color: #2c6e9e;">
  <div class="cell-title">🌟 Opportunities</div>
  ...
</div>
<div class="matrix-cell q4" style="--cell-color: #6a3a8c;">
  <div class="cell-title">🔥 Threats</div>
  ...
</div>
```
X-axis: Internal / External; Y-axis: Positive / Negative

### Skill Matrix (with scores)

Add score badges to each item:
```html
<div class="cell-item">
  <span class="item-text">React</span>
  <span class="item-score">★★★★☆</span>
</div>
```

### Weighted Matrix

Add a weight/priority badge to quadrant titles:
```html
<div class="cell-title">🎯 优先做 <span class="cell-weight">40%</span></div>
```

---

## Key Rules

1. **Always 2×2**: Four quadrants, equal size (`1fr 1fr`)
2. **Axis labels outside the grid**: Y-axis vertical text on left, X-axis horizontal on top
3. **Each quadrant has distinct color**: Border + title use the quadrant accent color
4. **Items left-aligned with colored left border**: Creates scannable list
5. **Quadrant order**: Top-left = Q1 (high priority), clockwise Q2-Q3-Q4
6. **Min-height on cells**: Ensures quadrants look balanced even with different item counts
7. **Gap**: 8px between cells — tight but distinct
8. **Content enrichment**: If user only provides axis labels, suggest 3-5 items per quadrant
