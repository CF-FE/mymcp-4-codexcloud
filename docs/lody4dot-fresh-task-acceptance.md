# 新云任务的接入验收

适用：已发布的lody4dot 0.1.3，Lody CLI 0.107.2。状态仍以[任务队列](../.codex/agent-state/todo.md)为准。

本轮已核实正式配置包含源码提交`a2e67962cba7cfdcb2e4c01fcec5a9bc644d0248`，启动说明与该提交的`.codex/cloud-start.md`一致，无待发布草稿。当前会话没有新建或附着独立Codex云任务的工具。继续本会话、重新读取文件或给子agent提供入口，都不能替代从已发布环境启动新任务的证据。

## 在已发布环境创建新任务

使用同一环境和仓库创建一个独立云任务。只给目标，不把技能路径提前写进提示；让新agent记录平台实际交付的启动说明和入口。可以使用：

> 验收这个已发布环境中的lody4dot云端接入。先记录环境是否自动提供了启动说明及技能入口，再按提供的指引做版本检查、重复安装和只读发现/观察。授权复用安全注入的LODY_CLI_TOKEN，只操作我指定的个人工作区；工作区无法唯一确定时先报告候选。不要创建、继续或取消会话，不改远端配置，不启动daemon，不打印凭证。入口缺失时如实报告。

## 实际执行与回执

1. 记录是否收到平台启动指引，以及实际从何处获知技能入口。随后读取SKILL和目标所需参考，报告资源路径和版本；只有文件存在不算读取回执。
2. 在现有checkout运行inspect，再用安装器做同锁复用。记录CLI版本、锁摘要、reused和退出码；不得创建worktree或重新登录来掩盖安装问题。
3. 新建0700私密任务state，登录前verify-only应报告未认证；只验证这个新state，不推断整个平台没有其他身份。随后用显式login复用已注入变量，做账户与选定工作区的完整机器目录查询。
4. 对获准观察的会话只读observe；记录source、freshness和实际状态，区分metadata与persisted。没有获准会话时保留观察未运行，不随意读取其他用户任务。
5. 删除自己创建的认证state，保留全局变量绑定。不把登录态移入安装目录、插件包或共享快照，不复制底层Agent认证。

建议回执包含以下不含身份信息的字段：

```json
{
  "startup_instructions_received": true,
  "entry_discovery_source": "environment_start_instructions",
  "skill_and_reference_reads": ["实际读取的资源路径"],
  "plugin_version": "0.1.3",
  "cli_version": "0.107.2",
  "install_reused": true,
  "inspect_exit": 0,
  "new_private_state_unauthenticated_before_login": true,
  "account_and_complete_catalog": "实际结果",
  "observation_source_and_freshness": "实际结果或未运行原因",
  "owned_auth_state_cleaned": true
}
```

模板字段必须按实际结果填写，不能原样复制为成功证据。不在公共回执中写工作区、机器、会话标识或业务文本。此项验收选定的start_skill云接入路线；原生插件注册是另一条路线，单独保留未验证。状态清理和新state的负向检查也不构成平台级快照隐私证明。
