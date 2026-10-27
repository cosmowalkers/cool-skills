# Discovery 中间结果规范

`_discovery.json` 是 AI 对扫描结果的结构化判断，不是代码目录的复制品。扫描器负责提供证据，
Discovery 负责判断模块、功能和知识价值。

```json
{
  "version": 1,
  "repository": "mall-ui",
  "root": ".",
  "modules": [
    {
      "id": "checkout",
      "name": "结算",
      "paths": ["src/modules/checkout"],
      "evidence": ["src/modules/checkout/routes.ts"],
      "confidence": "high"
    }
  ],
  "features": [
    {
      "id": "checkout-order-submit",
      "name": "提交订单",
      "module": "checkout",
      "evidence": ["src/modules/checkout/api/order.ts"],
      "knowledge_candidates": [
        {
          "type": "guide",
          "reason": "存在跨页面操作流程，且步骤不能仅从单个文件读出",
          "target": "guide/checkout-order-submit.md"
        }
      ],
      "confidence": "medium"
    }
  ],
  "decisions": [],
  "workflows": [],
  "gotchas": [],
  "ignored": []
}
```

硬性要求：

- `modules[].id` 和 `features[].id` 在单个 Discovery 内唯一；
- 每个模块和功能至少有一个仓库内证据路径；
- `features[].module` 必须引用已有模块；
- `confidence` 只能是 `high`、`medium`、`low`；
- 没有证据的推断放入 `ignored` 或标为 `low`，不得直接生成规则或决策；
- `knowledge_candidates` 只描述值得沉淀的知识，代码可直接读出的事实放入 `ignored`。
- `root` 和所有 evidence/path 字段使用仓库相对路径，不写本机绝对路径；
- `_discovery_review.md` 应记录 `pending`、`reviewed` 或 `rejected` 状态，以及审阅范围和变更原因；
  `reconcile` 只需要重新审阅受影响模块。

`_discovery_review.md` 应逐项记录人工确认、修改和排除原因。应用审阅结果后，再运行
`scripts/validate-discovery.py`，通过后才进入页面规划。
