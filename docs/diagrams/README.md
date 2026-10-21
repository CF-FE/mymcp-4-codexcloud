# 指引图表维护

这三张图服务于[环境、Dot、会话引用与权限指引](../lody4dot-environment-model.md)。它们是概念图，不声明物理部署、一对一绑定或权限继承。

| 图源 | 生成图 | 主要问题 |
| --- | --- | --- |
| [environment-context.mmd](environment-context.mmd) | [SVG](environment-context.svg) | 谁在交互、工具在哪里执行、哪些接入有前提 |
| [environment-lifecycle.mmd](environment-lifecycle.mmd) | [SVG](environment-lifecycle.svg) | 保存、发布、应用、送达、读取与结果如何分别取证 |
| [environment-permissions.mmd](environment-permissions.mmd) | [SVG](environment-permissions.svg) | 哪些权限条件共同限制一个操作 |

2026-10-21实际渲染运行库为Mermaid11.17.2，配合系统Chromium；临时工具集包含Mermaid CLI11.12.0，依赖未加入插件或仓库运行环境。配置见[mermaid-config.json](mermaid-config.json)。CLI的file页面加载受当前浏览器策略限制，本次使用本地HTTP页面调用同一Mermaid运行库生成SVG；未修改浏览器管理策略。

支持Mermaid CLI正常加载页面的环境可按下列方式重新生成，源文件与配置是维护输入：

```bash
mmdc -i docs/diagrams/environment-context.mmd -o docs/diagrams/environment-context.svg -c docs/diagrams/mermaid-config.json -b white
mmdc -i docs/diagrams/environment-lifecycle.mmd -o docs/diagrams/environment-lifecycle.svg -c docs/diagrams/mermaid-config.json -b white
mmdc -i docs/diagrams/environment-permissions.mmd -o docs/diagrams/environment-permissions.svg -c docs/diagrams/mermaid-config.json -b white
```

CLI示例适用于其受支持的运行环境，不代表本云机的file页面路径已通过。仅支持本地HTTP渲染时，通过Mermaid API的initialize/render使用同一配置和图源，不关闭网络、证书或浏览器管理检查。

维护时检查：

- 图源可解析，生成图包含中文标题/说明和清晰箭头；accTitle/accDescr及正文替代说明保持一致。
- 实线与虚线含义有文字解释，不依赖颜色；未知关系不能画成已验证调用。
- 不把自主检索读取变成必须先收到平台指引，不把链接变成访问凭证。
- SVG的viewBox、显式尺寸和文本完整；查看是否截字、遮挡或过长，并与正文表格交叉核对。
- 本图无需外部服务、真实业务数据或凭证。公开文件不含实际任务、会话、运行实例标识或私密资料。
