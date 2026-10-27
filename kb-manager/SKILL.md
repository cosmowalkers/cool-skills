---
name: kb-manager
description: |
  维护项目 AI 知识库。当用户要新增、更新、迁移、整理、校验 docs/ 知识页，或代码/方案变更后
  需要扫描项目代码、识别模块和功能、生成或对账 AI 知识库时使用。适用于前端、后端、客户端、
  基础设施等项目，统一复用 guide / rules / reference / decisions / gotchas 分类。必须先按
  taxonomy 判断知识类型和归属；知识库输出位置、主仓/子仓/common 的组织方式必须根据本次用户
  prompt 决定，不得写死。不要直接把代码事实复制成文档。
argument-hint: "[build|reconcile|update|migrate|verify] [path|scope|change description]"
metadata:
  author: Sugon
  version: "0.1.0"
  date: 2026-10-23
---

# kb-manager：项目知识库构建与维护

本 skill 是知识库生命周期编排器。它负责扫描代码、发现模块和功能、规划页面、生成或对账页面、
维护索引和日志，并在结束前执行人工审阅、质量评价和确定性校验。它借鉴 miwear 知识库的
“扫描 → Discovery → 审阅 → 规划 → 并行生成 → 评价 → 校验”流程。

## 设计边界

### 项目适配与输出组织

知识库不假设固定的仓库、语言、框架、目录、common 包或主子仓关系。每次运行都先扫描
用户指定的仓库和子模块，再从本次 prompt 中确定：

- 知识库输出根目录；
- 是否把主仓和子仓合并生成；
- 是否按仓库分目录；
- common、主仓、子仓之间的引用关系；
- 哪些页面需要跨仓共享，哪些页面只属于单个仓库。

prompt 未明确这些组织规则时，先输出扫描结果和两到三个组织方案，要求用户选择后再落盘。
已有知识库的组织方式只能作为候选依据，不能覆盖用户本次 prompt 的明确要求。

建议的生成输入：

```text
仓库根目录: ...
扫描范围: 主仓 + 子仓 / 仅主仓 / 指定目录
知识库输出目录: ...
组织方式: 合并 / 按仓库分组 / 共享页 + 仓库差异页
共享规则: ...
```

### 五类目录

知识分类和页面写法以 `references/taxonomy.md` 为准：

```text
docs/
├── README.md
├── guide/
├── rules/
├── reference/
├── decisions/
└── gotchas/
```

不要为了填充目录创建空页面或空目录。只有存在真实知识时才创建对应页面。

`decisions/` 是按独立决策拆分的目录，可以包含多个页面。一个页面只记录一个独立
的架构选择、约束方向或取舍主题；不能因为目录需要简洁而把多个决策合并成一个，
也不能为了凑数量虚构决策。是否创建决策页必须由用户明确决策、正式变更来源或代码
能够稳定证明的当前架构边界支持。代码只能证明当前实现时，页面必须明确写成当前
实现边界，不得补写不存在的历史评审、备选方案或“为什么当初这样选”。

### 明确不写的内容

- 可以直接从代码、类型、路由、接口签名或配置文件读取的事实；
- 复制 README、官方文档或 lint 已经表达清楚的常识；
- 没有证据的推测；
- 临时任务清单和个人偏好；
- 已有知识库中已经存在、但没有新增证据或变化的重复正文。

## 支持模式

从 `$ARGUMENTS` 判断模式。没有明确模式时，根据输入和已有文件自动选择，并在开始时展示判断结果。

| 模式 | 用途 | 前置条件 |
|---|---|---|
| `build` | 扫描项目并生成知识库 | 读取项目源码和用户指定的扫描范围 |
| `reconcile` / `update` | 根据代码变更对账已有知识库，支持新增、修改、删除、迁移和保留 | 已有知识库，或明确指定全量对账范围 |
| `migrate` | 从旧 docs 或源码散落文档迁移 | 先做内容拆分和迁移计划 |
| `verify` | 检查索引、元数据、引用和路径 | 只读，不写正文 |

输入可以是文件路径、目录、MR/commit 变更说明、飞书链接或用户描述。外部文档只作为
输入来源，不能绕过人工确认直接写入知识库。

`update` 是 `reconcile` 的兼容别名。“增量”只描述扫描范围，不描述动作类型。对账结果必须
明确标记每个页面的动作：

```text
create | update | delete | move | link_shared_page |
remove_repository_difference | ignore
```

### 最少步骤路径

已有知识库且用户已经明确仓库、输出位置和主子仓关系时，不重复询问组织方案：

