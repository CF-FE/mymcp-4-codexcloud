# lody4dot

为 Agent 提供 Lody 的任务指引、版本化命令资料、多宿主交接规则、资料交接指引，以及独立的安装、只读诊断、显式认证、依赖初始化和离线交接校验工具。源码清单版本为`0.2.5`；历史正式云来源与当前任务工作副本分开记录。2026-10-25按用户授权改为准备阶段解析官方npm的`lody@latest`，本轮源码锁及实际帮助为`0.108.1`，0.107.2历史业务证据不改称新版已测。首个已验证安装目标是Linux Codex云环境，工具需要Python3.10+、npm及受支持的Node：`>=22.14.0 <23`或`>=23.6.0`；实际依赖另以engine-strict核对。

核心能力源码在仓库的 `skill/lody4dot/`，薄setup入口在`skill/lody4dot-setup/`；本目录负责组合、运行时锁定和分发，不新增 MCP 服务。Lody 已有 MCP 只有在宿主提供有效 session/workspace/machine 上下文时才使用，不能将其内部入口当作独立通用服务。

多宿主知识与工具基础已提供，具体宿主的加载、控制与执行能力仍分别验收。OpenAI官方确认Dot是ChatGPT中的always-on agent产品，有自己的云电脑；它也能向预先配置的Codex云环境创建任务，或使用另行授权连接的本地电脑。这些执行位置分别核对，Dot不作为任意Agent的通用别名。macOS、WSL2和原生Windows未因此进入本插件实际安装支持列表，安装成功也不自动注册machine或启用worker。

## Dot与其他宿主如何接入

先读取共享技能，再按实际可用入口选择；完整规则见随包的[Dot接入指引](hosts/dot.md)。

| 当前条件 | 最小路线与边界 |
| --- | --- |
| Dot已有合法Lody app/MCP连接 | 在已授予权限内复用实际工具；不因换产品重复授权，也不推导具备全部写权限。 |
| Dot可使用已准备的Codex云环境 | 委托该已发布环境创建云任务，在任务中读取共享技能并使用该端CLI；任务与Dot自有云电脑分开。 |
| Dot当前执行器实际具备CLI前提 | 按该执行器的OS、工具和合法身份入口安装/检查；另一台机器的成功不能替代本端证据。 |
| Dot连接的本地电脑 | 需该电脑单独Allow access、在线且桌面应用运行；local skills需该连接，Codex连接或Work Sync不能代替。 |
| 只有知识可读 | 可规划与交接，工具调用、派发和执行保持未验证。 |

Dot、ChatGPT、ChatGPT Work和Codex可共享插件连接及已授予权限；技能安装/管理与具体工具暴露仍可能按产品区分。共享连接不复制浏览器登录、本地文件访问或模型凭证。本轮优先复用上述入口，不先部署MCP或Sites服务。

0.2.4补充Work Cloud与Codex Cloud的选择、文件能力条件及创建/触发/运行证据，统一见包根`skills/lody4dot/references/collaboration.md`的“Work Cloud与任务创建”。Work Cloud不自动继承Codex准备环境或本地STDIO；知识可读不证明本插件已在Work加载，业务MCP动作也不提供平台任务创建入口。此候选不新增Work适配器或改变受管runtime支持范围。

## 资料交接与任务结果

0.2.3增加随包的资料交接参考，由共享技能按需导航。对已确认可用且获授权的Dot资料中转直接复用；需要Lody节点发现、派发和观察时才组合Lody路线。分别记录原附件/正文/摘要、处理结果、保存回执和目的地回读；保存成功而回读受阻时保留两项事实，不盲目重复上传或替换对象。当前云任务不派生独立Codex云任务，任务创建由Dot承担。

纯Cloud/Space资料记录不填入schema1的Lody引用，也不送给`handoff.py`冒充Lody业务结果。真实Lody部分仍使用原校验器；本次不增加JSON字段、schema2、远程桥接或工具调用入口。知识导航、分发检查不证明Dot实际加载或新的业务读写已验收。

## 从仓库安装 CLI

在仓库根目录执行：

```bash
if [ -x /workspace/.tools/lody4dot-node/current/bin/node ]; then
  export PATH="/workspace/.tools/lody4dot-node/current/bin:$PATH"
fi
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot --json
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --json
/workspace/.tools/lody4dot/bin/lody --version
```

