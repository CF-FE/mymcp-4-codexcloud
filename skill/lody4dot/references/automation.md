# 调度与 Operation

适用于 Lody `0.107.2` 的已记录用法。先用当前安装版本的帮助核实具体参数；以下参考没有执行真实调度或取消操作。

2026-10-25已实际重发现0.108.1公开树并核对本节帮助，handler前提只做source_verified，见[审查矩阵](command-audit.json)。cloud CLI调度控制可使用独立workspace manager；目标机器daemon仍负责实际执行。OSS/local分支有本地control前提，不能从控制端没有daemon推导所有路径均失败或均可用。本轮未修改或运行调度。

## 选择正确的操作

| 目标 | 入口 | 必须区分的结果 |
| --- | --- | --- |
| 查看和管理已有调度 | `lody schedule --help` | 调度配置、运行记录和实际会话结果是不同对象 |
| 新建或编辑调度 | `lody schedule create --help`、`lody schedule edit --help` | CLI 的实际写入结果与 MCP 生成的待确认提议不能混用 |
| 查看请求方会话的持久操作 | `lody operation list` | 读取本机 store，不是所有机器的全局任务列表 |

## 配置调度

目标是让指定机器按规则运行指定 Agent 的任务。先确认用户授权、所属 workspace、执行机器、Agent/Role、项目以及要发送的 prompt。计划时间按执行机器的本地时区计算；不能把 Codex 宿主或当前聊天显示的时区自动当成执行机器时区。

1. 查看 `lody schedule --help`，再查看具体子命令帮助。基线公开子命令包含 `list`、`show`、`create`、`edit`、`pause`、`resume`、`run`、`delete`。
2. 使用当前版本支持的 JSON draft 输入约定；先核对 `create/edit --help` 所列参数和格式，不猜 JSON 字段、文件参数或默认目标。把 draft 保存在不含凭证的任务文件中。
3. 新建时确认目的对话：每次新建、固定对话，还是已有对话；使用已有对话可能沿用它的 Agent 和上下文。
4. 执行已授权操作后，读取返回的状态与调度标识，重新查询确认保存结果。若使用当前版本支持的 `--request-id` 重试，应保持同一逻辑请求的输入和 ID，不为不确定的请求不断生成新 ID。
5. 如果目标是验证运行，再核对所属机器上的运行记录、关联 Session 和持久化任务结果；保存成功或“立即运行”请求已受理，都不等于 Agent 完成。

实际 `0.107.2` 帮助已核实 `create/edit` 的文件和重试参数；JSON 字段值仍需按准确 schema/现有配置核实，不由示例猜测：

```bash
lody schedule create --workspace WORKSPACE_ID --file /path/to/schedule.json --request-id REQUEST_ID --json
lody schedule edit SCHEDULE_ID --workspace WORKSPACE_ID --file /path/to/patch.json --request-id REQUEST_ID --json
```

`schedule list` 使用 `--offset`、`--limit` 分页，不能套用资源目录的 cursor 或 `--all-pages`。`pause/resume/run` 支持稳定 `--request-id`；是否重试先核对原请求状态。

官方说明调度由所属用户机器上的 Lody CLI 执行，机器需在线且 CLI 支持该能力。它不是由 Lody 云端替离线机器执行的任务。机器关机、睡眠或 CLI 停止时不会按时执行；恢复后按官方规则仅补最近一次错过的运行。上次尚未结束时，后续运行至多排队一次。

暂停只影响之后的触发，已经运行的会话需要单独取消。先明确用户要“暂停之后的运行”还是“取消当前任务”，不能用其中一个操作冒充另一个。

## MCP 调度提议

Agent 在 Lody 会话中使用调度提议路径时，会产生确认卡片。用户点击创建之后才真正创建；忽略卡片不会创建。Agent 不能绕过这个提议流程，或将“提议成功”报告成“定时任务已创建”。

CLI `schedule create/edit` 与 MCP 的提议能力是两个不同入口：逐一核对实际帮助、工具 schema 与返回值，不能从同名业务推断它们有相同权限和落地行为。需要修改或删除已有调度时，先检查它的创建者、状态和当前用户权限。

## 查询 Operation

已核实的只读示例：

```bash
lody operation list --workspace WORKSPACE_ID --session REQUESTER_SESSION_ID --state active --json
```

请求方会话也可由受支持的 `LODY_SESSION_ID` 提供；使用前确认其身份和工作区。`operation list` 查询当前机器的持久 store，并限定请求方会话及登录用户；不能据此推断其他机器没有任务。

0.108.1源码显示该查询不要求已有daemon，但打开本机OperationStore可能创建/初始化SQLite，不能称为零本地文件副作用。只读业务意图也不自动授予读取任意会话的权限。

需要更多结果时，以本命令帮助为准使用 `--limit` 和 `--cursor`，保持相同筛选条件继续分页。取消或其他操作先查 `lody operation --help`，不要将 MCP 工具名机械转换成未经核实的 CLI 子命令。

## 成功证据与失败退出

- 提议：返回待确认提议及其状态，只报告“等待用户保存/创建”。
- 配置变更：返回对象标识，后续查询确认目标对象已更新。
- 调度运行：运行记录关联到明确 Session，再根据持久化完成、失败或取消结果报告。
- 连接超时或结果不确定：先用原请求标识查询状态，不盲目重试可能重复触发的操作。
- 权限、工作区或机器前提不满足：指出缺失条件，保留已有对象；不改选首个可用目标，不自动扩大权限。

## 来源

- [官方定时任务](https://lody.ai/zh/docs/scheduled-tasks/)：执行机器、本地时区、确认卡片、暂停和错过运行的语义。
- [官方 CLI](https://lody.ai/zh/docs/cli/)：Operation 请求方会话、本机 store、分页与资源发现。
- [官方 Agent 对话控制](https://lody.ai/zh/docs/session-orchestration/)：会话协调与异步结果边界。
- [npm 发布物](https://registry.npmjs.org/lody/0.107.2)：基线命令分组；精确参数继续以实际帮助为准。

返回 [技能入口](../SKILL.md)。
