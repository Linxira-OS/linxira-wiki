# Signing Keyring (linxira-keys / linxira-keyring)

## Why it exists

pacman can verify `[linxira]` packages and databases only when the release public key is
locally trusted. Asking users to download an ASCII key, import it and set trust by hand is
error-prone and unauditable. The keyring package turns “public key + fingerprint + local
signature” into ordinary software installed with the system.

Private keys are not part of this path: the package distributes the public key, and
signing happens in the maintainers' build environment.

## Responsibilities

**It owns**:

- The `linxira-keyring` package's public key and fingerprint:
  `/usr/share/keyrings/linxira.gpg` and
  `/usr/share/keyrings/linxira-release-fingerprint`. The package ships the binary key
  and the fingerprint file only, not the ASCII key.
- An install script that adds the key to pacman's keyring and locally signs it
  (`pacman-key --add`, `pacman-key --lsign-key`), running as root.
- The key vault (the private `linxira-keys` repository), which holds encrypted private key
  material and the public source files. Vault and GPG passphrases are kept by the key
  holder and are not in any repository.

**It does not own**:

- Package signing; packages and repository databases are signed in the maintainer's
  signing environment, and the release flow lives in the `packages` repository
  (`scripts/publish-repo.sh`).
- Repository hosting; `linxira-packages` is served by GitHub Pages and produces no
  signatures itself.
- Enabling the `[linxira]` repository; that is `/etc/pacman.conf` configuration.
- Removing old keys; `post_remove` is a no-op when the package is removed.
- Private-key recovery. This wiki does not document decryption, private-key import or
  passphrase handling.

## Who does what

| Party | Owns | Does not own |
|---|---|---|
| Private vault `linxira-keys` | The encrypted private keys (`linxira-master-secret.asc.enc`, `linxira-signing-subkey.asc.enc`) and the public source files (`linxira.asc`, `linxira.gpg`) | Signing, distribution, or any passphrase |
| The `linxira-keyring` package in `packages` | Packaging the public key and fingerprint; importing and locally signing them in `post_install` and `post_upgrade` | Signing packages, hosting the repository, or enabling it |
| `linxira-packages` (GitHub Pages) | Hosting packages, `.sig` files, the signed database, `SHA256SUMS` and the repository copy `x86_64/linxira.gpg` | Producing signatures; release automation pushes already-signed artifacts |
| ISO and WSL images | Pre-installing `linxira-keyring` as the bootstrap source of first trust | Verifying later packages on the repository's behalf |

Signing happens in the maintainer's signing environment with the signing subkey restored
from the vault. Private keys and passphrases never enter `[linxira]`, the repository, or
any image.

## How to use

On a new installation the ISO provides the keyring and pacman installs it normally (the
WSL image's package list also contains `linxira-keyring`). Then enable the repository:

```ini
[linxira]
Server = https://linxira-os.github.io/linxira-packages/$arch
SigLevel = Required DatabaseOptional
```

Public key information:

| Property | Value |
|---|---|
| UID | `Linxira OS Release Signing <release@linxira.org>` |
| Primary fingerprint | `E1A4155F457D1481CA85EE6BF9D157739534BC29` |
| Signing subkey fingerprint | `D477286C296F1E1C35735E52B22DF3E636274191` |

These are public identifiers suitable for scripts and checklists. Private key material is
not.

Users do not import the public key or set trust by hand: `post_install` and
`post_upgrade` both repeat the import and local signature.

## When root is required

- Reading the public key and fingerprint under `/usr/share/keyrings/` needs no root; they
  are public information.
- Installing or upgrading `linxira-keyring` is a normal root package operation run by pacman.
- The `pacman-key` calls in the package script run as root through pacman; users do not
  invoke them directly.
- Installing packages is still a root operation, but key trust is already established at
  the system level.

## Known limitations

- **First trust is bootstrapped**: the keyring package cannot be verified by the `[linxira]`
  repository it is about to enable. Install it from the ISO or another trusted channel,
  never first from an unknown mirror.
- The install script ignores `pacman-key` failures (each call ends in `|| true`), so after
  installation check that the fingerprint is actually present in the local keyring instead
  of assuming trust was established.
- Removing the package does not delete the key from the pacman keyring (`post_remove` is a
  no-op); revoking trust is an explicit administrator action
  (`pacman-key --delete <fingerprint>`).
- Private keys and passphrases exist only in the vault and with the key holder. This wiki
  provides no recovery procedure and no private key material.
- Rotating the fingerprint requires a new keyring package. Installing it adds and locally
  signs the current public key; it does not delete an older public key still present on
  the machine.
- The package's key is not the repository's only trust artifact: `linxira-packages` also
  serves `x86_64/linxira.gpg`. Both come from the same release key.

## Design notes

Repository hosting and signing are documented in
[`linxira-packages`](https://github.com/Linxira-OS/linxira-packages). The package definition
is in
[`packages/packages/linxira-keyring`](https://github.com/Linxira-OS/packages/tree/main/packages/linxira-keyring).
