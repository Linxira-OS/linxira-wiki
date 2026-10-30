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
| `.zeta/sessions/` | agent 会话记录，同样不进版本库的证据集 |

`gitignore` 掉 `.agents/skills/` 是有意为之：技能是工具配置，
不属于「这次崩溃发生了什么」的记录。

## 三条 lane

崩溃监视不自己写 agent 的调用逻辑，而是把三种入口固定成三条 lane。
三条 lane 都以同一个工作区为 `--cwd`，区别只在于会话形态与工具权限：

| lane | 命令 | 用途 |
|---|---|---|
| 交互 | `zetacode --cwd <ws> --session-dir <ws>/.zeta/sessions "<PROMPT> @<evidence>"` | 用户在场，边看边问；会话落在工作区里，可续 |
| 批处理 | `zetacode --cwd <ws> --goal "<PROMPT>"` | 一次给目标，跑完即止，用于成批整理证据 |
| 无人值守 | `zetacode --cwd <ws> -p --tools=read,grep,glob,lsp "<PROMPT>"` | 后台跑，工具集**只读**：读、搜、glob、LSP 查询 |

无人值守那条是三条里唯一允许自动跑的，代价是它**不能写**：
`--tools` 只给了 `read`、`grep`、`glob`、`lsp`，没有编辑与执行。
它的产物是结论，不是补丁。

## 技能

工作区里随崩溃监视一起物化的技能只有一个：`diagnose-crash`，
落在 `<ws>/.agents/skills/diagnose-crash/SKILL.md`。它是这个子系统的诊断流程说明，
内容随 crash-watch 的版本一起发布，不由用户手写。

自 0.1.4 起，崩溃监视**不再**把 `linxira-config` 技能复制进工作区。
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

## 深入设计

崩溃分类、队列推进、批次布局与 `dumpRef` 的解析规则见
[crash-watch-design.md](https://github.com/Linxira-OS/linxira-crash-watch/blob/main/document/crash-watch-design.md)。

| 项目 | 仓库 |
|---|---|
| 崩溃监视 | [`linxira-crash-watch`](https://github.com/Linxira-OS/linxira-crash-watch) |
