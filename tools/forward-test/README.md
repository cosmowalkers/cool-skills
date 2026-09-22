# 前向测试（forward test）

让**不知道内情**的 agent 真跑一遍任务，用来回答两个读文档回答不了的问题：

1. 这个 skill 的 description 会不会被触发、SKILL.md 里的规则守不守得住？
2. 相比一个没有 skill 的 agent，它到底多做了哪些事？

方法论借鉴 superpowers 的 `writing-skills`：**先看没有 skill 时失败成什么样，再让 skill 去堵**。
断言要来自观察到的真实失败，而不是想象出来的。

## 两个变体

| 变体 | 给 agent 什么 | 回答什么问题 |
| --- | --- | --- |
| `with` | skill 路径，让它先读 SKILL.md 及引用文件，再完成任务 | skill 能不能把行为带到预期上 |
| `base` | 明令禁用任何 skill，用它自己最顺手的方式做 | 对照组：这件事本来就能做成吗、做成什么样 |

`base` 是关键。少了它，你无法判断 `with` 的表现是 skill 的功劳还是模型的常识。

## 判分

分两层，别混：

- **机械检查**（`checks.py`）：产物是否存在、报告是否写了、源文件有没有被动、关键结论有没有出现。
  客观、可复现，适合当回归。
- **语义判断**：结论站不站得住、提醒到不到位、有没有把"差不多"说成"没问题"。
  机械检查抓不到这层，必须人或 LLM grader 读 `outputs/report.md` 与 `last_message.md`。

机械检查不是装饰。本轮实测里，"源文件是否被改动""有没有出现清晰度结论"这两条就直接区分出了
`with` 和 `base` 的行为差异。

## 怎么跑

在仓库根执行：

```bash
# 跑默认用例（1 号）的两个变体
python3 tools/forward-test/run.py --skill image-tools

# 跑指定用例、只要带 skill 的那组
python3 tools/forward-test/run.py --skill image-tools --cases 10,11 --variants with

# 全跑（贵：13 个用例 × 2 个变体）
python3 tools/forward-test/run.py --skill image-tools --cases all

# 不调模型，只生成各用例的 prompt，人工去跑
python3 tools/forward-test/run.py --skill image-tools --cases 1 --runner manual
```

结果默认落在 `/tmp/forward-test-<时间戳>/`，不写进仓库。每个用例/变体一个目录，顶层是
`report.md`（对比表）与 `results.json`（机读明细）。

### runner

| runner | 说明 |
| --- | --- |
| `codex`（默认） | `codex exec --ephemeral -C <project> -s workspace-write`，独立会话 |
| `claude` | `claude -p … --permission-mode acceptEdits`，需要本机装了 claude CLI |
| `manual` | 只写 TASK.md，不调模型，适合人工在别的环境里跑 |

需要写文件的 runner 要放在能写工作目录的沙箱里；`codex` 在受限沙箱下会起不来 app-server，
这时要在允许执行的环境里跑（本仓库实测需要放开沙箱）。

## 成本

一次 `codex exec` 大约 **40–55k tokens、2–4 分钟**。所以：

- 改文档措辞时不必全跑，挑受影响的用例
- 改脚本行为时跑对应的用例 + 回归用例（`<skill>/scripts/tests/`）
- 全量前向测试留给改 description、改铁律、发版前

## 已知限制

- **"禁用 skill" 是提示词约束，不是真隔离**。真要隔离得换 `CODEX_HOME`，但那会牵涉凭据，不建议在
  共享环境里做。所以 `base` 组的结果当"下界"看，别当严格对照。
- **子代理派发在本 harness 上不可靠**：实测 7 次 spawn / followup / send 里只有 1 次真正送达，
  所以才走 CLI runner。用子代理跑前向测试前先确认消息真的到了。
- **机械检查只能抓"有没有说"**，抓不到"说得对不对"。
- **一次运行有随机性**：同一个 prompt 两次跑出的产物可能不同。要看趋势，别拿单次结果下结论；
  关键结论至少跑两轮。
- 夹具是合成的（噪声图 + 规则线条），能暴露"压糊"和摩尔纹，但不代表真实业务素材的分布。

## 怎么加用例

1. 在 `<skill>/evals/evals.json` 加一条 `prompt` + `expected_output` + `assertions`。
   prompt 要写成像真人说的话（带背景、带情绪、带错误前提），别写成说明书。
2. 在 `checks.py` 的 `BY_CASE` 里给这条用例指定机械检查项（默认有产物、有报告、源文件未动、提了副作用）。
3. 需要新夹具时，在 `fixtures.py` 里加 `build_*` 并注册到 `BUILDERS`。
4. 先用 `--runner manual` 看一眼 prompt 是否像真的，再花 token 跑。

## 用例设计原则

- **压力场景优先**：正常用法谁都做得出来，有价值的是"用户催你跳过验证""用户要求直接覆盖源文件"
  "用户要求一个没实现的能力"这类会诱导违规的 prompt。
- **带真实上下文**：文件路径、CSS 显示尺寸、组件引用，让 agent 必须真的读代码。
- **断言对着失败写**：先跑 `base`，看它在哪里出错，再把这处写进 assertion。没观察到失败就别写断言。
