# Workspace Guard (`workspace-guard`)

## Why it exists

An agent runs inside the user's workspace with **full user privileges**. It can `rm -rf` a directory, and it can `rm -rf .git` — the latter is worse because it looks like ordinary cleanup. Once the workspace is gone, the user's code, commit history and unpushed branches go with it, and there is usually no second copy.

This mechanism does not try to make the agent more careful. It assumes the agent will make mistakes and keeps an independent recovery point **outside user privileges**: a root timer takes a snapshot every 30 minutes into the root-only directory `/var/lib/linxira/guard` on the system disk.

## Scope

This is a cross-project mechanism spanning four repositories:

| Part | Owner | Content |
|---|---|---|
| Executing snapshots and restores | [`linxira-components`](components.md) | `linxira-components-guard` snapshot / restore, and the snapshot timer |
| Store directory, registration, enabling | [`linxira-config`](config.md) | `linxira-config workspace-guard enable` |
| Writing the same-disk configuration at install time | [`linxira-iso-direct`](https://github.com/Linxira-OS/linxira-iso-direct) | the `shellprocess@linxira-workspace-guard` install script |
| Documentation | this wiki | this page and `ai/topics/workspace-guard.md` |

**It does not own**: backing up the system itself (that is timeshift's job), backing up the whole home directory, incremental sync or real-time monitoring. It does one thing: "keep full snapshots of registered workspaces under a policy".

## Two kinds of "workspace"

"Workspace" has two meanings in this wiki, and the guard only covers the first:

| | Workspace registered with the guard | Agent workspace |
|---|---|---|
| What it is | A directory the user works in, as a snapshot target | The agent's `--cwd`, where sessions and evidence land |
| Typical paths | `$HOME/Linxira-OS`, `$HOME/Projects`, `$HOME/work`, `$HOME/src` | `~/Linxira/debug` |
| Who uses it | The user | The agent |

`workspace-guard` registers **snapshot targets**, not agent workspaces, and agent workspaces are not registered automatically. The paths, lifetimes and purposes differ. See [Agent Workspace](agent-workspace.md) for the definition and rules of the agent workspace.

## Usage

### Enabling (root)

```bash
sudo linxira-config workspace-guard enable
```

Creates the root-only `/var/lib/linxira/guard` on the system disk, writes the configuration, registers the workspaces and starts the timer. It does not create partitions, does not touch the partition table and does not touch a second disk. The command is idempotent. The installer runs the same same-disk configuration (a failure there does not block installation; the guard simply stays off); `enable` is for rebuilding or re-enabling it.

```bash
sudo linxira-config workspace-guard disable   # stops the timer only, keeps every stored recovery point
```

### Day to day (agent-friendly, no authorisation)

```bash
linxira-config workspace-guard status
linxira-config workspace-guard status --json
linxira-components-guard status
linxira-components-guard list ~/Linxira-OS
linxira-components-guard list ~/Linxira-OS --json
```

When nothing is configured these commands degrade safely instead of failing — unconfigured is a normal state. `linxira-config workspace-guard handbook` additionally prints the AI-readable handbook manifest.

### Recovery point operations (Polkit authorisation)

```bash
linxira-components-guard snapshot ~/Linxira-OS
linxira-components-guard restore <id> --target ~/ws-restored
```

### Registering a workspace (root)

```bash
sudo linxira-components-guard init
sudo linxira-components-guard register ~/Linxira-OS
sudo linxira-components-guard unregister ~/Linxira-OS
```

Registration writes the guard's own root-owned table: it has no user-visible side effect and nothing to roll back, so it is administrator-only and deliberately opens no privilege entry that could be triggered repeatedly. A non-root run is refused outright rather than silently stopping halfway.

## When root and authorisation are needed

- **Read-only, no root**: `linxira-config workspace-guard status [--json]`, `linxira-components-guard status [--json]`, `linxira-components-guard list <path> [--json]`, and `linxira-config workspace-guard handbook`.
- **Root required**: `linxira-config workspace-guard enable|disable`, and `linxira-components-guard init|register|unregister`. A non-root run is refused outright rather than silently stopping halfway.
- **Polkit authorisation**: `linxira-components-guard snapshot` and `linxira-components-guard restore` go through a system D-Bus plan and confirmation, where Polkit asks for administrator authentication. An agent may start them but does not need to hold sudo.

## Lifecycle of a recovery point

The guard store lives on the system disk; it creates no separate partition and writes nothing to `/etc/fstab`. The directory is `root:root 0700`: an ordinary user's agent cannot read it, root can read and write it. The timer runs as root every 30 minutes, relying neither on the agent's good behaviour nor on the user being present.

## Three invariants

1. **The configuration is unreadable to agents.** `/etc/linxira/workspace-guard.conf` is `root:root 0600`. This is a security premise, not a setting — there is no option to put it somewhere the user can read.
2. **A restore never overwrites.** `restore` always writes into a new directory; targets inside the original workspace, inside the guard store, or existing and non-empty are all refused. Not a single byte of the original workspace is touched.
3. **The store directory is root-only.** `/var/lib/linxira/guard` is `root:root 0700`. Ordinary users can neither read nor modify it; root can read, write and delete.

## Known limitations

- The store lives on the root filesystem (default `/var/lib/linxira/guard`); it creates no separate partition and writes nothing to `/etc/fstab`. `enable` and the installer only offer the same-disk layout; another disk is not part of the automatic flow.
- Retention is whatever `enable` wrote: 24 scheduled and 10 manual snapshots (`keep_scheduled` / `keep_manual`); older recovery points are pruned.
- Every snapshot is a full copy, not incremental or real-time sync. The store grows with the workspace, and a full disk makes the snapshot fail with an explicit error.
- `enable` automatically registers only the existing `Linxira-OS`, `Projects`, `work` and `src` directories under the home of the user who ran sudo; anything else needs an explicit `linxira-components-guard register`.
- It does not back up the system itself or the whole home directory; Timeshift and your own backups own those.
- `restore` only writes a new directory and refuses targets inside the original workspace, inside the guard store, or existing and non-empty. There is no in-place rollback.
- When a non-root user cannot read `/etc/linxira/workspace-guard.conf`, `status` says "present but not readable" and recovery diagnostics can only report `configured: false`.

## Deeper design

Retention policy and snapshot directory layout belong to [`linxira-components`](https://github.com/Linxira-OS/linxira-components); the privilege layering is written in [`AGENTS.md`](https://github.com/Linxira-OS/linxira-components/blob/main/AGENTS.md). For a machine-readable summary run `linxira-wiki show workspace-guard`.
