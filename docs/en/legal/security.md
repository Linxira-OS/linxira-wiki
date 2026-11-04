# Security & Contribution

This page covers Linxira's signing trust chain, how far security updates actually reach, how to report a problem privately, and how code, documentation, translations and skills get merged. The official security centre at <https://linxira-os.github.io/en/security/> is authoritative; this page is the wiki's entry point and explanation.

## Security model

| Mechanism | What it does | Where it stops |
|---|---|---|
| `[linxira]` package and repository database signatures | pacman verifies at install time that a package came from Linxira and was not altered | It proves origin and integrity, not that the code is free of vulnerabilities |
| Ed25519 key separation | The master (Certify) key stays offline; day-to-day signing uses the signing subkey | Rotation and custody happen offline on the maintainer side; users only trust the public key shipped in the keyring |
| Keyring distribution | Installing Linxira or adding `[linxira]` makes pacman import and trust the signing key automatically, with no manual step | Key material is only distributed through official release announcements and repository metadata; fingerprints are not published on the site |
| Rolling security updates | Arch security patches reach the system with the next `pacman -Syu`, with no extra freeze cycle | Speed depends on upstream; local changes are still yours to track |
| Dual kernel | `linux` and `linux-lts` coexist, so a broken single-kernel update can be rolled back | It is not automatic rollback: you pick the other kernel at the boot menu |
| Pre-update snapshots | A Timeshift snapshot is created before the update transaction and can be booted from the GRUB menu | Snapshots live on the local disk; if the disk dies, they die with it |
| No telemetry | Nothing is collected | Only when you explicitly run the diagnostic collect/upload command does a bundle leave the machine, over the channel you chose |

## Signing and the trust chain

All Linxira packages and repository databases are signed with the project's own key and verified by pacman at install time. The keys are Ed25519: the master key only manages subkeys and stays offline, while everyday package and repository signing uses the signing subkey.

The signing public key ships with the system keyring package. Installing Linxira or adding the `[linxira]` repository makes pacman import and trust that key automatically, with no manual `pacman-key` work. Key material is only distributed through official release announcements and repository metadata; fingerprints are not published on the site.

!!! note "Signatures answer the origin question"
    Verification answers "was this package built by Linxira and unmodified in transit", not "does this code have a bug". The latter depends on upstream fixes and on how often you update.

## Security updates

- **Rolling updates**: the kernel, glibc, browsers and the rest are Arch's own builds. Once an upstream advisory is published, the fix arrives with your next `pacman -Syu`, with no distro freeze in between. Use `arch-audit` to check your machine for known issues; upstream advisories live at <https://security.archlinux.org/>.
- **Dual-kernel safety net**: `linux` and `linux-lts` coexist. If a kernel update leaves the system unbootable, pick the other kernel at the boot menu.
- **Pre-update snapshots**: `linxira-update` creates a Timeshift snapshot before the transaction. Snapshots enter the GRUB menu automatically, can be booted read-only to check first, and can then be rolled back. Enabling snapshots and their policy belongs to the `timeshift` subcommands of `linxira-config`.
- **Signature enforcement**: repository databases and packages are verified on the pacman side; unsigned packages or packages with a mismatched signature are not accepted.

!!! warning "Back up before you update"
    A snapshot is not a backup. Keep important data on a separate disk or off-machine copy, and do not attempt a major upgrade or partitioning work on your only device without a way back.

## What the model does not cover

- **AUR**: the AUR is not a repository but a collection of user-submitted build scripts; packages compile on your machine and carry no signature backing. It is disabled by default and no AUR helper is preinstalled. If you use it, read the whole PKGBUILD and any `.install` file and accept the consequences.
- **Third-party and proprietary software**: proprietary drivers and closed-source applications have their own update and security channels; this project cannot patch them for you.
- **Your own edited configuration**: locally modified configuration files are not repaired by package updates; `.pacnew` files need manual merging during upgrades.

## Reporting a vulnerability

Do **not** post exploit details in public issues, discussions or social media. The correct route is:

1. Open the repository of the affected component, for example <https://github.com/Linxira-OS>, and go to the **Security** tab.
2. Choose **Report a vulnerability** to submit through a GitHub Security Advisory; only repository maintainers can see it.
3. Include the affected component and version, the impact (privilege escalation, remote trigger, which data is exposed), minimal reproduction steps, and any proposed fix if you have one.
4. Keep it private until a fix ships; the maintainers will coordinate the public disclosure date with you.

!!! warning "Response is best-effort"
    The project is maintained by an individual / small team, with no 24/7 security response team and no promised response time. Unless a repository explicitly says otherwise, there is no monetary bug bounty. Reports that reproduce locally with a clear scope get handled faster.

## Contribution model

- **Public repositories and pull requests**: code, documentation, translations and skills are all submitted to the relevant public repository and merged after review. CI runs boundary checks and builds first; changes that fail it are not merged.
- **Review is required**: every change goes through maintainer review. There is no merge-first-fix-later path, including for security-related changes.
- **AI-assisted contributions**: they go through the same public submission and review as any other contribution, and the submitter remains responsible for the correctness and licence compliance of what they submit.
- **Security fixes are coordinated privately**: a vulnerability does not go through a public pull request until the fix and release are ready, so details are not exposed before users can patch.
- **Licensing**: [License & Legal](license.md) explains the code and documentation licences; submitting a contribution means you agree to release it under the relevant repository's licence.

## Further reading

- [Official security centre](https://linxira-os.github.io/en/security/)
- [Contributing guide](https://linxira-os.github.io/en/docs/contributing/)
- [Maintenance, trust and software security](https://linxira-os.github.io/en/docs/maintenance-security/)
- [License & Legal](license.md)
- [Update assistant (`linxira-update`)](../software/update.md): how updates and snapshots actually behave

---

[Back to the wiki home](../index.md)
