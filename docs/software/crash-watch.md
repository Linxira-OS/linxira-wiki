# 崩溃监视（crash-watch）

## 为什么存在

桌面上的崩溃是**看不见的**。一个程序被信号打死，窗口直接消失；内核或服务段错误，
只在 `journalctl` 里留下几行，用户不会去看。等到有人想起去查，现场已经被重启、
日志滚屏、升级覆盖掉了。

崩溃监视解决的是「现场留存」，不是「修复」。它在崩溃发生的那一刻就把证据写成文本，
放进一个可以事后翻阅、也可以交给 agent 的目录。这一步不需要模型参与，
因此**捕获本身不花任何 token**。

抓完证据就停下。只有用户在通知里**显式选了一个动作**，才会有一个 agent 被唤起。

## 职责边界

| 负责 | 具体内容 |
|---|---|
| 捕获 | 监视 systemd-coredump 的新条目，记录崩溃的程序、信号、时间与 `dumpRef` |
| 初筛 | 判断这次崩溃是否值得进队列，抑制重复与已知噪声 |
| 写工作区 | 把文本证据写进调试工作区，维护索引与待办队列 |
| 通知 | 用 `notify-send` 发出带动作按钮的通知，把「要不要看」交给用户 |

| 不负责 | 原因 |
|---|---|
| 自动修复 | 崩溃大多需要人判断；自动改配置会把一次崩溃变成一次事故 |
| 自动唤起 agent | 捕获与诊断解耦，没有用户动作就不消耗算力，也不产生误改 |
| 拥有系统配置 | 配置的读写入口属于 `linxira-config`，崩溃监视只读它的诊断信息 |
| 保存 core dump | 转储体留在 systemd-coredump 里，工作区只保存引用（`dumpRef`） |

## 工作区

工作区默认在 `~/Linxira/debug`，可通过配置项 `[workspace].path` 更改。
它是一个 **git 仓库，且只存放文本**：索引、队列、日志摘录、命令输出。
二进制与 core dump 不进工作区，所以仓库可以放心提交、对比、回溯。

| 路径 | 作用 |
|---|---|
| `INDEX.md` | 人读的崩溃索引，按时间排列，指向各批次的证据 |
| `backlog.json` | 机器可读的待处理队列 |
| `mute.json` | 按程序的静音规则 |
| `batches/` | 按批次组织的证据文件，一批一次崩溃事件 |
| `.agents/skills/<name>/SKILL.md` | 工作区自带的技能，`gitignored`（属工具，不是证据） |
| `.zeta/sessions/` | agent 会话记录；不是崩溃证据，但未被 `.gitignore` 忽略 |

`gitignore` 掉 `.agents/skills/` 是有意为之：技能是工具配置，
不属于「这次崩溃发生了什么」的记录。`.zeta/sessions/` 目前**不在**忽略列表里，
提交工作区前要自己确认没有把会话记录带进去。工作区第一次被创建时会执行 `git init`，
并补齐 `INDEX.md`、`backlog.json`、`mute.json` 与 `.gitignore`。

配置文件是 `~/.config/linxira/crash-watch.toml`：

```toml
[workspace]
path = "~/Linxira/debug"

[triage]
timeout          = "6h"
repeat_threshold = 3

[escalate]
driver_related = true

[lane.unattended]
enabled  = false
schedule = "04:00"
tools    = "read,grep,glob,lsp"
```

## 怎么用

后台捕获由用户服务 `linxira-crash-watch.service` 承担，preset 在首次登录时启用；
它运行 `linxira-crash daemon --interval 60`。日常操作都在同一个 CLI 里：

```bash
linxira-crash status                    # 工作区、超时、无人值守开关、事件计数
linxira-crash list --state pending      # 按状态列出事件
linxira-crash pin <id>                  # 只进 backlog，0 token
linxira-crash ignore <id>               # 忽略，可加 --reason
linxira-crash restore <id>              # 撤销分流，回到 pending
linxira-crash mute <program>            # 按程序静音（--list / --off <program>）
linxira-crash investigate <id>          # 启动 zetacode（会花 token）
linxira-crash investigate <id> --dry-run # 只打印将要执行的命令
```

应用菜单的「Linxira Crash Watch」执行 `linxira-crash status`。`status`、`list`、
`pin`、`ignore`、`restore`、`mute` 都不花 token，也可以离线使用；
只有 `investigate` 会启动 agent。

## 三条 lane

崩溃监视不自己写 agent 的调用逻辑，而是把三种入口固定成三条 lane。
三条 lane 都以同一个工作区为 `--cwd`，区别只在于会话形态与工具权限。
只有交互 lane 接在通知与 `linxira-crash investigate` 上；另外两条是固定的命令形状，
需要时手动执行：

