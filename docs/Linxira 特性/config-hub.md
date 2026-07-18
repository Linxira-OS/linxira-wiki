# Config Hub CLI

`linxira-config` 管理 Linxira 特有的软件配置、镜像选择和工作流。当前交付的是 CLI；GUI 版本仍在设计中。

## 软件源

支持 Arch、npm、pip 和 AUR Git 来源的列出、测速、选择与恢复：

```bash
linxira-config mirror arch list
linxira-config mirror arch speed
linxira-config mirror npm speed
linxira-config mirror npm set npmmirror
linxira-config mirror pip set tuna
linxira-config mirror pip reset
linxira-config mirror aur speed official
```

Arch、npm 和 pip 只接受内置审核项或显式 HTTPS 地址，并在写入前进行网络探测。

AUR 不是签名二进制仓库。CLI 默认只列出可验证的官方端点；自定义地址必须通过 AUR Git 智能 HTTP 探测。配置只重写软件包 Git 克隆流量，RPC 元数据仍使用官方服务：

```bash
linxira-config mirror aur set https://example.invalid/aur
linxira-config mirror aur reset
```

## 工作流

```bash
linxira-config install help
linxira-config install science
linxira-config workflow developer
```

`install` 和 `workflow` 读取 `/usr/share/linxira/catalog/catalog-v2.json` 中同一组经过审核的配置。AUR、Flatpak 和 AppImage 保持默认关闭。

## 系统服务

CLI 还提供 SSH、防火墙、远程桌面、虚拟化、电源和网络诊断入口。涉及系统修改的操作会明确调用 `sudo`，普通的列表和测速操作不要求 root。
