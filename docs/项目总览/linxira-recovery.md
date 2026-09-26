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

- **不执行修复**。lrd 只产出计划；执行由 [`linxira-components`](linxira-components.md) 在收到 receipt 后完成。
- **不做 root 操作**。采集阶段没有任何写操作，也没有 `subprocess` 走 shell。
- **不删东西**。pacman 锁被锁住时它只报告，不删除。

## 怎么用

```bash
linxira-recovery-diagnostics --report-json     # 全量 schema-v1 报告
linxira-recovery-diagnostics --support-bundle  # 私有、脱敏的证据包
linxira-recovery-diagnostics                   # 不带参数 = 打开 GUI
linxira-recovery-diagnostics --plan org.linxira.recovery.pacman-lock-diagnose.v1
```

GUI 有五个页签：Overview、Storage、Network、Support report、Workspace guard。
Repairs 页把每个 plan 的 `effects` 与 `preconditions` 摆出来；
`available: false` 的 plan 按钮是禁用的，并在 tooltip 里说明原因——**那是设计，不是 bug**。

已接入可执行后端的只读诊断只有两个：`pacman-lock-diagnose` 与 `live-chroot-readiness`。
其余计划处于等待 receipt 授权的状态。

## 何时需要 root

**全部不需要**。lrd 的定位就是只读诊断，任何时候都不提权。
这也是它能安全地在故障现场运行的原因——它跑不起来的时候，故障另有其因。

唯一与 root 有关的例外是工作区守护的证据采集：它读的是
root 拥有的 `/etc/linxira/workspace-guard.conf`，所以只能报告
「已配置但当前用户无权读取」或直接报 `configured: false`，不会因此崩溃或索取授权。

## 深入设计

内部实现见 [`linxira-recovery-diagnostics`](https://github.com/Linxira-OS/linxira-recovery-diagnostics)
仓库的 `document/` 目录。
