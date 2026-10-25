---
name: lody4dot
description: 使用 Lody CLI 或已有 Lody MCP 管理工作区、机器、Agent 配置和角色，创建、跟进、观察、调度与交付会话任务；也用于多宿主协作、Work Cloud与Codex Cloud分工、资料空间与Dot中转、结果存回、上下文交接，以及在受支持宿主安装、诊断或排查 Lody。覆盖公开命令发现、版本差异、运行位置和结果核验。
---

# 使用 Lody 完成任务

先识别目标和环境，再执行。不要把安装 CLI、出现进程、变量存在或命令退出成功当作真实任务已经完成。

宿主、操作系统和运行角色分别识别。OpenAI的Dot是ChatGPT中的always-on agent产品，有自己的云电脑；它也可向预先配置的Codex云环境创建任务，或使用另行授权连接的本地电脑。这些执行位置分别核实，Dot不作为任意Agent的通用别名；实际插件加载、Lody工具与执行能力仍需分项验证，见[多宿主协作](references/collaboration.md)。

## 按需阅读

| 当前目标 | 阅读 |
| --- | --- |
| 资料空间与Dot中转、输入交接或结果存回 | [资料交接](references/material-handoff.md) |
| Work/Work Cloud与Codex Cloud、任务创建或触发不明确 | [任务类型与创建入口](references/collaboration.md#work-cloud与任务创建) |
| 多处安装、跨端协作、上下文交接或重建后继续 | [多宿主协作](references/collaboration.md) |
| 安装、凭证、云环境准备 | [云端准备](references/setup-cloud.md) |
| 找工作区、机器、项目或可用能力 | [资源发现](references/discovery.md) |
| 配置 Agent、Role、MCP 或 GitHub | [配置与角色](references/configuration.md) |
| 创建、继续、观察和整理会话 | [会话工作流](references/sessions.md) |
| 调度、operation 和异步协调 | [自动化](references/automation.md) |
| 同步、导出、迁移、评审、反馈或桌面恢复 | [交付与维护](references/delivery.md) |
| cloud/OSS、CLI/MCP 或运行位置不明确 | [兼容性与状态](references/compatibility.md) |
| 报错、超时、未登录、版本或连接异常 | [故障处理](references/troubleshooting.md) |

完整导航见[命令索引](references/command-index.json)，逐项参数、身份/workspace、副作用和分层验证见[全量审查矩阵](references/command-audit.json)，来源见[来源记录](references/sources.json)。矩阵由0.108.1实际根帮助重新递归发现70业务/分组路径及12个内置help入口，不代表82项业务已实跑。不要一次加载全部参考。

## 执行流程

先按目标选择资料中转、直接工具或Lody处理；资料路线见[资料交接](references/material-handoff.md)。下列流程用于实际涉及Lody的部分，纯资料交接不要求发现machine、创建Lody会话或填写Lody引用。

1. **识别宿主、角色和入口。** 区分知识读取、控制端、执行节点或混合角色；每次工具操作分别定位执行器。使用安装器或 doctor 报告的稳定绝对入口，参考中的 `lody` 代表该入口。先记录实际版本，再查准确命令的 `--help`；当前随包帮助为`0.108.1`的20类70命令，`0.107.2`业务实测仍归历史范围。版本差异或版本查询失败只提示，兼容性按当前帮助与真实结果判断。安装准备按已授权的latest策略，日常检查不因版本提示自动升级。
2. **确认请求属于哪类操作。** 帮助和本地诊断、账户资源查询、创建/修改任务、长期执行节点的前提不同。复用当前任务已有授权，不要求每条命令重复确认，也不自动扩大目标、权限或副作用。
3. **选择明确目标。** 用官方CLI的只读入口或已注入且获授权的工具，先确认允许访问的工作区，再发现其机器、项目catalog、Agent config/Role和当前能力。工作区不明时仅报告最小缺项，不从本机`/workspace`、GitHub仓库或历史验收资源推导映射。重名时使用 ID；多页结果不能只读第一页。分清控制端与执行端，核对目标机器权限、可达性和 Agent 配置，不能仅凭 online 就宣称派发或执行成功。
4. **选择可用路径。** 优先使用当前实际可用的官方CLI与原生JSON/JSONL，不为发现或派发另写业务SDK。已注入的 Lody MCP 只有在具备有效宿主上下文且已获授权时才复用；不能手工调用 `__internal` 入口冒充通用外部 MCP。没有 MCP 时不捏造工具名，也不把直接HTTP探针当成CLI目录调用成功。
5. **执行并保留结果标识。** 协作时明确唯一协调写入者及每项产物的写入者，复验端保持只读。优先使用命令实际支持的 JSON/JSONL，stdout 与 stderr 分开。保留实际 session/user turn/assistant turn 或 operation/request 标识；超时先对账，无法唯一定位时停止自动重发。
6. **核验持久化结果。** 区分提议、等待用户保存、已接受、进行中、完成、失败和取消。用受支持的观察/历史及可检查产物核对；元数据 idle、presence 消失或 CLI 退出码 0 均不能独自证明任务完成。
7. **清楚报告与交接。** 说明目标、控制/执行位置、实际操作、版本、证据来源和未运行项；跨端路径注明所属执行器，身份状态各自保存。只清理或停止本任务明确拥有的临时资源，不影响用户已有 daemon、身份或会话。

## 始终保留的边界

- `LODY_CLI_TOKEN` 是本插件的凭证入口约定，不假定 CLI 自动读取；使用认证适配器，不输出值、前缀、长度或完整环境。变量存在仅表示已注入，登录验证还可能失败。
- Lody 登录不自动提供底层 Codex/Claude 或其他 Agent 的执行凭证；不能导出当前对话的认证来补齐。
- 插件可读、工具可调用、控制可用和执行可用分别验证；安装不自动注册machine。环境恢复先查依赖与原任务，不复制其他宿主登录态，不把初始化当作继续或重发业务的授权。
- 安装器及`bootstrap --prepare`按已授权策略联网解析npm latest，在暂存目录更新lody锁并验证后切换；inspect及已有依赖的启动检查保持离线。`--repair-missing`只有明确缺少受管依赖才进入安装。显式`doctor.py --check-updates`仅查询提示，版本warn不触发升级。锁完整性、Node/OS实际支持、真实命令/身份/权限失败仍按各自结果报告。
- `session create/chat/cancel` 的运行前提取决于目标：指向本机时需本机运行进程，远端可由已登录的控制端经机器 RPC 派发，无需控制端启动 daemon；执行端仍需运行进程及 Agent 凭证。`agent-config refresh-capabilities` 保留本机要求，取消返回 `alreadyStopped` 也不证明本次取消了运行回合。
- Role 会覆盖部分手工运行参数；最终生效配置以解析结果为准。提议确认卡片不等于角色或调度已保存。
- 归档可能递归影响后代并触发执行端资源释放；恢复范围不同，也不承诺恢复同一执行进程。维护前按会话参考核对关联范围，不能把归档/恢复当作无副作用的对称开关。
- 不默认启用 `--show-secrets`、不关闭证书校验、不绕过网络代理、不因权限错误自动提高权限。
- 检查过帮助不代表业务功能已实测；没有真实连接或受控任务结果时准确保留“未验证”。
