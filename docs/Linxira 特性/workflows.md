# 工作流配置

Linxira Config Hub 从系统的软件目录读取配置，不在脚本中维护另一份软件包清单。查看当前可用配置：

```bash
linxira-config workflow help
```

安装会先刷新并完整升级 Arch 软件包事务，避免滚动发行版的部分升级。

## 科学计算

```bash
linxira-config workflow science
```

包括 R、Octave、Gnuplot、ParaView、JupyterLab，以及 NumPy、SciPy、Matplotlib 和 pandas。

## 软件开发

```bash
linxira-config workflow developer
```

包括 `base-devel`、Git、CMake、Code、Rust、Go、Node.js、npm、Python 和 pip。

## AI 与机器学习

```bash
linxira-config workflow ai
```

包括 JupyterLab、PyTorch 和 scikit-learn。CUDA、ROCm 等厂商 GPU 栈与硬件和版本强相关，不由通用配置自动安装。

## 容器开发

```bash
linxira-config workflow containers
```

提供 Podman 与 Distrobox。固定版本的开发环境、服务器式服务和项目依赖应放在容器中，而不是依赖滚动更新的宿主机状态。

## 生物信息学

```bash
linxira-config workflow bioinformatics
```

基础配置安装 Apptainer。具体 BWA、SAMtools、Nextflow 等工具应来自经过审核并固定版本的工作流容器；Linxira 不会把未审核的 AUR 配方伪装成官方软件包。

## 产品边界

Linxira OS 面向个人科学工作站和桌面超算。它不推荐作为大规模企业滚动服务器；需要可重复部署的服务和开发环境应采用固定镜像、容器或其他隔离运行时。
