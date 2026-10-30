# 欢迎中心（linxira-welcome）

## 为什么存在

第一次开机看到的不该是一个空桌面。`linxira-welcome` 是 Plasma 原生的状态与
入口面板：Live 环境把「安装 Linxira OS」放在第一位置；装好的系统上，它先告诉你
这台机器是否就绪、首次配置是否完成，再把 Linxira 的各个工具按固定白名单摆出来。

它只读版本化的软件目录（catalog）和安装回执（installer receipt），然后打开
固定的可执行文件与固定参数。它不列出可安装软件，也不构造或执行 shell 字符串、
包事务、`sudo` 或 `pkexec`。

## 职责边界

**归它**：首页、状态、终端、系统、帮助五个固定页面；Live / 已安装判断；
健康与首次完成状态；系统语言选择；登录时是否显示；固定启动器白名单；
把 `linxira-config` 的子命令送进终端。

**不归它**：

- **装软件不归它**。软件在[快速配置系统软件](linxira-package-center.md)，
  运行时与组件在[快速配置系统运行时](linxira-component-manager.md)。
- **不提权**。所有按钮都是「以当前用户启动某个固定程序」，没有 `sudo`，
  没有 `pkexec`，也不改系统设置。
- **不是软件清单**。可安装软件、应用类别、运行时子命令仍然属于各自的
  catalog 与产品，Welcome 不复刻它们。
- **不做配置**。系统页只是把 `linxira-config` 的子命令交给终端，
  真正的设置在[Config CLI](linxira-config.md)。

## 怎么用

```bash
linxira-welcome              # 从应用菜单或终端启动
linxira-welcome --autostart  # 登录自启动条目使用的形式
```

应用菜单里的「Linxira 欢迎中心」执行 `/usr/bin/linxira-welcome`；自启动条目
执行 `/usr/bin/linxira-welcome --autostart`。带 `--autostart` 启动时，如果在
「帮助」页取消了「登录时显示欢迎中心」，程序会直接退出。

五个页面：

- **首页**。Live 环境显示安装横幅：点「安装 Linxira OS」会先把当前界面语言写入
  `/tmp/linxira-installer-lang`，再启动 `/usr/local/bin/linxira-installer-shell`，
  让安装器沿用同一语言。装好的系统上显示健康与首次完成状态；若有安装时因缺网
  延后的软件或组件，会出现对应的继续横幅，分别打开软件设置与运行时设置。
  下方是固定启动器：软件中心（Shelly）、快速配置系统软件、快速配置系统运行时、
  在终端里的 Config CLI、系统设置和终端；装好的系统还多出系统更新、游戏管理器、
  硬件与驱动、恢复诊断。
- **状态**。列出发行版本、内核、网络、catalog 是否可用及审核版本、安装回执状态、
  可用更新数、上次检查时间、是否需要重启，以及安装时选择的 profile 与应用。
- **终端**。bash 是系统基线与默认登录 shell，始终安装；fish、nushell、zsh 未安装时
  按钮会带着 `--select` 打开快速配置系统运行时，安装事务留在那个应用里完成。
  shell 已安装但不是当前登录 shell 时，按钮只是把 `chsh -s /usr/bin/fish`
  （按所选 shell 替换路径）复制到剪贴板，由你自己执行。
- **系统**。读取 `linxira-config-hub` 安装的能力清单，只渲染带 `welcome` 元数据的
  命令；每个磁贴都在终端里打开对应的 `linxira-config` 子命令。标记为会改系统的
  条目只有显式 opt-in 才出现；笔记本专用的条目在非便携机箱且没有 `BAT*` 设备时隐藏。
- **帮助**。Arch Linux 新闻、Linxira Wiki、ArchWiki、项目站点、仓库与问题反馈链接，
  以及「登录时显示欢迎中心」开关。

右上角的语言选择器提供英语、简体中文、繁体中文、德语、西班牙语、法语、日语、
韩语、巴西葡萄牙语和俄语；选择会持久化，未列出的系统语言回退到英语。

## 何时需要 root

**从不需要。** Welcome 里没有任何提权路径：启动器是固定的可执行文件加固定参数；
Config CLI 只是在一个 Konsole 窗口里打开；终端页把 `chsh` 命令交给用户自己执行。
需要 root 的动作由对应工具按各自的授权模型处理。

## 已知限制

- 它只是入口和状态面板，不呈现各工具的实时运行状态（状态页列出的字段除外）。
- 系统页依赖 `linxira-config-hub` 提供的 `/usr/share/linxira/agent/capabilities.json`；
  文件缺失时该页为空并提示清单未安装。
- 终端分发按能力区分：`konsole`/`alacritty`/`xterm` 直接接命令；
  `cosmic-term`、`kitty`、`foot` 没有可执行参数语义，只能借助临时
  `Terminal=true` 桌面条目和 `gtk-launch` 启动，缺 `gtk-launch` 时这类入口不可用。
- Live 镜像使用临时配置，每次重新进入 Live 都会再次弹出，登录设置不会跨启动保留。
- 翻译覆盖十种语言，其余语言按英语显示。

## 深入设计

内部实现见 [`linxira-welcome`](https://github.com/Linxira-OS/linxira-welcome)
仓库；目录与回执的契约分别见 [Linxira Catalog](https://github.com/Linxira-OS/linxira-catalog)
和[快速配置系统软件](linxira-package-center.md)。
