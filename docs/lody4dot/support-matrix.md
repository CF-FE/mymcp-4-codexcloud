# lody4dot 支持与验证矩阵

核实日期：2026-10-21。CLI基线为 `lody@0.107.2`；正式云环境已发布 `lody4dot 0.2.0`、来源 `d27f1a0`，当前源码为 `0.2.1` 候选。实际控制端为当前 Linux Codex 云环境；源码版本不替代正式来源或执行位置。本文覆盖全部 **20 个公开命令根、70 条公开命令路径**；逐条参数与帮助哈希见[命令索引](../../skill/lody4dot/references/command-index.json)和[帮助快照](../../skill/lody4dot/references/help-snapshot.json)。

所有路径的帮助已核实，不代表所有业务功能已经运行。下表的“通过”只覆盖列出的操作、目标及结果；“未运行”与“明确失败”分别记录。空目录查询通过，只证明该查询范围内当前没有条目。任务状态仍以[任务队列](../../.codex/agent-state/todo.md)为准，已有实测细节见[验证记录](validation.md)及[运行前提](runtime-findings.md)。

## 20 个命令根

| 命令根与知识入口 | 帮助证据 | 已运行的业务检查 | 当前边界、未运行项或失败 |
| --- | --- | --- | --- |
| [`agent-config`](../../skill/lody4dot/references/configuration.md) | 已核实 8 条路径 | 工作区完整目录查询返回 2 份已有配置；所选 Codex 配置的 `get` 通过，后续远端任务确实使用该配置 | 未创建、修改或删除配置，未刷新能力；`refresh-capabilities` 仍要求在正确本机运行，不从远端任务成功推导跨机刷新可用 |
| [`agent-role`](../../skill/lody4dot/references/configuration.md) | 已核实 5 条路径 | 真实完整列表查询通过，当前为 0 项 | 没有可验收的既有 Role；提议生成、用户保存、覆盖参数与基于 Role 的执行未实测 |
| [`app`](../../skill/lody4dot/references/delivery.md) | 已核实 2 条路径 | 未运行桌面打开或缓存变更 | 当前云机未验证桌面客户端；`reset-cache`、清除登录及下次启动效果未测，不能从 CLI 安装推导桌面功能可用 |
| [`daemon`](../../skill/lody4dot/references/setup-cloud.md) | 已核实 6 条路径 | `status` 退出 1，明确报告本机未运行；这是已确认的状态，不是 daemon 启动失败证据 | 未启动、停止、重启或恢复 daemon；长期驻留与跨任务恢复未验收。远端任务的控制端无需启动本机 daemon |
| [`export`](../../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 未运行工作区导出 | 导出用户会话、图片附件、输出完整性与离线导出未测；没有为测试导出整个工作区资料 |
| [`feedback`](../../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 未发送反馈 | 外部提交未测；需要明确的发送请求，不能自动上传账户信息或诊断资料 |
| [`github`](../../skill/lody4dot/references/configuration.md) | 已核实 2 条路径 | 已链接仓库的完整目录查询通过，当前为 0 项 | 只覆盖工作区已链接目录；不证明 GitHub App 授权、未链接仓库访问、仓库克隆或会话关联可用 |
| [`login`](../../skill/lody4dot/references/setup-cloud.md) | 已核实 1 条路径 | 全新 `0700` 任务状态在登录前 `verify-only` 退出 4、类别为 `authentication`；显式登录随后退出 0、账户为 `authenticated` | 前一结果是无登录态的预期拒绝，不是 token 登录失败。验证的是 API-key 路径；设备授权、配对、真实 keyring 存取和跨任务身份恢复未测，登录不证明远端机器已注册 |
| [`logout`](../../skill/lody4dot/references/setup-cloud.md) | 已核实 1 条路径 | 未运行 | 没有注销或撤销用户既有身份；CLI 注销的实际范围与后续状态未测。删除本任务拥有的临时状态不等于测试了 `logout` |
| [`machine`](../../skill/lody4dot/references/discovery.md) | 已核实 2 条路径 | 真实完整目录查询通过，返回 2 台 `online` 且 `canUse=true` 的已有机器；其中所选远端机器完成了受控任务 | 未新增或注册机器；其他机器的 Agent、所有协议能力及长期在线行为未逐项执行 |
| [`mcp`](../../skill/lody4dot/references/configuration.md) | 已核实 5 条路径 | 已授权工作区的完整MCP配置目录查询通过，当时为0项；后续Darwin Agent另有内置MCP的两项只读工具调用回执，见下文 | `add/set/remove`和新连接配置未测；配置目录与内置会话工具分开，不提供通用内部启动入口 |
| [`migrate`](../../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 未运行迁移 | 需要受支持的 OSS 源数据与明确目标；源关闭、记录和附件迁移、恢复续跑及导入后执行禁用行为未实测 |
| [`operation`](../../skill/lody4dot/references/automation.md) | 已核实 2 条路径 | 在本次控制端私密本机 store 中，以本任务自有 requester 查询成功，返回 0 项且 `hasMore=false` | 结果仅属于该本机 store、请求方及筛选范围，不能报告远端机器无 Operation；真实持久 Operation 的执行、恢复与协作未测，不能把 MCP 工具名当成公开 CLI 子命令 |
| [`project`](../../skill/lody4dot/references/discovery.md) | 已核实 4 条路径 | 指定工作区的完整项目目录查询通过，`kind=local` 为 1 项 | 没有读取或修改该既有项目文件，未测试 `add/delete`、本机 daemon 项目列表或 Git worktree。远端受控任务未附加既有项目 |
| [`review`](../../skill/lody4dot/references/delivery.md) | 已核实 2 条路径 | **渲染明确失败**：原生命令退出 1，未生成 HTML；匹配 Viewer 的发布资源当前不可取得 | 不能把帮助可读或其他 Viewer 的 SRI 通过当成渲染成功；匹配资源与恢复条件见下节 |
| [`schedule`](../../skill/lody4dot/references/automation.md) | 已核实 9 条路径 | `list` 退出 0；从 `offset=0, limit=100` 查询得到 `schedules=[]`、`matched=0`，没有后续 offset | 只验证目录读取；未创建、编辑、暂停、恢复、立即运行或删除调度，未验证触发、时区、补跑及执行结果。此命令的日志和分页规则见下节 |
| [`session`](../../skill/lody4dot/references/sessions.md) | 已核实 14 条路径 | 列表、历史及观察通过；已有远端Codex的create/chat两个回合completed，Agent回传产物经控制端校验；另一个running回合按assistantTurnId取消后persisted/synced/canceled。自有无后代会话的改名往返、归档/恢复通过，原标题及未归档状态还原，6条可见历史和latestTurn不变、队列及活动列表为空 | 仅覆盖该配置和受控任务；产物来自Agent回传，公开history无底层工具日志。回合取消及元数据恢复不证明工具进程终止/恢复；陈旧取消ACK可能成功，归档/恢复范围不对称。级联、删除、其他Agent/平台未测；本机Codex ACP仍有明确只读失败 |
| [`start`](../../skill/lody4dot/references/setup-cloud.md) | 已核实 1 条路径 | 未启动本机 host | 源码确认 API-key host 会登记全部可见工作区，不能将业务 `--workspace` 当成 host 范围限制；本机 Agent 执行和进程恢复未验收，不为远端派发自动启动 host |
| [`sync`](../../skill/lody4dot/references/delivery.md) | 已核实 1 条路径 | 独立 `lody sync` 命令未运行 | 目录及会话操作中的同步已有真实结果，但不能替代本命令的完整工作区缓存同步验收；同步也不等于 Git 推送、模型执行或产物完成 |
| [`workspace`](../../skill/lody4dot/references/discovery.md) | 已核实 2 条路径 | 真实账户查询退出 0，返回 2 个可访问工作区；后续只使用用户选定的个人工作区 | 未创建、变更或扩大工作区权限；账户列表成功与机器目录、长连接、任务执行分别核验 |

## 本轮查询的解析与范围

机器、Agent 配置、Role、项目、MCP 和已链接 GitHub 仓库按各自支持的完整分页入口查询。部分 `0.107.2` 目录命令在 JSON 前后输出同一工作区的两种精确 Streams attach/detach 日志；只有该窄兼容已验证，未知日志、混合工作区、多个或损坏 JSON 仍应失败，见[资源发现](../../skill/lody4dot/references/discovery.md)。

`schedule list` 的实际 JSON 是 `schedules` 与 `matched` 摘要，本次没有 `workspaceId`，前后另有两条精确匹配请求工作区的 Streams 日志。主线已按该命令的已知输出单独窄核验；不能直接套用要求 JSON 自带 `workspaceId` 的通用 `parse_native_json`，也不能任意丢弃非 JSON 文本。它使用 offset/limit；只有返回 `nextOffset` 才继续下一页，不使用 cursor 或 `--all-pages`。

Operation 的空结果只针对当前控制端的私密本机 store 与本任务自有 requester。它与选定工作区远端 Agent 的 Session 历史、活跃任务和远端持久 Operation 不是同一个查询范围。

## Review 的明确阻塞

真实 `lody review` 渲染退出 1，未生成 HTML。与固定 CLI 匹配的官方 `lody-code-review-viewer@0.107.2` 资源在 registry 与 jsDelivr 返回 404；这是当前匹配发布资源不可用，不能简化为“官网不通”或“所有 Lody 网络失败”。

另行核验的 `latest` 指向 `0.81.1`，包的 SRI 校验通过，但其模板 SHA-256 与 CLI 内置的固定预期不同，因此没有用于渲染，也没有改写预期哈希或关闭校验。SRI 通过仅证明包与该版本发布元数据一致，不能证明它符合当前 CLI 的模板契约。

恢复需取得官方匹配资源，或通过公开的 `LODY_REVIEW_VIEWER` 指定与 CLI 预期完全匹配的文件，再重跑渲染并检查实际 HTML。当前不交付虚构的渲染成功结果，资料与调用边界见[交付与维护](../../skill/lody4dot/references/delivery.md)。

## 云接入与执行位置

当前发布、源码和运行观测分别记录：

| 对象 | 已核实状态 | 不可据此推导 |
| --- | --- | --- |
| 正式云配置 | 已发布0.2.0、来源`d27f1a0`，无待发布草稿 | 当前源码0.2.1已发布、独立新任务已加载或原生插件已注册 |
| 当前运行观测 | `spec_revision/observed_spec_revision=9`，`observations_current=true`；网络与变量readiness仍为`unknown` | 将unknown填成ready/enforced，或仅凭版本变化宣布整机重建 |
| 发布后原任务恢复阶段 | 技能/接入资料读取、依赖检查及沿原Lody任务的只读对账通过；该阶段新增模型回合为0 | 首次入口送达、独立新云任务接入、真实磁盘重建或Dot自身执行；后续独立端MCP验证另记1个只读回合 |
| 源码0.2.1候选 | 补充Dot知识、接入材料及非阻塞版本策略；本轮127项回归、自包含构建、ZIP逐文件校验、包内安装复用与启动检查通过，安装输入基线仍0.107.2 | ChatGPT界面扫描/安装、正式云来源升级或独立新任务加载 |

较早0.1.3正式来源`a2e6796`、完整云准备脚本56项测试、同锁复用与离线inspect，保留为历史验收。0.1.4的56项回归、自包含包及包内安装/inspect也有独立记录；这些结果不能补齐旧截图任务当时缺少的版本和入口来源，也不能替代本次发布后的验证。

## 0.2.0 多宿主增量范围

0.2.0的108项回归、包内真实准备、新prefix缺失修复/二次检查和完整云准备脚本通过。代码固定验收来源为`2cc74de`，CLI/锁仍为0.107.2；后续正式配置已发布到包含该实现及交接记录的`d27f1a0`。发布后原任务复验见上表，独立新任务入口和真实宿主重建仍另验。0.2.1的127项回归已在本轮单独执行，不借用旧版本结果。

| 能力 | 本轮证据 | 仍缺的条件 |
| --- | --- | --- |
| 共享知识与包交付 | Linux端自主检索3场景；Darwin/arm64已有Agent经原生附件收包、显式读技能，摘要匹配 | 不能据此声称原生注册或平台自动注入 |
| 受管runtime安装/身份/进程边界 | Linux实跑；Win32/Darwin模拟结构化不支持；远端报告无Node/npm/LodyCLI | macOS native与WSL实测，Windows原生模型未定义 |
| 跨端工件复验 | Darwin单写273字节结果；Linux核对完整字节、摘要、challenge和原生引用；后续Darwin通过内置MCP查询同一会话并复验 | 证据为Agent回执及控制端字节核验，无底层工具trace；不推广至Dot、macOS受管安装或任意配置 |
| 依赖与身份恢复 | 自有临时prefix实际恢复；新私密state重新认证后沿原会话只读对账；本次发布后原任务再次只读对账通过 | C08实际宿主重建、新启动入口回执及Dot存储生命周期；同一任务恢复不替代这些证据 |
| 离线交接 | 27项行为测试；真实无产物回执blocked/3，完整记录pass/0 | 校验不证明实时身份、ACL、产物内容或业务真实性 |

详细路径和未运行项见[0.2.0验证记录](validation.md#020-linux云端与darwin-agent的实际交接)。Dot正式产品身份及部分接入路线现已核实；其自身环境生命周期、当前云ACP只读问题及Review匹配资源缺失仍分别保留，不相互替代。

## Dot官方支持路线与0.2.1候选

本轮读取9篇OpenAI官方帮助正文，确认Dot是ChatGPT中的常驻Agent产品，拥有自己的云电脑；它可在预先准备的Codex环境创建云任务，也可在用户明确连接的本地电脑使用local skills。三种执行位置分开取证，当前工具可用不能证明发生在Dot自己的云电脑。官方来源及适用范围见[宿主契约](host-contracts.md)。

| 能力或路线 | 官方事实与当前交付 | 未验证范围 |
| --- | --- | --- |
| 共享插件连接 | dots、ChatGPT、Work、Codex可共享插件权限及已有连接，仍在已授予范围内；可复用实际合法Lody工具 | 不自动复制CLI登录态、注入token、授予本地电脑或整个协作空间权限；当前候选未证明Dot实际调用Lody工具 |
| skills-only插件分发 | 官方支持含skills的插件ZIP上传及GitHub marketplace导入；候选提供[Dot宿主说明](../../plugin/lody4dot/hosts/dot.md)与[Dot验收流程](dot-acceptance.md) | 包格式候选采用已核实Codex0.163.0契约；ChatGPT界面扫描、ZIP包装接受、安装和实际原生加载未运行，完整格式指南仍CONNECT403 |
| GitHub导入 | 是正式支持的内容分发方式；不替代用户连接授权 | 当前三目录源码需builder收集技能，不能直接把未构建的`plugin/lody4dot/`当完整source；未执行导入/同步 |
| Dot委托Codex云任务 | 官方支持使用事先准备的Codex环境，可复用已发布0.2.0控制端路线 | Dot实际发起、执行位置、入口来源与该任务只读工具回执尚未取得；不是Dot自身CLI安装证明 |
| Dot连接本地电脑 | 官方要求在目标电脑的ChatGPT桌面App连接并Allow access；连接Codex或Work Sync不能替代 | lody4dot在Dot连接的本地端安装/读取未验；Lody现有Darwin Agent的内置MCP查询不证明该电脑已连接Dot |
| 准备、存储与恢复 | Dot主动Reset是产品/上下文删除；Codex Cloud默认最多7天VM恢复规则有独立作用范围 | Dot自身prepare/maintenance、周期磁盘重置及重建hooks仍未知；不将Codex会话hook、发布配置或原任务对账当成C08重建通过 |

0.2.1的29个内容文件及receipt已构建成候选ZIP，127项回归、包内同锁复用和只检查通过；字节数与摘要见[验证记录](validation.md#dot官方契约指引与021候选)。Lody CLI实际版本不同或探测失败只warn，不作为执行准入；显式`--check-updates`本轮取得npm latest0.107.2，网络失败/非最新版只提醒，默认启动保持离线且不自动升级。

后续已有Darwin Agent实际通过内置`lody_session_status_many/history`查询原会话，准确引用、273字节及challenge匹配，补齐C07有限双端范围；它使用宿主已有上下文，不依赖shell PATH的CLI。新增1个明确只读模型验收回合，最终persisted/synced/completed且无activeTurns，身份已清理。证据为Agent调用回执及控制端字节核验，不是底层工具trace或远端FS直读。详见[内置MCP验收](validation.md#远端内置mcp只读查询与c07有限双端验收)。Dot完整接入、独立新任务首次读取和实际宿主重建继续按各任务另验。

当前可用路径是 Codex 云端作为控制端，复用已有授权、在线的远端 Agent。当前云机的 managed Codex `0.160.1` bundled ACP 初始化返回 RPC1001；独立 SQLite 目录后仍有只读错误，官方代码还要求读写 Codex home 下的 `installation_id`。该本机失败不否定已通过的远端任务路径，也不泛化其他平台。

已选择的云接入路线是平台 `start_skill`；当前发布后原任务读取不替代独立新云任务收到指引、读取技能及随附资源、登录态边界的实际回执。原生注册是另一种接入模式，单独保留未验证，不追加为所选云接入路线的必选前提。范围依据见[平台契约](platform-contract.md)、[云端准备](../../skill/lody4dot/references/setup-cloud.md)和[验证记录](validation.md)。

用户新提供的截图已报告安装、认证、完整目录和手动读取通过。基本读取不要求技能全文自动注入；首次入口来源、实际版本、随附参考及重复安装记录仍待原验收任务补充，见[补充流程](fresh-task-acceptance.md#已有截图回执的补充)。不据摘要推断平台指引已送达或加载失败，不要求重复建任务、登录或发布。
