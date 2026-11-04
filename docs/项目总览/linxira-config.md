# Config CLI（linxira-config-hub）

## 为什么存在

装完系统之后，用户会问两类问题：「这个设置怎么改」和「现在到底什么状态」。
这两类问题都不该逼用户去读 wiki 或记命令。`linxira-config` 把它们收成一个入口：
一个命令、一个人读得懂的输出、能改的只有它明确列出的那些东西。

它是 `linxira-config-hub` 仓库的拥有物，也是系统里唯一面向用户的通用设置 CLI。

## 职责边界

**归它**：镜像源选择（Arch / npm / pip / AUR / Flatpak / Go）、网络诊断与 DNS、
SSH 服务与密钥、UFW 防火墙、日志采集与上传、Timeshift 快捷配置、
无头（服务器）模式切换、环境变量文件、GPU 状态、工作区守护的启用与状态、
catalog 的只读查询、`tui` 数字菜单，以及给 agent 读的能力清单。

**不归它**：

- **装软件不归它**。软件安装、分组与组件由 [`linxira-components`](linxira-components.md) 产出 plan。
  CLI 里的 `install` / `workflow` 入口会直接拒绝并指向正确的归属。
- **系统恢复不归它**。出问题要证据包时用 [`linxira-recovery-diagnostics`](linxira-recovery.md)。
- **catalog 内容不归它**。应用、组件与 bundle 的数据在 [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog)；
  CLI 只按 catalog ID 查询，不展开、不应用任何记录。
- **安装逻辑不归它**。`stack` 只是到 `linxira-component-manager` 的转发桥，
  plan → confirm → apply 仍在 [`linxira-components`](linxira-components.md) 里完成。
- **事务后端没准备好的写操作不归它**。`service`、`rdp`、`virt`、`power` 的变更动作、
  `security harden` 与 `net fix` 会明确报「等待事务后端」，而不是给一个半成品实现。

## 怎么用

```bash
linxira-config mirror arch speed            # 测延迟
linxira-config mirror arch auto             # 选最快的
linxira-config net diag                     # 网络诊断
sudo linxira-config ssh on                  # 首次开启 SSH(允许密码, 用于配密钥)
linxira-config ssh key generate             # 生成 Ed25519 密钥
linxira-config ssh key show                 # 查看公钥并授权到服务器
linxira-config ssh authorized list          # 已授权的公钥
linxira-config ssh authorized add /tmp/key.pub  # 只接受纯公钥
sudo linxira-config ssh harden              # 确认密钥可用后关闭密码登录
sudo linxira-config ssh password on --yes   # 显式重新允许密码登录
sudo linxira-config ssh off                 # 持久关闭
linxira-config ssh status                   # SSH 状态
# 临时开启(仅本次, 重启后关闭, 适合一次性排障):
#   sudo systemctl start sshd
#   sudo systemctl stop sshd
# 首次连接(跳过交互指纹、8 秒超时):
#   ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 用户名@IP
linxira-config timeshift status             # 快照后端状态
sudo linxira-config timeshift enable        # 绑定系统盘并启用
sudo linxira-config timeshift disable       # 停止自动快照
linxira-config workspace-guard status       # 工作区守护状态
linxira-config help                         # 完整命令表
```

其余入口与只读查询（同样来自 `linxira-config help`）：

```bash
linxira-config --launch                     # 应用菜单「Linxira 配置中心」执行的形式
linxira-config tui                          # 纯 bash 数字菜单，调用同一批命令
linxira-config status                       # 一屏系统摘要
linxira-config capabilities                 # 打印 agent 读的能力清单
linxira-config catalog software --all       # catalog 只读查询（software/component/bundle）
linxira-config headless status              # 桌面 / 服务器模式的目标状态
linxira-config env list --json              # 读取 /etc/profile.d/linxira-env.sh
linxira-config stack list                   # 可安装软件栈（转发到 component-manager）
linxira-config logs collect                 # 收集诊断日志到 ~/linxira-logs/
```

