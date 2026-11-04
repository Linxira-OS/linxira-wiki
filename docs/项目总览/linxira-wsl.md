# WSL 发行版（linxira-wsl）

## 为什么存在

相当一部分 Linxira 的目标用户（AI agent 协作开发者）日常工作在 Windows 上，
但 agent 的执行环境在 Linux 里。为他们维护双系统或虚拟机成本高；WSL2 是
Windows 侧的原生答案。linxira-wsl 把 Linxira 的工具链以 rootfs 发行版形式
带进 WSL：不含内核/固件/引导（WSL 自带），只带真正会在终端里用到的部分。

## 职责边界

**归它**：

- 构建供 `wsl --import` / `wsl --install --from-file` 导入的 rootfs `tar.gz`
  与同名 `.sha256`。
- 维护包清单 `wsl-packages.x86_64`、默认 `/etc/wsl.conf`（`wsl.conf`）与
  发布前的只读校验脚本 `verify-wsl-rootfs.sh`。
- 决定镜像里放哪些一方工具、以及刻意不放什么（内核、固件、引导、NetworkManager、Zeta）。

**不归它**：

- 不出桌面 ISO；那是 `linxira-iso-direct` 的产物，本仓镜像不随 ISO 发布。
- 不构建软件包本身；包来自 `packages` 仓库，经由 `[linxira]` 仓库分发。
- 不管理 WSL 网络；地址解析、代理与 hosts 都由 Windows 侧负责。
- 不做组件事务的规划与执行；`linxira-components` 是那条链的唯一实现。

## 与桌面版的关系

| | ISO 安装 | WSL |
|---|---|---|
| 内核/引导/分区 | 安装器处理 | 不适用（WSL 自带内核） |
| 桌面 | catalog 选择（KDE Plasma / COSMIC / 无桌面完整工具集 / 最小无桌面） | 无会话；GUI 工具走 WSLg（Win11） |
| 软件栈 | 装机时选择 / component-manager | `linxira-component-manager` 或 `linxira-config stack`（同一条链） |
| 工作区守护 | 定时器每 30 分钟 | 不默认启用（见下） |
| 网络管理 | NetworkManager | Windows 侧管理，镜像刻意不装 NetworkManager |
| Zeta | 完整二进制包（桌面路线） | 不预装；用 npm 版 `@linxiraos/zeta`，需先装 `nodejs`/`npm` |

**工作区守护在 WSL 里的语义变化**：WSL 虚拟机在没有进程运行时会被 Windows
关闭，systemd 定时器只在运行期触发——「每 30 分钟快照」会退化成「会话活跃时
快照」。因此镜像默认不启用守护；有需要的用户可以
`sudo linxira-config workspace-guard enable` 手动开启，但要理解触发条件。

## 怎么用

```powershell
wsl --import linxira C:\wsldata linxira-wsl-<版本>-x86_64.tar.gz --version 2
wsl -d linxira
# 卸载
wsl --unregister linxira
```

导入后默认用户是 root，systemd 已启用（`/etc/wsl.conf` 中 `systemd=true`、
`default=root`、`hostname=linxira`），`[linxira]` 仓库与 ISO 装机同款验签配置，
`linxira-update` 开箱可用。

镜像不自带 Node；需要 Zeta 的终端版本时：

```bash
sudo pacman -S nodejs npm
npm i -g @linxiraos/zeta
```

## 内容物

完整清单见仓库内 `wsl-packages.x86_64`，当前 **37 个显式条目**（解析依赖后
三百余个包；安装与压缩体积以构建脚本结尾打印的 `du -sh` 为准）。分三类：

- **基础与常用 CLI**：`base`、`curl`、`ca-certificates`（显式声明，构建会断言
  根证书库存在且证书数量正常）、`git`、`wget`、`nano`、`less`、`man-db`、
  `man-pages`、`bash-completion`、`unzip`、`zip`、`which`、`rsync`、`dnsutils`、
  `jq`、`fastfetch`、`openssh`、`sudo`、`btrfs-progs`、`archlinux-keyring`、
  `linxira-keyring`。
- **一方工具链与品牌资产**：`linxira-components`、`linxira-component-manager`、
  `linxira-config`（Config Hub）、`linxira-recovery-diagnostics`、
  `linxira-update`、`linxira-wiki`、`linxira-catalog`、
  `linxira-completion-agent`、`linxira-crash-watch`、`linxira-hooks`、
  `linxira-gaming-manager`、`linxira-hardware-driver-manager`、
  `linxira-package-center`、`linxira-welcome`、`linxira-artwork`。
