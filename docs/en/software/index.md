# Software

This is the index of Linxira-specific software. Each page describes one program: why it exists, what it owns, what it deliberately does not own, and when you should reach for it.

Pages are grouped by the workflow you are in, not by repository name.

!!! warning "Under construction"
    Some pages below are still being written. If a page is empty or missing detail, the Chinese wiki and the project's own `document/` directory remain authoritative.

## System entry

The programs you meet first, from first boot onward.

| Page | What it is |
|---|---|
| [Welcome](welcome.md) | The fixed entry screen: reads catalog and installation receipts, shows workstation state, launches a whitelisted set of tools |
| [Completion Agent](completion-agent.md) | Presents the plan for finishing setup on first online start, and delegates the actual transactions |
| [Gaming Manager](gaming-manager.md) | Game library, compatibility launching and per-user backup |

## Software management

Everything that installs, removes or updates software goes through one transaction shape.

| Page | What it is |
|---|---|
| [Components](components.md) | The transaction engine: planning, confirmation, privileged apply and receipts — the only owner of root-level change |
| [Package Center](package-center.md) | Installed-state presentation for packages |
| [Component Manager](component-manager.md) | Capability-state presentation for components and software stacks |
| [Update](update.md) | Background update checks, tray notifications and the snapshot-integrated update flow |

## Hardware and kernel

Read-only detection first, then policy and plans.

| Page | What it is |
|---|---|
| [HWD Detector](hwd-detector.md) | Read-only hardware detection and the hardware fact contract |
| [Hardware Driver Manager](hardware-driver-manager.md) | Driver policy UI, DKMS report and driver plans |
| [Kernel Manager](kernel-manager.md) | Kernel policy UI, boot-state report and kernel plans |

## Data and signing

| Page | What it is |
|---|---|
| [Catalog](catalog.md) | The versioned, reviewed metadata source for software, categories and workstation presets |
| [Keyring](keyring.md) | Signing keys and keyring distribution for Linxira packages |

## Platform and diagnostics

| Page | What it is |
|---|---|
| [Config](config.md) | `linxira-config`: settings, mirrors, environment, software stacks, SSH, firewall, remote desktop, virtualization and diagnostics |
| [Recovery](recovery.md) | Read-only evidence collection first, then a repair plan behind explicit authorisation |
| [Crash Watch](crash-watch.md) | Captures crash evidence as text before anything is restarted, and only invokes an agent after you choose an action |
| [Workspace Guard](workspace-guard.md) | Independent root snapshots of user workspaces, so an accidental `rm -rf` is recoverable |
| [Agent Workspace](agent-workspace.md) | The per-subsystem directory an agent starts in, holding sessions and evidence |
| [Agent Skills](agent-skills.md) | Scoped `SKILL.md` context that teaches an agent how a subsystem works |
| [WSL](wsl.md) | The Linxira toolchain as a WSL2 rootfs distribution, without kernel, firmware or bootloader |

## External products

Zeta and Linxira Bio SDK are external products, not Linxira OS system components. Each page here is an entry point: it states what the product is and where its authoritative documentation lives, then sends you there. The wiki does not carry their usage docs — both products ship and evolve their documentation on their own schedule, so a command reference copied here would only go stale.

| Product | Status |
|---|---|
| Zeta | External product — [entry page](zeta.md); the authoritative runtime docs live in its own repository |
| Bio SDK | External product — [entry page](bio-sdk.md); the authoritative usage docs live in its GitHub Wiki |

## Project overview

