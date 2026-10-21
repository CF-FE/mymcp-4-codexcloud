# 仓库开发约定

- 先读 [README.md](README.md) 及目标目录的 README；涉及组合或迁移时读 [架构说明](docs/architecture.md)。
- 能力源码放 `mcp/<id>/`、`skill/<id>/`；`plugin/<id>/` 负责组合和分发。保留已有插件布局的迁移例外见架构说明。
- 文档按项目归档到 `docs/<id>/`，维护 `README.md` 索引，配图及图源放在该项目的 `diagrams/`；禁止将项目专属文档以 `<id>-*.md` 散放在 `docs/` 根目录。仓库通用文档与技能随附资料的归属见[文档归档规范](docs/architecture.md#文档归档规范)，移动时同步修正引用。
- 不猜测 Codex 清单字段、技能加载入口或云端能力；以实际文件、平台文档与运行证据核实。
- 环境、会话引用和协作空间权限的术语与边界见[环境指引](docs/lody4dot/environment-model.md)，其中架构建议不当作平台已实现能力。
- 不提交凭证、依赖缓存和安装/分发生成物；随图源维护的文档SVG可提交，须保留来源与再生成说明。迁移时保留隐藏清单、资源引用及文件权限，先核对再移动。
- 在仓库根目录执行 `python3 scripts/check_repository.py` 和 `python3 -m unittest discover -s tests -v`；仅需 Python 3.10+ 标准库。
- 当前没有公共服务需要安装或启动。新增条目时补充其命令、工作目录和有实际行为断言的验证方法。
- 文档检查与目录存在不能证明插件安装、技能加载或 MCP 调用成功，报告时区分这些状态。
- 云任务已有隔离环境，使用现有 checkout；除非用户明确要求，不创建 Git worktree。
