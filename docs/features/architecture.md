# Direct Arch 架构

Linxira OS 直接基于 Arch Linux 构建。系统使用 Arch 官方仓库、`pacman` 和滚动更新模型，不经过 Debian、Ubuntu 或 Linux Mint，也不存在从 `pacman` 转换到 `apt` 的兼容层。

## 组件职责

| 组件 | 职责 | 不负责 |
|------|------|--------|
| Linxira Catalog | 维护版本化、经过审核的软件来源、分类和工作站配置元数据 | 执行命令或软件包事务 |
| Linxira Welcome | 读取 catalog 和安装回执，展示工作站状态，并启动固定白名单中的 Shelly、Calamares 和系统工具 | 执行 shell 字符串、提权或软件包事务 |
| Shelly | 在 Live 和已安装系统中提供默认图形化软件包管理与更新事务 | 定义 Linxira 工作站配置或承担系统安装 |
| Calamares | 从 Live 环境安装 Direct Arch 基础系统，并按 catalog 中允许安装的配置处理用户选择 | 承担安装后的日常软件管理 |
| Config Hub CLI | 管理 Linxira 镜像、经过审核的工作流和系统配置入口 | 维护独立的软件包清单或替代 catalog |

## 数据与事务边界

`/usr/share/linxira/catalog/catalog-v2.json` 是工作站配置的单一元数据来源。Catalog 只保存软件包标识和审核信息，不保存可执行命令。Welcome、Calamares 和 Config Hub 读取同一份数据；Shelly 可承接软件推荐入口和图形化软件包操作。

真正的软件包事务由 Calamares、Shelly 或经过审核的事务后端执行。Welcome 只展示信息和启动固定程序，因此 Live 会话中的“安装 Linxira OS”入口会启动 Calamares，而“打开 Shelly”入口会把软件包与更新操作交给 Shelly。

## 默认来源策略

基础系统来自签名的 Arch 官方仓库。AUR、Flatpak、AppImage 和第三方二进制仓库默认关闭，必须由用户明确选择；启用一种来源不会隐式启用其他来源。
