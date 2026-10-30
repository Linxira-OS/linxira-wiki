# Config Hub CLI

`linxira-config` manages Linxira-specific software configuration, mirror selection, software stacks and environment variables. Only the CLI is delivered today; a GUI is still in design.

## Software sources

It supports listing, speed-testing, selecting and resetting six kinds of sources — Arch, npm, pip, AUR, Flatpak and Go — plus conda channel management for Miniforge (conda-forge and bioconda only):

```bash
linxira-config mirror arch list
linxira-config mirror arch speed
linxira-config mirror npm speed
linxira-config mirror npm set npmmirror
linxira-config mirror pip set tuna
linxira-config mirror pip reset
linxira-config mirror aur speed official
linxira-config mirror flatpak auto
linxira-config mirror go set goproxy-cn
linxira-config conda channels list
```

Arch and Flatpak are configured system-wide; pip, AUR (Git clone traffic only) and Go apply per user. Since 2026-10, npm records the `LINXIRA_NPM_REGISTRY` preference in `/etc/profile.d/linxira-env.sh`, while `npm login` and `npm publish` always use the official registry. Every source accepts only built-in reviewed entries or an explicit HTTPS address, and is probed over the network before anything is written.

AUR is not a signed binary repository. By default the CLI lists only verifiable official endpoints; a custom address must pass an AUR Git smart-HTTP probe. The configuration only rewrites package Git clone traffic — RPC metadata still uses the official service:

```bash
linxira-config mirror aur set https://example.invalid/aur
linxira-config mirror aur reset
```

## Environment and software stacks

Environment variables and common software stacks (LaTeX, Python, containers, Rust, Node.js, …) are forwarded by the Config CLI to the component manager, using the same transaction chain as the GUI:

```bash
linxira-config env list | get KEY | set KEY VALUE | unset KEY
linxira-config stack list | status <id...> | install <id...> --yes | tui
```

A direct `linxira-config install <pkg>` is refused and redirected to the correct owner — a deliberate boundary, not an oversight.

## System services

The CLI also provides entry points for SSH, firewall, remote desktop, virtualization, power and network diagnostics. Operations that change the system invoke `sudo` explicitly; plain listing and speed tests require no root.

---

Back to the [wiki home](../index.md) · [software index](../software/index.md)
