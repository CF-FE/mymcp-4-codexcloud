# lody4dot 宿主接入与生命周期核实记录

核实日期：2026-10-21（北京时间）。对应[C01任务卡](collaboration-tasks.md#c01-核实宿主契约与生命周期)。本文记录已读取的官方契约和本实例观测；进度见[任务队列](../../.codex/agent-state/todo.md)。资料可读、入口存在、实际安装和真实加载分别取证。

## 本轮结论

Dot的官方身份已核实：[Getting started with your dot](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)将其称为“an always-on agent in ChatGPT”，并明确拥有自己的cloud computer。本文把Dot作为具体产品与宿主建模；Agent仍是参与任务的主体类别。Dot、Dot自己的云电脑，以及它创建的Codex云任务是不同对象。

已读Dot、Codex Cloud、插件和技能的官方帮助页；spec12发布后又读到完整插件格式与Dot电脑指南，补齐了portable/兼容清单、GitHub source和用户运行setup的契约。**仍未取得Dot自身云电脑的准备脚本、maintenance、定期磁盘重置或重建hook契约**。官方`onboardingSkill`是用户运行setup的入口，不能当作这些生命周期事件。

环境发布与访问证据如下，旧实例结果不再作为当前状态：

| 轮次/时间 | 配置、访问与范围 |
| --- | --- |
| 较早发布轮次 | 正式规则已有三个OpenAI域名、无草稿，但该次运行状态及策略快照仍只有五条Lody规则；三个官网请求均在继承代理处CONNECT403。它是当时实例的历史观测 |
| spec9历史轮次，14:46起 | spec/observed为9，正式无草稿；`observations_current=true`，网络策略为`unknown`，`/etc`网络快照已有三个OpenAI域名；帮助站9篇正文及官网索引HTTP200，开发站环境指南与Plugin Management仍CONNECT403 |
| 当前正式配置，spec12 | 正式源码`ed9096b`、插件0.2.1；spec/observed均为12、`observations_current=true`，无待发布草稿。网络与运行变量readiness仍为`unknown`，不据配置快照填成ready/enforced |
| spec12实际HTTPS，16:59–17:01 | 下列4篇完整指南均HTTP200，包括Plugin Management和开发站插件包装指南；这更新了旧轮次对这些精确URL的访问结论，不证明其他路径或UI操作通过 |
| spec12 Cloud CLI | `codex cloud list`从旧轮次代理拒绝变为HTTP401；本地`codex login status`显示ChatGPT登录，但Cloud API本次未授权。未取得可用Cloud ENV_ID，不猜原因或提交任务 |

本节资料查证保留继承代理、CA与TLS校验，没有修改云配置、重复保存草稿、认证、读取凭证值或安装新插件；发布后原Lody任务的独立只读复验见验证记录。当前工具目录没有网页检索或官方文档搜索工具，采用官方帮助站搜索及页面实际链接做有限查证。

## 宿主、加载与工具能力

操作系统支持与插件加载支持分开；官方Codex能安装在某OS，不证明lody4dot安装器兼容该OS。

| 宿主/目标 | 加载与工具入口 | 身份及路径边界 | 准备、启动与恢复 | 当前结论 |
| --- | --- | --- | --- | --- |
| 当前Linux托管Codex环境 | 已保存`start_skill`引导读取`skill/lody4dot/SKILL.md`；当前CLI有plugin/marketplace帮助 | 使用本实例允许的仓库、prefix和私密state；受保护配置不因此变成可写 | `install_script`已有安装/inspect，`start_skill`已有读取/inspect | 已有配置和CLI入口；新任务读取、原生注册、worker执行仍各需回执 |
| Codex Cloud任务 | 官方要求先准备并发布环境；Dot可在已有Codex环境创建云任务 | 每任务独立workspace和工作文件；共享环境不自动共享他人的任务、编辑权或GitHub仓库权限 | 已发布setup用于新任务；已有任务保留自身状态；VM恢复窗口见下表 | 可复用已核实环境接入路线；不能把一个任务的工具证明成Dot自身云电脑工具 |
| 用户本地Codex CLI | 0.163.0源码定义原生清单、skills和marketplace；目标端版本与注册另验 | 使用该端授权配置、安装prefix和私密状态 | 采用目标端实际加载入口；会话hook还受版本和管理策略限制 | 可准备匹配格式的分发，不声称用户电脑已加载 |
| Dot自身云电脑 | 官方确认独立cloud computer，可使用共享的插件连接；企业设置分别控制云浏览器、code/shell联网和桌面使用 | Dot拥有者、工作区角色、连接服务账号、动作权限分别约束；不自动继承本地VPN、浏览器登录或设备策略 | 官方称电脑可在使用间隔保留状态，拥有自己的文件、软件和浏览器会话；未给永久保留、重置周期或setup/maintenance、重建hook契约 | 产品与部分工具能力已确认；lody4dot在该电脑的CLI安装、技能读取及执行位置尚未实测 |
| Dot连接的本地电脑 | 通过该电脑的ChatGPT桌面App连接并Allow access后，可创建Work/Codex任务、使用local skills | 连接Codex或开启Work Sync不等于授权Dot；本地访问默认关闭 | 电脑需在线且App打开；本地工作在单独任务；切换选择不会搬迁已有任务 | 官方支持本地技能路径的产品能力；lody4dot加载格式和目标机实际读取仍待回执 |
| 其他Linux、macOS、Windows/WSL2宿主 | 知识与协议可复用，加载格式依宿主；当前受管安装器有Linux边界 | 每端独立prefix、私密state与凭证；Windows和WSL文件系统分开核实 | 分别验证依赖、路径、权限和进程行为 | 不从Codex各OS安装说明推导lody4dot跨平台安装通过 |

控制端不必同时成为Lody worker。安装CLI不自动注册Lody machine；能发送任务给远端节点，不代表当前宿主具备执行模型任务的凭证和进程条件。当前CLI/工具存在本身也不能确定运行于Dot自身电脑还是Dot创建的Codex任务。

## 插件、技能与连接：可用路线及限制

| 路线 | 已读官方契约 | lody4dot适用边界 |
| --- | --- | --- |
| Portable与Codex兼容插件 | 新包推荐根级`plugin.json`和`skills/`；`.codex-plugin/plugin.json`仍作为兼容fallback受支持。兼容清单skills以`./`相对插件根，禁止越界；portable自动发现根级`skills/` | 正式0.2.1继续使用已核实的兼容格式；本轮0.2.2候选只增加用户运行setup入口，暂不迁移portable清单。注册、启用和新会话读取另验 |
| ChatGPT插件/技能 | 插件可含skills、apps或两者；技能可上传/创建/分享，受套餐、工作区和产品界面限制；ChatGPT与Codex的技能安装/同步和管理可以不同 | 可以准备共享内容；不能把Codex已加载推导成Dot或ChatGPT技能已安装 |
| 插件ZIP上传 | 官方帮助给出管理员/有上传权限者在web的Plugins → Add → Upload plugin入口；完整指南确认portable/兼容包布局，但未规定ZIP包装层级 | 自包含包仍是候选；压缩包根层接受、上传扫描、UI安装与实际加载尚未验证，目录校验不能替代这些结果 |
| GitHub marketplace导入 | Source是仓库URL，Path是包含清单的目录，可选branch/tag/commit；支持Codex/Claude marketplace与独立Claude清单，条目可引用native、Claude、Agent Plugins 1.0或受支持技能包 | 本地source.path相对所选marketplace根；另支持`url`和`git-subdir`来源。导入不运行builder、不连接账号或授予app权限，不能将未构建的`plugin/lody4dot/`直接作为完整source |
| 用户运行插件setup | 可选`extensions.com.openai.onboardingSkill`指向包内技能；兼容清单也使用相同嵌套字段，路径从插件根解析 | 用户运行setup才调用技能，不是自动安装脚本或Dot重置hook。0.2.2候选已采用；实际界面入口与调用另验 |
| 声明MCP的导入插件 | 官方说明`mcp.json`/`.mcp.json`等MCP声明可能令插件标为Desktop only，即使服务器是remote HTTPS；添加`.app.json`引用不自动去掉此标签 | 不能把Codex/桌面MCP清单直接视作Dot/web通用包；已有app引用也不绕过限制 |
| ChatGPT custom MCP app | 官方入口Plugins → + → Add custom MCP server；公共HTTPS或支持的Secure MCP Tunnel；需认证、扫描/检查工具及相应角色权限。本地stdio不能直接供web使用 | 为无shell宿主提供候选控制面。full MCP限Business/Enterprise/Edu；Pro自定义MCP限read/fetch；不能据此承诺Pro可提交Lody任务 |
| ChatGPT Sites承载MCP | 可在Site承载MCP并生成插件；需要Sites及插件权限，Site拥有者发布；安装、连接、Site访问分别处理 | 是另一正式托管候选，仍需服务接口、身份映射、部署所有权和端到端验收；本轮未部署 |

Dot官方FAQ明确：**“Plugin permissions are shared across dots, ChatGPT, ChatGPT Work, and Codex.”** 已有连接可供Dot在授予范围内使用。因此，不能笼统写成跨产品连接和权限始终完全隔离；也不能反向理解为任意产品可访问全部任务、文件或工作区。插件可用性、skills管理、实际工具暴露、服务端ACL、读写动作和审批、Lody账号及模型执行凭证仍需分别核实。

原生清单的`hooks`字段已经官方源码确认，但字段存在不证明对应事件已启用或当前宿主允许注册。新读包装指南把lifecycle hooks限定为手动安装于Codex desktop的插件，含此类hooks的插件不能进入公共插件目录；web安装不会部署hook脚本，非托管hooks还需用户审阅并信任。`docs/config.md`另说明管理员可设置`allow_managed_hooks_only=true`；未据此推断当前环境启用了该设置。

## Portable格式与用户运行setup

[Package your plugin](https://developers.openai.com/plugins/build/plugins)推荐的根级`plugin.json`使用`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`，并声明`name`、`version`、`description`；根级`skills/`自动发现，无需portable `skills`字段。原文明确：“Existing `.codex-plugin/plugin.json` files remain supported as a compatibility fallback.” 因此本轮无需为有效性强制迁移正式0.2.1。

若使用portable清单，`extensions.com.openai`对象会整体替换`.codex-plugin/plugin.json`提供的OpenAI overlay，两者不合并；root identity和portable components仍以根级清单为准。本轮0.2.2候选保留兼容清单，只加入以下可选字段，setup技能源码仍由builder收集：

```json
{"extensions":{"com.openai":{"onboardingSkill":"./skills/lody4dot-setup/SKILL.md"}}}
```

该字段相对插件根，必须指向随包提供的技能。官方原文：“When users run setup, it invokes the skill in a new conversation, or in the existing conversation if they installed the plugin during that conversation.” 因此验收需分别记录用户运行setup、新会话/当前安装会话的入口与实际读取。它不承诺安装时自动执行，也不提供Dot电脑reset通知；候选构建、上传、安装及实际调用分别取证。

## 初始化、存储与会话事件

| 对象/事件 | 已取得的契约 | lody4dot约束 |
| --- | --- | --- |
| 当前环境准备和Agent引导 | 现有`install_script`与`.codex/cloud-install.sh`锁定安装/inspect；`start_skill`与`.codex/cloud-start.md`引导读取/inspect | 复用已有入口，准备依赖时不登录、不注册machine、不启动daemon；保存字段与实际触发分别取证 |
| Codex Cloud新旧任务 | 官方帮助明确新任务独立workspace；发布setup更新用于新任务，原任务继续保留自己的状态 | 环境发布、新任务创建、原任务恢复分开处理；新任务不能找回另一任务未提交修改 |
| Codex Cloud VM状态 | 官方默认自最近turn启动或任务resume起，保存的VM状态最多可恢复7天；这不是会话历史保留期 | 只适用于该文档中的Codex Cloud，不当作Dot自身磁盘重置周期、永久保留承诺或退出通知 |
| Codex会话hooks | 固定提交定义14类事件；`SessionStart`来源为`startup/resume/clear/compact/fork`，`SessionEnd`默认1秒、最多3秒 | `clear`不是磁盘清理；结束hook不适合完整备份或长安装，也不保证突发实例丢失前到达；不能推广为Dot存储事件 |
| 插件用户运行setup | `extensions.com.openai.onboardingSkill`声明包内技能，用户运行setup时在新会话或当前安装会话调用 | 可引导显式诊断和依赖准备；不是安装自动执行、Cloud环境prepare或Dot存储reset hook |
| Dot主动Reset | 官方说明用户Reset删除Dot及其会话、保存记忆和定时任务；另页说明Dot创建在其他位置的文件、Codex threads和ChatGPT conversations单独存储 | 产品删除操作与云电脑文件系统周期重置分开；不同位置按各自保留规则处理，不能把全部产物视作随Dot一起删除 |
| Dot自身电脑状态与重建 | 新指南说“the computer can keep its state between periods of use”，但未给准备、maintenance、周期存储重置或重建hooks契约 | 承认可跨使用间隔保持状态，不扩展成永久存储保证、已知重置周期、保留路径或重置前后回调 |

建议流程仍按[开发方案](collaboration-development.md#6-初始化hooks与存储恢复)：幂等准备依赖；运行入口检查，缺失时只修复所属prefix；持续保存任务关联及成果；恢复后按原session/turn查询对账。未知是否已受理的任务不自动重发。未来若取得适用hook，将其作为同一恢复入口的额外触发源；业务身份、模型执行与worker启动仍单独授权和验证。

## 官方证据与读取范围

下列9篇帮助正文均通过继承代理正常HTTPS读到，HTTP200，时间为2026-10-21 14:47–14:54北京时间。帮助页会更新，引用只证明读取时内容；未执行页面中的安装、连接、分享或发布操作。

| 官方URL | 支持的事实 |
| --- | --- |
| [Getting started with your dot](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot) | Dot身份、自身cloud computer、连接本地电脑/local skills、创建Codex云任务、任务原位置与主动Reset |
| [Manage dots in ChatGPT workspaces](https://help.openai.com/en/articles/20001554-manage-dots-in-chatgpt-workspaces) | Enterprise访问、cloud code/shell联网/浏览器/桌面权限、本地电脑授权与连接限制 |
| [Dots privacy, security, and safety FAQs](https://help.openai.com/en/articles/20001529-dots-privacy-security-and-safety-faqs) | 跨产品共享插件权限/连接；Dot上下文与外部产物保留边界；委托也受动作规则约束 |
| [Using Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud) | 独立任务workspace、已发布setup对新任务的作用、默认7天VM恢复窗口、共享环境与GitHub权限 |
| [Plugins in ChatGPT](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt) | 插件组成、安装/授权分开、skills与apps、workspace和产品界面限制 |
| [Importing and syncing plugin marketplaces from GitHub](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github) | marketplace路径/来源/同步、现有app引用、MCP声明与Desktop only限制 |
| [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) | 技能创建/上传/分享入口、角色权限、ChatGPT与Codex可分别管理 |
| [Connecting custom MCP servers in ChatGPT](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt) | HTTPS/Tunnel入口、套餐和角色范围、认证与工具更新审核、本地服务限制 |
| [Hosting a plugin with ChatGPT Sites](https://help.openai.com/en/articles/20001547-hosting-a-plugin-with-chatgpt-sites) | Site承载MCP、拥有者发布、安装/连接/分享条件 |

spec9历史轮次14:58:23（北京时间）请求Plugin Management曾CONNECT403。spec12配置发布后，按继承代理、CA和TLS重新读取该精确URL及正文链接，取得以下4篇HTTP200；旧拒绝不再代表这些页面当前不可读。正文只证明所列契约，ZIP/UI回执仍单独验收。

| 官方URL | HTTP与读取时间（北京时间） | 本轮新增事实 |
| --- | --- | --- |
| [Plugin Management](https://learn.chatgpt.com/docs/enterprise/plugin-management) | 200，2026-10-21 16:59:11 | marketplace目录与source/path、支持的包格式、GitHub来源及MCP/Desktop only边界 |
| [Package your plugin](https://developers.openai.com/plugins/build/plugins) | 200，2026-10-21 17:01:20 | portable/兼容清单、overlay优先级、用户运行onboardingSkill、lifecycle hooks适用范围 |
| [Dot computers and apps](https://learn.chatgpt.com/docs/dots/computers-and-apps) | 200，2026-10-21 17:01:20 | 电脑可在使用间隔保持状态；云电脑、连接本地电脑、插件与权限的分别约束 |
| [Getting started with your dot](https://learn.chatgpt.com/docs/dots/getting-started) | 200，2026-10-21 17:01:20 | Dot入口、独立连接及任务委托；未列环境准备或存储重置hook |

Plugin Management的Codex本地条目可使用`{"source":{"source":"local","path":"./plugins/team-tools"}}`，路径相对用户所选marketplace根，而非`.agents/plugins/`目录。`url`用于GitHub仓库根插件，`git-subdir`另指定仓库与子目录；Git来源可固定`ref`或40字符`sha`。这些schema不改变本仓库需先构建为自包含包的约束，也不确定ZIP是否接受额外外层目录。

spec9官方搜索包括`Dot`、`dot cloud computer storage reset`、`dot hooks setup maintenance`、`dot cloud computer files retention`、`dot environment setup hook`及`skills in ChatGPT`；检索未命中不作为“没有hook”的证明。Codex Cloud正文把完整设置流程指向[开发站环境指南](https://developers.openai.com/codex/environments/cloud-environments)，其完整正文仍未读取；本轮开发站插件包装页HTTP200不能替代该页或Dot专属hook契约。

官方Codex源码均于同日取得HTTP200。固定提交为`c7234c1174b27d9c55199fba0d546dc27d1b0415`；插件格式另按本机CLI匹配标签`rust-v0.163.0`核对：

| 来源 | 支持的事实 |
| --- | --- |
| [官方README](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/README.md)、[技能索引](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/docs/skills.md)、[配置与管理策略](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/docs/config.md) | Codex命名、安装入口、开发站链接及managed-hooks-only规则；Dot身份改用上方官方帮助核实 |
| [插件清单](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs)、[加载](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/loader.rs)、[marketplace](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/marketplace.rs) | 原生skills/hooks字段、资源路径及本地source解析 |
| [事件表](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/codex-rs/hooks/src/lib.rs#L23)、[SessionStart](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/codex-rs/hooks/src/events/session_start.rs#L23)、[SessionEnd](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/codex-rs/hooks/src/events/session_end.rs#L20) | 会话事件、来源及时间限制；不是Dot存储事件清单 |

本机`codex-cli 0.163.0`版本、plugin及marketplace帮助退出0，伴随无法写PATH别名的只读警告；只作为该实例的命令旁证。spec9公开正文临时保存在`/tmp/lody4dot-official-new-runtime-9ns1poig/`，spec12四篇正文及时间记录在`/tmp/lody4dot-plugin-contract-spec12-1ayrw7mx/`；临时路径不是交付依赖或持久存储承诺，正文与环境数据未提交。

## C01/C09可交付范围与剩余核实

C01已补齐Dot正式身份、独立电脑与Codex委托关系、共享连接权限、Codex Cloud恢复边界、portable/兼容清单及用户运行setup契约。C09可分别验收：skills-only插件与setup、Dot使用已授权连接、Dot委托已有Codex环境、连接本地电脑后的本地技能。每条路线都需记录实际界面、执行位置、版本/来源、技能读取和工具回执，不能互相替代。

未完成部分集中在：Dot自身电脑能否按公开入口安装该CLI/技能；其存储生命周期及初始化/重建hook；所选账号/角色是否具备候选连接能力；lody4dot真实端到端验收。完整Codex Cloud setup/maintenance的下一官方核实点是上方已被正文引用的开发站指南；Dot专属hook仍需正式产品契约，当前不再反复要求用户找链接或发布同一配置。C01保留部分完成，C09不声明Dot完整接入。
