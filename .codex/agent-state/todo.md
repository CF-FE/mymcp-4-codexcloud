# lody4dot 任务队列

权威：[上位方案r2](../../docs/lody4dot/plan.md)；契约：[开发方案d1](../../docs/lody4dot/development.md)与[多宿主方案c3](../../docs/lody4dot/collaboration-development.md)。本文件是唯一进度和执行证据入口。

当前授权：2026-10-20用户明确选择在本对话持续执行r2/d1；2026-10-21确认环境发布，并授权继续推进多宿主方案和任务卡、尽量自主完成。此前c2已授权主干保留；Role/Project知识0.2.6已交付。本轮用户明确“按优先级持续推进”：先固化离线ZIP命令，再修正离线测试夹具的宿主依赖，分别验证和提交；不扩大远端配置写入、新服务/部署或云环境权限。未创建后台Goal。`planned`表示尚未满足全部执行前提；可独立进行的准备继续，真实验收不以模拟结果替代。

## 当前环境与下一步

2026-10-21按用户要求实施Role/Project知识增量。来源修正已在spec17正式生效；本次最新观测为spec21，正式0.2.5、无草稿；0.2.6是独立知识候选。发布状态只在本节维护；历史spec17的ready及较早unknown均保留当时原义。

| 项目 | 本次实际结果 |
| --- | --- |
| 正式配置 | 固定`0a044f14622902b6d8d93418338df2251b7a38f8`/0.2.5，无草稿、无pending要求；0.2.5云环境来源升级已完成，不代表ChatGPT/Dot原生插件安装完成 |
| 工作副本 | 本轮开始于干净c8679b6，ff-only拉取无更新；先实现源码builder的离线ZIP可选输出，再修改测试夹具。保留0.2.6及更早ZIP、CLI锁和云脚本 |
| 运行观测 | 最新spec/observed21，observations_current=true，running/connected，failure=null；与已发布来源分别核对，不将spec变化推断为独立任务或VM/存储重建 |
| 网络与变量 | 最新network及两变量state均unknown，不用spec17的ready补填；未推断凭证无效、重配绑定或扩大网络。元数据readiness与实际服务授权仍分别验收 |
| 本轮依赖与回归 | 0.2.7的143项Linux回归（构建26项）、结构、ZIP真实命令/重复路径拒绝及移位离线bootstrap通过；移位仅doctor、bundle/runtime consistent，install/认证/daemon/任务恢复not_run。同锁CLI0.107.2，未升级 |
| 来源升级 | spec16保存的源修正已在spec17发布生效；本轮配置仍为同一正式ref、无草稿，不重新保存相同配置 |
| 独立Codex云任务入口 | 由Dot创建，用户已确认Dot具备权限；当前云任务不派生Codex云任务，不查询OpenAI任务目录。历史Cloud CLI/401尝试已撤下，不作插件前置或阻塞 |
| 用户setup入口 | 0.2.7沿用已有setup及Work适用范围，本轮未改入口；官方0.163.0 parser亦支持字段。已核实的CLI无独立setup/validate/dry-run，原生实际调用未验 |
| 当前候选 | 0.2.7在源码builder增加显式离线ZIP生成/验证和摘要；26构建测试与真实CLI通过。0.2.6知识及三场景证据保留，随包运行工具/CLI锁不变，非原生加载或业务验收 |
| Work创建入口观测 | 本轮可调用目录仍未见create_thread/chatgptWorkCloud；没有创建尝试。这仅描述本端工具范围，不推导Dot无权限或全产品无入口 |
| Role/Project验证范围 | 既有只读目录与Agent配置执行已测；先前帮助/源码确认多Role可复用配置、会话可组合Role与项目。多个Role创建/用户保存、项目登记及按Role运行未实测，见[关系核实](../../docs/lody4dot/validation.md#agent配置role与project关系核实) |
| 历史运行中恢复实验 | 单次新chat，准确回合running时SIGTERM本地follow观察进程并清理A身份；新B身份前4次仍见同turn running，第5次persisted/synced/completed。新274字节/SHA/challenge匹配，原8条历史未变、总10条；两身份清理。不是控制主机重启 |
| 下一步 | 非Dot增量按优先级执行：ZIP命令done，测试夹具修订planned，提交前者后继续后者；不改正式0.2.5或生成环境草稿。独立首次加载、实际Role/Project配置写入、真实跨平台和Dot路线仍按各自前提验收，不把本地工具/模拟结果补成真实宿主证据 |

## 原有交付任务

| ID | 结果 | 依赖 | 状态 | 执行证据 |
| --- | --- | --- | --- | --- |
| [T01](../../docs/lody4dot/development.md#t01冻结加载方式和平台契约) | 加载与平台契约 | 无 | done | [平台契约](../../docs/lody4dot/platform-contract.md)：同版本官方清单与技能路径已核实；采用云环境接入并交付原生产物，T09另验加载 |
| [T02](../../docs/lody4dot/development.md#t02验证固定版本运行时并生成锁定输入) | 固定版本与锁定输入 | T01 | done | [运行时记录](../../docs/lody4dot/validation.md)：锁定0.107.2和Tinypool2.1.2；冻结安装、native及原始worker通过，audit 0 |
| [T03](../../docs/lody4dot/development.md#t03实现技能来源与命令覆盖) | 技能、来源、命令覆盖 | T02 | done | [知识检查](../../docs/lody4dot/validation.md)：20类/70路径及帮助哈希匹配，未冒称业务已实测 |
| [T04](../../docs/lody4dot/development.md#t04实现可重复且失败可恢复的安装器) | 重复安装与失败恢复 | T02 | done | [安装器验证](../../docs/lody4dot/validation.md)：14项行为测试及真实安装/同锁复用通过 |
| [T05](../../docs/lody4dot/development.md#t05实现唯一只读-doctor) | 只读诊断 | T02 | done | [诊断与认证验证](../../docs/lody4dot/validation.md)：离线inspect、真实账户与完整workspace目录通过；窄兼容Streams诊断，doctor不推导任务成功，真实任务另见T10 |
| [T06](../../docs/lody4dot/development.md#t06实现显式认证适配) | 显式认证适配 | T05 | done | [诊断与认证验证](../../docs/lody4dot/validation.md)：显式模式、私密state、假凭证不回显通过；真实login/verify-only已通过，不误报机器注册 |
| [T07](../../docs/lody4dot/development.md#t07实现自包含构建与云环境接入) | 自包含包与云接入 | T03、T04、T05、T06 | done | [分发与云配置](../../docs/lody4dot/validation.md)：22文件移位安装通过；草稿保存已确认，用户随后确认已发布；实际加载未验 |
| [T08](../../docs/lody4dot/development.md#t08完成无账户集成与分发回归) | 无账户集成验证 | T07 | done | [无账户验收](../../docs/lody4dot/validation.md)：48项条目测试加8项原仓库测试通过，移位CLI安装及inspect通过 |
| [T09](../../docs/lody4dot/development.md#t09完成干净云任务加载安装和真实发现) | 真实云端加载、安装、发现 | T08；宿主、身份、网络、工作区 | blocked | [旧截图回执](../../docs/lody4dot/validation.md#用户截图回执与加载判定)报告安装/认证/目录及手动读取通过；该任务首次入口来源、实际源码/插件版本、参考及同锁记录待补。旧正式基线为0.1.3，不能以本轮0.2.0发布后恢复替补当时事实；在原任务补已有记录，不要求重建或重复认证。全文自动注入及原生注册均非该路线必选门槛 |
| [T10](../../docs/lody4dot/development.md#t10验证-agent-任务能力与受控执行闭环) | agent 场景与真实任务 | T09已验证的发现；测试目标、执行凭证 | done | [远端验收](../../docs/lody4dot/validation.md)：已有远端Codex create/chat两个回合completed，Agent二次读回字节及challenge校验匹配；另一个自有运行回合精确取消后为persisted/synced/canceled，无activeTurns；不冒称直接FS读取或工具进程终止 |
| [T11](../../docs/lody4dot/development.md#t11补齐高级能力的场景与平台边界) | 高级场景与支持矩阵 | T10 | done | [支持矩阵](../../docs/lody4dot/support-matrix.md)覆盖20根/70路径，列明高级只读实测、Review上游artifact失败、条件支持及未运行项；完成的是支持边界与场景覆盖，不冒称全部高级业务已运行 |
| [T12](../../docs/lody4dot/development.md#t12交付复现与支持范围确认) | 复现与交付 | T10、T11 | blocked | 分发、远端基本闭环和支持边界已复核；待T09截图对应任务补来源、版本等缺项，不标整体交付完成 |

既有r2/d1尚缺旧截图对应任务的来源和版本等记录，按[验收流程](../../docs/lody4dot/fresh-task-acceptance.md)核对后继续T12；不为补旧字段重新创建任务、登录或查询资源。自主检索后实际读取可以证明基本读取，首次入口来源仍须如实区分。T10远端闭环与T11支持矩阵已完成，不把T09旧补证设为c2独立工作的隐藏总前置。个人workspace及已有Agent测试授权保留；本机只读限制不阻塞获准远端控制。

运行状态见上方唯一快照。当前0.2.5候选的回归、分发和知识判断见[本轮验证](../../docs/lody4dot/validation.md#平台入口与项目职责知识025候选)，aea6798的0.2.4包及验证记录完整保留；CLI0.107.2仍只是知识/默认安装基线，版本不同或不可查询仅warn。不由发布版本补填旧任务事实。

环境、任务、实例、Dot会话引用及协作空间/Lody权限分别识别，见[环境模型](../../docs/lody4dot/environment-model.md)。不承诺某客户端或网页必然能选到此环境；“本机ACP”指当前云执行实例，不是用户电脑。

拟议任务先登记为 `planned`；开始执行后的状态为 `in_progress / blocked / done`。blocked 需注明具体前提及仍可推进的独立项；done 必须链接实际结果与未运行项。任务完成不等于整体发布完成，能力缺口不得被结构检查或 fixture 通过掩盖。

## r2/d1历史执行记录（2026-10-20至2026-10-21较早轮次）

以下历史段落的“当前”“本次”“仍”仅指各自轮次。较早正式版本、readiness、未运行项及草稿记录按当时事实保留；最新状态见开头唯一快照、C任务表及文末对应轮次记录。

### 本轮规划复核

2026-10-20，针对 r2/d1 完成独立审视：正常完成、安装失败、关键前提不成立三条路径未发现实质矛盾。5 份新改文档的 38 处本地链接、12 个任务与无环依赖检查通过，8 项现有仓库测试通过。这些是规划与仓库检查证据，不是上述实现任务的完成证据。

### 用户确认发布后的复查

2026-10-20，用户明确回复“已保存并发布”。只读复查：当前进程无任何 LODY 变量；当前运行状态 observations_current=true，spec_revision/observed_spec_revision 均为3，custom allowed_hosts 仅 lody.ai，runtime_variables 为空；三个服务域名实际 HTTPS 仍为 CONNECT 403。保存配置可读为 revision 5、四域名和 pending direct-environment-variable LODY_CLI_TOKEN。用户发布已作为会话事实接收；这些观测仅说明当前实例尚未获得对应配置，不能推断 token 无效或用户未配置。

可用工具不包含当前实例的发布、重启或切换入口。不重复写配置以免制造新草稿；先等待宿主重连/传播后按实际状态复查，若本会话持续保留旧运行实例，可在已发布环境的新云任务继续 T09。新任务先读本队列并复查变量存在性和实际网络，再做显式授权及只读发现；不要重新要求填写 token。

### 本次发布生效与真实授权

2026-10-20，用户再次发布后，同一任务观测 spec_revision/observed_spec_revision=4，四域名已生效，进程token present。auth login和verify-only均退出0，真实工作区查询ok且count=2。用户已明确选择个人workspace用于本机临时目录小任务，不再次询问。

目录查询发现新的、可复现的阻断：api/control-b/control-c/presence.streams-api-x.loro.dev 均 CONNECT403；机器及Role列表原始exit1，不当成空列表。网络规则按源码分片模式补充 *.streams-api-x.loro.dev；保留已有规则与变量。doctor 0.1.1可用 --workspace 保留账户已认证/目录失败的分项证据。后续先复验目录，再做观察与任务；没有启动daemon或创建真实会话。

### Loro 规则发布后的历史观测

用户已确认发布，正式配置中可读 *.streams-api-x.loro.dev（无新草稿），但当前运行实例仍为 revision4、仅四域名，实际 CONNECT403；完成独立准备后复查仍未变化。没有重复保存配置或重新登录。

[运行前提补充](../../docs/lody4dot/runtime-findings.md) 记录了适配器版本、managed0.160.1的受管入口、无模型初始化失败与官方状态目录边界，以及原生host会覆盖API-key可见的全部工作区。没有越过用户的个人工作区范围启动host。临时项目及验收断言已备妥，实际目录、观察和任务闭环仍待条件满足。

### 本次发布生效、目录与观察通过

2026-10-20，同一实例revision5和Loro分片规则已生效，实际HTTPS不再CONNECT403。新建0700私密任务state完成真实登录；account与完整machine目录均通过。个人workspace有2台机器、0个Role、2个Agent配置及工作区目录中kind=local项目1项，全部为真实查询结果，不在仓库存放ID或业务文本。

0.107.2原生目录在JSON前后输出两种精确Streams日志，导致此前工具误报无效响应；窄兼容已修复、独立审查通过，新增边界测试后共56项通过。实时agent从cloud-start与技能参考独立完成完整目录和观察：all观察2项synced/metadata，定点观察已有会话为synced/persisted且存在latestTurn。未发消息或取消已有任务；没有新任务或产物证据。该演练显式获知入口，不能证明新云任务自动加载。

本地daemon确实未运行。已校验官方managed0.160.1下载及版本，bundled ACP initialize仍RPC1001；只迁移子进程SQLite目录后实际RPC仍read-only。同版本官方代码和只读元数据确认额外强制写入CODEX_HOME/installation_id，而当前该文件系统只读；不存在独立目录选项可由sqlite_home/log_dir/cwd替代。当前支持安装、控制查询和观察；本机执行需平台提供可写环境或另行验收已授权worker。0.1.2自包含包及云安装脚本通过，包内真实control检查通过；全局凭证绑定保留，自有测试私密state已清理，没有新草稿或登录态快照。

### 已有远端Agent的受控验收

用户明确授权并指定“用已配置的agent来测试”。源码复核纠正先前关于控制端必须运行daemon的概括：公开0.107.2 CLI可独立连接指定工作区并向已有在线远端machine/config派发。本机执行与refresh-capabilities的前提不变；没有写入受保护installation_id或改HOME/CODEX_HOME。

已选择个人工作区唯一在线Codex配置，不附加既有项目，以固定标题新建一次会话。首回合创建临时验收文件并completed；后续只读chat回传文件字节和随机challenge，控制端验证input逐字节、结果JSON、Unicode/行数/逆序内容和challenge全匹配。最终observe为persisted/synced/latestTurn.completed且无activeTurns；history有两对user/assistant记录。独立验收审查通过，明确文件证据来自Agent回传，公开history不含底层工具执行日志，未声称直接远程FS读取。

没有新增机器、Agent配置、项目或Role，没有启动控制端host或影响其他工作区。已有用户会话未被操作；仅保留本次新建验收会话和临时产物。取消、其他Agent/平台、长期worker和高级操作仍未实测。T10的远端结果独立成立，T09新云任务加载仍须另验。

0.1.3的56项回归、结构检查、自包含构建和ZIP完整性通过，已生成不含身份的验收产物包；本轮私密认证state已清理。更正后的start_skill草稿已确认saved/requires_publish=true，仅供后续任务复用，未重配网络或变量；当前验收不再等待环境发布。原生插件注册、新云任务读取回执和高级场景仍分别留在T09/T11。

### 0.1.3正式发布后的复验

正式配置无draft，仓库ref=a2e6796，start_skill与checkout逐字一致；现有token和网络均ready/enforced，无需再次发布相同配置。cloud-install退出0，56项测试、同锁复用和inspect通过。新0700 state在登录前verify-only预期authentication失败，显式login后真实control/完整机器目录通过；只读重查自有验收会话为persisted/synced/completed，无activeTurns。认证state已清理，没有创建新模型任务或改远端资源。

高级只读MCP/Role/GitHub/Schedule查询通过，当前结果均为空；Operation只代表新controller本机store及自有requester，不能当全局空操作。Review真实渲染退出1/noHTML，已定位固定Viewer0.107.2官方artifact缺失；其他版本虽SRI通过但模板hash不匹配，未使用或放宽校验。具体条件与证据见支持矩阵和验证记录。

当前宿主工具没有新建/附着独立云任务的入口；子agent或同实例发布不冒充新任务加载。最小外部回执流程已写[新任务验收](../../docs/lody4dot/fresh-task-acceptance.md)。没有重存已发布配置或要求用户重新添加token；本轮只更新仓库中的验收文档。

T11按开发契约完成支持范围和场景覆盖：20根/70路径数量、来源、实测和条件边界已逐项核对，独立复核通过。Review保留明确上游阻塞，取消等未运行项不改成通过。整体交付仍由T12受T09新任务实证约束。

### 运行中精确取消补测

2026-10-20，当前会话继续使用已获授权的远端Codex配置和本任务自建验收会话。唯一匹配、空闲及空队列检查通过后只发一次受控chat；观察到本次userTurnId对应的唯一running assistantTurnId，再用--turn-id精确取消。原生响应success=true且不是alreadyStopped；最终同一user/assistant回合persisted/synced/canceled、activeTurns为空。详见[验证记录](../../docs/lody4dot/validation.md#运行回合的精确取消验收)，支持矩阵已更新。

取消闭环仅指Lody回合，不推导远端工具进程启动或即时终止。新建私密认证state已清理，没有改动其他用户会话、远端配置或已发布云配置。T09仍缺独立新云任务回执，T12仍blocked；本轮文档证据不改变0.1.3发布物。

### 会话维护与0.1.4知识修正

2026-10-21，用户要求持续推进能完成的部分。仅对本任务自有会话，以完整含归档元数据确认无后代、空闲/空队列后，完成rename往返、archive、restore；原标题与未归档状态还原，child IDs均为空，6条可见历史及latestTurn保持一致，最终persisted/synced、无activeTurns。未新增模型回合或配置，未向其他会话发起维护命令；认证state已清理。

独立源码复核修正归档递归范围、restore直接parent子项及资源释放的不对称，补入取消陈旧请求可能ACK成功和Operation inbox后继的边界。技能、索引、来源与分发说明同步为0.1.4；56项回归、结构、自包含构建、包内同锁安装/inspect及ZIP完整性通过，旧0.1.3产物保留，详见[验证记录](../../docs/lody4dot/validation.md#会话维护往返与知识修正)。已发布环境未改，T09/T12仍blocked，Review及本机ACP限制继续保留。

### 用户提供验收截图后的判定

2026-10-21，用户回传验收截图：报告Lody0.107.2安装检查、注入凭证认证及两个工作区的完整机器目录查询通过，技能和启动指引手动找到读取、未观察到自动加载；私密登录态已清理，无daemon或模型任务。这是用户提供的结果摘要，不冒称本会话执行日志；不复制工作区名称或业务数据入库。

原方案要求新任务实际读取入口、定位参考与诊断工具，没有要求技能全文自动注入。截图中的“手动”尚不能区分agent自行检索和用户给路径，也未列初始指引来源、源码SHA、插件版本、随附参考及重复安装记录；因此不判自动加载失败，也不提前关闭T09/T12。已只读核实正式ref仍a2e6796、start_skill完整、无草稿。最小下一步是在截图对应的原任务补这些已有记录；不重新建任务、不重复登录/查询、不重存配置。

### 环境与权限指引

2026-10-21，按用户要求将Dot、会话、云任务、发布版本、执行实例、本地环境及协作空间/Lody权限沉淀为[指引](../../docs/lody4dot/environment-model.md)。包含概念表、引用与权限表、状态保留范围、当前事实映射、交接场景、建议的关联记录与架构评审清单。

配套三张Mermaid图及SVG分别展示执行关系、发布/加载证据阶段和权限条件；保留源码、替代文字和渲染说明。正文标明事实、用户回执、建议与未知，不推测客户端入口或任务/实例一对一关系。该文档交付不等于T09/T12已通过，也不更新环境或0.1.4安装包。

指引经辩证评审后按“一分钟速查→实际链路→三个空间→按问题查表”重排，技术记录移至[设计参考](../../docs/lody4dot/environment-design.md)。分别识别Agent决策与工具位置、发布配置与安装快照，并改为通过已授权的必要请求核实未知访问权限；三张图同步。既有验证范围和T09/T12缺口保持按原证据记录。

## 多宿主协作与初始化方案

2026-10-21较早的c1阶段形成了多宿主安装、Lody协作与初始化方案，随后9篇官方Help明确Dot的产品关系并修订c2。现行[c3](../../docs/lody4dot/collaboration-development.md)延续已授权主干，补已试通的资料中转与交付口径；[C01–C10卡片](../../docs/lody4dot/collaboration-tasks.md)继续定义分层验收，下表为当前状态。

此前C02/C03/C06已完成对应实现与验证，本轮推进官方接入材料、发布后恢复和剩余真实验收。T09/T12旧截图补证不作为这些独立工作的隐藏总前置；不为补旧字段重复建任务或认证。

| 任务 | 内容 | 状态与输入 |
| --- | --- | --- |
| C01 | 宿主与生命周期契约 | done（有界官方核实）；9篇Help、4篇完整指南及同版本源码已覆盖卡内宿主/入口/身份/路径与生命周期边界。原卡允许未知hook记unknown并停止该分支，不追加未公开hook或C09实际加载作为门槛；独立验收复核通过，见[宿主契约](../../docs/lody4dot/host-contracts.md) |
| C02 | 共享技能与协作知识 | done；0.2.4/0.2.5交付保留。0.2.6已补原配置参考和版本化来源，三个新上下文按目标正确选择复用、待保存及跨机项目处理；见[本轮验证](../../docs/lody4dot/validation.md#role与project知识026候选)。只证明显式技能入口后的知识使用，不代表原生加载或真实配置写入 |
| C03 | doctor上下文、范围与来源 | done；42项诊断测试及真实包内inspect/来源检查通过，setup内容变化可见为mismatch。schema1保留范围、来源和真实失败分类；版本只提示，来源仅证明本地文件一致性 |
| C04 | 平台安装边界 | blocked；Linux与统一边界既有52项证据、Win32/Darwin模拟退出5保留。离线夹具宿主依赖已定向复现，修订planned；真实Darwin/arm64无Node/npm、WSL未提供，不宣布跨平台runtime支持 |
| C05 | 按宿主分发与加载 | blocked（本地ZIP增量done）；0.2.7默认兼容、目标保护及验包通过26构建测试/143全量和真实CLI，来源/移位通过。正式0.2.5不变；独立任务/首次读取、原生UI安装/setup实际调用仍缺，不恢复Cloud CLI/401或重复索权 |
| C06 | 最小交接整理/校验 | done；27项离线行为测试及分发回归通过，输入不改写、无网络/登录/派发；仅结构/声明一致性，真实性/ACL/产物内容未核验 |
| C07 | 两独立宿主协作 | done（有限范围）；Linux控制端与Darwin解包/显式读技能宿主完成原产物交接，Darwin随后通过自身内置MCP只读查询原session/history，准确引用、273字节、SHA及challenge均匹配。新增1个明确只读模型回合，最终persisted/synced/completed且无activeTurns；证据为Agent调用回执与控制端核验，无底层tool trace，见[内置MCP验收](../../docs/lody4dot/validation.md#远端内置mcp只读查询与c07有限双端验收)。不扩为macOS受管安装、原生注册或Dot |
| C08 | 初始化与恢复演练 | partial（受测Codex子范围done）；spec12的不同内核上下文/旧结果恢复保留。spec14另新增1个验收回合：真实follow在running时退出并清理身份，新身份沿同准确turn观察running→持久化completed，新274字节/SHA/challenge匹配、原8历史未变，两身份清理。整个协调脚本未退出；VM/磁盘机制、完全缺失结束通知及Dot lifecycle仍未证实，见[运行中恢复](../../docs/lody4dot/validation.md#运行中观察进程和身份清理后的恢复) |
| C09 | Dot合法接入 | blocked；官方候选路线已知，[Dot接入说明](../../docs/lody4dot/dot-acceptance.md)已提供。native UI上传/扫描、实际安装读取及工具调用仍未通过；共享插件连接不自动赋予CLI身份、本地文件或模型权限 |
| C10 | 含Dot闭环与交付 | blocked；C07有限双端已完成，仍缺C08剩余恢复和C09 Dot参与证据。若扩为跨runtime升级/回退分支，尚缺第二套已复核输入；当前只有一个锁，不为演练擅自换锁或升级CLI。原方案允许的安装入口/接入材料回退保持，不给所有路线追加第二CLI门槛 |

已核实正式0.2.1的准备脚本复用bootstrap，启动指引要求读取技能并检查/修复缺失依赖。当前候选沿用原显式用户setup入口，不冒充平台首次送达、独立任务加载或重置hook。恢复继续采用幂等准备、入口检查、执行中保存和原任务对账；未知Dot hook不是所有路线的总前置。

2026-10-21较早的c1实施轮次，正式规则已有三个OpenAI域名，但当时实例revision5仍只有5条Lody规则，三个官网请求CONNECT403；当时凭证ready且Lody可用。这些是旧轮次观测，不能作为本轮spec9的网络或变量readiness结论。

## 0.2.0发布前的实施记录（2026-10-21较早轮次）

该轮108项全量回归、结构/格式检查及完整新版cloud-install通过。0.2.0包为28内容文件+receipt，真实包内准备、移位和来源一致性通过；[验证记录](../../docs/lody4dot/validation.md#020-多宿主基础能力与无账户验收)列明当时摘要与范围。C02另有全新上下文Agent自主检索的3目标场景，C03/C06保留兼容与真实性边界；这些旧摘要不用于本轮重建中的0.2.1候选。

真实双端验收复用已授权的Codex配置，只新建一个自有隔离会话，三回合分别为下载失败报告、原生ZIP交付/产物生成、只读重开文件。首回合completed不当业务成功，无产物handoff实际blocked/3；后两回合持久化completed且准确引用、输入/273字节结果、包与技能摘要、随机challenge全匹配。最终无activeTurns。Darwin无Node/npm/LodyCLI，CLI与宿主内置Agent分开；因此只交付已证明的云控制、远端读取和工件交接，不关闭C07的第二独立控制查询要求。

真实临时prefix初次缺失修复、第二次仅检查通过；新0700控制身份未复制旧态，显式认证后沿同一原任务对账通过。它们不替代实际云主机重建。两个自有登录目录及演练prefix已清理，全局变量绑定保留；无认证文件的私密原生引用/交接记录在忽略的`dist/lody4dot-0.2.0-evidence/private/`，公开文档只保留脱敏结论。

该轮0.2.0升级草稿保存返回saved/requires_publish=true，首次读取revision15确认install/start逐字一致、源码为代码/包实测基线2cc74de，8条自定义域名沿用。交接时来源同步到最终完整HEAD d27f1a0；代码与包字节保持不变。保存时正式云来源尚为0.1.3、运行实例revision5；本轮已发布0.2.0并进入spec9，见下节，不重复保留“待发布”为当前阻塞。

该轮未决项曾包括Dot正式产品标识、环境发布和生命周期。本轮身份与候选工具路线、0.2.0发布已确认；仍缺的实际加载、独立控制和宿主生命周期证据按上方任务表逐项处理。T09/T12原截图来源补证仍单独保留。

## 本轮发布后恢复与官方资料收口（2026-10-21，spec9）

正式配置读取无草稿，来源为0.2.0/d27f1a0，install/start与该来源相符；spec_revision和observed_spec_revision均为9、observations_current=true。网络和runtime_variables元数据readiness仍unknown，不改写为enforced/ready。实际访问另有证据：官方Help搜索及9篇正文HTTP200，开发站仍在代理处403并停止该域名请求；产品身份与共享连接按[官方核实记录](../../docs/lody4dot/host-contracts.md)更新。

实际`bootstrap --repair-missing`只运行doctor并pass，没有触发安装、认证、daemon或模型任务。另建私密state完成真实认证，沿原0.2.0验收会话准确引用只读查询；持久化source/freshness为persisted/synced，目标回合completed、无activeTurns，原history回执、原产物摘要与恢复的本地结果匹配。发送新模型回合为0，临时auth已清理。脱敏结果保存在忽略的`dist/lody4dot-published-spec9-evidence/summary.json`；本轮没有复制登录态或重新创建原任务。

这证明发布后的当前依赖检查与原任务恢复对账；没有旧boot/实例基线或其他实际重建回执，不能宣布整机/存储重建、独立新任务或首次启动指引送达。T09旧截图不据此补填当时版本，C05/C07/C08/C09的剩余门槛也不由本轮查询自动关闭。

后续按[Dot接入与独立控制端验收](../../docs/lody4dot/dot-acceptance.md)使用已证实路线：有权限的UI候选导入/扫描和真实技能读取、已有合法连接或委托已准备云环境、具备本端身份的独立控制复验。候选OS仍需实际Node/native前提，Dot自有环境准备/maintenance/reset hooks另行核实。未知hook不阻塞已支持的云控制路线；本轮不为0.2.1知识修订重配token或要求重复发布。

## V01 CLI版本提示策略（本轮新增，done）

用户最新要求优先于旧版严格验证：Lody CLI版本差异、探测失败均只warn；安装、诊断和认证继续按实际命令结果执行。0.107.2只代表知识/默认安装输入基线，旧收据版本不再用于执行准入。显式`doctor --check-updates`对固定npm地址做一次最多5秒查询，非最新版/不可比较/查询失败只提醒；默认inspect/bootstrap离线，不自动升级，实际权限和命令失败保留原退出码。

127项全量回归和结构检查通过，包含41项诊断、4项版本策略、21项安装及8项生命周期行为测试；bootstrap文本也展示warn。真实npm查询本轮actual/latest同为0.107.2，账户not_run。最终包29内容文件+receipt，包内安装reused=true、启动仅doctor通过；ZIP完整性与逐文件摘要通过。最终ZIP及receipt摘要见[0.2.1验证记录](../../docs/lody4dot/validation.md#dot官方契约指引与021候选)，不再使用追加版本策略前的内部候选摘要。没有为版本检查创建业务任务、登录或升级CLI。

## C07内置MCP补证（V01完成后的独立验收阶段）

公开0.107.2源码确认会话可由宿主注入MCP，并不依赖Agent shell的PATH；于是复用既有Darwin Agent和自有原会话，只发送一次明确的只读验证目标，没有重发原产物业务。远端回执报告实际暴露36个Lody工具，只调用status_many/history两只读工具，参数唯一指向原session/URI，状态1项与历史8项、无后页；原两回合引用、273字节、SHA与challenge经控制端及另一只读审查上下文重算均匹配。Darwin Lody实际版本未知，不追加版本硬门槛。

新只读回合最终persisted/synced/completed、无activeTurns；本次新增模型回合为1，与此前发布后恢复阶段0新回合分别记录。新私密认证目录已清理，未新增会话/配置/Role/服务。脱敏结果在忽略的`dist/lody4dot-0.2.1-evidence/native-mcp-summary.json`；公开只记范围与匹配结论，不存实际引用或产物字节。

C07按卡中允许“执行节点属于其中一端”的范围完成：Linux CLI控制＋Darwin技能读取/原执行与随后内置MCP只读复验。证据仍是远端Agent结构化回执，无底层MCP tool trace，不扩为受管macOS安装或Dot。C05独立首次加载、C08真实宿主重建、C09/C10仍blocked；候选包和代码字节未改，本次只更新记录。

## spec11发布复查与文档归档

用户再次发布后，正式配置仍固定d27f1a0/0.2.0；运行spec/observed11、current=true，网络/变量readiness仍unknown。实际checkout保留0.2.1代码，完整`.codex/cloud-install.sh`退出0，127项测试和bootstrap prepare中的install/doctor通过，认证/daemon/业务恢复not_run。当前内核启动时间为2026-10-21T07:51:35Z，晚于旧spec9观测，旧/tmp缓存消失而dist证据保留；这些仅记录环境变化，未闭合真实VM/存储重建证明。

重新核实本机Codex CLI正式支持cloud exec；最小只读cloud list确实发往chatgpt.com，但请求失败，公开HTTPS进一步证实CONNECT403。没有提交新云任务、猜环境ID或更换认证。升级准备需在保留原8条自定义规则与已有变量的基础上追加chatgpt.com、learn.chatgpt.com，按实际HEAD保存新源码及已验证install/start；草稿不等于正式发布，最终状态依配置回执。

按用户要求将14篇专属文档及9份图资源归入docs/lody4dot/，去掉冗余文件名前缀并新增README索引；内部与仓库入口链接同步更新，图源/SVG/配置/渲染脚本字节保持不变。AGENTS及docs/architecture.md固化项目文档按文件夹归档、配图归属、运行技能资源例外及移动更新引用的开发规范。

升级草稿保存实际返回saved/requires_publish=true，读取revision18确认源码为本轮0.2.1验收及文档整理基线、mount保持mymcp-4-codexcloud，install/start与仓库文件逐字一致，原8条自定义规则保留且只追加chatgpt.com、learn.chatgpt.com；未改已有变量/凭证绑定。最终交接仅同步包含本记录的完整HEAD，具体固定SHA以配置回执为准，已测工具与候选包字节不变。这里是新源码/新目的地的升级草稿，不将此前发布旧固定ref当成该升级已生效；无需重配token。

## spec12正式生效与0.2.2 setup候选（本轮）

用户确认发布后，实际正式来源为ed9096b/0.2.1，spec/observed12且观测当前，无草稿；readiness仍unknown。开始编辑前0.2.1启动检查通过，随后实现0.2.2候选。原升级不再待发布，不重新添加token或保存相同配置。四篇官方开发/管理/Dot资料HTTP200，onboardingSkill、兼容清单与source规则已核实；Dot电脑可跨使用间隔保状态，但没有永久或周期reset承诺。

C08有限恢复范围取得新证据：本次内核启动08:55:43Z，晚于spec11真实观测08:01:10Z且boot摘要不同；旧证据和同锁runtime可读。对账时工作副本已开发未提交0.2.2，bootstrap仅doctor通过，不冒称纯正式源码安装或install reused。新0700私密身份单次认证，原session/turn与8条history、273字节、SHA/challenge全部匹配，persisted/synced/completed且无activeTurns，0新模型回合、auth已清理。摘要在忽略的dist/lody4dot-environment-checks/spec12/；准确VM/磁盘重建机制、Dot lifecycle、独立首次加载仍未证实。

0.2.2候选增加官方用户run setup入口，唯一薄技能复用核心与bootstrap，清单目标、打包收集及receipt允许范围同步。132项全量回归和结构检查通过；15项构建、42项诊断覆盖新增入口资源/路径拒绝、旧输出保留及内容修改可见。独立审查指出的额外setup资源契约不一致已修复。最终ZIP31文件、110840字节，CRC/逐文件摘要通过，移位包bootstrap仅doctor与来源consistent；旧0.2.1包未改。完整摘要见[验证记录](../../docs/lody4dot/validation.md#spec12正式发布与022用户setup候选)。

剩余可恢复条件：C05 Cloud CLI虽有创建入口，cloud list现HTTP401；本地ChatGPT登录不等于该API授权，具体原因未知，缺服务核实的Cloud ENV_ID，未提交任务。C05/C09原生UI安装及新/既有对话run setup无可调用界面，保持未验；不伪造hook/身份或重复派发。C10等待Dot真实参与及剩余恢复证据，T09/T12旧截图在原任务补来源。没有把未知hook作为所有路线的前置，也没有将同实例子Agent当新宿主。本轮文档继续按项目目录归档。

## spec14状态与运行中恢复（本轮）

本次发布已应用为spec/observed14、current=true，网络enforced、既有变量ready；正式仍固定ed9096b/0.2.1，无草稿。工作副本开始时1d4ee0c/0.2.2且干净，bootstrap仅doctor通过。唯一一次Cloud list仍HTTP401，无403，未提交云任务/猜ENV_ID，没有重复保存环境草稿或重配token。

C01按原卡和独立复核收口done：官方9+4资料、同版本清单/加载源码及规定CLI已覆盖有界契约核实。未知Dot自有直接CLI/存储hook按原卡保留unknown并停止该实现分支；实际UI安装/加载/调用归C05/C09，未取得未公开hook不再作为C01永久阻塞。源码resolve_openai_onboarding_skill确认字段支持，但当前CLI无独立setup/validate/dry-run，未用plugin list或注册冒称实际setup调用。

C08本轮新增一次受控chat：原session空闲/无activeTurns及8条历史核对后，私密落盘意图、保存ACK userTurnId。真实follow收到准确assistant的running快照/ready，再SIGTERM并等退出0，清理A身份；独立B身份恢复同准确turn，前4次仍running，第5次persisted/synced/completed、无activeTurns。原8历史完全不变，总10条；新274字节、SHA及challenge重算匹配，两个认证state已清理。没有自动重发、cancel或daemon。整个协调脚本未退出，不称主机重启；未显式查询queue数量，不补造queue=0。独立审查确认所有这些本地证据，详见[运行中恢复记录](../../docs/lody4dot/validation.md#运行中观察进程和身份清理后的恢复)。

该实验只交付观察进程/本地身份丢失后的恢复子范围。准确VM/磁盘机制、完全缺失结束通知、Dot生命周期和独立首次加载仍未证实；各自保留，不重复模型实验替代UI/API授权。初始metadata/CLI只读探针的0新回合与这次新增1回合分开记录。私密证据在忽略的dist/lody4dot-environment-checks/spec14/，公开不存引用、nonce、产物原文或身份文件。

同时使用既有唯一队列职责收拢环境ref/spec/readiness：当前只在本文件开头维护，README、指引、平台/宿主/接入/支持文档改为链接；旧轮次观测明确标为历史。0.2.2源码/包字节和CLI锁未改，运行记录按docs/lody4dot/归档。下一步条件见开头快照，当前Cloud API 401及原生UI缺口不能靠再发布同一配置消除。

## 用户确认Dot任务创建权限与路由修正

2026-10-21，用户明确当前云任务不能创建另一个独立Codex云任务，需由Dot发起，并补充Dot具备该权限。此确认优先于此前从CLI命令存在推导出的备选验收路径：当前云任务停止查询OpenAI任务目录，不尝试cloud exec，不把HTTP401、缺Cloud ENV_ID或等待OpenAI API授权列为插件前置/项目阻塞。原请求结果保留为历史，不改成成功，也不借此推断Dot无权限。

任务路由统一为Dot→已发布环境与仓库→独立云任务加载lody4dot→经Lody协作已有节点→必要引用与成果回Dot。需要补的是Dot实际发起、任务与环境关联及首次读取回执；Dot创建权限已确认，不再重复索取授权。获授权的Lody session/turn派发仍属于Lody服务动作，与Codex平台任务创建分开。当前工具未暴露Dot任务创建入口，仅记录本端工具范围，不声称Dot缺权限。

AGENTS保留短指引，详细边界与交接步骤落在环境指引、设计参考、主方案、C05/C09及新任务验收中。没有新建任务、调用Cloud/OpenAI目录、修改环境、凭证或候选包字节。

## c3审查与0.2.3资料知识实施

2026-10-21，先确认工作区干净并ff-only拉取origin/main，已包含`a4e272c`且完整读取其commit message。结合指定文档、现有工具和27项交接测试审查：Lody状态所有权、typed refs和恢复对账已足够；新增需求应补到Agent实际加载的知识入口，不扩schema1或重建服务。两份独立初审与完整差异复审未发现需改业务代码的实质缺陷。

在用户已明确授权的实施范围内完成0.2.3资料参考、核心/协作/交付导航、Dot宿主材料与版本更新；原位完善c3实现对照、C02卡片及交接契约适用说明，保持资料记录卡唯一。132项Linux回归、结构、自包含32文件ZIP、逐文件/收据/CRC和移位离线bootstrap通过；三个独立上下文从技能入口自主导航，分别正确处理原字节缺口、保存后回读403及固定原生路线。完整结果及边界见[本轮验证](../../docs/lody4dot/validation.md#c3资料交接知识与023候选)。

本轮没有改运行时代码/锁、增加契约/服务/权限、修改云配置或发起业务请求；不把模型知识演练当Dot原生工具证据，不重验已试通中转。C02知识增量已验证，C05候选已打包；剩余实际加载、恢复及C09/C10门槛不改为done。0.2.2和0.2.1旧包不变，macOS既有失败保留原记录；候选未宣称正式发布。

## dc8cd70交接与0.2.4 Work知识实施

2026-10-21，从干净main `2d8dd52`快进拉取到`dc8cd70`，按要求执行`git show -s --format=%B dc8cd70`并完整读取说明、指定文档、既有实现/契约/测试。本地Work产品补充可直接用于宿主选择；0.2.3资料/交接能力足够复用。独立审查未发现需改代码契约的缺陷，本轮选择在原协作参考集中补Work类型、创建/触发证据，核心/资料/兼容性及两份setup只补入口和适用条件。

0.2.4已通过132项Linux回归、结构检查、32文件ZIP逐文件/收据/CRC和移位离线doctor。三类新上下文演练覆盖Work资料条件、业务MCP无创建入口及计划保存未运行；创建场景初稿提出Codex备选，随后明确保留用户指定任务类型，并在最终包的新上下文中定向复验通过。不是三产品宿主或真实Work运行；详细范围与摘要见[本轮验证](../../docs/lody4dot/validation.md#work宿主与任务入口知识024候选)。

当前工具目录未见本地文档中的首方创建入口，本轮没有Work/Cloud平台任务、Lody业务、资料保存或连接写入，没有重验Dot中转或查询OpenAI任务目录。schema1、运行代码/锁、runtime支持、正式配置和原验收缺口保持；0.2.3/0.2.2/0.2.1旧ZIP不变，候选生成物继续忽略。C02知识增量完成，C05/C08/C09/C10的实际门槛和T09/T12旧任务补证不由本轮演练代结论。

## cb5cee6交接与0.2.5薄知识修订

2026-10-21，当前main在cb5cee6且干净，再次ff-only拉取确认最新并完整读取该message、交接、创建对照、c3及实现/契约/测试。两份独立对照确认0.2.4现有流程足够；仅在原协作参考补Codex手动/Dot/CLI平台入口、当前访问证据和项目分工。复审发现初稿会把本项目固定禁令带给其他宿主，已改为接收项目的条件式约定，并明确不限制合法Lody原生控制；未复制核心导航、setup、资料流程或创建工具。

最终0.2.5的132项Linux回归、结构、32文件ZIP/收据/CRC及移位离线doctor通过；本项目Dot约束、其他项目明确授权两类新上下文均正确应用项目条件，见[验证记录](../../docs/lody4dot/validation.md#平台入口与项目职责知识025候选)。0.2.4原ZIP与全部历史记录保留，更早0.2.3/0.2.2/0.2.1 ZIP也未变。

本轮未运行Codex Cloud CLI/任务目录、恢复401调查、重验Dot、创建平台任务或写入资料，没有新服务/契约/权限/部署；正式元数据和工具目录未刷新。知识演练不是独立产品宿主或真实业务，C05/C08/C09/C10及T09/T12保持原证据门槛，企业聊天委派继续排除。

## spec16发布复查与0.2.5来源修正

2026-10-21，用户确认发布后实际spec/observed16、current=true；正式配置仍为ed9096b/0.2.1，起初无草稿。当前984dad4/0.2.5已推送且干净。两份已保存脚本与旧正式及当前源码逐字相同，差异是仓库固定ref，不是缺变量或新安装逻辑；本轮不重新认证、对账或发模型任务。

按已授权setup范围完成全/workspace发现和准备后复查：仅1个实际项目，精确HEAD及mount已核实；空的受保护/workspace/.git目录不是Git仓库，runtime内部链接的真实目标已遍历，缓存不列为项目。完整cloud-install的132测试和install/doctor、启动repair-missing仅doctor均通过；未改代码/锁、网络或凭证。

仓库源修正草稿已saved且requires_publish，回读确认仅repo ref改变，其他配置一致。以984dad4为软件基线，收尾固定到含本记录的实际提交并回读，避免新任务缺本轮进度；精确目标见交付提交及草稿。详见[本轮验证](../../docs/lody4dot/validation.md#spec16发布复查与来源修正)。这是来源变更，不是重复保存相同配置；产品发布仍待环境设置操作，独立任务首次加载、Dot实际调用和C09/C10不据此关闭。

## spec17来源升级生效与启动复查

2026-10-21，用户再次发布后，正式固定0a044f1/0.2.5、无草稿，spec/observed17且current=true，网络enforced、两变量ready。当前checkout起始同正式ref且干净，拉取无更新；install/start与对应仓库文件一致。0.2.5来源升级待发布子门槛已关闭，本轮纯记录提交不要求正式环境跟随每次文档更新，未保存或要求新草稿。

按现有会话上下文定位并实际读取cloud-start、核心技能及云端准备参考；未据此填写首次自动注入。启动repair-missing仅doctor通过，插件0.2.5、CLI0.107.2、runtime锁consistent，未运行安装或填写reused，认证/daemon/任务恢复not_run。原132回归及完整prepare保留spec16已测范围，不重跑业务或模型实验。详见[本轮验证](../../docs/lody4dot/validation.md#spec17来源升级生效与启动复查)。

当前目录仍无Dot创建/UI入口；已关闭的是正式来源升级，C05独立首次读取、C08剩余恢复、C09/C10与T09/T12旧任务补证仍按实际门槛保留。发布和内核上下文变化不替代Dot实际发起、原生setup、工具调用或具体存储重建证据。

## 剩余工作复核

2026-10-21用户询问还能推进哪些工作。两份独立只读复核确认：安装器和既有资料/协作工具足够，无需新增实现。可直接补的知识缺口是把已核实的多Role复用配置、Project上下文边界和提议路由条件带入原configuration参考；本轮只定位，尚未修改技能或形成新候选。实际多Role保存、项目登记和按Role执行仍需对应工具、配置写入范围及用户保存，不从普通远端派发授权推导。

已移除静态任务卡的旧正式0.2.1副本，并区分C10的接入材料回退与可选跨runtime分支；仅后者需要两套真实输入，不新增所有路线的CLI门槛。当前安装只有b1baf3ab…一套锁，0.2.1至0.2.5共用它；不以复制依赖、改锁空白或同锁激活失败演练冒充跨runtime升级。没有新增任务状态、改源码/锁、业务写入或环境草稿，正式0.2.5仍可用于既定Dot验收。详见[复核记录](../../docs/lody4dot/validation.md#剩余工作与执行前提复核)。

## Role与Project知识0.2.6实施

2026-10-21用户明确按建议推进。从干净a9852a2拉取无更新，复用已核实官方0.107.2发布物，两个独立上下文复核源码及实际改动。在原configuration参考补多Role复用、角色提议的身份机器/会话工具前提、create/update字段与Project组合；来源JSON新增静态核实记录。核心导航、命令索引、Python工具、schema1、依赖锁和云脚本均不变，不创建新的组织层。

0.2.6的132项Linux回归、结构、32文件ZIP逐文件/收据/CRC及移位离线doctor通过；31个内容文件，bundle/runtime来源consistent。三个同一执行环境的新上下文从最终包技能入口自主阅读，分别正确处理双Role复用及提议路由、卡片未保存与model/mode限制、Role覆盖与跨机项目；它们不是独立产品宿主或真实业务调用。详见[本轮验证](../../docs/lody4dot/validation.md#role与project知识026候选)。

0.2.5及更早四份ZIP原摘要不变。正式ref仍0a044f1/0.2.5，无草稿；最新spec21/readiness unknown只按元数据记录，不重配凭证或扩大网络。本轮没有Role/Project写入、Lody业务/模型回合、Dot资料重验、Cloud任务目录或下游创建；C05/C08/C09/C10、真实跨平台及旧T09/T12保持原证据门槛。

## 非Dot优先项一：离线ZIP命令0.2.7

2026-10-21用户要求按优先级持续执行。原位记录BOUNDARY_NOTE，在唯一源码builder增加显式`--zip PATH`，默认目录/JSON/退出行为保留。ZIP只创建新路径，原收据及所有文件校验后才发布，既有目标/重叠/发布竞争保护到位；不承诺目录与ZIP共同原子提交。候选0.2.7不带入builder代码或新增依赖，旧随包工具/知识/CLI锁沿用。

先由独立上下文补RED，随后实现并通过26构建用例、143整仓测试和真实CLI验包/拒绝重复路径。复审发现epoch时间戳异常，新增RED并通过`strict_timestamps=False`修正；最终复审通过。移位包仅doctor且bundle/runtime consistent，0安装/认证/daemon/业务恢复。原0.2.6及更早五份ZIP摘要不变。详见[ZIP验证](../../docs/lody4dot/validation.md#离线zip命令与027候选)。

第二优先项仅完成定向定位：自有临时路径别名触发真实祖先/私密state检查，部分Linux语义测试在模拟Darwin下提前返回unsupported。下一提交只修测试夹具，不改生产平台支持，不把条件模拟当真实Darwin/WSL验收。正式0.2.5与云配置保持，未调用Cloud目录或创建下游任务。
