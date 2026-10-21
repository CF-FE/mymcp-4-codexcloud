# lody4dot 文档

lody4dot的设计、接入、验收和配套图表集中在本目录；实际任务状态与执行证据入口仍由[任务队列](../../.codex/agent-state/todo.md)维护。

## 从这里开始

| 想了解什么 | 阅读入口 |
| --- | --- |
| Dot、云任务、本地环境、会话引用和权限有什么区别 | [环境与权限指引](environment-model.md) |
| 对外分享Chat、Work、Dot、云电脑、Codex Cloud、资料空间与侧栏图标的完整概念 | [产品协作参考（分享版）](product-collaboration-reference.md) |
| Work Cloud怎样创建、能做什么，以及实际场景怎样选择入口 | [创建与触发方式](product-collaboration-reference.md#work-cloud-可以怎样创建或触发)、[能力表](product-collaboration-reference.md#work-cloud-能做什么)、[14个场景例子](product-collaboration-reference.md#常见场景怎么选)及[资料读写](product-collaboration-reference.md#work-cloud-能直接读写资料空间吗) |
| Codex Cloud有哪些创建方式，与Work Cloud和本项目分工怎样区分 | [创建方式对照](product-collaboration-reference.md#codex-cloud-与-work-cloud-的创建方式对照)及[平台能力、当前入口与项目分工](product-collaboration-reference.md#平台能力当前入口与项目分工分开看) |
| 把本次对话结论交给继续开发的云端任务 | [资料空间与Cloud协作交接](space-cloud-handoff.md) |
| 当前哪些能力已测、哪些有条件或未运行 | [支持矩阵](support-matrix.md) |
| 如何安装、诊断和使用工具 | [插件说明](../../plugin/lody4dot/README.md)与[技能入口](../../skill/lody4dot/SKILL.md) |
| Agent怎样区分Work/Codex环境及任务创建证据 | [随包协作规则](../../skill/lody4dot/references/collaboration.md#work-cloud与任务创建)，复用既有资料交接；不是另一套方案 |
| 安装后运行setup有什么作用 | [setup技能](../../skill/lody4dot-setup/SKILL.md)及[入口说明](../../plugin/lody4dot/README.md#安装后运行-setup)；平台调用仍待实际验收 |

## 设计方案

| 文档 | 用途 |
| --- | --- |
| [产品方案 r2](plan.md) | 目标、范围、取舍和交付定义 |
| [开发契约 d1](development.md) | 实现边界、接口、T01–T12任务与验收 |
| [多宿主协作方案 c3](collaboration-development.md) | 保留Lody主干，结合已验证Dot资料中转、schema1边界与回存完成口径的辩证修订 |
| [随包资料交接知识](../../skill/lody4dot/references/material-handoff.md) | Agent执行入口：路线、输入表示、处理/保存/目的地回读分别取证；不是另一套开发方案 |
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