```text
build:       扫描 → Discovery → 生成 → 校验
reconcile:   读取变更 → 影响分析 → 执行动作 → 校验
verify:      校验
```

只有以下情况才暂停确认：组织关系不明确、需要新增或改变 `decisions/`、事实只有推断、
或删除动作没有代码变更和用户意图支持。普通代码事实页面的新增、修改、失效和引用重算
不要求重复确认。

## 执行流程

### Phase 0：确定扫描范围和输出组织

1. 读取用户 prompt，提取项目根目录、扫描范围、输出目录和主子仓组织要求。
2. 如果 prompt 没有说明，识别当前仓库根目录，并列出主仓、子仓、common 包和已有 docs。
3. 读取项目的 `AGENTS.md`、`CLAUDE.md`、README、git submodule 配置和已有知识库索引。
   多仓工作区优先执行 `scripts/discover-topology.py <workspace> --output
   <path>/_repository_topology.json`，把仓库和 `.gitmodules` 关系作为事实输入。
4. 生成组织方案，明确页面如何分组、共享页面如何引用、仓库差异如何表达。
5. 组织关系不明确时，暂停在落盘前询问；不得因为目录名或技术栈自行决定归属。
6. 输出：

```text
知识库范围
项目仓库: ...
扫描范围: ...
知识库输出目录: ...
组织方式: ...
主仓/子仓关系: ...
输入来源: ...
模式: build | reconcile | update | migrate | verify
```

如果无法确定知识库输出目录或组织方式，暂停并询问用户；不要猜测写入位置。

仓库可以分为三种处理方式，但不能预先排除任一种：

- 有共同依赖：生成公共仓库知识、主仓接入知识和主仓定制化描述；
- 有子仓但没有 common：分别生成主仓和业务子仓知识，按证据建立引用；
- 完全独立：直接按单仓流程生成，不要求创建共享页面。

### Phase 1：扫描与 Discovery

先扫描用户指定范围内的代码、配置、脚本、测试和已有文档，生成项目结构与代码上下文。
扫描器只负责确定性文件发现和内容采集，模块边界、业务特性和知识价值由 AI Discovery 判断。
大型项目按模块分组，避免把整个仓库一次性塞入上下文。

优先使用 `scripts/scan-project.py <repository> --output <path>/_scan_context.json` 采集文件、
哈希、规模、候选模块和有限文本预览。不得把 `node_modules`、构建产物、缓存和覆盖率目录
作为 Discovery 证据。Discovery 结构必须符合 `references/discovery-schema.md`，生成后执行
`scripts/validate-discovery.py <path>/_discovery.json`。

Discovery 至少识别：

- 项目架构和模块边界；
- 面向用户或调用方的业务功能；
- 跨模块流程和隐式约束；
- 技术选型和架构决策；
- 开发、构建、部署和调试流程；
- 历史踩坑、兼容性问题和技术债；
- 可以从代码直接读取、因此不应写入的内容。

生成并保留以下中间产物，供审阅和变更对账使用：

```text
_scan_context.json
_discovery.json
_discovery_review.md
_tasks_export.json
```

首次 `build` 的 Discovery 必须先通过人工审阅，确认模块、功能和输出组织后才能规划正文
页面。`reconcile` 只重新检查受影响模块；如果组织关系和分类未变化，不重复全量审阅。

建立结构化候选结果，至少包含：

```text
候选页面
- path
- type
- repository
- module
- feature
- match_reason
- confidence

建议动作
- update_existing
- create_page
- split_by_repository
- link_shared_page
- ignore_as_code_projection
- ask_for_organization
```

必须区分以下情况：

- 已有页面覆盖且证据未变化 → 不重复创建；
- 同一知识被多个仓库使用 → 按用户指定的组织方式生成共享页和引用；
- 同名功能在不同仓库语义不同 → 分开生成并标注仓库范围；
- 子仓库知识依赖主仓库约束 → 建立明确的双向可追踪链接；
- 没有共性依赖的主仓或子仓 → 仍然生成其自身知识库，不强行归入 common；
- 命中多个页面 → 优先更新已有页面，不重复建页。

当本次 prompt 涉及两个或以上仓库的共性时，必须完成一次跨仓分析：

1. 分别扫描并生成每个仓库的 `_discovery.json`；
2. 使用 `scripts/cross-repo.py --discovery <repo>=<path>/_discovery.json ...`
   生成候选矩阵；
3. 按 `references/cross-repo-analysis.md` 将结果标记为共性候选、相似但不同、单仓知识
   或代码投影；
4. 在 `_discovery_review.md` 中确认共性候选后，才允许将页面放入用户指定的 common；
5. 共性页面生成后，为每个主仓生成只包含差异和引用的页面，并校验没有重复正文或丢失
   单仓约束。

