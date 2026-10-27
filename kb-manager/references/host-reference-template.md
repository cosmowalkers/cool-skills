# 多仓知识组织模板

本文件只在用户 prompt 明确要求共享页面、主仓、子仓或差异页时读取。skill 不预设任何
主仓、子仓或 common 关系，所有路径和名称必须替换为本次运行确认的值。

## 共享页面

```markdown
# 共享规则

> 适用于 repo-a 和 repo-b 的共同约束。

## 规则

...

## 验证来源

- `repo-a:src/...`
- `repo-b:src/...`

## 关联

- [repo-a 入口](../repo-a/rules/example.md)
- [repo-b 入口](../repo-b/rules/example.md)
```

## 仓库差异页面

```markdown
# repo-a 仓库入口

> 共享规则见 [共享页面](../shared/rules/example.md)；本页只记录 repo-a 的差异。

## 共享规则

请先阅读共享页面。

## 本仓差异

...

## 验证来源

- `repo-a:src/...`

## 关联

- [共享页面](../shared/rules/example.md)
```

如果某个仓库没有差异，不创建空的差异页。主仓、子仓和共享页之间的本地链接必须通过
校验脚本验证。
