# License & Legal

This page answers two questions: what license covers this wiki and Linxira's code, and what risk you take on when you use that content and software. The official page at <https://linxira-os.github.io/en/legal/license/> is authoritative; this page is the wiki's explanation and entry point, and the official page wins where the two differ.

## This wiki's license

Two kinds of content live in this wiki, under different licenses:

| Content | License | Notes |
|---|---|---|
| Page text under `docs/**` | **CC BY-SA 4.0** | Attribution + share-alike |
| Site code (build scripts, theme components, wiki CLI) | **MIT** | See the repository `LICENSE` |
| Source snippets quoted in page text | The owning repository's license | Quoting does not relicense the original |

In practice: reading, republishing and translating these pages is allowed, provided you keep attribution and release your modified version under CC BY-SA 4.0 as well.

### What CC BY-SA 4.0 means in practice

- **Attribution**: when you republish, translate or excerpt, keep the source (Linxira OS documentation), a link to the original page and the license notice.
- **Share-alike**: a modified document must be released under CC BY-SA 4.0 (or a compatible license); you cannot add stricter terms.
- **Commercial use is allowed**: CC BY-SA does not forbid it, but the attribution and share-alike obligations still apply.
- **Attribution is not endorsement**: naming the source does not mean the project endorses your version or service.
- **Snippets follow their repository**: a command or configuration fragment quoted from a code repository stays under that repository's `LICENSE`.

!!! note "The document/code boundary"
    One repository can carry both licenses. In `linxira-wiki` the build scripts and CLI are MIT, while the page text under `docs/**` is CC BY-SA 4.0. Judge by file location and the repository's own statement, not by the repository name.

## Code is licensed per repository

Every repository ships its own `LICENSE`; there is no single project-wide code license:

| Repository | License | Evidence |
|---|---|---|
| Most first-party repositories, e.g. `linxira-catalog`, `linxira-config-hub`, `linxira-component-manager`, `linxira-welcome`, `linxira-crash-watch`, `linxira-package-center` | MIT | Repository `LICENSE` |
| `linxira-update` | GPL-3.0-or-later | `LICENSE` holds the full GNU GPL v3 text; the README and SPDX headers declare "or any later version" |
| `linxira-hooks` | GPL-3.0-or-later | `LICENSE` holds the full GNU GPL v3 text; the `PKGBUILD` `license=` field is `GPL-3.0-or-later` |
| `linxira-hwd-detector` | GPL-3.0-only | `LICENSE` holds the full GNU GPL v3 text; `Cargo.toml` and the README both say `GPL-3.0-only` |
| `linxira-bio-sdk` | AGPL-3.0-or-later | `LICENSE` holds the full GNU AGPL v3 text; `Cargo.toml` says `AGPL-3.0-or-later` |

Repositories that modify upstream code (for example `linxira-update` and `linxira-hwd-detector`) also carry an `UPSTREAM.md` recording the upstream project, its license and the local changes.

!!! warning "Check “or later” per repository"
    The `LICENSE` files of `linxira-update` and `linxira-hooks` are the plain GNU GPL v3 text; the "or any later version" wording comes from repository metadata and source declarations (the README and SPDX headers in `linxira-update`, the `PKGBUILD` `license=` field in `linxira-hooks`). `linxira-hwd-detector` is explicitly `GPL-3.0-only` and offers no upgrade to later versions. To settle a repository, read its `LICENSE`, package metadata and source headers — not this table.

## Brand assets

Logos, wallpapers, icons and other brand assets are reserved Linxira property. They are **not** covered by the documentation's CC BY-SA 4.0 grant and are not offered under a general public license. Read the [brand assets policy](https://linxira-os.github.io/en/docs/brand-assets/) before redistributing, modifying or reusing them in another project.

## Upstream and non-free components

- **Upstream components keep their own licenses**: the base system, kernel, GNU tools, browsers and office suite remain licensed by their upstream projects. Shipping them together in one distribution does not put the whole system under a single license.
- **The boundary of GPL copyleft**: running Linxira OS locally is not restricted by copyleft; building a derivative distribution is where upstream licenses apply; your own configuration and scripts are unaffected unless they include GPL code.
- **Non-free components are optional**: proprietary firmware for some hardware, NVIDIA drivers, VS Code and Chrome are not free software. They are installed by user choice, and Linxira OS does not mandate non-free software. Their own terms take precedence over this page.
- The full upstream component list, license texts and per-item notes live on the [official license page](https://linxira-os.github.io/en/legal/license/).

## Legal risk and disclaimer

!!! warning "The software is provided “as is”"
    Linxira OS comes with no warranty of any kind. The project is maintained by an individual / small team with no foundation or company as a legal entity behind it, and offers no SLA or commercial support. Data loss, downtime or other damage from using the system is your own responsibility.

| Risk | What it looks like | What to do |
|---|---|---|
| Test images and rolling releases | Images may be test builds; rolling updates keep bringing upstream changes, and a given update can temporarily break a feature | Do not chase the newest build on your only production machine; make sure a rollback snapshot exists |
| The update itself | `pacman -Syu` is a system-wide transaction | Back up important data; keep the pre-update Timeshift snapshot |
| Root operations | An elevated command (partitioning, deleting, overwriting configuration) has no undo | Read the command before running it; never paste an unexplained root command |
| Third-party and proprietary software | Proprietary drivers and closed-source apps carry their own terms and support channels | Check the license and the source before installing |
| AUR | AUR packages are not an official repository, are disabled by default, are compiled locally and carry no signature backing | Read the whole PKGBUILD and any `.install` file; only use packages whose risk you accept |
| No legal entity | No commercial contract, indemnity or compliance commitment can be offered | Assess your own compliance requirements |

## Terms of use

The project's public usage rules, which are not a contract:

- **Lawful use**: do not use Linxira OS or its components for unlawful purposes.
- **No abuse of shared services**: mirrors, package repositories, CI and the issue tracker are public resources; do not degrade them for others with automated traffic, spam or abuse.
- **No impersonation**: republishing or redistributing must not suggest official Linxira endorsement.
- **Third-party terms apply**: once you install third-party or proprietary software (including AUR packages), its license and terms bind you, and this project does not vouch for it.
- **No warranty**: software and documentation are provided "as is", without express or implied warranty.
- The authoritative wording is on the [official legal page](https://linxira-os.github.io/en/legal/license/); this page adds no contractual obligation.

## Further reading

- [Official license page](https://linxira-os.github.io/en/legal/license/)
- [Brand assets policy](https://linxira-os.github.io/en/docs/brand-assets/)
- [Security and contribution](security.md)
- [Maintenance, trust and software security](https://linxira-os.github.io/en/docs/maintenance-security/)
- [Contributing guide](https://linxira-os.github.io/en/docs/contributing/)
- [Update assistant (`linxira-update`)](../software/update.md): the boundaries of pre-update snapshots
- [Software index](../software/index.md)

---

[Back to the wiki home](../index.md)
