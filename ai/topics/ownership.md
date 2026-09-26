---
name: ownership
summary: 每个仓库拥有什么，跨项目边界划在哪
audience: [human, ai]
tools: []
privilege: none
---

# 仓库归属与边界

`manifest.json` 的 `repositories[]` 给出全部仓库及其 `owns`（拥有的能力）与 `lifecycle`。
数据源是 `linxira-os/governance/repositories.yaml`，不要凭记忆回答「某功能归谁」。

## lifecycle 怎么读

- `active` — 在维护，功能承诺有效。
- `review-required` — 归属待复核。`linxira-hooks` 是当前唯一一个。
- `independent` — 自有节奏，不随系统发布走。
- `deprecated` — 已被取代，指向 `supersededBy`。不要在新工作里使用。

## 选工具的顺序

1. 装/卸软件、看包状态 → `linxira-components`（唯一有事务计划的入口）
2. 改系统设置、诊断网络与 SSH、镜像源 → `linxira-config`
3. 系统起不来、要证据包、要修复计划 → `linxira-recovery-diagnostics`
4. 查本手册 → `linxira-wiki`

不要跨过 `linxira-config` 直接调 `pacman` 做安装决策：`linxira-components` 才是产出
plan / confirm / receipt 的那个。

## 边界原则

一个能力只有一个拥有者。清单、UI、提权执行三层分属不同仓库时，不要在 UI 仓库里
重新实现提权逻辑，也不要在执行仓库里重新实现策略判断。

具体项目的内部设计见该项目仓库的 `document/` 目录，本手册不复制。
