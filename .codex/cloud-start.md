# 云任务启动说明

使用 `/workspace/mymcp-4-codexcloud` 中现有 checkout；不创建 Git worktree，除非用户明确要求。

涉及 Lody 时，先读取 `skill/lody4dot/SKILL.md`，再按目标读取随附参考。稳定 CLI 是 `/workspace/.tools/lody4dot/bin/lody`，检查依赖，缺失时按锁定输入修复：

```bash
cd /workspace/mymcp-4-codexcloud
python3 plugin/lody4dot/scripts/bootstrap.py --prefix /workspace/.tools/lody4dot --repair-missing --json
```

此启动说明属于云环境接入，不证明原生插件已经注册或新任务已经加载。首次任务需要记录入口和资源读取回执。

`bootstrap.py`默认只做inspect；`--prepare`在环境准备时安装并检查；`--repair-missing`先检查，仅在受管依赖缺失时安装。Lody CLI版本差异或版本探测失败只warn，不阻塞或触发重装；需要查最新版时显式运行`doctor.py --check-updates`，查询失败也只提醒，不自动升级。网络、身份或实际运行错误分别处理。它不恢复登录态、启动daemon或重建模型任务。环境中断后先按已持久化的原生session/turn引用查询原任务，核对产物；状态未知时停止重派。

安装与环境快照只保存依赖，不登录、不注册机器、不启 daemon。需要账户操作时，在当前任务的同一 shell 中先创建私密状态目录：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
```

后续命令显式传同一路径或继承此变量；已有私密登录态应使用它原来的目录。确认当前操作需要授权后，使用 `auth.py --login` 复用安全注入的 `LODY_CLI_TOKEN`。不展开或打印值；变量缺失只报告注入缺口，不要求用户在聊天重交密钥。不要在发布前执行登录或把登录态放到依赖目录/共享快照。

登录会写本机身份，部分授权流程还会连接或注册机器；已有登录仅用 `auth.py --verify-only` 检查。doctor 的 `--connect` 只做资源查询；查询成功不能证明 Agent 任务已经可以执行。先区分控制端和执行端：0.107.2 的公开 CLI 可向已有授权、在线的远端 machine/config 派发，控制端无需启动本机 daemon；本机执行才需要本机 runtime 与可写 Codex 状态。创建、继续、取消前核实明确目标及执行端进程、Agent 凭证和权限。用户允许使用已有 Agent 时，优先复用现有配置，不为派发远端任务启动覆盖全部工作区的本机 host。所有业务成功结论须以实际持久化状态和产物为据。
