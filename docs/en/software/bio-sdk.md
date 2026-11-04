# Bio SDK (linxira-bio-sdk)

!!! warning "External product — the repository and its Wiki are authoritative"
    Bio SDK is an externally evolving product. This wiki is only an entry point and does
    not copy its usage or SDK material. Commands, parameters, output formats and SDK
    interfaces live in the repository's GitHub Wiki; they change between releases, so
    check the current version before relying on them.

Linxira Bio SDK is a local-first, agent-native bioinformatics execution toolkit. It
combines concise skills with tested CLI, SDK and tool contracts so routine analyses use an
existing implementation instead of regenerating a script for every run.

## Why it exists

Letting a general coding agent run bioinformatics usually means writing a fresh script each
time: the same QC or statistics logic is rewritten in a different session, results cannot
be reproduced, and there is no versioned input/output contract. Bio SDK turns analyses
into versioned units with a machine-readable catalog, so an agent calls a contract instead
of generating code. Local execution is the default; work moves elsewhere only when measured
resources require it.

## Responsibilities

**It owns**:

- `linxira-bio`: the command-line interface for people and workflows.
- `skills/`: agent instructions bound to versioned capabilities; `capabilities/`: the
  machine-readable capability catalog.
- `engine/`: the Rust runtime (with future C++ kernels that must be justified by
  benchmarks).
- `skill-pack.json`: the import boundary for agent runtimes and `linxira-skills`.
- `linxira-bio-ui`: a native Rust desktop application without a WebView.
- `linxira-bio-mcp`: a stdio JSON-RPC MCP server where capability ids are the tool names
  and tool calls execute worker jobs.
- Versioned capability contracts and structured results. Release bundles are staged from a
  fixed manifest and always include the bilingual `docs/` tree, schemas, catalogs, skills
  and license notices.

**It does not own**:

- It does not replace `linxira-skills`, which remains the cross-discipline skill router and
  installer for research, Linux, HPC, cloud, browser and delivery workflows. Bio SDK
  supplies the executable bioinformatics capabilities.
- It does not reimplement mature native tools. salmon, kraken2, BLAST, HMMER and minimap2
  stay external and are orchestrated; Python and R are first-class backends with their own
  independent implementations, and plotting defaults to matplotlib and ggplot2.
- It does not bundle third-party interpreters, packages, databases or models; those are
  optional local backends.
- Browser-only services are connectors, not compute kernels, and the project never stores
  or auto-fills account credentials.

## How to use

Three user-facing entry points, all built on the same capability contracts:

| Entry point | Form | Purpose |
|---|---|---|
| `linxira-bio` | Command line | Direct use by people and workflows; structured result tables export as CSV, TSV, JSON, JSONL or XLSX |
| `linxira-bio-mcp` | stdio JSON-RPC MCP server | Point an MCP client at the binary; capability ids are the tool names |
| `linxira-bio-ui` | Native desktop app | Capability-aware result charts, local PDB/mmCIF structure viewing and PNG export |

Agents integrate through `skill-pack.json` and `skills/`, not through the GUI.

The exact subcommands, parameters, planning modes and data-format matrix are in the
repository docs and Wiki; this page does not copy them. Environment plans (`local-core`,
`scripting`, `managed-runtimes`, `containers`, `sequence-search`, `genomics-cli`,
`full-local`) are read-only. Installation is a separate capability that needs explicit
approval, and `environment.apply.v1` is still planned, so it cannot execute a plan
preview.

Platforms: Windows is the primary desktop and beginner-facing platform; Debian and Arch
are the supported Linux families for workstation, server and HPC use; macOS is not
currently a tested or packaged target. On Windows, WSL Debian is the compatibility provider
for older components and WSL Arch is the current-platform provider; Linxira WSL
installation still awaits a versioned rootfs and upgrade contract.

## Privileges

Routine analyses run locally as the current user and need no root. Only steps that change
system state need elevation: installing runtimes or system-missing components is a
separate, explicitly approved capability, and planning itself is read-only. Moving work
outside the local boundary (local GPU, institutional scheduler, approved cloud compute)
requires recording the provider, allocation, cost and data-retention boundaries first.
Browser services require an explicit user action gate and human-controlled authentication.
Structure files stay local and are bounded to 128 MiB after decompression and 100,000
atoms.

## Known limitations

- Every capability is single-step. Multi-step chains happen through skills, agents or
  manual chaining; there is no in-engine pipeline composition (no DAG runner, no
  intermediate artifact lifecycle between steps).
- The Python SDK is still planned; the repository says it arrives after the CLI contract
  stabilizes.
- `environment.apply.v1` is not available yet, so a plan preview cannot be executed
  directly.
- mmCIF is currently a viewer input, not an available analysis capability.
- macOS is not a tested or packaged target, and Linxira WSL installation is still planned.
- Release bundles do not include third-party interpreters, packages, databases or models,
  so analyses with external dependencies need a runtime the user prepares.
- The licence is AGPL-3.0-or-later: modified versions offered to users over a network must
  provide the corresponding source as the AGPL requires.

## Further design

The repository and product overview are at
[Linxira-OS/linxira-bio-sdk](https://github.com/Linxira-OS/linxira-bio-sdk); the
authoritative usage and SDK documentation is that repository's
[GitHub Wiki](https://github.com/Linxira-OS/linxira-bio-sdk/wiki); architecture, runtime
management, data formats and execution policy documents live in the repository's
[docs/](https://github.com/Linxira-OS/linxira-bio-sdk/tree/main/docs) directory.
