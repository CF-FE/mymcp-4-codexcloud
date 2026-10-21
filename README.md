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

云任务、运行实例、本地环境、Dot、会话引用和协作空间权限的区别，见[环境与权限指引](docs/lody4dot-environment-model.md)：先读一分钟速查和执行链路，再按问题查表。跨环境协作的对象关系、记录模板与评审清单见[架构设计参考](docs/lody4dot-environment-design.md)。

多处加载安装、经Lody协作及环境初始化/恢复，见[多宿主协作开发方案c2](docs/lody4dot-collaboration-development.md)与[C01–C10任务卡](docs/lody4dot-collaboration-tasks.md)。官方已确认Dot是ChatGPT中的常驻Agent产品，拥有自己的云电脑，也可创建独立的Codex云任务或使用获授权的本地电脑；三种执行位置分别建模。插件连接可在已授予范围内跨产品共享，本地访问、CLI身份和模型凭证另行核对。来源见[宿主契约](docs/lody4dot-host-contracts.md)，实现与真实验收见[任务队列](.codex/agent-state/todo.md)。

## 当前状态

已导入 [Gitee MCP 网关](mcp/gitee/README.md)：保留原源码、部署文档、验收资料和历史交付包，并记录来源与文件校验清单。文件导入与静态检查已验证；原服务的依赖安装、OAuth/Gitee 连接和实际运行尚未验证。另有 [lody4dot 技能](skill/lody4dot/SKILL.md) 和 [分发工具](plugin/lody4dot/README.md)。

仓库结构检查无需安装第三方依赖，也没有公共服务需要启动。运行单个 MCP 时需按其 README 准备依赖和配置。后续导入按照 [导入步骤](docs/architecture.md#导入已有插件) 迁移，并在此补充条目入口。

lody4dot 已实现 20 类、70 个公开命令的知识导航，以及锁定安装、只读诊断、显式认证和自包含打包。当前 Linux 云机已验证安装、真实授权和完整目录；通过已有远端 Codex Agent 完成了创建、执行、继续验证和持久化观察，并校验 Agent 二次读回的产物字节。控制端无需本机 daemon。已收到用户的安装、认证、目录和手动读取截图，仍需补齐入口来源与版本等回执；本机 Codex 执行的只读状态限制单独保留。见 [产品方案](docs/lody4dot-plan.md)、[开发契约](docs/lody4dot-development.md)、[验证记录](docs/lody4dot-validation.md) 和 [任务队列](.codex/agent-state/todo.md)。

正式云环境已发布0.2.0，来源为`d27f1a0`；本轮运行配置revision9，启动依赖检查通过，新私密身份沿原Lody引用完成只读对账，没有重发模型任务。这证明发布后控制端恢复子范围，尚不证明独立新任务加载或整机重建。平台网络/变量readiness仍为unknown，实际连接与认证结果单独记录。

当前源码候选为0.2.1：补齐官方Dot知识、接入说明与候选分发材料，并将CLI版本检查改为非阻塞提示。0.107.2保留为知识及默认可复现安装基线；实际版本不同或查询失败只warn。显式`doctor.py --check-updates`可查询npm latest，默认inspect/启动检查离线，不自动升级。真实命令、身份、权限和安装完整性问题按实际结果处理，受管runtime仅支持Linux。构建与回归结果见[验证记录](docs/lody4dot-validation.md)，实际支持范围见[支持矩阵](docs/lody4dot-support-matrix.md)。现有云准备入口可复用；Dot安装及独立控制端按[接入运行单](docs/lody4dot-dot-acceptance.md)验收。Review上游Viewer缺失、旧截图入口补证及Dot自有存储hooks分别保留缺口。

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
