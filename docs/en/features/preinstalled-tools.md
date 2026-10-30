# Preinstalled tools

The Linxira OS base system stays compact: a full installation needs no network. Large research, AI and development environments are installed either as optional presets in the installer or through Config Hub after first boot.

## Base desktop

| Category | Applications |
|------|------|
| Desktop | KDE Plasma, System Settings, Info Center |
| Files and terminal | Dolphin, Ark, Konsole, Kate |
| Documents and images | Okular, Gwenview, Spectacle |
| Browser | Firefox |
| Software management | Shelly |
| System monitoring | Plasma System Monitor, KScreen, `fwupd` |

## System foundation

- Official Arch `linux` and `linux-lts`, both installed
- `pacman` and signed official Arch repositories
- NetworkManager, PipeWire, Bluetooth and power configuration
- Btrfs, Timeshift, grub-btrfs and basic recovery components
- Fastfetch and `linxira-config`

## Off by default

AUR, Flatpak, AppImage, vendor GPU compute stacks and third-party binary repositories are all disabled by default. Miniforge, Bioconda, CUDA and large scientific software are not part of the base system either.

Such components must be explicitly chosen by the user, with the source and the transaction scope shown. For reproducible research environments, prefer isolation via Apptainer, Podman or Distrobox.

---

Back to the [wiki home](../index.md) · [software index](../software/index.md)
