# lody4dot 多宿主协作任务卡

本页定义C01–C10的静态开发任务，服从[c3多宿主协作开发方案](collaboration-development.md)。c3保留原任务依赖和插件验收；公子已试通的Dot资料中转不需要重复验证，但不代替C09/C10的插件加载、实际Lody调用与跨端证据。本轮没有新增正式任务或改变完成状态。本页不保存实时状态；进度、执行证据和阻塞仅在[任务队列](../../.codex/agent-state/todo.md)维护。已有工具的实际用法见[插件说明](../../plugin/lody4dot/README.md)和[交接说明](handoff.md)；命令与验收条件不代表真实宿主或业务检查已经通过。

目标是让多个实际安装宿主通过Lody服务协作。Dot是官方确认的ChatGPT always-on agent产品，其自有云电脑、它创建的Codex云任务与授权本地电脑分别定位；Agent仍是主体类别，不把产品Dot作通用别名。控制端、执行端和混合角色分别验收，不将控制端接入收缩为全部目标，也不把安装成功升级为machine注册或worker可用。

## 共用约束与依赖

- 权威：用户确认的多宿主目标、主方案、[环境指引](environment-model.md)、[设计参考](environment-design.md)。已有实现契约仍见[开发方案d1](development.md)；有冲突先记录具体范围，不用任务卡默改契约。
- 正式来源与当前运行观测只在[唯一队列](../../.codex/agent-state/todo.md#当前环境与下一步)维护，不在静态任务卡复制实时版本。0.2.2增加官方用户setup入口；`0.107.2`仅为知识与默认可复现安装基线，不是Lody CLI执行版本门槛。候选更新不自动升级实例，不重配token或重复保存相同云准备草稿。
- 2026-10-21用户授权V01版本提示修订：Lody版本差异、版本探测失败不阻塞业务；默认inspect/bootstrap离线，仅显式`doctor --check-updates`查询固定`https://registry.npmjs.org/lody/latest`，非最新版或查询失败只告警，不自动升级。真实CLI执行、身份、权限、Node/平台前提和安装输入完整性失败仍按实际结果报告；此修订优先于旧严格版本判定，其他既有契约不变，进度仍由队列维护。
- T09旧截图的当时入口/版本、当前发布后原任务恢复、新独立任务实际送达并读取技能分别取证。T12既有缺口继续单独保留，C任务不自动关闭它们；平台readiness未知不抹掉已取得的局部实测，也不等于全部ready。
- 验证命令在各目标宿主的仓库根目录执行；`python3`须指向Python3.10+。未提供shell或CLI的宿主使用实际可用的只读工具取证，不凭空填写命令或能力。
- 需要安装前缀的命令先将非秘密变量`LODY4DOT_PREFIX`设为该端安装回执的实际prefix；认证检查使用该端已有私密`LODY_DATA_DIR`。这些变量只选择本端路径，不复制登录态；缺路径时先补输入，不套用另一端的`/workspace`。
- 实现交付由集成执行者统一运行`python3 scripts/check_repository.py`、`python3 -m unittest discover -s tests -v`和`git diff --check`；并行文档工作只做对应链接、示例与一致性检查，避免重复干扰。卡内命令用于受影响范围；已有测试不替代真实宿主、身份或业务证据。
- 默认不登录、不注册machine、不启动host；业务请求、模型执行和部署按既有授权及明确目标进行。凭证不进入包、日志或公开回执，各宿主身份状态分别保存。
- Dot、ChatGPT、Work与Codex可复用已有合法插件连接及已授予权限，不因换产品重复连接；skills安装/管理、工具暴露和服务动作仍分别核对。共享连接不提供本地访问、浏览器登录、任意空间或模型凭证。
- 用户确认本项目的独立Codex云任务由Dot创建，Dot具备权限；当前云任务不派生Codex云任务，也不查询OpenAI任务目录。401只保留历史，不作为C05/C09或插件前置。获授权的Lody session/turn派发不受这条平台任务边界替代。
- 公开证据只记录脱敏结论、版本和必要摘要；真实业务引用及原始回执放各自受保护的私密记录，不建共享凭证库或全局调度数据库。

| 可独立验收的结果 | 前置任务与所需证据 |
| --- | --- |
| C01宿主契约、C02知识入口、C03诊断证据 | 三项可并行；复用已读官方契约，Dot未知生命周期不阻塞已支持接入路线 |
| C04平台安装边界 | C03报告语义；Linux基线与各候选平台分别给结果 |
| C05宿主分发与加载 | C01实际加载契约、C02资源、C04对应平台的证据 |
| C06最小交接 | C02引用规则、C03证据格式；包内新增工具再补C05分发回归 |
| C07两个独立宿主协作 | C05两个可用端、C06交接、实际Lody目标及授权 |
| C08重建恢复 | 本地依赖bootstrap可单独验证；真实重建与业务对账须有C01生命周期、C05引导与C07原生引用 |
| C09 Dot接入 | C01所选官方路线、C02知识、C03报告、C05适用分发、C06交接；不依赖未知Dot hook或C07完成才验证已有入口 |
| C10含Dot闭环与交付 | C07协作、C08恢复、C09 Dot真实接入；部分交付与整体完成分别报告 |

## C01 核实宿主契约与生命周期

- **权威/依赖**：主方案的宿主与角色边界、环境指引及[本轮9篇官方Help记录](host-contracts.md)；无前置任务。复用Dot身份、共享连接、Codex委派、local skills及Codex0.163.0的已核实契约，不将资料等同真实加载。
- **文件范围**：`docs/lody4dot/platform-contract.md`、`docs/lody4dot/host-contracts.md`及引用来源；本卡不改安装器、登录态或正式环境。
- **步骤**：按所选路线列Dot云电脑、Dot创建的Codex任务、本地电脑的加载入口、工具、路径与身份；有界核对生命周期。已读来源未给Dot prepare/reset hook时记录未知，明确唯一下一官方来源，不反复检索同一否定结果。用实际工具最小只读核验，保留资料版本、工具范围与未知项。
- **验收**：每个宿主能区分知识可读、CLI可运行、控制可用和执行能力；Codex默认7天VM恢复窗口、新setup用于新任务和Dot主动Reset分别解释，不混为周期磁盘事件。可选择官方已支持路线继续C09；未知hook既不补造，也不降格为“官方没有”。缺少本任务入口不写成用户无权限。
- **验证**：下面命令仅用于已提供Codex CLI的目标；Dot使用实际暴露的元数据/工具及官方资料，未提供则记录缺口，不新增虚构探针。

```bash
codex --version
codex plugin --help
codex plugin marketplace --help
```

- **证据/恢复**：保存来源、版本、操作位置及脱敏返回；只读核验无需配置恢复，实验若产生自有临时文件仅清理这些文件。
- **未决/停止**：Dot自有电脑未暴露实际CLI工具/合法身份入口，或未取得初始化hook契约时，分别停止相应分支；已有合法连接、预配置Codex委派和授权本地路线继续取证。完整Plugin Management指南受阻时不补猜格式，也不绕过代理；宿主接口实际不兼容时修订受影响契约，Lody版本差异本身只告警并按实际帮助核实。

## C02 共享技能与运行位置知识

- **权威/依赖**：主方案的协作行为与环境指引；无代码前置。C01尚未知的能力写成条件，不等待未知能力才能修复已知误述。
- **文件范围**：`skill/lody4dot/SKILL.md`、`references/{setup-cloud,compatibility,discovery,configuration,sessions,collaboration,material-handoff,delivery}.md`及来源记录；不复制第二套CLI命令索引。
- **步骤**：增加宿主识别→控制/执行角色→明确Lody目标→操作→持久化观察→交接的任务导航；说明Dot为具体Agent产品，并区分其自有电脑、Codex委派任务及本地授权，不把它当任意Agent别名。资料目标先选直连、中转或组合Lody的路线，再进入实际需要的Lody步骤；引用类型、输入表示及处理/保存/回读分别记录，复用既有超时对账。共享连接限已授予权限，协作空间与文件目录分别定位；按包内资源路径引导。取消只承认已测自有普通回合；local_runtime按控制端参照与目标条件说明，必要的schema调整另做兼容评审。
- **验收**：给新Agent业务目标而非现成命令，能找到参考、选择已有明确目标并说明操作位置；缺CLI仍可读取资料但不声称可派发。资料场景核对原字节缺口、保存后回读被拒及固定原生路线的选择，不以关键词测试代替选择理由；这些演练不重验产品中转或证明原生加载。用户提供路径、自主检索与平台引导分别记录，不新增全文自动注入门槛。
- **Work知识增量**：复用上述资料规则，补宿主类型与创建/触发证据；演练核对Work文件能力的条件、业务MCP不提供创建入口，以及计划保存不等于运行。不为此新增Work连接器、复制场景表或创建业务任务；官方支持不升级本插件宿主支持状态。
- **Role/Project知识增量**：将已有源码核实带入原配置参考，区分多Role复用、项目上下文与未核实的持久角色组、当前身份机器提议路由及用户保存。新上下文检验关系选择与缺工具的失败出口；不创建配置/角色/项目，不把普通远端派发结果当提议或保存证据。
- **验证**：下列知识测试已存在；补充目标选择、未知能力、Role覆盖及错误引用的行为案例，实际Agent演练回执独立记录。

```bash
python3 -m unittest discover -s tests/lody4dot -p test_knowledge.py -v
python3 scripts/check_repository.py
```

- **证据/恢复**：保留知识差异、来源版本和演练读取范围；修订失败只恢复该轮知识文件，不改业务会话或既有发布配置。
- **未决/停止**：宿主实际路径由C01/C05给出；当前CLI版本不变时不重采帮助或伪造帮助哈希。发现资料与具体版本实现冲突，保留差异并停止相应操作说明的肯定结论；版本差异本身不阻塞业务，所需命令按实际帮助核实。

## C03 唯一doctor与来源证据

- **权威/依赖**：主方案的诊断契约、d1的JSON及退出码；无前置任务。先完成Linux已有范围，不要求取得全部宿主标识。
- **文件范围**：`plugin/lody4dot/scripts/{doctor,common}.py`、`tests/lody4dot/test_diagnostics.py`；读取既有build/install收据，不新建第二套来源清单。
- **步骤**：保留失败前已完成checks及实际未运行项；增加观察时间、请求范围、控制端工具位置与可得的插件/CLI/锁/包摘要；区分账户查询和目标目录覆盖；保留`schema_version:1`与旧字段，版本提示按共用约束V01修订执行，其他退出码/字段含义保持；新字段为兼容扩展，未知引用不填假ID。
- **验收**：缺runtime、账户失败、目录失败均保留此前真实检查；账户通过不代表目录/任务通过。默认离线、不登录、不读写调用方既有身份state；版本探测可创建并清理自有一次性临时state。只有显式`--check-updates`才查固定npm latest；版本差异、探测失败、非最新版及更新查询失败均只告警，不使顶层阻塞或失败。`task/worker`不因目录成功改pass。缺包收据和版本不一致分别报告，原生输出与凭证不得回显。
- **验证**：新增失败上下文、字段兼容、收据来源及版本告警案例；区分版本探测失败与实际业务命令失败，核对默认离线和显式更新查询失败不阻塞。不把fixture通过当真实服务证据。

```bash
python3 -m unittest discover -s tests/lody4dot -p test_diagnostics.py -v
python3 -m unittest discover -s tests/lody4dot -p test_build.py -v
```

- **证据/恢复**：保留脱敏新旧输出对照和失败案例；发现兼容问题恢复本轮报告改动，已有身份、安装入口与Lody业务状态保持原样。
- **未决/停止**：宿主版本/实例标识仅在真实提供时记录，Lody版本未知仅告警；V01已获用户授权，不为撤除严格版本门槛再等待批准。其他旧JSON含义或退出码变更仍先明确兼容策略。诊断不读取凭证内容来“证明”身份。

## C04 平台安装层与结构化不支持结果

- **权威/依赖**：主方案的平台范围、C03报告语义；Linux已验证路径为基线。macOS/WSL仅为候选探测，Windows原生执行支持后置。
- **文件范围**：`plugin/lody4dot/scripts/{install,common,doctor,auth,platform_support}.py`、`tests/lody4dot/test_platform_support.py`及既有安装/诊断/版本策略/生命周期测试。离线夹具修订只改测试，生产平台边界不随之放宽。
- **步骤**：把平台识别提前到POSIX专属导入与操作前；局部封装路径、锁、稳定入口、私密state检查和超时清理；保留Linux事务行为；在实际macOS/WSL逐项探测native依赖与权限，只有证据满足的组合才加入支持矩阵。
- **验收**：Linux重复安装、失败切换恢复和旧state保护不回退；不支持平台返回脱敏JSON与退出码5，而非`fcntl/getuid/killpg`崩溃。只去掉Linux判断不算跨平台；WSL不算原生Windows，候选失败不触发自动登录、host或权限放宽。
- **离线夹具**：Linux后端语义用例显式选择模拟平台；只规范化TemporaryDirectory创建的自有基础根，不解析掉故意输入的符号链接或mock掉生产拒绝检查。原平台拒绝、用户state保护和Linux文件锁用例保留；普通路径、别名临时路径与条件模拟分别验证，不能据此宣称真实macOS/WSL支持。
- **验证**：下列测试均已提供。OS mock只证明分支行为，macOS/WSL支持须另附实际OS/架构的安装、native、重复安装和失败恢复记录。

```bash
python3 -m unittest discover -s tests/lody4dot -p test_platform_support.py -v
python3 -m unittest discover -s tests/lody4dot -p test_install.py -v
```

- **证据/恢复**：按OS/架构记录输入版本及探测结果；失败保留旧入口与陌生目录，撤销本轮自有暂存文件。Linux结果可独立供C05使用。
- **未决/停止**：没有真实候选宿主或native产物则不宣布支持；Windows私密权限与进程模型未定义时只实现结构化不支持，不用POSIX位数模拟其ACL。

## C05 按宿主契约分发与加载

- **权威/依赖**：C01的实际入口、C02资源与C04对应平台结果；只依赖本次选择支持的平台，候选OS未知不阻塞Linux基线分发。
- **文件范围**：`plugin/lody4dot/scripts/build.py`、已核实的清单、`plugin/lody4dot/hosts/dot.md`、`plugin/lody4dot/README.md`、`.codex/cloud-install.sh`、`.codex/cloud-start.md`及`tests/lody4dot/test_build.py`。
- **步骤**：用同一知识源码生成含Dot说明的自包含包，按官方支持的兼容清单准备目录/ZIP候选；0.2.2追加`extensions.com.openai.onboardingSkill`及薄setup技能，复用bootstrap。保留隐藏清单和全部资源。GitHub marketplace已有官方导入路线，但不运行builder；不能新增catalog直接指向未构建的`plugin/lody4dot/`，不提交生成分发物。ChatGPT web的扫描、安装、读取及用户run setup分别取证，新对话/安装所在对话各自测试；ZIP外层包装未知部分不猜。bootstrap与知识入口分开，安装prefix使用该端实际值。
- **独立云任务入口**：由Dot实际发起并保存任务/环境关联，子任务核实首次发现及读取后回传。Dot权限已由用户确认，无需再次索取；当前云任务不改用Cloud CLI创建下游任务，不以OpenAI任务目录401作为缺口。已有原任务补证优先，不为补旧字段重复创建。
- **验收**：移位包可找到全部资源与Dot指引；缺资源、包外引用、修改过的旧输出及已有规则覆盖的敏感文件/凭证fixture均失败。allowlist和来源仍须复核，扫描器不承诺识别任意秘密。安装不登录、不注册机器、不启动host。构建、上传扫描、安装/启用、启动入口送达和实际读取各有证据；Codex格式候选不称ChatGPT已接受，托管接入不冒称原生注册。
- **离线ZIP增量**：源码builder显式`--zip PATH`生成完整根目录ZIP并验证CRC/收据/文件摘要，保留默认目录JSON；已有ZIP目标（包括目录/符号链接）、源或输出重叠均拒绝，发布竞争不得覆盖他人文件，校验/发布失败清理自有暂存。旧时间戳按ZIP可表示范围规范化，不改变内容摘要。该本地分发子范围可独立验收，不代替真实宿主加载或GitHub发布。
- **验证**：命令只构建自有输出；目录已被陌生内容占用时停止并选择新的自有输出，不删除原目录。

```bash
python3 -m unittest discover -s tests/lody4dot -p test_build.py -v
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot-collaboration --json
```

- **证据/恢复**：记录包版本/哈希、移位检查和首次读取来源；构建失败保留旧包。宿主加载实验只撤销自有注册，正式配置发布另按已获授权范围处理。
- **未决/停止**：ChatGPT完整格式或UI回执缺失时交付明确标注的候选，不扩展未验证catalog。MCP声明可能造成Desktop only，`.app.json`不能自动解除；不通过添加MCP猜测web兼容性。不能绕过受保护配置或复制登录态。

## C06 最小handoff整理与校验

- **权威/依赖**：C02引用规则、C03证据语义和主方案的交接边界；新增工具纳入C05的allowlist与分发回归，不形成循环前置。
- **文件范围**：`plugin/lody4dot/scripts/handoff.py`、`tests/lody4dot/test_handoff.py`及[公开虚构示例](handoff.md)；同步`plugin/lody4dot/scripts/build.py`所需allowlist，不新增业务SDK。
- **步骤**：调用方准备目标/授权、控制与执行位置、版本、原生资源引用、实际观察、结果证据与未知项，再以`--input PATH --stage intent|dispatched|result --json`校验；工具不从Lody取回或生成记录。资源引用带系统与类型，操作意图、服务端观察及产物结果分开。
- **验收**：格式正确不等于实时授权或业务完成；未知值按阶段允许null，未知字段被拒绝，缺关键关联指出具体缺口。检查可识别的引用类型错误、来源缺失/声明矛盾、已知模式凭证内容和声明范围冲突；未核验的来源不能升级为“已验证”。`not_verified`保留身份、ACL、授权、来源、业务结果、工件内容、实时新鲜度和执行器身份映射。离线工具不能识别任意伪造，不发网络请求、不重发任务、不保存全局业务数据库。
- **验证**：现有测试覆盖有效记录、缺失引用、错误类型、声明过期观察、敏感输入拒绝及无网络/登录副作用；时间检查只验证格式与声明顺序，不验证当前新鲜度。最后一条用调用方私密记录；可先按公开虚构示例演练，fixture通过不证明真实业务。

```bash
python3 -m unittest discover -s tests/lody4dot -p test_handoff.py -v
python3 -m unittest discover -s tests/lody4dot -p test_build.py -v
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage result --json
```

- **证据/恢复**：测试使用虚构fixture标识并标明非平台对象；真实记录留在私密位置，公开只保留脱敏结果。失败保留输入，不覆盖已有交接文件。
- **未决/停止**：若需求扩成自动派发、调度、身份代理或新业务API，停止扩大该工具并单独评审；不强制新增installation_id，使用实际可得的宿主与Lody原生引用。

## C07 两个独立宿主经Lody协作

- **权威/依赖**：C05两个已可用端、C06记录、明确的工作区/目标及操作授权。先使用已具备入口的端，不等待Dot未知能力，也不把该结果当含Dot整体完成。
- **文件范围**：新增或扩展受控验收说明及脱敏验证记录；本任务主要交付实际证据，不新造通用远端执行器。
- **步骤**：证明至少两个实际安装宿主独立；分别读取技能、核对版本及本端合法身份；控制端A经Lody派发自有小任务，端B用同一原生引用只读观察/复验。端B可使用实际暴露的宿主内置Lody MCP，不强制安装独立CLI或复制登录态。可衔接已有完整派发/执行证据，不重发原产物业务；确需模型调用工具时，将其作为独立、明确的只读验收回合记录。执行节点可属于其中一端或既有第三端，按实际记录；核对持久化终态和产物，不把两个控制端称为两个worker。具体只读目标见[独立控制端运行单](dot-acceptance.md#无凭证交接与只读复验)。
- **验收**：不能用同实例子Agent冒充独立宿主；查询或ACK不足以证明完成。B可核对同一session/turn与结果，端间不依赖同名目录或共享登录态。失联、错误目标和结果不完整只保留失败/未知，不新建或重复发送替代任务。
- **验证**：现有命令检查控制端前提；A派发/B观察使用C01核实版本的原生命令，具体目标参数在私密运行单确定，不在公开卡中提供可误执行的写命令。

```bash
python3 plugin/lody4dot/scripts/doctor.py --prefix "$LODY4DOT_PREFIX" --profile inspect --json
python3 plugin/lody4dot/scripts/auth.py --prefix "$LODY4DOT_PREFIX" --verify-only --json
```

- **证据/恢复**：保存两端来源、独立性、版本、原生引用、持久化观察与产物摘要；仅清理自有临时state/产物，不维护用户既有会话。控制端CLI证据不冒称直接读远端文件系统。
- **未决/停止**：缺第二独立端、目标执行凭证或授权则停止对应真实操作，继续离线准备；当前只读ACP云实例可作控制端，不冒充云worker。

## C08 重建与恢复演练

- **权威/依赖**：本地依赖准备与缺失恢复可独立验收；真实宿主重建另依赖C01生命周期、C05安装/启动入口，业务对账另依赖C07可追溯原生结果。知识引导、依赖bootstrap及身份/业务恢复分别验证。
- **文件范围**：`plugin/lody4dot/scripts/bootstrap.py`、`tests/lody4dot/test_lifecycle.py`、`.codex/cloud-install.sh`、`.codex/cloud-start.md`及恢复验收说明；本地测试不证明真实平台生命周期。
- **步骤**：先冻结演练端与自有资源；环境准备使用`--prepare`，运行入口默认离线inspect或显式`--repair-missing`。只有诊断明确为缺少受管运行时才修复；Lody版本差异或探测失败只告警，不触发重装或阻塞，来源损坏等真实失败按原规则报告且不自动覆盖。Codex新发布setup应用于新任务，原任务恢复与新任务创建分开；默认7天VM窗口不当作Dot磁盘规则。依实际支持机制重建或切换自有安装目录后读取技能并记录实际版本/身份，再通过原生引用只读定位C07结果，不自动恢复模型任务。
- **验收**：bootstrap可复用同锁且失败保留旧入口；startup记录实际发现/读取来源。无官方reset hook时不杜撰自动挂钩；临时目录演练只证明文件恢复。未收到身份不自动复制登录态，原session仍可定位不等于进程恢复或允许重发。
- **验证**：下列本地测试已提供，不代替实际宿主重建回执。三个bootstrap命令分别为明确准备、默认检查、缺失修复，按场景选择，`--prepare`和`--repair-missing`不能合用；均不触发认证、daemon或业务恢复。不要为了演练在用户现有目录删除依赖。

```bash
python3 -m unittest discover -s tests/lody4dot -p test_lifecycle.py -v
python3 plugin/lody4dot/scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --prepare --json
python3 plugin/lody4dot/scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --json
python3 plugin/lody4dot/scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --repair-missing --json
```

- **证据/恢复**：记录重建前后真实宿主/版本与观察时间，未暴露标识保留未知；演练失败恢复自有稳定入口或保留旧产物，不触碰受保护HOME/CODEX_HOME或他人进程。
- **运行中观察恢复子场景**：在自有会话唯一一次chat后落盘ACK的userTurnId，从follow快照匹配running的assistantTurnId，实际终止该本地观察进程并等待退出，再清理本次身份。新私密身份只沿原引用观察与验产物，不重发。仅能证明观察进程/本地身份恢复；不将单次查询正常返回称作中断，也不推导主机重启或结束通知完全缺失。每次重复都是新的模型验收请求，不作为发布后的例行检查。
- **未决/停止**：没有Dot正式重建入口则停止该真实重建部分，已支持Codex准备路线继续，报告安装复用子范围；不把用户主动Reset当周期存储事件，不让shell启动文件、定时器或watchdog冒充官方hook。已有配置无需因知识补丁再次保存草稿或重配token。

## C09 Dot独立宿主接入

- **权威/依赖**：C01已核实的所选官方路线、C02知识、C03报告、C05适用分发与C06交接；C07可并行。Dot是具体always-on agent产品；它发起的Codex任务可作为委派路线，不能冒充Dot自有云电脑直接CLI。
- **文件范围**：`plugin/lody4dot/hosts/dot.md`、[Dot接入与独立控制端运行单](dot-acceptance.md)、支持矩阵及经确认必要的最小宿主适配；无缺口证据前不建立代理服务、Sites或伪插件清单。
- **步骤**：先确认Dot实际读取共享知识，按最小路线选已有合法app/MCP连接或预配置Codex云任务CLI；如选Dot自有电脑直接CLI，先核实当前执行器工具/OS/身份；如选local skills，先核实Dot本地电脑授权与在线。复用既有连接，用最小只读Lody请求确认目标访问并形成C06交接，不先派发模型任务。
- **验收**：各路线单独记录产品界面、执行器、技能读取、工具、版本/来源与目标；MCP须有真实服务入口和合法上下文。Dot委派任务须有Dot实际发起及任务关联证据，当前独立Codex工具或同实例子Agent不能代替。会话引用不等于空间枚举或Lody授权，知识加载不等于工具接入。共享权限不扩大服务/本地/模型访问；local skills不能只用Codex连接或Work Sync作为授权证据。
- **验证**：先按运行单检查候选导入、知识目标与真实入口。只有确认所选Dot执行器或其委派Codex任务具备CLI时才在该执行器运行下面命令，并明确实际位置；MCP路线用实际公布工具做等价只读检查并保存脱敏回执。平台无新任务创建或导入工具时保留未运行，不用子Agent冒充独立任务，不编写虚构命令。

```bash
python3 plugin/lody4dot/scripts/doctor.py --prefix "$LODY4DOT_PREFIX" --profile inspect --json
python3 plugin/lody4dot/scripts/auth.py --prefix "$LODY4DOT_PREFIX" --verify-only --json
```

- **证据/恢复**：保留Dot自己的入口、首次读取、连接、身份作用域与原生目标引用；撤销实验仅限自有适配配置，不把其他端凭证或会话全历史复制到Dot。
- **未决/停止**：所选路线工具入口未暴露则停止该分支并明确下一核实点，其他官方路线按实际条件继续。确需新MCP/Sites时先审调用身份、凭证范围、副作用与运维所有权；full custom MCP有套餐/角色限制，Pro的read/fetch不推导任务写入。发现期间不部署服务，不因未知Dot hook阻塞委派路线，也不将“Dot只读资料”写成完整接入。

## C10 含Dot多端闭环与分层交付

- **权威/依赖**：C07真实跨端协作、C08恢复证据及C09 Dot接入；主方案决定整体完成条件。可先交付有证据的子范围，含Dot闭环未通过前不宣布整体目标完成。
- **文件范围**：支持矩阵、分发说明、验证记录与现有唯一队列；版本及受影响清单按实际变更更新，不把本次方案版次当插件发布版本。
- **步骤**：由Dot或另一实际控制端形成目标与交接，经Lody派发到已授权执行端，另一安装宿主只读复验并将准确结果带回Dot；检查版本差异、未知项和失败出口；在自有安装上演练升级失败保留旧入口及已验证版本回退，整理各平台/角色的支持范围。
- **升级/回退范围**：区分插件知识包、宿主接入材料与CLI/runtime输入，保留主方案允许的上一安装入口或接入材料回退。若验收受管CLI/runtime的跨版本升级，需要两套经过复核的真实输入，在新的自有prefix验证升级失败保留A、B成功后按A原锁重新激活；不为验收擅自升级CLI、改锁空白或改收据伪造第二版本。同锁复用和fixture失败保护只能证明各自范围；只有知识内容变化的插件版本不算第二套runtime。第二套CLI输入不作为所有插件/接入材料回退的新增门槛。
- **验收**：分别交付共享知识、两个可用端协作、Dot接入、含Dot闭环与重建恢复证据；取消和归档范围不扩大为任意业务回滚。失败升级不破坏旧版本和身份；现有T09/T12缺口独立核实，正式环境升级另有实际配置与实例应用回执。
- **验证**：执行完整仓库回归与构建，另附含Dot真实链路及升级/回退回执。没有实际Dot记录时，仅报告可交付的子范围。

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot-collaboration --json
git diff --check
```

- **证据/恢复**：公开记录版本/哈希、检查结果、支持与未运行项；私密关联原生引用及实际观察。只在已有相应授权范围更新发布物或正式环境；未升级时交付可复现产物与具体升级步骤，不制造已发布结论。
- **未决/停止**：Dot或恢复关键证据缺失只阻塞整体完成，已支持子范围可独立发布；出现凭证混入、跨端权限扩大或错误目标立即停止相关发布/业务操作，保留现场并恢复自有已验证版本。
