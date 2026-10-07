# 项目总览

本 wiki 讨论**每个项目的大体设计流程**：为什么存在、职责边界、何时用哪个、权限模型。
具体项目的内部设计、数据结构与实现决策不在本 wiki，在各项目自己仓库的 `document/` 目录。

本页是全表。日常只需要记住五个项目，它们是 agent 与人会直接操作的那五个：

- [Config CLI](linxira-config.md) —— 改设置、查网络与 SSH、镜像源、守护的启用入口
- [Components](linxira-components.md) —— 装软件与一切需要 root 的事务
- [更新助手](linxira-update.md) —— 检查与应用系统更新、托盘提醒、快照一体化的更新侧
- [恢复诊断](linxira-recovery.md) —— 系统出问题时先取只读证据
- [工作区守护](workspace-guard.md) —— 跨项目机制，防 agent 误删工作区

## 全表

下表的 `owns` 与 `lifecycle` 来自 `linxira-os/governance/repositories.yaml`，
本包内的 `ai/manifest.json` 由该文件生成，不手工维护。

| 仓库 | owns | lifecycle |
|---|---|---|
| [`linxira-os`](https://github.com/Linxira-OS/linxira-os) | product-architecture、repository-governance、support-matrix、release-manifests | active |
| [`linxira-iso-direct`](https://github.com/Linxira-OS/linxira-iso-direct) | live-profile、installer-configuration、target-manifests、iso-build | active |
| [`packages`](https://github.com/Linxira-OS/packages) | pkgbuilds、package-ci、signed-repository-publication | active |
| [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog) | catalog-schema、applications、capabilities、presets、desktop-metadata | active |
| [`linxira-components`](https://github.com/Linxira-OS/linxira-components) | transaction-planning、confirmation、privileged-apply、receipts | active |
| [`linxira-package-center`](https://github.com/Linxira-OS/linxira-package-center) | package-center-ui、installed-state-presentation | active |
| [`linxira-component-manager`](https://github.com/Linxira-OS/linxira-component-manager) | component-manager-ui、capability-state-presentation | active |
| [`linxira-gaming-manager`](https://github.com/Linxira-OS/linxira-gaming-manager) | gaming-library、compatibility-launch、user-backup | active |
| [`linxira-update`](https://github.com/Linxira-OS/linxira-update) | system-update、update-status、update-tray | active |
| [`linxira-completion-agent`](https://github.com/Linxira-OS/linxira-completion-agent) | first-online-plan-presentation、completion-state、transaction-delegation | active |
| [`linxira-hwd-detector`](https://github.com/Linxira-OS/linxira-hwd-detector) | read-only-hardware-detection、hardware-fact-contract | active |
| [`linxira-hardware-driver-manager`](https://github.com/Linxira-OS/linxira-hardware-driver-manager) | driver-policy-ui、kernel-dkms-report、driver-plan | active |
| [`linxira-kernel-manager`](https://github.com/Linxira-OS/linxira-kernel-manager) | kernel-policy-ui、boot-state-report、kernel-plan | active |
| [`linxira-recovery-diagnostics`](https://github.com/Linxira-OS/linxira-recovery-diagnostics) | recovery-readiness、repair-plan、private-support-bundle | active |
| [`linxira-welcome`](https://github.com/Linxira-OS/linxira-welcome) | welcome-status、lifecycle-guidance、fixed-tool-routing | active |
| [`linxira-config-hub`](https://github.com/Linxira-OS/linxira-config-hub) | linxira-cli、diagnostics、runtime-adapters、source-adapters、ssh-network-plans | active |
| [`linxira-artwork`](https://github.com/Linxira-OS/linxira-artwork) | brand-assets、terminal-artwork、visual-policy | active |
| [`linxira-hooks`](https://github.com/Linxira-OS/linxira-hooks) | pacman-hooks、reboot-state | review-required |
| [`linxira-wiki`](https://github.com/Linxira-OS/linxira-wiki) | user-documentation | active |
| [`Linxira-OS.github.io`](https://github.com/Linxira-OS/Linxira-OS.github.io) | public-website、publication-endpoint | active |
| [`linxira-hello`](https://github.com/Linxira-OS/linxira-hello) | — | deprecated |
| [`linxira-iso`](https://github.com/Linxira-OS/linxira-iso) | — | deprecated |
| [`extendai-lab-cli`](https://github.com/Linxira-OS/extendai-lab-cli) | extendai-cli | independent |
| [`extendai-lab-Studio`](https://github.com/Linxira-OS/extendai-lab-Studio) | extendai-studio | independent |
| [`linxira-pulse`](https://github.com/Linxira-OS/linxira-pulse) | ai-assistant | independent |
| [`linxira-skills`](https://github.com/Linxira-OS/linxira-skills) | skill-platform | independent |

## 怎么读 lifecycle

- **active** —— 在维护，功能承诺有效。
- **review-required** —— 归属待复核。`linxira-hooks` 是当前唯一一个。
- **independent** —— 自有节奏，不随系统发布走。
- **deprecated** —— 已被取代，不要在新工作里使用。

## 怎么读这张表

一个能力只有一个拥有者。看到两个仓库都「管」同一件事时，以 `owns` 为准：
`linxira-config-hub` 拥有诊断与设置入口，`linxira-components` 拥有事务与提权执行。
UI 项目（`linxira-package-center`、`linxira-component-manager`）不重新实现提权逻辑。

## 何时需要 root

本页的表本身不需要任何授权。`linxira-wiki` 全部子命令都是只读免 root 的：

```bash
linxira-wiki show ownership
linxira-wiki manifest
```

## 深入设计

各项目的内部设计见其仓库的 `document/` 目录。归属数据的源头是
[`linxira-os/governance/repositories.yaml`](https://github.com/Linxira-OS/linxira-os/blob/master/governance/repositories.yaml)。
