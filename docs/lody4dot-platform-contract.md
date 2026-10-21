# lody4dot 平台契约与 T01 证据

核实日期：2026-10-20。适用：Codex CLI 0.163.0，Lody 研究基线 0.107.2。

2026-10-21按C01重新核对了同版本官方清单/加载/marketplace源码和本机帮助，原契约仍成立。多宿主、Dot、初始化及生命周期的新增证据见[宿主接入核实记录](lody4dot-host-contracts.md)；用户已授权持续推进c1任务，C01的已知宿主结论与Dot未决输入分别维护，不把计划写成接入成功。

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

0.1.3的正式发布源码和启动说明已核实；新任务加载仍按[独立任务验收](lody4dot-fresh-task-acceptance.md)取得实际回执。发布确认不能替代该回执，也不要求为此再次发布相同配置。

## C01补充：准备入口与hooks

当前配置已有`install_script`安装Lody并inspect，`start_skill`引导读取技能并inspect，复用即可；保存字段与实际新任务执行分别取证。用户本次发布后，正式自定义规则包含OpenAI官方三个站点且无草稿，但当前实例运行规则仍旧，单次官网访问仍在代理处CONNECT403。该差异只影响对应资料读取，不阻塞独立实现，也不要求重存相同草稿。

官方0.163.0原生清单源码包含`hooks`字段；固定提交源码另外定义了会话级`SessionStart/SessionEnd`等事件及管理策略。这些证据不能合并成“Dot支持存储重置hook”或“当前托管环境已经注册hook”。Dot按用户所指ChatGPT云服务独立建模，官方身份、安装/工具和存储生命周期接口尚未核实。来源、适用范围和后续判定见[宿主记录](lody4dot-host-contracts.md#初始化会话hooks与存储事件)。

## 来源

- [清单解析与 skills 字段](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs)：`RawPluginManifest`、`resolve_manifest_path`。
- [默认技能路径](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/loader.rs)：`plugin_skill_roots`。
- [marketplace 路径解析](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/marketplace.rs)：`resolve_local_plugin_source_path`。
- 本机 `codex --version` 与 plugin/marketplace 帮助，以及预装插件清单，仅作为对应版本的运行实例旁证。
- [Lody CLI 文档](https://lody.ai/zh/docs/cli/)：登录、运行进程、发现与查询契约。
