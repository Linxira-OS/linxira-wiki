# Config CLI（linxira-config-hub）

## 为什么存在

装完系统之后，用户会问两类问题：「这个设置怎么改」和「现在到底什么状态」。
这两类问题都不该逼用户去读 wiki 或记命令。`linxira-config` 把它们收成一个入口：
一个命令、一个人读得懂的输出、能改的只有它明确列出的那些东西。

它是 `linxira-config-hub` 仓库的拥有物，也是系统里唯一面向用户的通用设置 CLI。

## 职责边界

**归它**：镜像源选择（Arch / npm / pip / AUR / Flatpak / Go）、网络诊断与 DNS、
SSH 服务与密钥、UFW 防火墙、日志采集与上传、Timeshift 快捷配置、
无头模式、GPU 状态、工作区守护的启用与状态。

**不归它**：

- **装软件不归它**。软件安装、分组与组件由 [`linxira-components`](linxira-components.md) 产出 plan。
  CLI 里的 `install` / `workflow` 入口会直接拒绝并指向正确的归属。
- **系统恢复不归它**。出问题要证据包时用 [`linxira-recovery-diagnostics`](linxira-recovery.md)。
- **事务后端没准备好的写操作不归它**。`service`、`rdp`、`security harden`、`net fix`
  会明确报「等待事务后端」，而不是给一个半成品实现。

## 怎么用

```bash
linxira-config mirror arch speed            # 测延迟
linxira-config mirror arch auto             # 选最快的
linxira-config net diag                     # 网络诊断
sudo linxira-config ssh on                  # 首次开启 SSH(允许密码, 用于配密钥)
linxira-config ssh key generate             # 生成 Ed25519 密钥
linxira-config ssh key show                 # 查看公钥并授权到服务器
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

`ssh harden` 会检查当前用户至少有一把可用的 `authorized_keys`，把 `10-linxira.conf` 改成 `PasswordAuthentication no` 与 `KbdInteractiveAuthentication no`，先运行 `sshd -t`，再 reload。没有可用密钥会拒绝；非交互脚本加 `--yes`。不要用 `99-linxira-hardening.conf`：OpenSSH 先读 drop-in 且同一项取第一个值，`10-linxira.conf` 的 `yes` 会让后面的 `no` 静默失效。

以下四条支持 `--json`，输出单行 JSON，结构化数据可直接给 agent 解析：

```bash
linxira-config workspace-guard status --json
linxira-config ssh status --json
linxira-config net diag --json
linxira-config mirror arch list --json
```

其余命令的输出是给人看的指导文本，不承诺结构化；agent 只需知道它成功还是失败。

## 何时需要 root

- **不需要**：`list` / `speed` / `status` / `diag` / `show` / `source` / `info` / `runtime`。
- **需要**：`enable` / `disable` / `on` / `off` / `harden` / `ufw on` 这类改系统状态的命令，
  会显式要求 root 并提示 `sudo`。

设计上，agent 不代替用户发起需要 root 的交互式命令——把命令交给用户执行即可。

## 深入设计

[配置中心](https://linxira-os.github.io/linxira-wiki/Linxira%20%E7%89%B9%E6%80%A7/config-hub/) ·
内部实现见 [`linxira-config-hub`](https://github.com/Linxira-OS/linxira-config-hub) 仓库的 `document/` 目录。
