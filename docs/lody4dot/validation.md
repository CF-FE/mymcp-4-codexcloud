# lody4dot 实现与验证记录

记录起始：2026-10-20；本轮更新：2026-10-21（北京时间）。任务状态权威为 [队列](../../.codex/agent-state/todo.md)，接口依据为 [开发契约](development.md)。以下按轮次记录离线行为和真实账户结果；历史“当前”只描述该节当时的观测。账户成功不代替目录、宿主加载或任务验收。

## 环境与固定输入（T02）

- Linux，Node `v24.19.0`，npm `11.9.0`，Python `3.12.14`，Codex CLI `0.163.0`。
- Lody 固定为 `0.107.2`，使用提交的 [manifest](../../plugin/lody4dot/runtime/package.json)、[锁文件](../../plugin/lody4dot/runtime/package-lock.json) 和 [构建策略](../../plugin/lody4dot/runtime/build-policy.json)。
- 锁文件 SHA-256：`b1baf3ab20593c88f40e4ab7077b737296480d6ca3a0428b7d55499eee9bcced`，40 个锁项。
- 全部安装脚本禁用，锁中无 `hasInstallScript` 项。必要 native 模块无需另行运行构建脚本。
- 原始 CLI 无凭证采集的 70 页公开帮助均退出 0；排除内部命令。发布包的 Lody 版本未更改。

