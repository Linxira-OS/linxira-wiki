# Hardware and Driver Manager (linxira-hardware-driver-manager)

## Why it exists

Detection answers “what hardware is present”. It does not answer “which driver, which
packages, and how does a failure roll back”. Without that separation the user sees a
recommendation but not the plan behind it.

This manager turns hardware facts into **reviewable fixed-policy plans**, and hands
execution to the single system transaction backend.

## Responsibilities

**It owns**:

- Reading the `linxira-hwd-detector` JSON with strict schema, name, version and
  duplicate-key validation.
- A fixed policy table: Intel / AMD Mesa, NVIDIA open / proprietary, and
  Hyper-V / QEMU / VMware / VirtualBox guests.
- Installed-state reporting from fixed evidence only: `linux`, `linux-lts` and their
  headers, DKMS, initramfs, loaded modules and the reboot marker.
- Atomically saved plans (`0600`) under
  `$XDG_STATE_HOME/linxira/hardware-driver-manager/plans`.
- A root-owned read-only diagnosis, and confirmed installation transactions for three VM
  guest policies.

**It does not own**:

- Hardware detection ([Hardware Detection](hwd-detector.md)).
- The transaction backend, snapshots or Polkit ([Components](components.md)).
- Kernel packages themselves ([Kernel Manager](kernel-manager.md)).

## Chain of responsibility: who reads, who plans, who changes

| Step | Performer | Changes the system? |
|---|---|---|
| Collect hardware facts | [Hardware Detection](hwd-detector.md) (no-argument JSON) | Read-only |
| Facts → fixed policy → plan | This manager | Read-only; plans go to the user state directory |
| Driver installation, snapshot, service verification | [Components](components.md) system transaction service + Polkit | Privileged, with confirmation and a Timeshift snapshot |

Every local action stops at a plan. **Apply is not executed by this program**: it asks
`org.linxira.Components1` for a plan and for confirmation to run it; the backend performs
the package installation, service enablement and snapshot.

## How to use

### GUI

Launch **Linxira Hardware and Driver Manager** from the application menu, or run:

```bash
linxira-hardware-driver-manager
```

Four tabs:

| Tab | Contents |
|---|---|
| Overview | Detected hardware class IDs, detector name and version, `Run root diagnosis` |
| Drivers | Recommended policy, full plan JSON, `Save plan` and `Apply` |
| Kernel compatibility | `linux` / `linux-lts` kernel, headers and DKMS table |
| Activity / report | Complete read-only report JSON |

The Drivers tab lists only policies whose hardware class was detected; with no match the
list is empty. Saving needs the `I reviewed this exact plan` checkbox. `Apply` needs the
same checkbox plus a policy from the three VM guest set and an applicable plan; otherwise
it stays disabled, and for other policies it shows
`Only applicable reviewed VM guest policies have an executable backend`.

### Command line

```bash
linxira-hardware-driver-manager --report-json
linxira-hardware-driver-manager --plan org.linxira.driver.intel-mesa.v1
linxira-hardware-driver-manager --plan org.linxira.driver.intel-mesa.v1 --json
```

`--plan` accepts only the fixed policy IDs below; no package name, path or command. Plans
are always written under `$XDG_STATE_HOME/linxira/hardware-driver-manager/plans/`
(`~/.local/state/...` when unset), named after the plan's own SHA-256. Without `--json` the
command prints the plan path; with `--json` it prints the plan. Exit status is 0 when the
plan is applicable and 3 otherwise; when the detector is unavailable both `--report-json`
and `--plan` exit with status 2.

