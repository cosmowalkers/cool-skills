# Kanban — 看板

任务状态管理、工作流可视化、项目看板、Sprint 面板。

---

## Layout

```
[Title]
[Backlog (3)]    [In Progress (2)]   [Review (1)]    [Done (4)]
┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐
│ Task A   │    │ Task D       │    │ Task F   │    │ Task G   │
│ Task B   │    │ Task E       │    │          │    │ Task H   │
│ Task C   │    │              │    │          │    │ Task I   │
│          │    │              │    │          │    │ Task J   │
└──────────┘    └──────────────┘    └──────────┘    └──────────┘
[Summary Banner]
```

Horizontal columns (3-5) with stacked task cards inside each column.

---

## HTML Structure

```html
<div class="wrap">
  <div class="page-title">Sprint #12 看板</div>
  <div class="page-sub">2026-04-28 — 2026-05-09</div>

  <div class="kanban">
    <!-- Column: Backlog -->
    <div class="kb-col" style="--col-color: var(--s1);">
      <div class="kb-col-header">
        <span class="kb-col-title">待办</span>
        <span class="kb-col-count">3</span>
      </div>
      <div class="kb-cards">
        <div class="kb-card">
          <div class="kb-card-title">用户头像上传功能</div>
          <div class="kb-card-meta">
            <span class="kb-tag">Feature</span>
            <span class="kb-owner">@Alice</span>
          </div>
        </div>
        <div class="kb-card">
          <div class="kb-card-title">修复登录页白屏</div>
          <div class="kb-card-meta">
            <span class="kb-tag urgent">Bug</span>
            <span class="kb-owner">@Bob</span>
          </div>
        </div>
        <div class="kb-card">
          <div class="kb-card-title">性能监控接入</div>
          <div class="kb-card-meta">
            <span class="kb-tag">Infra</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Column: In Progress -->
    <div class="kb-col" style="--col-color: var(--s3);">
      <div class="kb-col-header">
        <span class="kb-col-title">进行中</span>
        <span class="kb-col-count">2</span>
      </div>
      <div class="kb-cards">
        <div class="kb-card">
          <div class="kb-card-title">订单列表分页</div>
          <div class="kb-card-meta">
            <span class="kb-tag">Feature</span>
            <span class="kb-owner">@Charlie</span>
          </div>
        </div>
        <div class="kb-card">
          <div class="kb-card-title">API 限流中间件</div>
          <div class="kb-card-meta">
            <span class="kb-tag">Infra</span>
            <span class="kb-owner">@Alice</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Column: Done -->
    <div class="kb-col" style="--col-color: var(--s5);">
      <div class="kb-col-header">
        <span class="kb-col-title">已完成</span>
        <span class="kb-col-count">4</span>
      </div>
      <div class="kb-cards">
        <div class="kb-card done">
          <div class="kb-card-title">登录流程重构</div>
          <div class="kb-card-meta">
            <span class="kb-tag">Feature</span>
            <span class="kb-owner">@Bob</span>
          </div>
        </div>
        <!-- ... more cards ... -->
      </div>
    </div>
  </div>

  <div class="banner">进度: <em>4/9 完成</em> — 本 Sprint 剩余 5 天</div>
</div>
```

---

## CSS

```css
.kanban {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

/* Column */
.kb-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

/* Column header */
.kb-col-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--card-bg);
  border: 1.5px solid var(--col-color);
  border-radius: 8px;
}
.kb-col-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}
.kb-col-count {
  font-size: 11px;
  font-weight: 700;
  color: var(--col-color);
  background: rgba(0,0,0,0.04);
  border-radius: 10px;
  padding: 1px 8px;
}

/* Cards container */
.kb-cards {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Individual card */
.kb-card {
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 8px;
  padding: 10px 12px;
  border-left: 3px solid var(--col-color);
}
.kb-card.done {
  opacity: 0.6;
}
.kb-card-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
}
.kb-card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

/* Tag */
.kb-tag {
  font-size: 9px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(0,0,0,0.05);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.kb-tag.urgent {
  background: rgba(184, 50, 50, 0.1);
  color: var(--critical, #b83232);
}

/* Owner */
.kb-owner {
  font-size: 10px;
  color: var(--text-muted);
}
```

---

## Variants

### WIP Limits

Show work-in-progress limits on column headers:
```html
<div class="kb-col-header">
  <span class="kb-col-title">进行中</span>
  <span class="kb-wip">2/3</span>
</div>
```
```css
.kb-wip {
  font-size: 10px;
  color: var(--text-muted);
  border: 1px solid var(--border-base);
  border-radius: 4px;
  padding: 1px 6px;
}
```

### Priority Indicators

Add priority dots to cards:
```css
.kb-card.high-priority { border-left-color: var(--critical); }
.kb-card.medium-priority { border-left-color: var(--minor); }
```

### Swimlanes

Group cards by category within columns:
```html
<div class="kb-swimlane">Frontend</div>
<div class="kb-card">...</div>
<div class="kb-swimlane">Backend</div>
<div class="kb-card">...</div>
```

---

## Key Rules

1. **3-5 columns equal width** (`flex: 1`): Classic Kanban layout
2. **Column header with count badge**: Shows how many items in each state
3. **Cards stack vertically**: Gap 6px between cards within a column
4. **Left accent border on cards**: 3px, matches column color for visual tracking
5. **Done cards dimmed**: `opacity: 0.6` to de-emphasize completed work
6. **Tags are tiny uppercase**: 9px, categorize tasks (Feature/Bug/Infra)
7. **Owners are muted**: 10px, secondary information
8. **Column gap**: 10px between columns
9. **align-items: flex-start**: Columns don't stretch to match tallest — natural height per content
