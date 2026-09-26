---
name: recovery
summary: 系统出问题时先取只读证据，再谈修复
audience: [human, ai]
tools: [linxira-recovery-diagnostics]
privilege: polkit
---

# 恢复诊断

`linxira-recovery-diagnostics`（lrd）分两半：**只读采集**与**修复计划**。
采集永远不需要授权；执行永远需要一张由用户授权的 receipt。

## 什么时候用

- 系统起不来、pacman 锁住、initramfs 或 keyring 可疑
- 需要一份能发给别人的离线证据包
- 用户说「昨天还好好的」，你要先弄清现状而不是先动手

## 只读采集

```bash
linxira-recovery-diagnostics --report-json      # 全量 schema-v1 报告
linxira-recovery-diagnostics --support-bundle   # 私有、脱敏的证据包
linxira-recovery-diagnostics                    # 不带参数 = 打开图形界面
```

GUI 的 Repairs 页把每个 plan 的 `effects` / `preconditions` 摆出来，
`available: false` 的 plan 会禁用按钮并说明原因——**那是设计，不是 bug**。

## 修复计划

```bash
linxira-recovery-diagnostics --plan org.linxira.recovery.pacman-lock-diagnose.v1
```

`--plan` 的可选值是 `linxira-recovery-diagnostics --help` 里列出的固定集合，不接受自由文本。
已接入后端的只读诊断只有两个：`pacman-lock-diagnose` 与 `live-chroot-readiness`。
其余（建快照、回滚、修 keyring、重建 initramfs、工作区守护快照/恢复）
在 `available: false` 状态下等待 receipt 授权。

## 不要做的事

不要手工删 pacman 锁，不要 `chroot` 后直接跑包管理器，不要在没拿到报告前
建议用户重装。这些都会破坏后续可用的证据。
