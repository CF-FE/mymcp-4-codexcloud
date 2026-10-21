# Dot、ChatGPT与已准备的Codex云环境

Dot是ChatGPT的常驻Agent产品，有自己的云电脑；它还可以创建预先配置的Codex云任务，或在用户明确连接的本地电脑上创建任务。三个执行位置分别识别，当前CLI工具可用不能单独证明调用发生在Dot自己的电脑上。

## 选择接入路线

先区分资料交接与Lody任务控制。对当前任务已有用户确认的“资料空间→Dot→Codex Cloud→Dot→资料空间”路线，直接复用：Dot负责资料读写及结果收取，Cloud负责处理；不为统一形式额外创建Lody会话、注册machine或部署MCP。输入表示、保存和回读规则见包根`skills/lody4dot/references/material-handoff.md`，源码为`skill/lody4dot/references/material-handoff.md`。这不代替本插件的Dot加载或Lody工具验收。

委派目标若是Work Cloud，先按包根`skills/lody4dot/references/collaboration.md`的“Work Cloud与任务创建”核对具体入口和实际返回类型；Dot云会话不一律视为Work Cloud，也不把Work的资料/插件能力套给Codex任务。下面的Codex准备路线仅适用于实际Codex环境。

| 当前条件 | 使用方式 | 需要单独验证 |
| --- | --- | --- |
| 已有合法Lody app/MCP连接 | 在已授予权限内复用实际提供的工具 | 真实工具名、目标workspace与只读查询；不猜内部MCP入口 |
| 可使用已准备的Codex云环境 | 让Dot在指定已发布环境创建云任务，按本包共享技能使用该端Lody CLI | Dot实际发起的任务、插件/源码版本及Lody原生引用；任务工作目录各自独立 |
| Dot当前执行器实际有Python/Node与合法凭证入口 | 按本端OS、prefix和身份边界做安装/检查 | 受管runtime当前仅支持Linux；不把另一台云机的安装回执套到此处 |
| 已明确连接到Dot的本地电脑 | 在本地任务中读取技能，使用该端已验证的工具 | Dot本地访问授权、电脑在线与桌面App运行；Codex连接和Work Sync不代替此授权 |
| 只有技能可读 | 用知识规划、整理引用和交接 | 不能报告Lody工具调用、控制或执行已通过 |

Dot可使用既有插件连接，连接和插件权限可在dots、ChatGPT、Work和Codex之间共享，仍受已授予权限与工作区控制约束。共享连接不表示浏览器已登录、本地电脑已授权、CLI登录文件可复制，或`LODY_CLI_TOKEN`会自动出现在每个执行器。

## 插件内容与安装候选

本包是skills及辅助脚本组成的原生Codex格式自包含包，不声明MCP服务器或预设Lody app ID。准确入口为`skills/lody4dot/SKILL.md`，协作规则在`skills/lody4dot/references/collaboration.md`；先确认实际产品界面是否送达并读取这些资源。

OpenAI帮助文档确认：有上传权限时，可在ChatGPT web的Admin console→目标workspace→Plugins→Add→Upload plugin上传ZIP；也可由管理员导入GitHub marketplace。个人账号、角色及产品界面的可用入口需以实际界面为准。已读取的[官方打包指南](https://developers.openai.com/plugins/build/plugins)支持现有兼容清单及用户运行setup的入口；其存在不能证明ZIP外层包装已被ChatGPT接受。导入、扫描、启用和实际技能调用仍须回执，不再沿用早期“完整指南当前无法读取”的访问结论。

本仓库源码的`plugin/lody4dot/`尚需builder收集外部技能。GitHub marketplace导入只读取源文件，不替你构建包；不能把这个未构建目录直接当完整插件source。当前先交付构建产物供候选导入，保持能力源码唯一。

MCP声明即使使用远程HTTPS，也可能使导入插件被标为Desktop only；`.app.json`引用不会自动移除该限制。本轮不通过加MCP声明来猜测web/Dot兼容性。需要新远程MCP或Sites托管时，先明确调用身份、权限、业务副作用和运维所有权，再单独实现与验收。

## 准备与恢复

在确认适用的Linux执行器，从包根目录使用[bootstrap](../scripts/bootstrap.py)。默认只检查；环境准备可显式`--prepare`，启动时可选择`--repair-missing`。这些入口不登录、不启daemon、不重发模型任务；安装位置和身份属于本端。

Lody`0.107.2`是已验证知识与默认可复现安装基线，不要求各执行器严格相同。实际版本不同或版本查询失败只warn；Node/OS、安装完整性及真实命令/身份/权限失败仍分别处理。inspect与启动bootstrap默认离线；只有显式`python3 scripts/doctor.py --prefix "$LODY4DOT_PREFIX" --profile inspect --check-updates --json`单次查npm latest，旧版或查询失败不自动升级，也不因此阻塞已有授权任务。

Dot的主动Reset会删除该Dot的上下文/会话/计划；这不是已核实的周期磁盘回收或存储reset hook。Dot自己的prepare/maintenance/磁盘重建hook仍无已读官方契约。Codex Cloud的已发布setup用于新任务、保存VM状态默认最多7天可恢复，这些规则也不直接套到Dot自己的电脑。依赖恢复与原Lody session/turn对账按共享协作参考执行。

来源：[Dot入门](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)、[Dot权限FAQ](https://help.openai.com/en/articles/20001529-dots-privacy-security-and-safety-faqs)、[Plugins](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)、[GitHub导入](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github)、[Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud)。
