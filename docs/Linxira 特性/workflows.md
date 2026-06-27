# 工作流模板

Linxira Config Hub 提供预设的工作流模板，一键配置完整开发环境。

## 科研工作流

包含：Python + R + LaTeX + Bioconda

```bash
linxira-config workflow science
```

预装组件：
- Python 科学计算栈 (numpy, scipy, pandas, matplotlib)
- R 语言基础环境
- LaTeX 文档排版
- Bioconda 通道 (bwa, samtools, star 等)

## 开发工作流

包含：Node.js + Rust + Go + Docker

```bash
linxira-config workflow dev
```

预装组件：
- Node.js LTS + npm/pnpm
- Rust + cargo
- Go
- Distrobox (可运行 Arch 容器)

## AI/ML 工作流

包含：Python + CUDA + PyTorch

```bash
linxira-config workflow ai
```

预装组件：
- Python + PyTorch
- CUDA 工具包 (需 NVIDIA 显卡)
- Jupyter Lab
- OpenCode AI 助手

## 生物信息学工作流

包含：Bioconda + Nextflow + Singularity

```bash
linxira-config workflow bio
```

预装组件：
- Bioconda 完整通道
- Nextflow 流水线引擎
- Singularity 容器运行时
- 常用生信工具 (bwa, samtools, star, fastqc 等)
