# 更新助手（linxira-update）

## 为什么存在

滚动发行版的风险不在「更新」本身，而在「更新时没有退路」。Linxira OS 的答案
是把更新与快照做成一件事：每次更新前自动留下可引导的 Timeshift 快照，
出问题从 GRUB 快照菜单回到更新前的系统。`linxira-update` 负责这件事里
「检查与提醒」的半边——后台定时检查、托盘与桌面通知、Welcome 更新卡，
都读同一份状态文件；默认只提醒不动手。

## 职责边界

**归它**：检查全部已配置 pacman 仓库（`[linxira]` + Arch core/extra）的可用更新、
写 `status.json`、托盘图标与桌面通知、交互式全量升级、新闻与待重启服务提示、
开启 `EnableAutoApply` 后的快照+全自动升级。

**不归它**：

- **装软件不归它**。组件安装走 `linxira-component-manager`
  （Config CLI 的 `stack` 也是转发到它），与更新共用同一套快照保护。
- **快照配置不归它**。Timeshift 的启用与策略在 [`linxira-config`](linxira-config.md)
  的 `timeshift enable|disable|status`。
- **AUR 与 Flatpak 默认不碰**。需在配置里显式 opt-in。

## 怎么用

```bash
linxira-update --check      # 只检查并通知（定时器每小时自动跑一次）
linxira-update              # 交互式全量升级
linxira-update --list       # 只列更新不应用
linxira-update --tray       # 托盘常驻
```

状态文件 `~/.local/state/linxira-update/status.json`：`check_status`
（ok/error/incomplete）、`available_update_count`、`last_check`、
`reboot_required`。检查不完整时更新数为 0 不代表已是最新。

定时检查由 user timer `linxira-update.timer`（每小时）承担，随包 preset 在
首次登录时自动启用；Welcome 更新卡与托盘只是它的展示层。

## 更新前自动快照与全自动更新

- 装好的系统上，任何 pacman 事务前都有 PreTransaction 钩子自动创建 Timeshift
  快照（保留最近 20 个），快照自动进 GRUB 菜单，可只读引导验证后回滚。
  详见 wiki 的 `updates-and-snapshots` 主题（`linxira-wiki show updates-and-snapshots`）。
- 在 `~/.config/linxira-update/linxira-update.conf` 加一行 `EnableAutoApply`
  可开启全自动更新：默认关闭；开启后仅在 btrfs + 快照设施齐备的机器上生效，
  每次自动升级前显式创建并校验快照，条件不满足就保持只检查+通知。

## 何时需要 root

检查、列表、托盘、通知都不需要。应用更新时由它通过
`PrivilegeElevationCommand`（默认 `sudo`）提权；自动应用路径使用
`pacman -Syu --noconfirm`，仅在全量升级时使用，绝不部分升级。

## 深入设计

内部实现见 [`linxira-update`](https://github.com/Linxira-OS/linxira-update)
仓库；命令面与全部配置键速查见 wiki 的 `update-cli` 主题。
