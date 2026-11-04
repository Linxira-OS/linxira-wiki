# Zeta (linxira-zeta)

!!! warning "External product — the repository is authoritative"
    Zeta is an externally evolving product. This wiki is only an entry point and does not
    copy its command reference. Installation, CLI reference and configuration live in the
    runtime documentation shipped with the product; that documentation changes between
    releases, so check the repository before relying on it.

Zeta is a Bun-native coding agent distribution built on the OMP runtime. It keeps the
terminal workflow fast and direct while owning its package namespace, product
presentation, release policy and its own local web workspace: one runtime, three surfaces
(terminal, browser, desktop).

## Why it exists

A coding agent usually has one entry point: either a CLI in the terminal or a web or
desktop app. Building all three usually means keeping a separate session store and a
separate settings model per surface, so history, model configuration and workspace state
disagree between them. Zeta puts the terminal, a local web workbench and a desktop shell
on one session tree, one settings model and one gateway API (`/api/*`), so changing
surface does not mean changing state.

## Responsibilities

**It owns**:

- A terminal coding workspace: file reading, search, patching, shell, git, task
  delegation and structured tool output.
- A bundled terminal editor (TTT Editor, maintained as `@linxiraos/editor`), launchable
  in any terminal including over SSH.
- Multi-provider model access, local configuration, OAuth flows, model discovery, session
  recovery and controllable retry behaviour.
- A local web workbench (`zeta serve`) and a desktop shell (`zeta-desktop`, Electron),
  both embedding the same coding-agent runtime.
- Product identity: the `@linxiraos/*` package namespace, the `~/.zeta` config directory,
  branding and the release chain.

**It does not own**:

- It is not a Linxira OS system component. It is absent from the `linxira-os` repository
  governance list and the software ownership table; system installation, updates, drivers
  and desktop integration belong to the respective Linxira OS repositories.
- It does not define the upstream runtime. OMP is the runtime tree it integrates; Pi and
  Pi Web are semantic-port sources, never raw merge sources.
- Internal development and product-process documentation (`document/`) is not user-facing
  and is not packaged.

## How to use

All three surfaces come from the same release artifact; the terminal editor is a separate
package:

| Surface | Entry point | Notes |
|---|---|---|
| Terminal | `zeta` | Opens in the current project directory; `zeta --help` lists commands and options |
| Terminal editor | `zeta-editor` | Separate `@linxiraos/editor` package, works in any terminal including SSH |
| Web workbench | `zeta serve` | Local Next.js app driving the same runtime through the `/api/*` gateway |
| Desktop shell | `zeta-desktop` | Electron tray app embedding the web UI build and the compiled runtime; target machines need neither Bun nor Node |

The released CLI installs from the npm package `@linxiraos/zeta`
(`npm i -g @linxiraos/zeta`, or `bun add -g @linxiraos/zeta`); the machine needs Node 20+
or Bun. The exact install steps, the complete command reference and configuration options
are in the runtime docs linked below — this page does not copy them.

The interface language is per install. The CLI ships complete Simplified Chinese and
English catalogues and resolves the active language from `language` in
`~/.zeta/settings.json`, then the `ZETA_LANG` / `LC_ALL` / `LC_MESSAGES` / `LANG` shell
locale, then the OS UI language, falling back to English. `/language` switches live
without a restart.

Platform support, per the repository's current release matrix:

| Surface | Windows | macOS | Linux |
|---|---|---|---|
| `zeta` CLI | x64 | x64, arm64 | x64, arm64 |
| `zeta-editor` | x64 | — | x64 |
| `zeta serve` | x64 | x64, arm64 | x64, arm64 |
| `zeta-desktop` | x64 | x64, arm64 | x64 |

## Privileges

Zeta runs as the current user; configuration, sessions and command definitions live under
the user's `~/.zeta/`. A user-level global install through npm or Bun is enough, so it
needs no system root and does not take over system package management. System-wide
installation is a distributor decision — for example a Linux downstream repository can pin
and verify the `zeta-desktop` release asset — and that is the distributor's privilege
boundary, not Zeta's behaviour.

## Known limitations

- `zeta-editor` currently ships Windows x64 and Linux x64 platform packages only; there is
  no macOS build.
- The desktop shell covers Windows x64, macOS x64/arm64 and Linux x64; Linux arm64 is not
  in the release matrix.
- Building from source needs Visual Studio Build Tools with the Desktop development with
  C++ workload on Windows, and the platform C/C++ toolchain required by Rust on macOS and
  Linux. Released binaries bundle the prebuilt native modules.
- The repository keeps two documentation trees: only `docs/` ships with the product
  (agents read it at runtime through `zeta://docs/`, or the live tree from a source
  checkout); `document/` is internal development documentation.

## Further design

The authoritative runtime documentation ships with the product at
[linxira-zeta/docs](https://github.com/Linxira-OS/linxira-zeta/tree/main/docs): tools,
tool-call conversion, skills, protocols, configuration and Zeta features, and the place
where installation, CLI reference and configuration are documented. The product overview
and platform matrix are in the
[README](https://github.com/Linxira-OS/linxira-zeta): repository
[Linxira-OS/linxira-zeta](https://github.com/Linxira-OS/linxira-zeta).
