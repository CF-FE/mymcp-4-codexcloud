# lody4dot 实现与验证记录

日期：2026-10-20。任务状态权威为 [队列](../.codex/agent-state/todo.md)，接口依据为 [开发契约](lody4dot-development.md)。以下记录当前机器及离线行为，不代替真实账户或宿主加载验收。

## 环境与固定输入（T02）

- Linux，Node `v24.19.0`，npm `11.9.0`，Python `3.12.14`，Codex CLI `0.163.0`。
- Lody 固定为 `0.107.2`，使用提交的 [manifest](../plugin/lody4dot/runtime/package.json)、[锁文件](../plugin/lody4dot/runtime/package-lock.json) 和 [构建策略](../plugin/lody4dot/runtime/build-policy.json)。
- 锁文件 SHA-256：`b1baf3ab20593c88f40e4ab7077b737296480d6ca3a0428b7d55499eee9bcced`，40 个锁项。
- 全部安装脚本禁用，锁中无 `hasInstallScript` 项。必要 native 模块无需另行运行构建脚本。
- 原始 CLI 无凭证采集的 70 页公开帮助均退出 0；排除内部命令。发布包的 Lody 版本未更改。

原始依赖 Tinypool `1.1.1` 在当时 audit 中涉及两项 critical 公告：[GHSA-5gmw-xhrv-c9v3](https://github.com/advisories/GHSA-5gmw-xhrv-c9v3)、[GHSA-85c8-ppgw-ccpr](https://github.com/advisories/GHSA-85c8-ppgw-ccpr)。公告描述的利用还需要特定输入/原型污染条件，不能据此宣称 Lody 已被利用。

采用限定在 Lody 下的 `tinypool: 2.1.2` override。没有执行强制 audit 修复或降级 Lody。该覆盖跨越原依赖 major 范围，因此做了原始 worker 对照，而非只相信安装成功：

- Tinypool 1.1.1 与 2.1.2 分别加载未修改的 Lody diff 和 file-index-scan worker。
- 并发 diff、Unicode、文件匹配/不匹配、递归/浅扫描、完整索引、异常传播与池恢复的规范化结果一致。
- 最终冻结安装再执行 [可复现 worker 检查](../tests/lody4dot/verify_workers.mjs)，7 组检查通过；使用空环境加 PATH，无账户凭证。
- 对最终冻结安装运行 `npm audit --omit=dev --json`，退出 0，各等级及 total 均为 0。这仅代表当时 registry 已知公告结果。

实测限于 Node 24.19/Linux；Node 22、Bun 和其他系统未实跑。官方 engines 范围与实际验证范围分别说明。

## 知识检查（T03）

[技能入口](../skill/lody4dot/SKILL.md) 配有 8 个主题参考、命令索引、来源记录和帮助快照。20 类、70 个公开路径逐条匹配；帮助 SHA-256、版本、命令树和索引字段一致。

25 个 fenced CLI 示例已对实际命令/参数检查；版本冲突保留在来源记录中，例如 `session create --env` 已 deprecated。帮助证据没有被标为业务功能实测。

## 安装器验证（T04）

真实执行以下入口：

```bash
python3 plugin/lody4dot/scripts/install.py --prefix /workspace/.tools/lody4dot --json
/workspace/.tools/lody4dot/bin/lody --version
```

首装 `reused=false`、同锁再装 `reused=true`，均退出 0。稳定入口输出 `0.107.2`；帮助和以下检查通过：SQLite 内存查询/关闭，PTY、keyring、loro 加载，以及 roost 的 ESM import。模块加载不能证明真实 keyring 存取或账户可用。

14 项安装器 fixture 测试覆盖未知目录/入口拒绝、Node 范围、冻结输入、同锁复用、隔离验证状态、代理/CA 继承，以及 npm/native/版本/切换失败时旧入口和用户状态保留。生产安装没有登录、注册机器或启动 daemon。

## 诊断与认证验证（T05、T06）

真实 `doctor.py --profile inspect --json` 退出 0：Node 和 CLI 通过，凭证观察为 missing，账户、运行进程、任务执行为 not_run。`task` 不会因 CLI 可用就通过。

12 项 fixture 测试验证默认不查账户、control 显式连接要求、task/worker 未验证状态、空/坏 JSON、权限和网络错误、超时终止、不回显假凭证、verify-only 不登录、私密状态要求和外部指针拒绝。

认证仅在显式 `--login` 时将 `LODY_CLI_TOKEN` 传给已核实的 `login --auth` 入口；原生 CLI 仅提供 argv 通道，因此同权限本机进程的参数可见性仍存在。适配器不用 shell、历史、debug 或原生输出转发掩盖这一边界。实际 Lody 授权尚未执行。

## 分发与云配置（T07、T08）

自包含产物共 22 个受哈希管理文件，另有构建 receipt，包含原生清单、marketplace、技能、工具和 runtime 锁定输入。没有依赖安装目录或登录态。

本次 `dist/lody4dot-0.1.0.zip` 共 23 文件、63,549 字节，解压完整性检查通过；SHA-256 为 `ac047a8836c8900103ca6541e605bab28ba424aae13845315c80ce91f130c738`。构建 receipt 的 SHA-256 为 `356547f1918cc72e1ca1990dd8058284ee67b600b7f267a45dfd823181e1bab0`。生成物留在被忽略的 dist，不作为第二份源码提交。

将整个产物复制到 checkout 外 `/workspace/.cache/lody4dot/relocated-package`，从该位置安装到全新 `relocated-install`：真实首装和 inspect 均退出 0。证明脚本/资源不依赖原 checkout 路径；未证明宿主加载。

10 项构建 fixture 验证移位资源与精确哈希、必需 common、缺资源、包外引用、敏感/额外文件、符号链接、未知输出保护及切换失败恢复。独立代码审查发现的 common 必需依赖漏检已修复，并增加回归测试。

标准命令现递归覆盖 39 项 lody4dot 测试及 8 项原仓库测试，共 **47 项通过**；结构检查为 `mcp=1 skill=1 plugin=1`。独立 worker 检查不计入这 47 项。

完整执行 `.codex/cloud-install.sh` 退出 0，实际完成这些测试、同锁安装复用和离线 inspect，未做认证或启动服务。

云配置草稿已由后端确认 `status=saved`、`requires_publish=true`：

- 安装脚本：[cloud-install.sh](../.codex/cloud-install.sh)，只装依赖及运行离线检查。
- 启动指引：[cloud-start.md](../.codex/cloud-start.md)，按需读取技能，在任务内使用私密状态。
- 保留 package_managers preset 与 `lody.ai`，新增 `convex.lody.ai`、`backend.lody.ai`、`api.lody.ai`。
- 只声明直接进程变量 `LODY_CLI_TOKEN` 的名称，没有提供值或另造代理 secret。

配置保存不执行安装、不发布环境、不证明新任务加载。原生注册命令已依据同版本官方源码核实；当前没有修改受保护的宿主配置或声称注册完成。

## 离线 agent 演练（T10 的独立准备）

另一个无前序会话上下文的 agent 只收到目标“查所有机器，并判断能否用已有 Role 发起任务”。它自行读取技能和必要参考，检查版本、inspect/task、verify-only 及准确帮助；识别缺身份/state，没有猜工作区、登录、启动 host 或创建会话。它正确区分分页、unknown 在线状态、Role 覆盖和持久化结果核验。

该结果证明这次演练的流程选择；agent 是显式获知技能路径，并非由新云任务自动发现。它没有真实账户/任务结果，不能让 T09 或 T10 的真实闭环通过。

## 外部条件与下一验证（T09–T12）

用户截图已经确认该环境添加了 `LODY_CLI_TOKEN` 变量名称。随后的只读复查仍显示：当前进程 missing，运行环境变量元数据为空；保存草稿中该变量为 `pending_runtime_requirements`，直接变量交付。不能由此否定用户已配置，也不能仅从截图推断已注入当前任务。

当前生效网络仅有 `lody.ai` 加包管理 preset。对三个服务域名进行无凭证 HTTPS 探测均为 curl 56、CONNECT 403，确为代理策略阻断；没有尝试绕过代理或关闭 TLS。

下一步是应用已保存草稿，再复查真实生效规则及当前任务变量存在性。只有变量实际注入后才做显式授权和只读工作区发现；工作区、测试机器/Role及底层 Agent 凭证须由实际结果确定。发布或源码配置版本号本身均不能代替这些检查。宿主新任务读取回执、私密状态/快照边界、真实查询/观察和受控任务仍未通过；整体目标保持未完成。

## 复现命令

在仓库根目录运行：

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 plugin/lody4dot/scripts/install.py --json
python3 plugin/lody4dot/scripts/doctor.py --profile inspect --json
env -i PATH="$PATH" node tests/lody4dot/verify_workers.mjs /workspace/.tools/lody4dot/current
python3 plugin/lody4dot/scripts/build.py --output dist/lody4dot --json
```

真实连接与执行结果只能在前提满足后追加，不能用上述离线通过替代。
