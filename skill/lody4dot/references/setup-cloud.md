# Codex 云端准备

## 目标与运行前提

先决定当前任务只需诊断和查询，还是需要在这台机器执行 Agent。Node 需满足 Lody 所支持的 `>=22.14.0 <23` 或 `>=23.6.0`；本知识基线为 `lody@0.107.2`。原生依赖、代理与 CA、长连接、宿主加载和底层 Agent 凭证仍需分别验证。

| 配置 | 能做什么 | 不能据此推导什么 |
| --- | --- | --- |
| inspect | 检查安装、版本、资料、凭证是否存在 | 不能证明已登录或任务可执行 |
| control | 已授权资源发现、会话历史与观察 | 不能证明当前 CLI 能创建或控制本机任务 |
| task | 满足本机运行前提后完成受控任务 | 不能证明永久在线、跨任务恢复或其他模型可用 |
| worker | 长期承载机器与 Agent | 需另有进程和身份恢复证据，不能由文件快照推导 |

## 仓库工具入口

在仓库根目录，使用随插件实现的工具。准确可用参数以脚本自己的 `--help` 和插件 README 为准：

```bash
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --json
```

inspect 默认离线，不会隐式登录或启动服务。需要验证已有账户状态时，在当前任务准备独立私密目录，或使用已经核实属于当前身份的目录：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
python3 plugin/lody4dot/scripts/auth.py --prefix /workspace/.tools/lody4dot --verify-only --json
```

新建目录没有登录态，verify-only 应如实报告缺前提，不会自动登录。auth 的 `--data-dir` 或 `LODY_DATA_DIR` 必需；目录必须由当前用户拥有、权限为 `0700` 且没有符号链接，显式 login 可新建安全目录。仅在当前任务允许登录时运行 `auth.py --login`。需要只读连接诊断时显式运行 doctor 的 `--connect` 并指明私密状态目录；`control` 不带此标志保持 blocked，`task/worker` 也不会因只读查询通过就报告真实执行能力。

若上述文件未随当前分发提供，报告资料/工具不完整，不把示例命令当作已经执行。独立分发包的工具布局和入口由包内 README 说明。后续所有 `lody` 示例代表安装器报告的稳定绝对入口，默认安装位置为 `/workspace/.tools/lody4dot/bin/lody`，不用临时 `_npx` 缓存路径登记启动项。

## 凭证和授权

用户通过环境变量 `LODY_CLI_TOKEN` 提供材料；不要求在聊天中重复提供。只观察变量是否非空，不打印值、前缀、长度，不运行环境转储。这个名称是 `lody4dot` 约定，不是已证明会由 CLI 自动读取的变量。

认证适配器区分只读验证已有登录和显式登录。官网的 `login --auth` 也会注册机器，不能把它作为每次诊断的自动步骤。只有当前任务允许登录时才使用显式登录入口；不得在命令文本、日志、异常或包里展开 token。CLI 只能接受 argv 时需遵循适配器已经验证的传递边界，不通过拼接 shell 启动。

当前适配器通过不经过 shell 的子进程 argv 调用 CLI 原生授权入口，避免 shell 历史并脱敏输出；这不隐藏操作系统的进程参数，同用户或更高权限进程仍可能观察它。不要在无法满足该运行边界的共享主机上把这种方式当作完全保密的传递通道。

变量未注入、凭证被拒、workspace 不可访问是不同结果。全局配置已保存不代表当前任务已收到变量；等待配置传播或任务启动时再检查，不能据此另造同名 secret。云代理的占位材料也不能不经验证直接保存为本地登录态。

## 状态、网络和启动

- Lody 支持 `LODY_DATA_DIR`；依赖目录、任务状态和身份状态分开。环境安装脚本与共享快照只准备依赖，登录在任务启动后显式进行。`/tmp` 路径本身不保证被快照排除；共享包或共享环境快照不得包含登录态，目录名字本身不能证明隔离。
- 保留继承的代理与 CA 配置。`lody.ai` 可读只证明官网链路；实际登录、API 和观察连接需分别检验，不关闭 TLS 校验解决错误。
- 官网明确 `session create/chat/cancel` 与 `agent-config refresh-capabilities` 需要当前机器运行 `lody start` 或 `lody daemon start`。启动 daemon 前确认登录、机器身份、任务授权和原有运行进程。
- 登录 Lody 不等于目标 Agent 的模型凭证已经准备好。创建任务前核实目标运行时能力和账户条件。
- 服务进程不会因为仓库文件和依赖恢复就自动恢复；长期启动使用稳定安装入口，并检查运行中的版本。只管理自己启动的进程。

## 成功证据与退出

分别记录插件实际加载、CLI 版本/帮助可用、账户资源查询和任务闭环结果。inspect 通过时允许账户/任务为未执行，不能把它们一起标为成功。安装失败保留旧版本与用户状态；授权失败继续独立资料或本地诊断，不改配置范围、不自行创建 workspace。

来源：[快速开始](https://lody.ai/zh/docs/quickstart/)、[CLI 文档](https://lody.ai/zh/docs/cli/)、[npm 发布元数据](https://registry.npmjs.org/lody)。
