# 游戏管理器（linxira-gaming-manager）

## 为什么存在

在 Arch 上打游戏要自己拼一整套东西：找到 Steam 库、给非 Steam 的 Windows
游戏配兼容层、记住每个游戏的环境变量、检查 UMU / Wine / GameMode / MangoHud
装没装、还要在折腾失败时留一份能恢复的备份。这些动作彼此相关，却没有一个
地方能把它们串起来。

`linxira-gaming-manager` 就是那个用户级工作区：发现 Steam 库、导入非 Steam
可执行文件、用固定参数数组启动游戏、检测兼容工具、创建显式 restic 备份，
并通过 catalog 绑定的计划部署审核过的游戏环境。它不发包事务，也不直接调用
包管理器。

## 职责边界

**归它**：游戏库发现与导入、每个游戏的托管 prefix、启动与日志、兼容工具状态、
游戏环境部署的确认与呈现、restic 备份的启动与记录。

**不归它**：

- **装包不归它**。部署环境时它只请求 catalog 里的 `bundle-gaming-setup`，
  计划、确认与特权执行由 [`linxira-components`](linxira-components.md) 完成。
- **不管理 Steam 本身**。Steam 的登录、安装与更新仍由 Steam 客户端负责。
- **不保存备份密码**。它只把密码文件路径交给 restic，密码内容从不写入自己的状态。
- **不改系统级配置**。驱动、内核与系统服务在各自的工具里。

## 怎么用

```bash
linxira-gaming-manager
```

没有命令行参数，应用菜单里的「Linxira Gaming Manager」执行的就是
`/usr/bin/linxira-gaming-manager`。**必须以普通用户运行**——以 root 启动时程序
打印错误并以状态码 1 退出。

可用环境变量：

| 变量 | 默认值 | 作用 |
|---|---|---|
| `LINXIRA_GAMING_STATE_PATH` | `${XDG_DATA_HOME:-$HOME/.local/share}/linxira/gaming-manager/state.db` | 游戏库与活动记录的 SQLite 文件 |
| `LINXIRA_STEAM_ROOTS` | `${XDG_DATA_HOME:-$HOME/.local/share}/Steam`、`$HOME/.steam/steam`、`$HOME/.local/share/Steam` | 用冒号分隔的 Steam 根目录列表 |

上面的 `$HOME` 就是 home 目录（用户主目录）。

### 库（Library）

- **刷新**会扫描每个 Steam 根的 `steamapps/libraryfolders.vdf` 及其
  `appmanifest_*.acf`，把找到的游戏写入本地库；重复扫描不会产生重复条目。
- **导入游戏**只接受 `.exe`，然后选择兼容运行器：**UMU-Proton（推荐）**
  或 **System Wine**。导入时按游戏 ID 生成独立 prefix，位置在
  `${XDG_DATA_HOME:-$HOME/.local/share}/linxira/gaming-manager/games/<id>/prefix`。
- **启动**单个游戏：Steam 游戏调用 `/usr/bin/steam steam://rungameid/<appid>`；
  导入游戏调用 `/usr/bin/umu-run` 或 `/usr/bin/wine`，工作目录为可执行文件所在
  目录，`WINEPREFIX` 指向托管 prefix，环境变量只传递固定白名单。启动输出合并后
  写入 `${XDG_STATE_HOME:-$HOME/.local/state}/linxira/gaming-manager/games/<id>/logs/<时间戳>.log`，
  最多保留 1 MiB 的本次输出。已有同名游戏在运行时不会重复启动。

### 兼容（Compatibility）

工具表列出 Steam、UMU Launcher、Wine、Protontricks、Winetricks、restic、
GameMode、Gamescope、MangoHud，未安装的显示 `Not installed`。

**Deploy gaming environment** 会先弹出一段说明：将安装官方 Arch Steam 包、
UMU-Proton、Wine、GameMode、MangoHud、Gamescope、Protontricks、VKD3D 与
Intel/AMD 开源 Vulkan 运行时，并说明 Steam 是专有软件、继续即记录你对
Valve Steam Subscriber Agreement 的显式接受。确认后它请求
`bundle-gaming-setup`，显示不可变计划里的固定包目标，再次确认后依次执行
`confirm` 与 `pkexec apply`。

### 备份（Backups）

填写「Prefix or save directory」「restic repository」「Password file」三项，点
**Create backup**。它执行 `restic --repo <仓库> backup <目录> --json`，通过
`RESTIC_PASSWORD_FILE` 传递密码文件。密码文件必须存在、源必须是目录；仓库由
restic 自己打开校验，`restic` 未安装时程序直接报错。

### 活动（Activity）

启动、导入、部署与备份的结果都会记进本地活动表（最多显示最近 100 条）。

## 何时需要 root

程序**自己拒绝以 root 运行**。部署游戏环境时，只有 `apply` 一步通过
`pkexec` 请求 Polkit 授权；库扫描、导入、启动与备份都不提权。备份即使写入
系统目录，也只以当前用户身份执行，由文件系统权限决定成败。

## 已知限制

- 部署的软件包集合由 catalog 的 `bundle-gaming-setup` 决定，程序不能自选或增减；
  catalog 缺少该 bundle 时计划直接失败。
- 只接受 `.exe` 导入；不识别原生 Linux 游戏（Steam 库里的由 Steam 启动）。
- 没有删除或卸载游戏、清除库条目的界面；备份也没有取消按钮。
- 游戏、备份或环境部署运行中不能关闭窗口。
- 备份依赖系统已安装 `restic`；程序不负责安装它。
- 兼容运行器路径固定为 `/usr/bin/umu-run` 与 `/usr/bin/wine`，缺席时启动会报
  「未安装」而不是自动回退。

## 深入设计

状态库与活动记录是本地 SQLite；兼容启动规则、prefix 边界与备份命令都写在
[`linxira-gaming-manager`](https://github.com/Linxira-OS/linxira-gaming-manager)
仓库里。事务形状见 [Components](linxira-components.md)。
