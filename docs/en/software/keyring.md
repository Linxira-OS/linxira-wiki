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
  `/usr/share/keyrings/linxira-release-fingerprint`.
- An install script that adds the key to pacman's keyring and locally signs it
  (`pacman-key --add`, `pacman-key --lsign-key`), running as root.
- Public distribution in ASCII (`linxira.asc`) and binary (`linxira.gpg`) form.
- The key vault (the private `linxira-keys` repository), which holds encrypted private key
  material and the public source files. Vault and GPG passphrases are kept by the key
  holder and are not in any repository.

**It does not own**:

- Package signing; that happens in the `packages` release flow.
- Enabling the `[linxira]` repository; that is `/etc/pacman.conf` configuration.
- Private-key recovery. This wiki does not document decryption, private-key import or
  passphrase handling.

## How to use

On a new installation the ISO provides the keyring and pacman installs it normally. Then
enable the repository:

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

- Installing or upgrading `linxira-keyring` is a normal root package operation run by pacman.
- The `pacman-key` calls in the package script run as root through pacman; users do not
  invoke them directly.
- Installing packages is still a root operation, but key trust is already established at
  the system level.

## Known limitations

- **First trust is bootstrapped**: the keyring package cannot be verified by the `[linxira]`
  repository it is about to enable. Install it from the ISO or another trusted channel,
  never first from an unknown mirror.
- Removing the package does not delete the key from the pacman keyring (`post_remove` is a
  no-op); revoking trust is an explicit administrator action.
- Private keys and passphrases exist only in the vault and with the key holder. This wiki
  provides no recovery procedure and no private key material.
- Rotating the fingerprint requires a new keyring package. Installing it adds and locally
  signs the current public key; it does not delete an older public key still present on
  the machine.

## Design notes

Repository hosting and signing are documented in
[`linxira-packages`](https://github.com/Linxira-OS/linxira-packages). The package definition
is in
[`packages/packages/linxira-keyring`](https://github.com/Linxira-OS/packages/tree/main/packages/linxira-keyring).
