# lody4dot 任务队列

权威：[上位方案 r2](../../docs/lody4dot-plan.md)；契约：[开发方案 d1](../../docs/lody4dot-development.md)。本文件是唯一进度和执行证据入口。

当前授权：规划文档。所有实现任务均未启动，未安装或运行 Lody，未创建会话或调度。`planned` 表示已定义，不表示已获本轮实现授权或已具备全部前提。

| ID | 结果 | 依赖 | 状态 | 执行证据 |
| --- | --- | --- | --- | --- |
| [T01](../../docs/lody4dot-development.md#t01冻结加载方式和平台契约) | 加载与平台契约 | 无 | planned | 无 |
| [T02](../../docs/lody4dot-development.md#t02验证固定版本运行时并生成锁定输入) | 固定版本与锁定输入 | T01 | planned | 无 |
| [T03](../../docs/lody4dot-development.md#t03实现技能来源与命令覆盖) | 技能、来源、命令覆盖 | T02 | planned | 无 |
| [T04](../../docs/lody4dot-development.md#t04实现可重复且失败可恢复的安装器) | 重复安装与失败恢复 | T02 | planned | 无 |
| [T05](../../docs/lody4dot-development.md#t05实现唯一只读-doctor) | 只读诊断 | T02 | planned | 无 |
| [T06](../../docs/lody4dot-development.md#t06实现显式认证适配) | 显式认证适配 | T05 | planned | 无 |
| [T07](../../docs/lody4dot-development.md#t07实现自包含构建与云环境接入) | 自包含包与云接入 | T03、T04、T05、T06 | planned | 无 |
| [T08](../../docs/lody4dot-development.md#t08完成无账户集成与分发回归) | 无账户集成验证 | T07 | planned | 无 |
| [T09](../../docs/lody4dot-development.md#t09完成干净云任务加载安装和真实发现) | 真实云端加载、安装、发现 | T08；宿主、身份、网络、工作区 | planned | 无 |
| [T10](../../docs/lody4dot-development.md#t10验证-agent-任务能力与受控执行闭环) | agent 场景与真实任务 | T09；测试目标、执行凭证 | planned | 无 |
| [T11](../../docs/lody4dot-development.md#t11补齐高级能力的场景与平台边界) | 高级场景与支持矩阵 | T10 | planned | 无 |
| [T12](../../docs/lody4dot-development.md#t12交付复现与支持范围确认) | 复现与交付 | T10、T11 | planned | 无 |

恢复实施后的第一项：T01。当前不开始安装或业务实现。前置资料整理可以独立进行，但不能提前标记依赖真实帮助/运行时证据的任务完成。

后续状态为 `in_progress / blocked / done`。blocked 需注明具体前提及仍可推进的独立项；done 必须链接实际结果与未运行项。任务完成不等于整体发布完成，能力缺口不得被结构检查或 fixture 通过掩盖。

## 本轮规划复核

2026-10-20，针对 r2/d1 完成独立审视：正常完成、安装失败、关键前提不成立三条路径未发现实质矛盾。5 份新改文档的 38 处本地链接、12 个任务与无环依赖检查通过，8 项现有仓库测试通过。这些是规划与仓库检查证据，不是上述实现任务的完成证据。
