# Checklist — 清单卡

上线 checklist、审核清单、确认事项、待办列表、核查表。

---

## Layout

```
[Title + Progress Bar]
[Group A]                    [Group B]
  ✓ Item 1                     ✓ Item 5
  ✓ Item 2                     ○ Item 6
  ○ Item 3                     ○ Item 7
  ○ Item 4
[Summary Banner: 4/7 completed]
```

Single or dual-column grouped checklist with progress indication.

---

## HTML Structure

```html
<div class="wrap">
  <div class="page-title">上线前 Checklist</div>
  <div class="page-sub">v2.3.0 发布检查清单</div>

  <!-- Progress bar -->
  <div class="cl-progress">
    <div class="cl-progress-bar" style="--pct: 57%;"></div>
    <div class="cl-progress-text">4 / 7 已完成</div>
  </div>

  <div class="cl-grid">
    <!-- Group A -->
    <div class="cl-group">
      <div class="cl-group-title">代码质量</div>
      <div class="cl-items">
        <div class="cl-item done">
          <span class="cl-check">✓</span>
          <span class="cl-text">单元测试覆盖率 ≥ 80%</span>
        </div>
        <div class="cl-item done">
          <span class="cl-check">✓</span>
          <span class="cl-text">ESLint 0 errors</span>
        </div>
        <div class="cl-item done">
          <span class="cl-check">✓</span>
          <span class="cl-text">Code Review 已通过</span>
        </div>
        <div class="cl-item pending">
          <span class="cl-check">○</span>
          <span class="cl-text">性能基准无回退</span>
        </div>
      </div>
    </div>

    <!-- Group B -->
    <div class="cl-group">
      <div class="cl-group-title">部署检查</div>
      <div class="cl-items">
        <div class="cl-item done">
          <span class="cl-check">✓</span>
          <span class="cl-text">灰度环境验证通过</span>
        </div>
        <div class="cl-item pending">
          <span class="cl-check">○</span>
          <span class="cl-text">回滚方案已确认</span>
        </div>
        <div class="cl-item pending">
          <span class="cl-check">○</span>
          <span class="cl-text">监控告警已配置</span>
        </div>
      </div>
    </div>
  </div>

  <div class="banner">状态: <em>进行中</em> — 需完成剩余 3 项后方可发布</div>
</div>
```

---

## CSS

```css
/* Progress bar */
.cl-progress {
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.cl-progress-bar {
  flex: 1;
  height: 8px;
  background: var(--border-base);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}
.cl-progress-bar::after {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: var(--pct);
  background: var(--success, #4a8c5c);
  border-radius: 4px;
}
.cl-progress-text {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
}

/* Grid layout */
.cl-grid {
  display: flex;
  gap: 12px;
}
.cl-group {
  flex: 1;
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 10px;
  padding: 14px 16px;
}
.cl-group-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-base);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Items */
.cl-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.cl-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12.5px;
  line-height: 1.4;
}
.cl-check {
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  width: 18px;
  text-align: center;
}
.cl-item.done .cl-check { color: var(--success, #4a8c5c); }
.cl-item.pending .cl-check { color: var(--text-muted); }
.cl-item.done .cl-text { color: var(--text-primary); }
.cl-item.pending .cl-text { color: var(--text-secondary); }
```

---

## Variants

### Single Column

For shorter checklists (≤ 6 items), use single column:
```css
.cl-grid { flex-direction: column; }
```

### With Notes

Add notes/context below items:
```html
<div class="cl-item done">
  <span class="cl-check">✓</span>
  <div class="cl-content">
    <span class="cl-text">灰度环境验证通过</span>
    <span class="cl-note">4/28 @Alice 验证，无异常</span>
  </div>
</div>
```
```css
.cl-note { font-size: 10px; color: var(--text-muted); display: block; margin-top: 2px; }
```

### Blocked Items

Show items that are blocked:
```css
.cl-item.blocked .cl-check { color: var(--critical, #b83232); }
.cl-item.blocked .cl-text { color: var(--critical, #b83232); }
```

### Priority Badges

Add urgency to pending items:
```html
<span class="cl-priority high">P0</span>
```

---

## Key Rules

1. **Progress bar at top**: Visual snapshot of completion status
2. **Grouped by category**: Dual-column when ≥ 6 items, single column when fewer
3. **Clear done/pending states**: ✓ green for done, ○ muted for pending
4. **Group title is uppercase**: Clear visual separation between groups
5. **Equal column width** (`flex: 1`): Groups are symmetric
6. **Item gap**: 8px between items within a group
7. **Summary banner**: States overall status and remaining actions
8. **Content enrichment**: If user provides bare list, add group headers and progress stats
