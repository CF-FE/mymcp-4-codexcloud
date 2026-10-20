# lody4dot 实现与验证记录

日期：2026-10-20。任务状态权威为 [队列](../.codex/agent-state/todo.md)，接口依据为 [开发契约](lody4dot-development.md)。以下分别记录离线行为和后续真实账户结果；账户成功不代替目录、宿主加载或任务验收。

## 环境与固定输入（T02）

- Linux，Node `v24.19.0`，npm `11.9.0`，Python `3.12.14`，Codex CLI `0.163.0`。
- Lody 固定为 `0.107.2`，使用提交的 [manifest](../plugin/lody4dot/runtime/package.json)、[锁文件](../plugin/lody4dot/runtime/package-lock.json) 和 [构建策略](../plugin/lody4dot/runtime/build-policy.json)。
- 锁文件 SHA-256：`b1baf3ab20593c88f40e4ab7077b737296480d6ca3a0428b7d55499eee9bcced`，40 个锁项。
- 全部安装脚本禁用，锁中无 `hasInstallScript` 项。必要 native 模块无需另行运行构建脚本。
- 原始 CLI 无凭证采集的 70 页公开帮助均退出 0；排除内部命令。发布包的 Lody 版本未更改。

原始依赖 Tinypool `1.1.1` 在当时 audit 中涉及两项 critical 公告：[GHSA-5gmw-xhrv-c9v3](https://github.com/advisories/GHSA-5gmw-xhrv-c9v3)、[GHSA-85c8-ppgw-ccpr](https://github.com/advisories/GHSA-85c8-ppgw-ccpr)。公告描述的利用还需要特定输入/原型污染条件，不能据此宣称 Lody 已被利用。

采用限定在 Lody 下的 `tinypool: 2.1.2` override。没有执行强制 audit 修复或降级 Lody。该覆盖跨越原依赖 major 范围，因此做了原始 worker 对照，而非只相信安装成功：

- Tinypool 1.1.1 与 2.1.2 分别加载未修改的 Lody diff 和 file-index-scan worker。
- 并发 diff、Unicode、文件匹配/不匹配、递归/浅扫描、完整索引、异常传播与池恢复的规范化结果一致。
- 最终冻结安装再执行 [可复现 worker 检查](../tests/lody4dot/verify_workers.mjs)，7 组检查通过；使用空环境加 PATH，无账户凭证。
- 对最终冻结安装运行 `npm audit --omit=dev --json`，退出 0，各等级及 total 均为 0。这仅代表当时 registry 已知公告结果。

实测限于 Node 24.19/Linux；Node 22、Bun 和其他系统未实跑。官方 engines 范围与实际验证范围分别说明。

## 知识检查（T03）

[技能入口](../skill/lody4dot/SKILL.md) 配有 8 个主题参考、命令索引、来源记录和帮助快照。20 类、70 个公开路径逐条匹配；帮助 SHA-256、版本、命令树和索引字段一致。

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

- 安装脚本：[cloud-install.sh](../.codex/cloud-install.sh)，只装依赖及运行离线检查。
- 启动指引：[cloud-start.md](../.codex/cloud-start.md)，按需读取技能，在任务内使用私密状态。
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

后续继续验证的发布传播、Codex 运行时与 host 范围见 [运行前提补充](lody4dot-runtime-findings.md)。该次独立准备没有真实模型任务结果。

## 分片规则生效与真实目录（0.1.2）

同一运行实例的 spec_revision/observed_spec_revision 更新为 **5**，observations_current=true，已包含 `*.streams-api-x.loro.dev`。正式配置无新草稿或待注入变量；现有全局 token 已可用。api/control-b/presence 的无凭证 HTTPS 请求不再遭 CONNECT 拒绝，curl 均退出 0，根路径 404。

新建 `0700` 私密任务状态后，真实登录和工作区查询再次通过。选定个人工作区的原生 machine list 全页查询退出 0、2 台机器、hasMore=false；agent-role list 确实为空，agent-config list 为 2 项，工作区目录中 `kind=local` 的项目为 1 项。没有把解析失败或无权限当作空目录。

原生 0.107.2 的目录 JSON 前后夹有同工作区的 `Remote Streams transport attached/detached` 日志。已定位发布源码中的两条精确消息及 compact JSON 输出位置；仅兼容唯一完整 JSON 及这两种同工作区消息，保留字段和分页校验。未知日志、跨工作区消息、多 JSON 和截断响应继续失败；stderr 仅提示忽略条数。没有采用任意截取最后一行或忽略全部非 JSON 的处理。独立差异审查通过。

修复后的真实 `doctor --profile control --connect --workspace ... --json` 退出 0：account authenticated、workspace_count=2、workspace_catalog pass、machine_count=2、all_pages=true、has_more=false；local_runtime 和 task_execution 仍为 not_run。21 项诊断测试及全部 **56 项**仓库测试通过。

真实 `session list --limit 5 --json` 退出 0，返回 1 个未归档会话；这是有界查询，不代表全量历史。`session observe --all --json` 退出 0，返回 2 个 synced/source=metadata 快照。另一个 agent 按 cloud-start → SKILL → discovery/sessions/compatibility 及准确帮助独立完成只读场景：完整机器目录 2 台 online、Role 确实为空；定点观察已有会话退出 0、ok=true、freshness=synced、source=persisted，存在 latestTurn。仅记录字段及状态，没有输出业务文本或标识，没有向已有会话发消息或取消任务。

这证明当前技能导航和真实发现/观察可用；all 的 metadata 不能冒充 persisted，已有会话的 persisted 读取也不能证明本次创建、模型执行或产物成功。agent 被提供了入口，不能证明新云任务自动加载。本机 daemon status 退出 1 且明确未运行；未启动 host 或建立测试会话。

当前剩余验收是新云任务的技能读取回执、私密状态跨任务边界，以及真实受控执行。已按官方大小/哈希下载并运行 managed Codex 0.160.1 的版本检查，但 bundled ACP 初始化仍失败；具体结果与 host 作用于全部可见工作区的限制见 [运行前提](lody4dot-runtime-findings.md)。不再要求重新配置 token 或重复发布已生效的分片规则。

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

这是上游匹配产物缺失，不能通过重复发布环境或只增加fallback域名修复。只能等待官方匹配文件，或由公开LODY_REVIEW_VIEWER指定与CLI固定哈希完全相同的文件后重试；不使用其他模板冒称成功。报告和脱敏摘要留在忽略的cache；临时state已清理。全部高级能力与条件见[支持矩阵](lody4dot-support-matrix.md)。

当前工具无法创建/附着独立云任务，因此发布确认和本次当前实例复验仍不等同新任务自动接入。剩余外部步骤见[新任务验收](lody4dot-fresh-task-acceptance.md)；既定路线是start_skill云接入，原生插件注册单独保留未验，不作为该路线的额外必选门槛。

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
