# 离线命令与角色知识

本入口只读取随包资料，不访问账户、不运行Lody、不写文件。已有会话的普通观察不需要先调用本工具；用法已确认时直接沿原引用操作。

## 位置与命令

源码：`python3 plugin/lody4dot/scripts/lookup.py`。自包含包：`python3 scripts/lookup.py`。可以使用脚本绝对路径从任意cwd运行；资料相对脚本定位，不依赖开发机目录。以下用`lookup.py`代表已定位的入口：

```text
lookup.py command 'session observe'
lookup.py command 'session observe' --detail help
lookup.py command 'session observe' --detail audit
lookup.py roles --scope workspace
lookup.py roles --scope project --project fanren-work
lookup.py role workspace_quality
lookup.py role workspace_quality --project fanren-work --render
lookup.py role fanren_owner --project fanren-work --render
lookup.py check
```

命令默认返回一个原始index条目及快照来源；help/audit按需选取。来源版本、日期和验证范围不等于当前CLI已测，实际命令变化时核对该版本帮助。未知命令或重复条目不猜测、不回退到全文。

角色列表只给摘要。`--project`包含通用共享角色和该项目角色，可再用`--scope`缩小；项目级角色必须显式给出匹配项目。单角色默认返回元数据、必读资源引用与可选方法可用性；`--render`一次组装共同合同、职责和显式项目适配，并提供组成文件摘要、字符数及来源。未选择项目时不注入项目规则。

`native_payload: false`表示中立知识，不能直接交给Lody角色创建/更新接口。实际机器/config/Role、模型/权限和用户Save按[配置](configuration.md)与本次工作区规则办理；移出历史机器名称不授权变更已有绑定。源V2.2中的观测与本库定义均不能替代当前部署回读。

外部方法标记`bundled: false`/`availability: not_bundled`，只作为灵感或可选资料；角色自带职责可以独立阅读。任务明确依赖的外部方法不可得时，仅保留该步骤缺口，不自动下载、安装或宣称能力可用。

## 失败与维护

所有结果为JSON；成功退出0，参数或资料错误退出2，不输出半份prompt。未知/重复ID、项目不匹配、缺失依赖、非法路径/符号链接、坏JSON及完整提示词超过32768字符均拒绝；不静默截断。无Python时直接读[index](roles/index.json)定位目标，再读取其中列出的common、角色及显式项目资源。

`check`用于维护/打包时校验全库，不是每次任务的前置。编辑后的版本维护见[角色库](workspace-roles.md#按需读取角色库)。文件字节和helper耗时只能说明本地读取成本；真实模型token、延迟和业务效果另测。
