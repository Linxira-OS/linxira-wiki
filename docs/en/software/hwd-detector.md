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
- A `schema_version = 1` document containing `detector` metadata, `evidence` (PCI, DMI,
  CPU, virtualisation), sorted and unique `profile_ids`, and structured `warnings`.
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

## How to use

### Read-only report

```bash
linxira-hwd-detector
```

Running with no arguments is the only contractually guaranteed read-only entry point:
no file writes, no package-manager calls, no network. Any argument routes to the full
CLI below.

Contract highlights:

- `schema_version` versions the whole document; `detector.version` versions the
  implementation. Both are validated strictly.
- Missing evidence is `null` or an empty array plus a structured warning, never a guess.
- Arrays are sorted, so repeated runs on one machine produce the same document apart
  from timestamps.

### Full CLI (`lhwd`)

```bash
lhwd --list                # profiles available for detected devices
lhwd --list-installed      # installed profiles
lhwd --list-all            # all profiles
lhwd --check <profile>     # check whether a profile matches this device
lhwd --autoconfigure       # choose profiles for detected devices
lhwd --install <profile>   # install a profile
lhwd --remove <profile>    # remove a profile
```

`--detail` adds fields to listings, `--force` allows reinstalling, and
`--autoconfigure` accepts an optional class ID (`any` when omitted).

## When root is required

- **Not required**: `linxira-hwd-detector`, `lhwd --list`, `--list-installed`,
  `--list-all`, `--check`.
- **Required**: `lhwd --install`, `--remove`, `--autoconfigure`. The source checks the
  effective UID before entering a package transaction and exits when it is not root.

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

Upstream provenance and the fork point are in the repository's `UPSTREAM.md`. See
[`linxira-hwd-detector`](https://github.com/Linxira-OS/linxira-hwd-detector).
