# Components (`linxira-components`)

## Why it exists

Any action in the system that changes the machine needs one uniform shape: compute a plan, let the user see it, execute it as root only after the user confirms, and leave a receipt that can be checked afterwards. Without that shape, every feature calls `sudo` on its own — the user cannot tell what is about to happen, and cannot check afterwards what actually happened.

`linxira-components` is that shape. It is the **only** project that owns transaction planning, confirmation, privileged apply and receipts.

## Scope

**It owns**: catalog reading, target selection, plan generation (`plan`), plan confirmation (`confirm`), execution as root (`apply`), receipt output, inventory and installed-state queries, and executing workspace-guard snapshots and restores.

**It does not own**:

- **Deciding what gets installed.** The software and component lists live in [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog).
- **UI.** The interfaces are in `linxira-package-center` and `linxira-component-manager`; they call this project and do not copy its logic.
- **General settings.** Mirrors, SSH, firewall and so on are in [`linxira-config`](config.md).

## Usage

Day-to-day installation starts in the Quick System Software Setup or Quick System Runtime
Setup UI; below is the CLI entry to the same transaction chain. Three steps, and the
output of each one is a file a human can read before handing it to the next:

```bash
# 1. plan: an installed system ships only catalog-v3.json, which accepts a selection or a fixed bundle
linxira-components plan --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --bundle bundle-python-runtime --output-dir ./out

# 2. confirm (confirms a plan that has not changed)
linxira-components confirm --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --plan ./out/request-plan.json --output-dir ./out

# 3. apply (needs root and authorisation; the GUIs use pkexec, sudo is equivalent in a terminal)
sudo linxira-components apply --confirmation ./out/confirmation.json
```

`--profile` and `--application` are the Catalog v2 compatibility entry points and only work with a v2 catalog file. An installed system ships only `catalog-v3.json`, so day-to-day installation has Package Center or Component Manager write an `org.linxira.component-selection.v1` selection document and pass it to `--selection`.

The workspace guard is another set of actions under the same shape:

```bash
linxira-components-guard status                                 # read-only, no authorisation
linxira-components-guard status --json                          # same state, one line of JSON
linxira-components-guard register ~/Linxira-OS                  # root only; writes the guard registry
linxira-components-guard snapshot ~/Linxira-OS                  # Polkit prompt
linxira-components-guard restore <id> --target ~/ws-restored     # Polkit prompt
```

See [Workspace Guard](workspace-guard.md) for details.

## When root is required

- **Not required**: `list`, `inventory`, `plan`, `confirm`, and `linxira-components-guard status` / `linxira-components-guard list`. Plans and confirmations are pure computation, and the guard's read-only queries report an unconfigured guard instead of asking for authorisation.
- **Root required**: `apply`, plus `linxira-components-guard init|register|unregister`. GUIs call `apply` through `pkexec linxira-components apply`; `sudo` is equivalent in a terminal.
- **Polkit authorisation**: `linxira-components-guard snapshot|restore` go through a system D-Bus plan and confirmation, where Polkit authenticates an administrator. An agent may start them without holding sudo itself.

A drift check sits between the plan file and the apply: if the system state changed between the two steps, that plan is void. This is deliberate — the plan shows the user the system as it was, not as it is now.

## Known limitations

- Only currently available `pacman` leaves from the `arch` source become package targets. AUR, Conda, operation and unavailable leaves are recorded as pending or unsupported and never executed.
- `apply` never performs a system upgrade, never removes packages and accepts no arbitrary pacman arguments; `systemUpgradeRequired` is always `false`.
- Any drift between confirmation and apply — catalog bytes, plan contents or the final leaf set — voids the plan. That is protection, not a stale cache.
- Plans and confirmations must be written into an existing directory under a plain filename; symlinked directories are refused.
- A package's own install scripts and hooks still run inside the Arch package trust boundary; this project does not rewrite them.
- The guard `snapshot` / `restore` actions require the store created by `linxira-config workspace-guard enable`; without it they report "not configured" and stop.

## Deeper design

[Direct Arch architecture](../features/architecture.md) · transaction design and the trust boundary are in [`docs/TRANSACTION_BACKEND.md`](https://github.com/Linxira-OS/linxira-components/blob/main/docs/TRANSACTION_BACKEND.md) in the [`linxira-components`](https://github.com/Linxira-OS/linxira-components) repository.
