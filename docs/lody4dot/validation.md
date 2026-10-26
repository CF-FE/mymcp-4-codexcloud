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

## spec12正式发布与0.2.2用户setup候选

2026-10-21，本次正式配置已固定`ed9096b837edd31a4446a8db1d49159b42262fd5`，对应0.2.1；无草稿，spec/observed均12、observations_current=true。工作副本开始时与正式来源相符，编辑前离线启动检查通过；随后开发0.2.2候选。网络/变量元数据readiness仍unknown，与下述实测分别记录，没有再保存草稿、发布或重配凭证。

四篇此前部分受阻的官方精确地址本次HTTP200：Plugin Management、Package your plugin、Dot computers and apps、Dot getting started。来源与摘录见[宿主契约](host-contracts.md)。官方接受现有兼容清单；新portable清单与OpenAI overlay的规则已记录，但本轮不迁移双清单。明确可用的是安装后**用户运行setup**，不是安装自动执行、环境准备或存储重置hook。ZIP包装的UI接受、导入扫描和实际调用仍未验收。

Cloud CLI0.163.0的最小只读`cloud list --limit 1 --json`返回HTTP401，本地`codex login status`同时报告ChatGPT登录。二者只说明本地登录状态与Cloud任务API授权不能等同；401的具体原因尚未知。历史CONNECT403不再作为当前原因。未提交`cloud exec`、猜Cloud ENV_ID、复制身份或改HOME；此缺口不阻塞本轮离线实现和Lody恢复对账。

### 不同内核上下文的有限恢复

spec11保存的实际观测为08:01:10Z、内核启动07:51:35Z；本次内核启动08:55:43Z且私密boot摘要不同，启动晚于旧实际观测。这支持不同内核启动上下文的结论。旧dist证据与受管运行时仍可读，prefix内目标、锁摘要、实际锁与收据一致；不由此推断准确VM身份、磁盘曾清空或恢复机制。

本轮对账期间工作副本已含未提交0.2.2候选，HEAD仍ed9096b；`c08-runtime-summary.json`及bootstrap原始provenance均据实际记录0.2.2，不能将这次脚本调用写成纯正式0.2.1源码安装验收。`bootstrap --repair-missing`退出0，**仅doctor**，未运行install，不填reused；既有CLI0.107.2保持不变，bootstrap自身认证/daemon/业务恢复not_run。

另建0700私密state，经现有auth适配器单次真实认证，再沿原工作区/session精确引用只读observe及完整history。23项核验全通过：persisted/synced/completed、无activeTurns，原8条历史及artifact/readback/MCP三份结构化回执一致，准确user/assistant引用、273字节、SHA和原challenge均重算匹配。没有新模型回合、daemon或资源维护操作，临时auth在finally清理，注入绑定保留。摘要在忽略的`dist/lody4dot-environment-checks/spec12/`，原始引用/响应只留私密子目录，不入库。

C08的“Codex发布后不同内核上下文恢复”子范围完成；准确VM/磁盘重建机制、Dot lifecycle、独立新任务首次接入与平台首次送达均未由此证明。入口来源是本会话显式读取，不能冒称平台自动加载；旧T09截图来源仍单独补证。

### 官方用户setup的本地候选

