# mymcp-4-codexcloud

面向 Codex 云端的 MCP、skills 和插件集合。

## 三个部分

| 目录 | 职责 | 每个条目的入口 |
| --- | --- | --- |
| [mcp/](mcp/README.md) | MCP 服务的源码、依赖及运行说明 | `mcp/<id>/README.md` |
| [skill/](skill/README.md) | 技能指令及其 references、scripts、资源 | `skill/<id>/SKILL.md` |
| [plugin/](plugin/README.md) | 将一个或多个能力组合成可安装插件的分发定义 | `plugin/<id>/README.md` |

MCP 和 skill 是能力，plugin 是组合与分发单元。一个插件可以同时包含多个 MCP 和 skills；能力源码只维护一份。三目录使用单数名称，保持统一。

仓库组织方式不等于 Codex 的自动发现或安装配置。把文件放入上述目录，并不能证明 Codex 已加载它们。设计依据、取舍和迁移方法见 [架构说明](docs/architecture.md)。

项目专属文档统一按`docs/<id>/`归档。lody4dot的完整阅读入口见[文档索引](docs/lody4dot/README.md)；新增资料遵循[文档归档规范](docs/architecture.md#文档归档规范)。

云任务、运行实例、本地环境、Dot、会话引用和协作空间权限的区别，见[环境与权限指引](docs/lody4dot/environment-model.md)：先读一分钟速查和执行链路，再按问题查表。跨环境协作的对象关系、记录模板与评审清单见[架构设计参考](docs/lody4dot/environment-design.md)。

多处加载安装、经Lody协作及环境初始化/恢复，见[多宿主协作开发方案c3](docs/lody4dot/collaboration-development.md)与[C01–C10任务卡](docs/lody4dot/collaboration-tasks.md)。c3结合产品对话与实测：保留Lody主干，复用公子已试通的Dot资料中转，明确schema1与资料回存的边界；本轮仅迭代文档。官方已确认Dot是ChatGPT中的常驻Agent产品，拥有自己的云电脑，也可创建独立的Codex云任务或使用获授权的本地电脑；三种执行位置分别建模。插件连接可在已授予范围内跨产品共享，本地访问、CLI身份和模型凭证另行核对。来源见[宿主契约](docs/lody4dot/host-contracts.md)，实现与真实验收见[任务队列](.codex/agent-state/todo.md)。

本次完整讨论沉淀为两种阅读入口：[产品协作参考（分享版）](docs/lody4dot/product-collaboration-reference.md)讲解概念、云环境、资料空间、MCP与图标；[云端任务交接版](docs/lody4dot/space-cloud-handoff.md)对照仓库实现，给出方案取舍、最小优化与验收边界。主方案仍为上面的c3，运行状态仍只在任务队列维护。

## 当前状态

已导入 [Gitee MCP 网关](mcp/gitee/README.md)：保留原源码、部署文档、验收资料和历史交付包，并记录来源与文件校验清单。文件导入与静态检查已验证；原服务的依赖安装、OAuth/Gitee 连接和实际运行尚未验证。另有 [lody4dot 技能](skill/lody4dot/SKILL.md) 和 [分发工具](plugin/lody4dot/README.md)。

仓库结构检查无需安装第三方依赖，也没有公共服务需要启动。运行单个 MCP 时需按其 README 准备依赖和配置。后续导入按照 [导入步骤](docs/architecture.md#导入已有插件) 迁移，并在此补充条目入口。

lody4dot 已实现 20 类、70 个公开命令的知识导航，以及锁定安装、只读诊断、显式认证和自包含打包。当前 Linux 云机已验证安装、真实授权和完整目录；通过已有远端 Codex Agent 完成了创建、执行、继续验证和持久化观察，并校验 Agent 二次读回的产物字节。控制端无需本机 daemon。已收到用户的安装、认证、目录和手动读取截图，仍需补齐入口来源与版本等回执；本机 Codex 执行的只读状态限制单独保留。见 [产品方案](docs/lody4dot/plan.md)、[开发契约](docs/lody4dot/development.md)、[验证记录](docs/lody4dot/validation.md) 和 [任务队列](.codex/agent-state/todo.md)。

正式ref、工作副本、运行观测、readiness及下一步统一维护在[当前环境与下一步](.codex/agent-state/todo.md#当前环境与下一步)，本页不复制发布快照。保存配置、正式发布、实例应用和目标API授权分别取证；发布不会自动把固定commit切到GitHub最新代码。

本项目独立Codex云任务由Dot创建，用户已确认Dot具备权限；云任务加载lody4dot后，通过Lody与其他节点协作并回传结果。云任务不派生Codex云任务，OpenAI任务目录API及其历史401不属于插件前置或项目阻塞；具体交接见[新任务验收](docs/lody4dot/fresh-task-acceptance.md)。

当前源码候选0.2.2增加官方用户运行setup的[薄入口技能](skill/lody4dot-setup/SKILL.md)，复用核心知识与bootstrap；它不是安装自动执行或存储重置hook。132项测试、自包含打包、移位检查与包来源对账通过，平台原生调用尚未验收。正式0.2.1已有的CLI版本策略继续保留：版本不同、探测或显式latest查询失败只warn，默认离线，不自动升级。受管runtime仅支持Linux，真实命令、身份、权限和完整性错误分别处理。见[验证记录](docs/lody4dot/validation.md)、[支持矩阵](docs/lody4dot/support-matrix.md)及[Dot接入运行单](docs/lody4dot/dot-acceptance.md)。

spec12恢复演练已验证不同内核上下文下依赖、身份及原会话/产物对账，该阶段0新模型回合；后续实验各自计数，见[验证记录](docs/lody4dot/validation.md)。它不证明具体VM身份、磁盘重建机制、Dot hook或独立新任务首次加载。Review上游Viewer、旧截图来源及Dot实际接入仍按各自缺口跟进。

此前通过Lody原生附件将0.2.0包交给Darwin/arm64已有Agent，解包后的receipt/技能摘要匹配，273字节产物二次读回及随机challenge验证通过；未独立核验远端原始ZIP字节。随后远端通过实际暴露的内置MCP查询同一会话，原引用、产物字节与challenge再次匹配，补齐有限双端控制/复验范围。缺少PATH中的Node/npm/CLI不等于缺少宿主内置工具；macOS受管安装、真实云主机重建及Dot接入仍未验证。

## 开发与验证

1. 先阅读目标目录的 README，新增 `mcp/<id>/`、`skill/<id>/` 或 `plugin/<id>/`。
2. 每个 MCP 自行声明并锁定依赖，记录运行、停止和功能验证命令。每个 skill 保留完整随附资源。
3. 插件说明必须列出所组合能力的路径，以及目标平台、安装方法、所需配置和验证方法。
4. 在仓库根目录执行下方检查，以及受影响条目的真实验证命令，再检查 `git diff --check` 和 `git status --short`。

仓库检查只需 Python 3.10+，不需要安装第三方包：

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
```

[结构检查](scripts/check_repository.py) 验证必需文档、条目命名和入口，拒绝分类目录、条目和入口上的符号链接，并显示各类条目数量；[测试](tests/test_check_repository.py) 验证这些检查能拒绝无效目录。结构检查脚本也可从任意工作目录通过完整路径调用。

数量为零时允许骨架检查通过；这不代表存在可运行插件。各条目仍需声明并执行自己的功能测试，结构检查不能替代插件打包、服务请求或技能加载验证。

## 配置与凭证

运行所需的变量名称、用途和网络目的地写入条目说明；凭证通过云环境设置安全注入。仓库只保存不含真实值的配置示例。构建产物和安装缓存不作为能力源码提交。