安装器每次在自有暂存目录定向运行`npm update lody --package-lock-only`解析官方latest，保留其余锁约束和reviewed override，再按得到的精确锁执行`npm ci`或复用同锁运行时。更新与安装均启用engine-strict、禁用生命周期脚本并核对官方registry来源；帮助/native模块验证成功后切换稳定入口。latest解析或真实安装失败不会静默用旧锁冒充更新成功。它不登录、不注册机器、不启动daemon；失败保留旧入口与用户状态，不提交工具目录、npm缓存或登录态，也不覆盖陌生非空目录。

`runtime/package.json`请求`latest`，源码lock精确记录本轮`0.108.1`；未来latest以当次解析与安装收据为准。已有CLI版本不必严格匹配，诊断中的版本差异或查询失败只提示，不触发重装或升级。安装锁/摘要/来源完整性、OS/Node支持和依赖实际可用性仍独立检查。安装成功与inspect通过不代表账户、长连接或Agent任务已经验证。

上述Node路径属于本任务受管runtime，本轮实际Node`24.22.1`、npm`11.19.1`；平台`/opt`内建Node未改。新launcher与doctor使用安装收据的`node_path`，不因PATH变化退回旧解释器。其他宿主核对自己的路径。源码和当前任务文件变更没有保存或发布环境模板，也没有更新固定ref。

## 可选更新检查与版本提示

默认inspect和启动bootstrap保持离线。需要知道npm当前latest时，在仓库根目录显式运行：

```bash
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --check-updates --json
```

这是对官方npm latest的单次查询，最多5秒，不安装、不切换CLI、不自动升级，也不在查询失败后反复重试。独立包使用`python3 scripts/doctor.py`及同样参数。`checks`中名为`cli_updates`的检查，其`evidence.observation`有三类warn：

| warn情况 | 含义与后续 |
| --- | --- |
| `update_available` | 实际CLI低于查到的latest，有更新可选；继续当前任务，是否升级单独决定。 |
| `comparison_unknown` | 无法可靠判断是否落后，例如实际版本未知、比latest更高或含prerelease；不推断过期或不兼容。 |
| `unavailable` | npm latest查询失败或不可用；保留已有CLI，不推断它过期或不可用。 |

实际版本与基线不一致时，`cli_version`也只warn；版本探测失败时，`runtime`的warn只表示入口存在，未证明版本命令执行成功。仍可按实际命令帮助和返回继续任务，不据此拒绝执行。查到与latest相同则为`current/pass`；更新和版本提示不进入`verified_scope`，不增加业务能力证明。

这些提示本身不改变成功退出码：其他必要检查通过时仍退出0；版本不同也不构成“语义不兼容”的证据。真实命令、身份/权限、Node/OS、依赖或安装完整性失败仍保留原有错误码和分类，`control/task/worker`所需证据不会被版本warn替代。参数或输出确实不兼容时，按实际错误核对帮助与适配，不按版本号预先拦截。

## 环境准备与恢复检查

### 安装后运行 setup

0.2.2候选在兼容清单`.codex-plugin/plugin.json`中声明官方`extensions.com.openai.onboardingSkill`，从插件根指向`./skills/lody4dot-setup/SKILL.md`。它用于用户安装后主动运行setup时，引导Agent识别实际执行位置，选择已有工具或检查/准备本端依赖；通用知识仍由核心技能维护。包内入口可移位，源码入口为`skill/lody4dot-setup/SKILL.md`。

