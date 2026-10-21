# lody4dot 任务队列

权威：[上位方案r2](../../docs/lody4dot-plan.md)；契约：[开发方案d1](../../docs/lody4dot-development.md)与[多宿主方案c2](../../docs/lody4dot-collaboration-development.md)。本文件是唯一进度和执行证据入口。

当前授权：2026-10-20用户明确选择在本对话持续执行r2/d1；2026-10-21确认环境发布，并授权继续推进多宿主方案和任务卡、尽量自主完成。本轮据官方资料将方案修订为c2。未创建后台Goal。`planned`表示尚未满足全部执行前提；可独立进行的准备继续，真实验收不以模拟结果替代。

| ID | 结果 | 依赖 | 状态 | 执行证据 |
| --- | --- | --- | --- | --- |
| [T01](../../docs/lody4dot-development.md#t01冻结加载方式和平台契约) | 加载与平台契约 | 无 | done | [平台契约](../../docs/lody4dot-platform-contract.md)：同版本官方清单与技能路径已核实；采用云环境接入并交付原生产物，T09另验加载 |
| [T02](../../docs/lody4dot-development.md#t02验证固定版本运行时并生成锁定输入) | 固定版本与锁定输入 | T01 | done | [运行时记录](../../docs/lody4dot-validation.md)：锁定0.107.2和Tinypool2.1.2；冻结安装、native及原始worker通过，audit 0 |
| [T03](../../docs/lody4dot-development.md#t03实现技能来源与命令覆盖) | 技能、来源、命令覆盖 | T02 | done | [知识检查](../../docs/lody4dot-validation.md)：20类/70路径及帮助哈希匹配，未冒称业务已实测 |
| [T04](../../docs/lody4dot-development.md#t04实现可重复且失败可恢复的安装器) | 重复安装与失败恢复 | T02 | done | [安装器验证](../../docs/lody4dot-validation.md)：14项行为测试及真实安装/同锁复用通过 |
| [T05](../../docs/lody4dot-development.md#t05实现唯一只读-doctor) | 只读诊断 | T02 | done | [诊断与认证验证](../../docs/lody4dot-validation.md)：离线inspect、真实账户与完整workspace目录通过；窄兼容Streams诊断，doctor不推导任务成功，真实任务另见T10 |
| [T06](../../docs/lody4dot-development.md#t06实现显式认证适配) | 显式认证适配 | T05 | done | [诊断与认证验证](../../docs/lody4dot-validation.md)：显式模式、私密state、假凭证不回显通过；真实login/verify-only已通过，不误报机器注册 |
| [T07](../../docs/lody4dot-development.md#t07实现自包含构建与云环境接入) | 自包含包与云接入 | T03、T04、T05、T06 | done | [分发与云配置](../../docs/lody4dot-validation.md)：22文件移位安装通过；草稿保存已确认，用户随后确认已发布；实际加载未验 |
| [T08](../../docs/lody4dot-development.md#t08完成无账户集成与分发回归) | 无账户集成验证 | T07 | done | [无账户验收](../../docs/lody4dot-validation.md)：48项条目测试加8项原仓库测试通过，移位CLI安装及inspect通过 |
| [T09](../../docs/lody4dot-development.md#t09完成干净云任务加载安装和真实发现) | 真实云端加载、安装、发现 | T08；宿主、身份、网络、工作区 | blocked | [旧截图回执](../../docs/lody4dot-validation.md#用户截图回执与加载判定)报告安装/认证/目录及手动读取通过；该任务首次入口来源、实际源码/插件版本、参考及同锁记录待补。旧正式基线为0.1.3，不能以本轮0.2.0发布后恢复替补当时事实；在原任务补已有记录，不要求重建或重复认证。全文自动注入及原生注册均非该路线必选门槛 |
| [T10](../../docs/lody4dot-development.md#t10验证-agent-任务能力与受控执行闭环) | agent 场景与真实任务 | T09已验证的发现；测试目标、执行凭证 | done | [远端验收](../../docs/lody4dot-validation.md)：已有远端Codex create/chat两个回合completed，Agent二次读回字节及challenge校验匹配；另一个自有运行回合精确取消后为persisted/synced/canceled，无activeTurns；不冒称直接FS读取或工具进程终止 |
| [T11](../../docs/lody4dot-development.md#t11补齐高级能力的场景与平台边界) | 高级场景与支持矩阵 | T10 | done | [支持矩阵](../../docs/lody4dot-support-matrix.md)覆盖20根/70路径，列明高级只读实测、Review上游artifact失败、条件支持及未运行项；完成的是支持边界与场景覆盖，不冒称全部高级业务已运行 |
| [T12](../../docs/lody4dot-development.md#t12交付复现与支持范围确认) | 复现与交付 | T10、T11 | blocked | 分发、远端基本闭环和支持边界已复核；待T09截图对应任务补来源、版本等缺项，不标整体交付完成 |

既有r2/d1尚缺旧截图对应任务的来源和版本等记录，按[验收流程](../../docs/lody4dot-fresh-task-acceptance.md)核对后继续T12；不为补旧字段重新创建任务、登录或查询资源。自主检索后实际读取可以证明基本读取，首次入口来源仍须如实区分。T10远端闭环与T11支持矩阵已完成，不把T09旧补证设为c2独立工作的隐藏总前置。个人workspace及已有Agent测试授权保留；本机只读限制不阻塞获准远端控制。

当前源码及候选包为0.2.1，补充Dot官方知识、接入材料及非阻塞CLI版本提示；最终包已重建并通过127项回归，摘要见验证记录。0.107.2保留为既有实测/默认安装输入基线，版本差异不作为执行准入，详见V01。正式云来源已发布为0.2.0、完整ref为`d27f1a0e6ec2890cd60e301118fc925d32872d46`，无待发布草稿。当前spec/observed9、observations_current=true，网络/runtime_variables元数据readiness仍unknown；实际HTTP与Lody认证结果单独记录。本轮未改正式配置，新提示策略对执行0.2.1脚本的端生效，现有云控制端可继续验收；未来任务使用新版须选择对应源码。

环境、任务、实例、Dot会话引用及协作空间/Lody权限分别识别，见[环境模型](../../docs/lody4dot-environment-model.md)。不承诺某客户端或网页必然能选到此环境；“本机ACP”指当前云执行实例，不是用户电脑。

拟议任务先登记为 `planned`；开始执行后的状态为 `in_progress / blocked / done`。blocked 需注明具体前提及仍可推进的独立项；done 必须链接实际结果与未运行项。任务完成不等于整体发布完成，能力缺口不得被结构检查或 fixture 通过掩盖。

## r2/d1历史执行记录（2026-10-20至2026-10-21较早轮次）

以下历史段落的“当前”“本次”“仍”仅指各自轮次。较早正式版本、readiness、未运行项及草稿记录按当时事实保留；最新状态见开头概述、C任务表及文末spec9记录。

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

[运行前提补充](../../docs/lody4dot-runtime-findings.md) 记录了适配器版本、managed0.160.1的受管入口、无模型初始化失败与官方状态目录边界，以及原生host会覆盖API-key可见的全部工作区。没有越过用户的个人工作区范围启动host。临时项目及验收断言已备妥，实际目录、观察和任务闭环仍待条件满足。

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

当前宿主工具没有新建/附着独立云任务的入口；子agent或同实例发布不冒充新任务加载。最小外部回执流程已写[新任务验收](../../docs/lody4dot-fresh-task-acceptance.md)。没有重存已发布配置或要求用户重新添加token；本轮只更新仓库中的验收文档。

T11按开发契约完成支持范围和场景覆盖：20根/70路径数量、来源、实测和条件边界已逐项核对，独立复核通过。Review保留明确上游阻塞，取消等未运行项不改成通过。整体交付仍由T12受T09新任务实证约束。

### 运行中精确取消补测

2026-10-20，当前会话继续使用已获授权的远端Codex配置和本任务自建验收会话。唯一匹配、空闲及空队列检查通过后只发一次受控chat；观察到本次userTurnId对应的唯一running assistantTurnId，再用--turn-id精确取消。原生响应success=true且不是alreadyStopped；最终同一user/assistant回合persisted/synced/canceled、activeTurns为空。详见[验证记录](../../docs/lody4dot-validation.md#运行回合的精确取消验收)，支持矩阵已更新。

取消闭环仅指Lody回合，不推导远端工具进程启动或即时终止。新建私密认证state已清理，没有改动其他用户会话、远端配置或已发布云配置。T09仍缺独立新云任务回执，T12仍blocked；本轮文档证据不改变0.1.3发布物。

### 会话维护与0.1.4知识修正

2026-10-21，用户要求持续推进能完成的部分。仅对本任务自有会话，以完整含归档元数据确认无后代、空闲/空队列后，完成rename往返、archive、restore；原标题与未归档状态还原，child IDs均为空，6条可见历史及latestTurn保持一致，最终persisted/synced、无activeTurns。未新增模型回合或配置，未向其他会话发起维护命令；认证state已清理。

独立源码复核修正归档递归范围、restore直接parent子项及资源释放的不对称，补入取消陈旧请求可能ACK成功和Operation inbox后继的边界。技能、索引、来源与分发说明同步为0.1.4；56项回归、结构、自包含构建、包内同锁安装/inspect及ZIP完整性通过，旧0.1.3产物保留，详见[验证记录](../../docs/lody4dot-validation.md#会话维护往返与知识修正)。已发布环境未改，T09/T12仍blocked，Review及本机ACP限制继续保留。

### 用户提供验收截图后的判定

2026-10-21，用户回传验收截图：报告Lody0.107.2安装检查、注入凭证认证及两个工作区的完整机器目录查询通过，技能和启动指引手动找到读取、未观察到自动加载；私密登录态已清理，无daemon或模型任务。这是用户提供的结果摘要，不冒称本会话执行日志；不复制工作区名称或业务数据入库。

原方案要求新任务实际读取入口、定位参考与诊断工具，没有要求技能全文自动注入。截图中的“手动”尚不能区分agent自行检索和用户给路径，也未列初始指引来源、源码SHA、插件版本、随附参考及重复安装记录；因此不判自动加载失败，也不提前关闭T09/T12。已只读核实正式ref仍a2e6796、start_skill完整、无草稿。最小下一步是在截图对应的原任务补这些已有记录；不重新建任务、不重复登录/查询、不重存配置。

### 环境与权限指引

2026-10-21，按用户要求将Dot、会话、云任务、发布版本、执行实例、本地环境及协作空间/Lody权限沉淀为[指引](../../docs/lody4dot-environment-model.md)。包含概念表、引用与权限表、状态保留范围、当前事实映射、交接场景、建议的关联记录与架构评审清单。

配套三张Mermaid图及SVG分别展示执行关系、发布/加载证据阶段和权限条件；保留源码、替代文字和渲染说明。正文标明事实、用户回执、建议与未知，不推测客户端入口或任务/实例一对一关系。该文档交付不等于T09/T12已通过，也不更新环境或0.1.4安装包。

指引经辩证评审后按“一分钟速查→实际链路→三个空间→按问题查表”重排，技术记录移至[设计参考](../../docs/lody4dot-environment-design.md)。分别识别Agent决策与工具位置、发布配置与安装快照，并改为通过已授权的必要请求核实未知访问权限；三张图同步。既有验证范围和T09/T12缺口保持按原证据记录。

## 多宿主协作与初始化方案

2026-10-21较早的c1阶段形成了多宿主安装、Lody协作与初始化方案。本轮9篇官方Help确认Dot是ChatGPT中的always-on agent产品，有自己的云电脑，也能委托Codex任务或连接另行授权的本地电脑；Dot与Agent类别不互斥。方案已修订为[c2](../../docs/lody4dot-collaboration-development.md)，[C01–C10卡片](../../docs/lody4dot-collaboration-tasks.md)继续定义分层验收；下表为当前状态。

此前C02/C03/C06已完成对应实现与验证，本轮推进官方接入材料、发布后恢复和剩余真实验收。T09/T12旧截图补证不作为这些独立工作的隐藏总前置；不为补旧字段重复建任务或认证。

| 任务 | 内容 | 状态与输入 |
| --- | --- | --- |
| C01 | 宿主与生命周期契约 | blocked（部分完成）；[宿主契约](../../docs/lody4dot-host-contracts.md)已核实9篇官方Help、Dot身份/共享连接/委托路线及既有Codex契约；Help正文200，开发站仍403。剩Dot自有环境生命周期hooks与实际集成证据，不再以产品身份未知阻塞已支持路线 |
| C02 | 共享技能与协作知识 | done；既有共享协作导航及全新上下文3目标场景通过；0.2.1候选按官方资料更正Dot分类与共享权限说明。知识实现不证明Dot实际UI加载或工具调用 |
| C03 | doctor上下文、范围与来源 | done；本轮41项诊断测试及真实离线inspect/显式latest查询通过；schema1保留早期checks、后续not_run、范围/来源和代理拒绝分层，来源仅证明本地文件一致性；版本提示见V01 |
| C04 | 平台安装边界 | blocked；Linux与统一边界通过52项相关测试，Win32/Darwin模拟退出5；真实Darwin/arm64报告无Node/npm，native安装前提缺失，WSL未提供，不宣布跨平台runtime支持 |
| C05 | 按宿主分发与加载 | blocked；0.2.0包/移位及Darwin显式读取已有回执，正式0.2.0现已发布；0.2.1的29内容文件候选包、ZIP完整性、包内安装复用/启动检查均通过。首次独立任务入口送达/读取仍未验；原生注册单列未验，不作为云接入路线额外门槛 |
| C06 | 最小交接整理/校验 | done；27项离线行为测试及分发回归通过，输入不改写、无网络/登录/派发；仅结构/声明一致性，真实性/ACL/产物内容未核验 |
| C07 | 两独立宿主协作 | blocked；既有[真实交接](../../docs/lody4dot-validation.md#020-linux云端与darwin-agent的实际交接)及本轮新私密state沿原引用/回执/摘要只读对账通过，0新模型回合；第二独立控制端自身查询仍未运行，按[独立控制端验收](../../docs/lody4dot-dot-acceptance.md)继续 |
| C08 | 初始化与恢复演练 | blocked；上轮临时prefix恢复与7项测试已测；本轮bootstrap仅doctor pass、新私密身份认证及原会话对账通过。无旧实例基线或其他实际重建回执，首次独立启动仍未验；未知Dot hook不阻塞这些已完成子范围 |
| C09 | Dot合法接入 | blocked；官方候选路线已知，[Dot接入说明](../../docs/lody4dot-dot-acceptance.md)已提供。native UI上传/扫描、实际安装读取及工具调用仍未通过；共享插件连接不自动赋予CLI身份、本地文件或模型权限 |
| C10 | 含Dot闭环与交付 | blocked；依赖C07/C08/C09真实证据，先交付有证据的0.2.0子范围 |

已发布0.2.0的准备脚本复用bootstrap准备入口，启动指引要求读取技能并检查/修复缺失依赖；本轮按该入口实际执行只运行doctor并通过。它不证明平台首次送达或独立任务已加载。恢复路线继续采用幂等准备、入口检查、执行中保存和原任务对账，未知Dot自身存储hook不是所有接入路线的总前置。

2026-10-21较早的c1实施轮次，正式规则已有三个OpenAI域名，但当时实例revision5仍只有5条Lody规则，三个官网请求CONNECT403；当时凭证ready且Lody可用。这些是旧轮次观测，不能作为本轮spec9的网络或变量readiness结论。

## 0.2.0发布前的实施记录（2026-10-21较早轮次）

该轮108项全量回归、结构/格式检查及完整新版cloud-install通过。0.2.0包为28内容文件+receipt，真实包内准备、移位和来源一致性通过；[验证记录](../../docs/lody4dot-validation.md#020-多宿主基础能力与无账户验收)列明当时摘要与范围。C02另有全新上下文Agent自主检索的3目标场景，C03/C06保留兼容与真实性边界；这些旧摘要不用于本轮重建中的0.2.1候选。

真实双端验收复用已授权的Codex配置，只新建一个自有隔离会话，三回合分别为下载失败报告、原生ZIP交付/产物生成、只读重开文件。首回合completed不当业务成功，无产物handoff实际blocked/3；后两回合持久化completed且准确引用、输入/273字节结果、包与技能摘要、随机challenge全匹配。最终无activeTurns。Darwin无Node/npm/LodyCLI，CLI与宿主内置Agent分开；因此只交付已证明的云控制、远端读取和工件交接，不关闭C07的第二独立控制查询要求。

真实临时prefix初次缺失修复、第二次仅检查通过；新0700控制身份未复制旧态，显式认证后沿同一原任务对账通过。它们不替代实际云主机重建。两个自有登录目录及演练prefix已清理，全局变量绑定保留；无认证文件的私密原生引用/交接记录在忽略的`dist/lody4dot-0.2.0-evidence/private/`，公开文档只保留脱敏结论。

该轮0.2.0升级草稿保存返回saved/requires_publish=true，首次读取revision15确认install/start逐字一致、源码为代码/包实测基线2cc74de，8条自定义域名沿用。交接时来源同步到最终完整HEAD d27f1a0；代码与包字节保持不变。保存时正式云来源尚为0.1.3、运行实例revision5；本轮已发布0.2.0并进入spec9，见下节，不重复保留“待发布”为当前阻塞。

该轮未决项曾包括Dot正式产品标识、环境发布和生命周期。本轮身份与候选工具路线、0.2.0发布已确认；仍缺的实际加载、独立控制和宿主生命周期证据按上方任务表逐项处理。T09/T12原截图来源补证仍单独保留。

## 本轮发布后恢复与官方资料收口（2026-10-21，spec9）

正式配置读取无草稿，来源为0.2.0/d27f1a0，install/start与该来源相符；spec_revision和observed_spec_revision均为9、observations_current=true。网络和runtime_variables元数据readiness仍unknown，不改写为enforced/ready。实际访问另有证据：官方Help搜索及9篇正文HTTP200，开发站仍在代理处403并停止该域名请求；产品身份与共享连接按[官方核实记录](../../docs/lody4dot-host-contracts.md)更新。

实际`bootstrap --repair-missing`只运行doctor并pass，没有触发安装、认证、daemon或模型任务。另建私密state完成真实认证，沿原0.2.0验收会话准确引用只读查询；持久化source/freshness为persisted/synced，目标回合completed、无activeTurns，原history回执、原产物摘要与恢复的本地结果匹配。发送新模型回合为0，临时auth已清理。脱敏结果保存在忽略的`dist/lody4dot-published-spec9-evidence/summary.json`；本轮没有复制登录态或重新创建原任务。

这证明发布后的当前依赖检查与原任务恢复对账；没有旧boot/实例基线或其他实际重建回执，不能宣布整机/存储重建、独立新任务或首次启动指引送达。T09旧截图不据此补填当时版本，C05/C07/C08/C09的剩余门槛也不由本轮查询自动关闭。

后续按[Dot接入与独立控制端验收](../../docs/lody4dot-dot-acceptance.md)使用已证实路线：有权限的UI候选导入/扫描和真实技能读取、已有合法连接或委托已准备云环境、具备本端身份的独立控制复验。候选OS仍需实际Node/native前提，Dot自有环境准备/maintenance/reset hooks另行核实。未知hook不阻塞已支持的云控制路线；本轮不为0.2.1知识修订重配token或要求重复发布。

## V01 CLI版本提示策略（本轮新增，done）

用户最新要求优先于旧版严格验证：Lody CLI版本差异、探测失败均只warn；安装、诊断和认证继续按实际命令结果执行。0.107.2只代表知识/默认安装输入基线，旧收据版本不再用于执行准入。显式`doctor --check-updates`对固定npm地址做一次最多5秒查询，非最新版/不可比较/查询失败只提醒；默认inspect/bootstrap离线，不自动升级，实际权限和命令失败保留原退出码。

127项全量回归和结构检查通过，包含41项诊断、4项版本策略、21项安装及8项生命周期行为测试；bootstrap文本也展示warn。真实npm查询本轮actual/latest同为0.107.2，账户not_run。最终包29内容文件+receipt，包内安装reused=true、启动仅doctor通过；ZIP完整性与逐文件摘要通过。最终ZIP及receipt摘要见[0.2.1验证记录](../../docs/lody4dot-validation.md#dot官方契约指引与021候选)，不再使用追加版本策略前的内部候选摘要。没有为版本检查创建业务任务、登录或升级CLI。
