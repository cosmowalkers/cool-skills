# 知识页任务规划

页面生成或变更前把已审阅的 Discovery、变更影响分析转成 `_tasks_export.json`，每个任务只
负责一个原子页面或一个明确的变更动作，避免批量生成时互相覆盖。

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "kb-001",
      "action": "create",
      "repository": "shared",
      "source_repositories": ["mall-ui", "console-ui"],
      "type": "rules",
      "target": "common/rules/request-error-handling.md",
      "evidence": ["mall-ui:src/...", "console-ui:src/..."],
      "prompt": "根据证据提炼跨仓共性，并明确适用范围、例外和验证方式",
      "depends_on": []
    }
  ]
}
```

规划规则：

- `action` 只能是 `create`、`update`、`delete`、`move`、`link_shared_page`、
  `remove_repository_difference` 或 `ignore`；
- 目标路径必须唯一；
- `update`、`delete` 和 `move` 必须列出当前页面和变更证据；
- `decisions` 按独立主题拆分；新建任务不能覆盖旧页面，删除任务只能标记历史页为
  `superseded`，不能为了减少文件数合并仍然独立的决策；
- 共享任务必须列出至少两个来源仓库；
- 差异任务必须依赖对应共享任务；
- 每个任务至少有一个证据路径；
- `ignore` 不进入生成任务；
- 规划完成后先检查目标路径、来源和组织方式，再启动页面生成。
