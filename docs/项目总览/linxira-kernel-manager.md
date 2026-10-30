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
- 不实现提权与事务后端；Apply 按钮固定不可用。

## 怎么用

### 界面

应用菜单里的 **Linxira Kernel Manager**，或直接运行：

```bash
linxira-kernel-manager
```

| 页签 | 内容 |
|---|---|
| Overview | 运行内核、下次启动的内核、重启状态、warnings / blockers |
| Kernels | `linux` 与 `linux-lts` 的版本、release、headers、镜像数量；DKMS 逐内核记录 |
| Boot | 受支持的 GRUB 条目、normal / fallback / 内核镜像证据 |
| Activity / report | 选择固定操作、审阅完整计划、`Save plan`（Apply 不可用） |

### 命令行

```bash
linxira-kernel-manager --report-json
linxira-kernel-manager --plan org.linxira.kernel.ensure-standard.v1
linxira-kernel-manager --plan org.linxira.kernel.boot-lts-once.v1
linxira-kernel-manager --plan org.linxira.kernel.regenerate-initramfs.v1
linxira-kernel-manager --plan org.linxira.bootloader.refresh-grub.v1
```

`--plan` 打印 `{path, plan}`：计划原子写入 home 目录（用户主目录）下的
`~/.local/state/linxira/kernel-manager/plans/`（`XDG_STATE_HOME` 未设置时）。
计划可应用时退出码为 0，否则为 3。

| 操作 ID | 计划里展示的预期命令 |
|---|---|
| `org.linxira.kernel.ensure-standard.v1` | `pacman -S --needed linux linux-headers linux-lts linux-lts-headers` |
| `org.linxira.kernel.boot-lts-once.v1` | 对唯一一个可识别的 `linux-lts` GRUB 条目执行 `grub-reboot` |
| `org.linxira.kernel.regenerate-initramfs.v1` | `mkinitcpio -P` |
| `org.linxira.bootloader.refresh-grub.v1` | `grub-mkconfig -o /boot/grub/grub.cfg` |

这些命令是**展示文本**（`displayOnly: true`），不是执行凭据。

## 事务边界

- 计划里 `apply` 固定为 `{"implemented": false, "result": "backend-not-ready"}`；
  界面上的 Apply 按钮始终禁用。
- 计划有源报告摘要（`sourceReportSha256`）与自身摘要（`planSha256`）；前置条件包括
  固定支持矩阵、包状态可读、目标内核是否安装、GRUB 条目是否唯一等。
- `boot-lts-once` 要求恰好存在一个带安全 ID 的 `linux-lts` GRUB 条目；不唯一就阻塞，
  不会猜一个。
- `refresh-grub` 只在 GRUB 配置可读且至少一个受支持内核已安装时才适用。

## 何时需要 root

目前不需要，也不提供。所有子命令都是只读或写用户自己的计划目录；程序不调用
`sudo`、`pkexec`、包管理器、服务写入、initramfs 生成或引导器写入。将来若接入
事务后端，授权也应走 [Components](linxira-components.md) 的 Polkit 路径。

## 已知限制

- 支持矩阵只有 `linux`、`linux-lts`、`linux-headers`、`linux-lts-headers`；自定义内核显式不支持。
- 只解析固定的 `/boot/grub/grub.cfg` 与 `grub-editenv list`；其他引导器不在范围内。
- GRUB 条目只在能解析出受支持内核镜像时保留；解析失败只会让计划阻塞，不会写入。
- 计划按 `0600` 保存，目录逐级拒绝符号链接。

## 深入设计

实现见
[`linxira-kernel-manager`](https://github.com/Linxira-OS/linxira-kernel-manager)
仓库；内核与驱动的交界见
[硬件与驱动管理器](linxira-hardware-driver-manager.md)。
