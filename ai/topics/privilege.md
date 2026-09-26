---
name: privilege
summary: 提权模型 — 任何时候都不要自己提权
audience: [human, ai]
tools: [linxira-components, linxira-config]
privilege: polkit
---

# 提权与权限模型

Linxira 把「要 root 的事」收进一条通道：命令 → plan → 用户确认 → Polkit → root helper → receipt。
agent 永远停在 plan 之前，root 在用户手里。

## 行为约定

这 4 条同样写进 `manifest.json` 的 `privilege_rules`，两处必须逐字一致（CI 校验）：

1. Never invoke sudo, su, doas, or run0 directly.
2. Root work goes through linxira-components; Polkit prompts the user for each action.
3. Read-only commands (list, status, show) never need root.
4. If authorization is denied, stop and report — do not retry or find another path.

## 免授权的部分

`list` / `status` / `show` / `search` / `manifest` 全部只读免 root：

```bash
linxira-wiki manifest
linxira-components guard status
linxira-config workspace-guard status
linxira-config ssh status
linxira-recovery-diagnostics --report-json
```

先跑只读命令拿事实，再决定要不要提权。跳过只读步骤直接申请授权，是最常见的错。

## 需要授权的部分

写系统状态的操作一律走 `linxira-components` 的 plan/confirm/apply，由 Polkit 弹窗。
`linxira-config` 的 `enable` / `on` / `harden` 这类是交互式运维命令，
在本机由 root 执行，**不适合 agent 代替用户发起**——把命令交给用户即可。
