# Mind Map — 思维导图

头脑风暴、知识整理、读书笔记、概念拆解、关联发散。

---

## Layout

```
                    [Leaf B1]
           [Branch B]
                    [Leaf B2]
[Leaf A1]          /
         [Branch A]       [CENTER]       [Branch C]
[Leaf A2]                                          [Leaf C1]
                                         [Branch D]
                                                   [Leaf D1]
                                                   [Leaf D2]
```

Center node with radial branches expanding left and right, 2-3 levels deep.

---

## HTML Structure

```html
<div class="wrap">
  <div class="page-title">产品思维框架</div>
  <div class="page-sub">核心概念与关联拆解</div>

  <div class="mindmap">
    <!-- Left branches -->
    <div class="mm-side mm-left">
      <div class="mm-branch" style="--branch-color: var(--s1);">
        <div class="mm-leaves">
          <div class="mm-leaf">用户调研</div>
          <div class="mm-leaf">数据分析</div>
          <div class="mm-leaf">竞品研究</div>
        </div>
        <div class="mm-connector-h"></div>
        <div class="mm-node">需求发现</div>
      </div>
      <div class="mm-branch" style="--branch-color: var(--s2);">
        <div class="mm-leaves">
          <div class="mm-leaf">MVP 定义</div>
          <div class="mm-leaf">优先级排序</div>
        </div>
        <div class="mm-connector-h"></div>
        <div class="mm-node">产品规划</div>
      </div>
    </div>

    <!-- Center node -->
    <div class="mm-center" style="--center-color: var(--s3);">
      <div class="mm-center-icon">🧠</div>
      <div class="mm-center-title">产品思维</div>
    </div>

    <!-- Right branches -->
    <div class="mm-side mm-right">
      <div class="mm-branch" style="--branch-color: var(--s4);">
        <div class="mm-node">设计执行</div>
        <div class="mm-connector-h"></div>
        <div class="mm-leaves">
          <div class="mm-leaf">交互设计</div>
          <div class="mm-leaf">视觉规范</div>
          <div class="mm-leaf">原型验证</div>
        </div>
      </div>
      <div class="mm-branch" style="--branch-color: var(--s5);">
        <div class="mm-node">增长迭代</div>
        <div class="mm-connector-h"></div>
        <div class="mm-leaves">
          <div class="mm-leaf">A/B 测试</div>
          <div class="mm-leaf">漏斗优化</div>
        </div>
      </div>
    </div>
  </div>

  <div class="banner">从 <em>发现需求</em> 到 <em>增长闭环</em> 的完整思维框架</div>
</div>
```

---

## CSS

```css
.mindmap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  min-height: 280px;
}

/* Center node */
.mm-center {
  background: var(--card-bg);
  border: 2.5px solid var(--center-color);
  border-radius: 50%;
  width: 120px;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 2;
}
.mm-center-icon { font-size: 28px; margin-bottom: 4px; }
.mm-center-title { font-size: 14px; font-weight: 700; text-align: center; }

/* Side containers */
.mm-side {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
}

/* Branch (one level-1 node + its leaves) */
.mm-branch {
  display: flex;
  align-items: center;
  gap: 0;
}
.mm-left .mm-branch { flex-direction: row-reverse; }
.mm-right .mm-branch { flex-direction: row; }

/* Level-1 node */
.mm-node {
  background: var(--card-bg);
  border: 1.5px solid var(--branch-color);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Horizontal connector (branch line) */
.mm-connector-h {
  width: 24px;
  height: 2px;
  background: var(--branch-color);
  flex-shrink: 0;
}

/* Leaf container */
.mm-leaves {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Leaf node */
.mm-leaf {
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}
```

---

## Variants

### Single-Side (Outline Style)

All branches on the right, more like an outline:
```css
.mindmap { flex-direction: row; justify-content: flex-start; }
.mm-left { display: none; }
.mm-center { border-radius: 10px; width: auto; height: auto; padding: 16px 24px; }
```

### Deep Hierarchy (3 levels)

Add sub-leaves inside `.mm-leaves`:
```html
<div class="mm-leaf-group">
  <div class="mm-leaf parent">Parent Leaf</div>
  <div class="mm-sub-leaves">
    <div class="mm-leaf sub">Sub item 1</div>
    <div class="mm-leaf sub">Sub item 2</div>
  </div>
</div>
```

### With Descriptions

Add descriptions to level-1 nodes:
```html
<div class="mm-node">
  <div class="mm-node-title">需求发现</div>
  <div class="mm-node-desc">理解用户真正的痛点</div>
</div>
```

---

## Key Rules

1. **Center node is circular**: Visually anchors the entire map, largest element
2. **Left-right balance**: Distribute branches roughly evenly between sides
3. **Max 2-3 levels**: Center → Branch → Leaf (deeper nesting gets unreadable at 860px)
4. **Max 4-5 branches per side**: Beyond that, group related branches
5. **Connector lines**: Simple 2px colored lines between nodes (no arrows — mind maps show association, not flow)
6. **Color per branch**: Each branch family uses one accent color consistently
7. **Leaves are smaller**: Clearly subordinate to branch nodes (smaller font, thinner border)
8. **Horizontal expansion**: Mind maps expand horizontally, unlike flowcharts which can go vertical
9. **Width**: Always 860px (horizontal nature demands full width)
