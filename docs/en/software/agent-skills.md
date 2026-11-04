# Agent Skills (skills)

## Why it exists

A skill is **context** for an agent, not configuration for a program. A `SKILL.md` explains a subsystem's procedure, boundaries and commands; when the agent opens the corresponding directory and reads it, it knows how to work without the user repeating the briefing every time.

Once discovered, a skill enters the context, so it has a cost. Which scope it sits in decides who sees it and how many tokens they pay for it. The principle is therefore not "install whatever will install" but **install it at the layer that should see it**.

## Responsibilities

**`linxira-skills` owns**:

- The `linxira-skills` executable: `init`, `status`, `update`, `uninstall`.
- Profiles and payload: materialising the selected profile as a three-level routing tree under `.agents/skills/`, plus `.linxira/manifest.json` and the `AGENTS.md` marker block.
- Each profile's skill list, sources and licence records (`THIRD_PARTY_NOTICES.md`, `docs/SOURCES.md`).

**It does not own**:

- How a runtime discovers skills; that is Zeta's provider priority and its switches.
- Installing the system skill directory; that is the distribution package's PKGBUILD.
- Materialising workspace skills; each component does that for itself (currently Crash Watch).
- Producing agent sessions or executing skill content.

## Implemented scopes

| Scope | Path | Installed by | Visible to |
|---|---|---|---|
| System | `/usr/share/linxira/agent/skills/<name>/SKILL.md` | distribution package (PKGBUILD) | the whole system; package-owned, read-only, upgraded with the package |
| Workspace | `<ws>/.agents/skills/<name>/SKILL.md` | materialised by a component when it creates the workspace | only inside that workspace (the agent's `--cwd`); `.agents/skills/` is gitignored |
| Project | `<repo>/.agents/skills/` | `linxira-skills init` | only that repository; also generates `.linxira/manifest.json` and the `AGENTS.md` marker block |

**`linxira-skills` has no user-scope install path.** `~/.agents/skills/` is a user-level directory that Zeta's `agents` provider scans, but only when `enableAgentsUser` is switched on there; `linxira-skills` writes nothing to it, and packages must not either. A skill reused across projects can today only be placed there by the user, who carries the context cost.

What actually exists today is deliberately little:

- **The system scope has a single skill**: `linxira-config`, installed by the `linxira-config-hub` PKGBUILD. Its companion manifest `/usr/share/linxira/agent/capabilities.json` records what it can do and which commands need root.
- **The workspace scope also has a single one**: `diagnose-crash`, materialised by Crash Watch.
- The project scope holds whichever profile the user installs; the system pre-installs nothing there.

!!! note "Layout is one layer, not a tree"
    Zeta's provider discovery only looks at `<skills-root>/<name>/SKILL.md` — one layer. A nested `<skills-root>/<group>/<name>/SKILL.md` is not loaded by default. `linxira-skills` therefore keeps its three-level routing tree under `.agents/skills/` and uses the generated `AGENTS.md` marker block plus relative `INDEX.md` links to walk an agent from router to index to leaf, instead of relying on recursive scanning.

## Who may write where

| Writer | May write | Must not write |
|---|---|---|
| Distribution package (PKGBUILD) | the system skill directory and `capabilities.json` | `~/.zeta/agent/skills`, `~/.agents/skills`, any user directory |
| Components (e.g. Crash Watch) | only its own single skill, into its own workspace | other subsystems' skills, the system skill directory |
| `linxira-skills` CLI | the project scope of the target Git repository (`.agents/skills/`, `.linxira/manifest.json`, the `AGENTS.md` marker block) | the system skill directory, `~/.agents/skills`, `~/.zeta/agent/skills` |
| The user | any scope, though the project scope should be installed through the CLI so it stays traceable and uninstallable | — |

!!! warning "Packages must not write the user scope"
    `~/.agents/skills` belongs to the user, not to a package. A package writing there makes one skill appear in every one of the user's projects — a skill the user never chose and cannot cleanly remove with `linxira-skills uninstall`. `~/.zeta/agent/skills` is the same story: it is Zeta's own user data, and packages must not write to it.

## Why the project scope is the default

A user-level skill is visible to **every project**: once its switch is on, the agent loads it in any repository, even when the task does not need it. That is context cost, and it is also where name collisions come from — when the same skill name exists in several sources only the highest-priority copy wins, which is not intuitive to debug.

The project scope avoids both: the skill travels with the repository that needs it and disappears when you switch projects, and `uninstall` can clean up the managed directories. The home directory is also not a repository, so it should not be filled with an `AGENTS.md` marker block or `.gitignore` entries — one reason the CLI only works inside a Git repository.

## Discovery order

At startup Zeta loads skills in provider priority order, **first come, first served for a given name**:

1. native `.zeta` skills (user and project level, priority 100);
2. `zeta-plugins` (90), then `claude` (80), then the priority-70 group: `claude-plugins`, `agents`, `codex`;
3. `opencode` (55) and `github` (30);
4. finally Zeta's auto-learned (managed) skills (5), which always yield to an authored skill of the same name.

The outcome: a native `.zeta` version beats a same-named `.agents` version, and `.agents/` is exactly where `linxira-skills` and the components materialise skills. The system skill directory is not on the default scan path; it is referenced explicitly through the `skill` field of `capabilities.json`, so an agent that reads the manifest can find it.

The `agents` provider has its own user-level and project-level switches (`enableAgentsUser`, `enableAgentsProject`); disabling Claude, Codex or other providers does not turn it off.

## Commands

```bash
# project scope (the only supported scope): run inside the target Git repository
npx @linxiraos/linxira-skills init
npx @linxiraos/linxira-skills init --profile core
npx @linxiraos/linxira-skills init --layout namespaced   # default; routers land in .agents/skills/linxira-<root>/
npx @linxiraos/linxira-skills init --layout flat         # routers land in .agents/skills/<root>/

# inspect, update, uninstall: follow the profile and layout recorded in the manifest
npx @linxiraos/linxira-skills status
npx @linxiraos/linxira-skills update [--force]
npx @linxiraos/linxira-skills uninstall [--force]
```

`init`, `update` and `uninstall` all support `--dry-run`. `update` only touches manifest-owned entries that are unmodified and asks for `--force` before replacing user edits. `status` / `update` / `uninstall` read the `.linxira/manifest.json` written at install time, so changing `--layout` leaves no old directory to clean up by hand.

Profiles:

- `core` (default): 10 first-party software, integrity, Linux, transfer and compute skills.
- `bioinformatics-core`: `core` plus 10 first-party bioinformatics and bulk RNA-seq skills.
- `biology-research-core`: the previous level plus 19 biological discovery, experimental design, wet-lab governance and academic-delivery skills.
- `science-research-core`: extends that with chemistry, physics, crop/plant, ecology, animal physiology, biochemistry and medical/translational study design.
- `research-communication-core`: `core` plus 44 manuscript, citation, formatting, figure, document, LaTeX, presentation and Chinese research-document skills (including vendored Apache-2.0 / MIT adaptations; see `THIRD_PARTY_NOTICES.md`).

!!! note "Not yet published to npm"
    The installation architecture document states that the package **has not been published to npm**. The `npx` forms above assume a published package; until then only a locally built package can be used, and `@linxiraos/linxira-skills` must not be assumed downloadable.

## Separation rule

System-management skills (such as `linxira-config`) **stay in the system directory and are not copied into workspaces**.

A workspace materialises only the single skill its own subsystem needs. Since crash-watch 0.1.4, Crash Watch no longer copies `linxira-config` into the debug workspace: two copies of one skill drift apart over time, and the system skill is upgraded with its package while a workspace copy is not. To tell an agent about system-configuration capability, read the system skill instead of keeping a stale copy in every workspace.

## Privileges

- `linxira-skills` needs no root and calls no `sudo`; it writes only managed files inside the target Git repository.
- System skills are installed by the package manager as root, as part of the ordinary system upgrade path.
- Components materialise workspace skills with the user's own permissions and never elevate.

## Known limitations

- `init` must run inside a Git repository (or one of its subdirectories); any other directory fails with an error.
- Running `init` again in an initialised repository fails and asks for `update` or `uninstall` instead.
- `linxira-skills` has no user-scope install path; whether `~/.agents/skills` loads depends on Zeta's `enableAgentsUser` switch, so placing skills there by hand does not guarantee they take effect.
- The system skill directory is not on Zeta's default scan path and is only reachable through the `skill` field of `capabilities.json`.
- Skill discovery sees one directory layer; nested directories rely on the router and `AGENTS.md` guidance rather than automatic scanning.
- The CLI does not run `git add`, modify source submodules, fetch upstream, or make network requests.
- Only the five listed profiles exist; third-party material that has not passed review is not part of the installable payload.

## Further design

- Installer and layout: `docs/INSTALLATION_ARCHITECTURE.md` and `docs/SKILL_LOADING_POLICY.md` in the [`linxira-skills`](https://github.com/Linxira-OS/linxira-skills) repository.
- Workspace materialisation: `src/linxira_crash_watch/workspace.py` in the `linxira-crash-watch` repository.
- System skill and manifest: the `agent/` directory in the `linxira-config-hub` repository.
