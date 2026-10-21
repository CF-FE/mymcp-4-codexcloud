# lody4dot 宿主接入与生命周期核实记录

核实日期：2026-10-21（北京时间）。对应[C01任务卡](lody4dot-collaboration-tasks.md#c01-核实宿主契约与生命周期)。本文记录已读取的接口、源码和本实例观测；不替代[任务队列](../.codex/agent-state/todo.md)的进度，不宣称所有宿主已接入。

Dot按用户明确指定的ChatGPT云服务作为独立宿主。已取得的OpenAI来源使用Codex CLI、Codex Web等名称，尚不足以确定Dot的官方产品标识或将其等同于Codex云端。未取得Dot的安装、工具连接、凭证与存储生命周期契约时，不能生成Dot专用清单、MCP入口或重置事件名。

## 本轮复核结论

- 用户确认环境发布后，配置读取已无草稿，正式自定义网络规则包含三个OpenAI官方站点；现有安装和启动字段仍分别包含Lody安装/inspect、读取技能/inspect。
- 同轮运行状态为`observations_current=true`、网络`enforced`，但当前实例的`allowed_hosts`仍只有原有五条Lody规则，启动策略文件也没有三个OpenAI域名。配置发布记录与当前实例的实际应用分别取证。
- 经继承代理分别请求开发站、帮助站和官网一次，仍为`CONNECT 403 Forbidden`，页面正文未取得。这是当前访问路径的拒绝，不能据此推断Dot不存在、用户未发布或用户没有产品权限；本轮未重复保存草稿或要求再次发布相同配置。
- 允许访问的OpenAI官方GitHub源码已取得HTTP 200；当前`codex-cli 0.163.0`的版本、plugin及marketplace帮助均退出0。帮助读取伴随无法写PATH别名的只读警告；没有修改受保护配置、注册插件、登录或启动模型任务。

## 宿主、加载与工具能力

“资料已读”“CLI入口可运行”“控制端可用”“执行节点可用”分别记录。操作系统支持也与宿主插件支持分开；官方Codex可安装在某OS，不能证明lody4dot安装器已兼容它。

| 宿主/目标 | 加载与工具入口 | 身份及路径边界 | 准备、启动与恢复 | 本轮可支持的结论 |
| --- | --- | --- | --- | --- |
| 当前Linux托管Codex环境 | 已保存`start_skill`引导读取`skill/lody4dot/SKILL.md`；当前Codex有plugin/marketplace帮助，但受保护配置不能据此写入 | Lody身份通过既有安全变量和私密state使用；仓库和受管CLI路径由本实例记录定位 | `install_script`已有安装与inspect，`start_skill`已有读取与inspect；恢复和实际执行须另验 | 准备/启动入口存在且帮助可读；不证明新任务已读技能、原生注册成功或本实例可充当worker |
| 用户本地Codex CLI | 0.163.0源码定义原生清单、skills及marketplace路径；实际机器上的CLI版本、注册和新会话读取另验 | 使用该端有权访问的配置与安装prefix；用户电脑文件不因云端工具存在而可读 | 使用该端真实配置入口；如采用会话hook，还需核实版本、事件、管理策略及实际触发 | 可按已核实格式准备分发；不能从本云实例帮助通过推导用户电脑加载成功 |
| 其他Linux云机/本地Agent宿主 | 可复用知识源码和Linux安装路线作为候选；加载格式依目标宿主决定 | 自有可写prefix与独立私密state；不搬用另一实例的同名目录或登录态 | 核对目标平台实际准备/启动机制，分别验证依赖恢复、认证与任务对账 | 尚需目标OS/架构和真实宿主安装、读取及连接记录 |
| macOS宿主 | 官方README提供Codex安装入口；当前lody4dot安装器仍有Linux限制 | 本地可写路径、原生依赖与私密状态需在目标机器核实 | POSIX适配只能作为候选，不能以删除平台判断代替真实验收 | Codex官方安装说明不等于lody4dot已支持macOS |
| Windows/WSL2宿主 | 官方README提供Windows Codex入口；lody4dot原生Windows支持尚未建立，WSL2为独立Linux候选 | 需区分Windows与WSL文件系统、身份、权限和启动器 | 分别验证目标环境，不假定任意symlink、uid/0700或killpg行为适用于Windows | 不宣布lody4dot原生Windows或WSL2已通过 |
| Dot | 共享技能与交接语义可作为设计输入，实际技能/插件入口、shell或合法远程工具仍待官方契约确认 | 宿主用户、Lody账号和模型执行凭证分别授权；会话链接不转移全空间权限 | 准备脚本、会话事件、实例/存储重置规则均待核实；不套用另一产品的hook | 用户目标明确，官方接入调查仍有缺口；知识文件存在或人工交接不能写成完整工具接入 |

当前托管路径是该实例的定位事实，不是跨宿主统一路径。安装并不自动把该宿主注册为Lody machine；控制端发往已有远端节点的任务不要求控制端同时成为worker。

## 原生插件与技能契约

本轮重新读取OpenAI官方`rust-v0.163.0`源码：

| 项目 | 已确认内容 | 仍须单独验证 |
| --- | --- | --- |
| 原生清单 | `.codex-plugin/plugin.json`；`skills`接受字符串或数组 | 目标宿主允许注册、插件实际启用与新会话读取 |
| 资源路径 | 清单路径以`./`开头，相对插件根；禁止`..`、绝对/越界路径；未声明技能路径时使用存在的`skills/`目录 | 构建产物内容、移位后的资源完整性与实际读取 |
| marketplace | 本地source的`.`或`./`指marketplace根；非根相对路径须合法 | 对应目标机器的marketplace注册与加载，不通过受保护目录覆盖绕过限制 |
| hooks字段 | `RawPluginManifest`定义`hooks`字段 | 字段存在不等于目标事件已启用、宿主允许注册或会自动执行；本轮未新增hook配置 |

官方仓库`docs/skills.md`仅指向开发站技能页面；该目标网页仍未取得，不能将链接存在描述成已经读过完整技能文档。`docs/config.md`另记载管理员可在`requirements.toml`设置`allow_managed_hooks_only=true`，忽略用户、项目与会话hook配置而保留托管层hooks；本轮没有据此推断当前环境启用了该策略，也没有尝试覆盖它。

## 初始化、会话hooks与存储事件

| 层次 | 已取得的证据 | 对lody4dot的约束 |
| --- | --- | --- |
| 当前环境准备 | 配置字段和仓库`.codex/cloud-install.sh`均有锁定安装与离线inspect | 复用已有入口；准备依赖时不登录、不注册machine、不启动daemon。字段保存不是事件已触发的证明 |
| 当前Agent启动指引 | 配置`start_skill`与仓库`.codex/cloud-start.md`含技能读取和inspect步骤 | 它是Agent指引，不是操作系统事件回调；送达、读取及命令执行分别取证 |
| 官方Codex会话事件 | 固定提交的事件表列14类，包括`SessionStart`、`SessionEnd`、工具、压缩、模型请求、子Agent及中断等 | 只代表该源码提交定义的事件；不自动推广到当前托管服务、用户本地版本或Lody管理的Codex0.160.1 |
| `SessionStart`来源 | `startup / resume / clear / compact / fork` | `clear`是这里的会话启动来源标签，不是磁盘清理或实例重置通知 |
| `SessionEnd` | teardown事件，默认超时1秒、最大3秒 | 不作为长时间安装、完整备份或突发实例丢失前必达通知 |
| Dot存储重置、setup/maintenance与回收绑定 | 本轮尚未取得对应官方页面或产品契约 | 不确认重置周期、保留目录、重置前后事件或maintenance触发时机；不创建虚构hook |

准备、运行身份、业务恢复和worker启动须分别处理。建议的依赖准备与恢复流程仍按[开发方案](lody4dot-collaboration-development.md#6-初始化hooks与存储恢复)：准备阶段幂等安装，运行入口先检查、缺失时按所属prefix修复，任务过程中保存必要关联和成果，恢复后按原session/turn查询对账。即使没有退出通知，也不能自动重发未知是否已受理的任务。

若后续取得适用的正式hook，复用同一初始化动作作为触发目标；不要把Lody登录、主机注册或恢复模型执行塞进所有会话启动。当前受保护配置没有因此变成可写，也不因文件里出现hook字段就声称已挂钩。

## 证据来源与读取范围

以下源码均于2026-10-21重新读取，HTTP 200。固定提交为`c7234c1174b27d9c55199fba0d546dc27d1b0415`；插件格式另以与本机CLI匹配的官方标签`rust-v0.163.0`核对。源码描述契约，真实加载/任务仍需运行回执。

| 来源 | 直接支持的结论 |
| --- | --- |
| [官方README](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/README.md) | 使用Codex CLI、Codex Web等名称；提供Codex各平台安装说明。没有据此确立Dot的官方身份 |
| [技能索引](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/docs/skills.md) | 指向开发站技能文档；本页不是完整安装契约 |
| [配置索引与管理策略](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/docs/config.md) | 开发站配置文档入口与managed-hooks-only规则 |
| [插件清单解析](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs) | skills、hooks字段及清单资源路径检查 |
| [技能根加载](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/loader.rs) | `plugin_skill_roots`、默认skills目录 |
| [marketplace本地路径](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/marketplace.rs) | 本地source路径解析规则 |
| [会话事件表](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/codex-rs/hooks/src/lib.rs#L23) | 固定提交中14类事件，不能作为Dot平台回收事件清单 |
| [SessionStart](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/codex-rs/hooks/src/events/session_start.rs#L23)、[SessionEnd](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/codex-rs/hooks/src/events/session_end.rs#L20) | 会话启动来源及结束时限 |

发布后单次访问记录：

| 请求 | 结果与范围 |
| --- | --- |
| `https://developers.openai.com/codex/cloud/environments/` | 继承代理的CONNECT403，未读到页面，不能声明已经核实setup/maintenance的具体契约 |
| `https://help.openai.com/en/?q=Dot` | 同上，未完成官方帮助站Dot检索 |
| `https://openai.com/sitemap.xml` | 同上，未读取官网索引 |

没有绕过代理、修改CA/TLS、重新保存网络草稿或读取凭证值。公开文档不保存真实宿主实例、Lody资源标识或业务数据。

## C01剩余输入与下一动作

当前可交给实现使用的部分是：已有托管准备/启动字段、0.163.0原生分发格式、当前CLI帮助入口，以及会话hook与存储事件的严格区分。它们可以支持C02/C03和已知宿主的分发准备。

Dot实际产品/接口、官方setup/maintenance与实例恢复契约、首批用户本地OS/架构及真实加载回执仍有缺口。后续在当前实例收到正式网络规则或获得相应官方资料后再复查相关页面；无需重复发布同一配置。取得宿主契约后执行最小读取/只读工具核验，再决定C05/C09路线。若需要新增MCP服务，按任务卡先明确身份映射、副作用与运维所有权，调查阶段不部署。
