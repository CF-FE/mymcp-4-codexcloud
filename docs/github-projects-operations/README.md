# GitHub Projects 操作 skill

通用技能1.0.1的源码在[skill/github-projects-operations](../../skill/github-projects-operations/SKILL.md)。适用于已提供官方GitHub Projects MCP的ChatGPT、Lody或其他兼容宿主，查询与写入使用实际工具；不要求运行Lody CLI，不包含MCP服务器、凭证或新的组织岗位。

- [完整方案](plan.md)：全员按范围读取、按对象收敛写入、skill分层、效率策略与接入步骤。
- [双端合并验证](validation.md)：ChatGPT Work与Lody的20方法覆盖、异常、遗留资源及本地技能验收。
- [组织适配](../organization-collaboration/github-projects.md)：本组织CF-FE默认及实际接入事实；这些值不进入通用skill。

固定提交`5a2186f`的1.0.0已取得[云端接入验收](validation.md#2026-10-27固定提交接入验收)：执行器与Dot实际读取通过，Dot直接完成指定Project与字段定义读取。原生skill自动发现仍未验。1.0.1只澄清字段定义／条目值的区别，以及复用已读取版本和连接证据；旧回执继续覆盖1.0.0，不推广为1.0.1已在所有端加载。

## 内容与使用

技能入口只保留最短操作路径；查询参考、写入／对账参考、迭代参考按需读取。只有生成等长连续周期时才需要可选的Python脚本，普通MCP操作没有本地运行时依赖。脚本只生成JSON计划，不认证、不联网、不写GitHub。

有准确任务引用和有效授权就复用；没有明确写入意图／范围时保持只读。组织场景从现有任务取得决定者、当前写者和验收来源；已安装组织协作skill时复用其规则，独立安装本技能也不会产生断链或自动授予权限。

## 分发与接入

完整交付`skill/github-projects-operations/`，保留`SKILL.md`、`references/`及`scripts/`相对结构。独立ZIP为该目录的完整文件包，不等同于ChatGPT原生插件清单。首次核对内容摘要，目标宿主按自身支持的技能入口读取或安装，实际触发另取回执。

在仓库根可用Python标准库生成一个新ZIP；先确认目标路径不存在，且源码目录不含缓存或临时文件：

```bash
python3 -m zipfile -c /private/tmp/github-projects-operations-1.0.1.zip skill/github-projects-operations
python3 -m zipfile -t /private/tmp/github-projects-operations-1.0.1.zip
```

本轮正式交付文件及逐文件SHA收据的位置见验证记录，生成物不入Git。现有lody4dot组合候选0.6.1和组织协议1.2.1保持各自版本；本技能独立分发，不隐式改变旧组合包、远端Role或在途加载版本。

## 本地检查

从仓库根运行：

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 skill/github-projects-operations/scripts/plan_iterations.py --start 2028-02-26 --days 7 --count 3 --title-prefix Sprint
```

测试检查日历生成及无效输入不输出部分计划；独立上下文走查检查skill决策，二者不等于真实MCP回归。复用已完成的双端测试，不把复跑20方法设为日常使用或安装前置。

更新时修改唯一源码并增加技能版本，重新核引用、受影响场景和分发；已知上游异常只有在对应分支取得新证据后才标记解决。服务端部署未知时，保留取证日期及范围，不从本地skill版本推定MCP版本。
