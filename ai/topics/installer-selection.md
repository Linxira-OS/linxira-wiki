---
name: installer-selection
summary: 安装期组件选择回执 —— installer-selection.json 记录装了什么、延后了什么，组件管理器据此预选
audience: [human, ai]
tools: [linxira-component-manager]
privilege: none
---

# 组件安装回执预选（installer-selection）

## 是什么

Calamares 装机阶段，`linxirapacstrap` 模块在装包完成后把用户的软件选择写成只读
回执（临时文件 + 原子替换）：

```
/var/lib/linxira/installer-selection.json   # schema org.linxira.installer.selection-receipt.v1
/var/lib/linxira/pending-install.json       # 仅 applications，消费者是 linxira-package-center
```

回执记录：selectedLeafIds / selectedBundleIds、installedItems、deferredItems
（安装时明确延后的组件）、catalogVersion 与 catalogSha256、status。

## 谁消费

- **linxira-component-manager（GUI）**：打开目录时读 deferredItems，把尚未安装的
  延后组件**预勾选**进组件树，状态栏提示 “Installer deferred N component(s)”。
  CLI 与 TUI 不读回执。
- linxira-completion-agent / linxira-welcome：只读，用于首次在线完成度判断。
- linxiravalidate（装机校验）：回执的 catalogSha256 必须与目标机 catalog 一致。

## agent 用法

想知道这台机器装了什么、欠了什么，读回执再对照实时状态：

```bash
cat /var/lib/linxira/installer-selection.json
linxira-component-manager list --json
linxira-component-manager install <id...> --yes   # 补装延后组件（plan→confirm→apply）
```

入口是 `linxira-component-manager`（无 `cm` 短名）：无参数开 GUI，`--tui` 开
curses TUI，带子命令走 CLI；三者共用与 GUI 相同的事务链，退出码：0 成功 /
2 计划被拒 / 3 授权或执行失败。