官方说明setup会在新对话，或安装发生的现有对话中调用技能。两种平台原生调用均须实际验收，本仓库构建通过不代替UI安装或调用。它不是安装时自动执行，也不是环境准备、存储重置或每次任务启动hook。当前0.2.1正式环境已有bootstrap入口，无需为这个候选重复发布或重配token。依据见[官方打包指南](https://developers.openai.com/plugins/build/plugins)。

### 依赖准备与启动检查

`bootstrap.py`复用现有受管安装器和doctor，把准备阶段与启动检查分开。在仓库根目录运行；下面prefix示例用于当前Linux云实例，其他端必须使用自己的实际安装位置：

```bash
python3 plugin/lody4dot/scripts/bootstrap.py --prefix /workspace/.tools/lody4dot --prepare --json
python3 plugin/lody4dot/scripts/bootstrap.py --prefix /workspace/.tools/lody4dot --json
python3 plugin/lody4dot/scripts/bootstrap.py --prefix /workspace/.tools/lody4dot --repair-missing --json
```

| 入口 | 行为 |
| --- | --- |
| `--prepare` | 在暂存目录解析官方latest、受管安装或同锁复用，再离线inspect。 |
| 不传动作参数 | 只做inspect；缺运行时也不自动安装。 |
| `--repair-missing` | 先离线inspect，仅在退出3且类别为`missing_runtime`时进入同一latest安装路线，再复检；目录所有权和来源检查仍由安装器执行。 |

`--prepare`和`--repair-missing`不能同时使用。检查阶段的版本差异或探测失败只提示，不触发安装或升级；Node/OS不支持、来源完整性等实际错误也不被当作缺失自动修复。陌生或被修改的安装目录不会被当作可覆盖目录。报告的`verification_scope`为`owned_dependency_readiness`，`authentication`、`daemon`和`task_recovery`均为`not_run`：此工具不登录、不启daemon、不恢复或重发模型任务，调用方既有身份state保持独立。安装阶段会解析latest；inspect本身不联网查更新。

已有环境准备入口可调用`--prepare`，运行入口可选择只检查或明确允许的`--repair-missing`。这不表示Dot支持存储重置hook。初始化后仍需核对本端身份与原Lody session/turn，再决定如何处理业务；详见包内`skills/lody4dot/references/collaboration.md`（源码为`skill/lody4dot/references/collaboration.md`）。

Codex Cloud官方说明：已发布setup更新用于新任务，已有任务保留自身状态；保存VM状态默认从最近turn启动或任务resume起最多可恢复7天。这不是会话历史保留期，也不是Dot自有云电脑的磁盘重置规则。Dot文档中的Reset是主动删除Dot的产品操作，尚无已读官方依据可注入Dot云电脑初始化hook。

## 离线交接校验

先将本任务的必要目标、授权声明、原生引用、版本与观察整理到私密JSON文件，再检查相应阶段：

```bash
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage intent --json
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage dispatched --json
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage result --json
```

阶段是字段检查级别，不会创建或改变任务。工具只读取指定的普通JSON文件，不跟随输入文件的符号链接，不打开记录内引用、不访问网络、不调用Lody、不改写输入。`status: pass`仅表示`structure_and_declared_consistency`通过；报告始终保留`not_verified`，不能证明实时权限、来源真实性、实际产物或业务完成。已完成/失败/取消的声明都可能在结构完整时通过，不能把退出0当任务成功。

输入/结构不合法退出2，缺少阶段所需证据退出3，结构及声明一致性通过退出0，内部错误退出10。未知根字段、重复JSON键、不有限数字和可识别的秘密输入会被拒绝，扫描范围仍仅是已知模式。随附技能参考包含协作规则；工具的`--help`列出实际阶段与参数。完整记录须由调用方根据实际原生回执准备，工具不会生成或补造业务证据。

## 认证与云端运行

复用环境中安全注入的 `LODY_CLI_TOKEN`；不要在聊天、命令文本或日志中复制值。此名称是本插件约定，Lody CLI 不会因此自动登录。新身份先使用本任务私有的状态目录；`mktemp -d` 在此创建权限为 `0700` 的目录。需要验证已有登录时，改用该身份原有的私有 `LODY_DATA_DIR`，不创建新目录替代它。先只读验证；需要登录时再显式执行最后一条：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
python3 plugin/lody4dot/scripts/auth.py --prefix /workspace/.tools/lody4dot --verify-only --json
python3 plugin/lody4dot/scripts/auth.py --prefix /workspace/.tools/lody4dot --login --json
```

登录会保存本机身份，须单独核对本次授权。0.108.1源码审查显示API-key分支验证已有token并保存本机身份；配对会exchange，设备授权会创建远端CLI key，不能混入只允许临时本地身份的范围。本轮只有source_verified，没有运行新版认证。CLI仍无已核实的`LODY_CLI_TOKEN`直读或无状态目录flag；目录依赖已有credentials和SQLite，不自造HTTP认证层。受支持入口通过子进程argv接收凭证，适配器不经shell展开也不输出值，但同用户进程仍可能读argv。凭证存在、登录、工作区权限和底层Agent凭证分别验证。

`0.107.2` 的 `session create/chat/cancel` 按目标区分运行前提：本机目标需要本机运行进程，远端可由控制端经机器 RPC 派发，无需控制端启动 host/daemon；执行端仍需运行进程、Agent 配置及凭证。取消返回 `alreadyStopped` 不证明本次取消了运行回合。`agent-config refresh-capabilities` 仍针对本机，不能套用远端派发规则。只读查询和请求被接受均不能单独证明任务完成。

保留继承的代理与 CA，不关闭 TLS 校验。官网资料使用 `lody.ai`；npm 下载及 CLI 的登录、API、观察链路还需各自网络权限。`convex.lody.ai`、`backend.lody.ai`、`api.lody.ai` 是当前发布物中的服务目的地，仍应按真实连接结果分别确认。配置已保存或官网能访问均不是全部网络通过的证据。

登录后的账户查询与目标工作区目录是两条连接链路。检查目录时显式指定目标；只查询工作区列表不会证明机器目录可用：

```bash
python3 plugin/lody4dot/scripts/doctor.py --profile control --connect --workspace WORKSPACE_ID --json
```

当前部署还会返回 Loro Streams 网关与分片后缀 `streams-api-x.loro.dev`。实测 `api`、`control-b`、`control-c`、`presence` 子域在只放行四个 Lody 域时被 CONNECT 403 拦截。源码的控制/数据/写入/presence 分片会使用同一后缀；云网络需包含 `*.streams-api-x.loro.dev`，不以只读账户查询成功替代该链路验证。该后缀属于本次实际返回值，部署变化时应重新核实。

doctor会保留失败前已完成的检查，并通过`observed_at`、`verified_scope`、`control_environment`和`provenance`报告本次范围与可得来源。包清单、构建收据、安装收据及实际CLI版本分别记录；缺收据不补造，摘要一致不等于签名、正式发布或模型任务验证。账户查询通过但目录未运行时，报告范围仅覆盖已做查询。

先查实际CLI `--help`，按随包`skills/lody4dot/references/discovery.md`只读选择明确workspace、machine、project catalog、Agent config/Role；仓库名和本机`/workspace`不自动映射Lody工作区。403保留原CLI退出码、HTTP状态、目标及响应来源，健康探针不能替代原CLI目录查询。0.108.1默认Streams短期token刷新/一次重试与新建CLI key不同；原始debug/响应正文不保证脱敏，诊断规则见随包`skills/lody4dot/references/troubleshooting.md`。

`0.107.2` 的部分目录命令会在 JSON 前后输出同工作区的 `Remote Streams transport attached/detached` 诊断行。工具仅识别这两种精确消息及唯一完整 JSON，仍拒绝未知输出、混合工作区和多个 JSON；安全提示写 stderr，不回显日志或身份。账户与完整目录在本次云机已实测通过。

状态通过 Lody 支持的 `LODY_DATA_DIR` 分离；身份不进入插件包和共享环境快照。不修改 `HOME` 或 `CODEX_HOME` 绕过受保护的宿主配置。云端启动说明应显式读取技能入口并运行 doctor；保存说明后仍需要新任务提供实际加载回执。

## 自包含插件包

源码目录中的 `skills: "./skills"` 由构建产物满足；不要直接将源码目录作为已完整的原生插件安装。

在仓库根目录构建：

```bash
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot --json
```

构建会收集技能、参考、工具和锁定输入，拒绝缺失资源、符号链接、包外引用、额外文件和可识别的凭证文件，生成 `.lody4dot-build.json` 哈希清单。产物不包含依赖安装目录或身份状态；自有且完整的旧产物可重新构建，陌生目录或被修改的产物不会被覆盖。

将整个产物目录复制到其他位置后，以产物根为工作目录执行`python3 scripts/install.py`、`python3 scripts/doctor.py`、`python3 scripts/auth.py`、`python3 scripts/bootstrap.py`或`python3 scripts/handoff.py`及其相应参数。技能入口为`skills/lody4dot/SKILL.md`；随附参考均在包内。这里的包内路径与前面的仓库源码路径不同，不应直接互换。

在允许写入配置的 Codex CLI 环境，可以使用已核实的原生入口：

```bash
codex plugin marketplace add /absolute/path/to/lody4dot
codex plugin add lody4dot@lody4dot-local
codex plugin list --json
```

原生清单和 marketplace 格式依据 Codex CLI `0.163.0` 同版本官方源码。构建成功、注册成功、新任务加载技能分别验收；当前托管环境的受保护配置不能通过改写环境目录绕过。托管云配置的 `start_skill` 接入应报告为云环境接入，不能冒称已经原生注册。

OpenAI官方支持ChatGPT web的插件ZIP上传，以及由管理员从GitHub导入marketplace。当前先按已核实的Codex0.163.0格式准备自包含目录/ZIP候选；需保留隐藏清单与完整包内资源，实际构建和哈希以交付回执为准。ChatGPT web的上传、扫描、启用及技能读取仍需实测；完整Plugin Management格式指南的精确URL当前CONNECT403，不能据此声称ChatGPT已接受ZIP包装层级。

GitHub导入读取源文件，不会替仓库运行builder。当前`mcp/`、`skill/`、`plugin/`三目录源码中的`plugin/lody4dot/`需构建才能包含完整技能，不能新增catalog直接指向该未构建目录，也不提交生成分发物。后续自动同步路线须先确定可完整读取的发布来源与格式。声明MCP即使指向远程HTTPS，也可能使导入插件标为Desktop only；添加`.app.json`不会自动解除限制。详见[Dot接入指引](hosts/dot.md)。

## 验证与支持范围

在仓库根目录执行：

```bash
python3 -m unittest discover -s tests/lody4dot -v
python3 scripts/check_repository.py
```

离线测试验证工具行为和分发边界，不能代替真实账户、长连接、宿主加载或任务产物验收。完整命令资料的帮助证据也不等于全部业务功能已经实测。当前实现进度和真实验证缺口统一记录在仓库的 `.codex/agent-state/todo.md`。

`0.1.2` 修复了原生 Streams 诊断日志导致目录 JSON 误报的问题。当前云机的安装、真实授权、完整目录和已有会话的持久化观察已通过；本机 Codex ACP 初始化仍遇到只读状态写入错误，未通过真实任务验收。host 还会登记凭证可见的全部工作区，不能把任务的 workspace 参数当成 host 范围限制；详见技能的兼容性参考。

`0.1.3` 更正了会话操作无条件要求控制端 daemon 的知识错误。无控制端 host/daemon 时，已有远端 Codex Agent 的创建、执行、继续验证和持久化观察已通过；两个回合均完成，Agent 二次读回的文件字节、JSON与随机 challenge 哈希经控制端核对匹配。公开 history 不含底层工具执行日志，该产物证据来自 Agent 回传，不能称控制端直接读取远端文件系统。取消、其他配置、平台和高级操作未因此算作通过。当前云机 ACP 的只读限制只涉及本机执行，不能据此否定远端派发。

`0.1.4` 补齐运行中取消的真实证据与准确参数：`--turn-id` 使用 assistantTurnId，ACK和alreadyStopped均不能代替对应回合的持久化终态。修正归档/恢复的知识边界：归档递归覆盖关联后代并触发资源释放，恢复只覆盖根和直接parent子项，不承诺进程恢复或完整回滚。CLI与依赖锁未变，旧0.1.3发布物保留；源码/新包版本不等于已发布云环境自动升级。

已对本任务自有、无后代的空闲会话完成改名往返、归档和恢复；原标题及未归档状态已还原，6条可见历史、最新回合、空队列及空活动列表保持一致。该元数据验收不扩大为级联或执行进程恢复成功。

`0.2.0`增加多宿主协作参考、诊断来源与范围、离线handoff校验和依赖bootstrap；CLI与锁定输入保持不变。历史发布及验证记录在仓库任务队列维护，平台readiness、依赖、身份及原会话对账分别解释。

`0.2.1`已正式发布，修正Dot官方身份、共享连接与运行位置知识，补充随包Dot接入指引，并将CLI实际版本作为非阻塞提示、增加显式更新查询。默认安装与知识基线仍为0.107.2。

`0.2.2`候选只增加官方用户setup入口及其分发/来源校验，复用现有bootstrap，保留受支持的兼容清单；尚未迁移为portable根`plugin.json`。Linux以外受管安装、ChatGPT web导入、原生setup调用、Dot工具接入及完整重建各自保留验收前提，知识和工具测试不代替这些证据。候选不自动升级正式环境，也不改变CLI锁定输入。

`0.2.3`补充资料路线与输入表示、保存/回读分层、资料写入超时先对账，以及schema1适用边界；修正Dot随包说明的过时访问结论。复用现有核心和工具，不更改CLI依赖、校验器契约或正式云环境；实际接入与业务验收仍按各端证据判断。

`0.2.4`在原协作参考集中补Work Cloud与Codex Cloud的分工、创建/触发/运行证据及MCP支持面，资料和setup仅补适用条件。保留已有资料交付流程和全部运行工具，不新增平台任务创建入口、安装支持或业务验收结论。

`0.2.5`仅在原协作参考补Codex平台手动/Dot/CLI入口与平台支持、当前访问证据、项目职责的区别；按所在项目已有分工执行，不增加创建工具或查询路线。0.2.4产物与原验证记录保留，其他知识、工具、schema1、依赖及支持范围沿用。

官方依据：[Dot入门](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)、[Dot权限FAQ](https://help.openai.com/en/articles/20001529-dots-privacy-security-and-safety-faqs)、[Codex Cloud](https://help.openai.com/en/articles/20001545-using-codex-cloud)、[Plugins](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)、[GitHub marketplace导入](https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github)、[Skills](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)（读取于2026-10-21）。
