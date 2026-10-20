# lody4dot 平台契约与 T01 证据

核实日期：2026-10-20。适用：Codex CLI 0.163.0，Lody 研究基线 0.107.2。

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

## 来源

- [清单解析与 skills 字段](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs)：`RawPluginManifest`、`resolve_manifest_path`。
- [默认技能路径](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/loader.rs)：`plugin_skill_roots`。
- [marketplace 路径解析](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/marketplace.rs)：`resolve_local_plugin_source_path`。
- 本机 `codex --version` 与 plugin/marketplace 帮助，以及预装插件清单，仅作为对应版本的运行实例旁证。
- [Lody CLI 文档](https://lody.ai/zh/docs/cli/)：登录、运行进程、发现与查询契约。
