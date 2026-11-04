# 内核管理器（linxira-kernel-manager）

## 为什么存在

一台机器的内核状态分散在 `uname`、`/usr/lib/modules`、`pacman`、`dkms`、`/boot`
和 GRUB 环境里。用户想弄清「现在跑的是哪个内核、LTS 装没装、为什么提示要重启」，
通常要在五六个命令之间来回对照，还没有统一的证据。

内核管理器把这些状态收成一份只读报告，并把「装标准内核 / 下次进 LTS / 重建 initramfs /
刷新 GRUB」做成固定操作的计划。它是报告与计划工具，不是引导器写入工具。

## 职责边界

**归它**：

- 只读采集：运行内核 release、`linux` / `linux-lts` 的安装版本、
  `pacman -Q` 包状态、`dkms status`、initramfs 与内核镜像、`/proc/modules`、
  `/proc/cmdline`、GRUB 菜单条目与 `grub-editenv list` 的 next/saved entry、重启标记。
- 只保留启动 `linux` 或 `linux-lts` 这两个精确内核镜像的 GRUB 条目。
- 生成固定操作的显示型计划，记录前置条件、预期命令、预期效果、warnings、blockers
  与计划摘要。
- 界面提供 Overview、Kernels、Boot、Activity / report 四个视图。

**不归它**：

- 不写 GRUB、不生成 initramfs、不安装或删除包、不改服务。
- 不支持自定义内核或第三方内核包。
- 不实现提权与事务后端；Apply 按钮固定不可用。内核包与驱动计划的交界在
  [硬件与驱动管理器](hardware-driver-manager.md)。

## 责任链：谁读、谁规划、谁改动

| 步骤 | 执行者 | 是否改动系统 |
|---|---|---|
| 采集内核与引导状态 | 本管理器 | 只读 |
| 状态 → 固定操作计划 | 本管理器 | 只读；计划只写用户状态目录 |
| 安装内核 / 重建 initramfs / 写 GRUB | 目前没有执行者 | 未实现 |

第三行是本页最需要看清的事实：计划里的命令只是展示文本，**当前没有任何组件会执行它们**。
将来若接入执行能力，提权也只应走 [Components](components.md) 的 Polkit 路径。

## 怎么用

### 界面

应用菜单里的 **Linxira Kernel Manager**，或直接运行：

```bash
linxira-kernel-manager
```

| 页签 | 内容 |
|---|---|
| Overview | 运行内核 release、生效的下次启动内核、重启状态、warnings / blockers |
| Kernels | `linux` 与 `linux-lts` 的版本、release、headers、镜像数量；DKMS 逐内核记录 |
| Boot | 受支持的 GRUB 条目、normal / fallback / 内核镜像证据 |
| Activity / report | 选择固定操作、审阅完整计划、`Save plan`（Apply 不可用） |

在 Activity / report 页勾选 `I reviewed this exact plan` 才能保存计划；`Apply` 按钮
始终禁用，提示为 `Apply backend is not ready`。

### 命令行

```bash
linxira-kernel-manager --report-json
linxira-kernel-manager --plan org.linxira.kernel.ensure-standard.v1
linxira-kernel-manager --plan org.linxira.kernel.boot-lts-once.v1
linxira-kernel-manager --plan org.linxira.kernel.regenerate-initramfs.v1
linxira-kernel-manager --plan org.linxira.bootloader.refresh-grub.v1
```

`--plan` 打印 `{path, plan}`：计划原子写入
`$XDG_STATE_HOME/linxira/kernel-manager/plans/`（未设置时是
`~/.local/state/...`），文件名取自计划自身的 SHA-256。计划可应用时退出码为 0，
否则为 3——包括「已经无需变更」的情况。

| 操作 ID | 计划里展示的预期命令 |
|---|---|
| `org.linxira.kernel.ensure-standard.v1` | `/usr/bin/pacman -S --needed linux linux-headers linux-lts linux-lts-headers` |
| `org.linxira.kernel.boot-lts-once.v1` | `/usr/bin/grub-reboot <detected-linux-lts-entry-id>` |
| `org.linxira.kernel.regenerate-initramfs.v1` | `/usr/bin/mkinitcpio -P` |
| `org.linxira.bootloader.refresh-grub.v1` | `/usr/bin/grub-mkconfig -o /boot/grub/grub.cfg` |

这些命令是**展示文本**（`expected.displayOnly = true`），不是执行凭据。

## 事务边界

- 计划里 `apply` 固定为 `{"implemented": false, "result": "backend-not-ready"}`；
  界面上的 Apply 按钮始终禁用，系统事务服务里也没有对应的内核/bootloader 操作。
- 计划有源报告摘要（`sourceReportSha256`）与自身摘要（`planSha256`）；前置条件包括
  固定支持矩阵、包状态可读、目标内核是否安装、GRUB 条目是否唯一等。
- `boot-lts-once` 要求恰好存在一个带安全 ID 的 `linux-lts` GRUB 条目；不唯一就阻塞，
  不会猜一个。
- `refresh-grub` 只在 GRUB 配置可读且至少一个受支持内核已安装时才适用。

## 何时需要 root

目前不需要，也不提供。所有子命令都是只读或写用户自己的计划目录；程序不调用
`sudo`、`pkexec`、包管理器、服务写入、initramfs 生成或引导器写入。将来若接入
事务后端，授权也应走 [Components](components.md) 的 Polkit 路径。

## 已知限制

- 支持矩阵只有 `linux`、`linux-lts`、`linux-headers`、`linux-lts-headers`；自定义内核显式不支持。
- 只解析固定的 `/boot/grub/grub.cfg` 与 `grub-editenv list`；其他引导器不在范围内。
- GRUB 条目只在能解析出受支持内核镜像时保留；解析失败只会让计划阻塞，不会写入。
- 已安装状态只来自固定证据：`/usr/bin/uname -r`、`/usr/lib/modules`、`pacman -Q`、
  `dkms status`、`/boot`、`/proc/cmdline`、`/proc/modules` 与 `/run/reboot-required`；
  子进程都是固定参数、`shell=False`、8 秒超时。
- 计划目录逐级拒绝符号链接，文件权限为 `0600`。

## 深入设计

当前行为与边界见
[`linxira-kernel-manager` README](https://github.com/Linxira-OS/linxira-kernel-manager/blob/main/README.md)，
维护者约定见仓库的 `AGENTS.md`；内核与驱动的交界见
[硬件与驱动管理器](hardware-driver-manager.md)。
