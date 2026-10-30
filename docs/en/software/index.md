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

## Placeholders

These are placeholders only. They are listed so the naming and the slot are reserved; nothing is delivered yet and nothing should be relied on.

| Page | Status |
|---|---|
| [Zeta](zeta.md) | Placeholder — no implementation |
| [Bio SDK](bio-sdk.md) | Placeholder — no implementation |

---

Back to the [wiki home](../index.md) · [English features](../features/architecture.md)
