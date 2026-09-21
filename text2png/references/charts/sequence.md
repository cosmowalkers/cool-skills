# Sequence — 时序图

参与者之间的消息交互与先后顺序：接口调用链、请求/响应、异步回调、用户与系统的多轮交互。

与 `timeline`（单轴事件）、`flowchart`（步骤分支）的区别：时序图的核心是**多个参与者**和**它们之间的消息**。

---

## Layout

```
[Title / Subtitle]
[Participant Row]        乘客     进站闸机    列车     出站闸机
[Lifelines]              │          │         │          │
[Messages]               │──刷卡──▶│         │          │
                         │          │──放行──▶│          │   ← 每条消息一行
[Legend / Note]
```

- 参与者 ≤ 5 个，横排等宽（`flex:1`），方框 + 名称，必要时加副标题（角色/系统类型）
- 生命线用 `repeating-linear-gradient` 或 `border-left: 1px dashed`，从参与者底部拉到画布底部
- **每条消息占一行**，高度固定（26-30px），保证箭头水平对齐
- 消息箭头：请求=实线 + 实心箭头；响应=虚线 + 空心箭头；异步=实线 + 开口箭头；自调用=回折小箭头
- 关键节点画**激活条**（生命线上的竖条），表示该参与者正在处理
- 消息文字压在箭头上方（`align-self:center`），序号可选（`1 · 2 · 3`）

---

## HTML Structure

```html
<div class="seq">
  <div class="seq-head">
    <div class="actor"><b>乘客</b><span>发起方</span></div>
    <div class="actor"><b>进站闸机</b><span>设备</span></div>
    <div class="actor"><b>列车</b><span>承运</span></div>
    <div class="actor"><b>出站闸机</b><span>设备</span></div>
  </div>

  <div class="seq-body">
    <div class="seq-line"><i class="life" style="--i:0"></i><i class="life" style="--i:1"></i>
      <i class="life" style="--i:2"></i><i class="life" style="--i:3"></i>
      <div class="msg req" style="--from:0;--to:1"><span class="label">刷卡/刷码</span></div>
      <div class="act" style="--i:1;--top:0;--h:1"></div>
    </div>

    <div class="seq-line">
      <div class="msg res" style="--from:1;--to:0"><span class="label">闸门开启</span></div>
    </div>
    <!-- ... 每个往来一行 ... -->
  </div>

  <div class="seq-legend">
    <span class="k solid">实线 = 请求</span>
    <span class="k dashed">虚线 = 响应</span>
    <span class="k act-solid">竖条 = 处理中</span>
  </div>
</div>
```

---

## CSS

```css
.seq-head { display: flex; gap: 8px; margin-bottom: 6px; }
.actor {
  flex: 1;
  text-align: center;
  border: 1.5px solid var(--accent);
  border-radius: 10px;
  padding: 8px 6px;
  background: var(--card-bg);
  font-size: 13px;
  font-weight: 700;
}
.actor span { display: block; font-size: 11px; font-weight: 400; color: var(--text-secondary); margin-top: 2px; }

.seq-body { position: relative; }
.seq-line { position: relative; height: 28px; }

/* 生命线：等宽分布，和参与者列对齐 */
.life {
  position: absolute;
  top: 0; bottom: -28px;
  width: 0;
  border-left: 1px dashed var(--border-base);
  left: calc((var(--i) + 0.5) * (100% / var(--actors, 4)));
}

/* 消息箭头：起止列之间画一条水平线 */
.msg {
  position: absolute;
  top: 50%;
  height: 0;
  border-top: 1.5px solid var(--accent);
  left: calc((var(--from) + 0.5) * (100% / var(--actors, 4)));
  width: calc((var(--to) - var(--from)) * (100% / var(--actors, 4)));
}
.msg.res { border-top-style: dashed; }
.msg .label {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11.5px;
  white-space: nowrap;
  color: var(--text-secondary);
}

/* 激活条 */
.act {
  position: absolute;
  width: 8px;
  left: calc((var(--i) + 0.5) * (100% / var(--actors, 4)) - 4px);
  top: calc(var(--top) * 28px);
  height: calc(var(--h) * 28px);
  background: var(--accent);
  border-radius: 2px;
  opacity: 0.85;
}
```

`--actors` 由容器设置（参与者数量），`--from`/`--to`/`--i` 是列下标——所有消息按这两组变量定位，不需要手工算像素。

---

## Variants

### 带 alt / loop 片段

在消息行上叠一个左侧竖条 + 标签框，表示条件分支或循环：

```html
<div class="frag" style="--from:0;--to:2;--top:2;--h:3">
  <span class="frag-tag">alt 令牌有效</span>
</div>
```

```css
.frag {
  position: absolute;
  left: calc((var(--from) + 0.5) * (100% / var(--actors)) - 14px);
  width: calc((var(--to) - var(--from) + 1) * (100% / var(--actors)));
  top: calc(var(--top) * 28px);
  height: calc(var(--h) * 28px);
  border: 1px solid var(--border-base);
  border-left: 3px solid var(--accent);
  border-radius: 4px;
  pointer-events: none;
}
.frag-tag { position: absolute; top: -9px; left: 6px; background: var(--card-bg); padding: 0 4px; font-size: 11px; }
```

### 异步消息

箭头用开口（`border-top` + 两条短线），消息文字加 `async` 标记；响应不再画回程箭头，直接用虚线箭头到目标参与者。

---

## Content Checklist

- 参与者 3-5 个，名字用真实角色（不是"系统A"）
- 每个往来都要有**动词 + 对象**（"刷卡进站" 而不是 "请求1"）
- 能给数据量就给（"扣费 ¥6"、"耗时 120ms"）
- 结尾补一条结果行（"闸门开启，行程开始"）或备注，让图有落点
