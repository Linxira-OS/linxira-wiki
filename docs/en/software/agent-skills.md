# Agent Skills (skills)

## Why it exists

A skill is **context** for an agent, not configuration for a program. A `SKILL.md` explains a subsystem's procedure, boundaries and commands; when the agent opens the corresponding directory and reads it, it knows how to work without the user repeating the briefing every time.

Once discovered, a skill enters the context, so it has a cost. Which scope it sits in decides who sees it and how many tokens they pay for it. The principle is therefore not "install whatever will install" but **install it at the layer that should see it**.

## The four scopes

| Scope | Path | Installed by | Visible to |
|---|---|---|---|
| System | `/usr/share/linxira/agent/skills/<name>/SKILL.md` | distribution package (PKGBUILD) | the whole system; package-owned, read-only, upgraded with the package |
| Workspace | `<ws>/.agents/skills/<name>/SKILL.md` | materialised by a component when it creates the workspace | only inside that workspace (the agent's `--cwd`); `.agents/skills/` is gitignored |
| Project | `<repo>/.agents/skills/` | `linxira-skills init` | only that repository; also generates `.linxira/manifest.json` and the `AGENTS.md` marker block |
| User | `~/.agents/skills/` | `linxira-skills init --user` | **every** project of that user; requires an explicit opt-in |

What actually exists today is deliberately little:

- **The system scope has a single skill**: `linxira-config`, installed by the `linxira-config-hub` PKGBUILD. Its companion manifest `/usr/share/linxira/agent/capabilities.json` records what it can do and which commands need root.
- **The workspace scope also has a single one**: `diagnose-crash`, materialised by Crash Watch.
- The project and user scopes hold whatever the user decides to install; the system pre-installs nothing there.

!!! note "Layout is one layer, not a tree"
    Directory scopes (`.zeta`, `.agents` and so on) all discover skills as `<skills-root>/<name>/SKILL.md`, scanning a single layer. A nested `<skills-root>/<group>/<name>/SKILL.md` is not loaded by default; `linxira-skills` sidesteps this with a router index instead of recursive scanning.

## Who may write where

| Writer | May write | Must not write |
|---|---|---|
| Distribution package (PKGBUILD) | the system skill directory and `capabilities.json` | `~/.zeta/agent/skills`, `~/.agents/skills`, any user directory |
| Components (e.g. Crash Watch) | only its own single skill, into its own workspace | other subsystems' skills, the system skill directory |
| `linxira-skills` CLI | the project scope (`.agents/skills/`, `.linxira/manifest.json`, the `AGENTS.md` marker block) and the user scope (`~/.agents/skills/`, `~/.agents/linxira-skills.json`) | the system skill directory |
| The user | any scope, though project and user scopes should be installed through the CLI so they stay traceable and uninstallable | — |

!!! warning "Packages must not write the user scope"
    `~/.agents/skills` belongs to the user, not to a package. A package writing there makes one skill appear in every one of the user's projects — a skill the user never chose and cannot cleanly remove with `linxira-skills uninstall`. `~/.zeta/agent/skills` is the same story: it is Zeta's own user data, and packages must not write to it.

## Why not global by default

A user-scope skill is visible to **every project**: started in any repository, the agent loads it even when the task does not need it. That is context cost, and it is also where name collisions come from — when the same skill name exists in several sources only the highest-priority copy wins, which is not intuitive to debug.

The default recommendation is therefore the **project scope**: the skill travels with the repository that needs it and disappears when you switch projects. Only skills genuinely reused across projects are worth installing at user scope, which is why `init --user` prints a context-cost warning. User-level installation also creates no `AGENTS.md` or `.gitignore`: the home directory is not a repository and should not be filled with project marker files.

## Discovery order

At startup Zeta loads skills in provider priority order, **first come, first served for a given name**:

1. native `.zeta` skills (user and project level) come first;
2. then plugins and the various provider directories, including `.agents/skills/`, Claude, Codex and so on;
3. finally Zeta's auto-learned (managed) skills, which always yield to an authored skill of the same name.

The outcome: a native `.zeta` version beats a same-named `.agents` version, and `.agents/` is exactly where `linxira-skills` and the components materialise skills. The system skill directory is not on the default scan path; it is referenced explicitly through the `skill` field of `capabilities.json`, so an agent that reads the manifest can find it.

Whether user-level skills take effect also depends on the runtime's user-level switch; installing into the home directory does not guarantee that they are loaded.

## Commands

```bash
# project scope (default): <repo>/.agents/skills/ + .linxira/manifest.json + AGENTS.md marker block
linxira-skills init
linxira-skills init --profile core
linxira-skills init --layout namespaced   # default; routers land in .agents/skills/linxira-<root>/
linxira-skills init --layout flat         # routers land in .agents/skills/<root>/

# user scope (opt-in): ~/.agents/skills/ + ~/.agents/linxira-skills.json
linxira-skills init --user
linxira-skills init --global              # equivalent to --user

# inspect, update, uninstall: follow the profile and layout recorded in the manifest
linxira-skills status
linxira-skills update
linxira-skills uninstall
```

`linxira-skills` comes from the npm package `@linxiraos/linxira-skills` and can also be called from a repository with `npx @linxiraos/linxira-skills init`. `status` / `update` / `uninstall` read the manifest written at install time, so after changing `--layout` or `--profile` there is no old directory to clean up by hand.

!!! note "`LINXIRA_SKILLS_HOME`"
    Setting this environment variable overrides the root of the user scope (the current home directory by default). It exists for tests and isolation, so the real home directory is left alone; it is not a switch for packages to install skills somewhere else.

## Separation rule

System-management skills (such as `linxira-config`) **stay in the system directory and are not copied into workspaces**.

A workspace materialises only the single skill its own subsystem needs. Since crash-watch 0.1.4, Crash Watch no longer copies `linxira-config` into the debug workspace: two copies of one skill drift apart over time, and the system skill is upgraded with its package while a workspace copy is not. To tell an agent about system-configuration capability, read the system skill instead of keeping a stale copy in every workspace.

See [Agent Workspace](agent-workspace.md) for what a workspace is and why it is split per subsystem, and [Crash Watch](crash-watch.md) for the crash workspace layout and its skill.

## Deeper design

- Installer and layout: `docs/INSTALLATION_ARCHITECTURE.md` and `docs/SKILL_LOADING_POLICY.md` in the [`linxira-skills`](https://github.com/Linxira-OS/linxira-skills) repository.
- Workspace materialisation: `src/linxira_crash_watch/workspace.py` in the `linxira-crash-watch` repository.
- System skill and manifest: the `agent/` directory in the `linxira-config-hub` repository.
