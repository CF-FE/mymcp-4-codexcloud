# Codex云环境接入

本页说明已有云配置入口的用法，不声明Dot与Codex云是同一产品，也不注册存储重置事件。Dot的官方扩展及生命周期契约仍须分别核实。

## 环境准备

从完整自包含包的根目录执行，LODY4DOT_PREFIX使用该实例已选定的自有安装目录：

```bash
python3 scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --prepare --json
```

[准备工具](../scripts/bootstrap.py)复用锁定安装与离线inspect，不登录、不登记machine、不启动host。准备入口可使用平台实际提供的install_script；该字段保存步骤，保存本身不执行或发布。仓库模式使用`plugin/lody4dot/scripts/bootstrap.py`，当前云目录示例为`/workspace/.tools/lody4dot`，不要将此路径当作所有宿主的默认目录。

## Agent进入任务

平台实际提供启动指引时，指向包内`skills/lody4dot/SKILL.md`并按目标读取参考，再执行：

```bash
python3 scripts/bootstrap.py --prefix "$LODY4DOT_PREFIX" --repair-missing --json
```

工具先检查；仅在诊断明确为缺少受管runtime时调用安装器，安装器仍检查prefix所有权与输入。版本不符或其他失败不会被当作缺失而覆盖。只有依赖就绪得到证明，账户、目标Agent、任务与worker仍分别验收。启动说明送达与实际读取分别记录，不要求技能全文自动注入。

## 身份与任务恢复

运行时按本任务已有授权使用独立私密状态。LODY_CLI_TOKEN的存在不代表已登录，已有身份用verify-only检查，确需登录再显式调用认证工具。发布物与共享快照不含登录态。

恢复后先按已保存原生引用查询原Lody会话/回合，再核验产物；初始化不恢复业务写操作，不自动重发任务或启worker。若没有正式重建hook，仍可从实际可用的任务入口执行同一准备/检查；不依赖重置前通知保存成果。具体协作规则在包内`skills/lody4dot/references/collaboration.md`。

来源：当前云配置的准备/启动字段与实际脚本；原生Codex能力另见[官方文档索引](https://github.com/openai/codex/blob/c7234c1174b27d9c55199fba0d546dc27d1b0415/docs/skills.md)。本页不证明原生插件已注册或独立新云任务已加载。