`common` 依赖关系只决定页面如何复用，不决定仓库是否生成知识库。每个被纳入扫描范围的
主仓、子仓和独立仓都必须有自己的 Discovery；只有没有新增知识时，才可以在任务规划中
标记为 `ignore`。

### Phase 2：分类与计划审阅

读取 `references/taxonomy.md` 和 `references/schema.md`。对每条候选知识给出：

```text
分类: guide | rules | reference | decisions | gotchas
归属: shared | repository | submodule | repository-difference
仓库: ...
模块: ...
目标路径: ...
更新策略: ...
理由: ...
```

然后生成一个变更计划。计划至少列出：

- 新建文件；
- 更新文件；
- 删除或不迁移的旧内容及原因；
- 主仓、子仓和共享页面的引用关系；
- 需要用户确认的责任边界、分类或事实；
- 证据来源和可信度。

计划应遵循 `references/task-planning.md`，输出 `_tasks_export.json`。如果存在已确认的
跨仓共性候选，可用 `scripts/plan-tasks.py` 生成独立任务；未确认候选不得进入任务列表。

在以下场景必须等待用户确认后再写入：

- 新建或改变无法由代码直接证明的 `rules/`；
- 新建或变更 `decisions/`；
- 改变主仓、子仓或共享页面的归属；
- 删除没有代码变更、用户意图或失效证据支持的页面；
- 事实来源只有推断，没有代码、MR、commit 或正式文档证据。

### 变更对账

`reconcile` 优先接收 `git diff --name-status`、commit range 或用户指定的变更文件。
使用 `scripts/impact-plan.py` 将变更映射到页面正文的验证来源，并输出未映射变更。对账时按以下规则
决定动作：

- 代码新增且属于已有知识范围：更新对应页面；不自动创建重复页面；
- 代码修改且页面验证来源命中：更新页面内容和验证来源；
- 代码删除导致页面事实失效：生成 `delete` 或 `move` 计划；决策历史只能标记替代；
- common 能力归属变化：先重算 common 与主仓引用，再决定更新或删除差异页；
- 变更没有命中任何页面：由 Discovery 判断 `create`、`ignore` 或 `ask_for_organization`；
- 页面证据全部消失但代码没有对应变更：标记 `stale_evidence`，不能直接删除。

执行删除、迁移或引用重算后，必须重新索引 README、追加 log，并检查所有受影响页面。

### Phase 3：生成或对账正文

读取 `references/schema.md` 中对应类型的模板，只写输入中有证据支持的信息。

每个新建或实际变更的页面必须：

- 从 Markdown 标题和 2–3 句摘要开始，不生成 YAML frontmatter；
- 说明适用范围和边界；
- 解释原因、约束、后果或验证方式；
- 在 `## 验证来源` 或 `## 证据` 中写出直接支撑结论的仓库相对路径；
- 给出至少一个相关页面链接；
- 控制在 80–250 行，超过 400 行时拆分；
- 不复述代码中可以直接查到的事实。

验证来源必须写在正文中。跨仓路径使用 `仓库标识:相对路径`，单仓路径不加仓库前缀。
验证来源必须是可以在仓库中定位的相对路径；不得使用 `code-scan`、`扫描结果`、
`跨仓扫描`、`skill-catalog` 或其他扫描过程名称代替路径。用户确认的未来方向直接写入
正文，并明确标注为未来方向；不要生成 `source` 字段或其他页面元数据。
不要生成 status、confidence、source、last_verified、owner 或 evidence 等页面元数据。

### 普通知识页面

页面按照用户确认的输出组织写入。无论页面属于主仓、子仓还是共享目录，都使用普通
Markdown；页面类型由所在目录确定，代码来源写入正文：

```markdown
# 国际化约束

> ...

## 规则
...

## 验证来源

- `src/locales/zh.json`
- `src/locales/en.json`
```

### 共享页和仓库差异页

只有用户明确要求“共享页 + 仓库差异页”时，才使用以下结构：

```markdown
# repo-a 仓库入口

> 共享规则见 [共享页面](<relative-link-to-shared-page>)；本页只记录 repo-a 的差异。

## 共享规则

请先阅读共享页面。

## 本仓差异

- ...

## 验证来源

- `repo-a:src/...`
```

如果仓库没有差异，不生成空的差异页。相对路径必须由 `scripts/verify-doc.py` 校验；路径深度应
根据实际文件位置计算，不手写假定路径。主仓引用的 common 页面必须保留相对路径，不能改成本机
绝对路径；common 尚未同步到 gitlink 时使用 `--common-map` 映射 canonical common 校验。

