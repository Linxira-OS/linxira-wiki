# WSL 发行版（linxira-wsl）

## 为什么存在

相当一部分 Linxira 的目标用户（AI agent 协作开发者）日常工作在 Windows 上，
但 agent 的执行环境在 Linux 里。为他们维护双系统或虚拟机成本高；WSL2 是
Windows 侧的原生答案。linxira-wsl 把 Linxira 的工具链以 rootfs 发行版形式
带进 WSL：不含内核/固件/引导（WSL 自带），只带真正会在终端里用到的部分。

## 与桌面版的关系

| | ISO 安装 | WSL |
|---|---|---|
| 内核/引导/分区 | 安装器处理 | 不适用（WSL 自带内核） |
| 桌面 | catalog 选择（plasma/cosmic/server/最小） | 无会话；GUI 工具走 WSLg（Win11） |
| 软件栈 | 装机时选择 / component-manager | `linxira-component-manager`（同一条链） |
| 工作区守护 | 定时器每 30 分钟 | 不默认启用（见下） |
| 网络管理 | NetworkManager | WSL 侧管理，刻意不装 NetworkManager |

**工作区守护在 WSL 里的语义变化**：WSL 虚拟机在没有进程运行时会被 Windows
关闭，systemd 定时器只在运行期触发——「每 30 分钟快照」会退化成「会话活跃时
快照」。因此镜像默认不启用守护；有需要的用户可以
`linxira-config workspace-guard enable` 手动开启，但要理解触发条件。

## 怎么用

```powershell
wsl --import linxira C:\wsldata linxira-wsl-<版本>-x86_64.tar.gz --version 2
wsl -d linxira
# 卸载
wsl --unregister linxira
```

导入后默认 root，systemd 已启用（`/etc/wsl.conf`），`[linxira]` 仓库与
ISO 装机同款配置（验签），`linxira-update` 开箱可用。

## 内容物

完整清单见仓库内 `wsl-packages.x86_64`（约 318 个包，装好 1.6G，压缩约
0.5G）：`base` + Linxira 一方 CLI 工具链（components / component-manager /
config-hub / recovery-diagnostics / update / wiki / catalog / completion-agent）。
`linxira-update` 会拉入 Qt 图形栈，在 Win11 + WSLg 下可直接显示。

## 构建

仓库：[`linxira-wsl`](https://github.com/Linxira-OS/linxira-wsl)。
在 Arch 环境运行 `./build-wsl-rootfs.sh`，产物为 tar.gz + sha256，
发布走 GitHub Release。

构建脚本刻意避开 `/tmp`（tmpfs 即内存）：实测事故——rootfs 打包写满 2G
tmpfs 后，同机并行的 ISO 构建进程被 OOM 杀掉。
