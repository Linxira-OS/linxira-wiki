# Recovery Diagnostics (`linxira-recovery-diagnostics`)

## Why it exists

When the system goes wrong, the first reflex is usually "fix it quickly". But many repair actions destroy the evidence, and once the repair is done you know neither where it first broke nor whether it is actually fixed.

`linxira-recovery-diagnostics` (lrd) fixes the order first: **read facts only, write the repair as a plan with preconditions, and require a user-authorised receipt to execute it.**

It is owned by the `linxira-recovery-diagnostics` repository and is the only read-only collector in the system allowed to run a fixed allowlist of commands on its own initiative.

## Scope

**It owns**: recovery readiness checks, read-only evidence collection (storage, timeshift, keyring, btrfs, pci, network), repair plans (`--plan` and the GUI Repairs page), and private redacted support bundles.

**It does not own**:

- **Executing repairs.** lrd only produces plans; execution is done by [`linxira-components`](components.md) after it receives a receipt.
- **Root operations.** The collection phase performs no writes and runs no `subprocess` through a shell.
- **Deleting things.** When the pacman lock is held it only reports; it does not delete.

## Usage

```bash
linxira-recovery-diagnostics --report-json     # full schema-v1 report
linxira-recovery-diagnostics --support-bundle  # private, redacted evidence bundle
linxira-recovery-diagnostics                   # no arguments = open the GUI
linxira-recovery-diagnostics --plan org.linxira.recovery.pacman-lock-diagnose.v1
```

The GUI has five tabs: Overview, Snapshots, Repairs, Workspace guard and Support report. The Repairs page lays out each plan's `effects` and `preconditions`; a plan with `available: false` has its button disabled and a tooltip giving the reason — **that is the design, not a bug**.

Only two read-only diagnostics have an executable backend wired up: `pacman-lock-diagnose` and `live-chroot-readiness`. The remaining plans are waiting for receipt authorisation.

## When root is required

**Never.** lrd is read-only diagnostics by definition and does not raise privileges at any point. That is also why it is safe to run at the scene of a failure: if it cannot start, the failure has some other cause.

The one root-related exception is workspace-guard evidence collection: it reads the root-owned `/etc/linxira/workspace-guard.conf`, so when the current user may not read it the report falls back to `configured: false` — a denied read is indistinguishable from an unconfigured guard. It neither crashes nor asks for authorisation.

## Deeper design

The implementation is in the `document/` directory of the [`linxira-recovery-diagnostics`](https://github.com/Linxira-OS/linxira-recovery-diagnostics) repository.
