# Agent 技能（skills）

## 为什么存在

技能是给 agent 的**上下文**，不是给程序的配置。一个 `SKILL.md` 说明某个子系统的
流程、边界与命令；agent 打开对应目录时读到它，就知道该怎么干活，不必让用户每次重复交代。

技能一旦被发现就会进入上下文，因此它是有成本的。放在哪个作用域，决定了
「谁会看到它、要为它付多少 token」。所以这里的原则不是「能装就装」，
而是**装在该看到它的那一层**。

## 职责边界

**归 `linxira-skills`**：

- 可执行文件 `linxira-skills`：`init` / `status` / `update` / `uninstall`。
- profile 与 payload：把选定的 profile 物化成 `.agents/skills/` 下的三级路由树，
  并生成 `.linxira/manifest.json` 与 `AGENTS.md` 标记块。
- 每个 profile 的技能清单、来源与许可记录（`THIRD_PARTY_NOTICES.md`、`docs/SOURCES.md`）。

**不归它**：

- 运行时如何发现技能；那是 Zeta 的 provider 优先级与开关。
- 系统技能目录的安装；那由发行包的 PKGBUILD 完成。
- 工作区技能的物化；那由组件自己完成（目前是崩溃监视）。
- 生成 agent 会话或执行技能内容。

## 已实现的作用域

| 作用域 | 路径 | 谁安装 | 谁能看到 |
|---|---|---|---|
| 系统 | `/usr/share/linxira/agent/skills/<name>/SKILL.md` | 发行包（PKGBUILD） | 全系统；包拥有、只读，随包升级 |
| 工作区 | `<ws>/.agents/skills/<name>/SKILL.md` | 组件在创建工作区时物化 | 只在该工作区（agent 的 `--cwd`）内；`.agents/skills/` 被 gitignore |
| 项目 | `<repo>/.agents/skills/` | `linxira-skills init` | 只在该仓库；同时生成 `.linxira/manifest.json` 与 `AGENTS.md` 标记块 |

**`linxira-skills` 没有用户作用域的安装入口。** `~/.agents/skills/` 是 Zeta 的 `agents`
provider 会扫描的用户级目录，但只有在 Zeta 打开 `enableAgentsUser` 时才加载；
`linxira-skills` 不会往那里写任何东西，安装包也不得写入。需要跨项目复用的技能，
目前只能由用户自行放置并承担上下文成本。

当前的实际内容很少，这是有意的：

- **系统作用域目前只有一个技能**：`linxira-config`，由 `linxira-config-hub`
  的 PKGBUILD 安装。配套清单 `/usr/share/linxira/agent/capabilities.json`
  记录它能做什么、哪些命令需要 root。
- **工作区作用域目前也只有一个**：崩溃监视物化的 `diagnose-crash`。
- 项目作用域由用户自己决定装哪个 profile，系统不预置。

!!! note "布局是一层，不是一棵树"
    Zeta 的 provider 发现只看 `<skills-root>/<name>/SKILL.md` 这一层；写成
    `<skills-root>/<group>/<name>/SKILL.md` 的嵌套结构不会被默认加载。
    `linxira-skills` 因此把三级路由树放在 `.agents/skills/` 下，并用生成的
    `AGENTS.md` 标记块与相对 `INDEX.md` 链接把 agent 从 router 带到 index、再到叶子，
    而不是依赖递归扫描。

## 谁可以写哪里

| 写入方 | 可以写 | 不可以写 |
|---|---|---|
| 发行包（PKGBUILD） | 系统技能目录与 `capabilities.json` | `~/.zeta/agent/skills`、`~/.agents/skills`、任何用户目录 |
| 组件（如崩溃监视） | 只把自己那一个技能物化进自己的工作区 | 别的子系统的技能、系统技能目录 |
| `linxira-skills` CLI | 目标 Git 仓库的项目作用域（`.agents/skills/`、`.linxira/manifest.json`、`AGENTS.md` 标记块） | 系统技能目录、`~/.agents/skills`、`~/.zeta/agent/skills` |
| 用户 | 任何作用域，但项目作用域应通过 CLI 安装，便于追踪与卸载 | — |

!!! warning "包不得写用户作用域"
    `~/.agents/skills` 属于用户，不属于包。包往里写会让一份技能出现在用户的
    每个项目里，用户既没有选择过，也无法通过 `linxira-skills uninstall` 干净移除。
    `~/.zeta/agent/skills` 同理——那是 Zeta 自己的用户数据，包不得写入。

## 为什么默认项目作用域

用户级技能对**每个项目**可见：在任何仓库里启动 agent，只要开关打开，它都会被加载，
哪怕这次任务完全用不上。这既是上下文成本，也是名字冲突的来源——
同一个技能名在多个来源出现时，只有优先级最高的那一份生效，排查起来很不直观。

项目作用域没有这个问题：技能跟着用得上它的仓库走，换项目就自然消失，而且
`uninstall` 能把受管目录清干净。home 目录也不是仓库，不该被塞进 `AGENTS.md`
标记块或 `.gitignore` 条目——这也是 CLI 只在 Git 仓库里工作的原因之一。

