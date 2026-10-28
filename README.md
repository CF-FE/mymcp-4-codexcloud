# mymcp-4-codexcloud

面向 **Codex Cloud 与云端 Dot** 的 MCP、skills 和插件集合，提供组织协作、Projects 任务记录、Lody 跨端操作及云环境准备能力。

本项目由 Dot 与公子沟通、协调项目负责人，并创建独立 Codex 云任务；执行端通过 Lody 协作和回传结果。这是本项目的职责约定，平台其他创建入口见[创建方式对照](docs/lody4dot/product-collaboration-reference.md#codex-cloud-与-work-cloud-的创建方式对照)。

## 从这里开始

| 要做什么 | 入口 |
| --- | --- |
| 明确岗位、汇报、任务分配与验收 | [组织协作 skill](skill/organization-collaboration/SKILL.md) · [接入说明](docs/organization-collaboration/README.md) |
| 查询或维护 GitHub Projects | [操作 skill](skill/github-projects-operations/SKILL.md) · [完整方案](docs/github-projects-operations/plan.md) · [CF-FE 接入记录](docs/organization-collaboration/github-projects.md) |
| 通过 Lody 发现资源、操作会话和跨端交接 | [Lody skill](skill/lody4dot/SKILL.md) · [文档索引](docs/lody4dot/README.md) |
| 使用工作区共享级／项目级专业角色 | [角色库](docs/lody4dot/workspace-roles/README.md) · [设计与边界](docs/lody4dot/workspace-roles/library-design.md) |
| 准备云环境、构建或分发插件 | [lody4dot 分发](plugin/lody4dot/README.md) · [新任务验收](docs/lody4dot/fresh-task-acceptance.md) |
| 查看已导入的 Gitee MCP | [源码与运行说明](mcp/gitee/README.md) |

## 当前状态

- **云端已验入口：**固定提交 `b37b3e9` 的组织协议 **1.3.0**、Projects 操作 skill **1.1.0** 已取得指定云端执行器与 Dot 的文件接入、实际读取回执；Linux 240 项测试、包校验和 16 项离线走查通过。已读取的会话可在有效授权内继续使用，见[云端接入证据](docs/organization-collaboration/validation.md#云端固定版本接入回执)。
- **源码与分发：**组织协议 **1.4.0**、组合包 **0.8.0** 增加[局部阻塞与并行交付](docs/organization-collaboration/parallel-delivery.md)，详细规则按需读取，项目阈值不自动启用。旧版接入与0.7.1构建证据保留；Projects skill **1.1.0** 仍独立分发。新版实际读取、原生发现、持续审计和真实效果分别取证，见[本轮验证](docs/organization-collaboration/validation.md#140局部阻塞与并行交付)。
- **Gitee MCP：**已完成源码与资料导入；服务依赖安装、认证连接和实际运行未在本仓库验证。
- **正式任务管理：**正式看板是统一首查入口，全员在授权范围 list/read，写入按职责和对象收敛。已有[登记与限定切换闭环](docs/organization-collaboration/validation.md#真实登记与限定切换闭环)完成并回读；各项目仍分别确认路由和采用范围。环境仓库尚未切换正式看板，当前进度沿[唯一任务队列](.codex/agent-state/todo.md#当前环境与下一步)。

## 协作与操作流程

项目负责人作业务决定和最终验收，当前记录写者登记并回读，流程审计者核对遗漏与整改；参与者优先查询正式看板及关联证据。图表示职责与调用路线，不表示已部署自动路由或已完成权限隔离。

![看板统一入口与流程审计](docs/organization-collaboration/diagrams/traceability-and-audit.svg)

[协作图源](docs/organization-collaboration/diagrams/traceability-and-audit.mmd) · [组织方案](docs/lody4dot/project-coordination.md) · [本轮验证与接入](docs/organization-collaboration/validation.md)

<details>
<summary>展开 Projects 最短操作流程与 UNKNOWN 对账</summary>

![Projects 操作与对账流程](docs/github-projects-operations/diagrams/operation-flow.svg)

[操作图源](docs/github-projects-operations/diagrams/operation-flow.mmd) · [图表维护说明](docs/github-projects-operations/diagrams/README.md)

</details>

## 目录与开发

| 目录 | 职责 |
| --- | --- |
| [mcp/](mcp/README.md) | MCP 服务源码、依赖和运行说明 |
| [skill/](skill/README.md) | 技能唯一源码及完整随附资源 |
| [plugin/](plugin/README.md) | 组合、构建与分发定义 |

MCP 与 skill 提供能力，plugin 负责组合分发；生成物中的副本不单独维护。新增能力先读 [AGENTS.md](AGENTS.md)、目标目录说明及[架构与文档归档约定](docs/architecture.md)。

在仓库根执行，检查仅依赖 Python 3.10+ 标准库：

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
```

本仓库没有需要统一启动的公共服务；各 MCP 按自己的说明运行。lody4dot 受管 runtime 仅支持 Linux，其他宿主的工具、安装和加载能力按[支持矩阵](docs/lody4dot/support-matrix.md)分别核验。

结构检查、文件可读、实际技能读取、MCP 调用和业务验收是不同证据层级。凭证使用目标环境的安全配置，不提交凭证、依赖缓存或构建包。

## 深入阅读

- [环境、会话与权限边界](docs/lody4dot/environment-model.md) · [多宿主方案](docs/lody4dot/collaboration-development.md) · [任务卡](docs/lody4dot/collaboration-tasks.md)
- [产品协作参考](docs/lody4dot/product-collaboration-reference.md) · [云端任务交接](docs/lody4dot/space-cloud-handoff.md)
- [Lody 历史验证与已知缺口](docs/lody4dot/validation.md) · [Projects 双端报告与技能验收](docs/github-projects-operations/validation.md)
