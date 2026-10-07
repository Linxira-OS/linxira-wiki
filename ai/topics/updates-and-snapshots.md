---
name: updates-and-snapshots
summary: 滚动仓库与快照一体化 —— 任何 pacman 事务前自动快照、可引导回滚，EnableAutoApply 开启后全自动升级
audience: [human, ai]
tools: [linxira-update, linxira-config]
privilege: user（enable/disable 与自动应用需 root，由工具内部提权）
---

# 更新与快照一体化（updates-and-snapshots）

## 滚动仓库与两个安装位置

- 仓库：`[linxira]` pacman 仓库（linxira-os.github.io/linxira-packages，签名 db+包），
  与 Arch core/extra 一样默认启用。跟随链：源仓 VERSION 提交 → release.yml 建 tag
  Release → packages 仓 auto-bump 每日扫描出 PR → checks 绿自动 squash 合并 →
  构建签名 → 同步 Pages。
- 位置①：Calamares 释放阶段离线 pacstrap（版本=镜像日），同时给装机系统写入
  `[linxira]` 在线仓。
- 位置②：装后 Welcome 入口——Welcome 是纯启动器，exec
  `/usr/bin/linxira-component-manager` 与 `/usr/bin/linxira-update --launch`，
  无内嵌副本。装后统一收敛到滚动仓库：**镜像老 ≠ 系统老**。

## 快照一体化（已实装）

- `/etc/pacman.d/hooks/linxira-timeshift-autosnap.hook`：PreTransaction、
  Operation=Upgrade/Install/Remove、Target=\* → 任何 pacman 事务（系统升级、组件
  安装、裸 pacman）前自动 `timeshift --create --tags O`，事务后修剪保留最近
  20 个 auto-snapshot。
- 无 `/etc/timeshift/timeshift.json` 时静默跳过；快照失败不阻塞事务——软门控是
  刻意的（PreTransaction 非零退出会中止事务）。
- 可引导回滚：grub-btrfsd 以 `--timeshift-auto` 运行（systemd 服务，自动探测
  timeshift 快照）→ 快照自动生成 GRUB 条目；mkinitcpio HOOKS 含
  `grub-btrfs-overlayfs` → 快照条目只读引导验证，满意后再恢复。
- 配置入口：安装期 calamares shellprocess_linxira-timeshift 与运行期
  `linxira-config timeshift enable|disable|status` 调用同一份
  `/usr/share/linxira/timeshift/linxira-timeshift-enable.sh`（幂等）。
  策略：btrfs 模式，每日 3 份 + 启动 3 份。

## EnableAutoApply（全自动更新，默认关闭）

`~/.config/linxira-update/linxira-update.conf` 加裸键一行 `EnableAutoApply` 即开启
（与 EnableAUR 同风格）。开启后 `--check` 发现更新时执行**硬门控**，四条全满足才动手：
btrfs 根文件系统；`/etc/timeshift/timeshift.json` 存在；mkinitcpio HOOKS 含
grub-btrfs-overlayfs；grub-btrfsd 单元已启用。

通过后：显式 `timeshift --create` 并校验成功 → `pacman -Syu --noconfirm`
非交互全量升级 → status.json 写 `pre_snapshot_id`。
任一门控不满足或快照失败 → 拒绝自动应用（保持只检查+通知），status.json 记
`auto_apply=false` 与原因。

- 非 btrfs / 服务器 / WSL 天然被门控拒绝，保持手动。
- 自动应用不做 AUR/Flatpak，不做白名单部分升级（Arch 部分升级纪律）。

命令面、全部配置键与 status.json 字段见 `update-cli` 主题。
