# 工作区守护（workspace-guard）

## 为什么存在

agent 在用户的工作区里以**完整的用户权限**运行。它能 `rm -rf` 一个目录，
也能 `rm -rf .git`——后者更隐蔽，因为它看起来像一次普通的清理。
一旦工作区没了，用户的代码、提交历史、未推送的分支一起没了，而且往往没有第二份。

这个机制不试图让 agent 更小心。它假设 agent 会犯错，然后在**用户权限之外**
留一层独立恢复点：root 定时器每 30 分钟做一次快照，写在一块 agent 够不着的介质上。

## 职责边界

这是一个跨项目机制，横跨四个仓库：

| 部分 | 归属 | 内容 |
|---|---|---|
| 快照与恢复的执行 | [`linxira-components`](linxira-components.md) | `guard_store` / `guard_worker` / `guard_cli` / 定时器 |
| 分区、容量选择、启用 | [`linxira-config`](linxira-config.md) | `linxira-config workspace-guard enable` |
| 装机时创建分区 | [`linxira-iso-direct`](https://github.com/Linxira-OS/linxira-iso-direct) | Calamares `workspaceGuard` 段 |
| 文档 | 本 wiki | 本页与 `ai/topics/workspace-guard.md` |

**不归它**：不备份系统本身（那是 timeshift 的事），不备份用户主目录整体，
不做增量同步或实时监控。它只做「把已注册工作区的完整快照按策略保留下来」。

## 怎么用

### 启用（root，用户交互）

```bash
sudo linxira-config workspace-guard enable
```

四步引导：选目标盘 → 选容量（32 / 64 / 128 GB 或自定义，最小 32 GB）→
创建 ext4 分区并写配置 → 注册工作区并开启定时器。整条命令是幂等的，
中途 Ctrl-C 后重跑会从检测步骤续跑，不会重复分区。

```bash
sudo linxira-config workspace-guard disable   # 只停定时器，保留仓库数据
```

已创建的分区**不会**被自动删除。删除分区表是破坏性操作，只能由用户显式执行。

### 日常（agent 可用，免授权部分）

```bash
linxira-config workspace-guard status
linxira-config workspace-guard status --json
linxira-components guard status
linxira-components guard list ~/Linxira-OS
linxira-components guard list ~/Linxira-OS --json
```

未配置时这些命令安全降级，不报错——未配置是正常状态。

### 恢复点操作（Polkit 授权）

```bash
linxira-components guard register ~/Linxira-OS
linxira-components guard snapshot ~/Linxira-OS
linxira-components guard restore <id> --target ~/ws-restored
linxira-components guard unregister ~/Linxira-OS
```

## 何时需要 root

- **不需要**：`workspace-guard status`、`handbook`、`guard status`、`guard list`。
- **需要**：`workspace-guard enable` / `disable`（root 直接执行）、
  `guard init` / `register` / `unregister` / `snapshot` / `restore`（Polkit 弹窗）。
- **定时器**：`linxira-workspace-guard-snapshot.timer` 以 root 身份每 30 分钟跑一次，
  不依赖 agent 自觉，也不依赖用户在场。

## 三条不变量

1. **配置 agent 读不到。** `/etc/linxira/workspace-guard.conf` 是 `root:root 0600`。
   这是安全前提，不是可配置项——不提供把它放到用户可读位置的选项。
2. **恢复不覆盖。** `restore` 永远写入新目录，落在原工作区内、落在守护仓库内、
   已存在且非空的目标全部拒绝。原工作区一个字节都不会动。
3. **备份盘开机不挂载。** 守护分区不写进 `/etc/fstab`。没有 root 就挂不上，
   agent 也就无法修改或删除已有的快照。

## 深入设计

数据结构、保留策略与 restic 仓库布局见
[`linxira-components`](https://github.com/Linxira-OS/linxira-components) 仓库的 `document/` 目录。
机器可读摘要见 `linxira-wiki show workspace-guard`。
