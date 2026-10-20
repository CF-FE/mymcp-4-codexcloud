# lody4dot 支持与验证矩阵

核实日期：2026-10-20。基线为 `lody@0.107.2`、`lody4dot 0.1.3`，实际控制端为当前 Linux Codex 云环境。本文覆盖全部 **20 个公开命令根、70 条公开命令路径**；逐条参数与帮助哈希见[命令索引](../skill/lody4dot/references/command-index.json)和[帮助快照](../skill/lody4dot/references/help-snapshot.json)。

所有路径的帮助已核实，不代表所有业务功能已经运行。下表的“通过”只覆盖列出的操作、目标及结果；“未运行”与“明确失败”分别记录。空目录查询通过，只证明该查询范围内当前没有条目。任务状态仍以[任务队列](../.codex/agent-state/todo.md)为准，已有实测细节见[验证记录](lody4dot-validation.md)及[运行前提](lody4dot-runtime-findings.md)。

## 20 个命令根

| 命令根与知识入口 | 帮助证据 | 已运行的业务检查 | 当前边界、未运行项或失败 |
| --- | --- | --- | --- |
| [`agent-config`](../skill/lody4dot/references/configuration.md) | 已核实 8 条路径 | 工作区完整目录查询返回 2 份已有配置；所选 Codex 配置的 `get` 通过，后续远端任务确实使用该配置 | 未创建、修改或删除配置，未刷新能力；`refresh-capabilities` 仍要求在正确本机运行，不从远端任务成功推导跨机刷新可用 |
| [`agent-role`](../skill/lody4dot/references/configuration.md) | 已核实 5 条路径 | 真实完整列表查询通过，当前为 0 项 | 没有可验收的既有 Role；提议生成、用户保存、覆盖参数与基于 Role 的执行未实测 |
| [`app`](../skill/lody4dot/references/delivery.md) | 已核实 2 条路径 | 未运行桌面打开或缓存变更 | 当前云机未验证桌面客户端；`reset-cache`、清除登录及下次启动效果未测，不能从 CLI 安装推导桌面功能可用 |
| [`daemon`](../skill/lody4dot/references/setup-cloud.md) | 已核实 6 条路径 | `status` 退出 1，明确报告本机未运行；这是已确认的状态，不是 daemon 启动失败证据 | 未启动、停止、重启或恢复 daemon；长期驻留与跨任务恢复未验收。远端任务的控制端无需启动本机 daemon |
| [`export`](../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 未运行工作区导出 | 导出用户会话、图片附件、输出完整性与离线导出未测；没有为测试导出整个工作区资料 |
| [`feedback`](../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 未发送反馈 | 外部提交未测；需要明确的发送请求，不能自动上传账户信息或诊断资料 |
| [`github`](../skill/lody4dot/references/configuration.md) | 已核实 2 条路径 | 已链接仓库的完整目录查询通过，当前为 0 项 | 只覆盖工作区已链接目录；不证明 GitHub App 授权、未链接仓库访问、仓库克隆或会话关联可用 |
| [`login`](../skill/lody4dot/references/setup-cloud.md) | 已核实 1 条路径 | 全新 `0700` 任务状态在登录前 `verify-only` 退出 4、类别为 `authentication`；显式登录随后退出 0、账户为 `authenticated` | 前一结果是无登录态的预期拒绝，不是 token 登录失败。验证的是 API-key 路径；设备授权、配对、真实 keyring 存取和跨任务身份恢复未测，登录不证明远端机器已注册 |
| [`logout`](../skill/lody4dot/references/setup-cloud.md) | 已核实 1 条路径 | 未运行 | 没有注销或撤销用户既有身份；CLI 注销的实际范围与后续状态未测。删除本任务拥有的临时状态不等于测试了 `logout` |
| [`machine`](../skill/lody4dot/references/discovery.md) | 已核实 2 条路径 | 真实完整目录查询通过，返回 2 台 `online` 且 `canUse=true` 的已有机器；其中所选远端机器完成了受控任务 | 未新增或注册机器；其他机器的 Agent、所有协议能力及长期在线行为未逐项执行 |
| [`mcp`](../skill/lody4dot/references/configuration.md) | 已核实 5 条路径 | 已授权工作区的完整 MCP 配置目录查询通过，当前为 0 项 | `add/set/remove`、连接、宿主注入及真实工具调用未测；空配置目录不证明当前 Agent 已加载 MCP，也不提供通用内部启动入口 |
| [`migrate`](../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 未运行迁移 | 需要受支持的 OSS 源数据与明确目标；源关闭、记录和附件迁移、恢复续跑及导入后执行禁用行为未实测 |
| [`operation`](../skill/lody4dot/references/automation.md) | 已核实 2 条路径 | 在本次控制端私密本机 store 中，以本任务自有 requester 查询成功，返回 0 项且 `hasMore=false` | 结果仅属于该本机 store、请求方及筛选范围，不能报告远端机器无 Operation；真实持久 Operation 的执行、恢复与协作未测，不能把 MCP 工具名当成公开 CLI 子命令 |
| [`project`](../skill/lody4dot/references/discovery.md) | 已核实 4 条路径 | 指定工作区的完整项目目录查询通过，`kind=local` 为 1 项 | 没有读取或修改该既有项目文件，未测试 `add/delete`、本机 daemon 项目列表或 Git worktree。远端受控任务未附加既有项目 |
| [`review`](../skill/lody4dot/references/delivery.md) | 已核实 2 条路径 | **渲染明确失败**：原生命令退出 1，未生成 HTML；匹配 Viewer 的发布资源当前不可取得 | 不能把帮助可读或其他 Viewer 的 SRI 通过当成渲染成功；匹配资源与恢复条件见下节 |
| [`schedule`](../skill/lody4dot/references/automation.md) | 已核实 9 条路径 | `list` 退出 0；从 `offset=0, limit=100` 查询得到 `schedules=[]`、`matched=0`，没有后续 offset | 只验证目录读取；未创建、编辑、暂停、恢复、立即运行或删除调度，未验证触发、时区、补跑及执行结果。此命令的日志和分页规则见下节 |
| [`session`](../skill/lody4dot/references/sessions.md) | 已核实 14 条路径 | 真实列表、历史和观察通过；已有远端 Codex 配置的 `create` 与只读 `chat` 两个回合均 completed，Agent 二次回传的产物字节及随机 challenge 经控制端校验匹配。另一个受控回合实际 running 后，以精确 assistantTurnId 取消成功，同一回合持久化为 `persisted/synced/canceled`，无活动回合 | 仅覆盖该配置和受控任务；文件证据来自 Agent 回传，公开 history 不含底层工具日志；回合取消不证明工具进程即时终止。恢复、归档、改名、删除及其他 Agent/平台未测；本机 Codex ACP 初始化另有明确只读失败 |
| [`start`](../skill/lody4dot/references/setup-cloud.md) | 已核实 1 条路径 | 未启动本机 host | 源码确认 API-key host 会登记全部可见工作区，不能将业务 `--workspace` 当成 host 范围限制；本机 Agent 执行和进程恢复未验收，不为远端派发自动启动 host |
| [`sync`](../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 独立 `lody sync` 命令未运行 | 目录及会话操作中的同步已有真实结果，但不能替代本命令的完整工作区缓存同步验收；同步也不等于 Git 推送、模型执行或产物完成 |
| [`workspace`](../skill/lody4dot/references/discovery.md) | 已核实 2 条路径 | 真实账户查询退出 0，返回 2 个可访问工作区；后续只使用用户选定的个人工作区 | 未创建、变更或扩大工作区权限；账户列表成功与机器目录、长连接、任务执行分别核验 |

## 本轮查询的解析与范围

机器、Agent 配置、Role、项目、MCP 和已链接 GitHub 仓库按各自支持的完整分页入口查询。部分 `0.107.2` 目录命令在 JSON 前后输出同一工作区的两种精确 Streams attach/detach 日志；只有该窄兼容已验证，未知日志、混合工作区、多个或损坏 JSON 仍应失败，见[资源发现](../skill/lody4dot/references/discovery.md)。

`schedule list` 的实际 JSON 是 `schedules` 与 `matched` 摘要，本次没有 `workspaceId`，前后另有两条精确匹配请求工作区的 Streams 日志。主线已按该命令的已知输出单独窄核验；不能直接套用要求 JSON 自带 `workspaceId` 的通用 `parse_native_json`，也不能任意丢弃非 JSON 文本。它使用 offset/limit；只有返回 `nextOffset` 才继续下一页，不使用 cursor 或 `--all-pages`。

Operation 的空结果只针对当前控制端的私密本机 store 与本任务自有 requester。它与选定工作区远端 Agent 的 Session 历史、活跃任务和远端持久 Operation 不是同一个查询范围。

## Review 的明确阻塞

真实 `lody review` 渲染退出 1，未生成 HTML。与固定 CLI 匹配的官方 `lody-code-review-viewer@0.107.2` 资源在 registry 与 jsDelivr 返回 404；这是当前匹配发布资源不可用，不能简化为“官网不通”或“所有 Lody 网络失败”。

另行核验的 `latest` 指向 `0.81.1`，包的 SRI 校验通过，但其模板 SHA-256 与 CLI 内置的固定预期不同，因此没有用于渲染，也没有改写预期哈希或关闭校验。SRI 通过仅证明包与该版本发布元数据一致，不能证明它符合当前 CLI 的模板契约。

恢复需取得官方匹配资源，或通过公开的 `LODY_REVIEW_VIEWER` 指定与 CLI 预期完全匹配的文件，再重跑渲染并检查实际 HTML。当前不交付虚构的渲染成功结果，资料与调用边界见[交付与维护](../skill/lody4dot/references/delivery.md)。

## 云接入与执行位置

正式配置复核已无草稿，仓库来源为公开提交 `a2e6796`，新版 `start_skill` 与保存的云启动说明逐字匹配。完整云安装脚本的 56 项测试、同锁安装复用和离线 inspect 已通过。这些是当前实例与正式配置的证据，不证明独立新云任务自动加载，也不证明原生 Codex 插件已注册。

当前可用路径是 Codex 云端作为控制端，复用已有授权、在线的远端 Agent。当前云机的 managed Codex `0.160.1` bundled ACP 初始化返回 RPC1001；独立 SQLite 目录后仍有只读错误，官方代码还要求读写 Codex home 下的 `installation_id`。该本机失败不否定已通过的远端任务路径，也不泛化其他平台。

已选择的云接入路线是平台 `start_skill`；独立新云任务收到指引、读取技能和随附资源，以及组件登录态在新任务中的边界仍需实际回执。原生注册是另一种接入模式，单独保留未验证，不追加为所选云接入路线的必选前提。范围依据见[平台契约](lody4dot-platform-contract.md)、[云端准备](../skill/lody4dot/references/setup-cloud.md)和[验证记录](lody4dot-validation.md)。
