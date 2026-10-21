# lody4dot交接记录与离线校验

本文说明自lody4dot`0.2.0`引入并沿用的schema1。`handoff.py`检查调用方提供记录的结构与声明一致性，不读取远端对象，不创建、继续或取消任务，不证明实时授权或业务完成。协作与恢复的设计依据见[开发方案](collaboration-development.md)；真实结果仍需使用合法连接核对。

真实Lody派发继续使用schema1；纯Cloud／Space资料交接不填造假的Lody引用，使用[资料交接记录卡](space-cloud-handoff.md#5-资料交接记录先用文档约定)。混合任务分别记录Lody执行与资料保存／回读，通过真实原生引用关联；该记录卡是文档约定，不新增schema或字段。

## 运行入口与检查阶段

在仓库根目录运行；`--input`必须指向已有普通JSON文件：

```bash
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage intent --json
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage dispatched --json
python3 plugin/lody4dot/scripts/handoff.py --input /path/to/private-handoff.json --stage result --json
```

独立分发包改用包内的`python3 scripts/handoff.py`，其余参数相同。默认阶段为`intent`，没有`--output`、联网查询或派发参数；报告只写stdout，输入不被修改。真实ID和业务资料应保存在私密记录中，公开回执仅保留必要的脱敏结果。

| 阶段 | 必需内容与声明核对 |
| --- | --- |
| `intent` | `schema_version:1`，非空目标与授权范围；尚未取得的原生引用和版本可为null。已提供的字段仍要满足各自格式。 |
| `dispatched` | 加上Lody的workspace、session、user_turn，以及执行位置（executor_ref或machine）和插件/CLI版本。 |
| `result` | 再加assistant_turn及匹配三种回合引用的持久化、已同步终态观察。最新声明观察须支持同一结果；completed还需至少一个结果工件，failed/canceled允许没有工件。 |

检查阶段不代表Lody状态变化。`result`结构完整可以描述完成、失败或取消；任何一种退出0都只是记录检查通过。

## 字段约定

| 字段 | 格式与边界 |
| --- | --- |
| `*_ref` | 对象含`system`、`kind`、`id`；Lody引用的system必须为`lody`，kind要与所属字段相符。关联号只关联记录，不是服务端幂等键。 |
| `lody_refs` | 可含workspace、machine、agent_config、session、user_turn、assistant_turn；两种turn不可混用或填成同一个ID。ChatGPT会话不能冒充Lody session。 |
| `versions` | plugin、cli为非空字符串；source_commit若提供，须为40或64位十六进制；environment可保留null。版本来源仍需调用方实际核实。 |
| `observations` | source为persisted/metadata/unknown，freshness为synced/stale/unknown；时间为带时区的ISO格式。result需匹配session/user_turn/assistant_turn，最新声明观察为persisted、synced及completed/failed/canceled，冲突终态不通过。 |
| 输入/结果工件 | 含location、executor_ref、sha256、byte_length、access_method、evidence_origin；摘要为64位十六进制，长度为非负整数。输入可以属于另一执行器；结果不能与同命名空间已声明执行机器冲突。工具不会打开location。 |
| `expected_outputs` / `unresolved` | 文本数组；分别说明预期结果和未决事项，不能用未决说明填补缺失的关键引用。 |

根字段固定，未知字段会被拒绝；JSON重复键、非有限数字、过深或过大的输入同样被拒绝。文件上限为1MiB，输入文件不能是符号链接。秘密键名和可识别的凭证值会被拒绝，但规则仅覆盖已知模式，仍须由记录提供者排除秘密。

## 可运行的虚构示例

以下全部ID、位置、授权和观察都是fixture，不是平台对象或真实执行回执。工件示例内容为`{"ok":true}`后接一个LF，UTF-8共12字节，摘要已计算；校验器仍不会读取或验证这份内容。将JSON保存为自有临时文件，再运行上面的命令即可检查格式。

```json
{
  "schema_version": 1,
  "correlation_ref": {"system": "lody4dot", "kind": "correlation", "id": "fixture-correlation"},
  "objective": "Check a fictional deterministic JSON result.",
  "authorization_scope": "Only fictional fixture resources are in scope.",
  "coordinator_ref": {"system": "fixture", "kind": "agent", "id": "fixture-coordinator"},
  "control_host_ref": {"system": "fixture", "kind": "runtime", "id": "fixture-controller"},
  "executor_ref": {"system": "lody", "kind": "machine", "id": "fixture-machine"},
  "lody_refs": {
    "workspace": {"system": "lody", "kind": "workspace", "id": "fixture-workspace"},
    "machine": {"system": "lody", "kind": "machine", "id": "fixture-machine"},
    "agent_config": {"system": "lody", "kind": "agent_config", "id": "fixture-agent-config"},
    "session": {"system": "lody", "kind": "session", "id": "fixture-session"},
    "user_turn": {"system": "lody", "kind": "user_turn", "id": "fixture-user-turn"},
    "assistant_turn": {"system": "lody", "kind": "assistant_turn", "id": "fixture-assistant-turn"}
  },
  "input_artifacts": [],
  "expected_outputs": ["A 12-byte JSON fixture"],
  "versions": {"plugin": "0.2.0", "cli": "0.107.2", "source_commit": null, "environment": null},
  "observations": [{
    "source": "persisted",
    "freshness": "synced",
    "status": "completed",
    "observed_at": "2026-10-21T08:00:00+08:00",
    "evidence_origin": "fictional_fixture",
    "session_ref": {"system": "lody", "kind": "session", "id": "fixture-session"},
    "user_turn_ref": {"system": "lody", "kind": "user_turn", "id": "fixture-user-turn"},
    "assistant_turn_ref": {"system": "lody", "kind": "assistant_turn", "id": "fixture-assistant-turn"}
  }],
  "result_artifacts": [{
    "location": "/fictional-executor/result.json",
    "executor_ref": {"system": "lody", "kind": "machine", "id": "fixture-machine"},
    "sha256": "e5f1eb4d806641698a35efe20e098efd20d7d57a9b90ee69079d5bb650920726",
    "byte_length": 12,
    "access_method": "agent_readback",
    "evidence_origin": "fictional_fixture"
  }],
  "unresolved": []
}
```

这个完整示例在三个阶段都可通过结构检查。新任务仅有意图时，不要复制fixture ID来填空：原生引用和版本保留null，只在`intent`阶段检查；待实际请求返回后再填真实引用。

## 解释报告

- 退出`0`且`status:pass`：所选阶段的结构与声明一致性通过。`validation_scope`固定为`structure_and_declared_consistency`。
- 退出`3`且`status:blocked`：缺少阶段必需内容或符合条件的结果声明，可按`findings`中固定路径与代码补齐已有证据。
- 退出`2`且`status:fail`：输入或字段不合法、类型/引用冲突等；内部错误退出`10`。工具不回显业务值或真实ID来解释错误。
- `not_verified`仍包括identity、service_acl、authorization、provenance、business_outcome、artifact_contents、current_freshness和executor_identity_mapping。跨系统执行器引用没有冲突，不代表实际身份映射已验证。
- `credential_scan:known_patterns_only`不是没有秘密的保证；`timestamp_check:format_and_declared_order_only`只比较声明时间，不证明观察现在仍新鲜。

交付前仍须由获授权的Agent核对原生session/turn、实际服务返回和产物内容。需要恢复控制端时先对账原请求，不因一份结构通过的记录自动重发任务；完整流程见[技能协作参考](../../skill/lody4dot/references/collaboration.md)。
