# Agent 配置、Role、MCP 与 GitHub

## 从可用配置开始

先按 [资源发现](discovery.md) 找到 workspace、机器和配置，再查询具体配置/Role。Agent 可用模型、mode 和 config options 来自目标运行时的能力协商；不同 provider 或版本不自动支持同一组选项。

```bash
lody agent-config get AGENT_CONFIG_ID --workspace WORKSPACE_ID --json
lody agent-role get ROLE_ID --workspace WORKSPACE_ID --json
lody agent-config show AGENT_CONFIG_ID --json
```

`show` 的安全输出与支持参数应核对对应版本；不要默认使用 `--show-secrets`。发现列表和 get 不作为完整凭证备份。更新返回的配置 ID 或 changed fields 不代表字段内容已经被检查，应另做安全查询。

## Agent 配置变更

`agent-config create/update/delete` 是真实配置变更，只在当前任务允许的范围内使用。通过该命令实际支持的环境文件入口提供所需变量，不把 token 写进聊天、示例或日志。更新时区分未传字段、空字符串清空和删除环境键，不能用一份不完整配置覆盖其他用户设置。

实际 `0.107.2` 的 `session create --help` 已将每会话 `--env` 标为 deprecated，要求改在 Agent config 配置环境。官网旧示例仍曾说明每会话环境保存；遇到该差异以当前准确版本帮助为准，不继续推荐旧入口。差异记录在 [来源记录](sources.json)。

安装或升级底层 coding CLI、修改环境或可用模式后，可在正确机器上刷新能力：

```bash
lody agent-config refresh-capabilities AGENT_CONFIG_ID --workspace WORKSPACE_ID
```

官网说明此操作需要本机运行进程，CLI 目前不支持跨机器刷新；不能仅因为远端机器在线就在当前云机刷新它。Registry 或 Custom ACP 仍要求目标主机已安装相应运行时、依赖和凭证。自定义 Launch command 直接作为进程及参数启动，不执行 pipes、重定向、glob 或变量展开；环境应放入 Agent 配置。

## Role 的两种使用

创建会话时，Role 绑定的 machine、Agent config、model/mode 等配置会覆盖部分手工参数；注意 ignored-flags 警告，以解析后的真实配置报告执行位置。Role 不包含新的 API key，也不是一个永久驻留 Agent。

通过 CLI 或 MCP 生成角色创建/更新提议时，命令成功只表示确认卡片已生成。用户在 Lody 保存后才生效，忽略卡片不修改角色。创建默认私有；更新保留未要求修改的字段。

```bash
lody agent-role create --file role.json --session SESSION_ID
lody agent-role update ROLE_ID --file patch.json --session SESSION_ID
```

JSON 文件和直接字段参数不能混用。更新文件只包含补丁字段，不再包一层 patch；角色 ID 放位置参数，重试使用相同输入及支持的 `--request-id`。可修改字段与限制查 `agent-role create/update --help`；不支持的字段不能用猜测值绕过。

## MCP 与 GitHub

`mcp list/add/set/remove` 的确切参数以帮助为准。配置变更和连接测试分别核验；不要把“保存了 MCP”当“当前 agent 已加载”。内置 Lody MCP 需要宿主注入会话、工作区和机器上下文，不能使用内部入口临时拼一个无上下文的服务。

`github list --workspace WORKSPACE_ID --json` 用于查看已经链接的仓库；访问目录与 GitHub 账户/App 授权是不同前提。不要从其他 Git 代理能够读某个仓库，推导 Lody 已完成 GitHub 集成授权。

## 成功证据

报告真实变更与目标标识；提议保留“待保存”，刷新能力需看到新能力查询结果，MCP 需要加载/调用证据。配置保存、运行时已安装、Agent 任务执行是独立状态。失败时不自动换机、提高权限或泄漏配置值。

来源：[CLI 文档](https://lody.ai/zh/docs/cli/)、[Agent 角色](https://lody.ai/zh/docs/agent-roles/)、[CLI 类型支持](https://lody.ai/zh/docs/cli-runtimes/)、[ACP 与扩展能力](https://lody.ai/zh/docs/acp-feature-support/)。
