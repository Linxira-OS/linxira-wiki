# Zeta（linxira-zeta）

!!! warning "外部产品，文档以仓库为准"
    Zeta 是独立演进的外部产品，本 wiki 只作为入口页，不复制它的命令手册。
    安装、CLI 参考与配置以随产品发布的运行时文档为准；这些文档随版本变化，
    使用前请核对仓库当前内容。

Zeta 是构建在 OMP 运行时之上的 Bun 原生编码 agent 发行版。它保持终端工作流快速
直接，同时掌控自己的包命名空间、产品呈现、发布策略，以及自己的本地 Web 工作区：
一个运行时，三种形态（终端、浏览器、桌面）。

## 为什么存在

编码 agent 通常只有一种入口：要么是终端里的 CLI，要么是网页或桌面应用。想做同一
件事的三种界面往往各自维护一套会话与设置，于是历史记录、模型配置和工作区状态在
三个地方各说各话。Zeta 把终端、本地 Web 工作台与桌面外壳放在同一会话树、同一设置
模型和同一网关 API（`/api/*`）之上，让用户按场合换界面而不换状态。

## 职责边界

**归它**：

- 终端编码工作区：文件读取、搜索、补丁、shell、git、任务委派与结构化工具输出。
- 内置终端编辑器（TTT Editor，以 `@linxiraos/editor` 形式维护），可在任意终端
  启动，包括通过 SSH。
- 多提供商模型访问、本地配置、OAuth 流程、模型发现、会话恢复与可控重试。
- 本地 Web 工作台（`zeta serve`）与桌面外壳（`zeta-desktop`，Electron），二者嵌入
  同一个编码 agent 运行时。
- 产品身份：`@linxiraos/*` 包命名空间、配置目录 `~/.zeta`、品牌与发布链。

**不归它**：

- 不是 Linxira OS 的系统组件。它不在 `linxira-os` 的仓库治理清单与软件所有权表中，
  系统安装、更新、驱动与桌面集成由各自的 Linxira OS 仓库负责。
- 不定义上游运行时本身。OMP 是它集成的运行时树，Pi / Pi Web 只是功能工作的语义
  移植来源，不是原始合并来源。
- 内部开发与产品流程文档（`document/`）不面向用户，也不随产品发布。

## 怎么用

三种形态的入口都在同一个发布产物中；终端编辑器是另装的独立包：

| 入口 | 名称 | 说明 |
|---|---|---|
| 终端 | `zeta` | 在当前项目目录打开；`zeta --help` 查看命令与选项 |
| 终端编辑器 | `zeta-editor` | 独立包 `@linxiraos/editor`，可在任意终端启动，包括 SSH |
| Web 工作台 | `zeta serve` | 本地 Next.js 应用，经 `/api/*` 网关驱动同一运行时 |
| 桌面外壳 | `zeta-desktop` | Electron 托盘应用，内嵌 Web UI 构建与编译后的运行时；目标机器无需 Bun 或 Node |

已发布的 CLI 通过 npm 包 `@linxiraos/zeta` 安装（`npm i -g @linxiraos/zeta`，或
`bun add -g @linxiraos/zeta`），机器上需有 Node 20+ 或 Bun。具体的安装步骤、完整
命令参考与配置项见下方运行时文档，本页不复制。

界面语言随安装选择：CLI 提供简体中文与英文两套完整目录，依次按
`~/.zeta/settings.json` 中的 `language`、`ZETA_LANG` / `LC_ALL` / `LC_MESSAGES` /
`LANG` 环境变量、操作系统 UI 语言解析，都不匹配时用英文；`/language` 可实时切换，
无需重启。

平台支持（按仓库当前发布矩阵）：

| 形态 | Windows | macOS | Linux |
|---|---|---|---|
| `zeta` CLI | x64 | x64、arm64 | x64、arm64 |
| `zeta-editor` | x64 | — | x64 |
| `zeta serve` | x64 | x64、arm64 | x64、arm64 |
| `zeta-desktop` | x64 | x64、arm64 | x64 |

## 权限

Zeta 以当前用户身份运行，配置、会话与命令定义写在用户目录下的 `~/.zeta/`；通过
npm 或 Bun 的用户级全局安装即可使用，不需要系统 root，也不接管系统包管理。发行版
层面的系统级安装由下游打包方决定（例如 Linux 下游仓库可固定并校验 `zeta-desktop`
发布资产），那属于打包方自己的权限边界，不是 Zeta 的行为。

## 已知限制

- `zeta-editor` 目前只发布 Windows x64 与 Linux x64 平台包，没有 macOS 构建。
- 桌面外壳提供 Windows x64、macOS x64/arm64 与 Linux x64；Linux arm64 未在发布
  矩阵中。
- 从源码构建时，Windows 需要 Visual Studio Build Tools 的「使用 C++ 的桌面开发」
  工作负载，macOS 与 Linux 需要 Rust 所需的平台 C/C++ 工具链；已发布二进制已捆绑
  预构建原生模块。
- 仓库同时维护 `docs/` 与 `document/` 两棵文档树：只有 `docs/` 随产品发布（运行时
  通过 `zeta://docs/` 读取，源码检出时读取实时目录），`document/` 是内部开发文档。

## 深入设计

权威运行时文档随产品发布在
[linxira-zeta/docs](https://github.com/Linxira-OS/linxira-zeta/tree/main/docs)：
工具、工具调用转换、技能、协议、配置与 Zeta 功能都在那里，安装、CLI 参考与配置
也以该目录为准。产品概览与平台矩阵见
[README](https://github.com/Linxira-OS/linxira-zeta)：仓库
[Linxira-OS/linxira-zeta](https://github.com/Linxira-OS/linxira-zeta)。
