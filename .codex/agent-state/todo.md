# lody4dot 任务队列

权威：[上位方案 r2](../../docs/lody4dot-plan.md)；契约：[开发方案 d1](../../docs/lody4dot-development.md)。本文件是唯一进度和执行证据入口。

当前授权：2026-10-20 用户明确选择在本对话持续执行 r2/d1。宿主无 Goal 工具，未创建后台 Goal。`planned` 表示尚未满足全部执行前提；可独立进行的准备继续，真实验收不以模拟结果替代。

| ID | 结果 | 依赖 | 状态 | 执行证据 |
| --- | --- | --- | --- | --- |
| [T01](../../docs/lody4dot-development.md#t01冻结加载方式和平台契约) | 加载与平台契约 | 无 | done | [平台契约](../../docs/lody4dot-platform-contract.md)：同版本官方清单与技能路径已核实；采用云环境接入并交付原生产物，T09另验加载 |
| [T02](../../docs/lody4dot-development.md#t02验证固定版本运行时并生成锁定输入) | 固定版本与锁定输入 | T01 | done | [运行时记录](../../docs/lody4dot-validation.md)：锁定0.107.2和Tinypool2.1.2；冻结安装、native及原始worker通过，audit 0 |
| [T03](../../docs/lody4dot-development.md#t03实现技能来源与命令覆盖) | 技能、来源、命令覆盖 | T02 | done | [知识检查](../../docs/lody4dot-validation.md)：20类/70路径及帮助哈希匹配，未冒称业务已实测 |
| [T04](../../docs/lody4dot-development.md#t04实现可重复且失败可恢复的安装器) | 重复安装与失败恢复 | T02 | done | [安装器验证](../../docs/lody4dot-validation.md)：14项行为测试及真实安装/同锁复用通过 |
| [T05](../../docs/lody4dot-development.md#t05实现唯一只读-doctor) | 只读诊断 | T02 | done | [诊断与认证验证](../../docs/lody4dot-validation.md)：默认离线inspect真实通过，账户/任务保持未验证 |
| [T06](../../docs/lody4dot-development.md#t06实现显式认证适配) | 显式认证适配 | T05 | done | [诊断与认证验证](../../docs/lody4dot-validation.md)：显式模式、私密state、假凭证不回显通过；真实授权留T09 |
| [T07](../../docs/lody4dot-development.md#t07实现自包含构建与云环境接入) | 自包含包与云接入 | T03、T04、T05、T06 | done | [分发与云配置](../../docs/lody4dot-validation.md)：22文件移位安装通过；草稿保存已确认，未发布/加载 |
| [T08](../../docs/lody4dot-development.md#t08完成无账户集成与分发回归) | 无账户集成验证 | T07 | done | [无账户验收](../../docs/lody4dot-validation.md)：39项条目测试加8项原仓库测试通过，移位CLI安装及inspect通过 |
| [T09](../../docs/lody4dot-development.md#t09完成干净云任务加载安装和真实发现) | 真实云端加载、安装、发现 | T08；宿主、身份、网络、工作区 | blocked | [外部条件](../../docs/lody4dot-validation.md)：新任务加载/私密state边界未验；当前缺token，3服务域名仍被拦，草稿待发布 |
| [T10](../../docs/lody4dot-development.md#t10验证-agent-任务能力与受控执行闭环) | agent 场景与真实任务 | T09；测试目标、执行凭证 | blocked | 依赖T09；实际工作区、测试目标/Role和底层Agent凭证未验证；离线agent演练单列，不替代闭环 |
| [T11](../../docs/lody4dot-development.md#t11补齐高级能力的场景与平台边界) | 高级场景与支持矩阵 | T10 | blocked | 高级参考与命令导航已覆盖；真实高级场景依赖T10及隔离目标 |
| [T12](../../docs/lody4dot-development.md#t12交付复现与支持范围确认) | 复现与交付 | T10、T11 | blocked | 离线实现已审查；T09–T11的真实验收未完成，不标整体交付完成 |

当前首项：T09。独立实现、无账户验证与草稿已完成；待已保存配置发布及当前任务实际收到凭证，再继续真实发现。最新任务检查仍未获得 `LODY_CLI_TOKEN`，只影响真实认证，不要求用户在聊天中重新提供值。

后续状态为 `in_progress / blocked / done`。blocked 需注明具体前提及仍可推进的独立项；done 必须链接实际结果与未运行项。任务完成不等于整体发布完成，能力缺口不得被结构检查或 fixture 通过掩盖。

## 本轮规划复核

2026-10-20，针对 r2/d1 完成独立审视：正常完成、安装失败、关键前提不成立三条路径未发现实质矛盾。5 份新改文档的 38 处本地链接、12 个任务与无环依赖检查通过，8 项现有仓库测试通过。这些是规划与仓库检查证据，不是上述实现任务的完成证据。
