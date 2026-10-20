# 云任务启动说明

使用 `/workspace/mymcp-4-codexcloud` 中现有 checkout；不创建 Git worktree，除非用户明确要求。

涉及 Lody 时，先读取 `skill/lody4dot/SKILL.md`，再按目标读取随附参考。稳定 CLI 是 `/workspace/.tools/lody4dot/bin/lody`，执行只读预检：

```bash
cd /workspace/mymcp-4-codexcloud
python3 plugin/lody4dot/scripts/doctor.py --prefix /workspace/.tools/lody4dot --profile inspect --json
```

此启动说明属于云环境接入，不证明原生插件已经注册或新任务已经加载。首次任务需要记录入口和资源读取回执。

安装与环境快照只保存依赖，不登录、不注册机器、不启 daemon。需要账户操作时，在当前任务的同一 shell 中先创建私密状态目录：

```bash
export LODY_DATA_DIR="$(mktemp -d /tmp/lody4dot-state.XXXXXX)"
```

后续命令显式传同一路径或继承此变量；已有私密登录态应使用它原来的目录。确认当前操作需要授权后，使用 `auth.py --login` 复用安全注入的 `LODY_CLI_TOKEN`。不展开或打印值；变量缺失只报告注入缺口，不要求用户在聊天重交密钥。不要在发布前执行登录或把登录态放到依赖目录/共享快照。

登录也会注册机器；已有登录仅用 `auth.py --verify-only` 检查。doctor 的 `--connect` 只做资源查询；查询成功不能证明本机 Agent 任务已经可以执行。创建、继续、取消任务前核实本机运行前提、目标和底层 Agent 凭证。所有业务成功结论须以实际查询或持久化结果为据。
