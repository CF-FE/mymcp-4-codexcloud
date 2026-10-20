# lody4dot 任务队列

权威：[上位方案 r2](../../docs/lody4dot-plan.md)；契约：[开发方案 d1](../../docs/lody4dot-development.md)。本文件是唯一进度和执行证据入口。

当前授权：2026-10-20 用户明确选择在本对话持续执行 r2/d1。宿主无 Goal 工具，未创建后台 Goal。`planned` 表示尚未满足全部执行前提；可独立进行的准备继续，真实验收不以模拟结果替代。

| ID | 结果 | 依赖 | 状态 | 执行证据 |
| --- | --- | --- | --- | --- |
| [T01](../../docs/lody4dot-development.md#t01冻结加载方式和平台契约) | 加载与平台契约 | 无 | done | [平台契约](../../docs/lody4dot-platform-contract.md)：同版本官方清单与技能路径已核实；采用云环境接入并交付原生产物，T09另验加载 |
| [T02](../../docs/lody4dot-development.md#t02验证固定版本运行时并生成锁定输入) | 固定版本与锁定输入 | T01 | done | [运行时记录](../../docs/lody4dot-validation.md)：锁定0.107.2和Tinypool2.1.2；冻结安装、native及原始worker通过，audit 0 |
| [T03](../../docs/lody4dot-development.md#t03实现技能来源与命令覆盖) | 技能、来源、命令覆盖 | T02 | done | [知识检查](../../docs/lody4dot-validation.md)：20类/70路径及帮助哈希匹配，未冒称业务已实测 |
| [T04](../../docs/lody4dot-development.md#t04实现可重复且失败可恢复的安装器) | 重复安装与失败恢复 | T02 | done | [安装器验证](../../docs/lody4dot-validation.md)：14项行为测试及真实安装/同锁复用通过 |
| [T05](../../docs/lody4dot-development.md#t05实现唯一只读-doctor) | 只读诊断 | T02 | done | [诊断与认证验证](../../docs/lody4dot-validation.md)：离线inspect与真实账户验证通过；0.1.1另检查指定workspace目录，任务仍未验证 |
| [T06](../../docs/lody4dot-development.md#t06实现显式认证适配) | 显式认证适配 | T05 | done | [诊断与认证验证](../../docs/lody4dot-validation.md)：显式模式、私密state、假凭证不回显通过；真实login/verify-only已通过，不误报机器注册 |
| [T07](../../docs/lody4dot-development.md#t07实现自包含构建与云环境接入) | 自包含包与云接入 | T03、T04、T05、T06 | done | [分发与云配置](../../docs/lody4dot-validation.md)：22文件移位安装通过；草稿保存已确认，用户随后确认已发布；实际加载未验 |
| [T08](../../docs/lody4dot-development.md#t08完成无账户集成与分发回归) | 无账户集成验证 | T07 | done | [无账户验收](../../docs/lody4dot-validation.md)：45项条目测试加8项原仓库测试通过，移位CLI安装及inspect通过 |
| [T09](../../docs/lody4dot-development.md#t09完成干净云任务加载安装和真实发现) | 真实云端加载、安装、发现 | T08；宿主、身份、网络、工作区 | blocked | [外部条件](../../docs/lody4dot-validation.md)：当前实例已收到token，真实登录/工作区查询通过；选定个人工作区目录被Loro Streams域名CONNECT403阻断，待新增规则生效 |
| [T10](../../docs/lody4dot-development.md#t10验证-agent-任务能力与受控执行闭环) | agent 场景与真实任务 | T09；测试目标、执行凭证 | blocked | [运行前提补充](../../docs/lody4dot-runtime-findings.md)：个人目标已选；builtin运行时与host全工作区副作用已核实，独立ACP初始化RPC1001，未创建会话 |
| [T11](../../docs/lody4dot-development.md#t11补齐高级能力的场景与平台边界) | 高级场景与支持矩阵 | T10 | blocked | 高级参考与命令导航已覆盖；真实高级场景依赖T10及隔离目标 |
| [T12](../../docs/lody4dot-development.md#t12交付复现与支持范围确认) | 复现与交付 | T10、T11 | blocked | 离线实现已审查；T09–T11的真实验收未完成，不标整体交付完成 |

当前首项：T09。独立实现、无账户验证与草稿已完成；用户已确认保存发布，当前实例实际注入及授权已验证；已有token和四域名无需重配。目录还依赖新发现的Loro Streams分片域名，待该项规则生效继续；用户已选个人workspace，保留选择。

后续状态为 `in_progress / blocked / done`。blocked 需注明具体前提及仍可推进的独立项；done 必须链接实际结果与未运行项。任务完成不等于整体发布完成，能力缺口不得被结构检查或 fixture 通过掩盖。

## 本轮规划复核

2026-10-20，针对 r2/d1 完成独立审视：正常完成、安装失败、关键前提不成立三条路径未发现实质矛盾。5 份新改文档的 38 处本地链接、12 个任务与无环依赖检查通过，8 项现有仓库测试通过。这些是规划与仓库检查证据，不是上述实现任务的完成证据。

## 用户确认发布后的复查

2026-10-20，用户明确回复“已保存并发布”。只读复查：当前进程无任何 LODY 变量；当前运行状态 observations_current=true，spec_revision/observed_spec_revision 均为3，custom allowed_hosts 仅 lody.ai，runtime_variables 为空；三个服务域名实际 HTTPS 仍为 CONNECT 403。保存配置可读为 revision 5、四域名和 pending direct-environment-variable LODY_CLI_TOKEN。用户发布已作为会话事实接收；这些观测仅说明当前实例尚未获得对应配置，不能推断 token 无效或用户未配置。

可用工具不包含当前实例的发布、重启或切换入口。不重复写配置以免制造新草稿；先等待宿主重连/传播后按实际状态复查，若本会话持续保留旧运行实例，可在已发布环境的新云任务继续 T09。新任务先读本队列并复查变量存在性和实际网络，再做显式授权及只读发现；不要重新要求填写 token。

## 本次发布生效与真实授权

2026-10-20，用户再次发布后，同一任务观测 spec_revision/observed_spec_revision=4，四域名已生效，进程token present。auth login和verify-only均退出0，真实工作区查询ok且count=2。用户已明确选择个人workspace用于本机临时目录小任务，不再次询问。

目录查询发现新的、可复现的阻断：api/control-b/control-c/presence.streams-api-x.loro.dev 均 CONNECT403；机器及Role列表原始exit1，不当成空列表。网络规则按源码分片模式补充 *.streams-api-x.loro.dev；保留已有规则与变量。doctor 0.1.1可用 --workspace 保留账户已认证/目录失败的分项证据。后续先复验目录，再做观察与任务；没有启动daemon或创建真实会话。

## Loro 规则发布后的继续验证

用户已确认发布，正式配置中可读 *.streams-api-x.loro.dev（无新草稿），但当前运行实例仍为 revision4、仅四域名，实际 CONNECT403；完成独立准备后复查仍未变化。没有重复保存配置或重新登录。

[运行前提补充](../../docs/lody4dot-runtime-findings.md) 记录了适配器版本、managed0.160.1的受管入口、无模型初始化失败与官方状态目录边界，以及原生host会覆盖API-key可见的全部工作区。没有越过用户的个人工作区范围启动host。临时项目及验收断言已备妥，实际目录、观察和任务闭环仍待条件满足。
