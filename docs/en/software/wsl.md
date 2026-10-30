# WSL Distribution (`linxira-wsl`)

## Why it exists

A good share of Linxira's target users — developers who work with AI agents — spend their days on Windows while the agent's execution environment is Linux. Maintaining dual boot or a virtual machine for them is expensive; WSL2 is the native answer on the Windows side. linxira-wsl brings the Linxira toolchain into WSL as a rootfs distribution: no kernel, firmware or bootloader (WSL ships its own), only the parts that are actually used in a terminal.

## Relation to the desktop edition

| | ISO install | WSL |
|---|---|---|
| Kernel / boot / partitioning | handled by the installer | not applicable (WSL ships the kernel) |
| Desktop | catalog choice (Plasma / COSMIC / no desktop) | no session; GUI tools via WSLg (Win11) |
| Software stack | chosen at install time / component-manager | `linxira-component-manager` (the same chain) |
| Workspace guard | timer every 30 minutes | not enabled by default (see below) |
| Network management | NetworkManager | managed on the WSL side; NetworkManager is deliberately not installed |

**What the workspace guard means in WSL**: a WSL VM is shut down by Windows when no process is running, and systemd timers only fire while it runs — "a snapshot every 30 minutes" degrades into "a snapshot while a session is active". The image therefore leaves the guard off by default. Users who want it can run `linxira-config workspace-guard enable` manually, but should understand the trigger conditions.

## Usage

```powershell
wsl --import linxira C:\wsldata linxira-wsl-<version>-x86_64.tar.gz --version 2
wsl -d linxira
# remove
wsl --unregister linxira
```

After import the default user is root, systemd is enabled (`/etc/wsl.conf`), the `[linxira]` repository uses the same configuration as the ISO install (with signature verification), and `linxira-update` works out of the box.

## Contents

The full list is `wsl-packages.x86_64` in the repository (about 318 packages after dependency resolution, about 1.7 GB installed and about 0.5 GB compressed — that size was measured before `linxira-crash-watch` was added): `base` plus the first-party Linxira CLI toolchain (components / component-manager / config-hub / recovery-diagnostics / update / wiki / catalog / completion-agent). `linxira-update` pulls in the Qt graphics stack and can display directly under Win11 + WSLg.

## Building

Repository: [`linxira-wsl`](https://github.com/Linxira-OS/linxira-wsl). Run `./build-wsl-rootfs.sh` in an Arch environment; the output is a tar.gz plus a sha256, published through GitHub Releases.

The build script deliberately avoids `/tmp` (tmpfs is RAM): a measured incident — packing the rootfs filled a 2 GB tmpfs and a parallel ISO build on the same machine was OOM-killed.
