# lody4dot的Dot接入与独立控制端验收

本页提供可操作的验收顺序，不表示已完成Dot界面导入或原生插件加载。产品事实见[宿主契约](host-contracts.md)，实际状态只在[任务队列](../../.codex/agent-state/todo.md)维护。

## 先选接入层级

| 要验证什么 | 可用路线 | 完成证据 |
| --- | --- | --- |
| Dot能正确理解Lody工作流 | 有权限的ChatGPT插件ZIP导入，安装技能包；实际调用时选择该插件 | 界面导入/启用结果、首次入口来源、实际读取的技能和插件版本 |
| Dot能使用Lody工具 | 复用真实可用的Lody连接，或由Dot创建已准备的Codex云任务使用该端CLI | 当前合法身份的只读workspace/session查询；执行位置明确 |
| 第二独立控制端能复验 | 在实际独立的授权任务/执行器取得无凭证交接记录，用自身连接查同一Lody原生引用 | 独立性来源、查询回执、同一产物及挑战值匹配 |
| Dot自己的电脑可自动重建依赖 | 仅在其正式准备/恢复接口已核实后绑定同一bootstrap | 实际触发与重建回执；Codex任务恢复不能替代 |

Dot自己的云电脑、其创建的Codex云任务、已连接的本地电脑是不同执行器。共享插件连接不自动复制CLI登录态、注入环境变量、授权本地文件或提供模型凭证。

## ZIP候选与导入入口

候选目录由仓库builder收集唯一技能源码后生成。ZIP中包含原生`.codex-plugin/plugin.json`、`skills/lody4dot/`、三份hosts说明和辅助脚本；没有MCP服务器声明或预设app ID。按包内清单检查完整性，不能拿源码中尚未生成skills目录的`plugin/lody4dot/`代替产物。

[官方Plugins文档](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)提供的web上传入口是Admin console→目标workspace→Plugins→Add→Upload plugin，前提是账号/角色有该入口和权限。上传后记录扫描、导入和安装结果；如界面不提供入口，报告当前账号能力缺口，不假定个人计划具备管理员入口。

候选使用已核实的Codex0.163.0清单。完整[Plugin Management](https://learn.chatgpt.com/docs/enterprise/plugin-management)正文当前CONNECT403，ChatGPT的ZIP包装/扫描尚未实测；不能把目录校验成功写成UI安装成功。遇到格式错误保留报告，先定位包装层级或清单问题，不添加未经验证的MCP/app字段。

可在有权限时使用GitHub marketplace同步，但当前三目录源码必须先构建才自包含。GitHub导入不会替你运行builder；不得添加指向缺失skills目录的catalog。生成分发物不提交到源码分支，GitHub分发目录/发布策略另行确定。参见[官方GitHub导入说明](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github)。

## 先做知识读取验收

安装候选后，可在Dot中选择插件并给它业务目标：

> 使用lody4dot规划一次协作：当前云端负责控制，已有远端Agent独自写验收产物，另一授权执行器只读复验。先报告你实际读到的插件/技能入口、版本和来源。说明如何选择Lody目标、超时后如何沿原请求对账，以及共享插件连接与本地电脑访问有什么区别。不要登录、创建任务、启动daemon或修改资源。没有读到插件时直接报告缺口。

检查其是否实际找到资源，而不是只重复本页的概念。入口来自平台插件、用户选择、仓库检索或直接提供路径要分别记录；全文自动注入不是完成门槛。正确规划不等于工具查询或执行已经成功。

## 复用已准备的云控制端

本轮已发布环境使用0.2.0及CLI0.107.2，启动检查和原任务只读对账已实测；0.2.1补充知识/接入材料，并改为非阻塞的CLI版本提示。默认安装输入仍为0.107.2，但实际版本不同或探测失败不阻塞；可显式`doctor.py --check-updates`查询npm latest，旧版或查询失败也只warn。现有准备入口可复用，不重配token或注册machine；正式源码版本与当前执行脚本分别记录。

当选择Dot委托Codex任务时，使用已发布的目标环境。官方说明新任务有独立工作区，不恢复另一任务未提交的文件；保存VM状态默认最多7天可恢复是Codex Cloud规则，不是Dot存储reset hook。参见[Using Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud)。

本会话的子Agent不构成独立云任务。已发现Codex CLI正式cloud exec入口，但本轮其cloud list所需chatgpt.com被代理拒绝，尚无经服务核实的Cloud ENV_ID，不能猜ID提交任务。当前没有插件导入界面工具；同实例子进程也不能替代独立任务。

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

记录知识读取、合法工具调用、跨端产物复验、实际宿主重建四项结果。任一项未执行保留未执行；Dot主动Reset、Codex会话事件或插件更新均不替代磁盘重建回调。真实记录仅保留在授权的私密位置，公开只记版本、来源、摘要匹配和具体缺口。
