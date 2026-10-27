# 仓库关系与知识库组织

知识库按仓库关系建模，不预设“基线库”和“宿主库”。一次运行可以包含一个仓库、一个主仓
及其子仓，或多个相互关联的主仓。

## 关系类型

- `shared-common`：多个主仓共同依赖的公共子仓；
- `business-submodule`：主仓挂载的业务或能力子仓；
- `standalone`：没有被当前扫描范围内其他仓库引用的独立仓库；
- `repository-only`：只在一个主仓中出现的知识；
- `shared-candidate`：经过多仓证据对比后，适合抽到 common 的知识。

## 生成规则

1. 先扫描仓库本身和 `.gitmodules`，建立主仓、子仓和引用边；
2. 每个仓库都可以独立生成自己的 `guide / rules / reference / decisions / gotchas`；
3. 有共同依赖时，公共仓库的 docs 描述公共能力，主仓 docs 描述接入方式和定制化行为；
4. 主仓之间的共性只有在证据对比和人工确认后，才生成共享页面；
5. 没有 common 依赖的独立仓库直接走单仓流程，不要求补造共享层；
6. 一个子仓被多个主仓引用时，公共页面不能写入任一主仓的专属假设；
7. 同名子仓在不同主仓使用不同分支或配置时，保留仓库关系和差异证据。

## 当前工作区的关系快照

| 公共子仓类型 | 对应主仓 |
|---|---|
| `aui-common` | `chatbot-ui`、`mall-ui`、`aihub-ui`、`ucenter-ui` |
| `su-common` | `console-ui`、`seller-ui`、`admin-ui` |

业务子仓包括 `su-sidenav`、`su-file`、`su-sag`、`su-appcenter`、`su-resource`、
`su-report`、`su-shell`、`su-ai`、`su-shop`、`su-sensor`、`su-business`、
`su-baremetal`、`su-cmdb`、`su-user`。它们可以被多个主仓复用，也可以单独作为仓库生成
知识库，不能仅凭名称判断是否存在共性。

当前工作区还包含独立检出的 `acm/acm`、`common/accdn` 以及各 common/业务子仓目录。
它们没有被当前扫描到的 `.gitmodules` 作为上级主仓引用时，按 `standalone` 流程处理。
