# Config CLI (`linxira-config-hub`)

## Why it exists

Once the system is installed, users ask two kinds of question: "how do I change this setting" and "what state is it in right now". Neither should force the user to read the wiki or memorise commands. `linxira-config` folds them into one entry point: one command, output a human can read, and only the things it explicitly lists can be changed.

It is owned by the `linxira-config-hub` repository and is the only general-purpose settings CLI in the system.

## Scope

**It owns**: mirror selection (Arch / npm / pip / AUR / Flatpak / Go), network diagnostics and DNS, the SSH service and keys, the UFW firewall, diagnostic log collection and upload, Timeshift quick setup, the headless (server) mode switch, the environment-variable file, GPU status, enabling and reporting on the workspace guard, read-only catalog queries, the `tui` number menu, and the capability manifest agents read.

**It does not own**:

- **Installing software.** Software installation, groups and components are planned by [`linxira-components`](components.md). The CLI's `install` / `workflow` entries refuse outright and point to the right owner.
- **System recovery.** When you need an evidence bundle, use [`linxira-recovery-diagnostics`](recovery.md).
- **Catalog content.** Applications, components and bundles belong to [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog); the CLI queries by catalog ID and never expands or applies a record.
- **Install logic.** `stack` is only a forwarding bridge to `linxira-component-manager`; plan → confirm → apply still happens in [`linxira-components`](components.md).
- **Write operations whose transaction backend is not ready.** The mutating actions of `service`, `rdp`, `virt` and `power`, plus `security harden` and `net fix`, say "waiting for the transaction backend" explicitly instead of offering a half-finished implementation.

## Usage

```bash
linxira-config mirror arch speed            # measure latency
linxira-config mirror arch auto             # pick the fastest
linxira-config net diag                     # network diagnostics
sudo linxira-config ssh on                  # first enable: allows password auth, so keys can be set up
linxira-config ssh key generate             # generate an Ed25519 key
linxira-config ssh key show                 # show the public key, to authorise it on a server
linxira-config ssh authorized list          # authorised public keys
linxira-config ssh authorized add /tmp/key.pub  # plain public keys only
sudo linxira-config ssh harden              # disable password login once key login is verified
sudo linxira-config ssh password on --yes   # explicitly allow password login again
sudo linxira-config ssh off                 # persistently disable
linxira-config ssh status                   # SSH status
# temporary enable (this boot only, closed after a reboot; for one-off debugging):
#   sudo systemctl start sshd
#   sudo systemctl stop sshd
# first connection (skips the interactive fingerprint prompt, 8 s timeout):
#   ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 user@IP
linxira-config timeshift status             # snapshot backend status
sudo linxira-config timeshift enable        # bind the system disk and enable
sudo linxira-config timeshift disable       # stop automatic snapshots
linxira-config workspace-guard status       # workspace guard status
linxira-config help                         # full command table
```

The remaining entry points and read-only queries (all from `linxira-config help`):

```bash
linxira-config --launch                     # what the "Linxira Config" menu entry runs
linxira-config tui                          # pure-bash number menu over the same commands
linxira-config status                       # one-screen system summary
linxira-config capabilities                 # print the capability manifest agents read
linxira-config catalog software --all       # read-only catalog query (software/component/bundle)
linxira-config headless status              # target state for desktop / server mode
linxira-config env list --json              # read /etc/profile.d/linxira-env.sh
linxira-config stack list                   # installable software stacks (forwarded to component-manager)
linxira-config logs collect                 # collect diagnostics into ~/linxira-logs/
```

`--launch` only hosts the interactive menu in an existing terminal: it tries Konsole, Alacritty and xterm in turn; when none exists it writes a temporary `Terminal=true` desktop entry and opens it with `gtk-launch` (the path a COSMIC session without those terminals takes). It never elevates privileges itself and never executes a user-supplied command string.

`ssh harden` checks that the current user has at least one usable `authorized_keys` entry, rewrites `10-linxira.conf` to `PasswordAuthentication no` and `KbdInteractiveAuthentication no`, runs `sshd -t` first and only then reloads. With no usable key it refuses; non-interactive scripts add `--yes`. Do not use `99-linxira-hardening.conf`: OpenSSH reads drop-ins in order and takes the first value for a setting, so the `yes` in `10-linxira.conf` would make a later `no` fail silently.

`linxira-config help` explicitly lists these four as accepting `--json`; each emits a single line of JSON that an agent can parse:

```bash
linxira-config workspace-guard status --json
linxira-config ssh status --json
linxira-config net diag --json
linxira-config mirror arch list --json
```

Everything else prints guidance meant for humans and makes no structural promise; an agent only needs to know whether it succeeded.

## When root is required

- **No root (read-only)**: `status`, `info`, `capabilities`, `catalog …`, `runtime status`, `gpu info`, `net diag`, `net dns` (show), `mirror … list|speed`, `ssh status`, `timeshift status`, `workspace-guard status`, `env list|get`, `stack list|status`, `logs collect`, `tui`, `help`.
- **Root required**: `ssh on|off|harden|password|port`, `security ufw on|off|allow`, `net dns set`, `timeshift enable|disable`, `workspace-guard enable|disable`, `env set|unset`, `headless on|off`, plus `mirror arch auto|set|reset` (rewrites `/etc/pacman.d/mirrorlist` through `sudo tee`) and `mirror npm auto|set|reset` (writes the system-wide environment file). These refuse to run without root and tell you to use `sudo`.
- **Per user**: `mirror pip|aur|flatpak|go auto|set|reset` only change the current user's pip, git, Flatpak or Go configuration.

By design, the agent does not start interactive commands that need root on the user's behalf — hand the command to the user to run.

## Known limitations

- The mutating actions of `service`, `rdp`, `virt` and `power`, plus `security harden` and `net fix`, currently answer "waiting for the transaction backend". They are disabled until plan / verify / receipt / rollback exist; they are not a half-working feature.
- `stack` requires `linxira-component-manager` to be installed and fails otherwise. `linxira-config install` and `workflow` are always refused and point at Shelly and Quick System Software Setup.
- `help` promises single-line JSON only for `workspace-guard status --json`, `ssh status --json`, `net diag --json` and `mirror arch list --json`. `capabilities`, `env list|get` and `stack list` also accept `--json` but are not in that list; everything else prints human guidance.
- `headless on now` stops the display manager and terminates the current desktop session, losing unsaved data. It asks for confirmation only on a TTY; non-interactive use has no extra guard.
- `logs upload` sends the chosen log file to a public paste service (paste.rs / termbin / dpaste); check the contents before uploading.
- `ssh harden` refuses to run without a usable `authorized_keys` entry and only rewrites `10-linxira.conf`; it does not take over other drop-ins in `sshd_config`.
- The command surface is terminal-only. `--launch` opens a terminal for you; there is no separate graphical settings window.

## Deeper design

[Config Hub](../features/config-hub.md) · the command surface, root boundaries and development rules are in the [`linxira-config-hub`](https://github.com/Linxira-OS/linxira-config-hub) repository's `README.md` and `AGENTS.md`.
