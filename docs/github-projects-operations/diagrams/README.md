# 方案图源与生成图

两张图用于[仓库首页](../../../README.md)和[完整方案](../plan.md)。修改Mermaid唯一图源后重新生成SVG，禁止单独改生成图；图的角色和判断不表示所有端已安装或服务端已实现权限隔离。

| 图源 | 生成图 | 内容 |
| --- | --- | --- |
| [access-and-recording.mmd](access-and-recording.mmd) | [SVG](access-and-recording.svg) | 全员按范围读取、业务决定与当前写者分工 |
| [operation-flow.mmd](operation-flow.mmd) | [SVG](operation-flow.svg) | 查询与授权写入、回读及UNKNOWN对账 |

图中所有参与者包含负责人、执行者、审查者及记录写者。查询可直达；事实依预授权登记，质量报告交业务负责人，正式决定由当前写者登记并回读。共享结构由获授权维护者处理。记录职责可兼任，节点不等于必须新建会话、机器或岗位。

维护时核对：同一对象单写；全员读取范围不扩大源权限；项目业务验收不转移给Dot或记录者；图不表示服务器已经实现按AI岗位隔离。

复用仓库已有的[渲染工具与临时依赖准备说明](../../lody4dot/diagrams/README.md)。从仓库根执行，`<临时工具目录>`替换为已准备的Mermaid／Puppeteer目录，浏览器使用本机已安装路径：

```bash
LODY4DOT_DIAGRAM_BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  node docs/lody4dot/diagrams/render.mjs <临时工具目录> access-and-recording operation-flow
```

解析、生成后检查中文换行、连线方向和截图；该工具只使用隔离临时浏览器profile与本地静态资源。渲染依赖不进入技能包或仓库，普通skill使用无需Node或浏览器。
