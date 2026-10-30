# Workflow presets

Linxira Config Hub reads its presets from the system software catalog; it does not keep a second package list in scripts. To see what is available:

```bash
linxira-config workflow help
```

Installation first refreshes and fully upgrades the Arch package transaction, so a rolling distribution is never left partially upgraded.

## Scientific computing

```bash
linxira-config workflow science
```

R, Octave, Gnuplot, ParaView, JupyterLab, plus NumPy, SciPy, Matplotlib and pandas.

## Software development

```bash
linxira-config workflow developer
```

`base-devel`, Git, CMake, Code, Rust, Go, Node.js, npm, Python and pip.

## AI and machine learning

```bash
linxira-config workflow ai
```

JupyterLab, PyTorch and scikit-learn. Vendor GPU stacks such as CUDA and ROCm are tightly coupled to specific hardware and versions, so a general preset does not install them automatically.

## Container development

```bash
linxira-config workflow containers
```

Podman and Distrobox. Pinned development environments, server-style services and project dependencies belong in containers rather than in the state of a rolling host.

## Bioinformatics

```bash
linxira-config workflow bioinformatics
```

The base preset installs Apptainer. Specific tools such as BWA, SAMtools and Nextflow should come from reviewed, version-pinned workflow containers; Linxira does not present unreviewed AUR recipes as official packages.

## Product boundary

Linxira OS targets personal science workstations and desktop supercomputing. It is not recommended as a large-scale enterprise rolling server; services and development environments that need reproducible deployment should use pinned images, containers or another isolated runtime.

---

Back to the [wiki home](../index.md) · [software index](../software/index.md)
