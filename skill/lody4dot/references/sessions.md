# 会话任务闭环

## 先确认执行位置

`0.107.2` 的公开 CLI 区分控制端与执行端：已登录的控制端可以为明确的远端机器派发 `session create/chat`，无须在控制端启动 `lody start` 或 daemon。目标为当前登录身份的本机时，CLI 才要求本机运行进程；远端经机器 RPC 检查和派发，执行端仍需运行进程、可用 Agent 配置及其执行凭证。使用 Role 或远端目标时，记录实际机器、项目、配置及最终覆盖结果，不能用“机器在线”代替权限、派发与执行结果核验。

没有控制端 host 时，CLI 可以建立选定工作区的独立 client；这与启动会登记全部可见工作区的 host 不同。已有 Lody MCP 的调用路径只有在宿主确实注入所需上下文且工具已可用时才使用。不手动运行 `__internal` 入口。`agent-config refresh-capabilities` 仍针对本机，不能套用远端派发规则。

跨宿主共同处理目标时，按[协作参考](collaboration.md)明确协调写入者和产物写入者；独立复验仅在本次要求明确时增加。已有准确引用的观察直接使用下方入口，不重做目录发现。故障接管沿原生引用对账，不以create代替查询；需要长会话接续时按下节保存新旧关联。路径与身份不因共享任务目标而共享。

## 创建或继续

