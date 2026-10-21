# lody4dot的Dot接入与独立控制端验收

本页提供可操作的验收顺序，不表示已完成Dot界面导入或原生插件加载。产品事实见[宿主契约](host-contracts.md)，当前发布来源、runtime、readiness及验收进度只在[任务队列](../../.codex/agent-state/todo.md#当前环境与下一步)维护。

## 先选接入层级

| 要验证什么 | 可用路线 | 完成证据 |
| --- | --- | --- |
| Dot能正确理解Lody工作流 | 有权限的ChatGPT插件ZIP导入，安装技能包；实际调用时选择该插件 | 界面导入/启用结果、首次入口来源、实际读取的技能和插件版本 |
| 用户能主动运行插件setup | 安装含`extensions.com.openai.onboardingSkill`的候选后，用户运行setup | setup入口、所在会话、实际读到的setup技能及授权范围；不以清单字段存在代替调用 |
| Dot能使用Lody工具 | 复用真实可用的Lody连接，或由Dot创建已准备的Codex云任务使用该端CLI | 当前合法身份的只读workspace/session查询；执行位置明确 |
| 第二独立控制端能复验 | 在实际独立的授权任务/执行器取得无凭证交接记录，用自身连接查同一Lody原生引用 | 独立性来源、查询回执、同一产物及挑战值匹配 |
| Dot自己的电脑可自动重建依赖 | 仅在其正式准备/恢复接口已核实后绑定同一bootstrap | 实际触发与重建回执；Codex任务恢复不能替代 |

Dot自己的云电脑、其创建的Codex云任务、已连接的本地电脑是不同执行器。共享插件连接不自动复制CLI登录态、注入环境变量、授权本地文件或提供模型凭证。

## ZIP候选与导入入口

候选目录由仓库builder收集唯一技能源码后生成。0.2.1 ZIP含兼容清单`.codex-plugin/plugin.json`、`skills/lody4dot/`、三份hosts说明和辅助脚本；没有MCP服务器声明或预设app ID。0.2.2候选已加入包内setup技能，保留兼容格式，不迁移portable根清单。各版按自己的receipt检查完整性，不能拿源码中尚未生成skills目录的`plugin/lody4dot/`代替产物。

[官方Plugins文档](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)提供的web上传入口是Admin console→目标workspace→Plugins→Add→Upload plugin，前提是账号/角色有该入口和权限。上传后记录扫描、导入和安装结果；如界面不提供入口，报告当前账号能力缺口，不假定个人计划具备管理员入口。

完整[Plugin Management](https://learn.chatgpt.com/docs/enterprise/plugin-management)与[包装指南](https://developers.openai.com/plugins/build/plugins)本轮均HTTP200，确认portable根清单与现有`.codex-plugin/plugin.json`兼容fallback。两篇未规定ZIP外层包装的接受规则，ChatGPT上传扫描、安装和加载仍未实测；目录校验不能当作UI安装成功。遇到格式错误保留报告，定位包装或清单问题，不添加未经验证的MCP/app字段。

可在有权限时使用GitHub marketplace同步：Source填仓库URL，Path填包含清单的目录；本地条目路径相对所选marketplace根，`url`/`git-subdir`另按完整指南填写。当前三目录源码必须先构建才自包含；导入不会运行builder，不得添加指向缺失skills目录的catalog。生成分发物不提交到源码分支，GitHub分发目录/发布策略另行确定。参见[官方GitHub导入说明](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github)。

## 用户运行setup的候选验收

官方可选字段为`extensions.com.openai.onboardingSkill`；0.2.2候选已在兼容清单声明`./skills/lody4dot-setup/SKILL.md`，路径相对插件根且技能随包提供。用户运行setup时，宿主会在新会话调用；若在当前会话安装插件，则可在当前会话调用。字段存在、builder通过和用户实际运行分别取证，不能声称自动安装、Dot环境准备或存储reset时会执行。

安装与扫描通过后，分别验收新会话及当前安装会话中的用户运行setup。记录入口、插件版本/来源、技能实际读取和诊断结果；只在支持的执行环境与允许写入的prefix准备依赖。登录、注册machine、启动daemon、派发任务均需各自授权与条件，setup声明不扩大权限。无shell或不支持安装时应报告能力缺口并指向已有控制端，不将引导文本当成工具执行成功。当前没有该候选的UI安装或setup实际调用回执。

## 先做知识读取验收

安装候选后，可在Dot中选择插件并给它业务目标：

> 使用lody4dot规划一次协作：当前云端负责控制，已有远端Agent独自写验收产物，另一授权执行器只读复验。先报告你实际读到的插件/技能入口、版本和来源。说明如何选择Lody目标、超时后如何沿原请求对账，以及共享插件连接与本地电脑访问有什么区别。不要登录、创建任务、启动daemon或修改资源。没有读到插件时直接报告缺口。

检查其是否实际找到资源，而不是只重复本页的概念。入口来自平台插件、用户选择、仓库检索或直接提供路径要分别记录；全文自动注入不是完成门槛。正确规划不等于工具查询或执行已经成功。

## 复用已准备的云控制端

复用[状态表](../../.codex/agent-state/todo.md#当前环境与下一步)所列的已发布环境，分别记录正式来源、执行脚本与实际版本。0.2.0启动检查和原任务只读对账保留为历史验收；spec12的unknown观测见[宿主历史记录](host-contracts.md#本轮结论)。CLI默认安装输入为0.107.2，实际版本不同或探测失败不阻塞；可显式`doctor.py --check-updates`查询npm latest，旧版或查询失败也只warn。复用已有准备入口，不重配token或注册machine。

当选择Dot委托Codex任务时，使用已发布的目标环境。官方说明新任务有独立工作区，不恢复另一任务未提交的文件；保存VM状态默认最多7天可恢复是Codex Cloud规则，不是Dot存储reset hook。参见[Using Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud)。

本会话的子Agent不构成独立云任务。Codex CLI有正式cloud exec入口；历史spec12中，cloud list已由代理拒绝转为HTTP401，本地ChatGPT登录未证明Cloud API授权。后续结果以状态表为准，不猜失败原因或Cloud ENV_ID提交任务。没有可用插件导入界面或setup执行入口时，保留未验；同实例子进程不能替代独立任务。

已有远端Agent也可成为另一控制端：本轮Darwin端实际通过其会话内置Lody MCP查询原会话，补齐了有限双端复验，不再要求为C07另建平台云任务。该结果不证明独立新任务的首次技能加载，后者仍属于C05，也不证明Dot自身调用。

## 远端有内置MCP时

先检查本次Agent实际暴露的工具。0.107.2公开实现可由宿主运行时为会话注入Lody MCP，可能使用HTTP或宿主自己的可执行文件，因此shell的PATH缺少Node/npm/LodyCLI不能推断工具缺失。这是Lody托管会话的上下文工具，不是可直接给任意Dot安装的通用公网服务。

本轮实际查询工具为`mcp__lody__lody_session_status_many`与`mcp__lody__lody_session_history`。前者仅传`{"sessionIds":["准确session ID"]}`；后者传`{"sessionId":"准确lody原生URI","limit":50}`，必要时用同一会话的`nextCursor`读取旧页。历史若被截断不能做完整字节验收。工具未暴露或拒绝时保留缺口，不自行提取身份或构造内部socket请求。

status的execution/observation与CLI observe字段不同；自查所在会话时，本次验证回合可为busy/running，而旧产物回合已完成。旧结果按准确assistant ID从history取回，不能用当前状态替换。实际MCP调用、字段与字节复验范围见[验证记录](validation.md#远端内置mcp只读查询与c07有限双端验收)。

## 无凭证交接与只读复验

真实Lody引用保存在任务私密资料中，不进入Git或公共提示。独立控制端须通过用户提供的工件或其自身合法文件渠道取得记录；同名`/workspace`或发布相同环境不证明文件已传输。

本轮已在忽略目录的私密位置生成一份`readonly-acceptance.json`，包括原session及两次回合的准确引用、插件/CLI/来源版本、输入/产物字节与摘要、读回challenge、授权范围说明。它是此次只读验收的工件，不是`handoff.py`输入协议或新的公共接口。它不包含Lody或模型凭证，也不自行授予权限。工作区选择不缩小token本身的可见范围。

在已建立的独立任务中，可以提交以下目标和该私密工件：

> 仅复验附件readonly-acceptance.json指向的自有Lody验收会话。先确认附件存在且目标唯一，识别当前执行器、入口和实际版本。使用本端合法Lody连接；如当前任务没有私密登录态，可在本任务0700目录显式复用已配置LODY_CLI_TOKEN认证，不从交接文件取得凭证。只运行observe/history等只读查询，核对准确workspace/session/user/assistant引用、原产物完整字节、SHA-256及读回challenge。不要create/chat/cancel/archive或启动host，不重建缺失文件，不复制其他端身份。报告独立任务的实际来源、读取和查询证据；缺附件、工具、权限或独立性证据时停止并保留未知，不按标题猜测。只输出脱敏结论，仅清理由本次新建的临时身份目录及登录态，保留既有state。

对于已有结果，目标回合可能不是session最新回合：产物回合与后续只读读回回合要按各自user/assistant ID查询，不能把latestTurn直接替代目标回合。metadata、idle或CLI退出0不代替持久化终态；Agent回传字节也不等于直接访问远端文件系统。

该流程可复现C07或供C09所选端继续验收；既有Darwin内置MCP证据已覆盖C07有限双端范围，不为此重复建任务。旧截图对应任务的T09来源补证仍按[原任务验收说明](fresh-task-acceptance.md)处理，不要求为补旧截图字段重复建任务。

## 结论如何分层

分别记录知识读取、用户运行setup、合法工具调用、跨端产物复验、实际宿主重建。任一项未执行保留未执行；Dot官方电脑可在使用间隔保留状态，但没有永久保留、重置周期或重建hook契约。用户运行setup、Dot主动Reset、Codex会话事件或插件更新均不替代该回调。真实记录仅保留在授权的私密位置，公开只记版本、来源、摘要匹配和具体缺口。
