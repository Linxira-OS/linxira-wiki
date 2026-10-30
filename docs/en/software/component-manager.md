# Component Manager (linxira-component-manager)

The UI calls itself **Quick System Runtime Setup**.

## Why it exists

Below applications sits another layer: capability bundles, runtimes, toolchains and
domain workspaces. They have dependencies, exclusions and required members, so
installing them one `pacman` command at a time hides both the relationships and the
reason each package is there. `linxira-component-manager` turns that layer into an
expandable, Windows Features-style tri-state tree: ticking requests an install,
expanding shows the nesting, and the whole plan is visible before anything runs.

The GUI, TUI and CLI share one transaction core, and all four entry points (GUI, TUI,
CLI, agent) follow the same `plan → confirm → apply` chain.

## Responsibility boundaries

**It owns**: the selection UI for Catalog v3 bundle trees (GUI, TUI, CLI), node
metadata and selection previews, and the plan display before confirmation.

**It does not own**:

- **Package name expansion.** It never turns component IDs into package names and never
  invokes a package manager.
- **Planning, confirmation or privileged apply.** Those belong to
  [Components](components.md).
- **Removal.** Phase 1 installs ready package targets only.
- **Metadata.** Bundles, roles and selection policies come from the catalog.

## How to use

### Graphical interface

```bash
linxira-component-manager                          # default catalog
linxira-component-manager --catalog ./catalog-v3.json
linxira-component-manager --select component-fish  # preselect a leaf, repeatable
```

It looks for `/usr/share/linxira/catalog/catalog-v3.json`, then
`/usr/share/linxira/catalog/catalog.json`. With neither, it opens empty; `Ctrl+O`
chooses a file and `Ctrl+S` saves the selection JSON. `--select ID` only preselects:
the transaction still happens in the window. Welcome's Terminal page uses this to hand
over a chosen shell.

Only top-level bundles whose `surface` is `components` are shown (an omitted `surface`
means `components`). The tabs show node details, a live selection JSON and the backend
plan. **Plan with linxira-components** performs a fixed flow:

1. Write the complete `org.linxira.component-selection.v1` document into a private
   temporary directory.
2. Run `linxira-components plan --catalog ... --selection ... --output-dir ...`.
3. Show the immutable `request-plan.json`, including separate ready package targets and
   pending/unsupported summaries.
4. After your confirmation, run `linxira-components confirm` against that exact plan.
5. If `directPackageTargets` is non-empty, run
   `pkexec linxira-components apply --catalog ... --confirmation ...`.

A plan with no direct package targets (only pending or unsupported leaves) is confirmed
without requesting `pkexec`. Pending and unsupported leaves are never applied.

### TUI

```bash
linxira-component-manager --tui
linxira-component-manager --tui --catalog ./catalog-v3.json
```

Keys: arrows (or `k`/`j`) move, space toggles, `a` selects or clears all, Enter creates
the plan and asks for confirmation, `q` or Esc quits. Authorization defaults to `auto`:
running as root applies directly, otherwise it uses `pkexec`.

### Command line

```bash
linxira-component-manager list
linxira-component-manager list --json
linxira-component-manager status component-fish
linxira-component-manager status component-fish --json
linxira-component-manager install component-fish --dry-run
linxira-component-manager install component-fish --yes
linxira-component-manager --catalog ./catalog-v3.json install component-fish
```

- `list` shows available `component` and `application` leaves and reads installed
  states from `linxira-components inventory`; when the backend is unavailable the state
  is `unknown`.
- `status` takes one or more leaf IDs.
- `install` uses the same `plan → confirm → apply` chain. `--dry-run` prints only the
  planned package targets, `--yes` skips the interactive prompt (for agents), and
  `--json` emits machine-readable output. Pending items that cannot be installed are
  reported and skipped.
- Exit codes: `0` success, `2` selection or plan rejected, `3` authorization or apply
  failure, `64` usage error.

## When root is needed

The default authorization mode is `auto`: **as root, apply runs directly; as a normal
user, `pkexec` asks Polkit for authorization.** Planning and confirmation never
elevate. Do not wrap the commands in `sudo`, and do not start the GUI as root.

## Known limitations

- **Phase 1 installs only.** Ready package targets install; removal is not supported.
- Pending and unsupported leaves are listed before confirmation and are never applied.
- There is no `--component`, profile/application, package-manager, remove or shell
  fallback — these are deliberately absent, not merely undocumented.
- It consumes Catalog v3 directly and does not translate v2 profiles or package arrays.
  Direct or indirect cycles in the bundle graph are rejected.
- Required leaves are locked and explained; `exclusive` clears sibling alternatives;
  `bounded` rejects a change beyond `maxSelected` instead of silently truncating.
- Without a usable catalog the CLI fails and asks for `--catalog PATH` or an installed
  `linxira-catalog`.

## Further reading

A complete nested example is in `examples/catalog-v3.example.json` in the repository.
The transaction shape is described under [Components](components.md); implementation
lives in
[`linxira-component-manager`](https://github.com/Linxira-OS/linxira-component-manager).
