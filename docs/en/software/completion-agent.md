# Completion Agent (linxira-completion-agent)

## Why it exists

The installer deliberately defers some software: it needs a network, needs extra
licence acceptance, or the provider behind it is not implemented yet. Those items must
not disappear silently — you need to see what is left, why, and what installing it would
change. `linxira-completion-agent` is the screen that lays out the software explicitly
deferred in the installer receipt.

It binds the recorded catalog to that receipt and shows source, size, licence,
repository impact and deferability per item. It accepts **no** package names, commands,
URLs or repository definitions.

## Responsibility boundaries

**It owns**: reading the explicitly deferred entries from the installer receipt,
presenting source and licence information, collecting explicit confirmation for
sensitive items, and recording the deferred or completed state.

**It does not own**:

- **Install decisions.** Which items may install, through which source and whether
  acceptance is required comes from the catalog and the receipt.
- **Package transactions.** When applying, it also goes through the
  [Components](components.md) `plan → confirm → apply` chain, with `pkexec` handling
  elevation.
- **The installer's job.** Reviewed official Arch applications and components must be
  installed into the Calamares target before first boot; a receipt that defers such an
  item to Completion is rejected.

## How to use

```bash
linxira-completion-agent             # from the application menu or a terminal
linxira-completion-agent --autostart # what the first-login entry runs
```

The table has six columns: software, source, size, licence, repository change and state.
State is either `Ready` or `Deferred`. Items with proprietary licences or an opt-in
requirement add a confirmation checkbox that must be ticked individually.

Two actions:

- **Defer** records the whole plan as deferred and closes the window.
- **Complete ready items** is enabled only when the network is available (checked via
  `nmcli`), at least one item is ready, and every sensitive item is ticked. It writes a
  selection document to a temporary directory, runs `linxira-components plan` and
  `confirm`, then `pkexec` runs `apply`.

Inputs are fixed: `/usr/share/linxira/catalog/catalog-v3.json` and
`/var/lib/linxira/installer-selection.json`. If either is a symlink, the receipt schema
is unsupported, the catalog changed after the receipt was written, or the
classifications disagree, the program prints the reason and exits with status 2.

State lives in `${XDG_STATE_HOME:-$HOME/.local/state}/linxira/completion/state.json` and
records the catalog and receipt SHA-256 values. With `--autostart`, a previous status of
`complete` or `deferred` exits immediately, and already succeeded items are not shown
again.

## When root is needed

Not at all. The agent runs as your normal user and only reads the catalog and receipt.
If something is applied, `pkexec` requests Polkit authorization. The agent never
elevates on its own and accepts no root commands.

## Known limitations

- **The current implementation is a review and defer surface.** Every deferred entry is
  classified `Deferred` (the executable flag is always false), so **Complete ready
  items is never enabled**. The `plan/confirm/apply` path exists but no item reaches it
  today.
- Only leaves listed in the receipt's `pendingItems` are shown; installed or unselected
  items never appear.
- Operation leaves wait for their dedicated system action. AUR, Flatpak, Conda,
  proprietary and review-channel items each wait for their provider and review contract.
- Only Catalog v3 and the `org.linxira.installer.selection-receipt.v1` receipt are
  accepted; a receipt that does not classify every selected item exactly once is
  rejected.
- It does not install reviewed official Arch applications or components; that belongs to
  the installer, and deferring them is treated as an error.

## Further reading

Receipt/catalog binding rules, item classification and the state file format are in the
[`linxira-completion-agent`](https://github.com/Linxira-OS/linxira-completion-agent)
repository. The transaction shape is described under [Components](components.md).
