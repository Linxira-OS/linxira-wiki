# Package Center (linxira-package-center)

The UI calls itself **Quick System Software Setup**.

## Why it exists

Shelly is the general software center. This workstation also needs a place that only
offers reviewed applications. `linxira-package-center` is that place: an install-only
PySide6 application that reads Catalog v3 by default, presents applications in an
expandable category tree, creates a catalog-bound plan, shows that plan unchanged, and
hands the privileged transaction to `linxira-components`.

It never builds package commands, never invokes pacman, and never duplicates backend
validation.

## Responsibility boundaries

**It owns**: selection UI, transaction presentation, progress, installed-state
presentation, and the continuation prompt for software deferred during installation.

**It does not own**:

- **Plan, confirmation and privileged apply.** Those belong to
  [Components](components.md); this UI only calls them.
- **Metadata and policy.** Which applications exist, how they are grouped and whether
  they are recommended comes from
  [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog).
- **Configuration and diagnostics.** Mirrors, SSH and firewall belong to
  [Config](config.md).
- **Removal.** Phase 1 installs only. There is no removal entry point until the shared
  backend has an ownership ledger, dependency attribution and drift detection.

## How to use

```bash
linxira-package-center
```

There are no command-line arguments; the menu entry runs
`/usr/bin/linxira-package-center`. Environment variables:

| Variable | Default | Effect |
|---|---|---|
| `LINXIRA_CATALOG_PATH` | `/usr/share/linxira/catalog/catalog-v3.json` | Catalog to read |
| `LINXIRA_INSTALLED_STATE_PATH` | unset | Optional installed-state document; without it the Installed view is empty and the rest of the catalog works normally |
| `LINXIRA_PENDING_INSTALL_PATH` | `/var/lib/linxira/pending-install.json` | Applications deferred during installation; the file is deleted once they are all installed |

The transaction backend is fixed at `/usr/bin/linxira-components`, and elevation is
fixed at `/usr/bin/pkexec`.

The flow:

1. Pick a view in the **Display** filter: reviewed and installable, included in the
   image (offline), requires network, installed, or third-party review channel
   (view-only, opt-in).
2. Expand a category and tick applications. Categories use `multi`, `exclusive`
   (at most one) or `bounded` (`maxSelected`) selection; a partial checkbox means only
   some children are selected. Installed items are locked selected leaves: they cannot
   be cleared and are never submitted as removals.
3. Click **Install selected software**. If the selection contains proprietary software
   that requires acceptance, a confirmation dialog appears first and the acceptance is
   recorded in the plan.
4. The UI writes an `org.linxira.component-selection.v1` document (bound to the
   catalog SHA-256 and release) and calls `linxira-components plan`, then shows the
   immutable `request-plan.json` in a **Confirm installation plan** dialog.
5. After you confirm, it runs `linxira-components confirm` and then
   `pkexec linxira-components apply --confirmation ...`, reporting progress in the
   status bar. Cancellation or failure removes the temporary transaction directory.

Installed state is optional. The document may contain `installedApplications: [id, ...]`
or an `applications` map whose values carry an installed state. Applications in
`partial` state are preselected and completed on install, as are items listed in the
pending-install document.

## When root is needed

The UI runs as your normal user. `plan` and `confirm` are pure computation; only
`apply` goes through `pkexec`, where Polkit asks you for authorization. Do not run the
UI as root and do not wrap it in `sudo`.

## Known limitations

- **Install only (Phase 1).** There is no uninstall, downgrade or rollback; installed
  applications are shown as locked state.
- **The third-party review channel is read-only.** AUR, WPS, proprietary and
  mixed-license candidates show provider, source, license, review state and opt-in
  requirements, but stay disabled.
- **Category roots need catalog support.** Using an application category as a
  transaction root requires a catalog bundle with the same ID, exactly the same direct
  children, all marked `optional`. The standalone Catalog v3 has no such contract yet,
  so planning fails closed before the backend is called. The UI never forges a bundle
  path.
- Catalog v2 is still supported, but entries must be `installer: true` with
  `review.status: reviewed`.
- Drivers, kernels and system updates are out of scope; they have their own tools and
  transaction boundaries.

## Further reading

Product boundaries are in the repository's `docs/BOUNDARIES.md`. The transaction shape
is described under [Components](components.md); implementation lives in
[`linxira-package-center`](https://github.com/Linxira-OS/linxira-package-center).