The [ownership and lifecycle](#ownership-and-lifecycle) table below is the full repository map. In daily use you only need a few user-facing entry points:

- [Config](config.md) — change settings, inspect network and SSH, mirrors; the enablement entry point for daemons
- [Components](components.md) — install software and every transaction that needs root
- [Welcome](welcome.md) — first start and the status entry point
- [Update](update.md) — check for and apply system updates, tray notifications, the snapshot-integrated update side
- [Recovery](recovery.md) — collect read-only evidence first when the system misbehaves
- [Crash Watch](crash-watch.md) — capture a crash scene as text evidence and only invoke an agent after you choose an action
- [Workspace Guard](workspace-guard.md) — a cross-project mechanism that survives an agent deleting a workspace by mistake

Build and release repositories (`packages`, `linxira-packages`, `linxira-iso-direct`) and brand assets are not end-user software, so they have no usage page of their own; brand assets are covered by the [branding system](../features/branding.md).

## Ownership and lifecycle

The `owns` and `lifecycle` columns below come from `linxira-os/governance/repositories.yaml`. The `ai/manifest.json` in this package is generated from that file and is not maintained by hand.

| Repository | owns | lifecycle |
|---|---|---|
| [`linxira-os`](https://github.com/Linxira-OS/linxira-os) | product-architecture、repository-governance、support-matrix、release-manifests | active |
| [`linxira-iso-direct`](https://github.com/Linxira-OS/linxira-iso-direct) | live-profile、installer-configuration、target-manifests、iso-build | active |
| [`packages`](https://github.com/Linxira-OS/packages) | pkgbuilds、package-ci、signed-repository-publication | active |
| [`linxira-packages`](https://github.com/Linxira-OS/linxira-packages) | package-repository-hosting、repository-metadata | active |
| [`linxira-keys`](https://github.com/Linxira-OS/linxira-keys) | signing-keys、keyring-distribution | active |
| [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog) | catalog-schema、applications、capabilities、presets、desktop-metadata | active |
| [`linxira-components`](https://github.com/Linxira-OS/linxira-components) | transaction-planning、confirmation、privileged-apply、receipts | active |
| [`linxira-package-center`](https://github.com/Linxira-OS/linxira-package-center) | package-center-ui、installed-state-presentation | active |
| [`linxira-component-manager`](https://github.com/Linxira-OS/linxira-component-manager) | component-manager-ui、capability-state-presentation | active |
| [`linxira-gaming-manager`](https://github.com/Linxira-OS/linxira-gaming-manager) | gaming-library、compatibility-launch、user-backup | active |
| [`linxira-update`](https://github.com/Linxira-OS/linxira-update) | system-update、update-status、update-tray | active |
| [`linxira-completion-agent`](https://github.com/Linxira-OS/linxira-completion-agent) | first-online-plan-presentation、completion-state、transaction-delegation | active |
| [`linxira-hwd-detector`](https://github.com/Linxira-OS/linxira-hwd-detector) | read-only-hardware-detection、hardware-fact-contract | active |
| [`linxira-hardware-driver-manager`](https://github.com/Linxira-OS/linxira-hardware-driver-manager) | driver-policy-ui、kernel-dkms-report、driver-plan | active |
| [`linxira-kernel-manager`](https://github.com/Linxira-OS/linxira-kernel-manager) | kernel-policy-ui、boot-state-report、kernel-plan | active |
| [`linxira-recovery-diagnostics`](https://github.com/Linxira-OS/linxira-recovery-diagnostics) | recovery-readiness、repair-plan、private-support-bundle | active |
| [`linxira-crash-watch`](https://github.com/Linxira-OS/linxira-crash-watch) | crash-diagnosis、crash-window、debug-workspace | active |
| [`linxira-welcome`](https://github.com/Linxira-OS/linxira-welcome) | welcome-status、lifecycle-guidance、fixed-tool-routing | active |
| [`linxira-config-hub`](https://github.com/Linxira-OS/linxira-config-hub) | linxira-cli、diagnostics、runtime-adapters、source-adapters、ssh-network-plans | active |
| [`linxira-artwork`](https://github.com/Linxira-OS/linxira-artwork) | brand-assets、terminal-artwork、visual-policy | active |
| [`linxira-hooks`](https://github.com/Linxira-OS/linxira-hooks) | pacman-hooks、reboot-state | review-required |
| [`linxira-wiki`](https://github.com/Linxira-OS/linxira-wiki) | user-documentation | active |
| [`Linxira-OS.github.io`](https://github.com/Linxira-OS/Linxira-OS.github.io) | public-website、publication-endpoint | active |
| [`linxira-wsl`](https://github.com/Linxira-OS/linxira-wsl) | wsl-distribution-image、wsl-rootfs-build | active |
| [`linxira-hello`](https://github.com/Linxira-OS/linxira-hello) | — | deprecated |
| [`linxira-iso`](https://github.com/Linxira-OS/linxira-iso) | — | deprecated |
| [`extendai-lab-cli`](https://github.com/Linxira-OS/extendai-lab-cli) | extendai-cli | independent |
| [`extendai-lab-Studio`](https://github.com/Linxira-OS/extendai-lab-Studio) | extendai-studio | independent |
| [`linxira-pulse`](https://github.com/Linxira-OS/linxira-pulse) | ai-assistant | independent |
| [`linxira-skills`](https://github.com/Linxira-OS/linxira-skills) | skill-platform | independent |
| [`linxira-fish-config`](https://github.com/Linxira-OS/linxira-fish-config) | fish-shell-configuration | paused |
| [`linxira-zsh-config`](https://github.com/Linxira-OS/linxira-zsh-config) | zsh-shell-configuration | paused |
| [`linxira-gnome-settings`](https://github.com/Linxira-OS/linxira-gnome-settings) | gnome-desktop-defaults | paused |
| [`linxira-kde-settings`](https://github.com/Linxira-OS/linxira-kde-settings) | kde-plasma-defaults | paused |
| [`linxira-hypr-noctalia`](https://github.com/Linxira-OS/linxira-hypr-noctalia) | hyprland-desktop-defaults | paused |
| [`linxira-niri-noctalia`](https://github.com/Linxira-OS/linxira-niri-noctalia) | niri-desktop-defaults | paused |
| [`linxira-mangowc-dms`](https://github.com/Linxira-OS/linxira-mangowc-dms) | mangowc-desktop-defaults | paused |
| [`linxira-settings`](https://github.com/Linxira-OS/linxira-settings) | system-settings-defaults | paused |
| [`linxira-wallpapers`](https://github.com/Linxira-OS/linxira-wallpapers) | wallpaper-assets | paused |

### Reading lifecycle

- **active** — maintained, and the feature commitments hold.
- **review-required** — the ownership is being re-checked. `linxira-hooks` is currently the only one.
- **independent** — has its own cadence and does not follow the system release.
- **paused** — archived and paused: the repository is read-only on GitHub, only to prevent accidental edits. Unarchive it to keep working; it can be reactivated at any time. Paused never means abandoned.
- **deprecated** — superseded; do not use it in new work.

### Who owns what

One capability has exactly one owner. When two repositories appear to own the same thing, `owns` decides: `linxira-config-hub` owns the settings and diagnostics entry points, and `linxira-components` owns transactions and the privileged apply. The UI projects (`linxira-package-center`, `linxira-component-manager`) do not re-implement escalation — see [Config](config.md) and [Components](components.md).

### Root access

The table itself needs no authorisation. Every `linxira-wiki` subcommand is read-only and needs no root:

```bash
linxira-wiki show ownership
linxira-wiki manifest
```

### Further design

The internal design of each project lives in that repository's `document/` directory, not here. The source of the ownership data is [`linxira-os/governance/repositories.yaml`](https://github.com/Linxira-OS/linxira-os/blob/master/governance/repositories.yaml); `ai/manifest.json` in this package is generated from that file and is never hand-edited.

---

Back to the [wiki home](../index.md) · [English features](../features/architecture.md)
