# 指引图表维护

环境三图服务于[环境、Dot、会话引用与权限指引](../environment-model.md)；协作三图服务于[云端Dot与项目负责人协作方案](../project-coordination.md)。环境图不声明物理部署或一对一绑定，协作图是2026-10-26评审候选，不表示已实现自动路由或派发。连线不扩大授权。

| 图源 | 生成图 | 主要问题 |
| --- | --- | --- |
| [environment-context.mmd](environment-context.mmd) | [SVG](environment-context.svg) | Dot、其执行去向和Lody接入怎样分层 |
| [environment-lifecycle.mmd](environment-lifecycle.mmd) | [SVG](environment-lifecycle.svg) | 配置应用与技能读取怎样分别取证 |
| [environment-permissions.mmd](environment-permissions.mmd) | [SVG](environment-permissions.svg) | 共享插件连接后还须核对哪些执行与访问条件 |
| [project-governance.mmd](project-governance.mmd) | [SVG](project-governance.svg) | 云端Dot、项目负责人、执行者和QA怎样分工；Dot如何直接委派Cloud |
| [project-task-flow.mmd](project-task-flow.mmd) | [SVG](project-task-flow.svg) | 全部需求怎样经审阅、规划、分配与验收，小任务怎样保持轻量 |
| [project-parallel-gates.mmd](project-parallel-gates.mmd) | [SVG](project-parallel-gates.svg) | 依赖、版本和资源满足后怎样开启并行并统一集成 |

2026-10-21实际渲染运行库为Mermaid11.17.2，配合系统Chromium154.0.8037.57及Puppeteer Core24.31.0；工具装在自有临时目录，依赖未加入插件或仓库运行环境。配置见[mermaid-config.json](mermaid-config.json)。CLI的file页面加载受浏览器策略限制，本次使用本地HTTP页面调用Mermaid API生成SVG；未修改浏览器管理策略。

Dot关系和权限修订依据本日实际读取的OpenAI官方[Dot入门](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)、[工作区管理](https://help.openai.com/en/articles/20001554-manage-dots-in-chatgpt-workspaces)和[隐私/权限FAQ](https://help.openai.com/en/articles/20001529-dots-privacy-security-and-safety-faqs)。Dot是持续运行Agent产品；它自己的云电脑、它创建的Codex云任务和经授权连接的本地任务分别识别。共享插件连接不证明浏览器会话、CLI私密状态、模型身份或任意本地文件已跨端可用。第三张生命周期图保留配置应用、知识读取与业务验证的分项取证；官网主动Reset不在图中解释成磁盘回收或重置hook。

支持Mermaid CLI正常加载页面的环境可按下列方式重新生成，源文件与配置是维护输入：

```bash
mmdc -i docs/lody4dot/diagrams/environment-context.mmd -o docs/lody4dot/diagrams/environment-context.svg -c docs/lody4dot/diagrams/mermaid-config.json -b white
mmdc -i docs/lody4dot/diagrams/environment-lifecycle.mmd -o docs/lody4dot/diagrams/environment-lifecycle.svg -c docs/lody4dot/diagrams/mermaid-config.json -b white
mmdc -i docs/lody4dot/diagrams/environment-permissions.mmd -o docs/lody4dot/diagrams/environment-permissions.svg -c docs/lody4dot/diagrams/mermaid-config.json -b white
```

CLI示例适用于其受支持的运行环境，不代表本云机的file页面路径已通过。本实例可用[本地HTTP导出脚本](render.mjs)重现同一路线：

```bash
diagram_tools="$(mktemp -d /tmp/lody4dot-diagrams.XXXXXX)"
printf '{"private":true}\n' > "$diagram_tools/package.json"
env -u LODY_CLI_TOKEN -u GITEE_ACCESS_TOKEN npm install \
  --prefix "$diagram_tools" --cache "$diagram_tools/cache" \
  --ignore-scripts --no-audit --no-fund \
  mermaid@11.17.2 puppeteer-core@24.31.0
env -u LODY_CLI_TOKEN -u GITEE_ACCESS_TOKEN node docs/lody4dot/diagrams/render.mjs \
  "$diagram_tools" environment-context environment-permissions
```

末两个图名可省略以重绘原环境三图。协作图显式指定下列三个名称；2026-10-26在macOS使用同版Mermaid/Puppeteer及本机Chrome生成，不下载浏览器、不改变用户浏览器profile或插件依赖：

```bash
LODY4DOT_DIAGRAM_BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  node docs/lody4dot/diagrams/render.mjs "$diagram_tools" \
  project-governance project-task-flow project-parallel-gates
```

`LODY4DOT_DIAGRAM_BROWSER`可选择已有浏览器可执行文件，默认仍为`/usr/bin/chromium`；macOS保持浏览器默认sandbox，原Linux临时容器参数保留。脚本从临时工具目录读取依赖，只向`127.0.0.1`提供Mermaid静态资源，并拒绝页面对其他origin的请求。它使用新建临时profile、保留继承的代理与CA、移除上述业务凭证环境，结束后清理浏览器profile；不读取用户浏览器登录态。

本容器未提供可用的Chromium SUID/namespace sandbox，因此此导出进程采用下列临时启动配置，**仅处理本仓库可信的本地图源**。该配置不改变托管执行器、网络策略或持久浏览器管理设置，也不适用于浏览不可信网页：

```javascript
{
  executablePath: "/usr/bin/chromium",
  headless: true,
  userDataDir: temporaryProfile,
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
  env: inheritedEnvironmentWithoutTaskCredentials
}
```

维护时检查：

- 图源可解析，生成图包含中文标题/说明和清晰箭头；accTitle/accDescr及正文替代说明保持一致。
- 实线与虚线含义按各图图注明确解释，不依赖颜色；未知关系不能画成已验证调用。总览的实线为已核实关系/能力、虚线为各端待验的Lody接入，不指定当前实例属于哪类电脑。
- 区分Agent决策、工具操作和模型服务位置；Lody workspace表示业务范围。
- 配置版本与安装快照分别识别；自主检索可引向实际读取，平台指引送达不是读取的唯一前提。
- 引用用于定位，访问按授权范围及服务端检查核实；允许必要的只读请求确认未知权限，不预先要求证明全部ACL。
- 共享插件连接是适用请求的可复用来源，不是所有CLI请求必须经过的先决步骤；本地电脑访问和浏览器会话不因连接共享自动迁移。
- SVG的viewBox、显式尺寸和文本完整；查看是否截字、遮挡或过长，并与正文表格交叉核对。
- 协作图同时保留Dot为项目代建Cloud与Dot自身任务直派两条路线，项目结果经Dot回传负责人验收；图与正文的输入版本、独立QA和UNKNOWN边界一致。维护图源后重绘SVG，不手改生成图或写入真实运行进度。
- 本图无需外部服务、真实业务数据或凭证。公开文件不含实际任务、会话、运行实例标识或私密资料。
