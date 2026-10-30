# 硬件检测（linxira-hwd-detector）

## 为什么存在

驱动建议必须站在可复核的硬件事实上。显卡是核显、独显，还是直通给虚拟机的设备；
CPU 与虚拟机厂商是什么——这些都不是界面能猜出来的。`linxira-hwd-detector` 把事实
收成一份固定契约的只读 JSON；[硬件与驱动管理器](linxira-hardware-driver-manager.md)
只负责把事实映射成策略，探测与策略不混在一起。

## 职责边界

**归它**：

- 从固定位置只读采集证据：`/sys/bus/pci/devices/*/{class,vendor,device}`、
  `/sys/devices/virtual/dmi/id/{sys_vendor,product_name,chassis_type}`、`/proc/cpuinfo`。
- 输出 `schema_version = 1` 的 JSON：`detector`（名称、实现版本、上游 CHWD 版本）、
  `evidence`（PCI、DMI、CPU、虚拟化）、排序去重的 `profile_ids`、结构化 `warnings`。
- 输出稳定的硬件类别 ID：`cpu.amd`、`cpu.intel`、`graphics.amd`、`graphics.intel`、
  `graphics.nvidia`、`graphics.hybrid`、`vm.hyperv`、`vm.qemu`、`vm.virtualbox`、
  `vm.vmware`、`vm.xen`。
- 提供完整 `lhwd` CLI 与随包安装的 CHWD 驱动档案（`/var/lib/chwd/db`）。

**不归它**：

- **不决定装什么包**。ID 到包的映射、许可证判断、内核与 DKMS 前置条件都在管理器里。
- **不构建内核**。Linxira 只随通用 `linux` / `linux-lts`，没有 CachyOS 式的定制内核流程。
- **不做提权编排**。会改系统的 `lhwd` 子命令只检查有效 UID 是否为 root，不调用 Polkit 或 sudo。

## 怎么用

### 只读报告

```bash
linxira-hwd-detector
```

无参数运行是由输出契约保证只读的入口：不写文件、不调包管理器、不联网。任何参数都会
转到下面的完整 CLI。

输出契约的要点：

- `schema_version` 版本化整份文档；`detector.version` 版本化实现，两者都会被严格校验。
- 缺失的证据用 `null` 或空数组表示，同时给出一条 warning，而不是猜一个值。
- 数组排序固定，同一台机器重复运行得到相同文档（时间戳除外）。

### 完整 CLI（`lhwd`）

```bash
lhwd --list                # 已探测设备可用的驱动档案
lhwd --list-installed      # 已安装的档案
lhwd --list-all            # 全部档案
lhwd --check <profile>     # 检查指定档案是否适用于当前设备
lhwd --autoconfigure       # 为探测到的设备选择档案
lhwd --install <profile>   # 安装档案
lhwd --remove <profile>    # 卸载档案
```

`--detail` 让列表输出更多字段；`--force` 允许重装；`--autoconfigure` 可以带一个
class ID（省略时为 `any`）。

## 何时需要 root

- **不需要**：`linxira-hwd-detector`、`lhwd --list`、`--list-installed`、`--list-all`、
  `--check`。
- **需要**：`lhwd --install`、`--remove`、`--autoconfigure`。源码在进入包事务前检查
  有效 UID；不是 root 就报错退出。

Linxira 的正常授权路径不在 `lhwd` 里：改机器的动作走
[Components](linxira-components.md) 的计划、确认与 Polkit。`lhwd` 是保留的完整
CHWD 工具面，不应作为日常驱动的提权入口。

## 已知限制

- 只描述「这是什么硬件」，不描述「该装什么」；策略在管理器。
- 包只创建 `/var/lib/chwd/scripts` 目录，没有安装 `/var/lib/chwd/scripts/chwd`
  助手脚本；而 `lhwd` 的 `--install` / `--remove` / `--autoconfigure` 事务都调用它。
  因此这些会改系统的子命令在当前打包态下无法完成；列表与检查类子命令不受影响。
- 探测范围固定，不做任意 sysfs 遍历；新增证据来源需要改契约。
- 驱动档案来自上游 CHWD 1.23.0，包名按 Arch 官方仓库与上游假设编写；管理器不会
  据此推断设备级支持承诺。

## 深入设计

上游出处与 fork 点见仓库的 `UPSTREAM.md`；实现见
[`linxira-hwd-detector`](https://github.com/Linxira-OS/linxira-hwd-detector)。
