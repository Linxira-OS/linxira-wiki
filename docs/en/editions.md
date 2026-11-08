# Editions and build strategy

This page sets out the boundaries, promises and update cadence of Linxira across
multiple bases. The site announcement is
[Editions preview](https://linxira-os.github.io/en/blog/editions-and-build-strategy/).

## Positioning

Linxira is not a distribution built from scratch. It is a **removable layer on
top of an upstream distribution**: catalog, transaction plan/confirm/receipt,
signed repository, configuration entry points, update notifications, crash
watch and welcome. Each base provides the kernel, hardware enablement and base
userland; Linxira provides the curated software, privilege boundaries and a
reproducible environment.

## Three editions

| Edition | Base | Role | Cadence | Exit | Status |
|---|---|---|---|---|---|
| **Arch x86_64** | Arch Linux | Primary development machine; also usable for inference | Rolling; planned monthly ISO snapshot | Remove `linxira-*` and you are back on vanilla Arch | Current mainline |
| **Ubuntu x86_64 / ARM64** | Ubuntu 26.04 LTS | Inference, scientific computing, Chinese GPUs; ARM for DGX Spark, N1X and similar | LTS point releases + upstream security; HWE at point releases | Removable derivative, but not a rolling exit | Under research |
| **NixOS** | NixOS (VM / container) | Reproducible reference environment, benchmarks, toolchains | Pinned flake; updated on demand | Configuration and flake only | Experimental, no SLA |

## Ubuntu timeline (do not wait for a version that does not exist)

- 26.04 LTS: released 2026-04-23, standard security maintenance until 2031-05,
  ESM until 2036.
- 26.10: released 2026-10, 9 months of support, ends 2027-07.
- 27.04 “Tenacious T-Rex”: 2027-04-22, still a 9-month interim.
- 27.10: October 2027, interim.
- Next LTS: 28.04 (April 2028).

There is no “long-term release after July 2027” option. For **LTS + kernel
7.3**, the target is **26.04.2 (2027-02-18)**: following Ubuntu's HWE cadence,
it should bring the 26.10 7.3 kernel into 26.04 LTS. Check the Ubuntu release
notes for the final word.

## China network and mirrors

- **Arch**: the best mirror coverage in China (TUNA, USTC, Aliyun and others);
  the monthly ISO is planned for GitCode / domestic object storage.
- **Ubuntu**: the official archive has Chinese mirrors (TUNA, USTC, Aliyun,
  Huawei Cloud and others); apt and ISOs can be served domestically. The
  installer will offer a domestic mirror option.
- **NixOS**: TUNA, USTC and SJTU provide nix-channels and binary-cache mirrors,
  but coverage and stability are not guaranteed. Until that is reliable, NixOS
  remains an experimental VM reference with no promise.
- **Chinese GPUs**: Moore Threads, Ascend and similar vendors ship drivers and
  toolchains mainly for Ubuntu.
- **DGX Spark / N1X**: NVIDIA DGX OS is based on Ubuntu 26.04 LTS ARM64, but
  image downloads may be account- or network-gated. Support is limited to a
  hardware allowlist, not generic ARM.

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
   working vanilla Arch. Ubuntu keeps the layer removable too, but it is not a
   rolling distribution.
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

## What happens next

- Ubuntu: research 26.04 LTS + 7.3 HWE, Chinese GPU drivers and the DGX Spark /
  N1X allowlist. No release date is promised until that research is done.
- NixOS: flake / VM configuration only.
- Arch: keep the mainline and move toward the monthly ISO snapshot and an exit
  test.
