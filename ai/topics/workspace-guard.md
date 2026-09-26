---
name: workspace-guard
summary: 防 agent 误删工作区的恢复点机制
audience: [human, ai]
tools: [linxira-config, linxira-components]
privilege: polkit
---

# 工作区守护

防的是一件事：**agent 用完整用户权限把工作区干掉**，包括 `rm -rf .git`。
恢复点由 root 定时器每 30 分钟独立生成，不依赖 agent 自觉，也不放在用户能改的地方。

## 布局

```
/etc/linxira/workspace-guard.conf     root:root 0600，agent 读不到（这是安全前提）
<独立 ext4 分区>/                     备份介质，不写进 fstab，开机不挂载
  <store>/workspaces/<workspace_id>/registered.json
  <store>/workspaces/<workspace_id>/<snapshot_id>/guard-manifest.json
```

配置不在 fstab 里，所以没有 root 就挂不上备份盘，agent 改不到快照。

## 只读状态（免 root）

```bash
linxira-config workspace-guard status    # 加 --json 给结构化输出
linxira-components guard status          # configured / snapshot_count / workspaces
linxira-components guard list             # 某工作区的快照清单
linxira-components guard list --json
```

未配置时全部安全降级，不报错——未配置是正常状态。

## 用户设置（root 交互，交给用户跑）

```bash
sudo linxira-config workspace-guard enable    # 选盘 → 选容量 → 分区 → 写配置 → 注册 → 开定时器
sudo linxira-config workspace-guard disable   # 只停定时器，保留仓库数据
```

`enable` 幂等：重跑从检测步骤续跑，不会重复分区。中断后直接再跑一次即可。
已创建的分区**不会**被自动删除——删分区表是破坏性操作，只能由用户显式执行。

## agent 能做什么（Polkit 授权）

```bash
linxira-components guard register ~/Linxira-OS     # 注册工作区
linxira-components guard snapshot ~/Linxira-OS     # 立刻做一个手动快照
linxira-components guard restore <id> --target ~/ws-restored
linxira-components guard list ~/Linxira-OS
linxira-components guard unregister ~/Linxira-OS
```

每一条都出 Polkit 弹窗，权限在用户手里。`guard list` / `guard status` 只读，不弹窗。

## 恢复的铁律

**恢复到新目录，绝不就地覆盖。** `restore` 会拒绝这些目标：

- 非绝对路径
- 落在原工作区内部（含等于工作区本身）
- 落在 guard store 内部
- 已存在且非空

```bash
linxira-components guard restore 20260926T041500Z-1a2b3c4d --target ~/ws-restored
ls -a ~/ws-restored          # 有 .git 与你的文件，没有 guard-manifest.json
```

符号链接按链接本身重建，不跟随；`guard-manifest.json` 是守护的元数据，不算用户内容，不出现在恢复结果里。

## 深一层

内部数据结构、restic 仓库布局与保留策略见 `linxira-components` 仓库的 `document/`。
