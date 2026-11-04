# Hardware Detection (linxira-hwd-detector)

## Why it exists

Driver advice has to start from evidence that can be checked, not from guesses in a UI.
Whether a GPU is integrated, discrete or passed through to a VM, and which CPU and
virtualisation vendor are present, cannot be inferred from a window.

`linxira-hwd-detector` turns those facts into one read-only JSON document with a fixed
contract. The [Hardware and Driver Manager](hardware-driver-manager.md) maps facts to
policy; detection and policy stay separate.

## Responsibilities

**It owns**:

- Read-only collection from fixed locations:
  `/sys/bus/pci/devices/*/{class,vendor,device}`,
  `/sys/devices/virtual/dmi/id/{sys_vendor,product_name,chassis_type}` and `/proc/cpuinfo`.
- A `schema_version = 1` document containing `detector` metadata (name, implementation
  version, upstream CHWD version), `evidence` (`pci`, `dmi`, `cpu`, `virtualization`),
  sorted and unique `profile_ids`, and structured `warnings` with `source` and `message`.
- Stable hardware-class IDs: `cpu.amd`, `cpu.intel`, `graphics.amd`, `graphics.intel`,
  `graphics.nvidia`, `graphics.hybrid`, `vm.hyperv`, `vm.qemu`, `vm.virtualbox`,
  `vm.vmware`, `vm.xen`.
- The full `lhwd` CLI and the CHWD driver profiles installed under `/var/lib/chwd/db`.

**It does not own**:

- Package choice. The ID-to-package mapping, licence checks, kernel and DKMS
  preconditions all live in the manager.
- Kernel builds. Linxira ships the generic `linux` and `linux-lts` kernels only.
- Privilege escalation. Mutating `lhwd` subcommands only check the effective UID; they do
  not orchestrate Polkit or sudo.

## Chain of responsibility: who reads, who plans, who changes

| Step | Performer | Changes the system? |
|---|---|---|
| Collect hardware facts (no-argument JSON) | `linxira-hwd-detector` | Read-only, zero side effects |
| Facts → policy → plan | [Hardware and Driver Manager](hardware-driver-manager.md) | Read-only; plans go to the user state directory |
| Driver installation / service changes | [Components](components.md) system transaction service + Polkit | Privileged, with confirmation and a snapshot |
| Kernel and boot-state report | [Kernel Manager](kernel-manager.md) | Read-only; plans go to the user state directory |

Detection stops at facts plus class IDs. Package names, licence decisions and execution
order all belong downstream; the detector takes no part.

## How to use

### Read-only report

```bash
linxira-hwd-detector
```

Zero arguments prints the JSON report directly: no file writes, no package-manager calls,
no network. Both binaries share one entry branch keyed on argument count, so `lhwd` with no
arguments prints the same report; any argument routes to the full CLI below.

Contract highlights:

- `schema_version` versions the whole document; `detector.version` versions the
  implementation. Both are validated strictly.
- Missing evidence is `null` or an empty array plus a structured warning, never a guess.
- Arrays are sorted and the document carries no timestamp field, so repeated runs on one
  machine produce byte-identical output.

The consumer is the manager, which calls the fixed path `/usr/bin/linxira-hwd-detector`
with a 10-second timeout and a 1 MiB output cap, then validates duplicate keys, name,
version and known class IDs.

### Full CLI (`lhwd`)

```bash
lhwd --list                # profiles available for detected devices
lhwd --list-installed      # installed profiles
lhwd --list-all            # every profile in the database
lhwd --check <profile>     # check whether a profile matches this device
lhwd --autoconfigure       # choose and install matching profiles for detected devices
lhwd --install <profile>   # install a profile
lhwd --remove <profile>    # remove a profile
```

`--detail` is only valid together with a listing option and adds fields. `--force` allows
reinstalling. `--autoconfigure` accepts an optional class ID (`any` when omitted); when no
device matches, it only warns and starts no transaction.

## When root is required

- **Not required**: `linxira-hwd-detector` (no arguments), `lhwd --list`,
  `--list-installed`, `--list-all`, `--check`.
- **Required**: `lhwd --install`, `--remove`, and `--autoconfigure` when a device is found.
  The source checks the effective UID before entering a package transaction and exits when
  it is not root.

The supported Linxira path is not `lhwd`: system changes go through
[Components](components.md) plans, confirmation and Polkit. `lhwd` is the retained full
CHWD tool surface, not the daily privilege entry point.

## Known limitations

- Describes hardware classes only; package policy belongs to the manager.
- The package creates `/var/lib/chwd/scripts` but does not install the
  `/var/lib/chwd/scripts/chwd` helper that `lhwd` calls for `--install`, `--remove` and
  `--autoconfigure`. Those mutating subcommands therefore cannot complete as packaged;
  listing and checking are unaffected.
- Detection covers a fixed set of evidence; adding a source means changing the contract.
- Profiles come from upstream CHWD 1.23.0 and assume upstream/Arch package names. The
  manager makes no per-device support claim from them.

## Design notes

Upstream provenance and the fork point are in the repository's `UPSTREAM.md`; current
behaviour and boundaries are in the
[`linxira-hwd-detector` README](https://github.com/Linxira-OS/linxira-hwd-detector/blob/main/README.md).
Maintainer conventions are in `AGENTS.md`. The licence is GPL-3.0-only.
