# 本地Codex CLI接入

宿主加载与OS运行支持分别检查。Codex CLI本身提供多种平台版本，不代表本插件安装工具已经跨平台；当前受管runtime工具只支持Linux。macOS、WSL和Windows均需各自真实验证，WSL不称原生Windows支持。

在允许写入配置的Codex CLI环境，先核对本机`codex --version`和plugin帮助。本包清单与marketplace依据已核实的Codex CLI0.163.0契约；从完整自包含包注册，而不是从源码中尚未生成skills目录的插件文件夹注册：

```bash
codex plugin marketplace add /absolute/path/to/lody4dot
codex plugin add lody4dot@lody4dot-local
codex plugin list --json
```

注册命令会修改本机宿主配置，仅用于用户选择安装的目标；当前受保护的托管配置不据此获得写权限。注册成功与后续Agent实际读取技能分别取证。

Linux目标可从自包含包根目录使用[准备工具](../scripts/bootstrap.py)。先将LODY4DOT_PREFIX设为该端实际自有、可写的安装目录，不套用另一机器的路径：

```bash
python3 scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --prepare --json
python3 scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --repair-missing --json
```

准备与检查不登录或启host。需要连接Lody时使用该端独立凭证通道与私密状态，工具入口来自本端安装回执；不从云端复制认证。控制端、执行节点和混合角色分别验证。两处安装不会自动成为两个在线Lody节点。

任务交接使用实际workspace/machine/config/session/user/assistant引用和所属执行器，产物通过获授权的通道传递。包内`skills/lody4dot/references/collaboration.md`给出选择与恢复规则；[离线交接工具](../scripts/handoff.py)只检查结构和声明一致性，不能证明真实权限或任务完成。

来源：[官方Codex清单源码](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core-plugins/src/manifest.rs)与本机0.163.0帮助；在目标宿主取得真实注册/读取回执后才确认其接入。未知产品、版本或接口保持未知。
