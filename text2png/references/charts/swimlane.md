# Swimlane — 泳道图

跨角色的流程：每一步谁负责、角色之间怎么交接。

与 `flowchart` 的区别：流程图只讲"先后"，泳道图多一个"责任归属"维度（横向=阶段，纵向=角色）。

---

## Layout

```
[Title / Subtitle]
        │ 阶段1      │ 阶段2      │ 阶段3
 用户   │ [下单] ────┼───────────┼──▶ [评价]
 商家   │            │ [接单][出餐]│
 骑手   │            │           │ [取餐]─▶[送达]
 平台   │ [派单]─────┼───────────┼─
```

- **横轴 = 阶段**（3-4 个），**纵轴 = 角色/系统**（3-5 条泳道）
- 每条泳道高度固定（48-56px），左侧标签栏固定宽度（90-110px）
- 用 grid 实现：`grid-template-columns: 110px repeat(N, 1fr)`，每个格子放一张任务卡
- 同一角色的连续动作用箭头连接；跨泳道的交接在格子边界处画箭头（可用 `→` 图标或 CSS 三角）
- 阶段表头用大写小字号标签 + 底部细线，和泳道区分开
- 高亮当前瓶颈/关键阶段（一张卡加边框 + 底色）

---

## HTML Structure

```html
<div class="lane-wrap">
  <div class="lane-head">
    <div class="lane-corner"></div>
    <div class="stage">① 下单</div>
    <div class="stage">② 履约</div>
    <div class="stage">③ 完成</div>
  </div>

  <div class="lane">
    <div class="lane-label">用户<span>发起方</span></div>
    <div class="cell"><div class="task hi">提交订单<em>10:02</em></div></div>
    <div class="cell"><div class="task ghost">等待出餐</div></div>
    <div class="cell"><div class="task">确认收货 / 评价<em>10:46</em></div></div>
  </div>

  <div class="lane">
    <div class="lane-label">商家<span>供给</span></div>
    <div class="cell"></div>
    <div class="cell"><div class="task">接单 → 出餐<em>10:05-10:22</em></div></div>
    <div class="cell"></div>
  </div>
  <!-- 骑手、平台同理 -->
</div>
```

---

## CSS

```css
.lane-wrap { display: flex; flex-direction: column; gap: 6px; }

.lane-head,
.lane {
  display: grid;
  grid-template-columns: 110px repeat(var(--stages, 3), 1fr);
  gap: 8px;
  align-items: stretch;
}

.lane-head .stage {
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-base);
  padding-bottom: 4px;
}

.lane-label {
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-size: 12.5px;
  font-weight: 700;
  border-left: 3px solid var(--accent);
  padding-left: 8px;
  background: var(--card-bg-alt, var(--card-bg));
  border-radius: 4px;
}
.lane-label span { font-size: 11px; font-weight: 400; color: var(--text-secondary); }

.lane .cell {
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--border-base) 30%, transparent);
  border-radius: 6px;
  padding: 6px;
}

.task {
  width: 100%;
  background: var(--card-bg);
  border: 1px solid var(--border-base);
  border-left: 3px solid var(--accent);
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 12px;
}
.task em { display: block; font-style: normal; font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
.task.hi { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--card-bg)); }
.task.ghost { opacity: 0.6; border-style: dashed; }
```

---

## Variants

### 带耗时标注的泳道

阶段表头下加一行时间刻度（`10:00 / 10:15 / 10:30`），任务卡右侧写区间（`10:05-10:22`）——适合"找出哪一段最慢"的复盘。

### 双泳道（仅两个角色）

把 `grid-template-columns` 的标签栏缩到 80px，阶段扩到 5 列，适合"前端 ↔ 后端联调"这类只有两方的流程。

---

## Content Checklist

- 角色 3-5 个，用真实角色名（用户/商家/骑手/平台，或 前端/后端/测试/运维）
- 阶段 3-4 个，用"事件"命名而不是"步骤1"
- 每个任务卡写"动作 + 时间"，空档用虚线卡（等待/阻塞）标出来——瓶颈往往就在空档里
- 至少高亮 1 张关键卡（瓶颈/风险），否则图会显得平
