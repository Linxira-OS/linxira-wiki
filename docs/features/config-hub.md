# Config Hub CLI

`linxira-config` 管理 Linxira 特有的软件配置、镜像选择、软件栈与环境变量。当前交付的是 CLI；GUI 版本仍在设计中。

## 软件源

支持 Arch、npm、pip、AUR、Flatpak 与 Go 六类来源的列出、测速、选择与恢复，
另有 Miniforge 的 conda 频道管理（仅 conda-forge / bioconda）：

```bash
linxira-config mirror arch list
linxira-config mirror arch speed
linxira-config mirror npm speed
linxira-config mirror npm set npmmirror
linxira-config mirror pip set tuna
linxira-config mirror pip reset
linxira-config mirror aur speed official
linxira-config mirror flatpak auto
linxira-config mirror go set goproxy-cn
linxira-config conda channels list
```

Arch 与 Flatpak 走系统配置；pip / AUR（仅 Git clone 流量）/ Go 按用户生效；
npm 自 2026-10 起记录 `LINXIRA_NPM_REGISTRY` 偏好到
`/etc/profile.d/linxira-env.sh`，npm login/publish 永远走官方 registry。
所有来源只接受内置审核项或显式 HTTPS 地址，并在写入前进行网络探测。

AUR 不是签名二进制仓库。CLI 默认只列出可验证的官方端点；自定义地址必须通过 AUR
Git 智能 HTTP 探测。配置只重写软件包 Git 克隆流量，RPC 元数据仍使用官方服务：

```bash
linxira-config mirror aur set https://example.invalid/aur
linxira-config mirror aur reset
```

## 环境与软件栈

环境变量与常用软件栈（LaTeX、Python、容器、Rust、Node.js 等）经 Config CLI
转发到组件管理器完成，与 GUI 走同一条事务链：

```bash
linxira-config env list | get KEY | set KEY VALUE | unset KEY
linxira-config stack list | status <id...> | install <id...> --yes | tui
```

直连 `linxira-config install <pkg>` 会被拒止并指向正确归属——这是刻意的边界。

## 系统服务

CLI 还提供 SSH、防火墙、远程桌面、虚拟化、电源和网络诊断入口。涉及系统修改的操作会明确调用 `sudo`，普通的列表和测速操作不要求 root。
