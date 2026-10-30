# Config CLI (`linxira-config-hub`)

## Why it exists

Once the system is installed, users ask two kinds of question: "how do I change this setting" and "what state is it in right now". Neither should force the user to read the wiki or memorise commands. `linxira-config` folds them into one entry point: one command, output a human can read, and only the things it explicitly lists can be changed.

It is owned by the `linxira-config-hub` repository and is the only general-purpose settings CLI in the system.

## Scope

**It owns**: mirror selection (Arch / npm / pip / AUR / Flatpak / Go), network diagnostics and DNS, the SSH service and keys, the UFW firewall, diagnostic log collection and upload, Timeshift quick setup, headless mode, GPU status, and enabling and reporting on the workspace guard.

**It does not own**:

- **Installing software.** Software installation, groups and components are planned by [`linxira-components`](components.md). The CLI's `install` / `workflow` entries refuse outright and point to the right owner.
- **System recovery.** When you need an evidence bundle, use [`linxira-recovery-diagnostics`](recovery.md).
- **Write operations whose transaction backend is not ready.** `service`, `rdp`, `security harden` and `net fix` say "waiting for the transaction backend" explicitly instead of offering a half-finished implementation.

## Usage

```bash
linxira-config mirror arch speed            # measure latency
linxira-config mirror arch auto             # pick the fastest
linxira-config net diag                     # network diagnostics
sudo linxira-config ssh on                  # first enable: allows password auth, so keys can be set up
linxira-config ssh key generate             # generate an Ed25519 key
linxira-config ssh key show                 # show the public key, to authorise it on a server
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

`ssh harden` checks that the current user has at least one usable `authorized_keys` entry, rewrites `10-linxira.conf` to `PasswordAuthentication no` and `KbdInteractiveAuthentication no`, runs `sshd -t` first and only then reloads. With no usable key it refuses; non-interactive scripts add `--yes`. Do not use `99-linxira-hardening.conf`: OpenSSH reads drop-ins in order and takes the first value for a setting, so the `yes` in `10-linxira.conf` would make a later `no` fail silently.

These four accept `--json`, emit a single line of JSON, and can therefore be parsed by an agent:

```bash
linxira-config workspace-guard status --json
linxira-config ssh status --json
linxira-config net diag --json
linxira-config mirror arch list --json
```

Everything else prints guidance meant for humans and makes no structural promise; an agent only needs to know whether it succeeded.

## When root is required

- **Not required**: `list` / `speed` / `status` / `diag` / `show` / `source` / `info` / `runtime`.
- **Required**: commands that change system state, such as `enable` / `disable` / `on` / `off` / `harden` / `ufw on`. They require root explicitly and tell you to use `sudo`.

By design, the agent does not start interactive commands that need root on the user's behalf — hand the command to the user to run.

## Deeper design

[Config Hub](../features/config-hub.md) · internals are in the `document/` directory of the [`linxira-config-hub`](https://github.com/Linxira-OS/linxira-config-hub) repository.
