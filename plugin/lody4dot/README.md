# lody4dot

为 Codex agent 提供 Lody 的任务指引、版本化命令资料，以及独立的安装、只读诊断和显式认证工具。首个安装目标是 Linux Codex 云环境，工具需要 Python 3.10+、npm 和 Lody 支持的 Node：`>=22.14.0 <23` 或 `>=23.6.0`。

能力源码在仓库的 `skill/lody4dot/`；本目录负责运行时锁定和分发，不新增 MCP 服务。Lody 已有 MCP 只有在宿主提供有效 session/workspace/machine 上下文时才使用，不能将其内部入口当作独立通用服务。

## 从仓库安装 CLI

在仓库根目录执行：

```bash
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot --json
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --json
/workspace/.tools/lody4dot/bin/lody --version
```

安装器使用固定依赖与锁文件，在自有暂存目录安装并验证，成功后切换稳定入口。它不登录、不注册机器、不启动 daemon。失败时保留旧版本与用户状态；不应将工具目录、npm 缓存或登录态提交到仓库。不要将一个已有非空目录直接指定为工具目录。

CLI 固定版本为 `0.107.2`；锁定输入、依赖修订及实际验证以 `runtime/` 和仓库任务队列为准。安装成功与 inspect 通过只证明本地工具前提，不代表账户、长连接或 Agent 任务已经验证。

## 认证与云端运行

复用环境中安全注入的 `LODY_CLI_TOKEN`；不要在聊天、命令文本或日志中复制值。此名称是本插件约定，Lody CLI 不会因此自动登录。新身份先使用本任务私有的状态目录；`mktemp -d` 在此创建权限为 `0700` 的目录。需要验证已有登录时，改用该身份原有的私有 `LODY_DATA_DIR`，不创建新目录替代它。先只读验证；需要登录时再显式执行最后一条：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
python3 plugin/lody4dot/scripts/auth.py --prefix /workspace/.tools/lody4dot --verify-only --json
python3 plugin/lody4dot/scripts/auth.py --prefix /workspace/.tools/lody4dot --login --json
```

登录会保存本机身份，配对或设备授权流程还可能连接/注册机器。0.107.2 的 API-key 路径验证 token 后保存本机身份；远端机器注册和在线状态仍需独立运行证据。CLI 当前的受支持入口通过子进程 argv 接收凭证；适配器不经 shell 展开，也不输出凭证，但本机同权限进程仍可能读取 argv，因此只在可信、隔离的任务环境中使用。凭证存在、登录成功、工作区权限和底层 Agent 凭证是不同条件。`session create/chat/cancel` 等执行操作还需要受支持的本机运行进程；查询可用不能证明这些操作可用。

保留继承的代理与 CA，不关闭 TLS 校验。官网资料使用 `lody.ai`；npm 下载及 CLI 的登录、API、观察链路还需各自网络权限。`convex.lody.ai`、`backend.lody.ai`、`api.lody.ai` 是当前发布物中的服务目的地，仍应按真实连接结果分别确认。配置已保存或官网能访问均不是全部网络通过的证据。

登录后的账户查询与目标工作区目录是两条连接链路。检查目录时显式指定目标；只查询工作区列表不会证明机器目录可用：

```bash
python3 plugin/lody4dot/scripts/doctor.py --profile control --connect --workspace WORKSPACE_ID --json
```

当前部署还会返回 Loro Streams 网关与分片后缀 `streams-api-x.loro.dev`。实测 `api`、`control-b`、`control-c`、`presence` 子域在只放行四个 Lody 域时被 CONNECT 403 拦截。源码的控制/数据/写入/presence 分片会使用同一后缀；云网络需包含 `*.streams-api-x.loro.dev`，不以只读账户查询成功替代该链路验证。该后缀属于本次实际返回值，部署变化时应重新核实。

状态通过 Lody 支持的 `LODY_DATA_DIR` 分离；身份不进入插件包和共享环境快照。不修改 `HOME` 或 `CODEX_HOME` 绕过受保护的宿主配置。云端启动说明应显式读取技能入口并运行 doctor；保存说明后仍需要新任务提供实际加载回执。

## 自包含插件包

源码目录中的 `skills: "./skills"` 由构建产物满足；不要直接将源码目录作为已完整的原生插件安装。

在仓库根目录构建：

```bash
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot --json
```

构建会收集技能、参考、工具和锁定输入，拒绝缺失资源、符号链接、包外引用、额外文件和可识别的凭证文件，生成 `.lody4dot-build.json` 哈希清单。产物不包含依赖安装目录或身份状态；自有且完整的旧产物可重新构建，陌生目录或被修改的产物不会被覆盖。

将整个产物目录复制到其他位置后，以产物根为工作目录执行 `python3 scripts/install.py`、`python3 scripts/doctor.py` 和 `python3 scripts/auth.py`。技能入口为 `skills/lody4dot/SKILL.md`；随附参考均在包内。

在允许写入配置的 Codex CLI 环境，可以使用已核实的原生入口：

```bash
codex plugin marketplace add /absolute/path/to/lody4dot
codex plugin add lody4dot@lody4dot-local
codex plugin list --json
```

原生清单和 marketplace 格式依据 Codex CLI `0.163.0` 同版本官方源码。构建成功、注册成功、新任务加载技能分别验收；当前托管环境的受保护配置不能通过改写环境目录绕过。托管云配置的 `start_skill` 接入应报告为云环境接入，不能冒称已经原生注册。

## 验证与支持范围

在仓库根目录执行：

```bash
python3 -m unittest discover -s tests/lody4dot -v
python3 scripts/check_repository.py
```

离线测试验证工具行为和分发边界，不能代替真实账户、长连接、宿主加载或任务产物验收。完整命令资料的帮助证据也不等于全部业务功能已经实测。当前实现进度和真实验证缺口统一记录在仓库的 `.codex/agent-state/todo.md`。