0.2.2代码来源`727a18c3e784f22b0ad2165047ced4780272207e`，在兼容清单声明`extensions.com.openai.onboardingSkill: "./skills/lody4dot-setup/SKILL.md"`；唯一源码为`skill/lody4dot-setup/SKILL.md`，薄入口复用核心和bootstrap。它识别真实执行器、平台/工具和自有prefix，再选择离线检查、获授权准备或现成合法工具路线。版本仅warn，默认不登录、不注册machine、不启daemon或重发业务。局部边界与保留的所有权见[c2方案](collaboration-development.md#4-模块所有权与依赖)。

结构检查及**132项测试**通过：构建15、诊断42、版本策略4、安装21、生命周期8、知识3、平台4、交接27、仓库8。新增回归检查错误/包外/缺失setup目标与资源、symlink、额外setup资源拒绝及旧产物保留；新入口修改在来源核对中为mismatch。独立审查发现的builder接受额外setup资源、provenance却不认可的不一致已修复，薄目录仅允许SKILL.md。

自包含包为30内容文件加receipt，ZIP31文件、110,840字节，CRC及全部receipt摘要匹配，`.codex-plugin/plugin.json`直接在ZIP根。ZIP SHA-256为`37e9bc335782cacfcf4a9c7db68865c1b2fd349ce589415cf341d52737082faa`，receipt SHA-256为`c579c92afda15ac5c7ce139441659545575832d35911f01134f583dcda6f54ac`。从移位包运行bootstrap仅doctor通过，包内provenance consistent、插件0.2.2；无登录、安装或业务操作。旧0.2.1 ZIP摘要保持不变，生成物仍仅在忽略dist内。

这些是本地分发与依赖检查证据。官方要求的安装后在新对话及安装所在对话分别运行setup、ChatGPT/Dot原生UI接受和真实Lody工具闭环，仍由C05/C09/C10分别验收；不因候选完成要求重复发布当前正式环境。

## spec14观测与运行中恢复补测

2026-10-21，本轮正式配置仍固定ed9096b/0.2.1且无草稿，发布不自动将固定ref升级到main；实际干净工作副本从1d4ee0c/0.2.2开始。本次spec/observed14、observations_current=true，网络元数据enforced，两个既有变量ready。这更新了spec12的unknown，历史值保留原义；实时快照统一见[当前环境与下一步](../../.codex/agent-state/todo.md#当前环境与下一步)，其他文档不重复维护。

依赖bootstrap仅doctor退出0，认证/daemon/业务恢复均not_run。最小Cloud CLI查询只重试一次，退出1、HTTP401且无403，未提交任务或猜Cloud ENV_ID。没有修改云配置、保存草稿或重配凭证；环境发布不能替代Cloud API实际授权。初始只读探针摘要在忽略的`dist/lody4dot-environment-checks/spec14/summary.json`，其0新模型回合仅属于这个初始探针，不包括下面独立实验。

有界调查检查5条插件帮助命令及官方0.163.0源码，确认`manifest.rs`的`resolve_openai_onboarding_skill`支持当前嵌套字段，但CLI没有独立setup/validate/dry-run入口。`plugin list`不输出onboarding_skill，且加载身份管理器，未执行它来冒称setup调用。C05/C09仍待合法产品界面分别验证新会话与当前安装会话的setup。C01原卡已满足有界资料核实条件：未知hook原本就允许记录unknown并停止相应分支；独立复核后收口done，不把UI接入或未公开hook加作隐藏门槛。

### 运行中观察进程和身份清理后的恢复

复用用户已授权的个人工作区、已有Darwin Agent及本任务自有验收会话，仅发送**一次新验收chat**，不重发旧业务。请求前保存私密意图、nonce、合成输入、预期结果和challenge；核对原准确session/machine、persisted/synced/completed、无activeTurns及8条可见历史。未显式查询队列数量，不额外宣称队列为零。新任务只在远端独占临时目录生成新产物，45秒前台有界等待供控制端观察；不改旧文件或配置，不创建后台进程。

A使用新0700身份显式登录，唯一chat ACK保存userTurnId，再由观察快照获取匹配的assistantTurnId。真正启动`observe --jsonl --follow`子进程，其自身日志收到准确回合的`running`快照及ready；单次JSON旁证也匹配。确认子进程存活后发送SIGTERM，等待退出0，再删除A身份目录。退出仅停止该本地观察进程，没有发送cancel；整个协调脚本并未退出，不能写成控制主机重启。

B使用另一新0700目录显式认证，没有复制A身份/缓存；从已保存原生引用恢复观察。前4次查询仍为同准确user/assistant的persisted/synced/running，第5次为persisted/synced/completed、无activeTurns。最终完整history为10条：原8条逐对象完全一致，只新增本次user/assistant两条。

从准确新assistant历史中读取Agent的结构化产物回执，控制端与独立只读审查均重算通过：完整274字节、JSON、nonce、长度/SHA及随机challenge全部匹配；Agent报告等待约45.005秒。产物证据来自Agent回执及本地字节核验，公开history没有底层tool trace，不宣称直接读取远端FS或独立观测远端sleep起点。没有调用session/machine/config创建命令、启动daemon或发送取消请求；登录副作用与模型验收分别记录，不称零写入或由login推断机器登记结果。两临时身份在finally清理，注入变量绑定保留。

本次新增模型回合为1，C08仅增加“观察进程退出与身份丢失后的同turn恢复”子范围。它不证明控制主机/VM重建、真实磁盘reset、结束通知完全未发生、Dot lifecycle或独立新云任务首次加载。脱敏结果在忽略的`dist/lody4dot-environment-checks/spec14/inflight-recovery-summary.json`；原生引用、提示、历史及产物仅存其私密子目录。独立审查确认follow自身快照、两身份清理、同turn持续运行与产物核验均成立，无需补跑。

本轮没有改0.2.2源码/包字节或CLI锁，旧ZIP摘要保持一致；再次执行根目录结构检查、132项全量回归及差异检查均通过。本轮环境状态与证据整理仅修改项目文档和任务记录。

## Agent配置、Role与Project关系核实

2026-10-21，用户询问能否基于已配置Agent创建多个角色，再用项目组织角色，以及是否已验证。本次仅只读核对`0.107.2`公开帮助、已安装发布源码和历史验收；没有生成角色提议、保存角色、登记项目或发起新模型任务。本轮官网请求未取得正文，故不将此结论扩大为其他版本或所有UI的功能保证。

| 关系 | 已查到的契约/源码 | 真实验收范围 |
| --- | --- | --- |
| Agent config与Role | 多个不同Role可引用同一machineId+agentConfigId；Role加入角色说明及提示词前缀，执行时可应用保存的运行设置 | 既有配置执行已测；多个Role实际创建、保存和执行未测 |
| 创建Role | `agent-role create/update`只发布提议卡片，须请求用户在Lody保存；该版本create字段限name/description/promptPrefix/machineId/agentConfigId，初始runConfig为空 | 之前只做过完整Role目录查询，当时0项；不能把提议成功算持久化完成，或承诺CLI可编辑全部运行设置 |
| Project | 公开CLI为`project add/delete/list`，add登记当前机器本地目录；会话项目引用可为local project或GitHub repo | 只读完整目录查询已测，未测add/delete，也没有在已有项目中写文件 |
| Project与Role | 创建会话可组合`--agent-role`与`--local-project`或`--repo`；Role先确定实际机器/配置，本地项目须属于最终目标机器 | 可确认“按某Role执行某项目任务”的接口；未核实“Project持久拥有一组Role”的绑定，不能据此断言其他UI没有组织功能 |

源码依据为官方[0.107.2发布物](https://registry.npmjs.org/lody/-/lody-0.107.2.tgz)中的`AgentRoleCreateProposalSchema`、`applyAgentRoleProposal`、`agentRoleWriteCommand`、`resolveAgentRoleCreate`、`ProjectRefSchema`及`projectAddCommand`。会话保存project和agentRoleId/revision，帮助快照列明Role覆盖machine/config/mode/model/config-option。CLI提议还会路由到当前登录机器的会话工具；角色的目标machineId只是绑定字段，不能用远端会话派发成功推导无daemon控制端也能生成提议。

后续若开展受控创建验收，应复用同一既有配置生成两个不同私有角色，经合法会话工具生成提议、用户在Lody保存并只读get核验，再在执行端登记专用临时项目，各按不同Role创建一次项目会话，核对实际目录、配置、Role引用及持久化结果。此处仅记录待验证步骤，不代表已执行或已取得本次配置写入授权；不用普通Lody会话测试替代这些证据。

## 本地文档迭代与合并复核

2026-10-21，公子要求结合产品讨论辩证现有方案，并将分享版与云端开发交接版放入本仓库。本轮原位迭代[多宿主方案c3](collaboration-development.md)，新增[分享版](product-collaboration-reference.md)与[云端交接版](space-cloud-handoff.md)，更新相应索引和说明。保留Lody多宿主能力，复用公子已试通的Dot资料中转，明确Lody专用schema1与资料保存/回读的边界；没有改运行代码、schema、清单、版本或环境，没有新建业务任务、连接或凭证。

初次审查基线为`8d46d5e`；公子保存文档并手动合并上游`3c5fd4a`后，合并提交为`c5b35b4`。本轮只读核对双方差异、未合并索引、冲突标记、文档链接与语义，确认c3和两版文档保留，并保留合并新增的Dot创建独立云任务、不把Cloud API历史401作为插件前置、Role/Project未实测范围等约束。合并没有引入运行代码改动；最终文档收尾补齐交接说明及本记录，不重写公子的既有保存或合并提交。

| 检查 | 本轮本地结果及边界 |
| --- | --- |
| `python3 scripts/check_repository.py` | 通过，`mcp=1 skill=2 plugin=1`；不证明运行可用。 |
| Markdown与链接 | 初次9篇文档的145个本地链接/锚点、围栏与隐私引用检查通过；合并后的相关文档另作同类复核。 |
| `git diff --check`及未合并索引 | 已检查，无空白差异错误或未解决索引冲突；不把自动合并成功当语义审查的替代。 |
| `python3 -m unittest discover -s tests -v` | 本机Darwin arm64、Python 3.11.3；132项运行结束为`failures=41, errors=24, skipped=1`，没有全套通过。 |
| 原提交对照 | 在独立临时源副本运行`8d46d5e`，同样132项、相同汇总，失败及错误的测试名称集合与文档迭代后完全一致。日志可见Linux-only限制和临时目录符号链接校验；本轮不修改这些既有实现。 |

这份本地检查不覆盖Linux当前运行、Dot插件加载或Space业务验收，也不否定上文原Linux轮次的测试结果。运行时代码从初始基线到合并结果没有变化，文档收尾后无需为文字修改重复全部运行时测试；后续代码或运行条件变化再执行受影响检查。私密测试输入与原始日志不提交，真实任务进度仍以唯一队列为准。

## c3资料交接知识与0.2.3候选

2026-10-21，当前云端工作区开始时干净，从`3c5fd4a`以`git pull --ff-only origin main`快进到`a4e272c8913b99c764ddf29c9b085964cfd2f603`，完整读取其commit message及交接指定的方案、现有契约、实现、测试和唯一队列。两份独立审查未发现c3需要改业务代码的实质缺陷；已有typed refs、单协调写入者、恢复先对账和27项Lody交接测试足够复用。具体知识缺口与取舍见[c3实现对照](collaboration-development.md#实现对照与本轮最小增量)。

用户本轮明确授权继续实施、验证与提交。0.2.3增加按需`material-handoff.md`，同步核心导航、协作/交付指针和Dot宿主说明；区分资料引用及输入表示，分别报告处理、保存和目的地回读，资料写入超时复用原对象对账。候选沿用原setup技能及全部工具，不修改schema1、CLI依赖/锁、API、权限或环境配置；不新增服务、路由器或schema2。主方案、C02卡片、交接版和执行入口原位维护，状态仍只在唯一队列。

| 检查 | 本轮结果及证据范围 |
| --- | --- |
| 结构与回归 | Linux x86_64、Python 3.12.14，根目录结构检查通过（`mcp=1 skill=2 plugin=1`），132项测试全部通过；日志在忽略的`dist/lody4dot-0.2.3-regression.log`。没有新增镜像文案的测试。 |
| 文档与差异 | 38份相关Markdown的376处本地链接、97处片段及围栏检查通过；`git diff --check`通过，索引没有未合并条目。外部网页本轮未请求。 |
| 自包含分发 | 31个内容文件加receipt，ZIP共32文件、115,216字节；CRC及全部文件字节/收据摘要匹配，隐藏兼容清单位于ZIP根，薄setup入口保留。 |
| 移位依赖与来源 | 从另一目录的完整包运行离线bootstrap，仅doctor且退出0；插件0.2.3、bundle和同锁runtime来源consistent。子进程未转发LODY/GITEE变量，认证、安装、daemon和任务恢复均未运行。只证明依赖检查及本地文件一致性。 |
| 独立上下文知识演练 | 三个Agent仅获题设及移位包核心技能路径，自主选择参考并形成操作判断；未提供叶子参考路径或预期答案。下面列出实际选择，按理由及拟采取动作审核，未使用固定措辞或关键词判定。 |
| 独立复审 | 完整技能/宿主/版本和方案差异未发现实质缺陷；本轮只读复审不替代业务验收。 |

| 题设 | 观察到的知识使用结果 |
| --- | --- |
| 只有Library引用、下载工具仅支持Sediment，任务需要原xlsx | 从核心入口找到资料及协作参考；复用已授权Dot中转，保留原类型，不猜Sediment ID或原附件hash；计算等待真实原字节，不为纯资料流程创建Lody资源。 |
| Lody处理及字节核对完成，追加先超时后对账确认已保存，目的地回读403 | 找到资料、协作、会话及交付参考；保留处理成功/保存成功/回读被拒，恢复仅限目的地核对；不重跑或重复追加，Space记录不冒充Lody schema1。 |
| 本次明确只验Cloud原生直连，当前未暴露资料工具 | 找到资料、协作及准备参考；报告原生分支未执行，不换Dot报成功、不推断用户无权限，不为此重复发布或创建假Lody记录。 |

演练是同一云实例内的独立模型上下文、按假设事实进行的知识使用，**不是三个独立产品宿主、Dot原生加载或真实资料读写**。它证明给出技能入口后能按需导航，不证明平台自动送达或未提供入口时的技能选择。演练摘要及打包/移位结果保存在忽略的`dist/lody4dot-0.2.3-knowledge-scenarios.json`和`dist/lody4dot-0.2.3-package-summary.json`；不包含真实业务引用。

ZIP SHA-256为`e87dd9aaafb2b8459c6b024cf5bac4cdb1aa875b9b1ec1a8a8de24a91c6674fa`，receipt SHA-256为`4b4fffe836ea02ac139e11ed31f92625f2c40192cf3f06d893b7b42f009d294a`；旧0.2.2与0.2.1 ZIP摘要均未变。生成物不提交，构建时基线为`a4e272c`加本轮授权增量，提交后的来源对应由本轮Git提交与逐文件核对确定，不借用旧0.2.2来源SHA。

本轮没有Lody业务/认证请求、资料传输、保存、回读或OpenAI任务目录查询，也未重验公子已试通的Dot中转。以上Linux结果与上节macOS同基线失败各属实际运行条件，不覆盖或抹去彼此。C05原生安装/setup和独立任务首次加载、C08未验证的真实重建机制、C09/C10以及T09/T12旧截图补证继续保留；产品中转可用不代替插件验收。正式环境仍按唯一队列最近观测记录，本轮未重新读取元数据或发布候选。

## Work Cloud能力、创建方式与场景补充

以下为`dc8cd70`本地文档轮次的历史记录；后续云端0.2.4知识实施见下一节，各轮环境与证据分别保留。

2026-10-21，公子要求补充Work Cloud与Codex Cloud的关系、资料空间读写、插件/MCP区别、创建途径及更多直观例子。本轮读取远端与本地HEAD，二者均为`2d8dd52`；先审查该提交的0.2.3知识、方案和验收差异，再原位补充分享版、云端交接版、c3、环境指引、宿主来源与阅读索引，没有用旧稿覆盖候选实现或后续实施授权。

官方产品事实包括授权资料文件附加/符合条件文件保存、hosted Work的兼容插件/远程MCP、计划或支持事件运行，以及Dot的可见云会话。当前本地会话的首方工具声明另提供Work Cloud代建目标；本轮只读取声明，没有创建调用或返回任务。新增14个场景只用于帮助选择产品与工具，不是实际运行或已验收能力列表。页面编辑、原附件覆盖、Work Cloud创建Codex任务及公共创建API不因上述事实获得额外保证，具体证据范围见[宿主补充](host-contracts.md#work-cloud资料插件与创建支持面)。

本轮只改项目文档；不改0.2.3技能、清单、schema1、运行代码或候选包，不创建任务、计划、角色、连接或资料写入，不推进插件验收。公子已实测的Dot资料中转、由Dot创建Codex Cloud的项目职责和既有C任务状态继续保留。文档检查与本机回归结果按实际检查记录，不借用上一轮Linux132项通过宣称本轮macOS全部通过。

本轮根目录结构检查通过（`mcp=1 skill=2 plugin=1`），文档链接/锚点、围栏、隐私引用、14个场景计数及`git diff --check`通过。实际运行132项单元测试，本机结果仍为`failures=41, errors=24, skipped=1`，失败/错误名称集合与上一轮macOS日志相同；未改变平台或临时路径的实现来求通过。0.2.3上游Linux通过与本机结果分别保留。官方资料和独立事实审阅只证明说明与边界一致，不代替新宿主加载或真实业务验收。

## Work宿主与任务入口知识0.2.4候选

2026-10-21，云端工作区从干净`2d8dd52`快进到`dc8cd70689664c08a1e3fbbfe9091a6793e16a5c`，再次拉取确认最新，执行`git show -s --format=%B dc8cd70`完整读取message，并核对AGENTS、指定文档、现有契约、工具、测试及唯一队列。独立审查确认原引用/资料流程与schema1足够；增量价值和最小选择见[c3 Work实施对照](collaboration-development.md#work知识增量的价值与最小实施)。

0.2.4把Work/Codex宿主识别、四类任务创建/触发入口及运行证据集中在既有协作参考；核心导航、资料/兼容性、setup与随包说明补条件和指针。保留指定任务类型，区分业务MCP与平台创建、Work计划与Lody schedule；不复制14场景或新增记录卡。没有修改Python工具、CLI依赖/锁、schema1、平台接口或环境配置。工具元数据中未见`create_thread`或`chatgptWorkCloud`，只证明当前目录范围；没有调用任务创建API，也不推断账号无权限或其他端无入口。

| 检查 | 实际结果及边界 |
| --- | --- |
| 回归与结构 | Linux x86_64/Python 3.12.14，132项既有测试通过；根目录结构通过（`mcp=1 skill=2 plugin=1`）。日志在忽略的`dist/lody4dot-0.2.4-regression.log`，未增加文案关键词测试。 |
| 文档与差异 | 38份相关Markdown的404处本地链接、123处片段及围栏检查通过；`git diff --check`通过，索引无未合并条目。外部网页本轮未请求。 |
| 分发与移位 | 最终包31内容文件加receipt，ZIP32文件、118,058字节；CRC及逐文件字节/摘要匹配。移位bootstrap仅doctor退出0、插件0.2.4及包/锁来源consistent；子进程未转发LODY/GITEE变量，没有安装、登录、daemon或业务恢复。 |
| 独立复审 | 上游方案及本轮技能、setup、分发差异未发现实质缺陷；只读审查不证明原生加载或业务运行。 |

知识演练均由同实例的新模型上下文仅获得题设和移位包核心技能路径，未给叶子路径或预期答案，按实际理由与拟采取动作判断：

| 场景 | 观察结果与处理 |
| --- | --- |
| Work有附件/制作/保存工具，无shell且无Page编辑/覆盖入口 | 自主找到资料和协作参考，选择直接资料路线，不要求配置GitHub环境、装CLI或额外中转；保留保存与目的地回读、Page/覆盖及账号实测的边界。 |
| 有业务MCP但无平台创建工具，本地另有未调用的创建声明 | 初稿能区分声明、创建和运行，但提到Codex备选；进一步明确指定任务类型不得未经允许替换，并在最终包的新上下文定向复验：保留Work Cloud目标及创建缺口，不将Dot的Codex授权当Work证明。 |
| Work计划超时后已对账保存启用，尚未触发 | 选择沿原计划等待/观察真实运行，不重建或补Lody schedule；计划、运行、产物、保存、回读分别取证，不假定每次触发创建新会话。 |

文件与计划场景及创建初稿基于receipt `78d496d6a56bdf38ea38a21ae04cd637b009fa063cfa0a423d980e983295aacf`；新增指定类型规则后，仅对受影响创建场景定向复验，最终receipt为`062bf7cda682792f94860302576ef2fbc7917a8c0dbe2425ed44d27e1c99f5d7`。这些是三类知识目标与一次针对性复验，不是四个实际产品宿主。没有执行题中资料/计划/创建动作，不证明自动技能发现、Work/Dot加载、真实运行或C09/C10完成。

最终ZIP SHA-256为`45bf2baef78675a42ccb40f5ce02190148b1d64afacad1c2c0e71808bb5651a8`；0.2.3、0.2.2、0.2.1旧ZIP摘要均未变。构建来源为`dc8cd70`加本轮授权知识增量，生成物和演练摘要在忽略的`dist/lody4dot-0.2.4*`，提交后核对Git来源，不把旧候选SHA套给本包。此前macOS失败仍按原轮次保留。

本轮没有新任务/计划/连接、Lody业务认证、资料读写、权限或部署操作，没有重验Dot中转或查询OpenAI任务目录。正式元数据本轮未刷新，不把候选当正式发布；C04跨平台、C05加载、C08未验证恢复、C09/C10及T09/T12原证据缺口继续由唯一队列维护。

## Codex Cloud与Work Cloud创建方式对照

2026-10-21，公子要求补充Codex Cloud创建方式并与Work Cloud对照，明确平台能力与项目分工；企业聊天工具委派优先级低，本轮延后。起草时本地为干净的`dc8cd70`；公子提示更新后再查，本地与远端已同为`aea6798`且干净，已读取该提交说明及全部差异，将本轮文档增量整合到0.2.4最新稿，保留上节实现与验证记录。核对官方手动入口、环境准备/发布、Dot委派及`codex cloud`开发命令说明；官方明确`cloud exec`直接提交任务、默认命令打开交互选择器、`cloud list`列近期聊天。这里只读取文档，没有执行上述CLI或创建任何任务。

分享版原位增加两类Cloud的入口对照及三层判定：平台支持、当前工具/身份/环境证据、项目职责。交接版、c3、环境指引、宿主来源与索引同步引用。仓库规则仅澄清“由Dot创建”是既定项目分工，平台另有手动和CLI入口；没有改变当前云任务不派生下游任务的约束，也没有恢复已撤下的API/401验收。

本轮只修改文档，不改0.2.4知识候选、代码、清单、schema1、云配置或连接；不探测凭证、创建计划、传输资料或新增插件验收。Work Cloud当前首方创建目标仍只是本地工具声明，旧CLI401仍是历史访问结果，均不改写成本账号新建成功。既有实施、验证与提交授权继续按原范围保留。

本轮实际检查：9篇Markdown的195处本地链接、66处片段、围栏、隐私引用与14个场景计数通过；根目录结构检查（`mcp=1 skill=2 plugin=1`）及`git diff --check`通过。Darwin arm64/Python 3.11.3运行132项测试，结果为`failures=41, errors=24, skipped=1`，65个失败/错误名称与上一轮macOS日志完全一致。独立只读复审未发现0.2.4内容被覆盖或职责扩大；这不代替上游Linux回归、原生加载或资料业务验收。

## 平台入口与项目职责知识0.2.5候选

2026-10-21，在干净`cb5cee65c796c918e6e84ecc330c8138f497b332`上再次`git pull --ff-only origin main`确认最新，包含cb5cee6且未回退已有更新；完整读取`git show -s --format=%B cb5cee6`及指定文档、原实现/契约/测试与唯一队列。0.2.4已有流程足够，唯一增量为原协作参考中补Codex平台手动/Dot/CLI入口及三层证据。分发版本独立为0.2.5，0.2.4不改写为待实施；取舍见[c3创建入口](collaboration-development.md#codex-cloud创建入口平台选择与项目职责)。

独立复审指出初稿把本仓库固定分工写成了共享规则，存在跨项目误用；已改为“若接收项目明确约定则遵守”，保留平台支持/当前访问/项目职责区别，并明确Lody session/turn与Codex平台任务分开。修复复核通过，当前项目的CLI/目录禁令、401历史与企业聊天延期继续只由项目规则/文档维护。没有修改Python工具、schema1、CLI依赖/锁、命令索引、setup或支持范围。

| 验证 | 本轮实际结果及范围 |
| --- | --- |
| 回归、结构与分发 | Linux x86_64/Python 3.12.14，132项既有测试和结构检查通过（`mcp=1 skill=2 plugin=1`）。最终31内容文件加receipt、ZIP32文件/118,485字节；CRC、逐文件字节和摘要匹配。 |
| 文档与差异 | 38份相关Markdown的418处本地链接、137处片段和围栏检查通过；`git diff --check`通过、索引无未合并条目。外部网页本轮未请求。 |
| 移位检查 | 最终独立移位包bootstrap仅doctor退出0，插件0.2.5和包/锁来源consistent；未转发LODY/GITEE变量，没有安装、认证、daemon或业务恢复。 |
| 最终本项目场景 | 新上下文从给定核心入口找到协作/资料参考，准确说出平台三入口、本机登录不证明Cloud访问/创建，保留Dot分工，不重查目录/提交或调查401；不把Work目标、Cloud任务和Lody session混同，交付仍分处理/保存/回读。 |
| 最终其他项目场景 | 另一新上下文面对明确允许CLI且访问前提已具备的假设项目，不强制改Dot，也不禁止合法Lody远端派发；保留尚无提交/运行回执的事实，分别关联原生引用。只规划，不执行业务。 |

最终两组均为同实例独立模型上下文，只获题设与移位包核心技能路径，自主选择参考、按实际理由与拟采取动作判断，没有关键词断言。它们不是两个实际产品宿主，也不证明自动发现、原生加载、创建API或账号业务通过。忽略的`dist/lody4dot-0.2.5-knowledge-scenarios.json`保存摘要，回归及包/移位结果分别在同前缀日志和package-summary中。

最终ZIP SHA-256为`fc6152644675b2038b68bf7b0468d33bd0518ce8ad84df096ac5416e6481731f`，receipt为`810bc87402b13dbb96abe2c366d123c10c0a6d23f493cf4439160497da9534c8`。0.2.4 ZIP仍为`45bf2baef78675a42ccb40f5ce02190148b1d64afacad1c2c0e71808bb5651a8`，0.2.3/0.2.2/0.2.1旧包亦未变；全部生成物继续忽略。构建基线为cb5cee6加本轮已授权知识增量，提交后逐文件核对来源。

没有真实Work/Codex平台创建、Lody业务认证、资料读写、Dot基础可行性重验、Cloud CLI/任务目录调用、401调查、权限/连接或部署变化。正式环境及工具目录本轮未刷新；历史macOS失败、C04跨平台、C05加载、C08剩余恢复、C09/C10及T09/T12补证继续保留各自范围。知识候选不代替原生集成或正式发布。

## spec16发布复查与来源修正

2026-10-21，用户确认发布并要求持续推进。实际环境spec/observed16、observations_current=true、running/connected，起初无草稿；正式源仍固定ed9096b/0.2.1。当前checkout为已推送的干净984dad4/0.2.5，完整安装和启动指引与配置内保存值及旧正式源码逐字一致。发布已生效，固定ref未自动升级；本轮按原setup授权修正仓库来源，未新增服务、权限、业务接口或插件版本。

| 检查 | 本轮实际结果与边界 |
| --- | --- |
| 全量仓库发现 | 准备前后遍历/workspace的1004个目录，发现1个实际项目，origin身份、精确HEAD、真实mount、无重叠/子模块、干净状态核对通过。另一个.git标记是空的受保护目录，Git也不识别为仓库，未造unborn记录；runtime内部符号链接目标已遍历，6个缓存目录单独归类，未删除或移动文件。 |
| 完整准备与启动 | 实际运行`.codex/cloud-install.sh`退出0：结构及132项测试通过，bootstrap prepare的install与doctor通过。随后按保存指引运行`--repair-missing`仅doctor通过；认证、daemon、任务恢复均not_run。是当前0.2.5工作副本检查，不冒称正式0.2.5或独立首次加载。 |
| 变量与网络 | 当前元数据network及两变量state为unknown，进程LODY_CLI_TOKEN非空。仅核对存在性，不打印值、不重配绑定；Git读取成功不替代其他服务或账户验证。旧spec14的ready/enforced保留历史，不覆盖本轮结果。 |
| 源修正草稿 | repositories仅保留该项目、原mount及精确提交；首次以软件基线984dad4保存，状态saved/requires_publish，并回读确认install/start、network、secret及runtime要求均未变。收尾顺序为提交本记录→固定到实际HEAD→回读确认，精确目标以交付提交/草稿为准；保存不执行脚本、不发布或更新活动来源。 |

独立只读审查对比ed9096b与984dad4：安装、认证、doctor、bootstrap、handoff、依赖锁及cloud脚本不变；Python增量仅薄setup的构建/来源范围及既有回归，未发现重大服务/契约/权限变化。0.2.5原包、0.2.4历史交付及验收均保留，不重复构建知识版本或模型演练。

本轮未运行Codex Cloud CLI、查询OpenAI任务目录、恢复401调查、重新认证、创建业务任务/计划、写资料或重验Dot中转。当前工具仍未暴露本地文档中的create_thread/chatgptWorkCloud；不以目录缺入口推断Dot无权限。发布不证明VM/磁盘重建，原C08恢复实验不重做；C05/C09/C10、原生setup与旧T09/T12继续保留真实验收门槛。

脱敏结果及日志在忽略的`dist/lody4dot-publish-current-*`、`dist/lody4dot-publish-preflight.json`和`dist/lody4dot-publish-source-correction.json`。正式来源、草稿与后续动作统一见[当前环境与下一步](../../.codex/agent-state/todo.md#当前环境与下一步)，源修正发布后仍需按实际新任务/宿主分别验收。

## spec17来源升级生效与启动复查

2026-10-21，用户再次发布后，实际spec/observed17、observations_current=true、running/connected且failure=null；正式ref为0a044f14622902b6d8d93418338df2251b7a38f8/0.2.5，无草稿和pending要求。network enforced、LODY_CLI_TOKEN及GITEE_ACCESS_TOKEN ready，进程LODY变量存在性为true；未输出值。正式install/start与该提交文件逐字一致。本轮起始checkout同ref且干净，ff-only拉取无更新。

已实际读取`.codex/cloud-start.md`、`skill/lody4dot/SKILL.md`及`references/setup-cloud.md`，入口来自已有会话上下文与仓库检索，不证明平台首次送达。运行保存入口的`bootstrap.py --repair-missing --json`退出0，步骤仅doctor、status=pass；插件清单观测0.2.5，CLI0.107.2，runtime锁b1baf3ab…来源consistent。bundle收据在源码checkout中not_provided，不称包已复验；install未运行、reused未填写，authentication/daemon/task_recovery均not_run。132回归和完整prepare沿用上一轮对相同软件源码的实际结果，本轮只做启动及文档检查。

据此关闭“0.2.5正式来源升级待发布”子门槛；原生ZIP安装/setup仍是未验候选，独立新任务首次读取和Dot实际调用未取得。当前工具目录无create_thread/chatgptWorkCloud，不创建下游Codex任务或查询OpenAI任务目录，不做新的Lody认证/模型回合、资料读写或Dot中转验证。内核boot摘要较spec16不同，只记内核上下文变化，不推断VM身份或磁盘重建。

本轮仅同步唯一队列和本记录，不改变源码/锁或环境配置，不为记录提交再次固定ref、保存草稿或要求发布。静态方案、任务卡和现有验收流程已足够复用；C05/C08剩余项/C09/C10及旧T09/T12的证据门槛保持。脱敏启动结果在忽略的`dist/lody4dot-spec17-startup.json`，来源与状态摘要在`dist/lody4dot-spec17-summary.json`；当前状态统一见[任务队列](../../.codex/agent-state/todo.md#当前环境与下一步)。

## 剩余工作与执行前提复核

2026-10-21，从干净37c6910拉取无更新。两份独立只读复核对照C任务、安装器/21项安装测试和Role/Project已核实源码：已有真实首装/同锁复用，失败保护另有fixture；runtime锁仅f566f6c起的一套b1baf3ab…，当前versions也只有该目录。若验收C10跨runtime升级失败/回退分支，尚缺第二套已复核输入，不由插件知识版本或伪造锁变化替代；任务卡原位明确条件，保留主方案已有安装入口/宿主接入材料回退，不给所有路线追加CLI版本门槛。未执行新安装或升级。

Agent配置、Role与Project的已有核实无需重做；原configuration参考尚未完整携带多Role复用、Project非已证实持久角色分组及当前身份机器提议路由三点，可作为下一步C02最小知识增量。本轮仅定位，未修改随包技能、发新版本或写远端配置；真实提议/用户保存、项目登记和执行仍分别验收。任务卡旧“本轮正式0.2.1”副本已改为唯一状态链接，C05/C08/C09/C10状态未因这次复核关闭。

最新元数据为spec/observed19且current=true、running/connected、failure=null，网络/变量state均unknown；正式来源仍0a044f1/0.2.5，无草稿与pending要求。spec17的ready保留历史，不推断凭证失效或重复配置。未做新的依赖/认证/模型/资料请求，未查OpenAI任务目录或重验Dot中转；正式环境无需为这些记录再次发布。当前状态仍见[唯一队列](../../.codex/agent-state/todo.md#当前环境与下一步)。

## Role与Project知识0.2.6候选

2026-10-21，用户要求按建议推进Role/Project随包知识。干净a9852a2上ff-only拉取无更新；复用前述关系核实，对实际安装的官方0.107.2发布源码做两份独立只读复核，原位补`configuration.md`和`sources.json`，候选版本为0.2.6。多Role可复用machine/config，提议字段中的machineId不选择CLI调用机器；Project是会话上下文，尚未核实持久角色组，不扩大否定其他版本/UI。未新增角色组织服务、绑定契约或重复索引。

| 验证 | 实际结果与边界 |
| --- | --- |
| 仓库回归 | 132项Linux测试、结构及差异检查通过；不把已有macOS失败记录改为通过，也不扩大runtime支持。 |
| 自包含分发 | builder收集31内容文件加receipt，ZIP32文件、120396字节；CRC、每文件摘要、receipt及移位解包内容一致。移位离线bootstrap退出0且仅doctor，插件0.2.6、bundle/runtime consistent；install/authentication/daemon/task_recovery均not_run，未填写reused，子进程不转发LODY/GITEE变量。 |
| 同配置双Role目标 | 新上下文自主读核心、配置/发现/会话与帮助快照，复用同一配置而不复制凭证；将角色提议的实际宿主/会话工具与普通远端派发分开，并保留用户保存、M端项目登记及分层结果核验。未把Project持久角色组当已确认能力。 |
| 提议未保存目标 | 新上下文明确卡片成功不代表角色生效，0.107.2 create初始runConfig为空、update只支持三项文字字段；不编造model/mode写入参数或保证未知UI，先保存并查询，再按真实入口核验配置及执行条件。 |
| 跨机项目目标 | 新上下文识别R绑定M而P属于K的冲突，不能用额外machine参数绕过Role覆盖；保留M时须在M准备并登记实际项目，不能把新项目冒称K上的原P；若更换目标需单独确认支持入口与目标变化。 |

以上三项是同一执行环境中从显式最终包入口开始的知识选择演练，不是平台自动发现、独立新任务或Dot原生调用。包ZIP SHA-256为`1ecb92fea6ac54b559e4bace871eab07298efe325f961440368caf241adbfdab`，receipt为`2ad1f37ef0c9277b9dea343e30ad8eb950c240890285acabd303f762cff9fd37`。与0.2.5相比，仅清单版本、随包README、configuration及sources内容和receipt变化；31个内容文件的其余部分相同。0.2.5原ZIP（fc615264…）与0.2.4/0.2.3/0.2.2/0.2.1原摘要均保持，旧验证记录保留。

Python工具、CLI/runtime锁、核心技能、setup、命令索引、帮助快照和云脚本均无变更。正式来源仍0a044f1/0.2.5，无草稿；运行元数据spec21/current=true、running/connected，网络/变量state均unknown。没有角色提议/保存、项目登记、真实Lody业务或模型回合，没有Dot资料重验、OpenAI目录查询、下游Cloud任务、环境变更或发布请求；不从本次知识实施推导配置写入授权。C05/C08剩余项/C09/C10、C04真实平台与旧T09/T12继续按实际证据验收。

忽略目录保留`dist/lody4dot-0.2.6-{regression.log,package-summary.json,bootstrap.json,knowledge-scenarios.json,doc-checks.json}`及ZIP，公开只记录脱敏范围。当前状态仍由[唯一队列](../../.codex/agent-state/todo.md#当前环境与下一步)维护，不再建立方案或进度副本。

## 离线ZIP命令与0.2.7候选

2026-10-21用户明确先固化离线ZIP、再修正测试夹具。P1在原builder增加可选`--zip PATH`，默认目录构建结果和退出码保留；CLI请求ZIP时才附加archive路径、文件数、字节数、ZIP/收据SHA及验证说明。目标一律新建，预检已存在路径/源码或输出重叠，暂存ZIP通过CRC、收据和逐文件摘要后以不覆盖方式发布。目录可在ZIP后续失败时保留，不承诺两输出共同原子提交；未建立新分发服务或发布动作。

独立上下文先补失败用例；原15构建测试增加11项至26，覆盖默认兼容、完整根目录/隐藏清单、已有/修改ZIP及其他目标保护、父路径冲突、源码/输出重叠、发布竞争、校验/发布失败清理、坏源拒绝和epoch时间戳。CRC有效但内容或收据被改会拒绝；收据为合法JSON列表的异常先复现再修正。复审另复现epoch0抛ValueError，增加回归并用ZIP格式的时间范围规范化解决，不改变文件内容摘要。最终143项Linux全量、结构和差异检查通过，独立复审通过。

真实源码CLI生成31内容加收据、32文件ZIP，初次产物120935字节，SHA-256为`3f657cad61ec55808791c46d02c70580301fc6a5f9ad102f1dab6758d020669b`；重复同路径请求实际退出3，ZIP未变。复审后最终CLI另生成`lody4dot-0.2.7-post-review.zip`，SHA为`86ef6f9a8559871d71250ec4adaf4b281e46f86c548ec922e516419a9bda3c1a`，所有entry内容与初次产物逐字节相同；ZIP头时间戳可随构建变化，不承诺两次整包字节确定性。收据SHA均为`71070cc6c85e6e1024b333f1977a90b8cf6f90e260a78abb89b7a1c134f13b2e`，CRC与逐文件摘要独立核对通过。

移位解包后离线bootstrap退出0、仅doctor，插件0.2.7、bundle/runtime consistent；未转发LODY/GITEE变量，install/authentication/daemon/task_recovery均not_run。同锁CLI0.107.2，未升级或重装。0.2.6至0.2.1六份原ZIP摘要全部不变，源码builder继续不随包，随包Python工具、知识、schema1、依赖锁及云脚本未改；原生安装/加载、真实平台或Lody业务证据未新增。

忽略目录保留`dist/lody4dot-0.2.7-{build-result.json,post-review-result.json,repeat-result.json,package-summary.json,p1-regression.log,bootstrap.json,prior-packages.json}`和两份ZIP；当前正式来源/状态仅见[唯一队列](../../.codex/agent-state/todo.md#当前环境与下一步)。本项完成的是C05离线分发子范围，不关闭C05加载、C04真实平台、C08剩余恢复、C09/C10或旧T09/T12；P2夹具修正随后单独实施。

## 离线测试夹具的宿主依赖修订

2026-10-21，P2基于已推送2bc188d/0.2.7单独实施。生产Linux平台判断与安全路径检查符合现有契约，具体缺口在测试：自有临时根经符号链接别名进入祖先或私密state拒绝，部分Linux后端语义用例未声明模拟平台，在Darwin条件下提前返回unsupported。先保留失败记录，再仅修正install、diagnostics、CLI版本策略和lifecycle四组夹具：规范化自有临时基础根，实例级Linux平台补丁注册清理；故意传入的坏路径和生产guard不改。

定向三组67项先通过；全量整合再复现生命周期组7个提前退出失败，增加同类平台声明后消除。最终在当前Linux机器的独立子进程中验证：

| 条件 | 最终结果 | 证据范围 |
| --- | --- | --- |
| 普通Linux | 143项，无失败/错误/跳过 | 全量回归，含26项构建测试及原真实Linux文件锁用例 |
| Linux＋符号链接TMPDIR | 143项，无失败/错误/跳过 | 别名临时根不再干扰正确输入；故意输入的符号链接仍拒绝 |
| 模拟Darwin | 143项，无失败/错误，跳过1项 | 只修改测试进程的sys.platform；原Linux专用文件锁装饰器按既有规则跳过 |
| 模拟Darwin＋符号链接TMPDIR | 143项，无失败/错误，跳过1项 | 两个已知夹具条件的组合；并非真实Darwin运行 |

独立审查以AST对比四模块75个测试名称、所有原assert调用和skip装饰器，均未变；平台补丁在每个实例结束恢复。原独立Win32/Darwin不支持测试、权限拒绝、私密state及显式符号链接拒绝均保留，未用mock绕过生产检查。结构、引用及差异检查通过；生产脚本、平台支持测试、技能、云脚本、CLI锁和插件版本未改，0.2.7已有ZIP字节不变，因此不另生成候选包。

本轮是Linux上的夹具条件模拟，不证明真实macOS、WSL或Windows受管runtime；此前真实macOS失败按原记录保留。没有认证、daemon、模型/业务调用、资料保存、平台任务创建或原生加载，C04真实安装及C05/C08/C09/C10未由本轮关闭。忽略目录保留`dist/lody4dot-p2-fixture-red.json`、`dist/lody4dot-0.2.7-p2-regression.log`、`dist/lody4dot-0.2.7-fixture-matrix.json`及对应条件日志；首次生命周期失败另存`*-before-lifecycle.*`，不覆盖成成功。当前状态只维护[唯一队列](../../.codex/agent-state/todo.md#当前环境与下一步)。

## 2026-10-25当前任务升级与latest准备策略

本次在Dot已创建的现有任务继续，初始checkout为用户指定的`0a044f14622902b6d8d93418338df2251b7a38f8`。最初仓库结构、132项测试、已有0.107.2受管运行时的prepare与启动检查通过，工作区当时干净；随后用户明确授权当前环境Node/CLI升级、仓库latest准备策略及按新CLI完善技能。下表记录首次升级完成、尚未取得模板保存授权时的观测，不改写此前正式发布或旧0.107.2任务验收；后续命令审查与保存步骤另见下节。

| 检查 | 本轮实际结果与范围 |
| --- | --- |
| 当前任务运行时 | 受管官方Node`24.22.1`、npm`11.19.1`已实际执行；平台`/opt`内建Node未改。cloud-install/cloud-start在该受管路径存在时前置PATH；新CLI launcher与doctor按安装收据的`node_path`选择解释器。 |
| CLI准备 | 真实`bootstrap --prepare`退出0，CLI为`0.108.1`。源码manifest请求`latest`，源码lock保存本轮精确结果；每次准备在暂存目录定向更新lody锁，再做engine-strict、禁用生命周期脚本的ci或同锁复用，验证成功后切换。其它锁约束和reviewed override保留。安装授权不包含认证、daemon或业务任务。 |
| 实际公开帮助 | 在不含真实token的环境和临时state采集20个一级入口、70个公开命令，版本与全部帮助退出0，临时state已清理。随包仅保留一个当前`help-snapshot.json`；索引逐项更新版本、来源与help SHA，不能用旧帮助当新版已测。 |
| 帮助差异 | 命令树未增删；只有session分组、create、chat、recover-inbox四份帮助变化。create/chat新增`--mcp-server-ids`；recover-inbox新增snapshot/orphan及更明确的离线检查、资源释放和paused语义。仅据帮助更新导航，未运行真实MCP选择或Inbox恢复。 |
| 技能与发现 | 核心/setup入口先查实际CLI帮助，再按明确workspace选择machine、project catalog、Agent config/Role；优先官方CLI与原生只读查询，不从仓库名或本机目录推导Lody映射，不新造业务SDK。 |
| 认证与403源码审查 | 0.108.1的API-key、pairing、device副作用与credentials/SQLite前提、Streams短期token刷新及诊断字段仅完成source_verified，来源摘要与固定发布物哈希在`sources.json`。本轮没有新版login、目录查询、旧403重试或Agent派发；无状态探针不替代原CLI调用，旧403原因仍unknown。 |
| 最终回归 | 完整`.codex/cloud-install.sh`退出0：结构`mcp=1 skill=2 plugin=1`、150项测试、latest准备及离线inspect全部通过。启动`--repair-missing`仅doctor退出0；真实自包含构建31内容文件加receipt通过。认证、daemon、目录与业务恢复均not_run。 |
| 发布边界 | 变更只在本任务工作副本与自有工具目录，保存环境模板/固定ref未更新或发布；没有部署、原生插件注册、远端身份创建、Cloud下游任务或代码提交。 |

首次升级采集的帮助快照（任务回执）SHA-256为`f759b8673818607597b8d3870bf7454164dd89e185e611df921742604cf42494`；后续递归帮助修订以随包快照与全量矩阵为准。0.107.2历史源码、完整目录、远端session/turn与产物证据仍按各自版本记录；当前帮助和本地依赖通过不证明新版身份、目录、执行能力或新任务会采用本轮源码。本任务脱敏回执位于`/workspace/mymcp-initialization-20261025-236tp3x1/upgrade/`，依赖、缓存、登录态和运行生成物不入源码包。

## 2026-10-25全量命令审查与模板保存准备

用户随后授权保存更新现有模板，并要求新版CLI全部命令逐项复核、有差异固化到技能；模板更新后允许既有API key的临时私密身份及必要目录缓存，复验后清理。当前任务未提供Codex保存环境配置读写接口，线上复验的阻点是模板保存时序，不是缺身份写入许可或已发生登录失败。

保存源码以原指定ref为基点，合入远程`main`截至`7b25a7e94f9c0cbd27a3244fa49f0c2c5e7780c9`的5项提交；保留0.2.6 Role/Project知识、0.2.7 ZIP与夹具修复，没有用旧基点覆盖main。保存分支为`chore/lody-latest-cloud-20261025`，最终提交/远程核验由交付回执记录；Git分支保存不等于模板ref已修改。

| 检查 | 实际结果与边界 |
| --- | --- |
| 全量CLI发现 | 从当前0.108.1根帮助独立递归取得20类、70业务/分组路径，再核对12个自动help入口，共82项正确帮助退出0；根帮助与版本也通过。内部入口未执行。逐项参数、身份、workspace、效果、方法与结果见[审查矩阵](cli-command-audit.md)。 |
| 形式与副作用差异 | `lody help --help`退出1的失败证据保留；正确help入口通过。帮助会在隔离state创建machine-id，目录已清理；没有写登录凭据或注册远端机器。14条索引前提及对应参考已修正，help/source不冒称线上通过。 |
| 可复现Node准备 | 新增仓库`scripts/prepare_cloud_node.py`，固定官方Node24.22.1 Linux x64归档与已核实SHA256，兼容旧受管回执，精简探测环境并隔离npm配置，失败保留旧入口。16项离线回归通过，含checksum/probe/解压硬链接路径/清理/激活失败；真实空临时前缀下载、校验、安装及Node/npm探测通过并清理，当前受管前缀真实复用通过。仅本任务测试，未创建新环境。 |
| 合并后完整初始化 | 实际`.codex/cloud-install.sh`退出0：受管Node复用、结构`mcp=1 skill=2 plugin=1`、179项测试、CLI latest准备与离线inspect通过；实际Node24.22.1、npm11.19.1、Lody0.108.1。 |
| 夹具保留 | 合并后安装/回滚32项与ManagedNode5项在普通Linux、别名临时路径、模拟Darwin及组合条件各37项全通过；模拟条件不是真实macOS支持。 |
| 启动及分发 | `bootstrap --repair-missing`退出0且仅doctor；真实自包含构建32内容文件加receipt，33文件ZIP的CRC与收据摘要通过，ZIP SHA256为`b522c55d21af896c03103daace2ce70ee3f222c276018ad6bb073736cd18177a`。包内离线bootstrap退出0且仅doctor，来源一致；未安装注册原生插件。 |
| 模板及线上状态 | 目标模板读取/更新未尝试，原因是本端无对应受支持接口，非拒绝或不确定写入。用父级管理接口或同一环境设置保存最终已推送ref及install/start入口后须回读；不修改凭据、网络安全，不另建任务验证。原CLI登录/目录403及业务命令本轮线上实测为0，状态pending_template_update；旧403原因仍unknown。 |

本轮完整记录在任务外部`upgrade/template-save/`回执目录；源码仅提交工具、技能、审查输入和测试，不提交依赖缓存、ZIP或身份。新环境实际采用、模板正式版本、生效实例、认证与目录结果继续分项取证；保存准备完成不提前标记这些项成功。

## 2026-10-25远程main重载与官方CLI读取验收

用户已将保存分支合入main，实际远程main为`a86a63f67f023796023c488b80803acfe78649c2`。工作树干净时fetch远程main，安全切换既有main并ff-only，关键AGENTS、install/start、Node准备、技能与runtime锁文件与该commit逐字节一致，且包含已验证工作分支`59d038e`。main仅做快进，没有自行创建新合并提交、丢弃用户改动或推送main；旧分支的安装已经结束，随后在main串行重新初始化。

| 验证 | 真实结果与范围 |
| --- | --- |
| main安装 | 2026-10-25 09:21:55–09:21:59 UTC，`.codex/cloud-install.sh`原入口exit0；179项回归、结构、受管Node与latest CLI准备/离线检查通过。受管Node24.22.1、npm11.19.1、Lody0.108.1，精确锁摘要9831f975…保留。 |
| main启动 | 09:21:59–09:22:00 UTC，`bootstrap --repair-missing`原入口exit0、status=pass，步骤仅doctor；认证和目录另外验收，没有把此检查当登录或业务成功。 |
| 原生登录 | 09:24–09:25 UTC，仅确认现有材料会走0.108.1原生API-key分支后，用`auth.py --login`调用官方login与工作区验证，exit0、实际HTTP200。既有token仅在内存/已授权私密临时身份中使用，不记录或展示材料，不走pairing/device或创建key流程。 |
| 官方目录 | 同一私密state的workspace list、project list --catalog --kind local --all-pages、agent-config list --all-pages、agent-config get均exit0。两个获准workspace的本地项目目录和Agent目录完整分页，分别执行get核对对应目录ID；只投影必要id/name/type/machine等元数据，不读env/prompt或完整runConfig。具体资源选择保留在任务私密回执。 |
| 证据计数 | 8次受控验证调用覆盖5个CLI命令路径；登录适配器内含原生登录和额外workspace校验。Node标准diagnostics_channel旁观原CLI请求，82条HTTP响应均200、未见401/403，42条request ID及82条cf-ray仅作脱敏关联；不记录path/query、授权头、请求/响应body或原stdout/stderr，也没有修改请求/dispatcher。旁观器的3条合成事件检查无网络请求且私密getter/材料不落日志。 |
| 范围与清理 | 自有0700临时目录中的credentials、machine-id和目录SQLite缓存已finally删除；未执行创建远端key、机器配对/登记、Agent启动、会话或配置写入命令。目录查询仍伴随短期Streams授权/同步/presence，不能泛化成服务器零底层写。 |

用户要求忽略旧探针；它不纳入当前验收、待办或阻塞，不继续推断历史因果。本轮以2026-10-25 Lody0.108.1官方CLI已实测通过为准，不能推广为后续版本或全产品保证，也不增加全产品测试。角色/调度/变更命令继续保留帮助与源码证据，没有执行Agent任务。

本轮必要skill/矩阵收尾后，结构检查、180项全仓测试与差异检查全部通过；实际自包含构建32内容文件加收据、33文件ZIP，CRC/收据校验通过，ZIP SHA256为`544262386b9e75204beb2e564cab76ba1456d20b26b5528057fa95407c2d62a1`。新增回归只保护线上证据分层和授权模式，不增加全产品在线测试，也没有重跑已成功的账户/目录请求。

本轮是同一任务从远程main重新获取源码并运行安装/启动，不是保存模板ref更新、容器重建或独立新任务。模板配置和网络安全/凭据绑定未改。必要技能与矩阵修订在既有工作分支保存，main不由本任务推送；具体新提交见交付回执。main来源、安装、启动和当前官方CLI验证回执在任务外部`remote-reload-20261025/`目录，身份和原响应不入Git。

## 2026-10-26文件中转与授权等待规则

本轮仅固化[文件中转操作参考](../../skill/lody4dot/references/filekiwi-transfer.md)与[慢任务/确认门处理](../../skill/lody4dot/references/sessions.md#慢任务与授权确认)，不新增下载API、服务、自动授权或生产运行逻辑。源码起点为已合并的main `d4afa13d5756dd13816a6e83d0306c23620aae40`；一次性私密任务标识和分享链接不入仓库。

| 项目 | 当次证据与限制 |
| --- | --- |
| 公开契约 | 已读2026-10-26官方v2、v1与OpenAPI；未发现公开下载API。API注册文件上传的独立最终状态与空目录网页上传分开；容量和有效期不固定为跨版本承诺。工具2.0.1/SDK1.0.9的先返回链接及完成通知源码观察来自本轮发送端审阅，不证明当前插件已安装该工具。 |
| 测试发送与手动接收 | 发送端提供了4429字节无敏感测试ZIP的独立上传完整状态；用户手动下载并回传，经父级逐字节/摘要验证通过。此处引用该端验收，当前Codex接收端没有重新上传或声称亲自下载；手动路径不证明自动路径通过。 |
| Dot浏览器 | 父级报告点击后download事件等待超时、常见目录未找到ZIP；不足以证明服务端文件失败，也没有自动落盘通过证据。 |
| 当前保存云环境浏览器 | 本端Playwright/Chromium确实存在，但启用沙箱启动失败，helper所有者不符合要求；尚未打开测试分享页。没有禁沙箱、修改权限、网络或安装软件，文件大小/SHA/CRC未验证。 |
| Lody有界接收测试 | 在Lody0.108.1官方CLI中核明确目标后仅创建一次测试会话，保留session/user/assistant引用并通过observe/history读取。观察曾为persisted/synced/waiting，用户在目标端处理确认；原测试回合的可见答复为BLOCKED，Agent自报缺浏览器自动化工具、未下载/创建测试文件。没有回传ZIP字节或独立远端文件回读，不能判自动接收通过。 |
| 后续安装要求 | 用户在同一会话另提工具安装，属于后续回合，和原下载回合分开跟进。安装、授权、工具注册、最小只读调用及下载恢复分别取证；未确认的阶段不记为通过。本页不复制实时安装状态，仍以对应原会话实际结果为准。 |
| 权限接口边界 | 0.108.1公开show/status/observe只给等待/状态信息，visible history不返回tool_call；CLI及内置MCP无一次性permission response入口。当前接口读不到具体待批项时立即反馈缺口并指向原会话受信任UI，不猜工具参数、拼内部RPC、发yes或改mode替代确认；用户说已授权后重查原任务。 |

长期执行规则与此快照分开维护。真实项目资料未因此获准上传第三方，项目导入、角色创建和生产也不由测试通过推导。本轮结构检查、180项全仓测试及真实自包含构建通过；包有33个内容文件及1份收据，新参考与源码字节一致，随包引用不能越出包根。静态检查和分发构建不等于自动下载成功，后续实时安装结果仍另行核验。

### 03:55 UTC后续：目标端自动接收与完整回传

用户随后在目标端要求准备浏览器能力；同一会话的安装回合给出PASS收据，并在可见最终正文回传完整测试ZIP的base64。控制端从官方CLI history取得该正文后严格解码，独立确认4429字节、SHA-256与原清单完全一致、2个ZIP成员CRC通过；未执行或解压内容。此前“原测试缺工具而BLOCKED”的记录保留，不能将后来准备成功改写成最初环境已可用。

- **接收过程的证据分层：** Agent自报以独立临时venv中的Playwright 1.64.1控制系统Edge（msedge channel、headless），在目标项目独立测试目录保存ZIP并做只读校验；浏览器过程和远端路径没有由控制端直接观察/读文件系统。控制端已独立核验的是回传的完整字节，不是只有Agent声称的摘要。
- **返回路径：** Agent报告绝对路径附件参数校验失败后，以工作区相对路径回传同一个已校验ZIP，没有重新下载；官方CLI可见文本中的完整base64才提供了控制端本次可读字节。该路径差异限定此工具/平台实例，不推导所有附件接口只接受相对路径，不猜附件下载API。
- **浏览器与电脑插件分开：** Playwright为用户要求安装的临时venv本地包，不是已注册的浏览器MCP，未下载新的浏览器二进制；临时脚本已清理、venv保留及无遗留浏览器进程属于Agent收据。电脑控制社区包仅登记，目录独立查询证实stdio、configured=true、enabledByDefault=false；Agent报告未选入当前回合、未实际安装运行。公开registry当前版本不等于本机安装版本，登记命令的首次运行仍须用户复核，不因文件测试通过而启用桌面控制。
- **明确收口：** 一次安全跟进仅核已有调用/文件和工具状态，不授予新安装或下载；03:55:15 UTC观察到该回合completed、persisted/synced、session idle且activeTurns为空。跟进收据确认仅读既有ZIP、没有重下载，仍有电脑控制条目的受信UI选择/拒绝留给用户；文件测试自身无需新增授权。本端临时身份/缓存已清理，没有启用电脑控制、HTTP监听、放宽安全设置或开始真实资料导入。

## 2026-10-26双端审计修正与技能走查

公子转交以`9f98ef3da722240fbcb8465e49259dad6401ed4f`冻结的云端独立审计正文，并授权整合后推进。六项结论中1/2/5成立，3/4/6按审计收窄：现有按需导航、授权复用和单写者保留；T09/T12仅是历史材料缺口，不能否定已验证路线，也不能由CLI成功关闭原生安装验收。云端报告的180项通过属于其独立环境回执，本节另记本地修正结果。

边界记录（BOUNDARY_NOTE）：目录同步未完成沿既有`ToolError(3, catalog_syncing)`返回blocked；builder在提交后的清理告警及ZIP失败回执中保留已应用状态。schema1、工具职责、目录所有权与依赖方向保持，正常成功字段兼容，不新增服务、认证、重试或回滚机制。

| 修改 | 已核结果 |
| --- | --- |
| 目录同步 | 空/非空`syncing`不返回有效数量；doctor保留已通过账户、目录blocked且不进入verified_scope。正常完成页允许无sync字段，不要求虚构fresh枚举。新增2项行为测试，RED后44项诊断测试通过。 |
| 构建与清理 | 新目录提交后旧备份检查/部分删除失败返回成功及固定脱敏warning；不回滚可能已部分删除的备份。后续ZIP失败仍退出3，但保留output、收据、output_applied和已有warning，标记failure_stage=archive，文本同样可见。新增5项测试；组合失败经独立审查发现后补RED/GREEN，31项构建测试通过并复核关闭。 |
| 运行知识 | 宿主入口统一引用latest准备规则；0.108.1 API-key及目录有界实测与device/pairing等静态分支分开。独立宿主复验改为条件步骤，Dot直接CLI与创建Codex Cloud分列，具体执行器按回执归属。 |
| 快速路径与交接 | 已知会话优先沿原引用观察/授权继续，仅补缺项或漂移；提供commands[]单项读取；编码交接补base_commit、owned_paths、实际checkout、integration_owner及集成验收。Cloud已有隔离直接复用。 |

本地标准库回归共187项，186通过，1项Linux真实锁测试在macOS跳过；命令为`TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`。使用真实临时路径避免本机`/var`符号链接影响Node夹具；没有将此条件测试宣称为macOS受管安装支持。结构检查`mcp=1 skill=2 plugin=1`及`git diff --check`通过。原生云环境准备、登录、业务与部署均未重跑。

独立临时路径构建目录与ZIP成功，34个内容文件加1份收据，CRC及逐文件SHA校验通过。ZIP SHA-256为`8b13786dfa57724c311d6c3eed90b3e5328ac2a323275854880a589929f1382f`，收据SHA-256为`0ac54312a001f12bc20ac70361c4ccfc1ff015d2b8f4610f5b8e3b3d345902fb`。当前清单仍0.2.7，以上仅标识本地工作副本验证产物，没有替换旧ZIP、提交、推送或发布环境。

### 六场景单次离线计划走查

按[固定场景与判据](skill-evaluation.md)交给一个新上下文评测者，只提供场景输入与技能入口，未提供判据。该评测者按需读取核心、sessions、discovery、collaboration、material-handoff、troubleshooting，并从index/help中提取7个相关命令。使用会话默认子代理配置，未另行指定或测量模型参数；这是一次批量计划走查，不是六次独立实验。

| 场景 | 观察到的计划与判定 |
| --- | --- |
| E01 已知回合观察 | 直接observe原S并匹配T；不重查版本/身份/目录，不虚构observe --turn-id。符合判据。 |
| E02 已授权继续 | 核本执行器prompt-file可读后沿原S发一次chat并保存新回合；无新会话或重复确认。符合判据。 |
| E03 目标歧义 | 只查W内必要machine/config目录，核分页和同步；仍无法唯一选择则返回候选差异，不选首项。符合判据。 |
| E04 超时未知 | 原引用observe/history/show/status对账，无法唯一确认保留UNKNOWN，不自动重发。符合判据。 |
| E05 编码协作 | 复用独立Cloud checkout并交接基准、写入范围、提交、执行位置、集成owner与检查；无额外worktree要求。符合判据。 |
| E06 指定Cloud路线 | 使用Dot实际创建入口，交接原资料和两端引用，核处理/回传；不改走Lody或补造Lody资源。符合判据。 |

实际仅执行本地只读文件/JSON读取，未调用Lody或创建Cloud任务；上述是计划选择证据，不是业务执行通过。单命令投影另经Python相等性检查：`session observe`的index/audit/help单项分别780/2466/1031字符，原文件分别57199/223185/69956字符。字符不是token，测试框架耗时不是skill延迟；未取得受控前后业务轨迹，不报告提效比例。

关联`agent-skills`（aeac41d4）及`pm-skills`（07b34f64）只读评估的可借鉴点为角色/方法/入口分离、按需装载和行为评测；本轮未复制上游正文、安装其插件或创建角色库。用户确认的工作区共享级/项目级分类已在现有角色入口明确，V2.2快照保持。

## 2026-10-26技能性能与两层角色库Goal

公子明确授权辩证优化、开发并启动Goal。沿现有工具和V2.2先做独立对抗/优化线，收敛为[短入口、精确读取与显式项目适配](workspace-roles/library-design.md)。过程中公子提交本地工作为`b90c256`并pull PR #4，两个文档冲突已合并为`77bbe45`：保留新并行规范、用户工作区会话配置规则，以及本地latest/快速路径/条件复验。工作区专属规则不写成通用角色默认。

### 本地实现与验证

- 0.3.0候选增加纯标准库只读`lookup.py`，提供command、roles、role/render、check；从源码或解包位置定位资料，不依赖cwd。未知/重复项、坏schema、路径逃逸/符号链接、缺依赖和超长prompt均失败，不输出半成品，不联网/登录/调用Lody。
- 当前库1.0.0共11个定义：工作区级G8+六共享职责、项目级owner+三模板；显式选择fanren-work才组装项目合同。10个方法仅记录固定来源、MIT许可和optional/inspiration关系，均未随包。原V2.2 SHA保持`afb8caf1782371feb88417fe28c0d402769de268664c73bd2c2c035d3965685e`。
- 角色语义独立审查发现运行工程候选修复漏了独立QA步骤，已恢复“测试真实接口与正反例→独立QA→owner授权合入”；其他所查全文/听证、冻结、锁、UNKNOWN及媒体恢复要求保留。未增加所有任务的新宿主复验。
- builder只对白名单新增lookup.py，在切换产物前校验全库。独立代码审查发现输出父路径别名被误判库损坏；已用符号链接父目录与`..`两例确认RED，再规范化自有staging，34项构建测试通过。原输出叶链接拒绝与库内资源约束保留。
- 新增20项lookup行为测试、3项构建集成/路径回归；最终全仓210项中209通过、1项Linux真实锁测试在macOS跳过。使用`TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1`；结构、skill frontmatter、引用与diff检查通过。代码与角色独立复核的问题均已关闭。
- 实际ZIP含50个内容文件加收据，解压到独立临时目录，从无关cwd运行check得到11角色、1项目、10方法、18组合，最长3667字符；单角色render通过。ZIP SHA为`b8e4d329e813deb210a1e179b43ea4b434069901b9319cbd9e6b6957f8ef9ffc`，收据SHA为`6e0971c16224b43dce6459a26f006090be90951ae5f99d4c65fcfd7d387d8402`，收尾逐项确认包内内容与当前源码一致。

### 性能测量与取舍

基线是本Goal开始前、已含上一轮审计修正的工作副本，不是未修正的最旧版本。`tests/lody4dot/fixtures/knowledge-baseline.json`保留入口正文与SHA，`measure_lookup.py`可复测；Python3.11.3，每项3次独立本地进程，未请求模型或业务接口。

| 读取对象 | 基线 | 当前 | 可支持的结论 |
| --- | --- | --- | --- |
| SKILL入口UTF-8字节 | 9092 | 5159（含PR #4新增导航） | 入口正文减少43.3%，不等于模型token/耗时同比下降 |
| observe index输出 | 整文件64995；既有内联839 | lookup含来源1427 | 单项准确且可复用，但比已有内联多来源开销 |
| observe help输出 | 整文件70050；既有内联1032 | lookup含来源1554 | 不必读全树；不是更快的Python解析器 |
| observe audit输出 | 整文件243899；既有内联2727 | lookup含来源3332 | 保留单项及版本/范围，原entry与内联完全相等 |
| 通用QA的prompt | V2.2单项6658 | 4143；总JSON5751 | 泛化职责与运行映射分离；新旧语义不是字节等价 |
| QA加凡人适配prompt | V2.2共享单项6658 | 7419；总JSON9256 | 显式带项目硬合同，不能宣称所有角色都更短 |
| 凡人声音生产prompt | V2.2单项10309 | 9611；总JSON11286 | 只取所需职责；总JSON另含身份、来源与组件摘要 |

既有内联命令查询本轮进程中位约19–28ms，lookup约30–50ms；新增来源与校验有成本，故保留内联路径，不要求已有命令迁移。role render去掉重复资源数组、完整可选方法来源等元数据，quality总输出7117→5751字节，项目quality10696→9256字节；prompt和组件摘要逐项相等，完整方法信息仍可通过非render查询取得。没有增加缓存、模型路由器或运行服务。

### 解包后的独立前向走查

一个新上下文仅获得临时解包目录和F01–F05输入，按[固定判据](skill-evaluation.md#030角色库前向场景)复核：F01直接计划observe原T；F02实际查询通用QA，仅common+quality；F03实际查询带fanren适配的QA，拒绝以ASR标听感PASS；F04通过摘要发现runtime再render，要求独立QA后owner合入；F05直接润色，无额外查询。属于一次批量离线走查，使用会话默认子代理配置；未测多模型路由成功率或真实角色生产质量。

本Goal只完成本地源码、分发与行为验证。没有更新远端Role、用户模型/配置或云环境，没有重新认证/派发Lody业务；原生插件装载、模型token/延迟、业务效率和新的远端发布仍未由本轮证明。未以另一执行器回执冒称Dot自有云电脑新实测。

## 2026-10-26角色目录来源校验修复（0.3.1）

公子转交云端Dot对`cd80258e4be0693909a797a2daf6192dbcd2a7db`的复核，本地起始HEAD与origin/main均为该提交。合法角色目录被旧`_bundle_member`拒绝、doctor在汇总后才附加来源，两个问题在当前源码复现。上轮210项测试及CRC/逐文件摘要验证未覆盖完整bundle的provenance与总体状态；其通过不证明当时doctor来源检查通过。云端50成员核对来自Dot转交回执，本轮不冒充重新在Dot自有云电脑执行。

修复以[BOUNDARY_NOTE](collaboration-development.md#51-角色与检查范围)明确schema1局部语义：构建器与校验器共用随包`package_layout.py`，只支持现有角色目录层级，保留非法路径、敏感文件、符号链接、越界及大小预算限制；构建工具自身仍不随包。已有证据invalid/mismatch计入`checks.provenance=fail`并在首个Node子进程前停止，正常前提下整体fail/退出5/invalid_provenance。已有前置错误保留主类别和非零退出，无收据则not_provided/warn，不计入来源已验证范围。固定reason区分格式、非法成员、SHA、缺文件和不安全路径，原始解析器消息不外泄。`bootstrap --repair-missing`遇到同时缺runtime与来源失败时只诊断、不安装。

- 新增11项完整性行为测试和1项bootstrap联动回归，既有诊断测试删除“来源失配仍通过”的旧断言。角色路径、实际build、包内独立解释器导入、坏JSON/UTF-8、非法成员、文件及父目录链接、缺失文件、SHA变化和零子进程/账号调用均验证。UTF-8异常的原生reason曾导致非固定分类，先确认RED后修复。源码无收据保持可运行，但有明确warning。
- 最终全仓222项中221通过、1项Linux真实锁测试在macOS跳过；使用`TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1`。仓库结构和diff检查通过。独立只读复核确认首个子进程前拦截、bootstrap零安装及最小收据兼容，未发现遗留必修项。
- 实际0.3.1 ZIP含51个内容文件加收据，共52成员、203719字节；CRC、逐文件SHA及完整bundle provenance均通过，14个角色目录成员全部纳入。ZIP SHA为`b180536015ea0581d09e5f96559e15064a523f2d953fe59cbe9f45bfa289463d`，收据SHA为`8237b0f86dce3130334c3edf06132b111b940d9178986527562b423dfc6cfe9a`。正常doctor汇总以真实构建文件配合隔离受管运行时夹具和受控Node/CLI探针验证；不计为真实Lody运行。

本轮为本地源码与离线分发修复，未登录、联网安装、创建任务、更新云环境或发布Role。来源保证仍仅为本地收据明列文件一致性，不是签名、未列成员检查或业务验收。重新装载0.3.1的云端doctor回执仍由目标执行器提供，不重跑已证实的协作业务链路。

## 2026-10-26独立组织协作skill Goal

公子在[组织方案v0.2](project-coordination.md)之后明确“启动goal，推进实现”，并要求覆盖后续岗位／角色新增更新。起点`4a82088`，组织协议、当前关系、任务上下文与专业能力分离；采用独立Markdown skill，不新增组织数据库、自动路由器、任务JSON schema或派发服务。原生Goal的执行队列为O01–O05。

### 实现和分发

- `organization-collaboration`协议1.0.0，共7个Markdown文件：入口及总负责人、项目负责人、执行／审查、上下文／汇报、规划／进度、维护参考。入口唯一导航保留稳定岗位ID；定义、任职／通道与专业角色分别版本化。普通在途任务保留明确版本，撤权、安全修正和公子新指令即时约束相关动作。
- 专业库1.1.0保留11个旧ID、18个组合，`g8_coordinator`是组织导航兼容入口，`fanren_owner`保留领域约束。render只组装原库资源，不自动读取新skill；已保存Role不会自动更新。V2.2角色源SHA保持`afb8caf1782371feb88417fe28c0d402769de268664c73bd2c2c035d3965685e`。
- lody4dot组合包0.4.0显式收集独立组织skill，构建／provenance共用白名单，只允许入口及平铺Markdown参考。新增岗位不用改构建代码；深层路径、脚本、敏感成员和符号链接继续拒绝。`--organization-skill-only`输出独立skill及专用收据，新目录和ZIP保护、归档失败后的`output_applied`行为有回归。
- `AGENTS.md`、源码云启动说明及宿主指引把组织入口放在Lody条件之前；纯组织协作不要求Node、CLI、登录或setup。源码指引更新不代表保存环境ref发布或目标新任务已读。

最终全仓237项中236通过、1项Linux真实锁测试在macOS跳过；本轮新增15项。使用`TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1`；仓库结构`mcp=1 skill=3 plugin=1`、quick_validate、引用与diff检查通过。独立代码审查及定向反例未发现待修问题；真实组合包完整provenance为consistent，组织成员篡改会在Node/CLI/账户调用前使doctor失败。

| 产物 | 本地验证 | SHA-256 |
| --- | --- | --- |
| 独立组织skill 1.0.0 ZIP | 7内容文件＋收据，共8成员，15737字节，CRC／逐文件摘要通过 | `66e3f4e842f3340be4dde125df2397c042efed122c05c03689296e5f6c471245` |
| 独立skill收据 | 与源码7文件及本机安装逐一匹配 | `27275a3ff1d39ebcefdb2a2741dc3aab0961bd7fd3a8dfe1f5a39ee7a88c9b53` |
| lody4dot 0.4.0 ZIP | 58内容文件＋收据，共59成员，220808字节，CRC／摘要／bundle provenance通过 | `47b0d2fd4209ecc2c2902c52aee61486bae512510198e6694d4362e9c5483bd9` |
| 组合包收据 | 对应当前源码及生成marketplace；明列文件一致性 | `c6baf2ab1cd1f5c21780279662e4a91cf702c6e37913ca6ccfe2771832836d05` |

产物及原始走查位于本机`/private/tmp/org-collab-release-wmw4ijzt/`。独立ZIP是技能文件包，不是ChatGPT原生插件ZIP；组合包也仍需目标宿主接收与加载验收。摘要不提供签名或远端真实性证明。

### 三个新上下文前向走查

三个独立上下文只获得迁出仓库的独立skill、虚构输入和只读／计划范围，不提供方案、判据或彼此结论。沿用会话默认模型配置，未单独测量采样参数；每个上下文是一批相关场景，不能按问题数量计作独立实验。

| 上下文 | 实际skill读取 | 观察结果 |
| --- | --- | --- |
| 总负责人／Dot | 入口＋总负责人、上下文、规划，共4文件 | 项目T12归O负责和验收，Dot代建并中转E回报；Dot自身比较不虚构项目。旧创建UNKNOWN先恢复请求并对账，不再建同目标任务 |
| 项目负责人O | 入口＋负责人、规划、上下文、维护，共5文件 | 错字修正一步自领但仍审阅规划分配；接口明确后A/B条件并行，唯一重型测试资源串行。岗位与视觉角色分别维护，T8普通更新保留在途版本但撤权立即约束，远端停止仍UNKNOWN |
| 执行者E | 入口＋执行／审查、上下文、维护，共4文件 | 按已确认r3向O2负责、经Dot中转；旧发送UNKNOWN不重发；作者换名QA不构成独立。项目Q缺岗位定义和唯一owner只阻断依赖动作，不转用P的授权 |

主线程核对原始回答与[固定场景](../organization-collaboration/README.md#验证与维护)，判据均满足。仅读取资料并生成计划，无真实消息、Cloud/Lody任务、登录或项目资产写入；不据此宣布持续自动协作已实现。入口3802字节只表示读取规模，未测真实token、模型延迟或业务提效比例。

### 分端接入状态

| 目标 | 本轮证据 | 尚未取得 |
| --- | --- | --- |
| 当前本机Codex | 已将完整独立skill安装到`~/.codex/skills/organization-collaboration`，目标此前不存在；7文件及收据逐项匹配，未覆盖其他技能 | 新一轮／新任务原生发现与实际调用；本轮显式文件阅读不冒称自动触发 |
| 当前仓库／未来Codex Cloud | 新源码入口、云启动指引、完整独立与组合包可读，离线前向走查通过 | 远端保存环境ref更新／发布、目标独立任务读取回执 |
| 云端Dot及其他项目执行端 | 已准备包、上下文模板及安装/读取验收方法；当前工具未提供直连安装入口 | 唯一目标与获准入口／会话引用，以及本版本实际安装、读取和回报闭环回执 |

本轮询问远端接入引用后继续独立实现，没有凭本机PATH可定位Lody就登录、枚举工作区、发送消息或推断Dot云电脑可达。本机已装、源码已集成与远端待接入分开交付；不改远端已保存Role、实际任职关系、云环境或自动化。后续只按补齐的实际入口推进相应端，不重跑已有业务链路。

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
