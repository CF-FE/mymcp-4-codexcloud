# 会话任务闭环

## 先确认执行位置

`0.107.2` 的公开 CLI 区分控制端与执行端：已登录的控制端可以为明确的远端机器派发 `session create/chat`，无须在控制端启动 `lody start` 或 daemon。目标为当前登录身份的本机时，CLI 才要求本机运行进程；远端经机器 RPC 检查和派发，执行端仍需运行进程、可用 Agent 配置及其执行凭证。使用 Role 或远端目标时，记录实际机器、项目、配置及最终覆盖结果，不能用“机器在线”代替权限、派发与执行结果核验。

没有控制端 host 时，CLI 可以建立选定工作区的独立 client；这与启动会登记全部可见工作区的 host 不同。已有 Lody MCP 的调用路径只有在宿主确实注入所需上下文且工具已可用时才使用。不手动运行 `__internal` 入口。`agent-config refresh-capabilities` 仍针对本机，不能套用远端派发规则。

## 创建或继续

1. 根据任务授权选择工作区、机器、Agent config/Role、项目或仓库；需要隔离的测试任务必须用明确的隔离目标。
2. 核实目标 Agent 能力、模型和执行凭证。`LODY_CLI_TOKEN` 只用于 Lody 账户，不给底层模型自动授权。
3. 查当前 `session create --help`，确定提示词与工作上下文；指定项目时 `--repo` 与 `--local-project` 不能同时使用，也可省略两者。依赖具体目录的任务仍须核对执行端实际目录，不能把控制端路径当作远端路径。Role 可能覆盖手工 machine/agent/mode/model/config-option。
4. 创建后保存返回标识与实际参数。超时先查状态、operation 或历史，不能直接创建第二份同样工作。

实际 `0.107.2` 帮助已弃用每会话 `--env`，环境改在 Agent config 配置。`--wait` 与 `--timeout` 可用于当前命令支持的等待，但等待超时不取消已经接受的任务，也不授权重发。

```bash
lody session create --help
lody session create --workspace WORKSPACE_ID --machine MACHINE_ID --agent-config AGENT_CONFIG_ID --title "Controlled task" --prompt-file /path/to/task.md --json
lody session chat SESSION_ID --workspace WORKSPACE_ID --prompt-file /path/to/follow-up.md
```

示例不代表已授权替换这些 ID。需要项目时，使用目标机器上的已授权项目选择器，不默认为控制端创建项目。附件和 prompt-file 从运行命令的机器读取，相对路径基于当前目录；先验证全部附件准备成功，再发送。独立重跑 chat/create 是新消息或新任务，不是安全重试。

## 观察真实结果

```bash
lody session show SESSION_ID --json
lody session observe SESSION_ID --json
lody session history SESSION_ID --limit 20 --jsonl
```

history 读取用户可见 transcript，不是执行状态流；observe 附着观察持久化状态，不发送任务，也不改写已读状态。需要持续观察时，核对帮助后用 `--jsonl --follow`，不循环发送新任务或无意义高频查询。停止观察不会取消正在运行的任务。

成功核验至少保留 workspace/session、所针对的 turn 或操作标识、持久化状态及可检查产物。observe 的 `turn.finished` 区分 `completed / failed / canceled`；初始快照的 latestTurn 可反映已快速完成的任务。只读 metadata、idle、presence 消失或 workspace ready 都不能证明任务完成。`freshness: unavailable` 或仅 metadata 来源时明确证据不足。

JSONL 的 sequence 只排序当前观察进程，不能用它保证跨进程恢复或完整重放；观察重启后重新核对快照与历史。用户可见回复也不能代替目标产物与相应测试。

## 会话维护与取消

- `list` 先明确工作区、活跃/已归档筛选；查询结果不自动代表全部历史。
- `rename` 修改标题；用环境 session 选择器时采用命令支持的显式标题参数，避免位置参数歧义。
- `archive` 与 `restore` 可逆整理会话；`restore` 只针对已归档会话。
- `delete` 永久删除已归档会话，并会排队进行机器侧资源清理；不能把它当普通归档或诊断动作。
- `cancel` 针对当前任务明确允许取消的运行回合；活动回合存在时，按目标机器走本机或远端取消路径。没有活动回合或指定 turn 已不匹配时可返回 `alreadyStopped`，不能据此声称本次取消了该回合。仍须核验持久化状态，不要在用户已有任务中试验取消。
- `recover-inbox` 用于检查被阻塞的本地执行；恢复前必须确认所有旧资源（包括未记录的进程）已释放，才可按准确 workspace、machine 和 execution ID 使用恢复参数。不得自动加 `--confirm-resources-released` 来掩盖不明状态。

## 最小闭环与失败处理

先读目标与成功条件，发现并选择资源，核对执行端进程及 Agent 凭证后创建一次任务，再观察、读取历史并检查产物，最后报告结果。控制端未运行 daemon 不能独自否定远端派发；未登录、权限拒绝、目标机器不可达或底层 Agent 启动失败时保留确切失败类别，不换用未经授权身份或扩权。若发起请求已超时，工作仍可能在目标会话继续，先核验再决定后续动作。

本次已验证无控制端 host/daemon 的公开 CLI 向已有远端 Codex 配置创建任务并继续一个只读验证回合：两个回合均完成，observe 为 persisted/synced，Agent 二次读回的产物字节、JSON和随机 challenge 哈希经控制端校验匹配。公开 history 只有可见文本，不含底层工具执行日志；产物证据来自 Agent 回传，不声称控制端直接读取远端文件系统。没有测试运行中取消，也不推导其他配置和平台均已通过。

来源：[CLI：Session 命令](https://lody.ai/zh/docs/cli/)、[Agent 对话控制](https://lody.ai/zh/docs/session-orchestration/)、[Agent 角色](https://lody.ai/zh/docs/agent-roles/)、[0.107.2 发布源码](https://registry.npmjs.org/lody/-/lody-0.107.2.tgz)。官网的运行进程概括与该版本按目标分支的差异见 [来源记录](sources.json)。
