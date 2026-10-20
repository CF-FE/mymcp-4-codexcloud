# lody4dot 云端执行前提补充

日期：2026-10-20。本文记录 T10 的独立准备；状态权威仍为 [任务队列](../.codex/agent-state/todo.md)。未启动 Lody host、创建 Session 或发送模型任务。

## 发布配置与当前实例

用户已发布包含 `*.streams-api-x.loro.dev` 的环境。保存配置读取已无草稿，正式规则中有该后缀；现有进程仍有 `LODY_CLI_TOKEN`。本次不重复写入配置或要求重交凭证。

前次观测的运行实例仍为 revision 4、仅四个域名，Loro 请求 CONNECT 403。本次发布后，同一实例的 `spec_revision/observed_spec_revision` 已均为 **5**，分片规则生效；api/control-b/presence 的无凭证 HTTPS 请求均退出 0、根路径 404。真实账户、完整目录和会话元数据观察随后通过，网络不再是这些检查的阻塞。来源版本号或根路径状态本身仍不能代替业务请求结果。

## 适配器和真正的 builtin 运行时

对 `lody@0.107.2` 发布代码核实：

- 随包有 `dist/codex-acp.js` 和 chunk；适配器 `--version` 实测 `acp-extension-codex 1.12.0`、退出 0。
- `resolveBuiltinACPProcessLaunch` 优先采用 `runtimeOverrides.codexPath`，否则安装 managed Codex **0.160.1**。系统 Codex **0.163.0** 存在不等于 builtin 会使用它。
- `mergeACPProcessEnv` 中 launch 环境覆盖配置环境，故 Agent config 的 `--env CODEX_PATH=...` 不能跳过 managed 解析和下载。
- 公开 create/update CLI 未提供该 runtimeOverrides 或 custom command 参数，不修改底层 store 伪造支持入口。

当前平台的 managed 资源为：

```text
https://api.lody.ai/api/runtimes/codex/0.160.1/linux-x64/codex-package-x86_64-unknown-linux-musl.tar.zst
SHA-256: 05f9279fcfb76564a1801dd835286a56277c0a4dd97d94f58543e71b2ed5f80c
size: 115738874
```

先前仅 HEAD 返回 200；本次已按上列固定输入真实下载，大小和 SHA-256 均匹配，检查归档不存在越界路径、链接或特殊条目后解包到自有缓存。实际二进制 `--version` 退出 0、输出 `codex-cli 0.160.1`。这是独立预检；没有写官方 managed 完成标记。`ManagedAgentRuntimeManager` 会验证大小与哈希后解包并创建受管入口，无需 npm 安装脚本；最终仍应由官方受管流程完成安装。

## 无模型 ACP 初始化探测

为检查当前系统 Codex 与适配器，直接使用该入口所要求的 `CODEX_PATH=/opt/codex/bin/codex`，仅发送 ACP `initialize`；这是一条独立预检，不冒称 builtin 默认链路。

第一次返回 RPC error **1001**，结构化错误命中 SQLite 初始化失败；stderr 同时有只读警告。`codex --help` 本身也可出现 PATH aliases 的同类警告，因此该警告不能单独定位失败原因。

依据官方源码，以新的私密 `/tmp` 目录设置单独的 `CODEX_SQLITE_HOME` 后重试一次：仍返回 RPC error **1001**，未初始化成功。错误不再命中此前 SQLite 关键词，但这不证明数据库设置已被采用或其余写入路径可用。没有进一步猜测权限绕过。

两个探测均移除子进程中的 Lody token，没有 `session/new`、`turn/start`、模型提示或认证材料复制；只终止自己启动的进程。受控项目输入和产物断言已在本机临时目录准备，实际产物尚未生成。

为排除仅系统版本不同导致失败，本次使用已校验的 **0.160.1** 重做 bundled ACP `initialize`：默认仍 RPC **1001**，结构化错误包含 SQLite 初始化失败。仅为子进程指定自有 `0700` 临时 `CODEX_SQLITE_HOME` 后重试，仍 RPC **1001**，实际 RPC 错误改为 `read-only`。这次证据来自 RPC 响应，不能与 stderr 的 PATH aliases 警告混为一谈；也不能声称 SQLite 目录调整已让执行可用。两次均无会话、模型、登录或 host；临时状态已清理，已校验二进制仅留在忽略的缓存。

随后仅做源码和文件系统元数据核实，未继续重试：同版本 [app-server 启动](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/app-server/src/lib.rs#L777) 在 SQLite 成功后无条件调用 `resolve_installation_id(&config.codex_home).await?`；[实现](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/core/src/installation_id.rs#L17) 创建 home，并以 read/write/create 打开 `installation_id` 后加锁，已有合法 ID 也先尝试可写打开。该函数没有独立目录参数；sqlite_home、log_dir 和 cwd 都不改变此路径。本机实际 Codex home 所在文件系统只读且 installation_id 不存在，没有读取 ID 或认证内容。这是源码与元数据证据，不冒称系统调用跟踪。

因此当前托管云机的已验证范围是安装、控制查询和观察。本机 Codex 执行需要平台提供可写执行环境，或另行验收已授权的 Lody worker；不改变 HOME/CODEX_HOME、复制认证或绕过托管要求。此限制属于当前运行环境，不泛化为其他平台均不可执行。

官方配置边界：

- [0.163 sqlite_home 字段](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/config.schema.json#L8058)；[解析和 log_dir](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/config/mod.rs#L4205)。
- [0.160.1 同字段](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/core/config.schema.json#L7664)；[同样的解析优先级](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/core/src/config/mod.rs#L4081)。
- `cfg.sqlite_home` 优先于 `CODEX_SQLITE_HOME`，再回退 CODEX_HOME；[平台强制要求](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/config/requirements.rs#L35) 仍可覆盖配置，不得绕过。
- 该设置只迁移 SQLite。[rollout 路径](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/rollout/src/recorder.rs#L1739) 仍使用 codex_home 下 sessions 目录，log_dir 也有独立默认位置；不能由此承诺只读宿主已可创建 Session。

## 工作区范围与后续任务

`LodyFleet.startWorkspaceSubscription → applyRemoteWorkspaceList → applyWorkspaceList` 使用 API-key 返回的全部工作区，为它们建立 runtime 并后台登记本机/默认配置。`--workspace` 和 `LODY_WORKSPACE_ID` 选择业务目标，不过滤 host 的订阅范围。

用户仅选择个人工作区作为隔离验收目标；没有据此扩大为对其他工作区的本机/配置写入授权。启动 host 前需要核实有受支持的范围限制，或另行明确该具体副作用的授权。不能靠手改 store、使用内部 MCP 入口或猜环境变量缩小范围。

同时避开 `LODY_E2E`、`LODY_TITLE_AGENT` 的认证复制分支；后续受控任务使用固定标题，保持 HOME/CODEX_HOME 和已有认证边界。

网络及运行前提满足后的公开 CLI 路线是：在个人工作区登记本机临时项目 → 发现本机已存在的配置 → 确无合适配置时创建一次 → 用固定标题创建一个小任务 → observe/history 与实际产物断言。Role 如绑定其他机器，不能直接套用本机临时路径；Role 覆盖与真实任务能力分别验收。

本次探测结束后已清理自有临时项目和独立数据库目录；保留脱敏结果与上述任务规范，后续真实验收时重新建立隔离输入。全局凭证绑定和用户目录未改变。
