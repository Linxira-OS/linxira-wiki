# Software Catalog (linxira-catalog)

## Why it exists

The installer, Package Center, Component Manager and Welcome all need to know which
software exists, how it is categorised, what is selected by default and whether it can
install offline. With a separate list per surface, IDs, defaults and review states drift.

`linxira-catalog` is the single reviewed, versioned source of software component metadata.
It describes software and the selection model; it never performs a package transaction.

## Responsibilities

**It owns**:

- `catalog-v3.json`: the graph of `desktops[]`, `applications[]`, `components[]`,
  `bundles[]`, `operations[]` and `categories[]`.
- `schema/*.schema.json`: JSON Schema Draft 2020-12 contracts, validated in the build.
- Stable leaf IDs shared by the installer, managers, plans, receipts and CLI handoffs.
- Offline policy: `included`, `online-only` and `defer-with-consent`, so every install
  surface shows the same badge.
- `catalog-v2.json` as a compatibility input for existing consumers. v3 does not replace
  the v2 `profiles[]` model.

**It does not own**:

- Planning, confirmation, execution or receipts — that is [Components](components.md).
- A user-facing command. The package installs data and schemas, not a CLI.
- Executable command strings. `operations[]` contains fixed, controlled operation IDs only.

## How to use

Users do not call this repository directly. The `linxira-catalog` package installs:

```text
/usr/share/linxira/catalog/catalog-v3.json
/usr/share/linxira/catalog/catalog-v3.schema.json
```

Consumers read those fixed paths and present them in their own UI:

| Consumer | Purpose |
|---|---|
| Installer | Desktop, application and component selection during installation |
| [Package Center](https://github.com/Linxira-OS/linxira-package-center) | Installed-state and software presentation |
| [Component Manager](https://github.com/Linxira-OS/linxira-component-manager) | Runtime, tool and capability state |
| [Completion Agent](https://github.com/Linxira-OS/linxira-completion-agent) | First-online completion plan |
| [Components](components.md) | Transaction plans built from leaf IDs |

Maintainer validation:

```bash
python -m unittest discover -s tests -v
```

Validation covers schemas, category-root ID pairs and all global IDs, references,
`primaryCategory` ownership, bundle surfaces, nested-bundle acyclicity, duplicate members,
provider/source boundaries, review-channel policy, offline policy and selection modes.

## When root is required

Never. The catalog is read-only data; writes happen only during repository development and
packaging.

## Known limitations

- The installed package ships v3 data and schema only. v2 remains in the repository for
  older consumers; do not reuse the v2 `profiles[]` capability model in v3.
- External ecosystems (AUR, Conda, proprietary software) are disabled by default and need
  explicit opt-in. Pending candidates stay in the review channel and are never default-selected.
- Installer-eligible leaves also require `review.status == "reviewed"`.
- Selection and receipts are keyed by leaf ID, not by tree path; removing a leaf or
  changing a stable ID affects every downstream consumer.
- The catalog lists package identifiers and metadata, not installation commands. Being in
  the catalog does not mean the software is installed.

## Design notes

See [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog). How transactions
consume leaf IDs is described in [Components](components.md).
