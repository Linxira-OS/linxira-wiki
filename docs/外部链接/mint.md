# Linux Mint 文档

!!! warning "历史迁移背景"
    此页面保留用于追溯 Linxira 早期 Linux Mint 路线，不描述当前系统，也不在当前导航中。Linxira OS 现已直接基于 Arch Linux 构建，不使用 Mint 作为底层发行版。

## 推荐资源

- [Linux Mint 用户指南](https://linuxmint-user-guide.readthedocs.io/)
- [Linux Mint 官方博客](https://blog.linuxmint.com/)
- [Linux Mint Forums](https://forums.linuxmint.com/)

## 历史参考工具

| 工具 | 说明 | 文档 |
|------|------|------|
| mintinstall | 软件管理器 | [GitHub](https://github.com/linuxmint/mintinstall) |
| mintupdate | 更新管理器 | [GitHub](https://github.com/linuxmint/mintupdate) |
| mintsources | 软件源配置 | [GitHub](https://github.com/linuxmint/mintsources) |
| timeshift | 系统快照 | [GitHub](https://github.com/linuxmint/timeshift) |

## 当前架构差异

当前 Linxira OS 与这条历史路线的主要差异：

- 直接使用 Arch Linux 官方仓库、`pacman` 和滚动更新模型
- 默认桌面环境为 KDE Plasma
- 使用 Shelly 管理图形化软件包与更新
- 使用 Linxira Welcome、Calamares 和 Config Hub 承担各自的产品职责
