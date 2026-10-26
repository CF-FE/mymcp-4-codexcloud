---
name: lody4dot
description: 用 Lody CLI 或合法已有 MCP 发现资源、创建与跟进会话、管理配置和角色、交接结果；适用于云端 Dot 与 Codex Cloud 协作及受支持 Linux 环境准备。按任务读取命令或角色，不把普通资料处理变成 Lody 操作。
---

# 使用 Lody 完成任务

先使用本任务已确认的入口、目标与授权，补齐实际缺项。Dot自己的执行器、它创建的Codex Cloud任务和Lody远端节点分别定位；每条回执归实际执行位置。纯资料任务沿已有资料工具处理，无须额外创建Lody资源。

## 选择最短路径

- **已有会话：** CLI/身份/用法未变时，直接按准确workspace/session/turn[观察原结果](references/sessions.md#观察真实结果)。用户授权继续则沿原session发一次新回合；上一请求结果未知时先对账，不能用新chat/create代替查询。无需重扫资源、重查版本或重复询问有效授权。
- **首次派发或目标不明：** 只[发现缺少的目标](references/discovery.md)。重名用稳定ID，确需目录查询时处理分页和同步。版本/配置变化、权限失效或真实命令失败时，再查对应帮助和必要资源。
- **选择或维护角色：** 只有任务确需职责定义时才读[角色库](references/workspace-roles.md#按需读取角色库)。工作区共享级与项目级分开；显式选择项目才加载项目适配。日常会话操作不先读角色库。
- **准备或恢复：** 按[本端准备规则](references/setup-cloud.md)检查依赖，恢复后沿原生引用核原任务。prepare解析官方npm latest；已有runtime的inspect保持离线，版本warn不触发升级。

## 精确读取知识

优先查询一个命令或一个角色，避免展开全量JSON。源码使用`python3 plugin/lody4dot/scripts/lookup.py`；自包含包使用`python3 scripts/lookup.py`，均从实际入口运行：

```text
lookup.py command 'session observe'
lookup.py command 'session observe' --detail help
lookup.py roles --scope workspace
lookup.py role workspace_quality --project fanren-work --render
```

lookup只读随包资料，返回来源版本和范围，不调用Lody或证明当前身份可用。命令条目与实际CLI不符时查该版本帮助；无Python时按[单项读取指引](references/discovery.md#按命令读取随包资料)或角色索引直接读取必要文件。外部方法标为not_bundled时只是参考，不能宣称已安装或自动补装。完整选项与失败语义见[离线知识入口](references/knowledge.md)。

## 按目标读取

| 任务 | 资料 |
| --- | --- |
| 创建、继续、观察、取消或会话维护 | [会话工作流](references/sessions.md) |
| 资源选择、目录分页与同步 | [资源发现](references/discovery.md) |
| Agent/Role/MCP配置与提议保存 | [配置](references/configuration.md)、[共享与项目角色](references/workspace-roles.md) |
| 资料输入、结果存回或FileKiwi文件中转 | [资料交接](references/material-handoff.md)；用到FileKiwi时再读[文件中转](references/filekiwi-transfer.md) |
| 跨端交接、编码集成、Work/Codex选路或接管 | [多宿主协作](references/collaboration.md) |
| 调度/operation；导出、迁移或评审 | [自动化](references/automation.md)；[交付维护](references/delivery.md) |
| 安装/认证；错误；平台边界 | [准备](references/setup-cloud.md)；[故障处理](references/troubleshooting.md)；[兼容性](references/compatibility.md) |

## 执行与结果边界

- 复用已有授权和明确目标；角色定义、工具可见或历史批准不能扩大本次操作范围。使用官方CLI/原生JSON或合法注入的MCP，不拼内部HTTP协议或`__internal`入口。
- 远端派发通常不需要控制端daemon；实际执行端仍须具备运行进程、模型凭证和可用配置。Lody身份不等于模型身份。凭据不进入输出或包，不复制其他宿主state。
- 每项资产一个写入者，接管先交还责任。并行编码交接基准、写入范围、实际checkout和集成owner；复用已有Cloud隔离。独立宿主复验只在本次确需时增加。
- 创建/继续/保存超时先按原引用对账，UNKNOWN不自动重发。目录`syncing`不算完整；旧metadata、idle、ACK或退出0都不能单独证明本次回合完成。
- 用准确回合的持久化终态及要求的产物验收；处理、保存、目的地回读分别报告。作者自检不冒充独立QA，未取得的内容不声称已核。
- Role可能覆盖手工运行参数。提议卡需要用户Save，保存后回读；库中模型建议与实际绑定分开。归档/恢复、取消与停止观察的语义不同，涉及时读取对应会话规则。

来源版本、帮助与业务验证分别保存在[来源记录](references/sources.json)及命令条目；后续[验证记录](https://github.com/CF-FE/mymcp-4-codexcloud/blob/main/docs/lody4dot/validation.md)不推广为全部宿主或命令已测。
