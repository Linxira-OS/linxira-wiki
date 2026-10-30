# Update Assistant (`linxira-update`)

## Why it exists

The risk in a rolling release is not "updating" but "updating with no way back". Linxira OS answers this by making updating and snapshotting one thing: a bootable Timeshift snapshot is taken automatically before every update, and if something breaks you return to the pre-update system from the GRUB snapshot menu. `linxira-update` owns the "check and remind" half of that — the background timer, the tray and desktop notifications, and the Welcome update card all read the same status file; by default it only reminds and never acts.

## Scope

**It owns**: checking all configured pacman repositories (`[linxira]` plus Arch core/extra) for available updates, writing `status.json`, the tray icon and desktop notifications, the interactive full upgrade, news and pending-reboot service hints, and — once `EnableAutoApply` is turned on — snapshot plus fully automatic upgrades.

**It does not own**:

- **Installing software.** Component installation goes through `linxira-component-manager` (the Config CLI's `stack` forwards there as well) and shares the same snapshot protection.
- **Snapshot configuration.** Enabling Timeshift and its policies belong to `timeshift enable|disable|status` in [`linxira-config`](config.md).
- **AUR and Flatpak by default.** They must be explicitly opted in in the configuration.

## Usage

On first entry into the installed system, run it once:

```bash
linxira-update
```

After that, day to day you can just check, or let the tray remind you:

```bash
linxira-update --check      # check and notify only (the timer runs this automatically every hour)
linxira-update              # interactive full upgrade
linxira-update --list       # list updates without applying them
linxira-update --tray       # keep the tray resident
```

Status file `~/.local/state/linxira-update/status.json`: `check_status` (ok/error/incomplete), `available_update_count`, `last_check`, `reboot_required`. When a check is incomplete, a count of 0 does not mean the system is up to date.

The scheduled check is the user timer `linxira-update.timer` (hourly), enabled by the package preset on first login; the Welcome update card and the tray are only its presentation layer.

## Automatic pre-update snapshots and fully automatic updates

- On an installed system a PreTransaction hook creates a Timeshift snapshot before any pacman transaction (the 20 most recent are kept); snapshots enter the GRUB menu automatically, can be booted read-only to verify, and then rolled back. See the wiki's `updates-and-snapshots` topic (`linxira-wiki show updates-and-snapshots`).
- Add an `EnableAutoApply` line to `~/.config/linxira-update/linxira-update.conf` to turn on fully automatic updates: off by default; once on it only takes effect on machines with btrfs and the full snapshot infrastructure in place. Every automatic upgrade explicitly creates and verifies a snapshot first, and when those conditions are not met it stays at check + notify.

## When root is required

Checking, listing, the tray and notifications need no root. Applying updates raises privileges through `PrivilegeElevationCommand` (default `sudo`); the automatic path uses `pacman -Syu --noconfirm`, only ever for a full upgrade, never a partial one.

## Deeper design

The implementation is in the [`linxira-update`](https://github.com/Linxira-OS/linxira-update) repository; the command surface and every configuration key are in the wiki's `update-cli` topic.
