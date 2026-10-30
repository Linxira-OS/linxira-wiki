# Crash Watch (`crash-watch`)

## Why it exists

Desktop crashes are **invisible**. A program killed by a signal simply loses its window; a kernel or service that segfaults leaves a few lines in `journalctl` that nobody reads. By the time someone thinks to look, the scene has been overwritten by reboots, log rotation and upgrades.

Crash Watch is about **preserving the scene**, not repairing it. The moment a crash happens it writes the evidence as text into a directory that can be browsed later and handed to an agent. No model is involved in that step, so **capture itself costs no tokens**.

It captures and stops. An agent is only started after the user **explicitly picks an action** in the notification.

## Scope

| It is responsible for | Specifically |
|---|---|
| Capture | Watch for new systemd-coredump entries and record the crashing program, signal, time and `dumpRef` |
| Triage | Decide whether this crash deserves the queue, suppress repeats and known noise |
| Writing the workspace | Write text evidence into the debug workspace, maintain the index and the backlog |
| Notification | Send a `notify-send` notification with action buttons and leave "do you want to look" to the user |

| It is not responsible for | Why |
|---|---|
| Automatic repair | Most crashes need human judgement; automatically editing configuration turns one crash into an incident |
| Starting an agent automatically | Capture is decoupled from diagnosis: without a user action no compute is spent and no bad edit is made |
| Owning system configuration | Configuration is read and written by `linxira-config`; Crash Watch only reads its diagnostic information |
| Storing core dumps | The dump body stays in systemd-coredump; the workspace keeps only a reference (`dumpRef`) |

## The workspace

The workspace defaults to `~/Linxira/debug` and can be changed with the `[workspace].path` configuration key. It is a **git repository and holds text only**: index, queue, log excerpts, command output. Binaries and core dumps never enter the workspace, so the repository can be committed, diffed and traced back without worry.

| Path | Purpose |
|---|---|
| `INDEX.md` | Human-readable crash index, in time order, pointing at each batch's evidence |
| `backlog.json` | Machine-readable queue of pending items |
| `mute.json` | Per-program mute rules |
| `batches/` | Evidence files grouped by batch, one batch per crash event |
| `.agents/skills/<name>/SKILL.md` | Skills shipped with the workspace, `gitignored` (tooling, not evidence) |
| `.zeta/sessions/` | Agent session records, also outside the versioned evidence set |

Ignoring `.agents/skills/` is deliberate: skills are tool configuration, not part of the record of "what happened in this crash".

## The three lanes

Crash Watch does not implement its own agent invocation logic; instead it fixes three entry points as three lanes. All three use the same workspace as `--cwd`; the only differences are the session shape and the tool permissions:

| Lane | Command | Purpose |
|---|---|---|
| Interactive | `zetacode --cwd <ws> --session-dir <ws>/.zeta/sessions "<PROMPT> @<evidence>"` | The user is present and asks as they look; the session lives in the workspace and can be resumed |
| Batch | `zetacode --cwd <ws> --goal "<PROMPT>"` | Give it one goal, it runs until done; used for tidying evidence in bulk |
| Unattended | `zetacode --cwd <ws> -p --tools=read,grep,glob,lsp "<PROMPT>"` | Runs in the background with a **read-only** tool set: read, grep, glob, LSP queries |

The unattended lane is the only one allowed to run automatically, and the price is that it **cannot write**: `--tools` grants only `read`, `grep`, `glob` and `lsp`, with no editing and no execution. Its output is a conclusion, not a patch.

## Skills

Exactly one skill is materialised into the workspace along with Crash Watch: `diagnose-crash`, at `<ws>/.agents/skills/diagnose-crash/SKILL.md`. It describes this subsystem's diagnostic procedure and ships with the Crash Watch version rather than being written by the user.

Since 0.1.4, Crash Watch **no longer** copies the `linxira-config` skill into the workspace. System-level skills stay in the system location and the workspace carries only the one belonging to this subsystem:

- System skill: `/usr/share/linxira/agent/skills/<name>/SKILL.md` (currently only `linxira-config`, installed by the `linxira-config-hub` PKGBUILD)
- Companion manifest: `/usr/share/linxira/agent/capabilities.json`

For skill scopes, installation and the `linxira-skills` CLI, see [Agent Skills](agent-skills.md). For what the workspace itself is and why it is split per subsystem, see [Agent Workspace](agent-workspace.md).

## Interaction

Notifications go out through `notify-send` with action buttons: investigate now, copy the prompt, pin, or mute. **Nothing runs until the user presses a button** — there is no background agent and no prepared patch.

Muting is **per program**: `mute.json` records program names, not this particular crash. Once a known-crashy third-party program is muted its new crashes no longer raise a notification, but by policy the records are still written into the workspace and can be found when needed.

## Deeper design

Crash classification, queue advancement, batch layout and the `dumpRef` resolution rules are in [crash-watch-design.md](https://github.com/Linxira-OS/linxira-crash-watch/blob/main/document/crash-watch-design.md).

| Project | Repository |
|---|---|
| Crash Watch | [`linxira-crash-watch`](https://github.com/Linxira-OS/linxira-crash-watch) |
