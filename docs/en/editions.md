# Editions and build strategy

This page sets out Linxira's near-term build plan and the promises attached to
it. The site announcement is
[Near-term plan](https://linxira-os.github.io/en/blog/editions-and-build-strategy/).

## Positioning

Linxira is not a distribution built from scratch. It is a **removable layer on
top of an upstream distribution**: catalog, transaction plan/confirm/receipt,
signed repository, configuration entry points, update notifications, crash
watch and welcome. Each base provides the kernel, hardware enablement and base
userland.

## Near-term plan

- **Arch x86_64**: the current mainline. Rolling updates, a planned monthly ISO
  snapshot; removing `linxira-*` returns you to vanilla Arch.
- **Ubuntu interim validation**: start with 26.10 (kernel 7.3) as a validation
  image, then 27.04 / 27.10 if needed, until the next LTS (28.04). These are
  9-month validation builds, not long-term products.
- **NixOS**: not a product line. Zeta already has Nix builds; use upstream Nix
  in a container or VM. We do not need to maintain a NixOS configuration.

| Line | Base | Role | Cadence | Exit | Status |
|---|---|---|---|---|---|
| Arch x86_64 | Arch Linux | Primary development machine; also inference | Rolling; planned monthly ISO snapshot | Remove `linxira-*`, return to vanilla Arch | Current mainline |
| Ubuntu interim validation | 26.10 / 27.04 / 27.10 | Validate apt backend, desktop, drivers, ARM allowlist | Follows interims, 9 months | Reimage; layer removable | In validation |
| Ubuntu LTS (future) | 26.04 LTS or 28.04 LTS | Inference, scientific computing, Chinese GPUs | LTS point releases + upstream security | Removable derivative, not a rolling exit | Pending |

Validation images will be labelled **“validation build, not long-term support,
EOL date”**, kept out of the support matrix and given no long-term promise.

## Ubuntu timeline

- 26.04 LTS: released 2026-04-23, standard security maintenance until 2031-05,
  ESM until 2036.
- 26.10: released 2026-10, 9 months of support, ends 2027-07.
- 27.04 “Tenacious T-Rex”: 2027-04-22, still a 9-month interim.
- 27.10: October 2027, interim.
- Next LTS: 28.04 (April 2028).

There is no LTS in 2027. For LTS + kernel 7.3, the decision point is
**26.04.2 (2027-02-18)**: if HWE brings 7.3 and the hardware validation passes,
move the long-term baseline to 26.04 LTS. Otherwise continue on 27.04, and
migrate or retire 26.10 before its EOL in 2027-07.

## China network and mirrors

- **Arch**: the best mirror coverage in China (TUNA, USTC, Aliyun and others);
  the monthly ISO is planned for GitCode / domestic object storage.
- **Ubuntu**: the official archive has Chinese mirrors (TUNA, USTC, Aliyun,
  Huawei Cloud and others); apt and ISOs can be served domestically. The
  installer will offer a domestic mirror option.
- **Chinese GPUs**: Moore Threads, Ascend and similar vendors ship drivers and
  toolchains mainly for Ubuntu.
- **DGX Spark / N1X**: NVIDIA DGX OS is based on Ubuntu 26.04 LTS ARM64, but
  image downloads may be account- or network-gated. Support is limited to a
  hardware allowlist, not generic ARM.
- **NixOS**: mirrors are unreliable in China and it is not a product entry
  point.

## Build and transaction contracts

- **catalog** is the single source of truth for software and target platforms.
  Each application maps to package targets per edition; the UI and installer do
  not hard-code package names.
- **components** keeps `plan → confirm → apply → receipt`; the execution layer
  selects a backend per edition:
  - Arch: fixed-argv `pacman`;
  - Ubuntu: fixed-argv `apt-get` / `dpkg-query`.
- **update / config-hub** select sources and update methods through edition
  adapters; the UI shares one status schema.
- **ISO**: each edition maintains its own build scripts but shares the
  selection/confirmation/receipt UX.

## Boundaries

1. Thin and removable: on Arch, removing every `linxira-*` package leaves a
   working vanilla Arch. Ubuntu validation images keep the layer removable too.
2. Common software only: no sponsor bloat, no strange system-level components.
3. Conservative supply chain: AUR is off by default on Arch; unreviewed PPAs are
   off by default on Ubuntu; vendor debs are reviewed and republished in our
   signed repository; `curl | sh` is not recommended.
4. No home-grown kernel: Arch uses the official latest kernel; Ubuntu uses HWE
   or vendor kernels. No v3 / CachyOS-derived kernel until a complete automation
   pipeline exists.
5. AI is optional: no agent auto-runs by default. Crash Watch performs
   zero-token triage; analysis starts only when the user clicks, stays local,
   read-only, and is never uploaded.
