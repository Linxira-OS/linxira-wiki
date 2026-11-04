# Agent 工作区

## 定义

**Agent 工作区**是 agent 被启动时所在的那个目录：`--cwd` 指向它，
会话与证据都写在它里面。它不是一个全局的临时目录，而是**按子系统划分**的
一处的落点——一个子系统一个工作区，互不混用。

这样划分的原因是证据的归属：崩溃的证据属于崩溃监视，配置变更的证据属于配置侧。
把两者塞进同一个目录，`INDEX.md` 会互相覆盖，`git diff` 也说不清「这次改动是哪个子系统产生的」。

工作区同时还承担会话存储。以交互 lane 启动时，
`--session-dir <ws>/.zeta/sessions` 让会话也落在工作区内，
于是「问了什么、看到了什么」和证据在同一棵目录里，事后可以对照。

## 职责边界

**归它（工作区约定本身）**：

- 规定工作区按子系统划分、只存文本、技能随子系统物化。
- 规定哪些路径算证据（批次目录、`INDEX.md`、`backlog.json`、`mute.json`）、
  哪些算工具状态（`.agents/skills/`、`.zeta/sessions/`）。

**不归它**：

- 不实现工作区：目前唯一的实现方是
  [崩溃监视](linxira-crash-watch.md)，它创建目录、写 `INDEX.md`、物化
  `diagnose-crash` 技能。
- 不定义 agent 的会话格式或恢复逻辑；`--cwd`、`--session-dir` 与 `.zeta/` 的语义属于 Zeta。
- 不做快照或恢复；那是 [工作区守护](workspace-guard.md)。
- 不安装项目技能树；那是 [Agent 技能](agent-skills.md) 里 `linxira-skills` 的职责。

## 怎么用

工作区由创建它的组件给出，不需要用户手工建目录：

```bash
linxira-crash status          # 打印工作区路径、配置与事件计数
linxira-crash investigate <id>  # 在工作区里启动 zetacode（消耗 token）
```

路径在 `~/.config/linxira/crash-watch.toml` 的 `[workspace].path` 配置，
默认 `~/Linxira/debug`。工作区第一次被使用时自动创建为 git 仓库，并写入
`INDEX.md`、`backlog.json`、`mute.json`、`batches/` 与
`.agents/skills/diagnose-crash/SKILL.md`。

## 当前实现

目前**只有一个**实现中的 agent 工作区：崩溃监视的 `~/Linxira/debug`（默认值，
配置项为 `[workspace].path`）。

| 路径 | 作用 |
|---|---|
| `INDEX.md` | 人读索引 |
| `backlog.json` | 机器可读的待处理队列 |
| `mute.json` | 按程序的静音规则 |
| `batches/` | 按批次存放的证据 |
| `.agents/skills/` | 工作区技能，**gitignored** |
| `.zeta/sessions/` | agent 会话记录 |

`.agents/skills/` 被忽略，是因为它属于工具配置而非证据：技能可以按版本重新物化，
崩溃现场不能。`.zeta/sessions/` 则是会话层的数据，同样不当作证据提交。

工作区是 git 仓库，且只存文本。core dump 留在 systemd-coredump 里，
工作区里只有指向它的 `dumpRef`。

## 硬规则

- **一个子系统一个工作区。** 不为「顺手放一下」新建第二个目录，也不把两个子系统的证据并进同一处。
- **不把别的子系统的技能复制进来。** 工作区只带本子系统需要的技能；
  系统级技能留在 `/usr/share/linxira/agent/skills/`，`~/.zeta/agent/skills` 是 Zeta 的用户数据，
  包不得写入。
- **不把 `~/Linxira/debug` 复用于系统与配置类工作。** 它是崩溃证据的目录，
  混入配置改动会让崩溃索引失去意义。
- **只存文本。** 二进制、core dump、大体积转储不进工作区。

## 与工作区守护的区别

两个概念都叫「工作区」，但指的不是一回事：

| | Agent 工作区 | 工作区守护注册的工作区 |
|---|---|---|
| 是什么 | agent 的 `--cwd`，会话与证据的落点 | 用户日常干活的目录 |
| 典型路径 | `~/Linxira/debug` | `$HOME/Linxira-OS`、`$HOME/Projects`、`$HOME/work`、`$HOME/src` |
| 谁在用 | agent | 用户自己 |
| 做什么 | 存证据、跑会话 | 默认由同盘守护定时做快照，供误删后恢复 |

工作区守护登记的是**快照目标**，不是 agent 工作区；反过来，
agent 工作区也没有被守护注册。两者的路径、生命周期与用途都不同，不要互相代入。
守护机制本身见 [工作区守护](workspace-guard.md)。

## 尚未实现

**系统/配置类的 agent 工作区目前没有实现。** 没有任何组件定义「系统工作区」：
`linxira-config-hub` 不注册 agent 工作区，也不启动 agent。

如果将来要加，以下是**约定与计划，不是当前行为**：

- 必须是独立路径，例如 `~/Linxira/system`，不复用 `~/Linxira/debug`；
- 与崩溃工作区不共享 `INDEX.md`、队列或会话目录；
- 同样遵守只存文本、按子系统带技能的规则。

在此之前，系统与配置类工作没有专属的 agent 工作区；
在本页写下的约定落地前，不要自行发明一个路径或复用崩溃工作区。

## 权限

- 工作区在 `$HOME` 下，由用户自己拥有；创建、写入与读取都不需要 root。
- 崩溃监视本身是用户级服务：无特权、不联网、不执行任意 shell。
- 工作区不是特权落点——不要把需要 root 的配置改动塞进去，也不要把它当作提权入口。

## 已知限制

- 只有一个子系统实现了工作区（崩溃监视的 debug 工作区）；系统/配置工作区仍不存在。
- `.agents/skills/` 与 `.zeta/sessions/` 被 gitignore，所以克隆或复制工作区不会带来
  技能与会话；技能可重新物化，会话不随证据归档。
- 只存文本：core dump、二进制与大体积转储都不进工作区，只有指向 systemd-coredump 的
  `dumpRef`。
- 工作区不被工作区守护注册，也就没有定时快照；误删工作区等于丢失证据。
- 布局由实现方决定（`INDEX.md`、`backlog.json`、`mute.json`、`batches/`），本页只记录
  当前唯一实现，不是一个可被任意组件套用的通用目录规范。

## 相关

- [崩溃监视](linxira-crash-watch.md) —— 目前唯一实现了 agent 工作区的子系统
- [Agent 技能](agent-skills.md) —— 技能的作用域、系统技能位置与 `linxira-skills` CLI
- [工作区守护](workspace-guard.md) —— 用户目录的快照与恢复

## 深入设计

工作区布局与分流规则见
[`linxira-crash-watch`](https://github.com/Linxira-OS/linxira-crash-watch)
的 `document/crash-watch-design.md`；实现入口见同仓 `README.md`。
