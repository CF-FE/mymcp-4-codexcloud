# 兼容性、调用路径与结果状态

当前公开帮助快照为`lody@0.108.1`，20类70命令均已实际执行帮助；默认受管安装准备解析官方npm latest，源码锁记录本轮精确结果。实际版本不同或版本查询失败只提示，命令帮助与实际返回决定具体参数和行为。0.107.2的静态源码、远端任务和历史连接证据仍保留当时范围，不能改称新版业务已测；资料记载某项能力不代表当前账户、机器、provider和宿主都支持它。准确版本与证据见[来源记录](sources.json)。

## 版本提示与实际失败

doctor默认inspect及启动bootstrap保持离线；显式`--check-updates`才单次查询npm latest，不自动升级。实际CLI较旧、实际版本查询失败或npm查询失败只warn；其余必要检查通过时仍退出0。版本提示不证明全部命令兼容，也不要求先升级才能使用：按当前命令帮助与真实结果继续已有授权任务。

上述离线规则用于检查阶段；已授权的安装器/`--prepare`每次在暂存目录解析latest并按精确锁安装或复用。启动`--repair-missing`仅在明确缺受管依赖时进入该安装阶段。latest安装政策不把日常版本warn变成升级动作，也不扩大认证或业务操作授权。

安装锁、包摘要和来源收据的完整性仍需校验，不能把损坏当作版本差异放过。Node/OS支持和依赖缺失也是独立前提。真实业务命令、身份、权限或实际语义不兼容按原错误码和分类报告；不能为保持退出0吞掉这些失败。`control/task/worker`原本需要的连接或执行证据也不因版本仅warn就算通过。

宿主、OS/架构与运行角色分别识别。OpenAI官方确认Dot是ChatGPT中的always-on agent产品，具备自己的云电脑，也可向预先配置的Codex云环境创建任务；产品Dot不作为任意Agent的通用别名。Dot云电脑、Codex云任务和另行授权的本地电脑分别核实工具与任务位置，不等同于已有Lody执行节点；lody4dot在这些位置的实际加载与工具调用仍分项验收。多端目标与交接见[协作参考](collaboration.md)。

## 平台和运行位置

