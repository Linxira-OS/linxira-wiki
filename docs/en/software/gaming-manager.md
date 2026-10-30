# Gaming Manager (linxira-gaming-manager)

## Why it exists

Gaming on Arch means assembling several pieces yourself: finding Steam libraries,
giving non-Steam Windows games a compatibility layer, remembering each game's
environment, checking whether UMU, Wine, GameMode and MangoHud are installed, and
keeping a restorable backup for when tinkering goes wrong. The pieces are related but
nothing ties them together.

`linxira-gaming-manager` is that per-user workspace. It discovers Steam libraries,
imports non-Steam executables, launches games with fixed argument arrays, detects
compatibility tools, creates explicit restic backups, and deploys the reviewed gaming
environment through a catalog-bound plan. It never sends package transactions or calls
a package manager directly.

## Responsibility boundaries

**It owns**: library discovery and import, per-game managed prefixes, launch and logs,
compatibility tool status, presentation of the gaming environment deployment, and
starting and recording restic backups.

**It does not own**:

- **Package installation.** Deployment requests only `bundle-gaming-setup` from the
  catalog; plan, confirmation and privileged apply belong to
  [Components](components.md).
- **Steam itself.** Sign-in, installation and updates stay with the Steam client.
- **Backup passwords.** It passes only the password file path to restic and never stores
  the contents.
- **System configuration.** Drivers, kernels and services belong to their own tools.

## How to use

```bash
linxira-gaming-manager
```

There are no command-line arguments; the menu entry runs
`/usr/bin/linxira-gaming-manager`. It **must run as a normal user** — started as root it
prints an error and exits with status 1.

Environment variables:

| Variable | Default | Effect |
|---|---|---|
| `LINXIRA_GAMING_STATE_PATH` | `${XDG_DATA_HOME:-$HOME/.local/share}/linxira/gaming-manager/state.db` | SQLite library and activity database |
| `LINXIRA_STEAM_ROOTS` | `${XDG_DATA_HOME:-$HOME/.local/share}/Steam`, `$HOME/.steam/steam`, `$HOME/.local/share/Steam` | Colon-separated Steam root directories |

### Library

- **Refresh** scans `steamapps/libraryfolders.vdf` and `appmanifest_*.acf` in each Steam
  root and upserts the games into the local library.
- **Import game** accepts only `.exe` files, then asks for a runner: **UMU-Proton
  (recommended)** or **System Wine**. Each imported game gets a managed prefix at
  `${XDG_DATA_HOME:-$HOME/.local/share}/linxira/gaming-manager/games/<id>/prefix`.
- **Launch** runs Steam games as `/usr/bin/steam steam://rungameid/<appid>`, and imported
  games through `/usr/bin/umu-run` or `/usr/bin/wine` with the executable's directory as
  the working directory, `WINEPREFIX` pointing at the managed prefix, and an allowlisted
  environment. Merged output is written to
  `${XDG_STATE_HOME:-$HOME/.local/state}/linxira/gaming-manager/games/<id>/logs/<timestamp>.log`
  (at most 1 MiB captured). A second launch of a running game is refused.

### Compatibility

The tool table lists Steam, UMU Launcher, Wine, Protontricks, Winetricks, restic,
GameMode, Gamescope and MangoHud, showing `Not installed` when missing.

**Deploy gaming environment** first explains what will be installed: the official Arch
Steam package, UMU-Proton, Wine, GameMode, MangoHud, Gamescope, Protontricks, VKD3D and
the Intel/AMD open Vulkan runtimes, plus a notice that Steam is proprietary and that
continuing records your explicit acceptance of Valve's Steam Subscriber Agreement.
After you confirm, it requests `bundle-gaming-setup`, shows the immutable package
targets, and on a second confirmation runs `confirm` followed by `pkexec apply`.

### Backups

Fill in **Prefix or save directory**, **restic repository** and **Password file**, then
click **Create backup**. It runs `restic --repo <repository> backup <source> --json` with
`RESTIC_PASSWORD_FILE`. The password file must exist and the source must be a
directory; the repository is opened and validated by restic itself, and a missing
`restic` is reported as an error.

### Activity

Launches, imports, deployments and backups are recorded in the local activity table
(the last 100 entries are shown).

## When root is needed

The program **refuses to run as root**. Only the `apply` step of an environment
deployment goes through `pkexec`, where Polkit asks you. Library scans, imports, launches
and backups never elevate; backups writing outside your home directory succeed or fail
according to filesystem permissions.

## Known limitations

- The deployed package set is fixed by the catalog's `bundle-gaming-setup`; the program
  cannot add or remove targets, and a catalog without that bundle fails planning.
- Only `.exe` files can be imported. Native Linux games are not managed (Steam library
  entries are launched through Steam).
- There is no UI to delete or uninstall a game or library entry, and no way to cancel a
  running backup.
- The window cannot be closed while a game, backup or setup operation is running.
- Backups require `restic` to be installed; the program does not install it.
- Runner paths are fixed at `/usr/bin/umu-run` and `/usr/bin/wine`; if one is missing,
  launch reports it as unavailable instead of falling back.

## Further reading

The state database is local SQLite; launch rules, prefix boundaries and the backup
command are documented in
[`linxira-gaming-manager`](https://github.com/Linxira-OS/linxira-gaming-manager). The
transaction shape is described under [Components](components.md).
