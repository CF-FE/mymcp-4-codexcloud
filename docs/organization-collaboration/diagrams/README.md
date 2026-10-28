# 组织追溯与审计图

[图源](traceability-and-audit.mmd)是维护输入，[SVG](traceability-and-audit.svg)是生成展示。它将统一入口、执行与登记、独立流程审计放在一张图中，不表示已部署自动派发、同步或巡检服务。

各角色优先从正式看板进入，详情按准确关联展开；尚未切换的项目仍沿原正式入口。看板记录冲突或落后时，定向核原生证据并补写，不能用旧阶段抹掉实际执行，也不能仅凭聊天改正式状态。图中的实线为工作与回执路线，虚线为审计对照来源；均须有本次授权和实际可用通道。

审计不位于所有任务的串行审批路径，不替代专业质量复核或负责人验收。缺访问、未完成分页或来源不全时，只报告已核覆盖与未验；审计者参与过的决定、执行或登记片段须回避。图中的 Dot 是本组织适配，通用岗位使用有效任职记录中的报告对象。

复用[既有渲染器与依赖准备说明](../../lody4dot/diagrams/README.md)，从仓库根执行：

```bash
LODY4DOT_DIAGRAM_BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  node docs/lody4dot/diagrams/render.mjs "$diagram_tools" traceability-and-audit
```

`diagram_tools` 指向已准备的临时 Mermaid / Puppeteer 工具目录，不是插件运行依赖。渲染器仅新增此图的显式白名单和输出目录；保持旧默认三图、浏览器配置及隔离方式。图源变更后重生成 SVG，核可解析、文字完整、箭头与正文一致；图不包含真实人员、会话、凭证、文件路径或业务进度。

2026-10-28 在 macOS 使用既有 Mermaid 11.17.2、Puppeteer Core 24.31.0 和本机 Chrome 生成；SVG XML 解析、尺寸及临时截图目视检查通过。该检查只覆盖文档渲染，不证明组织接入、权限隔离、持续监督或实际任务闭环已经生效。
