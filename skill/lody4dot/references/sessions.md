# 会话任务闭环

## 先确认执行位置

`session create/chat/cancel` 需要当前机器运行 `lody start` 或 `lody daemon start`。查询与观察通常只需要登录和工作区权限，不代表当前机器能派发任务。使用 Role 或远端目标时，记录实际机器、项目、配置及最终覆盖结果，不能用“机器在线”代替执行前提检查。

CLI 路径受本机运行进程约束；已有 Lody MCP 的调用路径只有在宿主确实注入所需上下文且工具已可用时才使用。不手动运行 `__internal` 入口。

## 创建或继续

1. 根据任务授权选择工作区、机器、Agent config/Role、项目或仓库；需要隔离的测试任务必须用明确的隔离目标。
2. 核实目标 Agent 能力、模型和执行凭证。`LODY_CLI_TOKEN` 只用于 Lody 账户，不给底层模型自动授权。
3. 查当前 `session create --help`，确定提示词与工作上下文；`--repo` 与 `--local-project` 二选一。Role 可能覆盖手工 machine/agent/mode/model/config-option。
4. 创建后保存返回标识与实际参数。超时先查状态、operation 或历史，不能直接创建第二份同样工作。

实际 `0.107.2` 帮助已弃用每会话 `--env`，环境改在 Agent config 配置。`--wait` 与 `--timeout` 可用于当前命令支持的等待，但等待超时不取消已经接受的任务，也不授权重发。

```bash
lody session create --help
lody session create --workspace WORKSPACE_ID --agent-config AGENT_CONFIG_ID --local-project PROJECT_ID --prompt-file /path/to/task.md
lody session chat SESSION_ID --prompt-file /path/to/follow-up.md
```

示例不代表已授权替换这些 ID。附件从运行命令的机器读取，相对路径基于当前目录；先验证全部附件准备成功，再发送。独立重跑 chat/create 是新消息或新任务，不是安全重试。

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
- `cancel` 针对当前任务明确允许取消的运行回合，并验证取消结果；不要在用户已有任务中试验取消。
- `recover-inbox` 用于检查被阻塞的本地执行；恢复前必须确认所有旧资源（包括未记录的进程）已释放，才可按准确 workspace、machine 和 execution ID 使用恢复参数。不得自动加 `--confirm-resources-released` 来掩盖不明状态。

## 最小闭环与失败处理

先读目标与成功条件，发现并选择资源，满足进程及 Agent 凭证后创建一次任务，再观察、读取历史并检查产物，最后报告结果。未登录、权限拒绝、daemon 不可用或底层 Agent 启动失败时保留确切失败类别，不换用未经授权身份或扩权。若发起请求已超时，工作仍可能在目标会话继续，先核验再决定后续动作。

来源：[CLI：Session 命令](https://lody.ai/zh/docs/cli/)、[Agent 对话控制](https://lody.ai/zh/docs/session-orchestration/)、[Agent 角色](https://lody.ai/zh/docs/agent-roles/)。