1. 根据任务授权选择工作区、机器、Agent config/Role、项目或仓库；需要隔离的测试任务必须用明确的隔离目标。
2. 核实目标 Agent 能力、模型和执行凭证。`LODY_CLI_TOKEN` 只用于 Lody 账户，不给底层模型自动授权。
3. 首次使用或版本/参数变化时查 `session create --help`，确定提示词与工作上下文；指定项目时 `--repo` 与 `--local-project` 不能同时使用，也可省略两者。依赖目录的任务核对执行端实际目录；Role可能覆盖手工参数。并行编码按[交接记录](collaboration.md#交接必要内容)明确base_commit、owned_paths、实际checkout/执行环境、integration_owner和集成验收，复用已隔离Cloud checkout。
4. 创建后保存返回标识与实际参数。超时先查状态、operation 或历史，不能直接创建第二份同样工作。

实际 `0.107.2` 帮助已弃用每会话 `--env`，环境改在 Agent config 配置。`--wait` 与 `--timeout` 可用于当前命令支持的等待，但等待超时不取消已经接受的任务，也不授权重发。

0.108.1实际帮助继续保留上述弃用提示，并为`session create/chat`增加`--mcp-server-ids <json>`；接受MCP IDs数组，`[]`禁用全部。先核对已授权的MCP目录与当前目标，再在本次任务范围内选择。帮助与参数存在不证明目标turn已加载工具；详见[配置与MCP](configuration.md)。

```bash
lody session create --help
lody session create --workspace WORKSPACE_ID --machine MACHINE_ID --agent-config AGENT_CONFIG_ID --title "Controlled task" --prompt-file /path/to/task.md --json
lody session chat SESSION_ID --workspace WORKSPACE_ID --prompt-file /path/to/follow-up.md
```

示例不代表已授权替换这些 ID。需要项目时，使用目标机器上的已授权项目选择器，不默认为控制端创建项目。附件和prompt-file从运行命令的机器读取，相对路径基于当前目录；先验证附件准备成功，再发送。控制端路径不证明目标可读，提示词中的skill路径/阅读指引不代替安装或实际读取回执，按[资料交接](material-handoff.md)分别核对。独立重跑chat/create是新消息或新任务，不是安全重试。

## 长会话接续与额度单位

2026-10-29实读[定价页](https://lody.ai/price/)：Free方案分别列出每工作区200个session、每session30个turn，不能解释为每项任务累计30轮。[首次会话第4步](https://lody.ai/docs/first-session/)明确建议长对话用简短摘要另开会话，[上下文与额度](https://lody.ai/docs/usage-and-quota/)也将摘要／新会话作为上下文管理方法。[条款9.1](https://lody.ai/terms/)指向当期方案与应用限制；所查文本未另设“同任务跨会话累计轮次”，不据此发明禁止正常接续的规则。数值是本次官方快照，不是插件固定阈值；实际新建仍服从当前工作区、方案、身份及权限准入。

上述来源未说明200是否含归档会话、刷新周期或归档是否返还额度。归档不能当作额度回收依据；不得重置计数、换身份、换工作区或改安全配置规避真实总额／权限拒绝。官方路径尚未证实时先核具体来源和拒绝范围，不猜命令，也不自行宣布全面禁止；取得官方肯定证据后纠正旧推断，重新核当前准入。

同任务已有明确续接授权时，按以下顺序处理，不重复索取泛授权；新数据外发、费用、权限或其他新增风险仍按实际范围确认：

1. **核旧执行，不再追加满额会话。** 沿原任务、session和准确turn核已受理请求、终态、队列、子tab／后代、后台作业及写锁；`UNKNOWN`继续对账，不在新会话重放。明确旧写者交还及未释放资源；不明冲突只阻塞依赖它的写入，独立获准工作可继续。
2. **保全成果并形成摘要。** 沿原任务保存目标、剩余获准范围、已验成果及版本／位置、失败和`UNKNOWN`边界、下一责任人、资源及写权交还情况。新端能实际取得必要输入才放行；摘要、路径字符串或旧PASS不替代产物回读与新版本验收。
3. **按当前准入新建一次。** 在原获准工作区核新session准入、目标机器／项目、Agent配置及权限，复用未变的有效证据。没有独立只读额度入口时，以本次已授权新建的正式准入响应为准，不编造余量或另建探针会话。仅派剩余范围，绑定同一正式任务与旧session／turn；新建失败或结果未知按原请求对账，不换路试建、不以新标题重做已验工作。
4. **确认承接与单写。** 保存新session及回合真实引用，取得明确接单ACK，并核接收端读回摘要、必要输入与成果版本；ACK本身不证明读取、执行或交付完成。旧写者交还、队列／子tab及冲突写锁未核清时，新端只做无冲突工作，不取得同一资产写权；正式记录由当前有权写者补关联并回读。
5. **在保全和移交后归档旧会话。** 按下方[维护规则](#会话维护与取消)核级联对象及既有归档授权，保留可定位的新旧引用，不删除成果或用delete清历史。[官方归档说明](https://lody.ai/docs/session/#archive-sessions)与[worktree清理](https://lody.ai/docs/worktrees/#automatic-cleanup)提示：受管worktree可先于会话永久删除而被回收；本地备份提交不是远程备份，ignored文件及cleanup脚本改删内容不保证保全，所需资产须在归档前另存到获准落点并核回读。恢复还依赖原仓库和分支。归档成功不证明后台进程、锁或预留已释放；Projects整体任务继续按原验收条件判断，不因旧会话归档而关闭。

## 观察真实结果

```bash
lody session show SESSION_ID --json
lody session observe SESSION_ID --json
lody session history SESSION_ID --limit 20 --jsonl
```

history 读取用户可见 transcript，不是执行状态流；observe 附着观察持久化状态，不发送任务，也不改写已读状态。需要持续观察时，核对帮助后用 `--jsonl --follow`，不循环发送新任务或无意义高频查询。停止观察不会取消正在运行的任务。

观察断连时按[主动恢复规则](troubleshooting.md#断连后的主动恢复)恢复原获准通道，再核同一session/turn及观察覆盖；不因此重发chat/create，也不把消息受理当作执行器恢复。

发送前记录规范化请求摘要、操作版本/幂等标识与准确目标；stdout/stderr分开接收。失败时先保留退出码及必要的脱敏原始错误字段，再清理本任务临时身份；不能只留下`native_command`分类而丢失具体异常，也不保存完整凭据、签名URL、私密输入或任意debug对象。该分类只是兜底，不能据此判定权限、网络或未送达。

0.108.1的`history --all --json`支持完整可见历史并返回`total/returned`；可按时间窗口查唯一标识与等价内容，再结合`show`的history/queue计数、`status`的latest/handled消息ID及对应turn核对。它们不提供完整服务端接收账本，可见历史为空、队列0或idle仍不能单独证明写入前失败。结果unknown时不重发；明确的新版本任务也须独立授权、核目标与基线，不以换版本或换requestId掩盖原未知操作。

读取协作端进度或分页回执时，先保留来源系统及原生引用，按该工具自己的游标继续有界读取；空页仍有后续游标不能判不存在。预设页数/时间/条数预算，到界仍未确认时报告已读范围、未读游标及下一步，保留UNKNOWN，不催促重发或重建。此规则不新增Lody CLI参数。用户问“哪个会话”时，在获准私密渠道先给真实session ID、当前名称；涉及提议卡时附本次卡数及pending/已保存/未知状态。尚无创建回执就直说未确认，不描述未经确认的卡片位置。

成功核验至少保留 workspace/session、所针对的 turn 或操作标识、持久化状态及可检查产物。observe 的 `turn.finished` 区分 `completed / failed / canceled`；初始快照的 latestTurn 可反映已快速完成的任务。只读 metadata、idle、presence 消失或 workspace ready 都不能证明任务完成。`freshness: unavailable` 或仅 metadata 来源时明确证据不足。

JSONL 的 sequence 只排序当前观察进程，不能用它保证跨进程恢复或完整重放；观察重启后重新核对快照与历史。用户可见回复也不能代替目标产物与相应测试。

### 慢任务与授权确认

2026-10-26按Lody `0.108.1`公开帮助与源码补核：任务比预期慢时，先查审批/授权等待，再沿原 workspace/session/userTurnId 核执行状态、同步/分页覆盖及长调用所在层；不要只反复报“进行中”、重跑基线或催促重发。看到 observe 的 `state=waiting` 或 `status.type=requestPermission`，立即反馈正在等待确认，并核具体工具、必要参数、目标、风险和 requestID。反馈等待不等于结束整个有界任务；继续无依赖的获准检查，确认后沿原回合跟进。

该版本 `show/status` 只提供状态和回合等元数据，`observe` 不含工具详情；公开 CLI history 与内置 `lody_session_history` 只返回可见正文，过滤 `tool_call`。因此不能承诺从这些入口取得待批工具、参数或 requestID；能力不足时明确说明，并指向原会话受信任界面的权限卡查看具体请求。请求的原生选项可能包含 `allow_once/allow_always` 等，风险仍需按实际动作评估，不整段回传原始参数、输出或私密链接。

只有用户已有授权覆盖该具体动作，且本端实际提供正式、受支持的单次确认入口，才可确认对应窄项。`0.108.1`公开 CLI 与内置 MCP 没有一次性 permission response/approve 入口；不要拼内部 RPC，不选全放行或 `allow_always`，不发“yes”、改 mode 或调整持久安全设置来代替回应。用户说“已授权”后立即重查原会话，不因这句话重发任务或再建会话。

每次对账保留原 userTurnId 及其 assistantTurnId。若 `latestTurn` 已变为后续回合，按原 assistantTurnId 匹配 history 中 `role=assistant` 且 `id` 相同的条目，读取其 `text`；不能以最新回合替代原请求结果。正文可能含私密输入，只提取本次必要结果；对应条目或终态无法确认时保留不确定状态，先对账而不重发。用户后续回合仍在运行不授权本任务取消、改写或管理其继续工作。

## 会话维护与取消

- 只读归档历史不授权restore、续发或恢复旧记录者职责；环境/服务恢复也不自动恢复旧业务会话。
- `list` 先明确工作区、活跃/已归档筛选；查询结果不自动代表全部历史。
- `rename` 修改标题；显式传入 session、workspace 与 `--title`，避免环境 session 选择器和位置参数歧义。保存原标题，需要往返验证时先检查目标空闲。
- `archive` 在 `0.107.2` 会递归归档以 `parentSessionId ?? openedBySessionId` 关联的后代，包括已经归档的后代；不能只核对根会话。先用 `session list --all --workspace WORKSPACE_ID --json` 取得包含已归档项的完整元数据，核对关联图和授权范围；该版本省略 `--limit` 返回全部同步条目，`--opened-by` 不能替代 parent 关系检查。
- `restore` 要求根会话已归档，只恢复根及直接 `parentSessionId` 子项，不承诺恢复归档时的所有递归或 openedBy 后代，也可能使原先已归档的直接子项变为未归档。先保存各受影响会话的原状态，不能把归档与恢复当作完整回滚。
- 执行端观察到归档后会释放 runtime、终端、预览及 ACP 等资源，并可能清理关联的活动子会话、安排关联 worktree 的 GC；归档前也须评估磁盘清理影响。恢复元数据不代表恢复同一进程或还原已发生的 worktree 清理；源码还保留终止失败的处理，不能从归档成功推导所有进程已停止。维护命令没有取消命令的 `--turn-id` 条件；有活动回合、排队输入或不明关联时先核实，不为测试归档用户已有任务。
- `delete` 永久删除已归档会话，并会排队进行机器侧资源清理；不能把它当普通归档或诊断动作。
- `cancel` 针对当前任务明确允许取消的运行回合；先用本次请求的 userTurnId 匹配 observe 中的 running 回合，再将对应的 **assistantTurnId** 传给 `--turn-id`。按目标机器走本机或远端路径。控制端重新同步时没有活动回合或指定 turn 不匹配，可返回 `alreadyStopped`；派发后的陈旧请求也可能被执行端忽略却返回 `success:true`。ACK 不证明取消，仍须核对同一 user/assistant 回合的 persisted/synced/canceled 终态。Operation inbox 的暂停还可能影响同一执行的后继回合，不能把 `--turn-id` 当成适用于所有协作流程的原子隔离保证。不要在用户已有任务中试验取消。
- `recover-inbox` 的0.108.1帮助将默认行为明确为所属本机store的离线检查，不传恢复参数时不执行恢复。恢复前先退出所属机器的Lody Desktop并停daemon；`--execution`须配合检查产生的准确`--snapshot`，缺失execution所有权按帮助使用对应`--orphan` token。缺execution或daemon已死不证明资源释放，必须独立确认全部旧进程和请求均已释放，再使用`--confirm-resources-released`。帮助承诺恢复保留历史与已保存结果、不重放不确定旧请求、Inbox仍保持paused；不要为清除暂停而自动发送新的human/Agent-chat输入。本轮未执行真实恢复，Windows仍需人工处理。

0.108.1源码补核：该operator入口不读取账号身份，按明确machine/workspace/session打开已有本地store；默认inspect以readonly方式打开SQLite，但仍先取得本机host lease，要求Desktop/daemon停止且不能在Agent会话内运行。它不等于普通线上session查询，也不是无任何本地影响的探针。本轮仅帮助与源码核对。

```bash
lody session cancel SESSION_ID --workspace WORKSPACE_ID --turn-id ASSISTANT_TURN_ID --json
lody session rename SESSION_ID --workspace WORKSPACE_ID --title "New title" --json
lody session archive SESSION_ID --workspace WORKSPACE_ID --json
lody session restore SESSION_ID --workspace WORKSPACE_ID --json
```

这些示例只展示准确参数，不替代目标与影响范围授权。超时先只读核对实际状态，不直接重发维护操作。无后代的自有验收会话可用于最小往返：先核对空闲、队列为空及最新回合标识，再逐步验证标题、isArchived 和最终历史；有后代时必须逐项评估原状态与恢复范围。

## 最小闭环与失败处理

先读目标与成功条件，发现并选择资源，核对执行端进程及 Agent 凭证后创建一次任务，再观察、读取历史并检查产物，最后报告结果。控制端未运行 daemon 不能独自否定远端派发；未登录、权限拒绝、目标机器不可达或底层 Agent 启动失败时保留确切失败类别，不换用未经授权身份或扩权。若发起请求已超时，工作仍可能在目标会话继续，先核验再决定后续动作。

已验证无控制端 host/daemon 的公开 CLI 向已有远端 Codex 配置创建任务并继续一个只读验证回合：两个回合均完成，observe 为 persisted/synced，Agent 二次读回的产物字节、JSON和随机 challenge 哈希经控制端校验匹配。另一次自有运行回合按 assistantTurnId 取消后，同一回合持久化为 canceled，活动列表为空。公开 history 只有可见文本，不含底层工具执行日志；产物证据来自 Agent 回传，不声称控制端直接读取远端文件系统，也不据回合取消证明工具进程即时终止。不推导其他配置、协作场景和平台均已通过。

在同一自有验收会话确认无后代、空闲且队列为0后，还完成了改名往返及归档/恢复：原标题与未归档状态还原，两个响应的 child IDs 均为空，6条可见历史和 latestTurn 保持一致，最终为 persisted/synced、无活动回合。该结果只覆盖无后代的元数据往返，未实测级联范围或进程恢复。

来源：[CLI：Session 命令](https://lody.ai/zh/docs/cli/)、[Agent 对话控制](https://lody.ai/zh/docs/session-orchestration/)、[Agent 角色](https://lody.ai/zh/docs/agent-roles/)、[0.107.2 发布源码](https://registry.npmjs.org/lody/-/lody-0.107.2.tgz)。官网的运行进程概括与该版本按目标分支的差异见 [来源记录](sources.json)。
