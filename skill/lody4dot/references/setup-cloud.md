# Codex 云端准备

## 目标与运行前提

先决定当前任务只需诊断和查询、从控制端派发远端任务，还是需要在这台机器执行 Agent。受管安装准备按已授权策略解析官方npm的`lody@latest`，在暂存目录更新精确锁并验证；本轮源码锁与实际帮助为`0.108.1`，不是未来latest或业务准入要求。版本差异或探测失败只提示。工具的Node支持范围仍为`>=22.14.0 <23`或`>=23.6.0`，安装另用engine-strict核对实际CLI及依赖的要求。原生依赖、OS、代理与CA、长连接、宿主加载和执行端Agent凭证仍分别验证。

本页的绝对路径和POSIX权限示例服务于Linux Codex云端。Work Cloud由平台托管，不自动采用这里的仓库环境、准备脚本、路径或身份；先按[宿主与任务入口](collaboration.md#work-cloud与任务创建)核对实际能力。迁移到其他宿主时使用该端实际安装回执与已验证接入，不能只替换路径就宣称跨平台；宿主与控制/执行角色的选择见[多宿主协作](collaboration.md)。下表是检查或验收范围，不是doctor已经证明角色可用；doctor不会派发模型任务。

Dot是ChatGPT中的always-on agent产品，其自有云电脑与它创建的Codex云任务分开。官方支持Dot使用预先在Codex配置好的云环境创建任务；本页的Codex准备入口适用于实际选中的Codex环境，不自动覆盖Dot自己的云电脑。Dot使用本地电脑另需该电脑在ChatGPT桌面应用明确连接授权并在线，local skills也需该连接；已有Codex连接或Work Sync不授予Dot本地访问。共享插件权限仍限已授予的应用连接，不证明任务已加载技能或具备Lody执行条件。

| 配置 | 能做什么 | 不能据此推导什么 |
| --- | --- | --- |
| inspect | 检查安装、版本、资料、凭证是否存在 | 不能证明已登录或任务可执行 |
| control | 已授权资源发现、会话历史与观察 | 不能证明当前 CLI 能创建或控制本机任务 |
| task | 核对实际执行端运行进程与凭证后完成受控任务；执行端可为远端 | 不能证明永久在线、跨任务恢复或其他模型可用 |
| worker | 长期承载机器与 Agent | 需另有进程和身份恢复证据，不能由文件快照推导 |

## 仓库工具入口

在仓库根目录，使用随插件实现的工具。准确可用参数以脚本自己的 `--help` 和插件 README 为准：

```bash
if [ -x /workspace/.tools/lody4dot-node/current/bin/node ]; then
  export PATH="/workspace/.tools/lody4dot-node/current/bin:$PATH"
fi
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --json
```

上述Node路径是本任务的受管官方Node安装位置；本轮实际为Node`24.22.1`、npm`11.19.1`，平台`/opt`内建Node未改。CLI launcher及doctor从安装收据的`node_path`选择解释器，避免PATH变化后退回旧Node。其他执行器须核对自己的路径。当前任务文件和源码更新未保存或发布到环境模板，不能据此声称新任务会采用它们。

inspect与启动bootstrap默认离线，不会隐式登录、检查npm更新或启动服务。需要查最新版本时显式运行：

```bash
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --check-updates --json
```

这只发起一次npm latest查询，不安装或升级。实际CLI较旧、实际版本探测失败、更新查询失败均作为warn；没有其他失败时仍退出0。版本不同或未知时继续按当前命令帮助和真实响应判断，认证/权限、缺依赖和其他必要检查失败不被掩盖。需要验证已有账户状态时，在当前任务准备独立私密目录，或使用已经核实属于当前身份的目录：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
python3 plugin/lody4dot/scripts/auth.py --prefix /workspace/.tools/lody4dot --verify-only --json
```

新建目录没有登录态，verify-only 应如实报告缺前提，不会自动登录。auth 的 `--data-dir` 或 `LODY_DATA_DIR` 必需；目录必须由当前用户拥有、权限为 `0700` 且没有符号链接，显式 login 可新建安全目录。仅在当前任务允许登录时运行 `auth.py --login`。需要只读连接诊断时显式运行 doctor 的 `--connect` 并指明私密状态目录；`control` 不带此标志保持 blocked，`task/worker` 也不会因只读查询通过就报告真实执行能力。

若上述文件未随当前分发提供，报告资料/工具不完整，不把示例命令当作已经执行。独立分发包的工具布局和入口由包内 README 说明。后续所有 `lody` 示例代表安装器报告的稳定绝对入口，默认安装位置为 `/workspace/.tools/lody4dot/bin/lody`，不用临时 `_npx` 缓存路径登记启动项。

## 凭证和授权

用户通过环境变量 `LODY_CLI_TOKEN` 提供材料；不要求在聊天中重复提供。只观察变量是否非空，不打印值、前缀、长度，不运行环境转储。这个名称是 `lody4dot` 约定，不是已证明会由 CLI 自动读取的变量。

认证适配器区分只读验证已有登录和显式登录。0.108.1发布源码审查显示：API-key路径验证已有token并保存本机machine-id/credentials，没有该分支显式创建远端key或注册machine；配对路径会exchange，设备授权会创建远端CLI API key，两者不能混入只允许临时本地身份的授权。以上是静态`source_verified`，本轮未执行新版登录或远端注册验收。只有当前任务允许相应认证副作用时才使用显式入口；不得在命令文本、日志、异常或包里展开token，不通过拼接shell启动。

0.108.1没有新增直接读取`LODY_CLI_TOKEN`完成认证的官方入口，也没有已核实的无状态目录查询flag；CLI目录路线仍依赖已有credentials及本地SQLite。不要为了省去登录而拼接内部HTTP协议、自造token存储或伪装stateless目录SDK。缺合法身份或写入许可时报告具体缺项；不要把token存在、无凭证健康检查或单个HTTP探针当CLI查询成功。准确来源见[来源记录](sources.json)。

当前适配器通过不经过 shell 的子进程 argv 调用 CLI 原生授权入口，避免 shell 历史并脱敏输出；这不隐藏操作系统的进程参数，同用户或更高权限进程仍可能观察它。不要在无法满足该运行边界的共享主机上把这种方式当作完全保密的传递通道。

变量未注入、凭证被拒、workspace 不可访问是不同结果。全局配置已保存不代表当前任务已收到变量；等待配置传播或任务启动时再检查，不能据此另造同名 secret。云代理的占位材料也不能不经验证直接保存为本地登录态。

## 状态、网络和启动

- Lody 支持 `LODY_DATA_DIR`；依赖目录、任务状态和身份状态分开。环境安装脚本与共享快照只准备依赖，登录在任务启动后显式进行。`/tmp` 路径本身不保证被快照排除；共享包或共享环境快照不得包含登录态，目录名字本身不能证明隔离。
- 账户查询与目录同步分开诊断：需要目标目录时用 `doctor.py --profile control --connect --workspace WORKSPACE_ID --json`。只读工作区列表成功不能证明机器、Role 或观察链路可用。
- 当前部署由后端返回 `streams-api-x.loro.dev` 作为 Loro Streams 后缀，目录同步实测访问 `api`、`control-b`、`control-c` 和 `presence` 子域。源码还按同一后缀生成控制、数据、写入和 presence 分片；当前云网络需允许 `*.streams-api-x.loro.dev`，部署变更后重查实际路由，不放宽到整个供应商域。
- 保留继承的代理与 CA 配置。`lody.ai` 可读只证明官网链路；实际登录、API 和观察连接需分别检验，不关闭 TLS 校验解决错误。
- `0.107.2` 的 `session create/chat/cancel` 按目标选择路径：本机目标需要本机运行进程；远端目标经机器 RPC，控制端无 host/daemon 也可派发，执行端仍需运行进程与 Agent 凭证。取消在无活动回合时还可直接返回 `alreadyStopped`，不能据此报告实际取消。`agent-config refresh-capabilities` 仍保留本机要求。
- 仅在确需本机执行时考虑启动 `lody start` 或 daemon；先确认登录、机器身份、任务授权和原有运行进程。host 的工作区登记范围另见兼容性参考，不能因为要派发远端任务就自动启动本机 host。
- 0.108.1源码显示`start`缺身份时可能进入设备授权，daemon启动也可做认证preflight；它们不是只读健康检查。`logout`仅清除本机保存身份，不证明远端CLI key已撤销；不为诊断自动启停或注销。
- 登录 Lody 不等于目标 Agent 的模型凭证已经准备好。创建任务前核实目标运行时能力和账户条件。
- 服务进程不会因为仓库文件和依赖恢复就自动恢复；长期启动使用稳定安装入口，并检查运行中的版本。只管理自己启动的进程。

## 环境准备与恢复

准备阶段的安装器及`bootstrap --prepare`每次在自有暂存目录定向运行`npm update lody --package-lock-only`解析latest，再用得到的精确锁执行`npm ci`或复用同锁运行时；保留其余锁定依赖约束与reviewed override，禁用生命周期脚本、校验官方registry来源及Node engines，通过帮助和native模块验证后才切换。latest解析、完整性或真实安装失败保留当前入口，不静默退回旧锁并报告已更新。

运行入口先做离线检查，明确缺少所属受管依赖时才由`--repair-missing`进入上述安装路线。已有runtime的版本差异或探测失败只提示，不触发重装。锁/摘要/来源完整性失败与陌生prefix仍按实际错误处理，不能以覆盖安装掩盖。不把登录态放进共享包或快照，不同时登录、注册machine或启host。

恢复后分别验证当前身份与目标范围，再用已有原生session/turn对账；任务仍运行则恢复观察，已完成则核验对应产物。没有关联记录就保留未知，不凭相同标题重建任务，不把初始化当成继续业务的授权。任务过程中把必要关联与成果保存到实际持久化目的地，不能依赖重置前通知或本地临时目录。

平台准备脚本、Agent启动指引、会话hook和存储重置事件各自核实。官方Dot文档的Reset是用户主动删除Dot的产品操作，未说明定期磁盘重置，也未给出可注入初始化的存储事件hook。Codex云准备脚本可以为该Codex环境准备依赖，不能据此声称已挂到Dot云电脑启动或重置；不猜事件名、不自动注册服务。跨端身份、文件和失败处理见[协作参考](collaboration.md)。

## 成功证据与退出

分别记录插件实际加载、CLI实际版本或查询未知、帮助/命令结果、账户资源查询和任务闭环。inspect可带版本warn通过，账户/任务仍可能未执行，不能把它们一起标为成功。安装失败保留旧版本与用户状态；真实命令、身份和权限失败保留原有退出码与分类，继续已有授权内不依赖该失败的工作，不改配置范围或自行创建workspace。

来源：[快速开始](https://lody.ai/zh/docs/quickstart/)、[CLI 文档](https://lody.ai/zh/docs/cli/)、[npm 发布元数据](https://registry.npmjs.org/lody)、[Dot入门](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)、[Dot工作区管理](https://help.openai.com/en/articles/20001554-manage-dots-in-chatgpt-workspaces)、[Dot隐私与权限FAQ](https://help.openai.com/en/articles/20001529-dots-privacy-security-and-safety-faqs)（Dot资料读取于2026-10-21）。
