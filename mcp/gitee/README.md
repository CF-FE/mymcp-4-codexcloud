# Gitee MCP 网关

G8 Gitee 网关提供仓库、文件、分支、提交、PR、issues 和 hooks 等 MCP 工具，通过 GitHub OAuth 验证访问身份。源码及原部署资料保存在 [完整部署](完整部署/00_归档索引.md) 中，保留原目录布局。

此条目属于 `mcp/`：上传内容未包含 `SKILL.md` 或 Codex plugin 清单。

## 来源与完整性

- 来源：[打包发给我](chatgpt-conversation://6ad70f50-09e8-83ec-8255-b1717762139a) 会话提供的 `gitee_20261020.zip`，2026-10-20 导入。
- 原压缩包共 19 个文件；其中 18 个文件按原路径和字节内容导入，外层 `gitee/` 对应本目录。
- `gitee/.token` 是凭证文件，未提取、未提交；原上传压缩包未修改。
- [import-manifest.json](import-manifest.json) 记录压缩包和导入文件的大小、SHA-256、原路径和权限。这是仓库的导入记录，不是 Codex 安装配置。
- `04_交付包/` 中三个 ZIP 是随附的历史交付快照，按原字节保留，不作为额外源码维护。其中升级包的部署指南为较旧版本，当前说明以展开目录为准。

## 文件入口

| 目录或文档 | 内容 |
| --- | --- |
| [01_代码与脚本](完整部署/01_代码与脚本/) | 网关、仓库工具、认证策略、启停脚本和配置示例 |
| [部署指南](完整部署/02_部署文档/部署指南.md) | 原服务器的完整部署步骤 |
| [服务启停说明](完整部署/02_部署文档/服务启停说明.md) | 后台进程、日志和停止方式 |
| [03_诊断与验收](完整部署/03_诊断与验收/) | 扩展网关测试、诊断程序及旧项目迁移清单工具 |
| [04_交付包](完整部署/04_交付包/) | 完整包、升级包、启停脚本包 |
| [05_历史资料](完整部署/05_历史资料/) | 历史配置示例与旧版测试 |

## 运行前提

原资料记录的运行环境为 Python 3.14.4、FastMCP/fastmcp-slim 4.0.11、MCP 2.3.0。源码会检查这三个 Python 包的准确版本，还引用 `httpx2`、`mcp_types`、`jsonschema` 等模块。原包未提供独立依赖锁文件，本次没有新增或猜测依赖版本。

原启动流程面向 Linux，依赖 Bash、GNU coreutils、util-linux 和已配置的 ngrok。网关使用 HTTP 传输，监听 `127.0.0.1:8765`，MCP 路径为 `/mcp`。

服务固定读取 `/opt/gitee-mcp-gateway/gateway/.env`，要求它是权限为 `600` 的普通文件。所需配置名称：

| 配置 | 用途 |
| --- | --- |
| `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET` | GitHub OAuth App |
| `GITEE_ACCESS_TOKEN` | 上游 Gitee 访问凭证 |
| `GITEE_MODE` | `READ` 或 `WRITE` 模式 |

外部目的地包括 GitHub OAuth/API、Gitee MCP/API 及原部署的 ngrok 域名；准确地址以源码和原部署指南为准。原代码还固定了允许的 GitHub 身份、域名和默认路径，因此归档成功并不代表它可直接在任意 Codex 云环境中启动。

## 原部署与测试方式

分类目录用于保存源资料。原部署指南要求将代码与诊断文件平铺到 `/opt/gitee-mcp-gateway/gateway/`，而非直接从当前分类目录执行测试：`test_gateway_tools.py` 会在自身同目录查找网关源码。

在原部署前提均满足后，从该部署目录执行：

```bash
/opt/gitee-mcp-gateway/.venv/bin/python test_gateway_tools.py
bash start.sh
# 停止由该脚本管理的服务
bash stop.sh
```

代表性就绪检查为未认证的 `/mcp` 请求返回 `401`，随后还需经过 OAuth 连接、列工具和只读请求验证；`401` 本身不能证明完整功能可用。具体步骤见原部署指南。本次没有执行上述部署、服务启动或外部请求。

`migration_manifest.py` 针对另一个项目的原八文件快照；它不是本次导入的验收工具。原文中的历史测试结果也不作为当前环境的测试结果。

## 本次验证范围

导入时检查 ZIP CRC、18 个文件的逐字节内容与 SHA-256、Python 源码解析、Shell 语法、仓库结构及仓库检查工具的测试。FastMCP、`httpx2` 和 `mcp_types` 当前未安装，原网关的离线功能测试、真实 OAuth/Gitee 连接及隧道启动尚未运行。

原始文件的结尾空行一并保留，因此导入差异的 `git diff --check` 有 4 处原有格式提示；新增说明和清单单独通过空白检查。

返回 [MCP 目录](../README.md) 或 [仓库首页](../../README.md)。
