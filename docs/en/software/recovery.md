# Recovery Diagnostics (`linxira-recovery-diagnostics`)

## Why it exists

When the system goes wrong, the first reflex is usually "fix it quickly". But many repair actions destroy the evidence, and once the repair is done you know neither where it first broke nor whether it is actually fixed.

`linxira-recovery-diagnostics` (lrd) fixes the order first: **read facts only, write the repair as a plan with preconditions, and require a user-authorised receipt to execute it.**

It is owned by the `linxira-recovery-diagnostics` repository and is the only read-only collector in the system allowed to run a fixed allowlist of commands on its own initiative.

## Scope

**It owns**: recovery readiness checks, read-only evidence collection (storage, timeshift, keyring, btrfs, pci, network), repair plans (`--plan` and the GUI Repairs page), and private redacted support bundles.

**It does not own**:

- **Executing repairs.** lrd only produces plans. The two read-only diagnostics are executed by the [`linxira-components`](components.md) system transaction service; repair plans have no execution backend.
- **Root operations.** The collection phase performs no writes and runs no `subprocess` through a shell.
- **Deleting things.** When the pacman lock is held it only reports; it does not delete.

## Usage

The GUI and the application-menu entry run `linxira-recovery-diagnostics-gui`; the
command-line entry point is `linxira-recovery-diagnostics`:

```bash
linxira-recovery-diagnostics --report-json     # full schema-v1 report
linxira-recovery-diagnostics --support-bundle  # private, redacted evidence bundle
linxira-recovery-diagnostics                   # no arguments = open the GUI
linxira-recovery-diagnostics --plan org.linxira.recovery.pacman-lock-diagnose.v1
```

The three options are mutually exclusive and do one thing at a time. Plans and
support bundles are written under generated names below
`$XDG_STATE_HOME/linxira-recovery-diagnostics` (default
`~/.local/state/linxira-recovery-diagnostics`); no output path can be supplied.

The GUI has five tabs: Overview, Snapshots, Repairs, Workspace guard and Support report. The Repairs page lays out each plan's `effects` and `preconditions`; a plan with `available: false` has its button disabled and a tooltip giving the reason — **that is the design, not a bug**.

The plan list is fixed and holds eight IDs. Only two are available, both read-only
diagnostics: `org.linxira.recovery.pacman-lock-diagnose.v1` and
`org.linxira.recovery.live-chroot-readiness.v1`, executed through the system D-Bus
transaction service with `read_only: true`. Plans themselves are generated locally;
the apply button is on the Repairs page. The other six (snapshot, rollback,
keyring, initramfs, and the workspace-guard snapshot and restore) all report
`apply-backend-not-ready`; rollback and guard restore additionally report
`future-root-receipt-required`. Their buttons stay disabled.

## When root is required

**lrd itself never raises privileges.** Collection, reports, plans and bundles all run
as the current user, with no writes and no shell.

The only root-related path is executing the two read-only diagnostics: lrd submits a
fixed operation ID to the system D-Bus transaction service, which runs as root and,
after Polkit administrator authentication, executes it and returns a read-only
receipt. lrd holds no sudo and accepts no user-supplied command or
argument.

Workspace-guard evidence collection reads the root-owned
`/etc/linxira/workspace-guard.conf`; when it cannot, the report falls back to
`configured: false` — a denied read is indistinguishable from an unconfigured guard.
It neither crashes nor asks for authorisation.

## Known limitations

- Only `/` and `/mnt` are inspected as system roots; there is no arbitrary path, snapshot identifier or command argument.
- External commands use an exact argv allowlist: `findmnt`, `lsblk`, Timeshift listing and read-only `systemctl is-enabled`/`is-active`. There is no shell, mount/chroot, package mutation or service mutation.
- The pacman lock is diagnosed, never deleted; while it is held, lrd only reports and leaves the decision to a human.
- Only the two read-only diagnostics have an executable backend; the other plans stay `available: false` even when every precondition is met.
- The support bundle performs recursive redaction and shows a manifest, including no journal, dmesg or raw process command lines, and uploads nothing; it is still an evidence snapshot, so review it against your own privacy needs before sharing.
- The GUI's Workspace guard tab can only show an unconfigured state when the guard is not set up; it is not an enablement entry point.

## Deeper design

Implementation and safety boundaries are in the [`linxira-recovery-diagnostics`](https://github.com/Linxira-OS/linxira-recovery-diagnostics) README.
