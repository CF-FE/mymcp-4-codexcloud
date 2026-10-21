# ChatGPT、Dot、Codex Cloud 与资料空间协作参考

分享版 · 整理与资料核对日期：2026-10-21。

本文整理一次围绕产品概念、云环境、资料空间、MCP 和跨端协作的完整讨论，保留会影响使用和技术选型的结论。对象标识、私人会话链接、凭证及测试文件正文均已省略。产品能力与套餐会变化，实际操作以当前入口、工具和权限为准。

开发者另读[云端任务交接版](space-cloud-handoff.md)；本仓库的方案取舍统一维护在[多宿主协作方案 c3](collaboration-development.md)。本文可以独立作为概念参考，不代表插件已经实现其中所有路线。

## 1. 先分清五个层次

| 层次 | 主要对象 | 回答的问题 |
| --- | --- | --- |
| 交互与产品 | Chat、Work、Codex | 这次主要在问答、交付成果，还是开发软件？ |
| 持续协调 | Dot | 谁持续理解目标、组织工作、跟进结果？ |
| 执行资源 | 本地电脑、Dot 云电脑、Codex Cloud 任务 VM、连接的远程主机 | 文件、命令和浏览器步骤实际在哪执行？ |
| 可复用准备 | Codex Cloud environment | 新编码任务使用哪些仓库、依赖、工具和访问设置？ |
| 资料与访问 | Space、插件连接、MCP、对象权限 | 资料保存在哪，通过什么入口、以什么范围读写？ |

这几层可以协作，但不是同一种东西。同一账号、同一个侧栏或同名目录，都不足以证明它们共享文件系统、工具、全部上下文和登录态。

### Chat、Work、Codex、Dot 的分工

| 名称 | 主要用途 | 与其他对象的关系 |
| --- | --- | --- |
| Chat／聊天 | 问答、解释、构思、对话起草 | “聊天”也可能泛指一个 Work 或 Codex 会话，不能仅凭侧栏名称判断运行环境。 |
| Work／工作任务 | 委派研究、分析、文档制作、定时工作等多步骤成果 | 可在本地或平台托管云端执行；不是“尚未配置云环境的 Codex 会话”。 |
| Codex | 构建、调试、测试、审查软件及开发工具 | 可使用本地或云端等执行位置。 |
| Dot | 持续承担责任、跟进变化、组织任务的 Agent | 可以自己工作，也能委派 Work 或 Codex；Dot 不等于某一台电脑。 |

