# 组织协作 skill

组织协议1.0.0的唯一源码为[skill/organization-collaboration](../../skill/organization-collaboration/SKILL.md)。它让各参与端按本次任务确定岗位、责任、汇报通道、派发和验收，包含粒度评估、依赖并行、进度表及岗位／角色更新流程。实现与[已接受的方案及四张图](../lody4dot/project-coordination.md)对应；实际状态统一记录于[任务队列O01–O05](../../.codex/agent-state/todo.md#当前goal独立组织协作skill)。

该skill全部为Markdown，不要求Python、Node、Lody身份、专业角色库或常驻服务。通用协议、当前关系、任务上下文分别维护；真实参与者和组织名单保留在已有私密正式记录中，不写进技能包。

## 读取与任务上下文

先读取`SKILL.md`，按稳定岗位ID只读对应指引：`organization_lead`、`project_owner`、`executor`、`reviewer`。首次接单、换项目和接管时用[上下文模板](../../skill/organization-collaboration/references/context-and-reporting.md)确认责任、报告对象与实际通道；已有有效任务上下文直接复用。纯独立问答不因此建立组织流程。

岗位和专业角色更新走[维护流程](../../skill/organization-collaboration/references/maintenance.md)。协议／岗位、专业角色库、实际任职关系各自版本化；新增岗位修改唯一导航和一份平铺参考，不能自动创建Agent或写远端配置。普通在途任务按明确版本及节点迁移；当前权限撤销、安全修正和公子新指令优先。

## 分发

从仓库根目录构建独立skill，仅打包该技能及自己的收据：

```bash
python3 plugin/lody4dot/scripts/build.py --organization-skill-only \
  --output dist/organization-collaboration-1.0.0 \
  --zip dist/organization-collaboration-1.0.0.zip --json
```

输出根直接包含`SKILL.md`、`references/`和`.organization-collaboration-build.json`，没有插件清单、Lody工具或专业角色库。这是技能文件包，不把它冒充ChatGPT原生插件ZIP。构建工具使用Python标准库，使用skill本身不需要Python；输出目录和ZIP必须是新路径，旧目录和自定义修改不会被覆盖。独立收据的工具名为`organization-collaboration-build`，CRC与SHA只证明本地文件一致性，不能用Lody doctor代替技能加载验收。

组合分发使用既有构建命令：

```bash
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot-0.4.0 \
  --zip dist/lody4dot-0.4.0.zip --json
```

组合包增加`skills/organization-collaboration/`并纳入原收据和provenance；组织协作入口与Lody操作入口分开。只需组织协议的执行端使用独立skill，不因组合包包含Lody而执行setup或安装CLI。

## 安装与实际加载

先明确目标端及其支持的技能目录／安装入口。已有目标若含用户修改，先核版本与变更，不直接覆盖；采用新目录或该宿主已验证的更新方式。组织skill不能替用户自行决定安装到哪台机器、发布到哪个工作区或发送给哪个会话。

| 目标 | 本仓库提供的入口 | 分别要取得的证据 |
| --- | --- | --- |
| 当前本机Codex | 完整skill目录放入本机支持的skills目录；按本次授权检查目标不存在后安装 | 目标文件与源摘要一致；下一任务实际发现/读取另记，不把本轮手动读取称原生触发 |
| 已有Codex Cloud环境 | `.codex/cloud-start.md`及`AGENTS.md`先指向组织skill，再按需读Lody | 代码提交、保存环境ref及发布各自状态；目标新任务读到实际版本和本次关系 |
| 云端Dot | 独立skill或组合插件通过当前获准入口送达；Dot岗位及项目记录作为任务输入 | 实际安装/可读入口、版本、已读上下文、到负责人的可用回报通道 |
| Lody项目执行端及其他参与者 | 沿原生引用交付获授权包或路径，保持本端身份和范围 | 对应执行器文件、读取与任务关联；控制端回执不替代目标端加载 |

没有实际可调用入口、唯一目标或消息授权时，只准备包和交接说明，不自动联系远端、注册机器或猜测安装路径。加载验收不是要求跨端重新登录或重跑既有业务。

## 本轮接入证据

2026-10-26已完成独立skill、组合分发、源码启动指引和三个新上下文离线走查；本机`~/.codex/skills/organization-collaboration`已放置完整文件并核对摘要。新一轮原生发现、云端Dot和各项目端实际加载尚未取得回执。包摘要、测试和分端状态统一见[验证记录](../lody4dot/validation.md#2026-10-26独立组织协作skill-goal)，不以可读文件推定全端安装成功。

## 验证与维护

本能力首版以可读协议和模板为合同，不新增任务JSON schema或程序路由器。结构／打包测试验证自包含、路径保护、收据和迁出仓库可读；新上下文走查检验职责、汇报、变更与UNKNOWN处理；真实安装和业务结果单独记录。

建议使用以下固定场景做离线前向走查，评测者只拿输入及完整skill，不预告判据：

| 场景输入 | 验收重点 |
| --- | --- |
| Dot代项目owner O创建Cloud任务C，执行端E只可回传Dot；专业角色为研究 | E明确向O负责/汇报，经Dot中转；Dot是派发者，不改变业务owner；不自动发消息 |
| 项目owner接到一处文案修正和依赖同一未定接口的A/B实现 | 小任务仍审阅规划分配且可自领；接口明确后A/B满足资源及写入条件才并行；一份正式进度表 |
| 原派发UNKNOWN且owner变更，新负责人要求立刻再开同目标任务 | 交接原引用和责任，先对账，不用接管重派；不把旧写者失联当已停止 |
| 新增组织岗位与更新视觉专业角色；一项在途工作使用旧版本，另有权限撤销 | 两类定义各归其主库；稳定ID/版本/影响范围/分端回执；普通更新不重启在途，撤权立即约束相关动作 |
| Dot的跨项目现状汇总，没有项目归属 | 可用工作区关系，不虚构项目；Dot在有效授权内自派自验；涉及项目资产则转对应owner |

保留实际输入、读取文件、回答、判定和未验证项。单次批量计划走查不是多个独立实验，不证明模型延迟降低或持续正确执行。全部项目检查仍在仓库根运行`python3 scripts/check_repository.py`及`python3 -m unittest discover -s tests -v`。
