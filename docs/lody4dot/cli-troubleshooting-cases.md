# CLI路由与观察排错复盘

## 2026-10-27：远端控制可用，Role提议走错前提

本页整理原控制任务经协调端转交的脱敏回执，文档整理端没有重跑线上操作。命令参数与路径解释沿用本仓库Lody `0.108.1`帮助/源码记录，不以随包版本代替失败命令的精确运行版本。实际update参数及服务端CardID未留存，不能独立复证参数requestId或卡片全链路；不补造字段。当前`--help`及所需子命令帮助仍是命令清单和参数来源。

### 观察、纠正与结果范围

| 观察 | 应得结论与纠正 |
| --- | --- |
| 控制端可读目录并操作远端普通session，一次`agent-role update`却在控制端本机IPC前报`DAEMON_NOT_RUNNING` | 两条调用路径的前提不同；不能归因目标电脑离线、CLI未装或用户未Save。既有文档已写本机control socket条件，任务前没有核对所需入口是协调失误。 |
| 启动官方daemon可能注册本机完整host并订阅账户返回的全部工作区 | 不能把它当修复一个socket的无副作用开关。本轮未扩大该范围；这不等于所有daemon启动都禁止，恢复既有获准普通进程仍按当次身份、范围与授权判断。 |
| 用户随后明确授权在目标端新建接收session，沿其正式Role工具生成六项提议，并由用户Save | 控制线程正式get的六个完整`promptPrefix`摘要与已审版本一致，专业正文、Role标识及machine/config绑定保留。原提议回合和只读补证回合均completed/persisted/synced，idle且active为空。当前字段足以证明保存状态，但不补足未留存的update参数/卡片关联，也不证明角色实际运行。整理端只记录转交证据。 |
| 协调端读`cloud_threads`最新页时`items=[]`但仍有`nextCursor`，历史消息也滞后，曾过早报告创建未确认 | 后续分页找到真实创建回执并更正。问题包含协调端读取不足，不能全归因工具慢；当前窗口未看到不等于没有发生。该游标属于协调线程工具，不是Lody CLI的新参数。 |

### 最短预防与排错顺序

1. **初始化先核可用入口。** 现有prepare/install已检查依赖、版本和根帮助，bootstrap只做依赖就绪检查，并把认证、daemon、业务恢复标为`not_run`。复用这些结果，按[用途预检](../../skill/lody4dot/references/setup-cloud.md#初始化与任务前预检)补当前用途缺项；不新建命令表、全量探针或健康检查任务。
2. **任务开始先选路，再批量制稿/派发。** 普通远端session、控制端本机IPC提议、目标会话正式工具分别核上下文；Role绑定的machine不选择提议调用位置，传`--session`也不自动跨机。缺本机入口时先选本次授权内可用的正式路径，不能只给提示词就报告工具已执行，见[配置与Role](../../skill/lody4dot/references/configuration.md#role-的两种使用)。
3. **出错先定位发生层。** 本机IPC检查失败不证明远端故障或卡片待Save；需要恢复进程时核实际登记/订阅副作用，不自动登录、注册host或换身份。审批/授权等待、执行状态、同步覆盖和长调用分别查，不能用重跑基线替代诊断，见[故障处理](../../skill/lody4dot/references/troubleshooting.md)。
4. **进度先对原引用。** 协调线程ID、Lody session/turn、Role/proposal/request分别记录。按来源工具自己的游标设定页数/时间/条数预算；空页有后续游标便续读，到界未确认则保留UNKNOWN和未读范围，不催促重发或重建。用户问“哪个会话”时，在获准私密渠道先给真实ID、当前名称、本次卡数及状态；未确认创建就不描述卡片位置，见[会话观察](../../skill/lody4dot/references/sessions.md#观察真实结果)。

### 写入和交付应保留的边界

- 本次授权与发布稿限定`promptPrefix`，实际update参数未留存，不把设计稿冒充实际调用参数。模型/effort等非委托字段出现并发变化时，保留当前值、核来源，不推定修改者或用旧快照回滚；六项保存状态以正式get的全文摘要与必要绑定核对。独立Role可按资源合理批量/并行，同一Role的依赖更新串行，逐项保留pending/成功/失败/UNKNOWN。
- 提议生成、用户Save、保存回读、实际角色运行分开；不为补证重发结果未知的提议。已归档的旧记录者不自动恢复，也不因新提示词取得写权。
- 控制端云路径不代表目标端可读。交接先确认目标文件或正式附件的实际可读证据；提示词中列出skill路径/阅读要求不等于文件已安装、原生发现或已经实际阅读。本轮证据止于提示词指引和维护会话手动读取，原生安装、自动发现及每个Role自身实际读取未验，见[环境与权限](environment-model.md)和[资料交接](../../skill/lody4dot/references/material-handoff.md)。

改进限定为现有入口的短预检、分层归因及有界对账；本轮文档修改没有改变doctor、启停daemon、调整权限或替用户迁移正式队列。六项保存内容的转交结果不关闭其他宿主/命令、原生技能加载、后续执行和真实异常恢复的未验项。公共页不保留真实机器/会话/Role/workspace标识、用户名路径、原始提示词或凭据。

来源与完整约束：[初始化入口](../../skill/lody4dot-setup/SKILL.md)、[版本与host范围](../../skill/lody4dot/references/compatibility.md#内置-codex-与-host-范围)、[CLI逐项审查](cli-command-audit.md)、[官方CLI文档](https://lody.ai/zh/docs/cli/)、[官方Agent角色](https://lody.ai/zh/docs/agent-roles/)。帮助/源码与受信业务回执分别取证；官方概述不替代具体版本路径和本轮执行证据。
