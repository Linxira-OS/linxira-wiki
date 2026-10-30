# Components (`linxira-components`)

## Why it exists

Any action in the system that changes the machine needs one uniform shape: compute a plan, let the user see it, execute it as root only after the user confirms, and leave a receipt that can be checked afterwards. Without that shape, every feature calls `sudo` on its own — the user cannot tell what is about to happen, and cannot check afterwards what actually happened.

`linxira-components` is that shape. It is the **only** project that owns transaction planning, confirmation, privileged apply and receipts.

## Scope

**It owns**: catalog reading, target selection, plan generation (`plan`), plan confirmation (`confirm`), execution as root (`apply`), receipt output, inventory and installed-state queries, the Timeshift-style snapshot backend, and executing workspace-guard snapshots and restores.

**It does not own**:

- **Deciding what gets installed.** The software and component lists live in [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog).
- **UI.** The interfaces are in `linxira-package-center` and `linxira-component-manager`; they call this project and do not copy its logic.
- **General settings.** Mirrors, SSH, firewall and so on are in [`linxira-config`](config.md).

## Usage

Three steps, and the output of each one is a file a human can read before handing it to the next:

```bash
# 1. plan
linxira-components list --catalog /usr/share/linxira/catalog/catalog-v3.json --json
linxira-components plan --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --profile workstation --output-dir ./out

# 2. confirm (confirms a plan that has not changed)
linxira-components confirm --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --plan ./out/request-plan.json --output-dir ./out

# 3. apply (needs root and authorisation)
linxira-components apply --confirmation ./out/confirmation.json
```

The workspace guard is another set of actions under the same shape:

```bash
linxira-components guard status                                  # read-only, no authorisation
linxira-components guard register ~/Linxira-OS                  # root only; writes the guard registry
linxira-components guard snapshot ~/Linxira-OS                  # Polkit prompt
linxira-components guard restore <id> --target ~/ws-restored     # Polkit prompt
```

See [Workspace Guard](workspace-guard.md) for details.

## When root is required

- **Not required**: `list`, `inventory`, `plan`, `confirm`. Plans and confirmations are pure computation.
- **Required**: `apply`, and the guard actions `init` / `register` / `unregister` / `snapshot` / `restore`. The guard snapshot and restore go over D-Bus and Polkit asks the user for authorisation, so the agent does not need to hold sudo itself. `guard init` / `register` / `unregister` edit a root-owned registry and must be run as administrator.

A drift check sits between the plan file and the apply: if the system state changed between the two steps, that plan is void. This is deliberate — the plan shows the user the system as it was, not as it is now.

## Deeper design

[Direct Arch architecture](../features/architecture.md) · internals are in the `document/` directory of the [`linxira-components`](https://github.com/Linxira-OS/linxira-components) repository.
