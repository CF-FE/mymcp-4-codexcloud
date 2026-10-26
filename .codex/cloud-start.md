# 云任务启动说明

使用 `/workspace/mymcp-4-codexcloud` 中现有 checkout；不创建 Git worktree，除非用户明确要求。

先读取`skill/organization-collaboration/SKILL.md`，按本次组织岗位读取必要参考，并复用当前有效任务包。确认业务责任人、汇报对象与实际通道、唯一派发者、验收者、协议/岗位/关系版本和原生任务引用；无依据的项保留UNKNOWN，只暂停依赖该缺项的动作。已批准任务内的读取和实现步骤不重复建单，普通跟进不重扫组织。该skill仅含Markdown，独立于Lody和专业角色库；不为组织接入安装Node或登录。

本组织由公子确认云端Dot统筹。Dot代建项目Cloud任务时，项目owner仍负责审阅规划分配和验收，Cloud沿原关联回传结果；Dot自身协调任务可用工作区上下文。不要因创建者、机器名或专业角色推定任职。岗位/角色新增更新及接管按组织skill的maintenance参考处理，普通在途版本与当前权限撤销分别判断。修改此源码指引不等于保存云环境已更新或新任务已实际读取，分端回执另验。

涉及 Lody 时，先读取 `skill/lody4dot/SKILL.md`，再按目标读取随附参考。稳定 CLI 是 `/workspace/.tools/lody4dot/bin/lody`，先检查依赖，仅在受管依赖明确缺失时进入安装准备：

```bash
cd /workspace/mymcp-4-codexcloud
if [ -x /workspace/.tools/lody4dot-node/current/bin/node ]; then
  export PATH="/workspace/.tools/lody4dot-node/current/bin:$PATH"
fi
python3 plugin/lody4dot/scripts/bootstrap.py --prefix /workspace/.tools/lody4dot --repair-missing --json
```

准备脚本`.codex/cloud-install.sh`先调用`scripts/prepare_cloud_node.py`，校验官方归档的SHA256后安装或复用Linux x64 Node `24.22.1`，再准备Lody latest。此Node版本是已验证兼容基线；未来latest要求更高版本时应更新并验证Node基线，不能降级CLI或忽略engines。实际安装收据及CLI/doctor的`node_path`决定解释器；平台`/opt`内建Node未改。启动检查不联网补装Node；受管Node缺失时报告缺项，在授权准备阶段重跑准备脚本。源码和当前任务更新不等于保存环境模板或固定ref已更新/发布。此启动说明属于云环境接入，不证明原生插件已经注册或新任务已经加载。首次任务需要记录入口和资源读取回执。

`bootstrap.py`默认只做离线inspect；`--prepare`在环境准备时按已授权策略解析官方npm latest、暂存精确锁、受管安装/复用并检查；`--repair-missing`先检查，仅在受管依赖明确缺失时进入同一安装路线。Lody CLI版本差异或版本探测失败只warn，不阻塞或触发重装；`doctor.py --check-updates`仅查询提示，不自动升级。安装保留engine-strict、禁用生命周期脚本和原锁约束，真实失败不覆盖旧入口。网络、身份或实际运行错误分别处理。它不恢复登录态、启动daemon或重建模型任务。环境中断后先按已持久化的原生session/turn引用查询原任务，核对产物；状态未知时停止重派。

当前随包帮助为0.108.1；先核实际CLI版本与目标命令`--help`，再只读选择已允许的workspace、machine、project catalog与Agent config/Role。没有指定工作区或合法已有身份时报告最小缺项，不自动选历史资源、登录、注册或发起任务。HTTP探针不代替原CLI查询，403诊断仅保留必要脱敏证据，见`skill/lody4dot/references/troubleshooting.md`。

安装与环境快照只保存依赖，不登录、不注册机器、不启 daemon。需要账户操作时，在当前任务的同一 shell 中先创建私密状态目录：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
```

后续命令显式传同一路径或继承此变量；已有私密登录态应使用它原来的目录。确认当前操作需要授权后，使用 `auth.py --login` 复用安全注入的 `LODY_CLI_TOKEN`。不展开或打印值；变量缺失只报告注入缺口，不要求用户在聊天重交密钥。不要在发布前执行登录或把登录态放到依赖目录/共享快照。

登录会写本机身份，部分授权流程还会连接或注册机器；已有登录仅用 `auth.py --verify-only` 检查。doctor 的 `--connect` 只做资源查询；查询成功不能证明 Agent 任务已经可以执行。先区分控制端和执行端：0.107.2 的公开 CLI 可向已有授权、在线的远端 machine/config 派发，控制端无需启动本机 daemon；本机执行才需要本机 runtime 与可写 Codex 状态。创建、继续、取消前核实明确目标及执行端进程、Agent 凭证和权限。用户允许使用已有 Agent 时，优先复用现有配置，不为派发远端任务启动覆盖全部工作区的本机 host。所有业务成功结论须以实际持久化状态和产物为据。
