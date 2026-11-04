# Agent Workspace

## Definition

An **agent workspace** is the directory an agent starts in: `--cwd` points at it, and sessions and evidence are written inside it. It is not a global scratch directory but **one landing place per subsystem** — one workspace per subsystem, never shared.

That split comes from evidence ownership: crash evidence belongs to Crash Watch, configuration-change evidence belongs to the configuration side. Putting both into one directory makes their `INDEX.md` files overwrite each other, and `git diff` can no longer say which subsystem produced a given change.

The workspace also stores sessions. Starting the interactive lane with `--session-dir <ws>/.zeta/sessions` puts the sessions inside the workspace too, so "what was asked, what was seen" and the evidence sit in the same tree and can be compared afterwards.

## Responsibilities

**It owns (the convention itself)**:

- The rules that a workspace is split per subsystem, stores text only, and carries only its own subsystem's skills.
- The split between evidence (batch directories, `INDEX.md`, `backlog.json`, `mute.json`) and tool state (`.agents/skills/`, `.zeta/sessions/`).

**It does not own**:

- Implementing a workspace. The only implementation today is
  [Crash Watch](crash-watch.md), which creates the directory, writes `INDEX.md` and
  materialises the `diagnose-crash` skill.
- The agent's session format or recovery logic; `--cwd`, `--session-dir` and `.zeta/`
  semantics belong to Zeta.
- Snapshot or restore; that is [Workspace Guard](workspace-guard.md).
- Installing project skill trees; that is `linxira-skills` in [Agent Skills](agent-skills.md).

## How to use

The component that creates the workspace provides it; users do not build the directory by hand:

```bash
linxira-crash status            # print workspace path, configuration and event counts
linxira-crash investigate <id>  # launch zetacode inside the workspace (spends tokens)
```

The path is configured in `~/.config/linxira/crash-watch.toml` under `[workspace].path`
and defaults to `~/Linxira/debug`. On first use the workspace is created as a git
repository containing `INDEX.md`, `backlog.json`, `mute.json`, `batches/` and
`.agents/skills/diagnose-crash/SKILL.md`.

## Current implementation

There is currently **only one** implemented agent workspace: Crash Watch's `~/Linxira/debug` (the default; the configuration key is `[workspace].path`).

| Path | Purpose |
|---|---|
| `INDEX.md` | Human-readable index |
| `backlog.json` | Machine-readable queue of pending items |
| `mute.json` | Per-program mute rules |
| `batches/` | Evidence stored by batch |
| `.agents/skills/` | Workspace skills, **gitignored** |
| `.zeta/sessions/` | Agent session records |

`.agents/skills/` is ignored because it is tool configuration rather than evidence: skills can be re-materialised per version, a crash scene cannot. `.zeta/sessions/` is session-layer data and is likewise not committed as evidence.

The workspace is a git repository and stores text only. Core dumps stay in systemd-coredump; the workspace holds only the `dumpRef` pointing at them.

## Hard rules

- **One workspace per subsystem.** Do not create a second directory "just to drop something in", and do not merge two subsystems' evidence into one place.
- **Do not copy another subsystem's skills in.** A workspace carries only the skills its own subsystem needs; system-level skills stay in `/usr/share/linxira/agent/skills/`, and `~/.zeta/agent/skills` is Zeta's user data, which packages must not write to.
- **Do not reuse `~/Linxira/debug` for system or configuration work.** It is the directory for crash evidence, and configuration changes mixed in make the crash index meaningless.
- **Text only.** Binaries, core dumps and large dumps do not enter the workspace.

## Difference from the workspace guard

Both concepts are called "workspace", but they are not the same thing:

| | Agent workspace | Workspace registered with the guard |
|---|---|---|
| What it is | The agent's `--cwd`, where sessions and evidence land | A directory the user works in |
| Typical paths | `~/Linxira/debug` | `$HOME/Linxira-OS`, `$HOME/Projects`, `$HOME/work`, `$HOME/src` |
| Who uses it | The agent | The user |
| What it does | Stores evidence and runs sessions | Snapshotted on a timer by the same-disk guard, for recovery after accidental deletion |

The guard registers **snapshot targets**, not agent workspaces; conversely, an agent workspace is not registered with the guard. Their paths, lifetimes and purposes differ, so do not substitute one for the other. The mechanism itself is described in [Workspace Guard](workspace-guard.md).

## Not implemented yet

**There is no system/configuration agent workspace.** No component defines a "system workspace": `linxira-config-hub` neither registers an agent workspace nor starts an agent.

If one is added later, the following are **conventions and plans, not current behaviour**:

- It must be a separate path, for example `~/Linxira/system`, never reusing `~/Linxira/debug`;
- It must not share `INDEX.md`, the queue or the session directory with the crash workspace;
- It follows the same rules: text only, and only the skills of its own subsystem.

Until then, system and configuration work has no dedicated agent workspace; do not invent a path or reuse the crash workspace before the conventions on this page are implemented.

## Privileges

- The workspace lives under `$HOME` and is owned by the user; creating, writing and reading
  it need no root.
- Crash Watch itself is an unprivileged user service: no root, no network, no arbitrary shell.
- The workspace is not a privileged landing place — do not put root-requiring configuration
  changes into it, and do not treat it as an escalation path.

## Known limitations

- Only one subsystem implements a workspace (Crash Watch's debug workspace); the
  system/configuration workspace still does not exist.
- `.agents/skills/` and `.zeta/sessions/` are gitignored, so cloning or copying a workspace
  brings neither skills nor sessions; skills can be re-materialised, sessions are not
  archived with the evidence.
- Text only: core dumps, binaries and large dumps never enter the workspace, only the
  `dumpRef` pointing into systemd-coredump.
- The workspace is not registered with the workspace guard, so it has no timed snapshots;
  deleting it means losing the evidence.
- The layout belongs to the implementation (`INDEX.md`, `backlog.json`, `mute.json`,
  `batches/`). This page records the single current implementation, not a generic
  directory contract any component may assume.

## Related

- [Crash Watch](crash-watch.md) — the only subsystem that implements an agent workspace today
- [Agent Skills](agent-skills.md) — skill scopes, the system skill location and the `linxira-skills` CLI
- [Workspace Guard](workspace-guard.md) — snapshot and restore for user directories

## Further design

Workspace layout and triage rules are in
[`linxira-crash-watch`](https://github.com/Linxira-OS/linxira-crash-watch)
`document/crash-watch-design.md`; the entry point is the same repository's `README.md`.
