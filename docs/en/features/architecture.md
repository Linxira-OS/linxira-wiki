# Direct Arch architecture

Linxira OS is built directly on Arch Linux. It uses the official Arch repositories, `pacman` and the rolling-release model. It does not go through Debian, Ubuntu or Linux Mint, and there is no compatibility layer translating `pacman` into `apt`.

## Component responsibilities

| Component | Owns | Does not own |
|------|------|--------|
| Linxira Catalog | Versioned, reviewed software sources, categories and workstation preset metadata | Running commands or package transactions |
| Linxira Welcome | Reading the catalog and install receipts, showing workstation state, launching Shelly, Calamares and system tools from a fixed whitelist | Executing shell strings, privilege escalation or package transactions |
| Shelly | Default graphical package management and update transactions, in both the live and installed system | Defining Linxira workstation presets or performing installation |
| Calamares | Installing the Direct Arch base system from the live environment, applying only the presets the catalog permits | Day-to-day software management after installation |
| Config Hub CLI | Managing Linxira mirrors, reviewed workflows and system configuration entry points | Keeping a separate package list or replacing the catalog |

## Data and transaction boundary

`/usr/share/linxira/catalog/catalog-v2.json` is the single metadata source for workstation presets. The catalog stores package identifiers and review information only; it stores no executable commands. Welcome, Calamares and Config Hub all read the same data; Shelly can carry software recommendations and graphical package operations.

Actual package transactions are performed by Calamares, Shelly or a reviewed transaction backend. Welcome only displays information and launches fixed programs. In the live session, therefore, "Install Linxira OS" starts Calamares, and "Open Shelly" hands package and update work to Shelly.

## Default source policy

The base system comes from signed official Arch repositories. AUR, Flatpak, AppImage and third-party binary repositories are disabled by default and must be explicitly enabled by the user. Enabling one source never implicitly enables another.

---

Back to the [wiki home](../index.md) · [software index](../software/index.md)
