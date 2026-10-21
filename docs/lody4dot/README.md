# lody4dot 文档

lody4dot的设计、接入、验收和配套图表集中在本目录；实际任务状态与执行证据入口仍由[任务队列](../../.codex/agent-state/todo.md)维护。

## 从这里开始

| 想了解什么 | 阅读入口 |
| --- | --- |
| Dot、云任务、本地环境、会话引用和权限有什么区别 | [环境与权限指引](environment-model.md) |
| 当前哪些能力已测、哪些有条件或未运行 | [支持矩阵](support-matrix.md) |
| 如何安装、诊断和使用工具 | [插件说明](../../plugin/lody4dot/README.md)与[技能入口](../../skill/lody4dot/SKILL.md) |

## 设计方案

| 文档 | 用途 |
| --- | --- |
| [产品方案 r2](plan.md) | 目标、范围、取舍和交付定义 |
| [开发契约 d1](development.md) | 实现边界、接口、T01–T12任务与验收 |
| [多宿主协作方案 c2](collaboration-development.md) | 经Lody组织Dot、云端及本地协作的技术路线 |
| [C01–C10任务卡](collaboration-tasks.md) | 多宿主方案的实施步骤与证据要求 |
| [环境架构设计参考](environment-design.md) | 对象关系、记录模板及架构评审问题 |

## 接入与验收

| 文档 | 用途 |
| --- | --- |
| [平台契约](platform-contract.md) | 原生分发格式、云环境接入与运行边界 |
| [宿主契约](host-contracts.md) | 官方Dot、Codex、插件及生命周期来源 |
| [云任务接入与发布后恢复](fresh-task-acceptance.md) | 首次读取、发布配置和原任务恢复的分项验收 |
| [Dot与独立控制端验收](dot-acceptance.md) | 候选导入、合法工具、内置MCP及只读复验步骤 |
| [交接记录与离线校验](handoff.md) | handoff输入、阶段、示例和校验范围 |

## 运行记录与图表

- [运行前提补充](runtime-findings.md)：云端ACP、身份和执行位置的实际调查。
- [实现与验证记录](validation.md)：按轮次保存检查结果、实测范围和未运行项。
- [图表维护](diagrams/README.md)：图源、SVG和再生成方法。

新增资料按[文档归档规范](../architecture.md#文档归档规范)归入所属目录；运行时技能资料继续维护在`skill/lody4dot/`，不在这里复制一份。
