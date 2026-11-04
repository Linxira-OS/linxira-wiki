# 恢复诊断（linxira-recovery-diagnostics）

## 为什么存在

系统出问题时，第一反应通常是「赶紧修」。但很多修复动作本身会毁掉证据，
修完之后既不知道最初坏在哪，也没法判断修好了没有。

`linxira-recovery-diagnostics`（lrd）先把这个顺序固定下来：
**只读取事实，把修复写成一份带前提条件的计划，执行需要一张用户授权的凭据。**

它是 `linxira-recovery-diagnostics` 仓库的拥有物，也是系统里唯一被允许主动
运行固定白名单命令的只读采集器。

## 职责边界

**归它**：恢复就绪度检查、只读证据采集（存储、timeshift、keyring、btrfs、pci、网络）、
修复计划（`--plan` 与 GUI 的 Repairs 页）、私有脱敏支持包。

**不归它**：

- **不执行修复**。lrd 只产出计划；两个只读诊断由 [`linxira-components`](linxira-components.md)
  的系统事务服务执行，修复类计划没有执行后端。
- **不做 root 操作**。采集阶段没有任何写操作，也没有 `subprocess` 走 shell。
- **不删东西**。pacman 锁被锁住时它只报告，不删除。

## 怎么用

GUI 与应用菜单执行 `linxira-recovery-diagnostics-gui`；命令行入口是
`linxira-recovery-diagnostics`：

```bash
linxira-recovery-diagnostics --report-json     # 全量 schema-v1 报告
linxira-recovery-diagnostics --support-bundle  # 私有、脱敏的证据包
linxira-recovery-diagnostics                   # 不带参数 = 打开 GUI
linxira-recovery-diagnostics --plan org.linxira.recovery.pacman-lock-diagnose.v1
```

三个选项互斥，一次只做一件事。计划与支持包都以生成的文件名写到
`$XDG_STATE_HOME/linxira-recovery-diagnostics`（默认 `~/.local/state/linxira-recovery-diagnostics`），
不接受输出路径参数。

GUI 有五个页签：Overview、Snapshots、Repairs、Workspace guard、Support report。
Repairs 页把每个 plan 的 `effects` 与 `preconditions` 摆出来；
`available: false` 的 plan 按钮是禁用的，并在 tooltip 里说明原因——**那是设计，不是 bug**。

计划 ID 是固定列表，共 8 个；可用的只有两个只读诊断：
`org.linxira.recovery.pacman-lock-diagnose.v1` 与
`org.linxira.recovery.live-chroot-readiness.v1`，它们经系统 D-Bus 事务服务执行且
`read_only: true`。计划本身在本地生成，执行按钮在 Repairs 页。其余六个（快照、回滚、
keyring、initramfs，以及工作区守护的建快照与恢复）一律写 `apply-backend-not-ready`，
其中回滚与守护恢复另加 `future-root-receipt-required`，按钮保持禁用。

## 何时需要 root

**lrd 自己从不提权。** 采集、报告、计划与支持包都以当前用户运行，没有任何写操作，
也没有 shell。

唯一与 root 有关的路径是两个只读诊断的执行：lrd 通过系统 D-Bus 事务服务提交固定
操作 ID，由 root 所属的服务按 Polkit 要求管理员认证后执行，再把只读结果作为
receipt 返回。
lrd 不持有 sudo，也不接受用户传入的命令或参数。

工作区守护的证据采集读的是 root 拥有的 `/etc/linxira/workspace-guard.conf`，
读不到时报告 `configured: false`（读取被拒绝与未配置在当前实现中不可区分），
不会因此崩溃或索取授权。

## 已知限制

- 只检查 `/` 与 `/mnt` 两个系统根；不接受任意路径、快照标识或命令参数。
- 外部命令只用精确的 argv 允许列表：`findmnt`、`lsblk`、Timeshift 列表与只读的
  `systemctl is-enabled`/`is-active`；没有 shell、mount/chroot、包变更或服务变更。
- pacman 锁只诊断，永不删除；锁还在时它只报告，把处置留给人。
- 可执行后端的只有两个只读诊断；其余计划即使前提全部满足也保持 `available: false`。
- 支持包会做递归脱敏并显示清单，不包含 journal、dmesg、原始进程命令行，
  不上传；但它是证据快照，分享前仍应按自己的隐私要求检查。
- GUI 的 Workspace guard 页在守护未配置时只能显示未配置状态，不提供启用入口。

## 深入设计

内部实现与安全边界见 [`linxira-recovery-diagnostics`](https://github.com/Linxira-OS/linxira-recovery-diagnostics)
仓库的 `README.md`。