| lane | 命令 | 用途 |
|---|---|---|
| 交互 | `zetacode --cwd <ws> --session-dir <ws>/.zeta/sessions "<PROMPT> @<evidence>"` | 用户在场，边看边问；会话落在工作区里，可续 |
| 批处理 | `zetacode --cwd <ws> -p "<PROMPT>"` | 打印模式，一次给目标，跑完即止，用于成批整理证据 |
| 无人值守 | `zetacode --cwd <ws> -p --tools=read,grep,glob,lsp "<PROMPT>"` | 无人值守形状，工具集**只读**：读、搜、glob、LSP 查询 |

crash-watch 源码里的批处理 lane 写的是 `--goal`，但当前 Zetacode CLI 没有这个开关；
本页因此给出可用的 `-p` 打印模式。无人值守 lane 默认关闭，由 `[lane.unattended].enabled` 控制；即便开启，它的
`--tools` 也只给 `read`、`grep`、`glob`、`lsp`，没有编辑与执行——产物是结论，不是补丁。
当前版本没有调度器会自己启动这条 lane：通知和 `investigate` 走的都是交互 lane。
`schedule` 键会被读取，但不会触发运行。

## 技能

工作区里随崩溃监视一起物化的技能只有一个：`diagnose-crash`，
落在 `<ws>/.agents/skills/diagnose-crash/SKILL.md`。它是这个子系统的诊断流程说明，
内容随 crash-watch 的版本一起发布，不由用户手写。

当前版本**不再**把 `linxira-config` 技能复制进工作区。
系统级技能留在系统位置，工作区只放与这个子系统相关的那一个：

- 系统技能：`/usr/share/linxira/agent/skills/<name>/SKILL.md`
  （目前只有 `linxira-config`，由 `linxira-config-hub` 的 PKGBUILD 安装）
- 配套清单：`/usr/share/linxira/agent/capabilities.json`

技能的作用域、安装方式与 `linxira-skills` CLI 见 [Agent 技能](agent-skills.md)。
工作区本身是什么、为什么按子系统划分见 [Agent 工作区](agent-workspace.md)。

## 交互

通知用 `notify-send` 发出，带四个固定动作：调查、复制提示词、固定、静音。
**在用户点下按钮之前，什么都不会运行**——没有后台 agent，没有预先写好的补丁。

静音是**按程序**的：`mute.json` 里记录的是程序名，不是这次崩溃。
一个已知会崩的第三方程序被静音后，它的新崩溃不再弹通知，
但记录仍按策略写入工作区，需要时还能翻出来。

## 何时需要 root

**从不需要。** 捕获端是**无特权用户服务**：`NoNewPrivileges`、`ProtectHome=read-only`、
只允许 `AF_UNIX` 地址族，可写路径只有 `%h/Linxira` 与 `%h/.local/state/linxira-crash-watch`。

- `linxira-crash` 的全部子命令都以当前用户运行；`investigate` 也是以当前用户启动
  `zetacode`，工作区在用户主目录里。
- 原始 core dump 留在 `systemd-coredump` 的存储里，工作区只保存引用；抓取不需要读
  root 文件，也不需要 `journalctl` 提权。
- 没有任何上传：分析纯本地，不联网、不自动向上游报 bug。

## 已知限制

- 只捕获 `systemd-coredump` 的新条目；没有经过 coredump 的崩溃（例如被 OOM killer
  直接杀掉的进程）不会出现在队列里。
- 通知依赖 `notify-send`；没有通知守护进程时通知退化为空操作，捕获与分流照常进行。
- 静音按程序名记录在 `mute.json`，不是按单次崩溃；被静音的后续崩溃仍按策略写入工作区。
- 自动分流只在超时后改变状态，永不唤醒 agent；每条决策可用 `restore` 撤销。
- 无人值守 lane 不会自动运行（见上），`schedule` 目前只是配置字段。
- 工作区只存文本；core dump 本体不会被复制进来，事后复查需要 `dumpRef` 指向的原始转储仍在。
- `.zeta/sessions/` 不在 `.gitignore` 里；提交工作区前要确认没有把 agent 会话记录一起提交。

## 深入设计

崩溃分类、队列推进、批次布局与 `dumpRef` 的解析规则见
[crash-watch-design.md](https://github.com/Linxira-OS/linxira-crash-watch/blob/main/document/crash-watch-design.md)。

| 项目 | 仓库 |
|---|---|
| 崩溃监视 | [`linxira-crash-watch`](https://github.com/Linxira-OS/linxira-crash-watch) |
