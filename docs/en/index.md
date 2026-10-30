# Linxira OS Wiki

Linxira OS is a KDE Plasma personal science workstation distribution built directly on Arch Linux, aimed at desktop supercomputing, scientific computing, AI, engineering, bioinformatics and container development.

## This site and the other two

Three sites, three different jobs — don't mix them up:

| Site | For | Shape |
|---|---|---|
| [Docs](https://linxira-os.github.io/en/docs/) | People who just installed the system | Short, task-oriented: installation, quick start, FAQ |
| **This site (Wiki)** | Long-term users and contributors | Long, reference-oriented: project overview, architecture, responsibility boundaries, permission model |
| [Blog](https://linxira-os.github.io/en/blog/) | People following what we are building | Narrative: release notes, benchmark reports, design trade-offs |

"How do I install it and get it running?" → docs site. "Why is it designed this way, and which component owns what?" → this site. "What happened recently?" → blog.

## Scope of this documentation

This documentation covers only the installer, Welcome, Shelly, Config Hub, software catalog, workflows and branding behaviour that are unique to Linxira OS. For generic Arch Linux, KDE, systemd, pacman and hardware configuration, refer to the [Arch Wiki](external/arch-wiki.md) first.

The wiki discusses **the general design of each project**: why it exists, its responsibility boundary, when to use which component, and its permission model. The full list is in the [project overview](#project-overview). Internal design, data structures and implementation decisions live in each project's own `document/` directory, not here.

## Linxira features

- [Direct Arch architecture](features/architecture.md): responsibility boundaries of Welcome, the software catalog, Shelly, Calamares and Config Hub
- [Config Hub CLI](features/config-hub.md): Arch, npm, pip and AUR source management plus system configuration
- [Preinstalled tools](features/preinstalled-tools.md): offline base desktop, and third-party sources that are off by default
- [Workflow presets](features/workflows.md): science, AI, development, container and bioinformatics setups
- [Branding system](features/branding.md): logo, wallpapers and visual assets

## Software

Every Linxira-specific program has a page in the [software index](software/index.md), grouped by the workflow it belongs to: system entry, software management, hardware and kernel, data and signing, platform and diagnostics, and placeholders.

## Project overview

The software section covers every first-party program in English. The repository ownership and lifecycle table remains in the Chinese [project overview](../项目总览/index.md), which is the authoritative source; the English [software index](software/index.md) groups the same programs by workflow.

## Boundaries of use

Linxira OS is intended for personal workstations and desktop compute nodes. Because it follows a rolling release model, it is not recommended for large-scale enterprise server deployments. When you need pinned dependencies, reproducible builds or server-style development environments, use version-pinned containers or another isolated environment.

Linxira OS is an independent project. It is not affiliated with, or endorsed by, Arch Linux.

---

!!! warning "This site is under construction"
    This wiki is not finished: the project overview and architecture sections are usable, while the operations manual, failure handling and permission-model chapters are still being completed.
    If you need "how do I install it and get it running", see the [docs site](https://linxira-os.github.io/en/docs/).
