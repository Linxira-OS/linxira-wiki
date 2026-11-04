# 预装工具

Linxira OS 的基础系统保持紧凑，完整安装不依赖网络。大型科研、AI 和开发环境通过安装器可选配置或首次启动后的 Config Hub 安装。

## 基础桌面

| 类别 | 应用 |
|------|------|
| 桌面 | KDE Plasma、System Settings、Info Center |
| 文件与终端 | Dolphin、Ark、Konsole、Kate |
| 文档与图像 | Okular、Gwenview、Spectacle |
| 浏览器 | Firefox |
| 软件管理 | Shelly |
| 系统监控 | Plasma System Monitor、KScreen、`fwupd` |

## 系统基础

- Arch Linux 官方 `linux` 与 `linux-lts` 双内核
- `pacman` 和签名的 Arch 官方仓库
- NetworkManager、PipeWire、Bluetooth 和电源配置
- Btrfs、Timeshift、grub-btrfs 和基础恢复组件
- Fastfetch 与 `linxira-config`

## 默认不启用

AUR、Flatpak、AppImage、厂商 GPU 计算栈和第三方二进制仓库均不默认启用。Miniforge、Bioconda、CUDA 和大型科学软件也不是基础系统的预装内容。

这类组件必须由用户明确选择，并显示来源和事务范围。可复现科研环境优先使用 Apptainer、Podman 或 Distrobox 等隔离方式。
