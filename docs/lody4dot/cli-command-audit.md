# Lody CLI逐项审查与有界线上复验

日期：2026-10-25；实际CLI：`0.108.1`，Node`24.22.1`。初始离线阶段只运行版本/帮助，在不含认证材料的私密空状态中重新从根帮助递归发现公开树，再独立对照索引和固定发布源码。

发现20个一级入口、70个业务/分组命令路径，另验证12个自动生成的帮助入口，共82项。根帮助中的`__internal`与`daemon-runner`明确标为internal，不执行也不纳入公开业务覆盖。默认参数可依执行目录变化，帮助文本哈希不同不自动代表功能变化。

机器可读的[完整矩阵](../../skill/lody4dot/references/command-audit.json)与唯一[帮助快照](../../skill/lody4dot/references/help-snapshot.json)随技能提供；下表仅列option名，精确类型、默认值和完整说明按同名command在快照查阅。源码位置统一指向[0.108.1官方发布物](https://registry.npmjs.org/lody/-/lody-0.108.1.tgz)的`dist/index.js`，SHA-256为`9c8a160f6c77de765c263558e60d7b94c7293952e2c4d235ed2560f616fa8881`。

所有82项正确帮助形式均退出0；70个业务/分组项还完成handler路由/前提/效果静态审查。`help_verified`与`source_verified`都不是线上验证。CLI初始化在私密state创建过`machine-id`文件，所有自有临时状态已删除；不宣称帮助零本地写入。

初始离线审查曾记录pending_template_update，原状态保留在矩阵audit_history。随后用户明确改为提交/push后从远程main重载并初始化，已在同一任务完成下述官方CLI复验；模板API不再是本轮前置。源码重载不代表模板更新或新容器，未指定业务执行目标，也未执行Agent任务。旧探针按用户最新要求忽略，不作当前准据、待办或阻塞。

## 2026-10-25官方CLI有界复验

09:24:32–09:25:42 UTC，来源为main `a86a63f67f023796023c488b80803acfe78649c2`，Node`24.22.1`、CLI`0.108.1`。8次受控验证调用覆盖5个命令路径：`auth.py --login`调用原生login并验证workspace；另一次`workspace list`，以及两个已授权可见workspace各一次local project catalog list、agent-config list和get。全部退出0，观测到82个HTTP响应且状态均200，没有401/403。

项目目录计数分别3/2，Agent配置5/4；两个目录均fresh、无syncing标记、全部页完成，各安全get一次。名称、ID及原始输出仅在外部私密回执，不进入公开Git、技能或测试。这里的“已执行”区分临时本机身份认证和只读元数据；未执行key创建、machine配对登记、Agent发送/启动或用户配置变更，临时credentials/cache已finally清理。

诊断仅使用Node标准diagnostics_channel旁观原CLI连接，不改请求；保留必要time/method/hostname/status/request ID/cf-ray，不保存body、query、原始header或stdout/stderr。5个路径具有明确official_cli回执，其余77项仍仅help/source。Lody独立且快速迭代，本表只说明2026-10-25/0.108.1实际参数与目标范围，不是未来永久规则。

## 发现的差异与固化

- Role提议需要当前身份机器的合法会话和本机control host；`project add/delete`也需要本机control host，delete还要求TTY。普通远端session派发无需控制端daemon的结论不能套用。
- MCP读写、Operation查询、sync/export的cloud CLI路线可用独立manager，无需已有控制端daemon；业务只读仍可写缓存/SQLite并发生正常传输认证，不能承诺底层零写。
- `export --offline`仍需合法身份，只跳过前置Loro同步；图片下载与usage查询仍可能联网。`mcp add/set`的JSON写回执可含connection原值，不保证自动脱敏。
- `logout`删除本机身份，不等于撤销远端key。`start`及daemon启动可进入认证，不能作为只读健康检查；缓存hard reset也不可自动执行。
- `recover-inbox`默认离线检查不需账户身份，但需明确本机store和host lease，在Agent会话外且先停Desktop/daemon；恢复另核snapshot/orphan与全部旧资源释放。
- 仅帮助形式`lody help --help`实测退出1、向stderr输出根帮助；正确`lody help`、`lody help session`与`lody session help`退出0。失败证据保留在本任务脱敏回执，未误报为业务70项失败。

上述差异已同步[命令索引](../../skill/lody4dot/references/command-index.json)及对应技能参考。main中0.2.6的Role/Project关系修订在0.108.1 schema/handler中仍适用：create保存后runConfig为空、update仅三项业务字段、提议执行机和Role目标机器分开、本地项目属于最终机器；该复核只有source_verified，不是新的提议或项目执行验收。

## 70个公开业务及分组命令

表中“有界通过”仅对应上述官方CLI回执；临时身份认证与只读元数据分开记录。“未执行”表示该项仍仅help/source，不能从其它路径成功推断变更、发送、启动停止或业务目标已可用。控制端运行进程条件完整保存在JSON矩阵；不是把执行端前提省略。

| 命令及参数名 | 用途 | 身份 / workspace | 副作用或前提 | 验证与结果 |
| --- | --- | --- | --- | --- |
| `agent-config`<br>`--help` | Manage agent configs | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `agent-config create`<br>`--agent-type` `--workspace` `--machine` `--name` `--description` `--env` `--env-file` `--prompt` `--prompt-file` `--title-config-option` `--json` `--debug` `--help` | Create a new agent config | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `agent-config delete`<br>`--workspace` `--json` `--debug` `--help` | Delete an agent config | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `agent-config get`<br>`--workspace` `--json` `--offline` `--help` | Read one agent_config by stable id | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；有界只读通过 |
| `agent-config list`<br>`--workspace` `--offline` `--json` `--debug` `--query` `--limit` `--cursor` `--all-pages` `--machine` `--help` | List readable agent_config resources | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；有界只读通过 |
| `agent-config refresh-capabilities`<br>`--workspace` `--machine` `--json` `--jsonl` `--debug` `--help` | Refresh ACP capabilities for an agent config on the current machine | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `agent-config show`<br>`--show-secrets` `--workspace` `--json` `--debug` `--help` | Show an agent config; environment values are hidden by default | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；本次未复验 |
| `agent-config update`<br>`--workspace` `--name` `--description` `--env` `--env-file` `--unset-env` `--prompt` `--prompt-file` `--title-config-option` `--clear-title-generation` `--json` `--debug` `--help` | Update an existing agent config | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `agent-role`<br>`--help` | Inspect Agent Roles and propose creations or updates | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `agent-role create`<br>`--file` `--name` `--description` `--prompt-prefix` `--session` `--workspace` `--request-id` `--json` `--debug` `--machine-id` `--agent-config-id` `--help` | Propose an Agent Role create; save the review card in Lody to apply it | 需要 / 需要 | 提议经当前身份机器本地control socket调用所属会话，需有效本机host/Desktop或daemon；目标machineId不是提议执行机。只生成确认卡片，用户保存才生效。 | 帮助0；源码核对；业务未执行 |
| `agent-role get`<br>`--workspace` `--json` `--offline` `--help` | Read one agent_role by stable id | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；本次未复验 |
| `agent-role list`<br>`--workspace` `--offline` `--json` `--debug` `--query` `--limit` `--cursor` `--all-pages` `--machine` `--help` | List readable agent_role resources | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；本次未复验 |
| `agent-role update`<br>`--file` `--name` `--description` `--prompt-prefix` `--session` `--workspace` `--request-id` `--json` `--debug` `--help` | Propose an Agent Role update; save the review card in Lody to apply it | 需要 / 需要 | 提议经当前身份机器本地control socket调用所属会话，需有效本机host/Desktop或daemon；不是普通远端session派发路线。 | 帮助0；源码核对；业务未执行 |
| `app`<br>`--workspace` `--json` `--debug` `--help` | Open the Lody desktop app on a new chat with a local directory selected (registers it if needed) | 需要 / 需要 | 根命令有真实action：登录后尝试登记本机项目并打开桌面/链接；不是只有分组帮助。 | 帮助0；源码核对；业务未执行 |
| `app reset-cache`<br>`--hard` `--cancel` `--json` `--debug` `--help` | Clear the desktop app's local cache on its next launch (use when its window is frozen) | 不需要 / 不需要 | 写下次启动清理请求；--hard清除本地数据/登录，--cancel仅撤未应用请求，不是立即清理完成。 | 帮助0；源码核对；业务未执行 |
| `daemon`<br>`--help` | Run lody as a background daemon service | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `daemon logs`<br>`--lines` `--help` | Show daemon logs | 不需要 / 不需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `daemon restart`<br>`--help` | Restart the lody daemon (stop if running, then start) | 按路径 / 按路径 | 停止并重新启动后台运行，可能进入启动认证路径；会影响正在承载的Agent，不是只读健康检查。 | 帮助0；源码核对；业务未执行 |
| `daemon start`<br>`--auth` `--machine-name` `--skip-auth-check` `--help` | Start lody daemon in the background | 按路径 / 按路径 | 启动长期进程；可能执行认证preflight或显式认证，缺身份的副作用先核授权；不自动使用skip-auth-check绕过。 | 帮助0；源码核对；业务未执行 |
| `daemon status`<br>`--help` | Show daemon status | 不需要 / 不需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `daemon stop`<br>`--help` | Stop the running lody daemon | 不需要 / 不需要 | 停止受管host/daemon，可能中断承载工作；仅操作本任务明确拥有的进程。 | 帮助0；源码核对；业务未执行 |
| `export`<br>`--workspace` `--all-workspace` `--no-images` `--offline` `--debug` `--help` | Export user-facing workspace session data | 需要 / 需要 | 即使--offline仍需身份和workspace；只跳过前置Loro同步，默认图片下载与usage查询仍可能联网。会写导出文件，无需已有本机daemon。 | 帮助0；源码核对；业务未执行 |
| `feedback`<br>`--stdin` `--json` `--debug` `--help` | Send product feedback with account identity and basic CLI/OS information | 需要 / 不需要 | 发送反馈正文、账号身份及基本CLI/OS信息，是外部发送动作。 | 帮助0；源码核对；业务未执行 |
| `github`<br>`--help` | Manage GitHub repositories linked to a workspace | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `github list`<br>`--workspace` `--json` `--debug` `--help` | List GitHub repositories linked to a workspace | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；本次未复验 |
| `login`<br>`--debug` `--machine-name` `--auth` `--help` | Login to Lody using device authorization flow or an API key | 不需要 / 不需要 | API-key路径校验已有key并保存本机machine-id/credentials；device流程会创建远端CLI key，pairing会exchange，不能混入临时本地身份许可。 | 帮助0；源码核对；有界临时认证通过 |
| `logout`<br>`--debug` `--help` | Logout from Lody and clear saved authentication | 按路径 / 不需要 | 仅清除本机保存身份；该路径未撤销服务端key，不可报告远端凭据已作废。 | 帮助0；源码核对；业务未执行 |
| `machine`<br>`--help` | Inspect registered machines | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `machine list`<br>`--query` `--limit` `--cursor` `--all-pages` `--workspace` `--online-only` `--online-status` `--json` `--include-acp-capabilities` `--include-agents` `--debug` `--help` | List machines in a workspace | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；本次未复验 |
| `mcp`<br>`--help` | Manage workspace MCP servers | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `mcp add`<br>`--workspace` `--json` `--debug` `--offline` `--command` `--arg` `--env` `--env-passthrough` `--url` `--bearer-token` `--header` `--description` `--default` `--no-default` `--help` | Add a workspace MCP server | 需要 / 需要 | 写workspace MCP配置；JSON回执可能包含connection中的bearer/header/env原值，不保证脱敏。独立manager无需现有本机daemon。 | 帮助0；源码核对；业务未执行 |
| `mcp list`<br>`--workspace` `--offline` `--json` `--debug` `--query` `--limit` `--cursor` `--all-pages` `--help` | List readable mcp resources | 需要 / 需要 | 业务只读目录路线使用独立workspace manager，不要求已有本机daemon；仍可能写本地cache并经历正常Streams连接/短期token刷新。 | 帮助0；源码核对；业务未执行 |
| `mcp remove`<br>`--workspace` `--json` `--debug` `--offline` `--help` | Remove a workspace MCP server | 需要 / 需要 | 删除workspace MCP配置；独立manager无需现有本机daemon。 | 帮助0；源码核对；业务未执行 |
| `mcp set`<br>`--workspace` `--json` `--debug` `--offline` `--command` `--arg` `--env` `--env-passthrough` `--url` `--bearer-token` `--header` `--name` `--description` `--default` `--no-default` `--help` | Update a workspace MCP server | 需要 / 需要 | 更新workspace MCP配置；JSON回执可能包含connection中的bearer/header/env原值，不保证脱敏。独立manager无需现有本机daemon。 | 帮助0；源码核对；业务未执行 |
| `migrate`<br>`--from-oss` `--source` `--workspace` `--yes` `--debug` `--help` | Import a frozen OSS snapshot into an existing cloud workspace | 需要 / 需要 | 冻结OSS快照，写journal并导入远端数据；需源已停止，缺身份的交互路线可能进入device登录，不能当只读预检。 | 帮助0；源码核对；业务未执行 |
| `operation`<br>`--help` | Inspect Operations on this machine | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `operation list`<br>`--workspace` `--session` `--state` `--limit` `--cursor` `--json` `--debug` `--help` | List Operations owned by a requester Session and the authenticated user | 需要 / 需要 | 按身份和requester session读取本机OperationStore；打开SQLite可能初始化文件，无需已有daemon；不是跨机器全局操作列表。 | 帮助0；源码核对；业务未执行 |
| `project`<br>`--help` | Manage local projects | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `project add`<br>`--workspace` `--all-workspaces` `--json` `--debug` `--help` | Add a local project directory | 需要 / 按路径 | 只登记当前机器目录，必须本机daemon/control host可达；不迁移代码或登记远端目录。 | 帮助0；源码核对；业务未执行 |
| `project delete`<br>`--json` `--debug` `--help` | Delete local projects | 需要 / 按路径 | 必须本机daemon/control host可达且有交互TTY；删除项目登记，影响对象先确认。 | 帮助0；源码核对；业务未执行 |
| `project list`<br>`--query` `--limit` `--cursor` `--all-pages` `--workspace` `--machine` `--kind` `--catalog` `--json` `--debug` `--help` | List local projects | 需要 / 按路径 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；有界只读通过 |
| `review`<br>`--repo` `--output` `--no-open` `--help` | Render a .review.md into a self-contained HTML review and open it | 不需要 / 不需要 | 无file时给指南；有file时读取Git/审查输入、可下载Viewer、写HTML并默认打开浏览器；不需Lody账号。 | 帮助0；源码核对；业务未执行 |
| `review prompt`<br>`--help` | Print the Code Review prompt that teaches an agent to write a .review.md | 不需要 / 不需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `schedule`<br>`--help` | Manage scheduled tasks. The target machine daemon owns execution. | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `schedule create`<br>`--workspace` `--json` `--debug` `--file` `--request-id` `--help` | 管理schedule create；具体用法见实际帮助。 | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `schedule delete`<br>`--workspace` `--json` `--debug` `--help` | 管理schedule delete；具体用法见实际帮助。 | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `schedule edit`<br>`--workspace` `--json` `--debug` `--file` `--request-id` `--help` | 管理schedule edit；具体用法见实际帮助。 | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `schedule list`<br>`--workspace` `--json` `--debug` `--query` `--limit` `--offset` `--help` | 管理schedule list；具体用法见实际帮助。 | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `schedule pause`<br>`--workspace` `--json` `--debug` `--request-id` `--help` | 管理schedule pause；具体用法见实际帮助。 | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `schedule resume`<br>`--workspace` `--json` `--debug` `--request-id` `--help` | 管理schedule resume；具体用法见实际帮助。 | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `schedule run`<br>`--workspace` `--json` `--debug` `--request-id` `--help` | 管理schedule run；具体用法见实际帮助。 | 需要 / 需要 | 启动/发送/执行或取消，会产生真实业务影响；本轮不执行。 | 帮助0；源码核对；业务未执行 |
| `schedule show`<br>`--workspace` `--json` `--debug` `--help` | 管理schedule show；具体用法见实际帮助。 | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `session`<br>`--help` | Manage sessions without the web UI | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `session archive`<br>`--workspace` `--json` `--debug` `--help` | Archive a session | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `session cancel`<br>`--workspace` `--turn-id` `--json` `--debug` `--help` | Cancel the current running turn for a session | 需要 / 需要 | 启动/发送/执行或取消，会产生真实业务影响；本轮不执行。 | 帮助0；源码核对；业务未执行 |
| `session chat`<br>`--workspace` `--mode` `--mcp-server-ids` `--model` `--config-option` `--attach` `--prompt` `--prompt-file` `--json` `--jsonl` `--wait` `--timeout` `--debug` `--help` | Send a new user prompt to an existing session | 需要 / 需要 | 启动/发送/执行或取消，会产生真实业务影响；本轮不执行。 | 帮助0；源码核对；业务未执行 |
| `session create`<br>`--workspace` `--machine` `--agent` `--agent-config` `--agent-role` `--parent` `--use-current-session-as-parent` `--title` `--repo` `--local-project` `--worktree` `--branch` `--mode` `--mcp-server-ids` `--model` `--config-option` `--env` `--attach` `--prompt` `--prompt-file` `--json` `--jsonl` `--wait` `--timeout` `--history-backend` `--debug` `--help` | Create a new session | 需要 / 需要 | 启动/发送/执行或取消，会产生真实业务影响；本轮不执行。 | 帮助0；源码核对；业务未执行 |
| `session delete`<br>`--workspace` `--json` `--debug` `--help` | Permanently delete an archived session | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `session history`<br>`--workspace` `--limit` `--all` `--reverse` `--offline` `--json` `--jsonl` `--debug` `--help` | Read visible session transcript history | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `session list`<br>`--workspace` `--archived` `--all` `--opened-by` `--opened-by-current` `--query` `--machine-id` `--agent-config-id` `--agent-role-id` `--limit` `--offline` `--json` `--debug` `--help` | List sessions in a workspace | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `session observe`<br>`--workspace` `--all` `--follow` `--json` `--jsonl` `--debug` `--help` | Observe persisted Session state without executing or marking messages read (Cloud CLI) | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `session recover-inbox`<br>`--machine` `--workspace` `--execution` `--snapshot` `--orphan` `--confirm-resources-released` `--help` | Inspect blocked Inbox ownership offline; recover only after all old resources are released | 不需要 / 需要 | 不读取账户身份，直接针对明确machine/workspace/session的本地store；默认inspect为readonly SQLite，但会取得host lease，须在Agent会话外且先停Desktop/daemon。恢复参数才写store，且另需确认全部旧资源已释放。 | 帮助0；源码核对；业务未执行 |
| `session rename`<br>`--workspace` `--title` `--json` `--debug` `--help` | Rename a session | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `session restore`<br>`--workspace` `--json` `--debug` `--help` | Restore an archived session | 需要 / 需要 | 修改目标配置/状态；须另有明确资源与变更授权。 | 帮助0；源码核对；业务未执行 |
| `session show`<br>`--workspace` `--offline` `--json` `--debug` `--help` | Show session metadata | 需要 / 需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；业务未执行 |
| `session status`<br>`--workspace` `--offline` `--json` `--debug` `--help` | Show current session status | 需要 / 需要 | 可用独立workspace manager并查询目标状态，无需已有控制端daemon；状态查询成功不代表任务完成。 | 帮助0；源码核对；业务未执行 |
| `start`<br>`--machine-name` `--cli-types` `--debug` `--heartbeat-log` `--auth` `--help` | Start agent service in native mode | 按路径 / 按路径 | 启动前台host；cloud缺身份时可能进入device授权，不能当只读健康检查或仅查询版本。 | 帮助0；源码核对；业务未执行 |
| `sync`<br>`--workspace` `--all-workspace` `--concurrency` `--json` `--jsonl` `--debug` `--help` | Sync workspace Loro data to the local cache | 需要 / 需要 | 写本地工作区cache，并进行网络同步；独立manager无需已有本机daemon。 | 帮助0；源码核对；业务未执行 |
| `workspace`<br>`--help` | Manage workspaces | 按路径 / 按路径 | 显示分组帮助，子命令各自审查。 | 帮助0；源码核对；分组 |
| `workspace list`<br>`--json` `--debug` `--help` | List accessible workspaces | 需要 / 不需要 | 只读业务意图；正常认证/连接可刷新短期token，workspace manager可能写本地cache/SQLite，不承诺零底层写入。 | 帮助0；源码核对；有界只读通过 |

## 12个内置帮助入口

这些入口仅调用帮助，不是额外业务能力；`help [command]`的帮助文本对应父入口快照，不再复制全文。

| 帮助入口 | 帮助目标 | 结果 |
| --- | --- | --- |
| `help` | `lody` | 帮助退出0；无需身份或workspace；无业务执行 |
| `agent-config help` | `agent-config` | 帮助退出0；无需身份或workspace；无业务执行 |
| `agent-role help` | `agent-role` | 帮助退出0；无需身份或workspace；无业务执行 |
| `daemon help` | `daemon` | 帮助退出0；无需身份或workspace；无业务执行 |
| `github help` | `github` | 帮助退出0；无需身份或workspace；无业务执行 |
| `machine help` | `machine` | 帮助退出0；无需身份或workspace；无业务执行 |
| `mcp help` | `mcp` | 帮助退出0；无需身份或workspace；无业务执行 |
| `operation help` | `operation` | 帮助退出0；无需身份或workspace；无业务执行 |
| `project help` | `project` | 帮助退出0；无需身份或workspace；无业务执行 |
| `schedule help` | `schedule` | 帮助退出0；无需身份或workspace；无业务执行 |
| `session help` | `session` | 帮助退出0；无需身份或workspace；无业务执行 |
| `workspace help` | `workspace` | 帮助退出0；无需身份或workspace；无业务执行 |

## 后续验证边界

当前只承认上述日期、版本、参数和授权范围内的官方CLI回执；后续Lody迭代或新目标按当时实际帮助与结果核对。保留实际退出码及必要脱敏HTTP元数据，未提供字段记not_available；不会为填满表格自动跑创建/修改/删除、发消息、调度、启停服务或密钥管理。没有明确会话/业务目标的读取也不擅自进行。

当前以2026-10-25的0.108.1官方CLI实测为准；旧探针忽略，不继续诊断或列为阻塞。矩阵仅五条有明确有界回执的路径标记online_success，其它77项保持未执行；不造资源、不换身份、不绕过代理/TLS。
