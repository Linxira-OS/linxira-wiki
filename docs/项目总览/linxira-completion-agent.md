# 完成代理（linxira-completion-agent）

## 为什么存在

安装器会明确把一部分软件延后：需要网络、需要额外许可、或对应的提供者还没实现。
这些条目不能悄无声息地消失——用户需要知道「还有什么没装、为什么、装它会改变什么」。
`linxira-completion-agent` 就是把安装回执里明确延后的软件摊开的那一屏。

它把安装时记录的 catalog 与回执绑定起来，逐项显示来源、大小、许可证、对软件仓库的
影响以及是否可延后。它**不接受**任何软件包名、命令、URL 或仓库定义。

## 职责边界

**归它**：读取安装回执中明确延后的条目、展示来源与许可信息、收集敏感条目的显式确认、
记录延后或完成状态。

**不归它**：

- **不做安装决策**。哪些条目能装、走哪个来源、是否需要接受许可，来自 catalog 与回执。
- **不发包事务**。真正执行时同样经过 [`linxira-components`](linxira-components.md)
  的 `plan → confirm → apply`，提权由 `pkexec` 完成。
- **不处理安装器该做的事**。经过审核的官方 Arch 应用与组件必须在首次启动前就装进
  Calamares 目标环境；回执如果错误地把这类条目交给 Completion，程序会直接拒绝。

## 怎么用

```bash
linxira-completion-agent             # 从应用菜单或终端启动
linxira-completion-agent --autostart # 首次登录自启动条目使用的形式
```

窗口里的表格有六列：软件、来源、大小、许可证、对软件仓库的变更、状态。状态只有
`Ready` 与 `Deferred` 两种；带专有许可或需要 opt-in 的条目下方会出现确认勾选框，
必须逐项勾选。

底部两个动作：

- **Defer**：把当前计划整体标记为延后并关闭窗口。
- **Complete ready items**：仅在网络可用（通过 `nmcli` 的连接检查）、存在 ready 项、
  且所有敏感条目都已勾选时可用。执行时同样在临时目录生成选择文档，调用
  `linxira-components plan`、`confirm`，再以 `pkexec` 执行 `apply`。

固定输入路径是 `/usr/share/linxira/catalog/catalog-v3.json` 与
`/var/lib/linxira/installer-selection.json`。任一是符号链接、回执版本不受支持、
catalog 在回执写入后发生变化、或各项分类互相矛盾时，程序打印原因并以状态码 2 退出。

运行状态写在 `${XDG_STATE_HOME:-$HOME/.local/state}/linxira/completion/state.json`
（`$HOME` 即 home 目录（用户主目录）），其中包含 catalog 与回执的 SHA-256。`--autostart` 启动时，如果上一次的状态是
`complete` 或 `deferred`，程序直接退出；已经成功的条目也不会再次出现。

## 何时需要 root

不需要。代理以普通用户运行，读取 catalog 与回执；真正应用时由 `pkexec` 请求
Polkit 授权。它自己不提权，也不接收 root 命令。

## 已知限制

- **当前实现是查看与延后面板**：所有回执延后条目都被归类为 `Deferred`
  （可执行标志恒为 false），因此 **Complete ready items 始终不可用**。
  `plan/confirm/apply` 的代码路径存在，但现阶段没有条目会走到它。
- 只展示回执 `pendingItems` 里列出的叶子；其余已安装或未选择的条目不会出现。
- operation 类叶子要等其专用系统动作实现；AUR、Flatpak、Conda、专有软件与
  审阅渠道条目各自等待 provider 与审阅契约。
- 只接受 Catalog v3 与 `org.linxira.installer.selection-receipt.v1` 回执；
  回执必须完整分类每个被选条目，否则拒绝启动。
- 不负责安装官方 reviewed Arch 应用与组件——那是安装器的职责，延后它们会被视为错误。

## 深入设计

回执与 catalog 的绑定规则、条目分类与状态文件格式见
[`linxira-completion-agent`](https://github.com/Linxira-OS/linxira-completion-agent)
仓库；事务形状见 [Components](linxira-components.md)。
