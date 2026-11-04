# Kernel Manager (linxira-kernel-manager)

## Why it exists

Kernel state is scattered across `uname`, `/usr/lib/modules`, `pacman`, `dkms`, `/boot`
and the GRUB environment. Answering “which kernel is running, is LTS installed, why is a
reboot pending” normally means comparing several commands with no shared evidence.

Kernel Manager collects that state into one read-only report and turns four fixed actions
into reviewable plans. It is a reporting and planning tool, not a bootloader writer.

## Responsibilities

**It owns**:

- Read-only collection of the running release, installed `linux` / `linux-lts` versions,
  `pacman -Q` state, `dkms status`, initramfs and kernel images, `/proc/modules`,
  `/proc/cmdline`, GRUB entries, next/saved entries from `grub-editenv list`, and the
  reboot marker.
- Keeping only GRUB entries that boot the exact `linux` or `linux-lts` images.
- Display-only fixed-operation plans with preconditions, expected commands, effects,
  warnings, blockers and a plan digest.
- The GUI views Overview, Kernels, Boot and Activity / report.

**It does not own**:

- Writing GRUB, generating initramfs, installing or removing packages, or changing services.
- Custom or third-party kernels.
- Privilege escalation or the transaction backend. Apply is permanently disabled. The
  driver-side boundary is in [Hardware and Driver Manager](hardware-driver-manager.md).

## Chain of responsibility: who reads, who plans, who changes

| Step | Performer | Changes the system? |
|---|---|---|
| Collect kernel and boot state | This manager | Read-only |
| State → fixed-operation plan | This manager | Read-only; plans go to the user state directory |
| Install kernels / regenerate initramfs / write GRUB | Nobody today | Not implemented |

That third row is the load-bearing fact: the commands in a plan are display text, and **no
component currently executes them**. If an execution path is added later, authorisation
should still go through [Components](components.md) and Polkit.

## How to use

### GUI

Launch **Linxira Kernel Manager** from the application menu, or run:

```bash
linxira-kernel-manager
```

| Tab | Contents |
|---|---|
| Overview | Running kernel release, effective next boot, reboot state, warnings/blockers |
| Kernels | `linux` and `linux-lts` versions, releases, headers, image counts; per-kernel DKMS records |
| Boot | Supported GRUB entries; normal, fallback and kernel-image evidence |
| Activity / report | Pick a fixed operation, review the full plan, `Save plan` (Apply disabled) |

In Activity / report, `I reviewed this exact plan` must be checked before `Save plan` is
enabled. The `Apply` button is always disabled with the tooltip `Apply backend is not ready`.

### Command line

```bash
linxira-kernel-manager --report-json
linxira-kernel-manager --plan org.linxira.kernel.ensure-standard.v1
linxira-kernel-manager --plan org.linxira.kernel.boot-lts-once.v1
linxira-kernel-manager --plan org.linxira.kernel.regenerate-initramfs.v1
linxira-kernel-manager --plan org.linxira.bootloader.refresh-grub.v1
```

`--plan` prints `{path, plan}` and writes the plan atomically under
`$XDG_STATE_HOME/linxira/kernel-manager/plans/` (`~/.local/state/...` when unset), named
after the plan's own SHA-256. Exit status is 0 when the plan is applicable and 3 otherwise,
including when no change is needed.

| Operation ID | Expected command shown in the plan |
|---|---|
| `org.linxira.kernel.ensure-standard.v1` | `/usr/bin/pacman -S --needed linux linux-headers linux-lts linux-lts-headers` |
| `org.linxira.kernel.boot-lts-once.v1` | `/usr/bin/grub-reboot <detected-linux-lts-entry-id>` |
| `org.linxira.kernel.regenerate-initramfs.v1` | `/usr/bin/mkinitcpio -P` |
| `org.linxira.bootloader.refresh-grub.v1` | `/usr/bin/grub-mkconfig -o /boot/grub/grub.cfg` |

Those commands are **display text** (`expected.displayOnly = true`), not execution tokens.

## Transaction boundary

- The plan's `apply` field is always
  `{"implemented": false, "result": "backend-not-ready"}`; the Apply button stays disabled,
  and the system transaction service exposes no kernel or bootloader operation.
- Each plan carries `sourceReportSha256` and `planSha256`. Preconditions cover the fixed
  support matrix, readable package state, whether the target kernel is installed, and
  whether a GRUB entry is unambiguous.
- `boot-lts-once` requires exactly one `linux-lts` GRUB entry with a safe ID; otherwise it
  blocks rather than guessing.
- `refresh-grub` is applicable only when the GRUB configuration is readable and at least
  one supported kernel is installed.

## When root is required

Never, and no root path is implemented. Every command is read-only or writes only the
user's plan directory. The program does not call `sudo`, `pkexec`, a package manager,
service writes, initramfs generation or bootloader writes. If a backend is added later,
authorisation should go through [Components](components.md) and Polkit.

## Known limitations

- The support matrix is `linux`, `linux-lts`, `linux-headers`, `linux-lts-headers`; custom
  kernels are explicitly unsupported.
- Only the fixed `/boot/grub/grub.cfg` and `grub-editenv list` are parsed; other
  bootloaders are out of scope.
- A GRUB entry is kept only when a supported kernel image can be parsed. Parse failures
  block a plan; they never cause a write.
- Installed state comes only from fixed evidence: `/usr/bin/uname -r`, `/usr/lib/modules`,
  `pacman -Q`, `dkms status`, `/boot`, `/proc/cmdline`, `/proc/modules` and
  `/run/reboot-required`; subprocesses use fixed arguments, `shell=False` and an 8-second
  timeout.
- The plan directory chain rejects symlinks and files use `0600` permissions.

## Design notes

Current behaviour and boundaries are in the
[`linxira-kernel-manager` README](https://github.com/Linxira-OS/linxira-kernel-manager/blob/main/README.md),
maintainer conventions in `AGENTS.md`. The driver-side boundary is in
[Hardware and Driver Manager](hardware-driver-manager.md).