`--launch` 只在现有终端里承载交互菜单：依次尝试 Konsole、Alacritty、xterm；
都不存在时，写一个临时的 `Terminal=true` 桌面条目并用 `gtk-launch` 打开
（没有这些终端的 COSMIC 会话就走这条回退）。它不自行提权，也不执行用户输入的命令字符串。

`ssh harden` 会检查当前用户至少有一把可用的 `authorized_keys`，把 `10-linxira.conf` 改成 `PasswordAuthentication no` 与 `KbdInteractiveAuthentication no`，先运行 `sshd -t`，再 reload。没有可用密钥会拒绝；非交互脚本加 `--yes`。不要用 `99-linxira-hardening.conf`：OpenSSH 先读 drop-in 且同一项取第一个值，`10-linxira.conf` 的 `yes` 会让后面的 `no` 静默失效。

`linxira-config help` 明确列出以下四条支持 `--json`，输出单行 JSON，结构化数据可直接给 agent 解析：

```bash
linxira-config workspace-guard status --json
linxira-config ssh status --json
linxira-config net diag --json
linxira-config mirror arch list --json
```

其余命令的输出是给人看的指导文本，不承诺结构化；agent 只需知道它成功还是失败。

## 何时需要 root

- **不需要 root（只读）**：`status`、`info`、`capabilities`、`catalog …`、`runtime status`、
  `gpu info`、`net diag`、`net dns`（只看）、`mirror … list|speed`、`ssh status`、
  `timeshift status`、`workspace-guard status`、`env list|get`、`stack list|status`、
  `logs collect`、`tui`、`help`。
- **需要 root**：`ssh on|off|harden|password|port`、`security ufw on|off|allow`、
  `net dns set`、`timeshift enable|disable`、`workspace-guard enable|disable`、
  `env set|unset`、`headless on|off`，写 `/etc/pacman.d/mirrorlist` 的
  `mirror arch auto|set|reset`（经 `sudo tee`），以及把 npm 偏好写进系统环境文件的
  `mirror npm auto|set|reset`。这些命令会显式要求 root，并提示使用 `sudo`。
- **按用户生效**：`mirror pip|aur|flatpak|go auto|set|reset` 只改当前用户的 pip、git、Flatpak 或 Go 配置。

设计上，agent 不代替用户发起需要 root 的交互式命令——把命令交给用户执行即可。

## 已知限制

- `service`、`rdp`、`virt`、`power` 的变更动作、`security harden` 与 `net fix` 目前都直接报
  「等待事务后端」；它们要等 plan / verify / receipt / rollback 齐备后才会启用，不是可用的半成品。
- `stack` 需要已安装 `linxira-component-manager`，否则直接报错；`linxira-config install`
  与 `workflow` 一律拒绝，并指向 Shelly 与快速配置系统软件。
- `help` 只对 `workspace-guard status --json`、`ssh status --json`、`net diag --json`、
  `mirror arch list --json` 承诺单行 JSON；`capabilities`、`env list|get`、`stack list`
  也接受 `--json`，但不在那个清单里。其余输出是给人看的指导文本。
- `headless on now` 会停止显示管理器并结束当前桌面会话，未保存的数据会丢失；切换前只在
  TTY 上要求确认，非交互场景没有额外保护。
- `logs upload` 会把选定的日志文件送到 paste.rs / termbin / dpaste 这类公开粘贴服务，
  上传前应确认文件内容。
- `ssh harden` 在没有可用 `authorized_keys` 时拒绝执行；它只改 `10-linxira.conf`，
  不会接管 `sshd_config` 里的其他 drop-in。
- 命令界面是终端；`--launch` 只是替你打开终端，没有独立的图形设置窗口。

## 深入设计

[配置中心](https://linxira-os.github.io/linxira-wiki/Linxira%20%E7%89%B9%E6%80%A7/config-hub/) ·
命令面、根权限边界与开发约定见 [`linxira-config-hub`](https://github.com/Linxira-OS/linxira-config-hub) 仓库的 `README.md` 与 `AGENTS.md`。