| 情况 | 正确判断 |
| --- | --- |
| Lody cloud构建 | 指Lody发布构建的平台选择，与Work Cloud或Codex Cloud执行位置不同；仍需验证网络与登录 |
| OSS/local platform | 不具有全部 cloud 查询；不能仅设置一个变量就把 cloud 发布包切换为 OSS |
| Work或Work Cloud | 通用任务可本地或托管执行，不自动使用已发布Codex开发环境；任务类型和创建入口见[协作参考](collaboration.md#work-cloud与任务创建) |
| Dot自有云电脑 | 受Dot和工作区实际云能力约束；不假定使用Codex准备脚本、相同目录或相同浏览器登录 |
| Dot创建Codex云任务 | 使用已预先配置的Codex环境；该任务的加载、身份和执行证据与Dot自身分别记录 |
| Dot连接本地电脑 | 本地访问默认关闭，需本机ChatGPT应用单独连接授权、在线；Codex连接或Work Sync不能代替 |
| Codex 云端 control | 可以实现登录后的发现和观察；不能默认承担全部本机执行 |
| Codex 云端 task | 执行端需运行进程、Agent 凭证与明确目标；远端派发不要求控制端启动 daemon |
| 长期 worker | 需独立验证启动、机器注册、进程与任务恢复；不承诺一次性云任务永久在线 |
| 桌面 app、模拟器、原生 provider 能力 | 条件支持，先检查目标平台与实际能力协商 |

公开的 `lody` npm 构建选择 cloud 平台；不要假定 `LODY_PLATFORM` 是支持的切换入口。`LODY_DATA_DIR` 的目录选择也不证明私密隔离、跨任务恢复或共享快照安全。

Dot与ChatGPT、ChatGPT Work、Codex共享插件连接和已授予权限；它们不自动提供本地文件访问、全部协作空间访问、写入权、其他端登录态或Lody目标Agent的模型凭证。local skills要求电脑已连接到Dot，插件共享设置本身不证明每个任务实际加载了技能或工具。官方Reset是主动删除Dot的产品控制；未证明周期磁盘重置、自动初始化hook或云目录持久化。

`0.107.2` 的会话 CLI 可以在无本机 host 时创建工作区 client。本机目标才由 `ensureTargetMachineOnline` 要求本机运行进程；远端目标通过机器 RPC 检查、创建和继续，活动回合的取消也按目标路由。无活动回合时 `cancel` 可返回 `alreadyStopped`。因此控制端 daemon 缺失不能作为拒绝远端派发的依据，`agent-config refresh-capabilities` 的本机要求则不变。

项目既有验收已通过远端Codex配置的create/chat与两个回合的持久化完成，Agent二次读回的文件字节及随机challenge经控制端校验匹配。另一个自有普通运行回合按assistantTurnId精确取消后，同一回合为persisted/synced/canceled。只承认这些配置与操作的证据，不推广到Operation协作链、其他配置/平台或工具进程即时终止，也不称控制端直接读取远端文件系统。

## 命令索引的运行前提

索引中的 `requires.local_runtime` 以运行命令的本端为参照，不能单独表示所有目标端的要求。`session create/chat/cancel` 的false表示存在不需要控制端host的远端路径；选择本机目标时仍需本机运行进程，远端执行端也仍需运行进程和Agent凭证。结合具体命令的 `runtime_note`、实际目标与[会话参考](sessions.md)判断。`agent-config refresh-capabilities` 为true，保留正确本机执行限制，不转成跨机刷新能力。当前说明不改变索引schema，也不将help_verified或documented升级为业务实测。

## CLI 与已有 MCP

CLI 的帮助是当前参数和位置参数的权威来源。原生 JSON/JSONL 直接保留；辅助工具不重写 session/schedule 业务 API。

已读官方资料支持hosted Work经兼容插件使用连接器和远程MCP；本机STDIO或本地Codex配置不会自动迁入云端，Desktop only限制仍按具体插件核实。Codex Cloud当前指南未建立任意MCP/插件的通用原生注册流程；获授权的shell服务调用也不等于模型原生工具注册。这些产品支持范围不证明本插件在Work Cloud已加载。来源：[MCP支持面](https://learn.chatgpt.com/docs/extend/mcp)、[插件](https://learn.chatgpt.com/docs/plugins)、[Codex云环境](https://learn.chatgpt.com/docs/environments/cloud-environments)。

MCP不是天然只读，写动作取决于实际工具、连接身份、对象权限、工作区控制及审批。业务MCP不自动提供资料空间权限或平台任务创建入口；创建/触发的选择见[协作参考](collaboration.md#work-cloud与任务创建)，不照搬其他会话的客户端工具名。来源：[动作控制](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors#step-2-manage-capabilities)。

Lody 内置 MCP 的资源发现、会话、operation、调度和角色工具需要真实宿主上下文。已显示的配置和 MCP 选择不等于工具加载成功；只有实际注入与可调用证据才能选择该路径。不能在缺少 session/workspace/machine 上下文时调用内部启动入口，也不能凭网上出现的工具名伪造当前工具存在。

模型/模式/权限和扩展能力来自目标运行时协商。支持一个 ACP 或 Lody 扩展不表示支持其余扩展；刷新能力也须满足实际机器与进程约束。Lody 账户 token 不等于 Provider 的模型凭证。

0.108.1认证与Streams刷新仅完成静态源码核对：API-key登录会写本机身份；设备授权和配对具有不同远端副作用。目录CLI仍依赖credentials和SQLite，没有新增已核实的无状态目录入口。默认Streams对401/403可刷新短期Streams token并重试一次，这不是新建CLI API key或重新登录；不能凭403直接决定关闭刷新或推断认证可用。原始异常可能含响应正文，诊断仍须脱敏，见[准备规则](setup-cloud.md)与[故障处理](troubleshooting.md)。本轮未重试旧403或进行新版线上认证。

## 内置 Codex 与 host 范围

`0.107.2` 自带 `dist/codex-acp.js`（适配器 `1.12.0`），builtin Codex 默认解析 managed `0.160.1`；系统 PATH 里存在另一个 Codex 不表示它会被采用。内置 launch 先解析 `runtimeOverrides.codexPath` 或 managed runtime，再设置 `CODEX_PATH`，后者覆盖 Agent config 的同名 env。当前公开 create/update CLI 没有对应 runtimeOverrides 或 custom command 参数，不猜字段、不改底层 store。

直接启动 bundled adapter 时，`CODEX_PATH` 是该入口明确要求的参数；这种单独预检与 builtin 默认运行链路分别记录。ACP `initialize` 不发送模型任务，但可能启动原生 app-server 并尝试写运行状态；`session/new` 会建立 thread 并查询模型，不能作为零持久化探测。

项目在2026-10-20至21的托管Linux实例验收中已校验并运行managed `0.160.1 --version`，但bundled ACP `initialize` 返回RPC1001；单独指定私密 `CODEX_SQLITE_HOME` 后仍返回read-only错误。同版本官方启动代码还无条件以可写方式打开 `$CODEX_HOME/installation_id`，该测试实例的文件系统只读；sqlite_home、log_dir和cwd不改变此路径。遵守宿主要求，不改变HOME/CODEX_HOME或复制认证来绕过限制。这是该实例与版本的记录，不能作为全部云环境的固定结论；它不否定控制端向已授权远端派发，其他执行端仍各自验收。

API-key 路径的 `LodyFleet` 为账户返回的全部工作区建立 runtime 并登记本机/默认配置；任务的 `--workspace` 或 `LODY_WORKSPACE_ID` 不过滤 host 的工作区订阅。用户限定单个工作区时，先核实凭证或宿主是否有受支持的范围限制，不因任务目标已指定就假称 host 只影响该工作区。

不使用 `LODY_E2E` 或标题辅助进程作为认证隔离技巧；对应分支可能创建工作目录 `.codex` 并复制默认认证。受控任务使用明确标题，并保持已有认证边界。

## 证据和状态

| 观察 | 可以报告 | 不能单独报告 |
| --- | --- | --- |
| 资料和入口文件可读 | 文件可访问 | 新任务已加载技能 |
| `--version`、帮助通过 | CLI 入口可运行 | 账户和任务可用 |
| 变量存在 | 凭证材料已注入 | 已登录 |
| 有效身份查询成功 | 当前授权已验证 | 目标机器与 Agent 可执行 |
| 进程存在 | 发现运行进程 | daemon 就绪或任务完成 |
| 目录有可用缓存 | 当前发现结果 | 资源被预留、请求一定成功 |
| 提议响应成功 | 待用户保存的提议已生成 | 角色或调度已生效 |
| persisted turn 结果与产物核验 | 对应任务完成/失败/取消 | 所有其他能力也已验证 |

状态不明就明确保留未验证、待确认或进行中。不要以 mock、帮助输出、文字声明或错误退出被隐藏的管道代替真实业务结果。

来源：[CLI 文档](https://lody.ai/zh/docs/cli/)、[快速开始](https://lody.ai/zh/docs/quickstart/)、[ACP 与扩展能力](https://lody.ai/zh/docs/acp-feature-support/)、[npm 发布元数据](https://registry.npmjs.org/lody)、[Dot入门](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)、[Dot工作区管理](https://help.openai.com/en/articles/20001554-manage-dots-in-chatgpt-workspaces)、[Dot隐私与权限FAQ](https://help.openai.com/en/articles/20001529-dots-privacy-security-and-safety-faqs)（Dot资料读取于2026-10-21）。
