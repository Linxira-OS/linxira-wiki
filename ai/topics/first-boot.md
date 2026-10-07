---
name: first-boot
summary: 新机器第一次开机，按什么顺序做什么
audience: [human, ai]
tools: [linxira-welcome, linxira-config, linxira-components, linxira-wiki]
privilege: user
---

# 首次启动

新装的机器上，一次开机之内要完成的事是有顺序的。跳过前一步做后一步，后面会返工。

## 1. 先把系统更新到最新

`linxira-welcome` 是入口（控制中心），更新由 `linxira-update` 负责。
先更新再配任何东西，否则配的东西可能被后续更新覆盖。

agent 要更新包时直接用 `pacman`，不必绕 `linxira-update`。
机制（滚动仓库、事务前自动快照、可选的全自动更新 EnableAutoApply）
见 `updates-and-snapshots` 与 `update-cli` 主题。

## 2. 配镜像源与网络

```bash
linxira-config mirror arch speed     # 先测延迟
linxira-config mirror arch auto      # 自动选最快的
linxira-config net diag              # 确认网络真的通
linxira-config ssh status            # 需要远程接入时再开
```

`net diag`、`ssh status`、`mirror arch list` 支持 `--json`，直接给结构化事实。

## 3. 装软件走 components

装软件、分组、组件都归 `linxira-components`，它是唯一产出 plan / confirm / receipt 的入口。
不要直接 `pacman -S` 绕过计划。

```bash
linxira-components list --catalog /usr/share/linxira/catalog/catalog-v3.json --json
```

安装时被延后的组件已由回执预选：组件管理器 GUI 打开即预勾选
（机制见 `installer-selection` 主题）。

## 4. 注册工作区守护（可选但建议）

用户有代码仓库时，装机阶段应已创建独立 ext4 分区。
确认它跑起来了：

```bash
linxira-config workspace-guard status
linxira-components guard status
```

## 5. 知道去哪查

```bash
linxira-wiki show first-boot
linxira-wiki search privilege
```

本手册随系统安装（`/usr/share/linxira/wiki`），离线也能读。
