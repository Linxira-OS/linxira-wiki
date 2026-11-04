# Update Assistant (`linxira-update`)

## Why it exists

The risk in a rolling release is not "updating" but "updating with no way back". Linxira OS answers this by making updating and snapshotting one thing: a bootable Timeshift snapshot is taken automatically before every update, and if something breaks you return to the pre-update system from the GRUB snapshot menu. `linxira-update` owns the "check and remind" half of that — the background timer, the tray and desktop notifications, and the Welcome update card all read the same status file; by default it only reminds and never acts.

## Scope

**It owns**: checking every configured pacman repository (the Linxira repository plus whichever Arch repositories the system has enabled) for available updates, writing `status.json`, the tray icon and desktop notifications, the interactive full upgrade, news and pending-reboot service hints, and — once `EnableAutoApply` is turned on — snapshot plus fully automatic upgrades.

**It does not own**:

- **Installing software.** Component installation goes through `linxira-component-manager` (the Config CLI's `stack` forwards there as well) and shares the same snapshot protection.
- **Snapshot configuration.** Enabling Timeshift and its policies belong to `timeshift enable|disable|status` in [`linxira-config`](config.md).
- **AUR and Flatpak by default.** They must be explicitly opted in in the configuration.

## Usage

To walk through the full flow once after installation, run:

```bash
linxira-update
```

After that, day to day you can just check, or let the tray remind you:

```bash
linxira-update --check      # check and notify only (the timer runs exactly this)
linxira-update              # interactive full upgrade
linxira-update --list       # list updates without applying them
linxira-update --tray       # keep the tray resident (--tray --enable also writes the autostart entry)
linxira-update --launch     # what the menu entry and a tray click run: open the interactive flow in a terminal
linxira-update --gen-config # write an example config (--force overwrites an existing file)
linxira-update --show-config # print the current config
```

These entry points share one state: the "Linxira Update" menu entry runs `--launch`, "Linxira Update Tray" and `linxira-update-tray.service` run `--tray` (the package also ships `/etc/xdg/autostart/linxira-update-tray.desktop`, so the tray starts at login), and the Welcome update card only reads `status.json` instead of checking again.

Status file `~/.local/state/linxira-update/status.json`: `check_status` (ok/error/incomplete), `available_update_count`, `last_check`, `reboot_required`; the automatic path also records `auto_apply` and `pre_snapshot_id`. When a check is incomplete, a count of 0 does not mean the system is up to date.

The scheduled check is the user timer `linxira-update.timer` (two minutes after boot, then hourly, `Persistent=true`), enabled by the package preset `80-linxira-update.preset` on first login. It runs `linxira-update.service`, which executes `linxira-update --check` with `LINXIRA_UPDATE_UNATTENDED=1`. The Welcome update card and the tray are only its presentation layer.

## Automatic pre-update snapshots and fully automatic updates

- On an installed system with Timeshift enabled, a PreTransaction hook creates a Timeshift snapshot before any pacman transaction (the 20 most recent are kept). With Timeshift and grub-btrfs fully configured, snapshots enter the GRUB menu automatically, can be booted read-only to verify, and then rolled back. See the wiki's `updates-and-snapshots` topic (`linxira-wiki show updates-and-snapshots`).
- Add an `EnableAutoApply` line to `~/.config/linxira-update/linxira-update.conf` to turn on fully automatic updates: off by default. Once on, only the unattended `linxira-update.service` triggers it; manual `--check` from the tray or a terminal never applies anything. Five hard gates must all pass: a btrfs root filesystem, Timeshift configured, `grub-btrfs-overlayfs` in the `mkinitcpio` `HOOKS`, `grub-btrfsd` enabled, and a usable privilege-elevation command. Only then does it explicitly create and verify a snapshot (`timeshift --create`, then confirm the snapshot appears under its comment) and run `pacman -Syu --noconfirm`. Any failure keeps it at check + notify and records the reason.

## When root is required

Checking, listing, the tray, notifications and `--gen-config`/`--show-config` need no root. Applying updates raises privileges through `PrivilegeElevationCommand`, which accepts only `sudo`, `sudo-rs`, `doas` or `run0` and defaults to `sudo`. The automatic path uses `pacman -Syu --noconfirm`, only ever for a full upgrade, never a partial one.

## Known limitations

- AUR and Flatpak are off by default and require `EnableAUR` / `EnableFlatpak` in the configuration file. Installed foreign packages named `linxira` or prefixed with `linxira-` are never sent to an AUR helper; if no pacman repository provides them, the check is reported as incomplete.
- A zero `available_update_count` means "up to date" only when `check_status` is also `ok`.
- Automatic updates only happen in the unattended service. A manual check in a terminal or the tray never applies them, even with every gate satisfied.
- The pacman PreTransaction hook creates a pre-update snapshot when `timeshift.json` exists and keeps the 20 most recent. The hook wraps snapshotting in `|| true`, so **a failed snapshot does not stop the pacman transaction**; "a snapshot exists" is not an absolute guarantee.
- The hook fires for Upgrade, Install and Remove. The initial Linxira snapshot is never pruned; boot and daily snapshots keep the 3 most recent each.
- The update check does not replace reading Arch news: news prompts appear only in the interactive flow, while the automatic path only upgrades packages.
- `--tray --enable` works by copying an XDG autostart entry. If that file already exists it fails instead of overwriting your existing login item.

## Deeper design

The implementation is in the [`linxira-update`](https://github.com/Linxira-OS/linxira-update) repository — see [`README-LINXIRA.md`](https://github.com/Linxira-OS/linxira-update/blob/main/README-LINXIRA.md) and `doc/man/`. The command surface and every configuration key are also in the wiki's `update-cli` topic.