这是产品定位，能力会重叠。例如 Dot 自己也能处理编码工作，不存在“凡是写代码都必须委派”的已知规则。[产品使用方式](https://learn.chatgpt.com/docs/use-chatgpt)、[Work](https://learn.chatgpt.com/docs/get-started-with-work)、[Dots](https://learn.chatgpt.com/docs/dots)

### Work、Work Cloud 和 Codex Cloud 的关系

Work 是面向通用成果的任务模式；Work Cloud 是在平台托管环境运行的 Work。Codex 面向软件开发，Codex Cloud 则使用已发布的仓库、依赖、工具和访问准备执行开发任务。Work Cloud 不要求先创建 GitHub 编码环境，也不会因为配置了该环境而自动变成 Codex Cloud。[Work 入门](https://learn.chatgpt.com/docs/get-started-with-work)、[Codex Cloud](https://learn.chatgpt.com/docs/environments/cloud-environments)

Work Cloud 使用 Codex 的任务执行框架，共享部分核心执行与隔离机制，但工具、权限和管理控制不完全相同。Work Cloud 由平台管理其执行环境，不能直接套用 Codex Cloud 的 VM 规格、每任务状态或插件配置规则。[执行框架与边界](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security#where-cloud-tasks-run)

### Work Cloud 能做什么

| 能力类别 | 可用于什么 | 取决于什么 |
| --- | --- | --- |
| 资料研究与分析 | 汇集来源、比较信息、分析文件、形成有依据的结论 | 实际提供的输入、项目资料、连接器和可用工具。 |
| 制作交付文件 | 生成报告、演示文稿、表格及其他可审阅成果 | 相应文件制作能力、输出格式与本次工具支持。 |
| 网页工作 | 获取批准网站的内容，或用支持的云浏览器完成工作 | 云浏览器/网络权限、网站访问及账户身份。 |
| 插件与远程MCP | 检索外部服务，执行其支持且已授权的动作 | 兼容插件、工具动作、连接授权、对象权限和审批。 |
| 资料空间文件 | 使用主动附加的资料，保存符合条件的文件 | 资料入口可用、目标对象及保存方式；不代表任意Page/原附件可覆盖。 |
| 时间或事件运行 | 定期更新、跟进检查，或响应支持的应用事件 | 已保存且启用的计划、套餐/工作区、触发器和实际运行。 |
| 连接本地资源 | 云协调任务在获批准的在线电脑上完成所需步骤 | 启用相应本地访问后的合资格新任务、本机在线和独立授权；云端不自动继承本机状态。 |

这些是产品支持类别，不保证每个账号或任务同时提供全部能力。资料处理、连接业务工具、创建其他任务分别核实；平台管理的云端执行也不等于可任意配置GitHub编码环境。[Work能力](https://learn.chatgpt.com/docs/get-started-with-work)、[云任务资料与本地访问](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security#what-a-cloud-task-can-access)

### 常见场景怎么选

下表是帮助选择入口的例子，不是互斥能力清单，也不是本账号已经逐项验收的结果。任务实际可用的工具、授权和输出要求优先。

| 想让它完成什么 | 通常选择 | 关键条件与分工 |
| --- | --- | --- |
| “解释这段报错，先告诉我可能原因” | Chat | 主要交付解释；尚未要求访问仓库或修改文件。 |
| “把这段说明改得更清楚，给我三个版本” | Chat | 短文本起草与讨论即可完成。 |
| “汇总这些资料，形成带来源的调研报告” | Work Cloud | 使用获授权的上传、项目资料、插件或网页来源。 |
| “读取指定资料空间文件，分析后制作 PPT 并保存” | Work Cloud | 需要实际文件读取、制作品和保存入口；本账号整条链路尚未实测。 |
| “比较多份报价，生成带公式的表格” | Work | 云端可取得资料时用 Work Cloud；需本机文件时选择获授权本地执行。 |
| “整理我电脑指定文件夹中的文档” | 本地 Work | 需要本机文件权限；使用云协调加本地访问时，相关电脑须在线。 |
| “通过已连接的业务系统，整理本周问题清单” | Work Cloud | 使用兼容插件或远程 MCP，操作范围由连接与对象权限决定。 |
| “打开批准的网站，收集资料并导出报告” | Work Cloud | 须有支持的云浏览器或网页工具；不能把此能力套给 Codex Cloud。 |
| “每天检查指定网站，更新一份简报” | Work 的计划任务 | 显式设置并核对计划；执行位置、可用资料和实际运行结果分别确认。 |
| “修复指定 GitHub 仓库的 bug，运行测试并提交” | Codex Cloud | 使用已发布的相应仓库环境；文件、命令和检查结果属于该任务。 |
| “修改当前本地项目，并用本机工具预览” | 本地 Codex | 使用实际本地 checkout、工具与权限。 |
| “持续跟进项目，拆分工作并收敛多个任务结果” | Dot | 持续协调责任；具体任务的执行位置和工具另记。 |
| “把资料交给 Cloud 修改仓库，完成后将结果存回资料空间” | Dot＋Codex Cloud | 沿用公子已试通的中转，由 Dot 负责资料交接与回存，Cloud 负责开发处理。 |
| “向已有远端 Agent 派发工作，并持续核对同一回合” | 具备合法 Lody 工具的控制端 | 使用 Lody 原生 session／turn；不把它当作 Codex 平台任务的自动镜像。 |

同一个“做一份报告”的需求也可有不同分工：直接整理资料并生成文件，通常用 Work；若还要将分析脚本纳入仓库、补测试和提交，开发部分可交给 Codex；若需长期跟进多个任务，由 Dot 组织。最终按所需操作选择，而不是只按产物扩展名判断。

### Work Cloud 可以怎样创建或触发

Work Cloud 不只支持用户手动点击创建。应分别识别“创建任务”“向已有会话发起新一轮”和“定时触发运行”，它们不是同一事件。

| 方式 | 当前可确认的范围 | 需要保留的边界 |
| --- | --- | --- |
| 用户从网页或支持的桌面入口创建 | 选择 Work，并使用云端执行方式；网页 Work 使用平台托管环境 | 以当前账号的可用入口和工作区设置为准。 |
| 当前本地助手经首方客户端工具代建 | 本次会话工具声明提供 `mcp__codex_app__create_thread`，目标可选 `chatgptWorkCloud`；用户明确要求后可使用 | 属于本次工具快照，本轮没有调用；不是已公布的通用外部 HTTP API，其他会话不保证暴露相同入口。 |
| 平台按时间或支持的应用事件触发 | 可从 Chat／Work 请求创建计划任务；网页任务可在原会话继续，或按设置产生独立运行／新会话 | 事件触发受套餐、工作区和支持事件限制；不把所有桌面计划任务都叫 Work Cloud。 |
| Dot 创建独立云会话 | 官方明确 Dot 可启动可见云会话并跟进；本项目的 Codex Cloud 创建由 Dot 负责 | 这不单独证明每种 Dot 入口都能创建指定 Work Cloud 类型，应记录实际创建工具及返回类型。 |

来源：[选择云端或本地 Work](https://learn.chatgpt.com/docs/use-chatgpt#choose-cloud-or-local-work)、[计划与事件触发任务](https://learn.chatgpt.com/docs/automations)、[Dot 委派](https://learn.chatgpt.com/docs/dots/tasks-and-memory#assigned-work)。首方客户端工具一行来自本次实际工具声明，不是公开 API 文档或已创建成功的回执。

本次没有建立“任意外部程序可调用统一 Work Cloud API”的结论。能调用某个业务 MCP，只说明有该服务的相应动作；若要让它创建 Work Cloud，还需要实际任务创建入口、身份与授权，不能从 MCP 连接成功直接推导。

与 Codex Cloud 的入口对照及本项目的创建分工，见[云任务创建方式对照](#codex-cloud-与-work-cloud-的创建方式对照)。

## 2. 云电脑、云任务、云环境分别是什么

| 对象 | 含义 | 文件与配置的理解方式 |
| --- | --- | --- |
| Dot 自己的云电脑 | Dot 可使用的云端电脑，有自己的文件、软件和浏览器会话 | 官方说明可跨使用间隔保留状态；没有据此建立永久保留或固定硬件承诺。 |
| Codex Cloud 任务 | 一个独立的编码工作单元，有自己的会话与隔离工作区 | 任务从所选已发布环境开始，任务内的改动不会自动成为其他任务或环境的状态。 |
| Codex Cloud 环境 | 可复用的仓库、依赖、工具、网络及访问准备 | 类似“准备好的模板”；不是整个账号共用的一台电脑。 |
| 本地 Codex | 在本机或所连接本地主机使用文件、命令及工具的 Codex 工作方式 | “本地”主要说明执行位置，不表示模型离线运行。 |
| 远程主机 | 通过连接使用的另一台执行机器 | 要确认主机身份；不一定是 OpenAI 提供的云电脑。 |

Dot 自己的云电脑与 Codex Cloud 任务，应当按**分别管理的执行环境**理解。不能默认共享磁盘、安装的软件、环境变量或浏览器登录。这是产品与状态边界，不是在断言它们一定部署在两台不同的物理服务器上。[Dot 电脑与应用](https://learn.chatgpt.com/docs/dots/computers-and-apps)、[Dot 委派任务](https://learn.chatgpt.com/docs/dots/tasks-and-memory#assigned-work)

“云端”还可能描述协调位置。启用 Local computer access with Work Cloud 后创建的合资格新任务，可由云端协调，在获批准且在线的本地电脑执行某些步骤；不能把 Codex Cloud 的每任务 VM 规则套给所有 Work 任务。[Work Cloud 执行位置](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security#where-cloud-tasks-run)

### Dot 什么时候自己做，什么时候委派？能指定吗？

目前没有查到可作为确定规则的自动路由算法。通常应按任务目标、所需工具、持续状态、仓库和环境条件选择，并通过任务详情核实实际位置。

可以明确指定：

```text
请在你自己的云电脑完成本任务，不委派；如缺少所需能力，报告具体缺口。

请把这项编码工作委派到 Codex Cloud，使用我指定的已发布环境。
交接必要输入，记录实际任务与环境；环境不可用时报告，不自行换执行位置。
```

“让 Dot 把编码任务委派到该环境”，指它创建相应的 Codex Cloud 编码任务。该任务接收为工作准备的指令和上下文，不自动获得与 Dot 的全部对话。更换 Dot 当前选择的电脑，也不会迁移已有任务。[委派与上下文](https://learn.chatgpt.com/docs/dots/tasks-and-memory#assigned-work)

### Dot 创建的云任务在哪里看？Lody 能看到吗？

官方说明，新云会话会出现在桌面、网页和移动端应用，具有自己的对话。在桌面端可以打开 **Dot 的个人资料 → Activity → 对应任务**，检查进度、文件、结果或输入请求。[任务可见性与 Activity](https://learn.chatgpt.com/docs/dots/tasks-and-memory#assigned-work)

Codex 平台任务不会自动同步成 Lody 会话。两边的可见对象分别是：

| 操作 | 在哪里查看 |
| --- | --- |
| Dot 创建 Codex Cloud 任务 A | ChatGPT／Codex 的独立会话及 Dot Activity。 |
| A 只读取 lody4dot、安装 CLI 或查询 Lody | A 仍属于 Codex；这些动作不会自动创建 Lody session，也不会自动注册 machine。 |
| A 通过 Lody 向已有节点派发，创建 Lody 会话 B | B 及其回合、执行节点由 Lody 记录；A 的平台进度仍在 ChatGPT／Codex 查看。 |

需要端到端追踪时，在协作记录中关联 A 的平台任务引用与 B 的 Lody session／turn。记录关联不代表 Lody 界面已经提供 Codex 任务的统一视图，也不要求为了“可见”把 Cloud 任务注册成 worker。

## 3. GitHub 配置的 Codex Cloud 环境给谁用

环境准备可包括 GitHub 仓库、依赖与工具、安装和启动安排、网络、环境变量及受支持的网络密钥等。它主要用于**选择该环境的新 Codex Cloud 任务**；任务的创建入口与环境准备是两回事，入口对照见下表。

它不会自动应用到普通 Chat、其他 Work Cloud 任务、Dot 自己的云电脑或本地 Codex。共享仓库表示可以取得同一代码来源，不等于共享未提交修改、整个开发目录和全部配置。[Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)

### Codex Cloud 与 Work Cloud 的创建方式对照

Codex Cloud 不只有手动创建。当前核实的入口包括**用户手动、Dot 委派、CLI 提交**。先准备并发布 Codex 环境，再向它发起任务；一次环境准备可供多个新任务使用。准备环境、创建独立任务、向已有任务发起新一轮，以及定时启动运行，分别记录。

| 入口 | Codex Cloud | Work Cloud | 证据与使用边界 |
| --- | --- | --- | --- |
| 用户手动创建 | 网页/桌面选择 **Work in → Cloud**、已发布环境后发送任务；移动端从 Codex 选择已发布环境 | 从支持的 Work 入口选择云端执行，不要求先发布 GitHub 编码环境 | 官方产品入口；以账号、工作区及当前可用界面为准。 |
| Dot 委派 | 官方明确可在已准备的 Codex 云环境创建独立编码任务 | 官方明确 Dot 可启动独立云会话；具体入口是否为 Work Cloud，仍看实际创建工具及返回类型 | 有独立会话与上下文，不自动继承全部 Dot 对话或电脑状态。 |
| Codex CLI 提交 | 官方 `codex cloud exec` 可直接提交任务；`codex cloud` 默认打开交互选择器，`codex cloud list` 查看近期聊天 | 本次没有建立通过 `codex cloud exec` 创建 Work Cloud 的支持依据 | CLI 是平台提供的另一入口；需实际客户端支持、服务访问和适用环境。本轮未执行 CLI 提交，也未验证所选已发布环境的兼容性。 |
| 首方客户端助手代建 | 本次本地 `create_thread` 工具声明没有 Codex Cloud 目标，不据此推导存在该入口 | 本次声明有 `chatgptWorkCloud` 目标，用户明确要求后可代建；本轮未调用 | 属于当前会话工具快照，不是公共 HTTP API，也不代表所有宿主相同。 |
| 计划或支持的应用事件 | 本次没有建立这些 Work 触发器会创建 Codex Cloud 任务的结论 | 网页 Work 支持计划/合资格事件运行；按设置可继续原会话或产生独立运行/新会话 | 保存计划、实际触发、是否新建会话、执行和交付分开取证。 |

来源：[Codex Cloud 手动入口](https://learn.chatgpt.com/docs/environments/cloud-environments#start-a-task-in-codex-cloud)、[环境准备与发布](https://learn.chatgpt.com/docs/environments/cloud-environments#create-and-publish-an-environment)、[Dot 委派](https://learn.chatgpt.com/docs/dots/tasks-and-memory#assigned-work)、[Codex CLI Cloud 命令](https://learn.chatgpt.com/docs/developer-commands#codex-cloud)、[Work 执行位置](https://learn.chatgpt.com/docs/use-chatgpt#choose-cloud-or-local-work)、[计划与事件运行](https://learn.chatgpt.com/docs/automations)。首方工具一行的依据为本次工具声明。

### 平台能力、当前入口与项目分工分开看

| 层次 | 本次结论 | 对方案的影响 |
| --- | --- | --- |
| 平台支持 | Codex Cloud 有手动、Dot、CLI 提交路径；Work Cloud 的已核实入口见上表 | 文档描述可选路径，不把项目选择写成平台唯一入口。 |
| 当前工具与访问 | 本地首方声明提供 Work Cloud 代建；旧 Cloud CLI 查询曾返回 401，本轮没有重试或提交任务 | 工具存在、CLI 登录、API 授权与创建成功分别判断；历史失败不证明其他账号/入口不可用。 |
| 本项目职责 | **独立 Codex Cloud 任务由 Dot 创建；当前云任务不再派生下游 Codex Cloud 任务。** | 沿用现有授权和分工；CLI 平台入口的补充不要求接入新调度器、重试旧 API 或索取新凭证。 |

CLI 官方说明沿用主 CLI 凭证、提交失败返回非零；登录成功仍不能代替目标 Cloud 服务实际授权。本文不补造通用创建 REST API、环境 ID 或未核实的命令参数。企业聊天工具委派按公子要求延后，不纳入本轮方案与实施优先级。

例如，公子自己从 Cloud 入口开一个修复任务，属于平台手动创建；让 Dot 在指定环境开同类任务，属于平台委派入口，也是本项目采用的分工；从终端用 `codex cloud exec` 提交同类工作，属于另一平台入口，本项目当前不接入。任务开始后读取 lody4dot、经 Lody 派发到已有节点，属于 Lody 的 session/turn 操作，不等于又创建了一个 Codex Cloud 任务。

### 保存环境与创建任务分别核实

| 操作 | 应怎样理解 |
| --- | --- |
| Save | 保存环境设置；部分设置会影响当前准备过程。 |
| Publish | 捕获准备好的文件系统，供新任务使用。 |
| Republish | 更新供新任务采用的准备状态；已有任务仍有自己的状态。 |
| 自动刷新仓库 | 可保留依赖缓存，不代表重新执行全部安装或启动。 |
| 在任务内安装或修改文件 | 改变该任务，不自动更新环境模板或其他任务。 |

配置保存、环境发布、目标任务采用，以及业务操作成功，要分别确认。[环境复用与更新](https://learn.chatgpt.com/docs/environments/cloud-environments#reuse-and-update-saved-state)

### 是 Docker 吗？硬件多大？

官方当前以 **VM** 描述任务执行资源。可以用 Docker 的“准备环境再创建实例”帮助理解复用，但不能因此把平台实现、隔离方式或权限直接当作 Docker。

2026-10-21 官方列出的每任务默认规格：

| 计划 | vCPU | 内存 | 磁盘 |
| --- | ---: | ---: | ---: |
| Plus、Edu Plus | 2 | 8 GiB | 8 GiB |
| Pro、Business、Enterprise | 4 | 16 GiB | 32 GiB |
| Edu、Edu Pro | 4 | 16 GiB | 32 GiB |

Enterprise 可咨询更大或定制规格；该页没有给出可据以承诺的 CPU 型号或 GPU。此表不适用于 Dot 云电脑、Work Cloud 或资料空间容量。[VM specifications](https://learn.chatgpt.com/docs/environments/cloud-environments#vm-specifications)

默认保存的 VM 状态可在上次启动一轮或恢复任务后最多七天内恢复。这不是七天持续运行，也不是七天后全部会话、Git 仓库和资料空间文件统一删除。重要成果仍应提交或保存到持久目的地。当前文档还将 computer/browser use、本机个人 Skills 不自动同步等列为边界；不要套用 Dot 云电脑的浏览器能力。[生命周期](https://learn.chatgpt.com/docs/environments/cloud-environments#vm-specifications)、[当前限制](https://learn.chatgpt.com/docs/environments/cloud-environments#current-limitations)

当前 Cloud 与 Codex Cloud (Legacy) 有独立说明；旧版的准备流程和密钥规则不能未经核对套到当前环境。

## 4. 资料空间与 100 GB

Space 是资料和协作入口，官方将其描述为原 Library 的演进，汇集 Pages、Slides、上传文件及共享内容等；不同对象的编辑方式和工具不同。[Space](https://learn.chatgpt.com/docs/space)、[企业 Space 说明](https://learn.chatgpt.com/docs/enterprise/chatgpt-space)

本次核实的本地客户端 Pro 套餐文案包含 **100 GB 文件存储容量**。这是套餐文案证据，没有查询账号当前分配、使用量或剩余额度；不能推广为所有套餐都有 100 GB，或每个独立 Space 各有 100 GB。

| 容易混淆的“空间” | 实际对象 |
| --- | --- |
| 资料空间／Space | 持久页面、文件和共享资料。 |
| ChatGPT 个人或组织 workspace | 账号成员、管理策略和设置范围。 |
| Codex 任务 workspace | 某个执行环境的工作目录。 |
| Git worktree | 某仓库的独立工作副本。 |
| Lody workspace | Lody 的机器、配置、会话等业务资源范围。 |

文件存储容量、模型上下文、Memory、电脑磁盘是不同概念。资料进入 Space 不等于自动进入每个任务的上下文，也不等于挂载到 VM 的 `/workspace`。

谁能操作，取决于具体对象的查看／评论／编辑权限、账号与工作区策略，以及当前产品实际提供的工具。页面可读不保证其链接原附件可读；能编辑原生表格或页面，也不等于能上传任意二进制文件。分享页面不自动分享私人聊天或全部记忆。[资料协作与权限](https://learn.chatgpt.com/docs/space/collaboration)

### Work Cloud 能直接读写资料空间吗

官方已建立受支持的文件读取与保存路径，不必把 Dot 设为这些操作的必经中转；这里的“直接”指产品提供的授权入口，不是将整个资料空间挂载进云电脑。

| 操作 | 官方支持与当前边界 |
| --- | --- |
| 读取资料文件 | 可使用用户主动从 Library 附加、上传或通过项目提供的文件，以及已启用应用通过合法连接取得的内容。不是默认读取账号下全部文件。 |
| 保存结果文件 | Library 可用时，符合条件的上传或生成文件可保存其中；不据此保证覆盖原附件、保留任意格式或处理任意大小。 |
| 创建、修改 Page | Space 支持 ChatGPT 创建和修订页面；某个 Work Cloud 会话仍须实际提供所需工具并通过对象访问检查。文件保存能力不单独证明任意 Page 都可编辑。 |

来源：[云任务可以访问什么](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-cloud-security#what-a-cloud-task-can-access)、[Cloud Work 文件保存](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-overview#cloud-work)、[Page 操作](https://learn.chatgpt.com/docs/space/pages)。资料空间的部分文件说明仍使用 Library 名称，应按实际对象入口判断。

以上是官方支持范围，本次没有在公子的 Work Cloud 会话完成“读取→处理→保存→目的地回读”实测。此前缺工具的回执针对那个 Codex Cloud 任务，不能套用为 Work Cloud 的运行结果。

## 5. 本地 Codex 通过什么操作资料空间

本次本地 Codex Desktop 会话暴露了首方资料工具，示例包括：

| 工具名称 | 该入口的用途 |
| --- | --- |
| `mcp__codex_apps__chatgpt_space_read_page` | 读取 Page。 |
| `mcp__codex_apps__chatgpt_space_create_page` | 创建 Page。 |
| `mcp__codex_apps__chatgpt_space_edit_page` | 编辑 Page。 |
| `mcp__codex_apps__chatgpt_space_write_page_reference` | 写入页面文件引用，具体能力按实际 schema。 |
| `mcp__codex_app__read_page_reference` | 经页面及文件权限检查读取支持的关联文件。 |

这些名称是**本次桌面会话的工具界面快照**，不表示所有本地 CLI 或云任务都提供，也不是稳定公共 HTTP API、可导出的服务地址或通用安装清单。不是只有 Dot 能操作资料空间；本地 Desktop 也可在工具和权限允许的具体范围操作。

MCP 是工具连接协议。要使用它，还需要服务器实现、传输与地址、认证、客户端注册和目标权限。工具带有 `mcp__` 前缀，不足以证明电脑上存在一个可直接转发的自托管 Space 服务。

官方 MCP 指引说明，同一 Codex host 的桌面、CLI 和 IDE 可共享配置，支持 STDIO、Streamable HTTP；网页 Chat／Work 可通过相应插件连接远程 MCP。这不能直接视为当前 Codex Cloud 的任意原生工具注册流程。[MCP 配置](https://learn.chatgpt.com/docs/extend/mcp#connect-an-existing-mcp-server)、[插件支持面](https://learn.chatgpt.com/docs/plugins)

插件连接可按官方约定在已授予范围跨产品复用，但共享连接不保证某一次任务实际暴露全部工具。工具暴露、对象权限、本地电脑访问、浏览器会话、CLI 身份及模型凭证仍应分开核实。仓库的进一步依据见[宿主契约](host-contracts.md)。

### Work Cloud 与 Codex Cloud 的插件和 MCP 有何区别

| 对比 | Work Cloud | Codex Cloud |
| --- | --- | --- |
| 产品内插件入口 | 官方明确 hosted Work 可安装并连接兼容插件，使用其连接器和远程 MCP 工具 | 不能从桌面 Codex／CLI 支持插件，推定每个 Codex Cloud 任务自动加载。 |
| 远程 MCP 注册 | 通过受支持的 ChatGPT 插件连接入口使用；网页不会自动采用本地 Codex 配置 | 当前核对的环境指南未建立任意 MCP／插件的通用原生注册方法；不是所有云端调用永远不可能。 |
| 本机 STDIO 服务 | 不会自动搬进云端；通过已连接电脑使用本地能力时，另核实本地工具、在线状态及认证 | 本地 `codex mcp add`／`config.toml` 不直接成为已验证的 Cloud 配置。 |
| 服务器网络调用 | 兼容插件工具由产品及连接策略提供 | 任务可在获授权的网络与身份范围使用服务客户端；在 shell 安装 SDK 或发 HTTP，不等于注册成模型原生 MCP 工具。 |

来源：[MCP 的托管 Work 与本地主机支持面](https://learn.chatgpt.com/docs/extend/mcp)、[插件支持面](https://learn.chatgpt.com/docs/plugins)、[Codex Cloud 配置](https://learn.chatgpt.com/docs/environments/cloud-environments)。`Desktop only` 插件需要桌面支持；服务器是远程 HTTPS，并不能单独证明整个插件可在网页或纯云端使用。

MCP 并非天然只读。写操作需要工具本身提供相应动作、连接身份获授权、对象允许访问，并满足工作区动作控制和审批。首方资料工具与外部 MCP 是不同入口，不能从“已连接某个 MCP”推导额外的 Space 权限，也不能用单一套餐标签概括所有 MCP 的读写能力。[连接能力与动作控制](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors#step-2-manage-capabilities)

## 6. 实际验证得出了什么

| 证据来源 | 实际观察 | 可支持的结论 |
| --- | --- | --- |
| 本地 Desktop 逐步工具回执 | 创建 Page、上传 776 字节 JSON、追加附件链接、独立读取附件成功；上传与源文件摘要一致。 | 这些具体写入和附件读取步骤成功。 |
| 同轮后续本地调用 | `read_page` 返回 `page_read_forbidden`。 | 页面访问存在实际拒绝，不能把前述成功推广为稳定的全部读写链路；也不能抹去已成功的步骤。 |
| 用户贴回的 Codex Cloud 实测结果 | 该任务无 Space／Pages／Library 工具；未读取输入，未计算、未保存结果、未回读。 | 该次任务缺少直接访问所需的入口；不是已证明文件不存在或用户没权限。 |
| 用户明确确认 | Dot 中转已试通，要求不再验证。 | **资料空间 ⇄ Dot ⇄ Codex Cloud 是本次已成立的可行路线。** |
| Work Cloud 官方资料与本地工具声明 | 已读取文件附加／保存、插件远程 MCP、计划任务和创建入口的说明；本轮未调用 Work Cloud 创建工具或资料读写。 | 有产品支持依据和本会话工具入口证据，尚无本账号端到端运行回执。 |

Cloud 结论来自用户提供的执行回执，本整理会话没有独立进入那个 Cloud 任务。资源与模板枚举为空只是其中一项信息；MCP 的 Tools、Resources、Templates 不是同一清单，不能只靠空资源列表判断没有工具。

该任务的 `download_file` 只接受 Sediment 文件 ID，不能据此读取 `library-file:`。网页 URL、`library-file:`、`project-file:`、Sediment ID、执行端路径和 Git 引用都有自己的语义，不能改前缀或直接互换。

Dot 中转可行与 Cloud 缺少原生工具并不矛盾：前者是多方协作完成业务，后者描述一个执行端的直接能力。已试通的中转不需要重做基础可行性验证；任意格式、大小、吞吐或自动化程度没有在这次讨论中建立统一保证。

## 7. 推荐怎样协作

### 资料空间里的输入要交给 Cloud 处理

已知可用的分工是：**Dot 读资料和组织交接 → Cloud 处理 → Dot 收取结果、写回资料空间并确认可读取。**

1. 指定源资料、处理目标、目的位置和允许的写入方式。
2. Dot 通过实际工具取得输入，说明交给 Cloud 的是原文件、提取正文还是摘要。
3. Cloud 在指定任务与环境处理输入，返回处理结果及可取得的产物。
4. Dot 将结果保存到指定资料对象，回读或通过受支持入口核对结果，返回持久引用和阶段状态。

需要原始字节一致时再对取得的文件计算字节数和 SHA-256；复制到对话的文本可能被重编码，不能用它的哈希冒充原附件哈希。

可直接给 Dot 的指令：

```text
请读取我指定的资料空间文件，将本任务需要的输入交给指定的 Codex Cloud 环境处理。
由你负责资料空间读写，Cloud 负责计算与代码工作。
完成后把结果保存到指定资料位置，并从目的位置核对内容，返回持久引用。
说明实际传递的是原文件还是提取正文，以及读取、处理、保存、回读各自的结果。
沿用已试通的中转方式；如某一步受阻，保留已有成果并报告该步，不用重复创建任务。
```

### 什么情况下使用 Lody 或本地 Codex

需要经 Lody 发现节点、向既有 Agent 派发、持续观察原生 session／turn 或多宿主复验时，使用本仓库已提供的 Lody 协作能力。仅完成资料空间与 Cloud 的已可用 Dot 中转，不必为了统一形式再绕一层 Lody。

需要本机文件或本机工具时，可选择本地 Codex，前提是本端有合适的连接和权限。不同产品、不同机器的成功不能相互代替，但同一任务内已经成立的授权和能力也不必反复申请或重复证明。

## 8. 能把本地资料工具通过远程 MCP 转给 Cloud 吗

**工程上可以评估远程桥接，但本次没有建立“现有首方工具可以直接导出”的结论，也没有查到当前 Cloud 通用的原生 MCP 安装步骤。**

可能的实现路径有区别：

| 路线 | 必须另行具备什么 | 本次状态 |
| --- | --- | --- |
| Cloud 使用原生资料工具 | 产品在该任务提供相应工具、连接和权限 | 目标实测任务未提供；其他任务不据此一概否定。 |
| Cloud shell 经 HTTPS／MCP client 调用远程桥接 | 已授权网络、客户端、认证、服务端，以及受支持的资料读写上游 | 工程候选，未实现或验收。 |
| 在线本地 Agent 接单，再用其会话工具处理 | 本地 Agent 在线、合法工具上下文、任务与结果传递入口 | 另一种中转工程；不等于导出首方连接器。 |
| Dot 中转 | Dot 可用的资料工具与实际委派、结果收取方式 | 用户已试通，当前优先复用。 |

Cloud 支持配置网络和凭证访问服务，说明外部 API 路线可以研究；允许域名不提供认证，安装 MCP SDK 也不自动把服务注册成模型工具。[连接服务](https://learn.chatgpt.com/docs/environments/cloud-environments#connect-to-services)

若未来确需桥接，先核实上游接口、认证和服务所有者。不要猜 Space MCP URL、抓取桌面 Cookie、转交登录态，或将当前工具 schema 当作已公开的 HTTP 服务。已知 Dot 中转满足需求时，暂不引入新的常驻服务和维护负担。

## 9. 侧栏图标速查

以下来自 2026-10-21 本地已安装客户端的图标、可访问标签和渲染条件核实；界面可能随版本和布局变化。图标描述会话类型或某项状态，不代替任务详情与结果回执。

| 图形／显示 | 当前可确认的含义 | 阅读边界 |
| --- | --- | --- |
| 截图中的笔记本＋下方点阵 | `Cloud environment setup`，云环境配置会话 | 不是通用“本地电脑”标识，不代表已发布或成功。 |
| 云朵 | 云端会话／任务的环境标记 | Work 也使用，不能据此认定是 Codex 或某个 GitHub 环境。 |
| 分叉箭头 | Git worktree | 是独立工作副本，不仅是普通分支。 |
| 地球 | 已连接的远程主机 | 看主机名称；不等于 Dot 云电脑。 |
| 地球＋分叉 | 远程主机上的 worktree | 不表示运行结果。 |
| 普通对话气泡 | 某些固定会话行的默认图标，可被自定义图标替代 | 不是 Chat 模式唯一标识。 |
| Dot 自定义头像 | 对应 Dot 的主会话 | 不表示执行器或工具权限。 |
| 转动圆环／Working | 正在工作，也可能在发布环境 | 不表示发布成功或进度百分比。 |
| 蓝点／数字 | 未读更新／未读数量 | 不表示成功、失败或运行任务数。 |
| 红色错误提示 | 该行有错误状态 | 原因需查看详情。 |
| 时钟／日程 | 已安排运行或关联了计划任务 | 不证明已触发，也不限定云端执行。 |
| 语音标记／活动脉冲 | 语音会话或语音活动 | 不代表全部后台任务状态。 |
| Awaiting approval／Needs input | 需要审批或输入 | 按实际文字处理。 |
| 没有环境图标 | 可能由本地默认行、分组或布局条件导致 | 不能单凭缺省图标判断产品类型。 |

本次未建立“完成任务必有固定绿色对勾”的通用规则。

## 10. 交付时保留哪些信息

一份可核查的协作回执至少说明：目标及授权范围、输入来源与实际取得方式、协调者与执行位置、实际路线、产物所在位置、保存和回读结果，以及未完成的步骤。用户转述、工具回执、官方说明和工程推论分别标注。

Cloud 生成了本地文件，只能证明计算产物存在；有链接或任务显示完成，不单独证明资料空间保存成功。对于要求“处理后存回资料空间”的任务，结束条件是结果进入指定资料对象，并有足够的内容核对证据。

后续若产品工具、计划、权限或配置变化，只复核受影响的结论。已确认的 Dot 中转基础不重复验证；新增文件类型、桥接接口或正式插件集成，按各自新增要求验收。
