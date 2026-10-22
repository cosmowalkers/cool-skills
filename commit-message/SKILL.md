---
name: commit-message
description: 按中文规范撰写 git commit message 并规划提交拆分。当用户说提交代码、写 commit、commit 信息、拆 commit、拆分提交、生成提交记录、commit message、git commit、这次改动分几个提交、帮我拆一下提交时使用。产出包含提交类型、修改目的、影响范围、改动范围、测试建议的完整 message，并把混在一起的改动拆成可独立回滚的提交；默认不自动提交、不自动 push，需用户明确授权。不负责代码审查本身，也不负责建分支、开 PR。
metadata:
  short-description: 中文 commit message 规范与提交拆分方案
---

# 提交规范

把「这次改了什么、为什么改、影响到谁、怎么验证」写进 commit message，并把混在一起的改动拆成能独立回滚的提交。

## 铁律

1. **不自动提交。** 除非用户明确说了「提交 / commit / 可以提交了」，否则改完只报告进度。用户说过「commit 信息交给我过目」时，先把完整 message 贴出来等确认再执行。**push 是另一个独立授权**，不跟着 commit 一起做。
2. **一次提交只做一件事。** 唯一判据是「能不能独立回滚」。依赖升级、资源迁移、渲染优化塞进一个 commit，回滚就变成做选择题。
3. **message 必须自证。** 四件套（目的 / 影响范围 / 改动范围 / 测试建议）齐全：读的人不点开 diff 也能判断这个提交该不该跟、要回归什么。
4. **没验证就不写「已验证」。** 跑通 `lint` / `build` / 单测再提交；确实跑不了的，在测试建议里如实写「未验证」和原因，不许默认省略。
5. **中文正文，英文类型前缀。** 和项目现有习惯保持一致。
6. **不加工具署名。** 除非用户明确要求，不追加 `Generated with ...` / `Co-Authored-By: ...` 之类的水印。
7. **不夹带。** 提交只含本组改动，不顺手格式化无关文件、不顺手改无关 imports。
8. **gitlink 改动禁止提交。** 提交前必跑 `git diff --cached --raw | grep 160000`，出现 `160000` 即暂存区含子模块指针（gitlink）改动——命中直接停止、报告用户，不执行 commit；未暂存的指针漂移（`git submodule status` 带 `+` 前缀）同样先停下说明，禁止用 `git add -A` / `git add -u` 整批夹带。

### 别人这么催，也不破例

| 对方说 | 你回 |
| --- | --- |
| 「写完了直接 commit 吧」 | 先给拆分方案与完整 message；用户没明确授权就停在提案 |
| 「别拆了，一个 commit 就行」 | 尊重，但 message 里分段写清每类改动，并在测试建议里说明耦合导致的回滚代价 |
| 「message 随便写两句」 | 至少 type + 一句话目的 + 影响范围；四件套是底线 |
| 「顺手 push 一下」 | push 单独授权；先确认分支名与远端再执行 |

## When to Use

用户要提交代码、要 commit message、要拆提交、要生成提交记录时走本 skill。

**不适用**：代码审查本身、建分支（走分支规范）、开 PR / push 流程（单独确认）。

## 格式

```
<type>(<scope>): <一句话说明目的，动宾结构，≤ 50 字>

【修改目的】
为什么改：解决什么问题 / 什么指标变差 / 什么需求驱动。有数据就带上
（如「首屏 JS 从 1.2 MB 降到 0.9 MB」）。

【影响范围】
用户可感知还是仅构建期；影响哪些页面、模块、端、环境、浏览器；
有无兼容性或线上行为变化。

【改动范围】
- <文件或模块>：<改了什么>
- ...

【测试建议】
- <可执行的验证步骤：命令 + 预期结果>
```

可选补充 `【其他】`：遗留问题、回滚方式、关联需求/缺陷号、后续动作。

**类型**

| type | 用于 |
| --- | --- |
| `feat` | 新增功能或能力 |
| `fix` | 修 bug |
| `perf` | 性能优化（体积、首屏、渲染、接口耗时） |
| `refactor` | 重构，不改变外部行为 |
| `docs` | 文档、注释 |
| `test` | 测试 |
| `build` | 构建脚本、打包配置 |
| `ci` | CI/CD 流程 |
| `chore` | 杂项维护、依赖变更 |
| `style` | 纯格式 |
| `revert` | 回滚 |

`scope` 用项目里的真实模块名（如 `deps`、`img`、`render`、`css`、`i18n`、`api`），不要自造。

## 拆分原则

