# Linxira OS Wiki

Linxira OS 是直接基于 Arch Linux 构建的 KDE Plasma 个人科学工作站发行版，面向桌面超算、科学计算、AI、工程、生物信息和容器开发。

[English edition](en/index.md) · [软件索引](项目总览/index.md)

## 本站与另外两个站的分工

三个站点的定位不同，别混着看：

| 站点 | 面向 | 内容量级 |
|---|---|---|
| [文档站](https://linxira-os.github.io/zh/docs/) | 刚装完系统的人 | 短、任务导向：安装、快速开始、常见问题 |
| **本站（Wiki）** | 长期使用者与贡献者 | 长、参考导向：项目总览、架构、职责边界、权限模型 |
| [博客](https://linxira-os.github.io/zh/blog/) | 关注我们在做什么的人 | 叙述性：发布记、实测报告、设计取舍 |

需要「怎么装、怎么跑起来」→ 文档站；需要「为什么这样设计、哪个组件负责什么」→ 本站；需要「最近发生了什么」→ 博客。

## 文档范围

本文档只记录 Linxira OS 独有的安装器、Welcome、Shelly、Config Hub、软件目录、工作流和品牌行为。通用 Arch Linux、KDE、systemd、pacman 与硬件配置应优先参考 [Arch Wiki](外部链接/arch-wiki.md)。

本 wiki 讨论**每个项目的大体设计流程**：为什么存在、职责边界、何时用哪个、权限模型。完整清单见 [项目总览](项目总览/index.md)。具体项目的内部设计、数据结构与实现决策不在本 wiki，在各项目自己仓库的 `document/` 目录。

## Linxira 功能

- [Direct Arch 架构](Linxira%20特性/architecture.md)：Welcome、软件目录、Shelly、Calamares 和 Config Hub 的职责边界
- [Config Hub CLI](Linxira%20特性/config-hub.md)：Arch、npm、pip、AUR 来源管理和系统配置
- [预装工具](Linxira%20特性/preinstalled-tools.md)：离线基础桌面与默认关闭的第三方来源
- [工作流配置](Linxira%20特性/workflows.md)：科学、AI、开发、容器和生物信息配置
- [品牌系统](Linxira%20特性/branding.md)：Logo、壁纸和视觉资产

## 使用边界

Linxira OS 适合个人工作站和桌面计算节点。由于采用滚动更新，它不推荐用于大规模企业服务器部署。需要固定依赖、可重复构建或服务器式开发环境时，应使用版本固定的容器或其他隔离环境。

Linxira OS 是独立项目，与 Arch Linux 无隶属关系，也未获得 Arch Linux 官方认可。

---

!!! warning "本站建设中"
    这份 Wiki 尚未写完：项目总览与架构部分可用，运维手册、故障处置、权限模型等章节仍在补齐。
    需要「怎么装、怎么跑起来」请看[文档站](https://linxira-os.github.io/zh/docs/)。
