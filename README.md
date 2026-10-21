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

云任务、运行实例、本地环境、Dot、会话引用和协作空间权限的区别，见[环境与权限指引](docs/lody4dot-environment-model.md)。指引包含关系图、生命周期、权限表及后续架构设计检查项。

## 当前状态

已导入 [Gitee MCP 网关](mcp/gitee/README.md)：保留原源码、部署文档、验收资料和历史交付包，并记录来源与文件校验清单。文件导入与静态检查已验证；原服务的依赖安装、OAuth/Gitee 连接和实际运行尚未验证。另有 [lody4dot 技能](skill/lody4dot/SKILL.md) 和 [分发工具](plugin/lody4dot/README.md)。

仓库结构检查无需安装第三方依赖，也没有公共服务需要启动。运行单个 MCP 时需按其 README 准备依赖和配置。后续导入按照 [导入步骤](docs/architecture.md#导入已有插件) 迁移，并在此补充条目入口。

lody4dot 已实现 20 类、70 个公开命令的知识导航，以及锁定安装、只读诊断、显式认证和自包含打包。当前 Linux 云机已验证安装、真实授权和完整目录；通过已有远端 Codex Agent 完成了创建、执行、继续验证和持久化观察，并校验 Agent 二次读回的产物字节。控制端无需本机 daemon，56 项回归测试通过。已收到用户的安装、认证、目录和手动读取截图，仍需补齐入口来源与版本等回执；本机 Codex 执行的只读状态限制单独保留。见 [产品方案](docs/lody4dot-plan.md)、[开发契约](docs/lody4dot-development.md)、[验证记录](docs/lody4dot-validation.md) 和 [任务队列](.codex/agent-state/todo.md)。

当前源码与分发为0.1.4：已验证自有运行回合取消及无后代会话的改名、归档/恢复，补齐级联范围、资源释放与取消竞态指引。正式云环境仍为已核实的0.1.3，新包不等于环境已升级。具体实测、条件支持和未运行项见[支持矩阵](docs/lody4dot-support-matrix.md)。Review仍受上游匹配Viewer缺失限制；[接入验收](docs/lody4dot-fresh-task-acceptance.md)先在已有截图对应任务补充记录，不重复建任务或登录。

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
