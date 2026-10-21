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

已核对的 `0.107.2` 允许多个不同 Role 复用同一 `machineId` 和 `agentConfigId`，分别提供名称、说明和提示词前缀；这不会复制 Agent 配置或凭证。

创建会话时，Role 绑定的 machine、Agent config、model/mode 等配置会覆盖部分手工参数；注意 ignored-flags 警告，以解析后的真实配置报告执行位置。Role 不包含新的 API key，也不是一个永久驻留 Agent。

通过 CLI 或 MCP 生成角色创建/更新提议时，命令成功只表示确认卡片已生成。用户在 Lody 保存后才生效，忽略卡片不修改角色。创建默认私有；更新保留未要求修改的字段。

该版本以 cloud 身份运行 CLI 时，提议通过当前登录身份机器的合法会话工具执行 `session/call-tool`，需要对应的会话与运行条件；创建字段中的 `machineId` 只是 Role 的绑定目标，不选择提议调用的机器。不能从无本机 host 的控制端已能向远端派发普通会话，推导它也能生成角色提议；已有 MCP 路线同样须核实实际宿主上下文，不手工调用内部入口或为此自动启动 host。

```bash
lody agent-role create --file role.json --session SESSION_ID
lody agent-role update ROLE_ID --file patch.json --session SESSION_ID
```

JSON 文件和直接字段参数不能混用。更新文件只包含补丁字段，不再包一层 patch；角色 ID 放位置参数，重试使用相同输入及支持的 `--request-id`。可修改字段与限制查 `agent-role create/update --help`；不支持的字段不能用猜测值绕过。

`0.107.2` 的 create 业务字段为 `name`、`machineId`、`agentConfigId`，以及可选的 `description`、`promptPrefix`；保存后初始 `runConfig` 为空。update 补丁仅支持 `name`、`description`、`promptPrefix`，不能据此承诺 CLI 可编辑产品界面的全部运行设置。其他版本以其实际帮助和 schema 为准。

## Project 与 Role 的组合

该版本的 `project add` 登记运行命令那台机器的本地目录，不迁移代码或登记另一台机器的目录；只在允许项目配置写入时使用。创建会话可组合 `--agent-role` 与 `--local-project` 或 `--repo`，后两者互斥。先按 Role 解析最终机器和配置，再核对本地项目属于该机器，不能把控制端路径当作远端项目。会话参数及结果核验见[会话工作流](sessions.md)。

这确认的是“按某 Role 执行某项目任务”；尚未核实 Project 持久拥有一组 Role 的绑定，不能据此编造该分组关系，也不据此断言其他版本或产品界面没有组织功能。角色提议、用户保存、只读查询已保存角色及按该角色执行项目任务分别取证，保存成功不代表执行成功。

## MCP 与 GitHub

`mcp list/add/set/remove` 的确切参数以帮助为准。配置变更和连接测试分别核验；不要把“保存了 MCP”当“当前 agent 已加载”。内置 Lody MCP 需要宿主注入会话、工作区和机器上下文，不能使用内部入口临时拼一个无上下文的服务。

`github list --workspace WORKSPACE_ID --json` 用于查看已经链接的仓库；访问目录与 GitHub 账户/App 授权是不同前提。不要从其他 Git 代理能够读某个仓库，推导 Lody 已完成 GitHub 集成授权。

## 成功证据

报告真实变更与目标标识；提议保留“待保存”，刷新能力需看到新能力查询结果，MCP 需要加载/调用证据。配置保存、运行时已安装、Agent 任务执行是独立状态。失败时不自动换机、提高权限或泄漏配置值。

来源：[CLI 文档](https://lody.ai/zh/docs/cli/)、[Agent 角色](https://lody.ai/zh/docs/agent-roles/)、[CLI 类型支持](https://lody.ai/zh/docs/cli-runtimes/)、[ACP 与扩展能力](https://lody.ai/zh/docs/acp-feature-support/)、[0.107.2 发布源码](https://registry.npmjs.org/lody/-/lody-0.107.2.tgz)。
