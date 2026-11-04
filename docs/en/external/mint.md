# Linux Mint Documentation

!!! warning "Historical migration context"
    This page is kept to trace Linxira's early Linux Mint route. It does not describe the current system and is not part of the current navigation. Linxira OS is now built directly on Arch Linux and does not use Mint as its base distribution.

## Recommended resources

- [Linux Mint User Guide](https://linuxmint-user-guide.readthedocs.io/)
- [Linux Mint official blog](https://blog.linuxmint.com/)
- [Linux Mint Forums](https://forums.linuxmint.com/)

## Historical reference tools

| Tool | Purpose | Documentation |
|------|---------|---------------|
| mintinstall | Software manager | [GitHub](https://github.com/linuxmint/mintinstall) |
| mintupdate | Update manager | [GitHub](https://github.com/linuxmint/mintupdate) |
| mintsources | Software source configuration | [GitHub](https://github.com/linuxmint/mintsources) |
| timeshift | System snapshots | [GitHub](https://github.com/linuxmint/timeshift) |

## Current architecture differences

The main differences between the current Linxira OS and this historical route:

- Uses the official Arch Linux repositories, `pacman` and the rolling-release model directly
- KDE Plasma is the default desktop environment
- Uses Shelly to manage graphical packages and updates
- Uses Linxira Welcome, Calamares and Config Hub for their own product responsibilities

---

Back to the [wiki home](../index.md)
