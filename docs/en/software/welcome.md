# Welcome (linxira-welcome)

## Why it exists

The first screen after boot should not be an empty desktop. `linxira-welcome` is a
Plasma-native status and routing surface: on the Live ISO it puts installation first;
on an installed system it reports whether the machine is ready and which first-run
steps are still pending, then offers a fixed allowlist of Linxira tools.

It only reads the versioned software catalog and the installer receipt. It does not
list installable software, and it never builds or executes shell strings, package
transactions, `sudo` or `pkexec`.

## Responsibility boundaries

**It owns**: the five pages (Home, Status, Terminal, System, Help), Live vs installed
detection, health and first-completion state, language selection, the show-at-login
preference, the fixed launcher allowlist, and handing `linxira-config` subcommands to
a terminal.

**It does not own**:

- **Software installation.** Applications belong to
  [Package Center](package-center.md); runtimes and components belong to
  [Component Manager](component-manager.md).
- **Privilege escalation.** Every tile launches a fixed program with fixed arguments;
  there is no `sudo` and no `pkexec`.
- **Catalog content.** Applications, categories and component subcommands stay with
  their own products.
- **Configuration.** The System page only opens `linxira-config` subcommands in a
  terminal; the settings live in [Config](config.md).

## How to use

```bash
linxira-welcome              # from the application menu or a terminal
linxira-welcome --autostart  # what the login entry runs
```

The menu entry is `/usr/bin/linxira-welcome`; the autostart entry appends
`--autostart`. With `--autostart`, Welcome exits immediately if you cleared
**Show Welcome at login** on the Help page.

The five pages:

- **Home.** Live shows the install banner; clicking install writes the selected UI
  language to `/tmp/linxira-installer-lang` and starts
  `/usr/local/bin/linxira-installer-shell`, so the installer continues in the same
  language. Installed shows health and first-completion tiles. If installation left
  deferred software or components behind, continuation banners open Package Center or
  Component Manager respectively. Below that is the launcher grid: Software Center
  (Shelly), Quick System Software Setup, Quick System Runtime Setup, Config CLI in a
  terminal, System Settings and Terminal; an installed system also gets System Update,
  Gaming Manager, Hardware and Drivers and Recovery Diagnostics.
- **Status.** Release, kernel, network, catalog availability and review, installer
  receipt status, available updates, last check, reboot flag, and the profiles and
  applications chosen during installation.
- **Terminal.** bash is the system default and always installed. For fish, nushell or
  zsh the button opens Quick System Runtime Setup with `--select`; the transaction
  stays there. If the shell is already installed but is not your login shell, the
  button only copies `chsh -s /usr/bin/fish` (with the chosen path) to the clipboard.
- **System.** Reads the capability manifest installed by `linxira-config-hub` and
  renders only commands carrying `welcome` metadata. Each tile opens the matching
  `linxira-config` subcommand in a terminal. Mutating entries are skipped unless they
  opt in; laptop-only entries are hidden when the chassis is not portable and no
  `BAT*` device exists.
- **Help.** Links to Arch Linux News, the Linxira Wiki, ArchWiki, the project site,
  the repository and the issue tracker, plus the show-at-login checkbox.

The language selector offers English, Simplified Chinese, Traditional Chinese, German,
Spanish, French, Japanese, Korean, Brazilian Portuguese and Russian. The choice is
persisted; unsupported locales fall back to English.

## When root is needed

**Never.** Welcome has no elevation path: launchers use fixed executables and fixed
argument vectors, Config CLI is opened inside Konsole, and the Terminal page leaves
`chsh` for you to run. Anything requiring root goes through the owning tool and its
own authorization model.

## Known limitations

- It is an entry and status surface, not a live monitor of the other tools.
- The System page depends on `/usr/share/linxira/agent/capabilities.json` from
  `linxira-config-hub`; when it is missing the page is empty.
- Terminal dispatch is capability based: `konsole`, `alacritty` and `xterm` accept a
  command directly; `cosmic-term`, `kitty` and `foot` are started through a throwaway
  `Terminal=true` desktop entry via `gtk-launch`, so those entries fail without
  `gtk-launch`.
- The Live ISO uses an ephemeral profile, so Welcome opens on every fresh Live boot and
  the login preference does not persist across boots.
- Ten UI languages are shipped; everything else falls back to English.

## Further reading

Implementation lives in the
[`linxira-welcome`](https://github.com/Linxira-OS/linxira-welcome) repository. Catalog
and receipt contracts are described under [Catalog](catalog.md) and
[Package Center](package-center.md).