| Policy ID | Hardware fact | Current status |
|---|---|---|
| `org.linxira.driver.intel-mesa.v1` | `graphics.intel` | Plan only; Apply is not offered |
| `org.linxira.driver.amd-mesa.v1` | `graphics.amd` | Plan only; Apply is not offered |
| `org.linxira.driver.nvidia-open-dkms.v1` | `graphics.nvidia` | Plan only; explicit review required |
| `org.linxira.driver.nvidia-proprietary-dkms.v1` | `graphics.nvidia` | Unavailable: no dual-kernel proprietary NVIDIA DKMS package in the reviewed Arch cohort |
| `org.linxira.driver.vm-qemu-guest.v1` | `vm.qemu` | Apply available in the GUI |
| `org.linxira.driver.vm-virtualbox-guest.v1` | `vm.virtualbox` | Unavailable: dual-kernel guest-module providers are not fixed |
| `org.linxira.driver.vm-vmware-guest.v1` | `vm.vmware` | Apply available in the GUI |
| `org.linxira.driver.vm-hyperv-guest.v1` | `vm.hyperv` | Apply available in the GUI |

A plan records the policy ID, the hard-coded package set, the detector digest, licence
and driver model, kernel/header and DKMS preconditions, expected effects, warnings,
blockers, applicability and the plan's own SHA-256. Plans are written atomically with
private permissions; a plan directory that is itself a symlink is rejected.

## Transaction boundary

- **A local plan is a review artifact, not an execution token.** Plans from the CLI and the
  GUI preview describe what would happen; the CLI has no apply subcommand, and a local
  plan's `apply` field is always
  `{"implemented": false, "result": "backend-not-ready"}`.
- **Read-only diagnosis** goes through the system D-Bus service `org.linxira.Components1`
  with the fixed operation `org.linxira.hardware.driver-state-diagnose.v1`, an empty
  parameter object and a plan whose risk is `read-only`. After the user confirms in the
  transaction service, the receipt must report `status = succeeded` and `changed = false`.
  Nothing in this step touches packages, services or system files.
- **Apply is available only for the three VM guest policies** (Hyper-V, QEMU, VMware). On
  Apply the manager first asks the transaction service for a root-owned, reviewable driver
  plan whose risk is `system-change-reboot-possible` and whose rollback is the pre-change
  Timeshift snapshot; after confirmation the backend creates the snapshot, applies the
  fixed package set, verifies platform services and returns an immutable receipt. A change
  in repository or hardware evidence between the two steps invalidates the plan.
- VirtualBox, proprietary NVIDIA and the ordinary Intel / AMD / NVIDIA graphics plans have
  no executable backend; their Apply control stays disabled with
  `Apply unavailable: backend-not-ready`.

## When root is required

- **Not required**: `--report-json`, `--plan`, browsing, policy preview and plan saving.
- **Required**: `Run root diagnosis` and applying a VM guest policy. Both go through the
  system transaction service, where Polkit decides authorisation and prompts when needed;
  the manager never calls `sudo`, `pkexec` or a package manager itself.

## Known limitations

- The support matrix is `linux` and `linux-lts` plus their headers. DKMS-based policies
  report a blocker when a required kernel is missing.
- NVIDIA open and proprietary are alternatives requiring an explicit choice. Device-ID
  support is not claimed; the proprietary DKMS comparison is blocked.
- Installed state comes only from fixed evidence: `uname -r`, `/usr/lib/modules`,
  `pacman -Q`, `dkms status`, initramfs under `/boot`, `/proc/modules`, `/proc/uptime` and
  `/run/reboot-required`; no arbitrary path is scanned.
- Detector output is capped at 1 MiB with a 10-second timeout. Without the detector the
  report is unavailable (CLI exit status 2).
- Plan directories and files reject symlinks and use `0600` file permissions.
- Internal subprocesses use fixed argument lists, `shell=False` and an 8-second timeout; no
  path, package name or command input is accepted.

## Design notes

Current behaviour and boundaries are in the
[`linxira-hardware-driver-manager` README](https://github.com/Linxira-OS/linxira-hardware-driver-manager/blob/main/README.md),
maintainer conventions in `AGENTS.md`. The transaction shape is described in
[Components](components.md).