## 发现顺序

Zeta 启动时按 provider 优先级依次加载技能，**同名先到先得**：

1. 原生 `.zeta` 技能（用户级与项目级，优先级 100）；
2. `zeta-plugins`（90），然后是 `claude`（80）、`claude-plugins` / `agents` / `codex`（70 组）；
3. `opencode`（55）、`github`（30）；
4. 最后是 Zeta 的自动学习（managed）技能（5），它总是让位于同名的作者技能。

结果就是：原生的 `.zeta` 版本会盖过同名的 `.agents` 版本；而 `.agents/`
这一层正是 `linxira-skills` 与各组件物化技能的地方。系统技能目录不在默认扫描
路径里，它通过 `capabilities.json` 的 `skill` 字段被显式引用——agent 读清单就能找到它。

`agents` provider 有自己的用户级与项目级开关（`enableAgentsUser` /
`enableAgentsProject`）；关闭 Claude、Codex 等 provider 不会连带关闭它。

## 命令

```bash
# 项目作用域（唯一支持的作用域）：在目标 Git 仓库内运行
npx @linxiraos/linxira-skills init
npx @linxiraos/linxira-skills init --profile core
npx @linxiraos/linxira-skills init --layout namespaced   # 默认；router 落在 .agents/skills/linxira-<root>/
npx @linxiraos/linxira-skills init --layout flat         # router 落在 .agents/skills/<root>/

# 查看、升级、卸载：跟随 manifest 记录的 profile 与布局
npx @linxiraos/linxira-skills status
npx @linxiraos/linxira-skills update [--force]
npx @linxiraos/linxira-skills uninstall [--force]
```

`init`、`update`、`uninstall` 都支持 `--dry-run`。`update` 只更新 manifest 记录且
未被改动过的条目，遇到用户修改会要求 `--force`。`status` / `update` / `uninstall`
读取安装时写下的 `.linxira/manifest.json`，因此换过 `--layout` 不需要手工清理旧目录。

profile：

- `core`（默认）：10 个一方软件、完整性、Linux、传输与计算技能。
- `bioinformatics-core`：`core` 加 10 个一方生物信息与 bulk RNA-seq 技能。
- `biology-research-core`：在上一级之上加 19 个生物学发现、实验设计、湿实验治理与
  学术交付技能。
- `science-research-core`：再扩展化学、物理、作物/植物、生态、动物生理、生化与
  医学/转化研究设计。
- `research-communication-core`：`core` 加 44 个文稿、引用、排版、图表、文档、LaTeX、
  演示与中文科研文档技能（含 vendored 的 Apache-2.0 / MIT 改编，见
  `THIRD_PARTY_NOTICES.md`）。

!!! note "尚未发布到 npm"
    安装架构文档标注该包**尚未发布到 npm**。上面的 `npx` 形式以发布为前提；
    在发布之前只能使用本地构建的包，不要假定 `@linxiraos/linxira-skills` 已可下载。

## 分离规则

系统管理类技能（如 `linxira-config`）**留在系统目录，不复制进工作区**。

工作区只物化本子系统需要的那一个技能。自 crash-watch 0.1.4 起，崩溃监视不再把
`linxira-config` 复制进调试工作区：同一份技能存在两个副本会随时间漂移，
而系统技能随包升级，工作区副本不会。要让 agent 知道系统配置能力，应该读系统技能，
而不是在每个工作区里养一份过期副本。

## 权限

- `linxira-skills` 不需要 root，也不调用 `sudo`；它只在目标 Git 仓库内写受管文件。
- 系统技能由包管理器以 root 安装，属于普通系统升级路径。
- 组件物化工作区技能用的是用户自己的权限，不提升。

## 已知限制

- `init` 必须在 Git 仓库（或其子目录）里运行；非 Git 目录会直接报错。
- 已初始化的仓库再次 `init` 会报错，要求改用 `update` 或 `uninstall`。
- `linxira-skills` 没有用户作用域安装入口；`~/.agents/skills` 是否被加载取决于 Zeta 的
  `enableAgentsUser` 开关，手工放到那里也不等于一定生效。
- 系统技能目录不在 Zeta 的默认扫描路径中，只能通过 `capabilities.json` 的
  `skill` 字段被引用。
- 技能发现只看一层目录；嵌套目录必须靠 router 与 `AGENTS.md` 引导，而不是自动扫描。
- CLI 不运行 `git add`、不修改源码 submodule、不抓取上游、不发网络请求。
- 只有列出的五个 profile；未通过评审的第三方内容不进入可安装 payload。

## 深入设计

- 安装器与布局：[`linxira-skills`](https://github.com/Linxira-OS/linxira-skills)
  仓库的 `docs/INSTALLATION_ARCHITECTURE.md` 与 `docs/SKILL_LOADING_POLICY.md`。
- 工作区物化：`linxira-crash-watch` 仓库的 `src/linxira_crash_watch/workspace.py`。
- 系统技能与清单：`linxira-config-hub` 仓库的 `agent/` 目录。