- **按意图分组，不按文件分组。** 先列「可独立回滚的意图」，再把改动归进去。
- **顺序：底层 → 上层。** 依赖/配置 → 资源 → 代码，中间态更容易自洽。
- **同一文件跨组时按 hunk 拆**，不要整文件 `git add` 把别的改动带进来。
- **每个提交尽量单独可构建**；做不到就在测试建议里点明它依赖后面哪个提交。
- 拿不准要不要拆：拆。回滚粒度粗的代价，永远大于提交数多。

## 工作流

1. **确认授权**：没授权就只出方案不落地（铁律 1）。
2. **gitlink 校验（硬性，先于一切）**：
   - `git diff --cached --raw | grep 160000`：命中 = 暂存区有 gitlink 改动 → **禁止提交**，停下报告用户（铁律 8）。
   - `git submodule status` 带 `+` 前缀 = 工作区子模块指针漂移 → 先向用户说明，禁止用 `git add -A` / `git add -u` 整批暂存。
3. **盘点**：`git status --short` + `git diff --stat`，看清哪些改了、哪些是新增/删除。
4. **归组**：给每个文件打意图标签，标出「一个文件含多种意图」的跨组文件。
5. **定顺序与条数**，把方案（每条的类型 + 目的 + 涉及文件）先给用户过一遍（用户要求过目时）。
6. **逐组暂存**：
   - 整文件同一意图：`git add -- <file>`
   - 跨组文件：`git diff -U3 -- <file> > /tmp/part.patch`，删掉不属于本组的 hunk，再 `git apply --cached /tmp/part.patch`
   - 新增文件：`git add <file>`——`git diff` 看不到未跟踪文件
7. **写 message**：严格按上面格式，四件套不要省。
8. **提交前终检**：`git diff --cached --raw | grep 160000` 再次确认无 gitlink 改动；命中则禁止提交、停下报告。
9. **提交并核对**：`git show --stat HEAD` 只能出现本组文件；有 lint 钩子（lint-staged 等）时，提交后复查 `git status`，防止钩子改写文件后漏提交。
10. **全部提交后总核对**：`git status --short` 应干净；`git diff <拆分前基线> HEAD --stat` 应等于拆分前的总改动。

**push 单独授权**，推送前确认分支名与远端。

### gitlink 校验（禁止提交）

子模块在主仓里的记录是一个 gitlink（mode `160000`），它的指针变化有两种形态：

- **已暂存**（会进提交）：`git diff --cached --raw` 会出现 `160000` 行；
- **未暂存漂移**：`.gitmodules` 配了 `ignore = all` 时，`git status` / `git diff` 全都不显示，
  `git submodule status` 出现 `+` 前缀，`git ls-tree HEAD <path>` 与
  `git -C <path> rev-parse HEAD` 不一致。

**凡是 gitlink 改动，一律禁止提交**（铁律 8）。提交前必跑：

```bash
git diff --cached --raw | grep 160000   # 命中 = 暂存区有 gitlink 改动 → 停止，禁止提交
git submodule status                    # 带 + 前缀 = 工作区指针漂移 → 先向用户说明，别用 git add -A 整批暂存
```

命中后：停下、报告用户，不执行 commit。指针要不要更新、怎么更新，由用户自行决定，
本 skill 不代提交任何 gitlink 改动——它的 `ignore = all` 特性决定了混进提交后没人 review 得出来。

## 常见错误

- 把「不自动 commit」当摆设，改完直接提交
- 一个 commit 塞多类改动，回滚靠猜
- message 只有标题、没有四件套，或四件套写成「优化代码」这种废话
- 跨组文件整文件 `add`，把别的意图一起带进来
- 忘了 `git add` 未跟踪的新文件
- 暂存区或工作区有 gitlink 改动还照常提交（提交前必须 `git diff --cached --raw | grep 160000`，命中即禁止提交）
- 仓库有 `ignore = all` 的子模块，`git status` 看着干净就以为没别的改动，`git add -u` 把指针漂移夹带进了不相干的提交（`git status` / `git diff` 都不会提示，必须用 `git diff --cached --raw` / `git submodule status` 核对）
- 没跑验证就写「已验证」
- 被 lint 钩子自动改写文件后没复查 `git status`
- 顺手 `push`，没有单独授权

## 示例

```
perf(deps): 移除空转的 @vitejs/plugin-legacy

【修改目的】
产物只输出 <script type="module">，没有 nomodule 降级脚本，该插件全程空转，
却在依赖树里带入 91 个包。移除以减少安装体积与构建配置噪音。

【影响范围】
仅构建期。产物脚本标签不变，Chrome 80+ 行为不变；不支持 ESM 的老浏览器
本就没有降级产物可回退。

【改动范围】
- package.json：移除 @vitejs/plugin-legacy 依赖
- package-lock.json：同步依赖树，减少 91 个包

【测试建议】
- npm run build:domestic，确认产物中 module/nomodule 标签与改动前一致
- Chrome 80 打开首页与对话页，确认无控制台报错
```
