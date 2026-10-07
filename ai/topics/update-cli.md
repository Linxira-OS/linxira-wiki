---
name: update-cli
summary: linxira-update 命令面速查 —— 参数、全部配置键、status.json 字段与 user timer
audience: [human, ai]
tools: [linxira-update]
privilege: user（应用更新经 PrivilegeElevationCommand 提权）
---

# linxira-update 命令面（update-cli）

## 是什么

系统更新通知与维护助手（fork 自 arch-update/Cachy-Update，GPL-3.0）。入口
`/usr/bin/linxira-update`；Welcome 更新卡、托盘图标、桌面通知读同一个 status.json。

## 参数

```bash
linxira-update              # 交互式全量升级（flock 单例）
linxira-update --check      # 只检查：写 status.json、切托盘图标、有更新发桌面通知
linxira-update --list       # 只列更新不应用（无更新退 7；检查不完整退 19）
linxira-update --launch     # 托盘/桌面入口：在可用终端里承载交互式更新
linxira-update --tray       # 托盘常驻；--tray --enable 写入用户自启动
linxira-update --news [N]   # 查看发行新闻
linxira-update --services   # 列出需要重启/重启后需检查的服务
linxira-update --gen-config [--force] | --show-config | --edit-config
```

## 配置（~/.config/linxira-update/linxira-update.conf）

| 键 | 默认 | 说明 |
|---|---|---|
| EnableAUR / EnableFlatpak | 关 | AUR 与 Flatpak 更新需 opt-in |
| EnableAutoApply | 关 | 全自动更新（硬门控，见 updates-and-snapshots） |
| NewsNum / NewsTimeout | 5 / 10 | 新闻条数 / 每条展示秒数 |
| UpdateCheckTimeout | 120 | checkupdates 超时秒数，硬错误自动重试一次 |
| PrivilegeElevationCommand | sudo | 可选 sudo sudo-rs doas run0 |
| KeepOldPackages / KeepUninstalledPackages | 3 / 0 | 包缓存保留数量 |
| DiffProg | — | pacdiff 使用的比较器 |
| TrayIconStyle | blue | blue light dark |
| AURHelper | 自动探测 | paru > yay > pikaur |

另有布尔键 NoColor / NoVersion / NoNotification / ColorblindMode。

## status.json（~/.local/state/linxira-update/status.json，原子写）

`version`=1、`available_update_count`、`check_status`（ok/error/incomplete）、
`last_check`、`reboot_required`，可选 `message`；开启 EnableAutoApply 后新增可选
`pre_snapshot_id`（string）与 `auto_apply`（bool），既有字段不变。
消费方（Welcome 更新卡、托盘）要求 version==1。
**check_status 非 ok 时，更新数为 0 不代表已是最新。**

## 定时器与更新范围

- systemd user timer `linxira-update.timer`（OnBootSec=2min、OnUnitActiveSec=1h、
  Persistent=true），随包 preset `/usr/lib/systemd/user-preset/80-linxira-update.preset`
  → 用户首次登录自动启用，之后每小时一次 `--check`。
- 范围：默认全部已配置 pacman 仓库（[linxira] + Arch core/extra）；AUR/Flatpak 需 opt-in。
- `linxira-*` 等外来包永不送 AUR helper；`[linxira]` 仓未配置或不可达时报
  incomplete 并提示检查仓库连通性，不谎报最新。
