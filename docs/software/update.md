# 更新助手（linxira-update）

## 为什么存在

滚动发行版的风险不在「更新」本身，而在「更新时没有退路」。Linxira OS 的答案
是把更新与快照做成一件事：每次更新前自动留下可引导的 Timeshift 快照，
出问题从 GRUB 快照菜单回到更新前的系统。`linxira-update` 负责这件事里
「检查与提醒」的半边——后台定时检查、托盘与桌面通知、Welcome 更新卡，
都读同一份状态文件；默认只提醒不动手。

## 职责边界

**归它**：检查全部已配置 pacman 仓库（Linxira 仓库加系统已启用的 Arch 仓库）的可用更新、
写 `status.json`、托盘图标与桌面通知、交互式全量升级、新闻与待重启服务提示、
开启 `EnableAutoApply` 后的快照+全自动升级。

**不归它**：

- **装软件不归它**。组件安装走 `linxira-component-manager`
  （Config CLI 的 `stack` 也是转发到它），与更新共用同一套快照保护。
- **快照配置不归它**。Timeshift 的启用与策略在 [`linxira-config`](config.md)
  的 `timeshift enable|disable|status`。
- **AUR 与 Flatpak 默认不碰**。需在配置里显式 opt-in。

## 怎么用

安装完成后可以先手动走一遍完整流程：

```bash
linxira-update
```

之后日常可以只检查或让托盘提醒：

```bash
linxira-update --check      # 只检查并通知（定时器会自动执行这一条）
linxira-update              # 交互式全量升级
linxira-update --list       # 只列更新不应用
linxira-update --tray       # 托盘常驻（--tray --enable 同时写开机自启）
linxira-update --launch     # 应用菜单与托盘点击执行的形式：在终端里打开交互流程
linxira-update --gen-config # 生成示例配置（--force 覆盖已有文件）
linxira-update --show-config # 显示当前配置
```

这些入口共用同一份状态：应用菜单的「Linxira Update」执行 `--launch`，
「Linxira Update Tray」与 `linxira-update-tray.service` 执行 `--tray`（包还附带
`/etc/xdg/autostart/linxira-update-tray.desktop`，登录即启动托盘），
Welcome 的更新卡只读 `status.json`，不另跑一次检查。

状态文件 `~/.local/state/linxira-update/status.json`：`check_status`
（ok/error/incomplete）、`available_update_count`、`last_check`、
`reboot_required`，自动更新路径还会写 `auto_apply` 与 `pre_snapshot_id`。
检查不完整时更新数为 0 不代表已是最新。

定时检查由 user timer `linxira-update.timer` 承担（开机 2 分钟后一次，之后每小时，
`Persistent=true`），随包 preset `80-linxira-update.preset` 在首次登录时启用；
实际执行的是 `linxira-update.service`，它运行 `linxira-update --check`，
并带 `LINXIRA_UPDATE_UNATTENDED=1` 标记。Welcome 更新卡与托盘只是展示层。

## 更新前自动快照与全自动更新

- 在已启用 Timeshift 的装好系统上，任何 pacman 事务前都有 PreTransaction 钩子自动创建 Timeshift
  快照（保留最近 20 个）；在 Timeshift 与 grub-btrfs 配置齐备时，快照自动进
  GRUB 菜单，可只读引导验证后回滚。
  详见 wiki 的 `updates-and-snapshots` 主题（`linxira-wiki show updates-and-snapshots`）。
- 在 `~/.config/linxira-update/linxira-update.conf` 加一行 `EnableAutoApply`
  可开启全自动更新：默认关闭。开启后只由无人值守的 `linxira-update.service` 触发，
  托盘与终端里的手动 `--check` 永远不会自动应用。硬门控有五项：btrfs 根文件系统、
  Timeshift 已配置、`mkinitcpio` 的 `HOOKS` 含 `grub-btrfs-overlayfs`、
  `grub-btrfsd` 已启用、存在可用的提权命令。全部通过才显式创建并校验快照
  （`timeshift --create`，再按注释确认快照入列），随后执行
  `pacman -Syu --noconfirm`；任一环节失败就保留「只检查+通知」并记录原因。

## 何时需要 root

检查、列表、托盘、通知与 `--gen-config`/`--show-config` 都不需要 root。
应用更新时由它通过 `PrivilegeElevationCommand` 提权，该键只接受
`sudo`、`sudo-rs`、`doas`、`run0`，默认 `sudo`。自动应用路径使用
`pacman -Syu --noconfirm`，仅做全量升级，绝不做部分升级。

## 已知限制

- AUR 与 Flatpak 默认关闭，必须在配置文件里显式写 `EnableAUR` / `EnableFlatpak`。
  名字为 `linxira` 或以 `linxira-` 开头的已安装外部包永远不会交给 AUR helper；
  没有 pacman 仓库提供它们时，检查结果记为 incomplete。
- `available_update_count` 为 0 时，只有 `check_status` 也是 `ok` 才能理解为「已是最新」。
- 自动更新只在无人值守服务里生效；在终端或托盘手动检查不会自动应用，即使门控全部满足。
- pacman PreTransaction 钩子在 `timeshift.json` 存在时创建更新前快照，保留最近 20 个；
  钩子里快照失败用 `|| true` 兜底，**不会中止 pacman 事务**，所以「有快照」不能当作绝对保证。
- 钩子对 Upgrade / Install / Remove 都生效；`Linxira 初始快照` 永不修剪，
  boot 与 daily 快照各保留最近 3 个。
- 更新检查不代替 Arch 新闻阅读：新闻提示只在交互流程里出现，自动路径只做包升级。
- `--tray --enable` 通过复制 XDG autostart 条目实现；目标文件已存在时会直接报错，
  不会覆盖你已有的登录项。

## 深入设计

内部实现见 [`linxira-update`](https://github.com/Linxira-OS/linxira-update)
仓库的 [`README-LINXIRA.md`](https://github.com/Linxira-OS/linxira-update/blob/main/README-LINXIRA.md)
与 `doc/man/`；命令面与全部配置键速查见 wiki 的 `update-cli` 主题。
