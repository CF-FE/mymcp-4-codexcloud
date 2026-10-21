# lody4dot 平台契约与 T01 证据

核实日期：2026-10-20。适用：Codex CLI 0.163.0，Lody 研究基线 0.107.2。

2026-10-21按C01重新核对了同版本官方源码和本机帮助，并读取9篇官方帮助、4篇完整插件/Dot指南。Dot是ChatGPT中的具体产品，自己的cloud computer与其创建的Codex云任务分别建模。新增portable清单不废弃现有兼容格式；官方用户运行setup也不等于Dot重置hook。来源与边界见[宿主记录](host-contracts.md)，资料可读不代表插件已安装或Dot接入成功。

## 分发契约

OpenAI 官方 `rust-v0.163.0` 源码确认：Codex兼容清单位于 `.codex-plugin/plugin.json`，`skills` 可以是字符串或数组，路径以插件根为准，必须以 `./` 开头，不允许 `..` 或包外路径。未显式声明时默认读取 `skills/`。新读[包装指南](https://developers.openai.com/plugins/build/plugins)推荐根级`plugin.json`及自动发现的`skills/`作为portable格式，并明确旧兼容清单继续支持；本轮保留兼容格式，不迁移portable入口。

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

主技能源码仍在 `skill/lody4dot/`、组合与脚本在 `plugin/lody4dot/`；0.2.2候选另从唯一的`skill/lody4dot-setup/`源码收集setup技能。源码清单不能指向 `../../skill/`；未经构建的源码目录不当作原生安装包。上图是0.2.1结构，候选新增技能不代表正式环境已更新。

自包含产物内的本地 marketplace 以产物根为基准，使用 `source: {"source": "local", "path": "."}` 定位同一插件。CLI 的正式入口是 `codex plugin marketplace add`、`codex plugin add` 和 `codex plugin list`，不是 `plugin install`。

官方Help确认有权限者可在ChatGPT web上传插件ZIP、管理员可导入GitHub marketplace。完整[Plugin Management](https://learn.chatgpt.com/docs/enterprise/plugin-management)本轮已HTTP200，支持native、Claude、Agent Plugins 1.0及受支持技能包；Source为仓库URL、Path为包含清单的目录，本地条目路径相对所选marketplace根。当前源码仍需builder组合外部技能，不能直接作为完整GitHub插件source；导入不会运行builder，也不为此提交生成物。指南未说明ZIP外层包装的接受规则，UI扫描、安装和加载仍未验。

0.2.2候选仅在兼容清单增加`extensions.com.openai.onboardingSkill: "./skills/lody4dot-setup/SKILL.md"`。路径相对插件根且技能必须随包提供；用户运行setup时才会在新会话或当前安装会话调用，不承诺安装自动执行。若未来采用portable格式，内联`extensions.com.openai`会整体替换兼容overlay而非合并，需单独迁移验收。详情见[用户运行setup契约](host-contracts.md#portable格式与用户运行setup)。

跨界面分发还需分别判断工具类型：官方指出声明MCP的导入插件即使使用remote HTTPS也可能标为Desktop only，`.app.json`引用不会自动移除限制。ChatGPT技能安装/同步与Codex可以不同；插件安装不完成底层app授权。Dot/web远程工具候选应按受支持的custom MCP app或Sites路线另验，不能直接把桌面清单当成通用web安装包。

## 当前托管环境接入

本机 CLI 的格式和命令入口已核实，但当前任务的受保护 Codex 配置目录不可写；不通过修改 `HOME`、`CODEX_HOME` 或绕过权限来注册。当前云端采用受支持的环境 `start_skill` 显式读取技能入口和运行诊断，报告为“云环境接入”。原生产物同时交付，正式注册仅在支持的配置范围验证。

保存启动说明不等于已加载；新任务读取入口、随附资源和工具的回执仍属于 T09。T01 完成的是实际可选路线与格式契约，不声称原生注册或新任务加载通过。

## 运行与工具契约

- CLI 依赖与稳定入口在 `/workspace/.tools/lody4dot/`，位于 checkout 外；不与登录态混合。
- 安装器只准备 CLI，不自动登录、注册机器或启动 daemon；doctor 默认只读。
- installer 使用自有 marker、版本目录、验证后原子切换的 `current` 指向和稳定 `bin/lody`；失败保留旧指向。安装目录内部受控链接与分发包的包外链接是不同边界。
- 认证仅使用 `LODY_CLI_TOKEN`，显式调用已核实的登录入口。T01初期未观察到变量；后续已安全注入且真实授权通过，当前证据见[验证记录](validation.md)，不沿用早期缺失结论。
- 查询/观察和 create/chat/cancel 的运行进程前提分开，内置 MCP 需要实际注入的上下文。
- 默认状态和缓存目录需在允许写入的位置；不改变继承的代理和 CA，不禁用验证。

当前正式来源、checkout版本、runtime与readiness统一见[当前环境与下一步](../../.codex/agent-state/todo.md#当前环境与下一步)。0.2.0的`d27f1a0`和旧截图0.1.3保留为历史。新任务加载仍按[独立任务验收](fresh-task-acceptance.md)取得回执，发布确认不能替代该证据，也不要求重复发布相同配置。

## C01补充：准备入口与hooks

`install_script`调用`bootstrap --prepare`，`start_skill`引导读取技能后调用`--repair-missing`，复用即可；保存字段与实际新任务执行分别取证。spec12的四篇HTTP200、当时readiness unknown和Cloud list 401保留在[历史观测](host-contracts.md#本轮结论)，不作为当前快照。本地ChatGPT登录状态不等于Cloud API授权，不能据此猜Cloud ENV_ID。

官方0.163.0源码包含`hooks`及会话级`SessionStart/SessionEnd`。新包装指南仅支持手动安装于Codex desktop的lifecycle hooks，web安装不部署脚本；用户运行`onboardingSkill`又是另一入口。这些证据均不能合并成“Dot支持存储重置hook”。Codex Cloud新任务各有独立workspace，已发布setup用于新任务，默认VM恢复窗口最多7天；不推广为Dot规则。Dot电脑官方可在使用间隔保持状态，但永久保留、重置周期和初始化回调未给出；主动Reset是产品及上下文删除操作。

Dot正式身份、共享插件连接和本地技能的产品能力已核实；C01按有界调查条件收口，未知Dot自有setup/maintenance与存储hook保持未知，对应分支不实施。实际加载与工具调用仍由C05/C09验收。共享连接不等于全空间访问，执行位置也不能凭当前工具存在推断；来源及边界见[宿主记录](host-contracts.md#初始化存储与会话事件)。

## 来源

- [清单解析与 skills 字段](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs)：`RawPluginManifest`、`resolve_manifest_path`、`resolve_openai_onboarding_skill`；字段解析不证明实际setup调用。
- [默认技能路径](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/loader.rs)：`plugin_skill_roots`。
- [marketplace 路径解析](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/marketplace.rs)：`resolve_local_plugin_source_path`。
- [Plugin Management](https://learn.chatgpt.com/docs/enterprise/plugin-management)、[Package your plugin](https://developers.openai.com/plugins/build/plugins)：2026-10-21 HTTP200；portable/兼容格式、source/path、用户运行setup与hooks范围。
- [Dot computers and apps](https://learn.chatgpt.com/docs/dots/computers-and-apps)、[Getting started](https://learn.chatgpt.com/docs/dots/getting-started)：同日HTTP200；执行位置、连接与状态保持边界。
- 本机 `codex --version` 与 plugin/marketplace 帮助，以及预装插件清单，仅作为对应版本的运行实例旁证。
- [Lody CLI 文档](https://lody.ai/zh/docs/cli/)：登录、运行进程、发现与查询契约。
