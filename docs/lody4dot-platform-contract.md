# lody4dot 平台契约与 T01 证据

核实日期：2026-10-20。适用：Codex CLI 0.163.0，Lody 研究基线 0.107.2。

2026-10-21按C01重新核对了同版本官方清单/加载/marketplace源码和本机帮助，原契约仍成立。本轮又读到9篇OpenAI官方帮助正文，确认Dot是ChatGPT中的具体产品，拥有自己的cloud computer，并能创建Codex云任务；两种执行环境分别建模。共享连接、安装路线及未决生命周期问题见[宿主接入核实记录](lody4dot-host-contracts.md)，不把资料核实写成插件已安装或Dot接入成功。

## 分发契约

OpenAI 官方 `rust-v0.163.0` 源码确认：原生清单位于 `.codex-plugin/plugin.json`，`skills` 可以是字符串或数组，路径以插件根为准，必须以 `./` 开头，不允许 `..` 或包外路径。未显式声明时默认读取 `skills/`。

采用的原生产物结构为：

```text
dist/lody4dot/
  .codex-plugin/plugin.json
  .agents/plugins/marketplace.json
  skills/lody4dot/SKILL.md
  skills/lody4dot/references/
  scripts/
  runtime/
```

源码仍分别在 `skill/lody4dot/` 和 `plugin/lody4dot/` 维护，构建时复制技能。源码清单不能指向 `../../skill/`；未经构建的源码目录不当作原生安装包。

自包含产物内的本地 marketplace 以产物根为基准，使用 `source: {"source": "local", "path": "."}` 定位同一插件。CLI 的正式入口是 `codex plugin marketplace add`、`codex plugin add` 和 `codex plugin list`，不是 `plugin install`。

官方Help另确认ChatGPT web可在具备权限时上传插件ZIP，以及管理员可导入GitHub marketplace；这不等于当前包已通过UI扫描、安装或加载。当前`plugin/lody4dot/`源码由builder组合外部技能，不直接作为已包含skills的GitHub插件source；不为导入提交生成物或猜测source schema。完整格式指南位于`learn.chatgpt.com`，本轮未读；优先沿用自包含ZIP作为候选，并附正式上传入口及未验证范围。

跨界面分发还需分别判断工具类型：官方指出声明MCP的导入插件即使使用remote HTTPS也可能标为Desktop only，`.app.json`引用不会自动移除限制。ChatGPT技能安装/同步与Codex可以不同；插件安装不完成底层app授权。Dot/web远程工具候选应按受支持的custom MCP app或Sites路线另验，不能直接把桌面清单当成通用web安装包。

## 当前托管环境接入

本机 CLI 的格式和命令入口已核实，但当前任务的受保护 Codex 配置目录不可写；不通过修改 `HOME`、`CODEX_HOME` 或绕过权限来注册。当前云端采用受支持的环境 `start_skill` 显式读取技能入口和运行诊断，报告为“云环境接入”。原生产物同时交付，正式注册仅在支持的配置范围验证。

保存启动说明不等于已加载；新任务读取入口、随附资源和工具的回执仍属于 T09。T01 完成的是实际可选路线与格式契约，不声称原生注册或新任务加载通过。

## 运行与工具契约

- CLI 依赖与稳定入口在 `/workspace/.tools/lody4dot/`，位于 checkout 外；不与登录态混合。
- 安装器只准备 CLI，不自动登录、注册机器或启动 daemon；doctor 默认只读。
- installer 使用自有 marker、版本目录、验证后原子切换的 `current` 指向和稳定 `bin/lody`；失败保留旧指向。安装目录内部受控链接与分发包的包外链接是不同边界。
- 认证仅使用 `LODY_CLI_TOKEN`，显式调用已核实的登录入口。T01初期未观察到变量；后续已安全注入且真实授权通过，当前证据见[验证记录](lody4dot-validation.md)，不沿用早期缺失结论。
- 查询/观察和 create/chat/cancel 的运行进程前提分开，内置 MCP 需要实际注入的上下文。
- 默认状态和缓存目录需在允许写入的位置；不改变继承的代理和 CA，不禁用验证。

当前正式发布源码为0.2.0的`d27f1a0`，准备/启动说明已与该来源核对；工作副本0.2.1另含最新CLI版本提示规则，尚未改变正式来源。0.1.3是旧截图轮次的历史基线。新任务加载仍按[独立任务验收](lody4dot-fresh-task-acceptance.md)取得实际回执。发布确认不能替代该回执，也不要求为此再次发布相同配置。

## C01补充：准备入口与hooks

当前配置的`install_script`调用`bootstrap --prepare`，`start_skill`引导读取技能后调用`--repair-missing`，复用即可；保存字段与实际新任务执行分别取证。早期发布轮次的运行规则仍旧且三个官网均CONNECT403，保留为历史观测。本次spec/observed9、正式无草稿，网络快照已有三个OpenAI域名；运行状态网络仍`unknown`，不宣称已enforced/ready。实际帮助站及官网索引现可读取，开发站仍CONNECT403且不再重试；无需重复保存相同草稿。

官方0.163.0原生清单源码包含`hooks`字段；固定提交另定义会话级`SessionStart/SessionEnd`及管理策略。这些证据不能合并成“Dot支持存储重置hook”或“当前托管环境已经注册hook”。官方Codex Cloud帮助明确新任务各有独立workspace、发布setup只用于新任务，默认保存VM状态可在最近turn启动/resume起最多7天恢复；该规则不适用于Dot自身云电脑。Dot主动Reset是删除产品及其上下文的操作，不是周期磁盘重置通知。

Dot正式身份、共享插件连接和本地技能的产品能力已核实，lody4dot实际加载及Dot专属setup/maintenance、存储重建hooks仍待验证。共享连接不等于全空间访问，执行位置也不能凭当前工具存在推断。来源、权限边界及C01/C09剩余项见[宿主记录](lody4dot-host-contracts.md#初始化存储与会话事件)。

## 来源

- [清单解析与 skills 字段](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs)：`RawPluginManifest`、`resolve_manifest_path`。
- [默认技能路径](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/loader.rs)：`plugin_skill_roots`。
- [marketplace 路径解析](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/marketplace.rs)：`resolve_local_plugin_source_path`。
- 本机 `codex --version` 与 plugin/marketplace 帮助，以及预装插件清单，仅作为对应版本的运行实例旁证。
- [Lody CLI 文档](https://lody.ai/zh/docs/cli/)：登录、运行进程、发现与查询契约。