- **刻意不含**：内核、固件、引导；NetworkManager；Zeta 二进制包；Node 运行时；
  任何桌面会话。

`linxira-update` 依赖 Qt6（`python-pyqt6`、`qt6-svg`），在 Win11 + WSLg 下可以
直接显示界面。

## 网络

镜像**不内置**任何 DNS、代理或 hosts 覆盖：`/etc/hosts` 与 `/etc/resolv.conf`
由 WSL 自动生成，解析交给 Windows 侧。国内网络下「某些网站打不开」通常是宿主侧
原因。最常见的是 Steam++ / Watt Toolkit 之类加速器把域名写进 Windows `hosts` 指向
`127.0.0.1`；WSL2 经 Windows 解析器拿到这些地址后，连接会被拒（`Connection refused`）。
这**不是证书问题**——镜像根证书库与 Arch 一致。

要让加速器或代理在 WSL 内生效，二选一：

- **镜像网络模式**（推荐，Win11 22H2+）：在 `%UserProfile%\.wslconfig` 加
  `[wsl2]` / `networkingMode=mirrored`，然后 `wsl --shutdown`；
- **显式代理**：`export HTTPS_PROXY=http://<Windows 宿主 IP>:<端口>`（NAT 模式的宿主
  IP 见 `/etc/resolv.conf` 的 nameserver），或写进 shell 启动文件。

## 权限

- 默认用户是 **root**，镜像同时带 `sudo`；这与 WSL 官方发行版的做法一致，但也意味着
  默认没有权限隔离。需要普通用户时自行创建账户，再改 `/etc/wsl.conf` 的 `default`。
- pacman 装包与组件事务需要 root；`linxira-config workspace-guard enable` 需要 root。
- 只读查询（`linxira-config status`、`linxira-crash status`、`linxira-config workspace-guard status`）
  不需要 root。

## 已知限制

- 没有桌面会话；图形工具只在 Win11 + WSLg 下显示，Win10 上只能走 CLI。
- WSL 虚拟机闲置会被 Windows 关停，systemd 定时器只在运行期触发；工作区守护因此
  默认关闭，快照语义也弱于桌面版。
- 镜像**仍在开发中**，仓库规范明确不得把测试产物称为正式版；发布路径是 GitHub
  Release（`linxira-wsl-<YYYY.MM.DD>-x86_64.tar.gz` + `.sha256`）。
- 不随 ISO 发布，也不参与桌面 ISO 的构建链。
- 不提供 DNS/代理/hosts 覆盖；网络问题先查宿主侧。
- 默认 root 且没有预置普通用户，多用户隔离需自行配置。

## 构建

在 Arch 环境（或 arch 容器）中：

```bash
sudo pacman -S --needed arch-install-scripts
./build-wsl-rootfs.sh
LINXIRA_MIRROR=https://mirrors.aliyun.com/archlinux ./build-wsl-rootfs.sh
```

- **必须在 ext4 上构建**：不能直接对着 `/mnt/c`、`/mnt/f`（9p/drvfs）构建——那里
  建不出字符/块设备节点，整条 pacstrap/chroot/tar 链路也会慢一个数量级。脚本用
  `findmnt` 探测并在命中 9p/drvfs 时退出 65；排障才用 `LINXIRA_ALLOW_DRVFS=1`。
- **刻意避开 `/tmp`**（tmpfs 即内存）：实测事故——rootfs 打包写满 2G tmpfs 后，
  同机并行的 ISO 构建进程被 OOM 杀掉。
- 构建期 `[linxira]` 仓库使用 `SigLevel = Never`，只为解决「密钥在被安装的包里」的
  引导问题；装入镜像的最终 `/etc/pacman.conf` 与 ISO 装机完全相同的验签配置。
- 发布前跑只读校验：

```bash
./verify-wsl-rootfs.sh out/linxira-wsl-<YYYY.MM.DD>-x86_64.tar.gz
```

校验许可文件、品牌资产、fastfetch 标识、catalog 组件条目、crash-watch 服务与
`diagnose-crash` 技能、Linxira 包版本、每个一方包的 `/usr/share/licenses/<pkg>/`
以及根证书数量；任一失败即非零退出。

## 深入设计

仓库与构建说明见 [`linxira-wsl`](https://github.com/Linxira-OS/linxira-wsl)
的 `README.md`；包清单与构建约束见同仓 `wsl-packages.x86_64` 与 `AGENTS.md`。
