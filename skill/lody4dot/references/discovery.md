# 发现工作区、机器、项目和能力

## 选择目标

先明确用户允许访问的 workspace，再查询该工作区的机器、项目和 Agent 配置。不要静默选首个匹配；名称冲突或 workspace 不明确时使用显式 ID。缓存中的可用性不是资源预留，也不是派发许可。

产品协作空间、某执行器的 `/workspace` 目录与Lody workspace是三种对象，按已有上下文和对应工具定位；目录搜索不能替代空间对象访问。会话链接与上传文件也各有来源系统和读取范围，不能把ChatGPT会话引用当Lody sessionId。跨端定位规则见[多宿主协作](collaboration.md)。

```bash
lody workspace list --json
lody machine list --workspace WORKSPACE_ID --all-pages --json
lody project list --workspace WORKSPACE_ID --kind local --all-pages --json
lody agent-config list --workspace WORKSPACE_ID --machine MACHINE_ID --json
lody agent-role list --workspace WORKSPACE_ID --all-pages --json
lody mcp list --workspace WORKSPACE_ID --json
```

这些是已公布的命令形式，示例 ID 需替换为经发现且被授权的目标。实际使用前核对当前版本对应 `--help`。

## 分页和输出

工作区机器、项目、Agent 配置、Role、MCP 目录默认有界，通常一页 20 项，页大小上限 100。支持分页的命令用同样筛选条件和 cursor 继续，或用该命令支持的 `--all-pages`。`items`、`hasMore` 和可选 `nextCursor` 决定是否结束，不能从第一页面数猜总数。

支持 `--json` 的查询优先读取结构化结果；保留 stderr 的错误类别，不能把空 stdout 当空目录。各目录的机器、项目等专属数组别名不是新的独立查询。对于 `operation` 等目录不要假定它们也支持 `--all-pages`，查具体帮助。

## 0.107.2 的目录 JSON 兼容

部分目录命令虽退出 0，仍会在完整 JSON 前后向 stdout 输出 `[WORKSPACE_ID] Remote Streams transport attached/detached`。这是已核实的版本行为；会话命令另有 stderr 路由，不能假定所有命令相同。

自带 doctor 已做窄兼容：先严格解析整个 JSON，必要时只接受一个完整单行 JSON 及同一 workspace ID 的上述两种精确消息；字段及分页完成条件继续验证。其他日志、多个 JSON、跨工作区前缀、截断响应都应报错。不要任意取最后一行或把解析失败当空目录；不回显原始日志中的身份或凭证。

## 本机目录与工作区目录

不带工作区/catalog 选项的 `project list` 保留本机 daemon 项目列表行为。需要从未运行本机 daemon 的客户端查看工作区项目时，使用明确的工作区目录路径。工作区目录可包含已授权机器的本地项目和已启用 GitHub 仓库；`--machine` 限制为该机器本地项目。

`github list` 只列当前工作区已经链接的仓库，不能把 GitHub App 有权限但未加入工作区的仓库也算进去。OSS/local platform 不支持全部 cloud 目录查询。`--offline` 不等于跳过授权，GitHub 目录仍有连接前提。

## 能力证据

- `machine list` 的 `onlineStatus` 可以为 online、offline 或 unknown；未知不能报告成离线。
- 旧的 `--include-agents`、`--include-acp-capabilities` 详情输出不能混用目录分页/筛选选项；使用 `agent-config list/get` 做有界发现。
- `agent-config get` 和会话创建选项可暴露目标 mode/config option 的 ID、类型和选择。用实际能力值，不从模型名称推导权限模式。
- Role 不可用时仍可能出现在列表，需读取原因，不能自动换机或换配置。
- MCP 列表隐藏连接值；已选择或有配置不证明当前 Turn 成功加载。

## 核验与失败处理

结果应包含选中的明确工作区与资源标识、查询条件和分页完成情况。权限失败、重名、机器状态未知或能力缺失时，保留具体缺口，继续不依赖它的只读工作。不要创建替代资源或扩大访问权限来让发现通过。

来源：[CLI：资源发现与分页](https://lody.ai/zh/docs/cli/)、[CLI 类型支持](https://lody.ai/zh/docs/cli-runtimes/)、[ACP 与扩展能力](https://lody.ai/zh/docs/acp-feature-support/)。