原始依赖 Tinypool `1.1.1` 在当时 audit 中涉及两项 critical 公告：[GHSA-5gmw-xhrv-c9v3](https://github.com/advisories/GHSA-5gmw-xhrv-c9v3)、[GHSA-85c8-ppgw-ccpr](https://github.com/advisories/GHSA-85c8-ppgw-ccpr)。公告描述的利用还需要特定输入/原型污染条件，不能据此宣称 Lody 已被利用。

采用限定在 Lody 下的 `tinypool: 2.1.2` override。没有执行强制 audit 修复或降级 Lody。该覆盖跨越原依赖 major 范围，因此做了原始 worker 对照，而非只相信安装成功：

- Tinypool 1.1.1 与 2.1.2 分别加载未修改的 Lody diff 和 file-index-scan worker。
- 并发 diff、Unicode、文件匹配/不匹配、递归/浅扫描、完整索引、异常传播与池恢复的规范化结果一致。
- 最终冻结安装再执行 [可复现 worker 检查](../../tests/lody4dot/verify_workers.mjs)，7 组检查通过；使用空环境加 PATH，无账户凭证。
- 对最终冻结安装运行 `npm audit --omit=dev --json`，退出 0，各等级及 total 均为 0。这仅代表当时 registry 已知公告结果。

实测限于 Node 24.19/Linux；Node 22、Bun 和其他系统未实跑。官方 engines 范围与实际验证范围分别说明。

## 知识检查（T03）

[技能入口](../../skill/lody4dot/SKILL.md) 配有 8 个主题参考、命令索引、来源记录和帮助快照。20 类、70 个公开路径逐条匹配；帮助 SHA-256、版本、命令树和索引字段一致。

25 个 fenced CLI 示例已对实际命令/参数检查；版本冲突保留在来源记录中，例如 `session create --env` 已 deprecated。帮助证据没有被标为业务功能实测。

## 安装器验证（T04）

真实执行以下入口：

```bash
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot --json
/workspace/.tools/lody4dot/bin/lody --version
```

首装 `reused=false`、同锁再装 `reused=true`，均退出 0。稳定入口输出 `0.107.2`；帮助和以下检查通过：SQLite 内存查询/关闭，PTY、keyring、loro 加载，以及 roost 的 ESM import。模块加载不能证明真实 keyring 存取或账户可用。

14 项安装器 fixture 测试覆盖未知目录/入口拒绝、Node 范围、冻结输入、同锁复用、隔离验证状态、代理/CA 继承，以及 npm/native/版本/切换失败时旧入口和用户状态保留。生产安装没有登录、注册机器或启动 daemon。

## 诊断与认证验证（T05、T06）

真实 `doctor.py --profile inspect --json` 退出 0：Node 和 CLI 通过，凭证观察为 missing，账户、运行进程、任务执行为 not_run。`task` 不会因 CLI 可用就通过。

18 项 fixture 测试验证默认不查账户、control 显式连接要求、task/worker 未验证状态、空/坏 JSON、权限和网络错误、超时终止、不回显假凭证、verify-only 不登录、私密状态要求和外部指针拒绝。

认证仅在显式 `--login` 时将 `LODY_CLI_TOKEN` 传给已核实的 `login --auth` 入口；原生 CLI 仅提供 argv 通道，因此同权限本机进程的参数可见性仍存在。适配器不用 shell、历史、debug 或原生输出转发掩盖这一边界。最初无账户阶段尚未执行实际授权；后续真实授权与目录链路结果见下文。

## 分发与云配置（T07、T08）

自包含产物共 22 个受哈希管理文件，另有构建 receipt，包含原生清单、marketplace、技能、工具和 runtime 锁定输入。没有依赖安装目录或登录态。

初版 `dist/lody4dot-0.1.0.zip` 共 23 文件、63,549 字节，解压完整性检查通过；SHA-256 为 `ac047a8836c8900103ca6541e605bab28ba424aae13845315c80ce91f130c738`。构建 receipt 的 SHA-256 为 `356547f1918cc72e1ca1990dd8058284ee67b600b7f267a45dfd823181e1bab0`。生成物留在被忽略的 dist，不作为第二份源码提交。

将整个产物复制到 checkout 外 `/workspace/.cache/lody4dot/relocated-package`，从该位置安装到全新 `relocated-install`：真实首装和 inspect 均退出 0。证明脚本/资源不依赖原 checkout 路径；未证明宿主加载。

10 项构建 fixture 验证移位资源与精确哈希、必需 common、缺资源、包外引用、敏感/额外文件、符号链接、未知输出保护及切换失败恢复。独立代码审查发现的 common 必需依赖漏检已修复，并增加回归测试。

0.1.1 阶段的标准命令覆盖 45 项 lody4dot 测试及 8 项原仓库测试，共 **53 项通过**；结构检查为 `mcp=1 skill=1 plugin=1`。独立 worker 检查不计入这 53 项。本次 0.1.2 的新增验证见下文。

完整执行 `.codex/cloud-install.sh` 退出 0，实际完成这些测试、同锁安装复用和离线 inspect，未做认证或启动服务。

云配置草稿已由后端确认 `status=saved`、`requires_publish=true`：

- 安装脚本：[cloud-install.sh](../../.codex/cloud-install.sh)，只装依赖及运行离线检查。
- 启动指引：[cloud-start.md](../../.codex/cloud-start.md)，按需读取技能，在任务内使用私密状态。
- 保留 package_managers preset 与 `lody.ai`，新增 `convex.lody.ai`、`backend.lody.ai`、`api.lody.ai`。
- 只声明直接进程变量 `LODY_CLI_TOKEN` 的名称，没有提供值或另造代理 secret。

配置保存不执行安装、不发布环境、不证明新任务加载。原生注册命令已依据同版本官方源码核实；当前没有修改受保护的宿主配置或声称注册完成。

## 离线 agent 演练（T10 的独立准备）

另一个无前序会话上下文的 agent 只收到目标“查所有机器，并判断能否用已有 Role 发起任务”。它自行读取技能和必要参考，检查版本、inspect/task、verify-only 及准确帮助；识别缺身份/state，没有猜工作区、登录、启动 host 或创建会话。它正确区分分页、unknown 在线状态、Role 覆盖和持久化结果核验。

该结果证明这次演练的流程选择；agent 是显式获知技能路径，并非由新云任务自动发现。它没有真实账户/任务结果，不能让 T09 或 T10 的真实闭环通过。

## 发布传播的历史观测（T09）

用户截图已经确认该环境添加了 `LODY_CLI_TOKEN` 变量名称。随后的只读复查仍显示：当前进程 missing，运行环境变量元数据为空；保存草稿中该变量为 `pending_runtime_requirements`，直接变量交付。不能由此否定用户已配置，也不能仅从截图推断已注入当前任务。

当前生效网络仅有 `lody.ai` 加包管理 preset。对三个服务域名进行无凭证 HTTPS 探测均为 curl 56、CONNECT 403，确为代理策略阻断；没有尝试绕过代理或关闭 TLS。

用户随后已明确确认保存并发布。再次复查当前实例，仍无 LODY 变量，三个服务域名仍为 CONNECT 403；当前运行元数据仅允许 lody.ai，保存配置仍可读到四域名和待应用变量要求。此处区分用户已完成发布与当前实例尚未获得配置，不否定用户操作，也不依据来源版本号单独推断必须换任务。

当时的下一步是由宿主重连/传播，或在已发布环境的新运行任务中复查真实生效规则及进程变量存在性。当前会话没有重启/切换运行实例工具，不重复保存相同配置制造新草稿。只有变量实际注入后才做显式授权和只读工作区发现；工作区、测试机器/Role及底层 Agent 凭证须由实际结果确定。发布或源码配置版本号本身均不能代替这些检查。宿主新任务读取回执、私密状态/快照边界、真实查询/观察和受控任务仍未通过；整体目标保持未完成；后续状态以下方真实连接记录及任务队列为准。

## 本次真实连接与目录诊断（T09）

用户再次发布后，当前同一任务的运行观测更新到 spec_revision/observed_spec_revision 均为 4，四个 Lody 域名生效，保存配置不再有 pending 变量；进程实测 `LODY_CLI_TOKEN` 为 present。没有新建任务，因此事实推翻了“当前会话必然要换任务才会更新”的假设；此前只将新任务作为恢复尝试，没有用来源版本号判定它必需。

三个服务的无凭证 HTTPS 探测已不受策略阻断：convex 根路径 200，backend/api 根路径 404，curl 均为 0。根路径 404 不表示实际业务 API 已通过。

随后使用当前任务新建的 0700 私密临时目录，显式 `auth.py --login` 退出 0，真实 `workspace list --json` 返回 ok，发现 2 个工作区。再执行 `--verify-only` 退出 0，无重新登录；账户级 `doctor --profile control --connect` 通过。用户已明确选择个人工作区用于后续隔离验收；不在公共仓库存放工作区 ID、机器信息或原始业务响应。

源码复查进一步区分授权路径：0.107.2 的 API-key 登录仅验证 token、取得稳定本机 ID 并保存身份，不调用远端 registerMachine。因此适配器将机器注册报告为 not_verified，新增 local_identity 字段；没有把登录成功当成远端机器注册或在线。配对/设备授权仍有各自连接副作用，登录保持显式操作。

目标工作区的机器与 Role 完整目录查询原始退出 1，不能解释为空目录。一次受控 debug 只在内存提取 hostname 和错误枚举，发现实际依赖的 Loro Streams 端点：

- `api.streams-api-x.loro.dev`
- `control-b.streams-api-x.loro.dev`
- `control-c.streams-api-x.loro.dev`
- `presence.streams-api-x.loro.dev`

上述四个精确域名的无凭证 HTTPS 探测均为 curl 56、HTTP 000、代理 CONNECT 403，证明当前规则遗漏了目录同步服务。没有证书错误证据，未尝试绕过代理。源码 `getLoroStreamsShardUrls` 和 `getLoroStreamsPresenceBaseUrl` 按平台返回的同一后缀生成控制、数据、写入与 presence 分片；因此所需规则限于 `*.streams-api-x.loro.dev`，不放宽到整个 loro.dev。

doctor 0.1.1 增加显式 `--workspace` 目录探测，执行原生 machine list 的全部页，保留账户已认证与目录失败两个独立结果。新增测试覆盖失败不误报成功/空机器、完整分页与坏响应、参数边界，以及登录不误报注册；没有重新包装 session/schedule 业务。

本机 daemon status 退出 1，报告未运行；未启动 daemon，未创建会话或修改已有项目。原生 Codex login status 退出 0 且报告已登录，仅作为后续运行前提线索，没有读取、复制或导出认证材料，仍不能证明 Lody Agent 实际执行成功。

更新后的 `dist/lody4dot-0.1.1.zip` 共 23 文件、65674 字节，完整性检查通过；SHA-256 为 `35a1ac9cb234e61672337598993de7d1693daa1658116ecfdd1f82c445fcb8a0`，构建 receipt SHA-256 为 `329cb72be4bf65659ab1f6c3575663075aafde4377ce48878bcb35e91c4fcc57`。完整云安装脚本再跑退出0，53项测试通过；此复跑不登录、不启动服务。

本次测试身份只写到新建的0700私密临时目录，credentials.json实测0600；保存新网络草稿前已删除整个自有测试state，保留全局安全注入的变量绑定。没有把身份放入依赖或分发物，也没有证明平台可私密跨任务恢复身份。

当时目录、观察和受控任务需待该服务规则生效后继续。新增规则不是重复添加原来的 token 或四个域名；用户已选工作区无需重新询问。以下记录本次规则生效后的结果。

后续继续验证的发布传播、Codex 运行时与 host 范围见 [运行前提补充](runtime-findings.md)。该次独立准备没有真实模型任务结果。

## 分片规则生效与真实目录（0.1.2）

同一运行实例的 spec_revision/observed_spec_revision 更新为 **5**，observations_current=true，已包含 `*.streams-api-x.loro.dev`。正式配置无新草稿或待注入变量；现有全局 token 已可用。api/control-b/presence 的无凭证 HTTPS 请求不再遭 CONNECT 拒绝，curl 均退出 0，根路径 404。

新建 `0700` 私密任务状态后，真实登录和工作区查询再次通过。选定个人工作区的原生 machine list 全页查询退出 0、2 台机器、hasMore=false；agent-role list 确实为空，agent-config list 为 2 项，工作区目录中 `kind=local` 的项目为 1 项。没有把解析失败或无权限当作空目录。

原生 0.107.2 的目录 JSON 前后夹有同工作区的 `Remote Streams transport attached/detached` 日志。已定位发布源码中的两条精确消息及 compact JSON 输出位置；仅兼容唯一完整 JSON 及这两种同工作区消息，保留字段和分页校验。未知日志、跨工作区消息、多 JSON 和截断响应继续失败；stderr 仅提示忽略条数。没有采用任意截取最后一行或忽略全部非 JSON 的处理。独立差异审查通过。

修复后的真实 `doctor --profile control --connect --workspace ... --json` 退出 0：account authenticated、workspace_count=2、workspace_catalog pass、machine_count=2、all_pages=true、has_more=false；local_runtime 和 task_execution 仍为 not_run。21 项诊断测试及全部 **56 项**仓库测试通过。

真实 `session list --limit 5 --json` 退出 0，返回 1 个未归档会话；这是有界查询，不代表全量历史。`session observe --all --json` 退出 0，返回 2 个 synced/source=metadata 快照。另一个 agent 按 cloud-start → SKILL → discovery/sessions/compatibility 及准确帮助独立完成只读场景：完整机器目录 2 台 online、Role 确实为空；定点观察已有会话退出 0、ok=true、freshness=synced、source=persisted，存在 latestTurn。仅记录字段及状态，没有输出业务文本或标识，没有向已有会话发消息或取消任务。

这证明当前技能导航和真实发现/观察可用；all 的 metadata 不能冒充 persisted，已有会话的 persisted 读取也不能证明本次创建、模型执行或产物成功。agent 被提供了入口，不能证明新云任务自动加载。本机 daemon status 退出 1 且明确未运行；未启动 host 或建立测试会话。

当前剩余验收是新云任务的技能读取回执、私密状态跨任务边界，以及真实受控执行。已按官方大小/哈希下载并运行 managed Codex 0.160.1 的版本检查，但 bundled ACP 初始化仍失败；具体结果与 host 作用于全部可见工作区的限制见 [运行前提](runtime-findings.md)。不再要求重新配置 token 或重复发布已生效的分片规则。

完整 `.codex/cloud-install.sh` 退出 0，56 项测试、同锁复用安装和离线 inspect 通过；脚本不登录或启动服务。0.1.2 自包含产物构建通过，直接从产物运行真实 control+完整目录检查也退出 0。`dist/lody4dot-0.1.2.zip` 共 23 文件、69,005 字节，解压完整性通过；SHA-256 为 `bf8d2d1fe0b27486d0789939aad494b8051f1614523d4ecda0e7358857934626`，receipt SHA-256 为 `e61149fc1653782fcff61d2cd6a1943bccb26f1a092eb285931070c20f03a95e`。产物保留在忽略目录，不提交为源码。结束后已删除本轮自有私密认证 state；全局安全注入变量保留，没有新建环境草稿或把登录态放入快照。

## 已有远端 Agent 的真实验收（0.1.3）

用户明确授权“用已配置的agent来测试”，继续已选个人工作区。已复验2台机器online且canUse=true、2份已有配置；按明确类型选择唯一在线Codex配置。全程使用公开CLI、现有全局token和新建0700私密任务state；未启动控制端host/daemon，未新增机器、配置、项目或Role。

固定标题、省略repo/local-project/parent，`session create --workspace ... --machine ... --agent-config ... --prompt-file ... --json` 原始退出0，ok=true，返回的工作区、机器和配置均与选择匹配。执行端建立独立chat上下文，任务约束仅在OS临时目录创建input.txt及result.json；不声称OS强制隔离。首回合follow观察匹配userTurn并报告completed。

随后仅对这个新建会话发送一次只读 `session chat --json --wait`，退出0、ok=true并返回新turn标识。该回合要求重新读两份文件，回传base64字节及随机challenge的SHA-256。控制端从公开history获取回复并独立解码校验：input为65字节，逐字节与预设UTF-8输入一致；result为225字节，nonce、输入哈希、3行文本及逆序内容完全匹配；challenge哈希匹配。输入SHA-256为 `f0eb020f6939c19b062490387d3c497d7f2ff723c422126d105b46c5616a105e`，结果SHA-256为 `1d1b3bf40d4b03b411d18075e1cf8869f12ec9880514a647aba8737f56102e08`。

最终observe原始退出0、source=persisted、freshness=synced、latestTurn.state=completed、activeTurns为空，公开history有4条可见记录（两对user/assistant）。独立验收复核通过。artifact解析器的重复匹配数不计为额外磁盘读取；实际二次验证来自另一只读回合。公开history不暴露底层工具执行日志，产物证据为Agent回传后控制端校验，不称控制端直接读取远端文件系统。

这些结果证明该已有远端Codex配置的创建→执行→继续验证→持久化观察闭环。此前将本机daemon要求扩大到远端的知识错误已更正，并保留官网概括与0.107.2发布源码的差异记录。控制端的installation_id只读限制仍在，但不阻塞此远端路径；未用mock、改HOME/CODEX_HOME或复制认证。取消、其他配置/平台、高级操作、长期worker和新云任务自动加载均未据此标为通过。

本轮56项回归、结构和空白检查通过。重建时发现上轮从产物运行Python留下的一个`__pycache__`额外文件，构建器按保护规则拒绝覆盖；已完整保留旧目录后在新目录构建成功，没有放宽receipt检查。0.1.3插件ZIP为23文件、71,929字节，完整性检查通过；SHA-256为 `6b30af467ac907a8dbf39f09565f68cde224d2f0babbf25aa99aa64b37a2a3ea`，receipt为 `2c331adbd3e09370d111ee0e6d7d7b87c3f99bfa71d2755a8fe06f1a6d2b70de`。另有四文件验收包，包含Agent回传的input/result副本、脱敏校验摘要和来源说明，不含账户/资源标识；均留在忽略的dist。

已清理本轮0700私密认证state，保留全局token绑定；本次新建远端会话和验收临时文件保留用于追溯，未操作用户既有会话或项目。修正后的完整云启动说明已由后端确认status=saved、requires_publish=true；只更新start_skill，网络、凭证及安装脚本均未重配。该草稿供后续云任务复用，仍需环境设置中的发布；当前远端验收结果不依赖再次发布。

## 0.1.3 发布后的复验与高级能力边界

用户确认环境发布后，正式配置已无草稿，仓库ref为`a2e67962cba7cfdcb2e4c01fcec5a9bc644d0248`；start_skill与该checkout的启动说明逐字相同，SHA-256为`bb1e9001744505d3c250097e9eb42f6df5c0a831f67dd90e20935c6e52ba5811`。现有网络enforced、LODY_CLI_TOKEN ready/present，无待注入变量；网络spec_revision/observed_spec_revision仍均为5，不能由该编号未变推断源码或启动说明发布失败。没有重存配置、添加变量或再次制造待发布草稿。

完整cloud-install退出0：56项测试、同锁安装复用与inspect通过，CLI仍为0.107.2。前轮私密运行记录已不在当前/tmp；本轮另建0700 state，登录前verify-only退出4、类别authentication，随后显式login退出0并真实认证。control+完整机器目录退出0、machine_count=2。通过精确标题重新发现本次自有验收会话，发布后只读observe退出0、persisted/synced、latestTurn.completed、activeTurns为空。没有新建模型任务、操作用户既有会话或启动控制端daemon；本轮state已清理。

进一步真实只读查询均原始退出0：MCP和Role完整目录为0项、hasMore=false；GitHub已链接仓库为0项；Operation查询仅针对当前新私密本机store和自有requester，0项、hasMore=false，不能据此推断远端机器没有Operation。Schedule list使用offset=0、limit=100，返回`schedules=[]、matched=0`，未创建、暂停或运行调度。

Schedule stdout同样含两条精确Streams消息，但其JSON没有workspaceId。本次按请求中的确切工作区核对两种消息，要求唯一完整JSON及准确schema后读取，未将通用目录解析失败当空列表，也未放宽doctor账户/机器解析器。非空列表须依据nextOffset续页，不套用目录的cursor或all-pages。

Review做了无账户真实渲染尝试：依据原生review prompt编写覆盖a2e6796及其parent间15个变更文件的报告，使用--no-open，子进程移除LODY_CLI_TOKEN。报告/Git阶段无diagnostics，但Viewer下载失败，原始退出1，未生成HTML。CLI要求`lody-code-review-viewer@0.107.2`及SHA-256 `d1ba5702aa0bd441b40492bd916d6412f8b970e92683f7073878a36efbdb0649`；官方registry版本端点和jsDelivr文件均404。官方latest 0.81.1的包SRI通过，但模板哈希不匹配，未用于渲染，未改期望哈希或关闭TLS。

这是上游匹配产物缺失，不能通过重复发布环境或只增加fallback域名修复。只能等待官方匹配文件，或由公开LODY_REVIEW_VIEWER指定与CLI固定哈希完全相同的文件后重试；不使用其他模板冒称成功。报告和脱敏摘要留在忽略的cache；临时state已清理。全部高级能力与条件见[支持矩阵](support-matrix.md)。

当前工具无法创建/附着独立云任务，因此发布确认和本次当前实例复验仍不等同新任务自动接入。剩余外部步骤见[新任务验收](fresh-task-acceptance.md)；既定路线是start_skill云接入，原生插件注册单独保留未验，不作为该路线的额外必选门槛。

## 运行回合的精确取消验收

2026-10-20，继续用户授权的已有远端 Codex Agent 测试，仅使用前述本任务自建的验收会话。新建0700私密认证state后真实登录；按完整标题唯一匹配会话，并检查未归档、messageQueueCount=0、persisted/synced/idle、latestTurn.completed及activeTurns为空。发送前再次观察，确认最新回合未变且仍无活动回合；没有操作用户其他会话。

只发送一次`session chat --json`，提示约束为一个45秒的前台等待命令，不创建文件、访问网络或凭证、变更配置、启动后台工作或重试。保存返回的userTurnId后，observe实际显示persisted/synced/running，唯一active turn的userTurnId匹配本次请求，并取得其assistantTurnId。随后以`session cancel SESSION_ID --workspace WORKSPACE_ID --turn-id ASSISTANT_TURN_ID --json`精确取消；该参数使用assistantTurnId，不是chat返回的userTurnId。

chat、运行中观察、cancel及取消后观察的原始退出码均为0。取消响应ok=true、response.success=true，没有alreadyStopped=true；最终observe的userTurnId及assistantTurnId均与本次选择完全匹配，source=persisted、freshness=synced、latestTurn.state=canceled、state=idle、activeTurns为空。控制端重新同步时若发现目标不再匹配，可返回alreadyStopped，不能算本次取消成功。后续源码复核补充：派发后的陈旧请求也可能被执行端忽略却返回success:true，Operation inbox暂停还可能影响同一执行的后继回合；精确turn参数不是所有协作流程的原子隔离保证。本轮成功依据对应回合的持久化终态，而非只看ACK。

这些证据仅证明该配置的Lody运行回合被精确取消并持久化。公开history不包含工具日志，没有据此证明等待命令已启动、远端进程收到何种系统信号或被即时终止。未测试超时恢复、其他配置/平台、长期worker或独立新云任务加载。自有私密认证state已删除，全局token绑定保留；未启动控制端host/daemon、修改远端配置或重新保存云环境草稿。原0.1.3发布物保持不变，本轮仅补充验收记录。

本轮仓库结构、空白及56项回归检查通过；4份改动文档的本地链接检查通过，差异未包含本轮真实资源标识或凭证。

## 会话维护往返与知识修正

2026-10-21，继续用户授权范围，在本任务自建验收会话补测rename、archive与restore。新0700私密state真实登录后，先以`session list --all --json`同步完整元数据，不加limit；核对完整标题与既有ID唯一匹配，并按parentSessionId和openedBySessionId检查没有关联后代。show/observe确认未归档、idle、persisted/synced、队列0、activeTurns为空、最新回合仍为此前canceled；公开history --all实际返回6条可见记录。

使用显式session/workspace/--title完成一次临时改名和还原标题，各阶段重新读取show/observe核对标题、空闲状态及最新回合。再次确认无后代后归档，响应archivedChildSessionIds=[]，后续同步读取isArchived=true；再确认目标及关联范围后恢复，响应restoredChildSessionIds=[]，后续isArchived=false。所有原生命令退出0。最终原标题、未归档状态、空队列及空活动列表还原，persisted/synced；latestTurn的标识、状态及字段与基线一致，6条公开transcript条目的规范化JSON摘要前后匹配。该比较只涉及本次可见历史，不推导底层日志或所有生命周期数据均未更新。

独立源码复核发现原知识中“archive/restore可逆整理”的概括不完整：collectSessionArchiveTargets按parentSessionId ?? openedBySessionId递归，readSessionOperationTargets的restore仅根与直接parent子项，不能保证完整回滚；执行端releaseArchivedSessionRuntime释放终端、预览、ACP和会话运行状态，并安排关联worktree GC。终止失败仍可能保留进程，restore不承诺恢复同一进程或还原已发生的磁盘清理。没有为验证级联而创建或操作其他会话，未测试进程恢复或worktree清理，本次会话未附加repo。已将准确边界、取消的assistantTurnId用法及陈旧ACK竞态同步到技能、命令索引和来源记录，版本升为0.1.4。

本轮56项回归、结构及构建检查通过；新包22个内容文件加receipt共23文件，直接从包执行安装器reused=true及inspect均通过，固定CLI仍为0.107.2，锁摘要未变。`dist/lody4dot-0.1.4.zip`为74,514字节，ZIP与receipt逐文件哈希和完整性检查通过；ZIP SHA-256为`3d4e41b7f37272a05e604e6aac4826f9fa47eb3dfe0eaf44f7be44c7c19bc54d`，receipt为`c51eb2bd810a75152b1556a79ae9203f4af86da09f45c53417dde81c5ee291fc`。产物保留在忽略目录，旧0.1.3包不覆盖。

自有认证state已删除，保留全局变量绑定；没有新模型回合、永久删除、向其他会话发起维护命令、新增远端配置或启动控制端daemon。没有据此断言执行端后台GC或所有其他磁盘状态均无变化。已发布环境仍以0.1.3源码为准，未新建云草稿，不能把0.1.4源码与包完成当作云环境已升级。T09独立新云任务回执和T12整体交付仍blocked；Review匹配上游资源、本机ACP只读限制及其他未运行项不改为通过。

同日另以两次无账户公开GET复查Review匹配资源，各限时20秒：registry的lody-code-review-viewer/0.107.2版本端点与源码首选jsDelivr的0.107.2/standalone.html均实际连接成功但返回404。没有重跑已知无法取得模板的渲染，也没有替换版本、哈希或网络配置；该上游阻断尚未解除。

## 用户截图回执与加载判定

2026-10-21，用户提供另一项验收结果的截图，报告Lody0.107.2安装检查通过、使用注入凭证完成认证、两个工作区的机器目录连接和完整分页通过；技能和启动指引是手动找到并读取，本次未观察到自动加载。截图还报告临时登录态已清理、注入凭证未改动，未启动daemon或创建模型任务。本节记录用户提供的摘要，不等同取得该任务原始命令退出码、首次入口发现记录或平台任务元数据；没有在本会话重复这些操作。

按产品方案的“插件已加载”定义，新任务实际读取入口并能定位随附参考与诊断工具才是基本读取要求；并非要求技能全文自动进入上下文。agent在目标任务下自主检索并读取，与用户直接指定路径、平台启动指引引导及原生插件自动发现，是不同的入口来源。截图的“手动”未说明是哪一种，不能据此判定加载失败，也不能推断start_skill已送达或原生插件已注册。

当前只读配置核对：正式源码ref仍为a2e6796，无待发布草稿，start_skill与仓库云启动说明一致。保存了指引不证明平台已在截图对应的任务中交付它；没有据截图重写启动说明或要求重复发布。

后续只在截图对应的原任务补来源与版本记录：首次入口来自平台指引、AGENTS/README、自主搜索还是用户给路径；实际源码SHA和插件清单版本；已读入口/参考路径；已有同锁重复安装记录或如实标未运行。先查该任务已有记录，不重复登录或资源查询。尚无该任务标识或实际版本证据时，明确保留来源未证实，T09/T12继续blocked。

## 0.2.0 多宿主基础能力与无账户验收

2026-10-21，按c1任务卡完成共享知识、兼容诊断、Linux平台边界、纯离线交接和依赖bootstrap。CLI仍固定0.107.2，依赖锁未改。仓库结构检查和108项测试通过：知识3、诊断33、平台4、安装15、构建11、交接27、生命周期7及原仓库8项。独立审查覆盖诊断来源读取、交接引用一致性、bootstrap副作用与移位分发；发现的深层JSON、FIFO、目标冲突及缺执行位置问题均补回归并修复。

全新上下文Agent从根目录AGENTS/README自主检索到技能与协作参考，正确选择云控制/远端执行、超时后按原引用对账、区分裸ID命名空间与所属执行器；没有联网或调用Lody。这是知识选择与显式读取证据，不是平台自动注入或第二独立宿主证据。

0.2.0包为28个内容文件加receipt共29文件，移位检查及包内工具帮助入口通过。从包执行真实`bootstrap --prepare`安装/inspect通过，来源报告bundle/runtime均consistent；现有prefix的`--repair-missing`只运行doctor，认证、daemon、业务恢复均not_run。打包未含私密state或凭证。ZIP保留在忽略的`dist/lody4dot-0.2.0.zip`，96,208字节，SHA-256为`3414bbb21152ccc6c326fa1eb51139af54069f21adc067cbc35aadfcdb9a4bb7`；receipt SHA-256为`d31209d019de4935020fa4de8a16a8ef7a7775f65afab09e66eca08716ad58e3`。哈希仅用于本产物比对，不提供签名、可信身份或业务真实性。

doctor保持schema1旧字段/退出码，新增时间、真实通过的检查范围及本地来源一致性；账户目录和任务能力分开。Win32/Darwin模拟可返回结构化退出5，但没有据此宣布macOS/WSL/Windows安装支持。handoff的27项测试无网络、登录、派发或输入改写，明确8项not_verified；fixture通过不等于任务成功。bootstrap的7项行为测试不代替真实宿主重建或Dot存储reset hook。

用户确认环境发布后，复查时正式配置无草稿且含三个OpenAI域名，当前实例仍revision5及旧5条Lody网络规则，官方三站CONNECT403；官方GitHub源码可读。当前注入凭证ready，本轮显式私密state认证及个人工作区完整目录通过，唯一已授权在线Codex配置可用。随后真实双端子范围及0.2.0升级草稿见下文；原截图对应的T09/T12仍另行保留。

## 0.2.0 Linux云端与Darwin Agent的实际交接

2026-10-21，复用用户此前授权的个人工作区与唯一可用Codex配置，新建一个无repo/project/parent的自有验收会话。代码来源固定为`2cc74de62952763e2cb0559e268b055e19f55b53`；没有新增机器、Agent配置或Role，没有启动控制端daemon。当前云端负责协调与复验，远端Agent单独写临时产物。

| 位置 | 实际能力与证据 | 本轮范围 |
| --- | --- | --- |
| Linux/x86_64云端 | 0.2.0工具与0.107.2CLI；真实Lody身份、目录、派发、持久化观察与history | 控制及Agent回传字节复验；本机ACP执行仍未通过 |
| Darwin/arm64远端 | Agent报告Python3.11.3；控制端发送96,208字节ZIP，远端解包后回传匹配的receipt/技能摘要 | 此次明确指示下的技能读取、临时产物生成和只读读回；没有原生插件注册证据 |
| 远端独立Lody客户端 | PATH未发现Node、npm或LodyCLI；宿主内置Agent和独立CLI分别识别 | 未运行本端Lody查询，未安装macOS受管runtime，不宣布该平台安装支持 |

首回合报告`DOWNLOAD_FAILED`，没有源码或结果；原生回合虽为completed，业务验收未通过。以该真实回执填写的无产物handoff在result阶段返回blocked/3、`result_artifact_required`。确认该范围后，在原会话发起一个明确的新附件交付回合，通过公开`session chat --attach ... --prompt-file ... --json`传递自包含ZIP；没有重复create或将ACK当成收件成功。

远端按附件任务报告解包并读取SKILL与collaboration参考，回传的build receipt及两份技能摘要与控制端逐项相符。回执未单独包含原始ZIP长度/摘要，因此收件证据限于解包后的内容回执，未独立证明远端原始ZIP逐字节一致。此次入口记为`task_directed_read`，不能称平台自动注入。原生附件可能在会话工作目录写`.lody/attachments`并更新该目录所属Git的`info/exclude`，不承诺全部附件处理只写临时目录。

产物回合生成273字节确定性JSON。第三回合仅重新打开原input/result，不重写；返回完整字节、长度、SHA-256、`SHA256(challenge_utf8 || result_bytes)`及文件stat未变声明。控制端验证两次结果字节、输入字节、随机challenge、来源摘要和原session/user/assistant引用全部匹配。结果SHA-256及脱敏摘要保留在忽略的`dist/lody4dot-0.2.0-evidence/`。证据来自Agent读回；公开history无底层工具日志，未据此宣称控制端直接访问远端文件系统。

两个有效回合均曾观察为persisted/synced/completed；最终第三回合与准确user/assistant引用匹配，无activeTurns。真实handoff记录在本地离线校验为pass/0，仍保留8项not_verified；实际字节检验由上述独立步骤完成。该链路证明云控制、远端显式技能读取和产物交接子范围，C07要求的第二独立控制端自身Lody查询仍缺入口，含Dot闭环尚未成立。

## 0.2.0 依赖和控制身份恢复子范围

在新的自有临时prefix实跑包内`bootstrap --repair-missing`：首次doctor/missing_runtime→install→doctor成功；第二次仅doctor成功，runtime一致性通过，认证/daemon/任务恢复均not_run。清理了这一自有prefix，仅保留脱敏结果；未删除当前受管安装或用户状态。完整新版cloud-install脚本亦退出0，108项检查及同锁准备/inspect通过。

另建全新0700控制端state，以已注入材料显式认证，没有复制旧登录态；新CLI进程沿原生引用只读定位上述同一会话、终态及history，并完成字节复验。这证明控制客户端和私密state重建后的原任务对账子范围；没有实际重建云主机、测试新宿主首次启动或验证Dot存储hook。两个测试登录目录均已删除，保留全局变量绑定；私密业务引用和无认证文件的交接记录仅在忽略目录中保存。

## 0.2.0 云配置升级草稿

在完整遍历实际workspace并核对唯一Git根、完整HEAD和远程身份后，保存0.2.0升级草稿，返回saved/requires_publish=true。首次读取回执revision15、源码为代码/包验收基线`2cc74de`，mount仍为`mymcp-4-codexcloud`；install_script和start_skill与仓库新文件逐字一致，8条自定义网络规则沿用。交接时草稿来源同步到含最终任务结果的完整HEAD，具体固定SHA由配置读取回执确定；后续仅文档更新，已验收代码与包字节保持不变。

新准备入口调用`bootstrap --prepare`；启动入口要求读取技能后调用`--repair-missing`。工具只保存草稿，未发布、重启或切换当前实例；正式云来源仍按0.1.3基线记录。发布后的实际读取、安装快照及对应任务版本仍须另取回执。Dot官方产品/工具/存储事件契约和第二独立控制端条件继续保持明确缺口，不注册猜测的reset hook。

## 0.2.0 发布后的当前实例与原任务恢复

2026-10-21，用户确认再次发布后，正式配置无草稿，来源固定为`d27f1a0e6ec2890cd60e301118fc925d32872d46`，对应插件0.2.0；本轮开始时checkout相符。运行观测`spec_revision/observed_spec_revision=9`、`observations_current=true`，实例运行且连接。网络和运行变量的readiness字段仍为`unknown`，不能替换为ready或enforced；以下实测结果独立记录。

读取当前技能、协作参考和云启动说明后，实际执行`bootstrap --repair-missing`，只运行doctor且退出0；插件0.2.0、受管CLI0.107.2及来源收据一致，`verified_scope`仅node/runtime。没有重装依赖；bootstrap的认证、daemon与任务恢复均not_run。该手动读取不证明平台首次送达，也没有旧boot/实例基线可证明整机重建。

随后在本任务新建的0700身份目录，显式复用已注入材料完成真实认证；它是独立步骤，不把上述bootstrap的not_run改成已认证。只读沿此前0.2.0验收的准确workspace/session/user/assistant引用读取observe和history：来源persisted、freshness synced、目标读回回合completed、activeTurns为空；原读回回执完全匹配，恢复出的本地产物摘要与原记录一致。没有create/chat或任何新模型回合，没有复制旧登录态。仅删除本次新建身份目录，既有全局变量绑定与远端会话保留。

脱敏摘要保存在忽略目录`dist/lody4dot-published-spec9-evidence/summary.json`；它明确保留`infrastructure_host_rebuild_proven=false`、`startup_instructions_received=unknown`和`metadata_readiness=unknown`。这补齐了发布后控制端身份重建及原任务对账子范围，不代替C07第二独立控制端查询、C08真实主机重建或T09旧截图任务的入口来源。

## Dot官方契约、指引与0.2.1候选

本轮以正常HTTPS读取9篇OpenAI官方Help正文，均HTTP200，确认Dot是ChatGPT的常驻Agent产品；其自有云电脑、所创建的Codex云任务、获授权的本地电脑分别识别。官方共享插件连接限定在已授予范围；浏览器登录、Dot本地访问、CLI私密state、模型身份和环境变量不会因此自动迁移。官方来源、读取范围和完整安装路线见[宿主契约](host-contracts.md)。

网络策略快照现含三个OpenAI域名，帮助站及官网索引实际可读；开发站与精确Plugin Management地址仍CONNECT403，已停止相关请求，未修改代理、CA、TLS或云配置。已读正文及有界检索尚未给出Dot自有电脑的prepare/maintenance/周期存储重置hook；Dot主动Reset不等于磁盘事件，Codex Cloud默认最多7天的VM恢复规则也不能套到Dot电脑。

据此修正环境指引、两张图、共享技能、c2方案和任务卡，新增随包`hosts/dot.md`及[Dot/独立控制端验收运行单](dot-acceptance.md)。本地HTTP渲染同步SVG，图源解析、目视和独立语义审查通过；临时渲染依赖与浏览器profile均不进入插件。另备妥无认证材料的私密`readonly-acceptance.json`，用于合法独立任务沿原引用复验；它不是handoff.py协议，当前没有用子Agent冒充第二独立云任务。

用户随后要求CLI版本不要严格验证，已将安装、诊断和认证中的实际CLI版本差异/探测失败改为warn，继续按真实命令结果执行。0.107.2是知识及默认安装输入基线，收据分别记录实际观测与基线；不再用收据中的CLI版本拒绝执行。安装锁/目录完整性和help/native真实失败仍分别处理，复用安装的收据采用原子更新，写失败保留旧记录。

新增显式`doctor.py --check-updates`，只对固定npm latest地址做一次查询，整体最多5秒、响应限64KiB，保留代理/CA、拒绝重定向，不传认证头或自动升级。旧版、不可比较或查询失败均warn，默认inspect和bootstrap不查更新。真实查询本轮实际CLI与npm latest同为0.107.2，退出0且账户未查询；旧版、探测超时、无效输出、网络失败等非阻塞路径另用fixture验证，不能把当前latest值当作长期不变事实。

最终0.2.1代码来源为`6493a58098ba436ccb3067350c699f8122d2f36f`，候选包保持原依赖锁。仓库结构和127项回归通过：诊断41、版本策略4、安装21、生命周期8、知识3、平台4、构建11、交接27及原仓库8项。实际builder输出29个内容文件，Dot说明纳入receipt和允许清单。从最终包执行安装器`reused=true`、实际CLI0.107.2；再执行`bootstrap --repair-missing`只运行doctor且通过，插件0.2.1、bundle/runtime收据一致。未登录、重装依赖、启daemon或发起业务；bootstrap文本也会展示版本warn。

最终候选ZIP为30个文件（含receipt）、107,453字节，`.codex-plugin/plugin.json`直接位于ZIP根，无外层目录。ZIP CRC、完整文件集合和逐文件receipt摘要均匹配。ZIP SHA-256为`26917b7897b0c059737c62098efe2a3904968b44201395eedeff30775843407d`；receipt SHA-256为`e86b7880a1fa209396e3acbe1db502bced850095c4fa52160384f3a0104ce34d`。旧0.2.0包及追加版本策略前的内部候选分别保留，生成物仍在忽略目录；哈希只用于完整性比对，不是身份签名。

此包采用已核实的Codex0.163.0格式；ChatGPT上传扫描、ZIP包装接受、安装与Dot实际读取尚未运行。GitHub marketplace导入是官方支持的路线，但不会运行本仓库builder，因此未添加指向缺失skills的源码catalog。正式云来源仍是0.2.0，本轮未新建升级草稿；0.2.1的新提示策略仅适用于执行新版脚本的端，未来任务若要使用新版须选用对应源码，不能把本工作副本完成当作正式环境自动升级。当前任务可以继续验证，无需重配token。当前工具没有插件UI导入或建立独立平台任务入口，相关真实验收及未知Dot生命周期契约继续在队列保留。

## 远端内置MCP只读查询与C07有限双端验收

在CLI版本提示策略交付后继续检查替代入口。本机0.107.2公开发布物的`buildBuiltinMcpServers`及ACP new/load/resume路径会在上下文成立时加入内置Lody MCP，可使用HTTP或宿主`process.execPath`，不要求Agent shell的PATH有Node/npm/CLI。源码存在不证明远端实际注入，因此没有仅凭这一发现关闭C07。

随后复用既有授权的Darwin/arm64 Agent及本任务原验收会话，新增**一个明确的只读模型验收回合**。它不是重发此前产物业务；此前发布后身份恢复阶段的0新回合结果仍成立。控制端另建0700私密身份显式登录，先确认原准确读回回合persisted/synced/completed、无activeTurns，再只发送一次该验证目标。没有新增会话、配置、Role或服务。

远端回执报告实际暴露内置MCP，并成功调用`mcp__lody__lody_session_status_many`和`mcp__lody__lody_session_history`。控制端逐项核对两次参数只指向原session/URI：状态返回1项、machine online、observation fresh；execution busy对应正在执行的验证自身，不当作旧产物未完成。history返回8项、无后页；远端按原两次assistant引用从查询结果取得旧回执，返回完整273字节结果、SHA-256及challenge重算值。

控制端验证新nonce、准确原生引用、完整base64解码字节、长度、SHA-256、原challenge及远端computed各项全部匹配。远端声明未修改文件。最终本次新验证回合persisted/synced/completed、无activeTurns；本次临时控制身份已清理。脱敏结论为`dist/lody4dot-0.2.1-evidence/native-mcp-summary.json`，准确引用/提示/完整回执仅存忽略目录私密位置。

结合此前Darwin解包读取技能、单写产物和Linux控制端复验，C07的两个实际宿主协作及各端原生查询子范围已具备证据。远端使用宿主合法内置MCP，不另装CLI、不共享控制端登录文件；不再以PATH缺少CLI阻塞此范围。证据强度为远端Agent的结构化调用回执和控制端独立字节核验，公开history没有底层工具trace；不宣称直接访问远端FS、macOS受管runtime安装、原生插件注册或Dot接入。C05首次独立加载、C08真实宿主重建及C09/C10含Dot验收仍保留。

本次只新增验收记录，插件源码、0.2.1候选包字节和127项测试结果未变。

## spec11发布复查与文档归档

2026-10-21，用户再次发布后，正式配置读取无草稿，来源仍为`d27f1a0`/0.2.0；运行spec/observed均11且current=true。实际checkout保留0.2.1代码，执行完整`.codex/cloud-install.sh`退出0：仓库结构及127项测试通过，bootstrap prepare中的install/doctor均通过，认证/daemon/业务恢复not_run。CLI版本策略保持只告警，没有为验收创建新的Lody模型回合。

当前内核启动时间为2026-10-21T07:51:35Z，晚于旧spec9观测时间；旧/tmp官方资料缓存不存在，dist验收资料保留。已在忽略的`dist/lody4dot-environment-checks/spec11/`保存当前启动摘要和本次准备结果供后续比较。没有旧boot标识或平台重建回执，不能据此宣布特定VM重建、磁盘reset、Dot生命周期hook或独立任务首次启动。网络/变量readiness仍unknown，实际检查结果单独记录。

发现并读取Codex CLI0.163.0正式`cloud exec/list/status`帮助。一次`codex cloud list --limit 1 --json`实际发起任务目录请求，但返回HTTP request failed；其PATH aliases只读警告不是已证实的主因。随后对chatgpt.com作无凭证HTTPS检查，代理明确CONNECT403；当前规则未包含此目的地。未发起cloud exec、未猜Cloud ENV_ID，也未将托管实例ID当该服务环境ID。后续升级准备保留原规则并追加chatgpt.com及官方格式指南所在learn.chatgpt.com，实际保存与发布分别取证。

另按用户要求迁移14篇专属文档至本目录并去除冗余前缀，9份图资源移至diagrams，新增README阅读索引。迁移后的本地链接及渲染命令检查通过，8份非Markdown图资源字节完全相同；独立审查确认旧文档除路径外事实和命令语义不变。开发规范写入AGENTS与[仓库架构说明](../architecture.md#文档归档规范)。能力源码、CLI依赖锁和已验收候选包字节均未因文档归档改变。

在完整遍历/workspace并确认唯一项目Git根后，保存0.2.1升级草稿，回执saved/requires_publish=true；读取revision18确认源码为本轮验收/归档基线，install/start与对应仓库文件逐字一致，10条自定义规则正好是原8条加chatgpt.com和learn.chatgpt.com。/workspace/.git经核实为空的非仓库标记，两个node_modules依赖目录不声明为项目checkout；未删除或移动任何checkout。未重配变量/凭证、发布或切换运行实例。交接时仅同步包含最终记录的完整HEAD，测试代码和候选包字节保持不变；源码固定SHA以最终配置读取回执确定。

## 复现命令

在仓库根目录运行：

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 plugin/lody4dot/scripts/install.py --json
python3 plugin/lody4dot/scripts/doctor.py --profile inspect --json
env -i PATH="$PATH" node tests/lody4dot/verify_workers.mjs /workspace/.tools/lody4dot/current
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot --json
```

真实连接与执行结果只能在前提满足后追加，不能用上述离线通过替代。
