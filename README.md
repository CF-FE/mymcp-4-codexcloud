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

## 当前状态

目前已建立目录、贡献约定和结构校验工具，尚未导入任何实际 MCP、skill 或 plugin。「协作空间 → 插件集合」中的原插件尚未迁入，因此其完整性、依赖、打包格式和云端运行情况均未验证。

仓库骨架无需安装依赖，也没有公共服务需要启动。获得首个真实插件后，按照 [导入步骤](docs/architecture.md#导入已有插件) 迁移，并在此补充条目入口。

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
