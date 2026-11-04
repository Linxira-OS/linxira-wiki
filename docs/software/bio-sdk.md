# Bio SDK（linxira-bio-sdk）

!!! warning "外部产品，文档以仓库与 Wiki 为准"
    Bio SDK 是独立演进的外部产品，本 wiki 只作为入口页，不复制它的使用说明或
    SDK 内容。命令、参数、输出格式与 SDK 接口以仓库自带的 GitHub Wiki 为准；
    这些内容随版本变化，使用前请核对当前版本。

Linxira Bio SDK 是一个本地优先、面向 agent 的生物信息学执行工具包。它把简明的技能
与经过测试的 CLI、SDK 和工具契约结合起来，让常规分析使用已有实现，而不是每次运行
都重新生成脚本。

## 为什么存在

让通用编码 agent 直接跑生信分析，最常见的做法是每次临时写一段脚本：同一份 QC 或
统计逻辑在不同会话里被重写，结果无法复现，也没有版本化的输入输出契约。Bio SDK 把
分析能力做成带版本、有机器可读目录的单元，agent 通过契约调用它们，而不是自由生成
代码；本地执行是默认，只有在测得资源不足时才把工作移出去。

## 职责边界

**归它**：

- `linxira-bio`：面向人员与工作流的命令行界面。
- `skills/`：绑定到带版本能力上的 agent 指令；`capabilities/`：机器可读的能力目录。
- `engine/`：Rust 运行时（未来只引入有基准数据支撑的 C++ 内核）。
- `skill-pack.json`：面向 agent 运行时与 `linxira-skills` 的导入边界。
- `linxira-bio-ui`：不依赖 WebView 的原生 Rust 桌面应用。
- `linxira-bio-mcp`：stdio JSON-RPC MCP 服务器，能力 id 即暴露给 MCP 客户端的
  工具名，工具调用执行的是 worker 作业。
- 版本化的能力契约与结构化结果；发布包从固定的 bundle 清单暂存，始终带双语
  `docs/`、schema、目录、技能与许可证声明。

**不归它**：

- 不取代 `linxira-skills`——后者仍是研究、Linux、HPC、云、浏览器与交付工作流的跨
  学科技能路由与安装器。Bio SDK 只提供可执行的生物信息学能力。
- 不重写成熟的本地工具。salmon、kraken2、BLAST、HMMER、minimap2 这类原生工具保持
  外部，由本工具包编排；Python 与 R 是带独立实现的一等后端，绘图默认用 matplotlib
  与 ggplot2。
- 不捆绑第三方解释器、软件包、数据库或模型；它们是可选的本地后端。
- 浏览器类服务只是连接器，不是计算内核，也不保存或自动填充账号凭据。

## 怎么用

三个用户入口，都基于同一套能力契约：

| 入口 | 形态 | 用途 |
|---|---|---|
| `linxira-bio` | 命令行 | 人员与工作流直接调用；结构化结果表可导出为 CSV、TSV、JSON、JSONL 或 XLSX |
| `linxira-bio-mcp` | stdio JSON-RPC MCP 服务器 | 把 MCP 客户端指向该二进制，能力 id 即工具名 |
| `linxira-bio-ui` | 原生桌面应用 | 能力感知的结果图表，本地 PDB/mmCIF 结构查看与 PNG 导出 |

agent 侧通过 `skill-pack.json` 与 `skills/` 接入，而不是调用 GUI。

具体的子命令、参数、规划模式与数据格式矩阵见仓库文档与 Wiki，本页不复制。环境规划
（`local-core`、`scripting`、`managed-runtimes`、`containers`、`sequence-search`、
`genomics-cli`、`full-local`）是只读的；安装是独立的、需要显式批准的能力，
`environment.apply.v1` 仍处于规划中，不能执行规划预览。

平台：Windows 是主要桌面与入门平台；Debian 与 Arch 是工作站、服务器与 HPC 场景
支持的 Linux 家族；macOS 目前不是经过测试或打包的目标。在 Windows 上，WSL Debian
是较旧组件的兼容提供者，WSL Arch 是当前平台提供者；Linxira WSL 的安装仍待带版本的
rootfs 与升级契约发布。

## 权限

常规分析在当前用户权限下本地运行，不需要 root。需要提权的只有改变系统状态的步骤：
安装运行时或系统缺失的组件是独立的、需显式批准的能力，规划本身只读。把工作移出本地
边界（本地 GPU、机构调度器、获批云算力）需要记录提供方、配给、成本与数据保留等边界
后才执行；浏览器服务要求用户显式动作与人控认证。结构文件保持在本地，解压后上限
128 MiB、100,000 个原子。

## 已知限制

- 每个能力是单步的。多步链靠技能、agent 或手动串联完成；引擎内目前没有 pipeline
  组合（无 DAG 运行器、无步骤间工件生命周期）。
- Python SDK 仍是计划项，仓库说明它在 CLI 契约稳定之后提供。
- `environment.apply.v1` 尚未可用，规划预览不能直接执行。
- mmCIF 目前只是查看器输入，不是可用的分析能力。
- macOS 不是经过测试或打包的目标；Linxira WSL 安装仍是计划。
- 发布包不捆绑第三方解释器、软件包、数据库或模型，带外部依赖的分析需要用户自行
  准备运行时。
- 许可是 AGPL-3.0-or-later：通过网络向用户提供修改版时，需按 AGPL 提供对应源代码。

## 深入设计

仓库与产品说明见
[Linxira-OS/linxira-bio-sdk](https://github.com/Linxira-OS/linxira-bio-sdk)；
权威的使用与 SDK 文档是该仓库的
[GitHub Wiki](https://github.com/Linxira-OS/linxira-bio-sdk/wiki)；架构、运行时
管理、数据格式与执行策略等设计文档在仓库的
[docs/](https://github.com/Linxira-OS/linxira-bio-sdk/tree/main/docs) 目录。
