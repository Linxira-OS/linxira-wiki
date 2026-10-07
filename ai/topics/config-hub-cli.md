---
name: config-hub-cli
summary: linxira-config 命令面速查 —— SSH、诊断日志上传、镜像源、安全与系统状态的一站式入口
audience: [human, ai]
tools: [linxira-config]
privilege: user（ssh on / workspace-guard enable 等变更需 root/sudo）
---

# Config Hub CLI（config-hub-cli）

## 何时查这页

需要远程接入这台机器（SSH）、把诊断日志变成一个可分享链接、切换
国内外镜像源、查安全态势，或想不起来 `linxira-config` 某个子命令
的时候。一切以 `linxira-config help` 与 `--json` 输出为准（版本
2.5.2 起）。

## 命令面（agent 可直接调用）

```bash
# 诊断日志 —— 排障第一步；上传后把短链交给维护者即可
linxira-config logs collect          # 收集到 ~/linxira-logs/（含安装器完整日志）
linxira-config logs upload [file]    # paste.rs -> termbin -> dpaste 自动降级，返回短链

# SSH 远程接入
linxira-config ssh on|off|status [--json]
linxira-config ssh port <n>
linxira-config ssh key generate|list|show|fingerprint|remove
linxira-config ssh authorized add <公钥>|list|remove <指纹> --yes

# 镜像源（arch/npm/pip/aur/flatpak/go）
linxira-config mirror <type> list|speed|auto|set|reset [--json]
linxira-config conda channels list|add|remove|reset   # 仅 conda-forge / bioconda

# 环境变量与软件栈（stack 转发 component-manager，见 stacks-and-env）
linxira-config env list|get|set|unset
linxira-config stack list|status|install|tui

# 工作区守护（详见 workspace-guard 主题）
linxira-config workspace-guard status [--json]|handbook
sudo linxira-config workspace-guard enable|disable

# 快照一体化（enable/disable 需 root；机制见 updates-and-snapshots 主题）
linxira-config timeshift status              # 版本/配置/hook/grub-btrfsd/最近快照
sudo linxira-config timeshift enable|disable # 调 /usr/share/linxira/timeshift/linxira-timeshift-enable.sh（幂等）

# 状态与安全
linxira-config security status
linxira-config security ufw allow <port>
linxira-config net diag [--json] | dns | dns set <ip>
linxira-config headless on           # 下次启动不加载桌面
linxira-config info | status | tui
```

## 架构事实（agent 需要知道）

- `logs upload` 通道顺序：paste.rs → termbin（bash /dev/tcp，无 nc
  依赖）→ dpaste；0x0.st 已全网停服，不要再用。
- `logs collect` 覆盖 /tmp/linxira-installer.log（安装器崩溃第一现场）、
  Calamares 会话日志、pacman.log、失败单元与本次开机错误日志。
- `ssh on` 直接可用（无需事务后端）：live 会话内 installer 用户免密
  sudo，装机后普通用户经 wheel/sudo。live 会话 root 密码为 linxira。
- `mirror` 的 pip/aur/go 源按用户生效（pip config / git insteadOf，仅改
  clone 流量 / go env -w）；npm 记 `LINXIRA_NPM_REGISTRY` 偏好到
  /etc/profile.d/linxira-env.sh，npm login/publish 永远走官方 registry。
  Arch 与 Flatpak 走系统配置。Miniforge 仅放行
  conda-forge / bioconda。
- `rdp`、`virt kvm-on/docker-on`、`security harden`、`power` 写操作
  刻意等待事务后端，只读 status 可用——不要试图绕过。
- 所有列出的 `--json` 子命令输出机器可读结果，agent 优先用它们。
