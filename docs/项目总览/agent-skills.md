# Agent 技能（skills）

## 为什么存在

技能是给 agent 的**上下文**，不是给程序的配置。一个 `SKILL.md` 说明某个子系统的
流程、边界与命令；agent 打开对应目录时读到它，就知道该怎么干活，不必让用户每次重复交代。

技能一旦被发现就会进入上下文，因此它是有成本的。放在哪个作用域，决定了
「谁会看到它、要为它付多少 token」。所以这里的原则不是「能装就装」，
而是**装在该看到它的那一层**。

## 四个作用域

| 作用域 | 路径 | 谁安装 | 谁能看到 |
|---|---|---|---|
| 系统 | `/usr/share/linxira/agent/skills/<name>/SKILL.md` | 发行包（PKGBUILD） | 全系统；包拥有、只读，随包升级 |
| 工作区 | `<ws>/.agents/skills/<name>/SKILL.md` | 组件在创建工作区时物化 | 只在该工作区（agent 的 `--cwd`）内；`.agents/skills/` 被 gitignore |
| 项目 | `<repo>/.agents/skills/` | `linxira-skills init` | 只在该仓库；同时生成 `.linxira/manifest.json` 与 `AGENTS.md` 标记块 |
| 用户 | `~/.agents/skills/` | `linxira-skills init --user` | 该用户的**所有**项目；需显式 opt-in |

当前的实际内容很少，这是有意的：

- **系统作用域目前只有一个技能**：`linxira-config`，由 `linxira-config-hub`
  的 PKGBUILD 安装。配套清单 `/usr/share/linxira/agent/capabilities.json`
  记录它能做什么、哪些命令需要 root。
- **工作区作用域目前也只有一个**：崩溃监视物化的 `diagnose-crash`。
- 项目与用户作用域由用户自己决定装什么，系统不预置。

!!! note "布局是一层，不是一棵树"
    目录型作用域（`.zeta`、`.agents` 等）都按 `<skills-root>/<name>/SKILL.md` 发现，只扫描一层。
    写成 `<skills-root>/<group>/<name>/SKILL.md` 的嵌套结构不会被默认加载；
    `linxira-skills` 用 router 索引绕开这一点，而不是靠递归扫描。

## 谁可以写哪里

| 写入方 | 可以写 | 不可以写 |
|---|---|---|
| 发行包（PKGBUILD） | 系统技能目录与 `capabilities.json` | `~/.zeta/agent/skills`、`~/.agents/skills`、任何用户目录 |
| 组件（如崩溃监视） | 只把自己那一个技能物化进自己的工作区 | 别的子系统的技能、系统技能目录 |
| `linxira-skills` CLI | 项目作用域（`.agents/skills/`、`.linxira/manifest.json`、`AGENTS.md` 标记块）与用户作用域（`~/.agents/skills/`、`~/.agents/linxira-skills.json`） | 系统技能目录 |
| 用户 | 任何作用域，但项目/用户作用域应通过 CLI 安装，便于追踪与卸载 | — |

!!! warning "包不得写用户作用域"
    `~/.agents/skills` 属于用户，不属于包。包往里写会让一份技能出现在用户的
    每个项目里，用户既没有选择过，也无法通过 `linxira-skills uninstall` 干净移除。
    `~/.zeta/agent/skills` 同理——那是 Zeta 自己的用户数据，包不得写入。

## 为什么不默认全局

用户作用域的技能对**每个项目**可见：在任何仓库里启动 agent，它都会被加载，
哪怕这次任务完全用不上。这既是上下文成本，也是名字冲突的来源——
同一个技能名在多个来源出现时，只有优先级最高的那一份生效，排查起来很不直观。

因此默认推荐**项目作用域**：技能跟着用得上它的仓库走，换项目就自然消失。
只有确实跨项目复用的技能才值得装到用户作用域，`init --user` 也会为此打印
上下文成本警告。用户级安装还不创建 `AGENTS.md` 或 `.gitignore`：
家目录不是仓库，不该被塞进项目标记文件。

## 发现顺序

Zeta 启动时按 provider 的优先级依次加载技能，**同名先到先得**：

1. 原生 `.zeta` 技能（用户级与项目级）优先；
2. 其后是插件与各家 provider 目录，包括 `.agents/skills/`、Claude、Codex 等；
3. 最后是 Zeta 的自动学习（managed）技能，它总是让位于同名的作者技能。

结果就是：原生的 `.zeta` 版本会盖过同名的 `.agents` 版本；而 `.agents/`
这一层正是 `linxira-skills` 与各组件物化技能的地方。系统技能目录不在默认扫描
路径里，它通过 `capabilities.json` 的 `skill` 字段被显式引用——agent 读清单就能找到它。

用户级技能是否生效还取决于运行时的用户级开关，装到家目录不等于一定被加载。

## 命令

```bash
# 项目作用域（默认）：<repo>/.agents/skills/ + .linxira/manifest.json + AGENTS.md 标记块
linxira-skills init
linxira-skills init --profile core
linxira-skills init --layout namespaced   # 默认，router 落在 .agents/skills/linxira-<root>/
linxira-skills init --layout flat         # router 落在 .agents/skills/<root>/

# 用户作用域（opt-in）：~/.agents/skills/ + ~/.agents/linxira-skills.json
linxira-skills init --user
linxira-skills init --global              # 与 --user 等价

# 查看、升级、卸载：跟随 manifest 记录的 profile 与布局
linxira-skills status
linxira-skills update
linxira-skills uninstall
```

`linxira-skills` 来自 npm 包 `@linxiraos/linxira-skills`，也可以在仓库里通过
`npx @linxiraos/linxira-skills init` 调用。`status` / `update` / `uninstall`
读取安装时写下的 manifest，因此换过 `--layout` 或 `--profile` 之后不需要手工清理旧目录。

!!! note "`LINXIRA_SKILLS_HOME`"
    设置该环境变量可以改写用户作用域的根（默认是当前家目录），
    用于测试与隔离，避免动到真实家目录。它不是让包把技能装到别处的开关。

## 分离规则

系统管理类技能（如 `linxira-config`）**留在系统目录，不复制进工作区**。

工作区只物化本子系统需要的那一个技能。自 crash-watch 0.1.4 起，崩溃监视不再把
`linxira-config` 复制进调试工作区：同一份技能存在两个副本会随时间漂移，
而系统副本随包升级，复制品不会。要让 agent 知道系统配置能力，应该读系统技能，
而不是在每个工作区里养一份过期的拷贝。

工作区本身是什么、为什么按子系统划分见 [Agent 工作区](agent-workspace.md)；
崩溃监视的工作区布局与技能见 [崩溃监视](linxira-crash-watch.md)。

## 深入设计

- 安装器与布局：[`linxira-skills`](https://github.com/Linxira-OS/linxira-skills)
  仓库的 `docs/INSTALLATION_ARCHITECTURE.md` 与 `docs/SKILL_LOADING_POLICY.md`。
- 工作区物化：`linxira-crash-watch` 仓库 `src/linxira_crash_watch/workspace.py`。
- 系统技能与清单：`linxira-config-hub` 仓库 `agent/` 目录。