### Phase 4：索引、日志与关联

每次新增、更新、删除、迁移或引用关系变化都要同步：

1. 所有实际生成页面所在目录的 `README.md`；
2. 对应知识库的 `log.md`；
3. 相关页面的 `## 关联`；
4. 主仓、子仓和共享页面之间的链接。

README 条目必须包含：

- 页面链接；
- 一句话摘要；
- “何时读”；
- 页面所属分类。

索引只收录实际存在的页面。日志 append-only，不改写历史记录。

### Phase 5：质量评估与定向修复

读取 `references/quality-standards.md`，按其中的硬性规则和五个维度评价页面。

对新增或更新页面逐页检查：

- 内容是否来自可追溯证据；
- 是否误把代码投影写成知识；
- 分类是否正确；
- 仓库/子仓/共享归属是否符合用户确认的组织方案；
- 页面是否从标题开始且没有 YAML frontmatter；
- 验证来源是否写在正文并能回到当前代码；
- 验证来源是否都是可定位的仓库相对路径，且没有 `code-scan`、`扫描结果` 等占位符；
- 共享页和仓库差异页是否只承担各自职责；
- 是否存在重复页面；
- 跨仓场景下，是否有证据矩阵、共享页与差异页是否职责清晰、是否重复维护同一事实；
- 是否有有效关联；
- 是否进入 README；
- 是否超出篇幅；
- 是否存在模糊、绝对化或未经验证的结论。

如果发现问题，格式问题可以直接修复；规则、决策、组织关系和没有证据的删除需要再次确认。
代码事实页面可以在证据明确时直接修复。最多定向修复两轮，仍不确定的内容放入任务记录
等待确认，不得编造内容。

### Phase 6：确定性校验和交付

执行：

```bash
scripts/verify-doc.py --root <knowledge-docs-root> --check-links \
  [--common-map aui-common=<canonical-common-root>]
scripts/check-name.sh <target-path>
```

跨仓场景还要复核每个 Discovery 和共性分析产物：

```bash
scripts/validate-discovery.py <repository>/_discovery.json
scripts/cross-repo.py --discovery <repo>=<path>/_discovery.json ... --output <path>/_cross_repo.json
```

如果校验失败，修复后重新执行。最终输出：

```text
知识写入完成
项目仓库: ...
扫描范围: ...
知识库输出目录: ...
组织方式: ...
新增: ...
更新: ...
仅保留引用: ...
未迁移: ...
校验: passed | failed
待人工确认: ...
```

## 更新策略

详细规则见 `references/update-policy.md`。
变更对账的动作、证据和删除边界见 `references/change-reconciliation.md`。

- `guide/`：可原地更新，步骤和命令变化时同步修改；
- `rules/`：原地更新，但规则变化必须人工确认；
- `reference/`：事实变化时原地更新，保留验证来源；
- `gotchas/`：同一根因补充到原页面，不同根因新建页面；
- `decisions/`：永远不覆盖原页面。新建决策页，旧页追加替代说明并链接新页。

## 与 miwear 设计的对应关系

| miwear 能力 | 本 skill 对应实现 |
|---|---|
| 全量 KB 构建 | `build` 模式 + Phase 0–6 |
| 变更对账 `kb-update` | `reconcile` / `update` 模式 + 变更影响分析 |
| taxonomy | `references/taxonomy.md` |
| schema | `references/schema.md` |
| index / log | Phase 4 |
| 人工 review | Phase 2、Phase 5 |
| 质量评价 | Phase 5 |
| 确定性工具 | `scripts/` |
| 证据和来源 | 页面正文的 `## 验证来源` 或 `## 证据` |
| 关联知识 | `## 关联` wikilinks |

## 资源读取顺序

按需读取，不要一次加载所有参考文件：

1. 新建或分类不确定 → `references/taxonomy.md`
2. 写正文和检查证据 → `references/schema.md`
3. 更新已有页面 → `references/update-policy.md`
4. 需要生成共享页或仓库差异 → `references/host-reference-template.md`
5. 迁移旧 docs → `references/migration-guide.md`
6. 质量评价 → `references/quality-standards.md`
7. 多仓共性 → `references/cross-repo-analysis.md`
8. 仓库关系 → `references/repository-topology.md`
9. 变更对账 → `references/change-reconciliation.md`
10. 任务拆分 → `references/task-planning.md`
11. Discovery 校验 → `scripts/validate-discovery.py`
12. 最终校验 → `scripts/verify-doc.py` 和 `scripts/check-name.sh`

$ARGUMENTS
