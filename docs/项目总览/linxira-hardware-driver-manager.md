# 硬件与驱动管理器（linxira-hardware-driver-manager）

## 为什么存在

硬件探测只回答「有什么设备」，不回答「该装哪个驱动、会改哪些包、失败怎么回滚」。
把这两件事混在一起，用户只能看到一句「建议安装」，却不知道计划里到底有什么。
这个管理器把硬件事实变成**可审阅的固定策略计划**，并把真正执行交给唯一的系统事务后端。

## 职责边界

**归它**：

- 读取 `linxira-hwd-detector` 的只读 JSON，并严格校验 schema、名称、版本与重复键。
- 维护固定策略表：Intel / AMD Mesa、NVIDIA open / proprietary、Hyper-V / QEMU / VMware / VirtualBox guest。
- 汇报已安装状态：仅 `linux`、`linux-lts` 及其 headers、DKMS、initramfs、已加载模块、重启标记。
- 生成并原子保存计划（权限 `0600`，位于 `$XDG_STATE_HOME/linxira/hardware-driver-manager/plans`）。
- 在界面里发起 root 拥有的只读诊断，并对三种 VM guest 策略发起经确认的安装事务。

**不归它**：

- 不探测硬件（[硬件检测](linxira-hwd-detector.md) 的事）。
- 不实现事务后端、快照与 Polkit（[Components](linxira-components.md) 的事）。
- 不管理内核包本身（[内核管理器](linxira-kernel-manager.md) 的事）。

## 怎么用

### 界面

应用菜单里的 **Linxira Hardware and Driver Manager**，或直接运行：

```bash
linxira-hardware-driver-manager
```

窗口分四个页签：

| 页签 | 内容 |
|---|---|
| Overview | 探测到的硬件事实、检测器版本、`Run root diagnosis` |
| Drivers | 推荐策略、完整计划 JSON、`Save plan` 与 `Apply` |
| Kernel compatibility | `linux` / `linux-lts` 的安装、headers、DKMS 表 |
| Activity / report | 完整只读报告 |

### 命令行

```bash
linxira-hardware-driver-manager --report-json
linxira-hardware-driver-manager --plan org.linxira.driver.intel-mesa.v1
linxira-hardware-driver-manager --plan org.linxira.driver.intel-mesa.v1 --json
```

`--plan` 只接受下面这些固定策略 ID，不接受任意包名、路径或命令。计划总是写入
home 目录（用户主目录）下的 `~/.local/state/linxira/hardware-driver-manager/plans/`
（`XDG_STATE_HOME` 未设置时）：不加 `--json` 时打印计划路径，加 `--json` 时打印计划本身。
计划可应用时退出码为 0，否则为 3。

| 策略 ID | 硬件事实 | 当前状态 |
|---|---|---|
| `org.linxira.driver.intel-mesa.v1` | `graphics.intel` | 只生成计划，界面不提供 Apply |
| `org.linxira.driver.amd-mesa.v1` | `graphics.amd` | 只生成计划，界面不提供 Apply |
| `org.linxira.driver.nvidia-open-dkms.v1` | `graphics.nvidia` | 只生成计划；必须人工复核 |
| `org.linxira.driver.nvidia-proprietary-dkms.v1` | `graphics.nvidia` | 不可用：官方 Arch 仓库没有双内核的专有 NVIDIA DKMS 包 |
| `org.linxira.driver.vm-qemu-guest.v1` | `vm.qemu` | 界面可 Apply |
| `org.linxira.driver.vm-virtualbox-guest.v1` | `vm.virtualbox` | 不可用：双内核 guest 模块供应方尚未修好 |
| `org.linxira.driver.vm-vmware-guest.v1` | `vm.vmware` | 界面可 Apply |
| `org.linxira.driver.vm-hyperv-guest.v1` | `vm.hyperv` | 界面可 Apply |

计划里记录：策略 ID、硬编码包集合、检测器文档摘要、许可证与驱动模型、内核 / headers
与 DKMS 前置条件、预期效果、warnings、blockers、适用性，以及计划自身的 SHA-256。
计划文件用私有权限原子写入；目录是符号链接时直接拒绝。

## 事务边界

这是本页最需要看清的部分：

- **本地计划是审阅物，不是执行凭据。** CLI 生成的计划与界面里的预览都只描述
  「如果执行会做什么」；CLI 没有 apply 子命令。
- **只读诊断**走系统 D-Bus 上的 `org.linxira.Components1`：固定操作
  `org.linxira.hardware.driver-state-diagnose.v1`、空参数、计划风险必须是 `read-only`。
  用户审阅后确认，回执必须满足 `changed = false`。这一步不改包、不改服务、不改系统文件。
- **Apply 只对三种 VM guest 策略开放**（Hyper-V、QEMU、VMware）。点击 Apply 时，
  管理器先向事务服务申请一份 root 拥有、可审阅的驱动计划；确认后由后端创建
  Timeshift Btrfs 变更前快照，再执行固定包集合、校验平台服务、留下不可变回执。
  仓库与硬件证据在两步之间变化，计划即作废。
- VirtualBox、NVIDIA proprietary 以及 Intel / AMD / NVIDIA 的普通显卡计划都没有
  可执行后端，界面上的 Apply 保持不可用。

## 何时需要 root

- **不需要**：`--report-json`、`--plan`、界面的浏览、策略预览与计划保存。
- **需要**：`Run root diagnosis` 与三种 VM guest 的 Apply。两者都走系统事务服务，
  由 Polkit 决定是否授权（需要时弹窗）；管理器自己从不调用 `sudo`、`pkexec` 或包管理器。

## 已知限制

- 支持矩阵只有 `linux`、`linux-lts` 及各自 headers；需要 DKMS 的策略在缺少所需内核时
  直接给 blocker。
- NVIDIA open 与 proprietary 是两种互斥方案，必须人工选择；不从 PCI 设备 ID 推断支持。
  专有 DKMS 比较因缺少双内核包而阻塞。
- 已安装状态只来自固定证据：内核、`pacman -Q`、`dkms status`、initramfs、`/proc/modules`
  与重启标记；不扫描任意路径。
- 检测器输出有 1 MiB 上限与 10 秒超时；检测器缺失时报告不可用（CLI 退出码 2）。
- 计划目录与文件都拒绝符号链接，文件权限固定为 `0600`。

## 深入设计

内部实现见
[`linxira-hardware-driver-manager`](https://github.com/Linxira-OS/linxira-hardware-driver-manager)
仓库；事务形态见 [Components](linxira-components.md)。
