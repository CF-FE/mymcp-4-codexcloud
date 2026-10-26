# 发现工作区、机器、项目和能力

## 选择目标

已有当前任务确认的workspace/session等准确引用时，直接使用所需[会话命令](sessions.md#观察真实结果)，不为观察原任务重新遍历目录。首次派发或目标缺项时，先明确用户允许访问的workspace，再按需查询机器、项目或Agent配置。不要静默选首个匹配；名称冲突用显式ID。缓存中的可用性不是资源预留，也不是派发许可。

先使用稳定CLI检查实际版本和对应`--help`，再进行已授权的只读发现。下列参数已用0.108.1实际帮助核对；帮助通过不表示本次身份、工作区或目录已查询成功。复用官方CLI和原生JSON，不猜HTTP地址，也不以无状态探针替代CLI调用。尚未指定工作区时，最小缺项是允许访问的名称或ID；在已有合法身份和相应授权下可先列出工作区供选择，不自动选第一项。

产品协作空间、某执行器的 `/workspace` 目录与Lody workspace是三种对象，按已有上下文和对应工具定位；目录搜索不能替代空间对象访问。会话链接与上传文件也各有来源系统和读取范围，不能把ChatGPT会话引用当Lody sessionId。跨端定位规则见[多宿主协作](collaboration.md)。

```bash
lody workspace list --json
lody machine list --workspace WORKSPACE_ID --all-pages --json
lody project list --workspace WORKSPACE_ID --catalog --kind local --all-pages --json
lody agent-config list --workspace WORKSPACE_ID --machine MACHINE_ID --all-pages --json
lody agent-role list --workspace WORKSPACE_ID --all-pages --json
lody github list --workspace WORKSPACE_ID --json
lody mcp list --workspace WORKSPACE_ID --json
```

这些是可选择的命令，不是每次都要执行的清单。示例ID须来自已确认且获授权的目标；首次使用、版本变化或实际失败时核对对应帮助。

## 按命令读取随包资料

随包提供了可重复使用的[lookup离线入口](knowledge.md)：`lookup.py command 'session observe'`默认只读index，必要时加`--detail help`或`--detail audit`。以下内联读取仍可用于没有该脚本的既有版本，不必为了查询资料先升级安装。

三个JSON均以`commands[]`中的`command`定位单项。先从`command-index.json`取目标命令，需要参数或验证来源时再取`help-snapshot.json`或`command-audit.json`的同一项。以下路径替换为本端实际技能目录；脚本只读资料，不调用Lody：

```bash
python3 - /absolute/path/to/lody4dot/references/command-index.json 'session observe' <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
entries = [item for item in data["commands"] if item["command"] == sys.argv[2]]
if len(entries) != 1:
    raise SystemExit("Expected one exact command entry; check the command name and source.")
print(json.dumps(entries[0], ensure_ascii=False, indent=2))
PY
```

快照缺少当前命令或版本不同时，再读实际CLI的该命令帮助；不为查询一条命令展开完整审计矩阵，也不把历史帮助当作本次业务成功证据。

## 分页和输出

工作区机器、项目、Agent 配置、Role、MCP 目录默认有界，通常一页 20 项，页大小上限 100。支持分页的命令用同样筛选条件和 cursor 继续，或用该命令支持的 `--all-pages`。`items`、`hasMore` 和可选 `nextCursor` 决定是否结束，不能从第一页面数猜总数。

支持 `--json` 的查询优先读取结构化结果；保留 stderr 的错误类别，不能把空 stdout 当空目录。各目录的机器、项目等专属数组别名不是新的独立查询。对于 `operation` 等目录不要假定它们也支持 `--all-pages`，查具体帮助。

对0.108.1的`source_verified`核对显示，目录返回`sync.state: syncing`时可能仍退出0；应保留同步状态并等待获准的后续查询，不能把尚未同步的空`items`报告为资源不存在。只有所需范围新鲜、cursor/hasMore已结束且全部页校验通过，才报告完整目录。2026-10-25本次实际project/agent-config列表为fresh且无syncing标记、全部页完成；这不保证其他时间或版本总是如此。

`agent-config list/get`在该版本返回目录摘要，省略env、credentials和prompt；但runConfig中的选项值不能整段回传。只需选择Agent时，优先保留`id/name/machineId/cliType/agentType`及必要的`availability/capabilityStatus`，必要时再取models/modes的`id/name`。`show`默认虽隐藏env值，仍可包含prompt和titleGeneration配置值，并非更小的安全摘要；不为枚举改用`--show-secrets`或完整show输出。

## 0.107.2 的目录 JSON 兼容

部分目录命令虽退出 0，仍会在完整 JSON 前后向 stdout 输出 `[WORKSPACE_ID] Remote Streams transport attached/detached`。这是已核实的版本行为；会话命令另有 stderr 路由，不能假定所有命令相同。

自带 doctor 已做窄兼容：先严格解析整个 JSON，必要时只接受一个完整单行 JSON 及同一 workspace ID 的上述两种精确消息；字段及分页完成条件继续验证。其他日志、多个 JSON、跨工作区前缀、截断响应都应报错。不要任意取最后一行或把解析失败当空目录；不回显原始日志中的身份或凭证。

## 本机目录与工作区目录

不带工作区/catalog 选项的 `project list` 保留本机 daemon 项目列表行为。需要从未运行本机 daemon 的客户端查看工作区项目时，使用明确的工作区目录路径。工作区目录可包含已授权机器的本地项目和已启用 GitHub 仓库；`--machine` 限制为该机器本地项目。

0.108.1帮助提供`project list --catalog`及`--kind local|github`；配合明确`--workspace`选择跨机器catalog，需要某台机器的本地项目时再加`--machine`。Agent配置和Role也支持`--machine`筛选及`--all-pages`。先读取目录中的稳定ID与可用性，再按需`agent-config get`或`agent-role get`；“名称包含Codex”不能代替执行端凭据和能力核验。

`github list` 只列当前工作区已经链接的仓库，不能把 GitHub App 有权限但未加入工作区的仓库也算进去。OSS/local platform 不支持全部 cloud 目录查询。`--offline` 不等于跳过授权，GitHub 目录仍有连接前提。

## 能力证据

- `machine list` 的 `onlineStatus` 可以为 online、offline 或 unknown；未知不能报告成离线。
- 旧的 `--include-agents`、`--include-acp-capabilities` 详情输出不能混用目录分页/筛选选项；使用 `agent-config list/get` 做有界发现。
- `agent-config get` 和会话创建选项可暴露目标 mode/config option 的 ID、类型和选择。用实际能力值，不从模型名称推导权限模式。
- Role 不可用时仍可能出现在列表，需读取原因，不能自动换机或换配置。
- MCP 列表隐藏连接值；已选择或有配置不证明当前 Turn 成功加载。

## 2026-10-25有界官方CLI实测

在main `a86a63f67f023796023c488b80803acfe78649c2`同任务远程重载和初始化后，Node24.22.1/Lody0.108.1的显式已有APIkey临时认证、workspace list、local project catalog list、agent-config list/get通过；仅必要元数据白名单，临时credentials/cache已finally清理。其余命令与参数分支不由此算作通过，具体边界见[逐项矩阵](command-audit.json)。同任务源码重载不是环境模板更新或新容器；旧探针按用户要求忽略，当前以当日官方CLI结果为准。

## 核验与失败处理

结果应包含选中的明确工作区与资源标识、查询条件和分页完成情况。权限失败、重名、机器状态未知或能力缺失时，保留具体缺口，继续不依赖它的只读工作。不要创建替代资源或扩大访问权限来让发现通过。

失败时区分CLI原始退出码、HTTP状态和目标网络层。官网可读、无凭证健康探针成功或token存在均不证明目录可用；403也不能脱离实际请求、响应来源和目标hostname直接解释为工作区无权限。诊断规则见[故障处理](troubleshooting.md)。

来源：[CLI：资源发现与分页](https://lody.ai/zh/docs/cli/)、[CLI 类型支持](https://lody.ai/zh/docs/cli-runtimes/)、[ACP 与扩展能力](https://lody.ai/zh/docs/acp-feature-support/)。
