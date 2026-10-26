# 两层角色库与按需知识读取

2026-10-26，公子要求共同优化skill性能、推进角色库，明确工作区共享级/项目级，并授权辩证后启动Goal执行。本设计承接V2.2及现有CLI工具；实际进度仍在[唯一队列](../../../.codex/agent-state/todo.md)。

## 辩证结论

保留角色、方法和任务编排的分工，优先复用现有11份定义。两个独立上下文分别挑战风险与提出简化后，确认V2.2有两类共同合同、共享职责夹带项目特定要求；不能把简单删字当优化，也不能把一次机器/模型观测烘焙为通用能力。短文件若需多次串行读取，成本也可能增加。

采用短入口、精确单项读取、显式项目适配、一次完整组装；不增加远端服务、自动路由器、缓存或任意层级继承。已有单命令内联Python读取同样可行，新脚本的增量是可复用、可移位与失败行为可测；无Python时仍可直接阅读同一资料。外部方法只记录固定来源和可选关系，不暗示已安装。

## 所有权与范围

- 当前可编辑角色知识归`skill/lody4dot/references/roles/`；V2.2四文件与来源清单保留为历史，不改字节。
- `index.json`只维护角色元数据、项目适配、方法来源及版本；职责正文各维护一次。`common.md`保留必要的授权、单写者、UNKNOWN、证据/独立QA、模型建议与Save边界。
- 共享角色适用于工作区内跨项目任务；项目owner/模板须明确项目。显式选择项目才组合该项目合同。共享提示词不携带固定机器、真实ID或项目生产路径。
- 现有六共享职责、G8、项目owner与三模板共11个定义，不创建11个运行实例。定义版本与Lody实际Role ID、machine/config、模型、权限、Save/回读分开；库中的scope/project_id不是原生Lody字段。
- PR #4的[工作区执行规范](execution-policy.md)与[并行规范](../../../skill/lody4dot/references/collaboration.md#并行在办任务)已合入本地：本用户win-work新会话显式选择已核映射的codex over Claude配置，不降级；此规则作为当前任务输入，不烘焙为所有用户的通用角色默认。
- 保留作者/QA、共享研究/项目事实owner、运行工程/媒体作者的区别；凡人适配保留完整审稿/听证、共享锁、输入冻结与范围证据等硬条件。

本轮局部边界为BOUNDARY_NOTE：新增离线只读知识接口和随包角色资料；原生CLI、身份、副作用、分发所有权及已有schema1交接不变。新输出是中立知识，不可直接当agent-role create/update载荷。

## 最小数据合同

`roles/index.json`采用`schema_version: 1`、`library_version: "1.0.0"`：

- `common: {resource}`指向通用合同。
- `roles[]`：`id/name/scope/kind/summary/resource/methods/source_role_id`；scope为workspace或project，project条目另有`project_id`。id在库内唯一；kind保留coordinator/shared_role/project_owner/task_template区别。
- `projects[]`：`id/name/resource`，只显式组合一项，不做覆盖继承。
- `methods[]`：`id/name/relation/bundled/source`；本轮relation为optional_method或inspiration，bundled=false；source记录repository、commit、path、url、license。它们不构成运行前置，实际任务要求的方法不可得时只暂停依赖步骤，不自动安装或改走未经允许的方法。
- `provenance`记录V2.2仓库路径、冻结commit、原文件SHA-256及本库的派生说明；不把历史runtime_created状态作为现在的部署状态。

resource是相对index的本地Markdown路径，必须属于roles目录内的普通文件，不穿越符号链接；所有引用在源码与解包产物中校验。外部方法url只作为资料，不联网获取。角色依赖必须能解析到methods中的唯一ID；完整组装结果不得超过已核实的32768字符提示词上限，不静默截断。

## 离线入口

源码使用`python3 plugin/lody4dot/scripts/lookup.py`，自包含包使用`python3 scripts/lookup.py`。根目录由脚本位置定位，与cwd无关；命令返回JSON，失败非零且不输出部分结果。

```text
lookup.py command 'session observe' [--detail index|help|audit]
lookup.py roles [--scope workspace|project] [--project fanren-work]
lookup.py role ROLE_ID [--project fanren-work] [--render]
lookup.py check
```

command默认仅返回一条原index对象，保留来源文件、知识版本和验证范围；detail只读取相应原始快照，不合成模糊verified。roles只列摘要，不展开正文。role默认返回目标元数据、必要资源引用和方法可用性；render一次返回common+role+显式project的完整prompt、组成文件摘要、来源范围及`native_payload: false`。project级role必须给匹配project；workspace角色不选project时不加载项目规则。check校验全库，拒绝未知/重复ID、缺引用、非法路径、依赖缺项及超长组装。

## 验证与性能口径

先完成一个共享角色及项目适配的端到端，再扩齐11份定义。测试针对单项输出隔离、精确选择、来源保留、缺项失败、语义硬要求与迁出仓库后的运行；新增工具不执行网络、Lody、环境查询或写入。构建仅增加lookup.py的明确白名单，沿用原收据与ZIP验证。

性能同时比较：现有完整文件、已有内联单项读取、新lookup输出；角色比较完整V2.2快照和单角色组装。记录实际UTF-8输出字节、字符与离线调用数，helper耗时只代表本地工具。对同一已知会话、未知目标、超时、两层角色选择做独立场景走查；无实际业务轨迹时，模型延迟、token和成本改善保持未测。

## 维护

角色变化修改唯一正文及库版本，方法来源变化核对固定上游commit与适用范围；不自动追随上游main。固定V2.2快照不作为运行依赖。实际复制第三方正文须带对应许可；本轮借鉴组织原则、保留来源链接，不整包复制上游。正常运行不要求逐次读取来源全文、全库check或角色索引。
