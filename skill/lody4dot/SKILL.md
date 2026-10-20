---
name: lody4dot
description: 使用 Lody CLI 或已有 Lody MCP 管理工作区、机器、Agent 配置和角色，创建、跟进、观察、调度与交付会话任务；也用于在 Codex 云端安装、诊断或排查 Lody。覆盖公开命令发现、版本差异和结果核验。
---

# 使用 Lody 完成任务

先识别目标和环境，再执行。不要把安装 CLI、出现进程、变量存在或命令退出成功当作真实任务已经完成。

## 按需阅读

| 当前目标 | 阅读 |
| --- | --- |
| 安装、凭证、云环境准备 | [云端准备](references/setup-cloud.md) |
| 找工作区、机器、项目或可用能力 | [资源发现](references/discovery.md) |
| 配置 Agent、Role、MCP 或 GitHub | [配置与角色](references/configuration.md) |
| 创建、继续、观察和整理会话 | [会话工作流](references/sessions.md) |
| 调度、operation 和异步协调 | [自动化](references/automation.md) |
| 同步、导出、迁移、评审、反馈或桌面恢复 | [交付与维护](references/delivery.md) |
| cloud/OSS、CLI/MCP 或运行位置不明确 | [兼容性与状态](references/compatibility.md) |
| 报错、超时、未登录、版本或连接异常 | [故障处理](references/troubleshooting.md) |

完整导航见 [命令索引](references/command-index.json)，来源和适用范围见 [来源记录](references/sources.json)。不要一次加载全部参考。

## 执行流程

1. **识别入口和版本。** 使用安装器或 doctor 报告的稳定绝对入口；参考中的 `lody` 代表该入口。先查版本；遇到未知参数，查 `lody <group> <subcommand> --help`。本资料基线为 `0.107.2`，不得把未知版本当已兼容。
2. **确认请求属于哪类操作。** 帮助和本地诊断、账户资源查询、创建/修改任务、长期执行节点的前提不同。复用当前任务已有授权，不要求每条命令重复确认，也不自动扩大目标、权限或副作用。
3. **选择明确目标。** 先发现工作区、机器、项目、Agent/Role 和当前能力。重名时使用 ID；多页结果不能只读第一页。分清控制端与执行端，核对目标机器权限、可达性和 Agent 配置，不能仅凭 online 就宣称派发或执行成功。
4. **选择可用路径。** CLI 和已注入的 Lody MCP 可以按真实能力使用。MCP 必须有有效宿主上下文；不能手工调用 `__internal` 入口冒充通用外部 MCP。没有 MCP 时不捏造工具名。
5. **执行并保留结果标识。** 优先使用命令实际支持的 JSON/JSONL；stdout 与 stderr 分开。创建返回的 session、operation 或 request 标识用于后续核验，超时不立即重复创建。
6. **核验持久化结果。** 区分提议、等待用户保存、已接受、进行中、完成、失败和取消。用受支持的观察/历史及可检查产物核对；元数据 idle、presence 消失或 CLI 退出码 0 均不能独自证明任务完成。
7. **清楚报告。** 说明目标、实际操作、证据和未运行项。只清理或停止本任务明确拥有的临时资源，不影响用户已有 daemon、身份或会话。

## 始终保留的边界

- `LODY_CLI_TOKEN` 是本插件的凭证入口约定，不假定 CLI 自动读取；使用认证适配器，不输出值、前缀、长度或完整环境。变量存在仅表示已注入，登录验证还可能失败。
- Lody 登录不自动提供底层 Codex/Claude 或其他 Agent 的执行凭证；不能导出当前对话的认证来补齐。
- `session create/chat/cancel` 的运行前提取决于目标：指向本机时需本机运行进程，远端可由已登录的控制端经机器 RPC 派发，无需控制端启动 daemon；执行端仍需运行进程及 Agent 凭证。`agent-config refresh-capabilities` 保留本机要求，取消返回 `alreadyStopped` 也不证明本次取消了运行回合。
- Role 会覆盖部分手工运行参数；最终生效配置以解析结果为准。提议确认卡片不等于角色或调度已保存。
- 不默认启用 `--show-secrets`、不关闭证书校验、不绕过网络代理、不因权限错误自动提高权限。
- 检查过帮助不代表业务功能已实测；没有真实连接或受控任务结果时准确保留“未验证”。
