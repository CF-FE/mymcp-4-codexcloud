# Skills

每个技能使用独立目录 `skill/<id>/`，以 `SKILL.md` 为入口，并完整保留它引用的 `references/`、`scripts/`、assets 等文件。`<id>` 使用小写字母、数字和连字符。

技能目录应说明适用场景、执行步骤和必要前提。如果技能调用 MCP 工具，需在 `SKILL.md` 或其引用文档中列明所需服务、能力及不可用时的处理方式，不复制 MCP 的实现源码。

迁移已有技能时，保留其元数据和资源相对路径；检查每个文件引用是否仍然有效。不能只迁移 `SKILL.md` 而遗漏其随附文件。

`skill/` 是源码维护目录。目标 Codex 环境的发现、安装与分发入口，在读取真实插件及确认平台格式后配置。目录存在不代表技能已加载。

当前条目：[lody4dot](lody4dot/SKILL.md)，按需导航 Lody 公开命令、任务流程和云端安装。

[organization-collaboration](organization-collaboration/SKILL.md) 独立维护组织岗位、任务责任、汇报与进度、接管和岗位／角色更新。所有参与端可使用同一协议，真实任职关系由当前任务提供；不依赖Lody、Node或专业角色库。[分发与加载](../docs/organization-collaboration/README.md)区分文件安装、实际读取和业务验收。

[lody4dot-setup](lody4dot-setup/SKILL.md) 是插件用户运行 setup 时的薄引导入口，复用核心技能和已有初始化工具，按本端实际能力检查或准备依赖；不作为自动安装或存储重置 hook。

返回 [仓库首页](../README.md)。
