# Components（linxira-components）

## 为什么存在

系统里任何会改机器的动作都需要一个统一的形状：先算出一份计划，让用户看清，
用户确认之后再由 root 执行，执行完留下可核对的凭据。没有这个形状，
每个功能各自 `sudo` 一次，用户既看不懂要发生什么，也无法事后核对到底发生了什么。

`linxira-components` 就是那个形状本身。它是**唯一**拥有
transaction-planning、confirmation、privileged-apply、receipts 的项目。

## 职责边界

**归它**：catalog 读取、目标选择、计划生成（plan）、计划确认（confirm）、
以 root 执行（apply）、receipt 产出、库存与已安装状态查询、
以及工作区守护的快照与恢复执行。

**不归它**：

- **不决定「装什么」**。软件与组件的清单在 [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog)。
- **不做 UI**。界面在 `linxira-package-center` 与 `linxira-component-manager`，它们调用本项目，不复制本项目的逻辑。
- **不做通用设置**。镜像源、SSH、防火墙等在 [`linxira-config`](config.md)。

## 怎么用

日常安装从快速配置系统软件或快速配置系统运行时的界面开始；下面是同一事务链的
CLI 入口。计划三步走，每一步的产物都是文件，可以被人读过再交给下一步：

```bash
# 1. 计划：装好的系统只有 catalog-v3.json，它接受选择文档或固定 bundle
linxira-components plan --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --bundle bundle-python-runtime --output-dir ./out

# 2. 确认（确认一个未改动的计划）
linxira-components confirm --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --plan ./out/request-plan.json --output-dir ./out

# 3. 执行（需要 root 与授权；GUI 走 pkexec，终端里用 sudo 同样可以）
sudo linxira-components apply --confirmation ./out/confirmation.json
```

`--profile` / `--application` 是 Catalog v2 的兼容入口，只对 v2 catalog 文件有效；
装好的系统只安装 `catalog-v3.json`，所以日常安装由包中心与组件管理器生成
`org.linxira.component-selection.v1` 选择文档，再交给 `--selection`。

工作区守护是同一套形状下的另一组动作：

```bash
linxira-components-guard status                                 # 只读，免授权
linxira-components-guard status --json                          # 同一状态，单行 JSON
linxira-components-guard register ~/Linxira-OS                  # 需要 root
linxira-components-guard snapshot ~/Linxira-OS                  # Polkit 授权
linxira-components-guard restore <id> --target ~/ws-restored
```

详见 [工作区守护](workspace-guard.md)。

## 何时需要 root

- **不需要**：`list`、`inventory`、`plan`、`confirm`，以及 `linxira-components-guard status` /
  `linxira-components-guard list`。计划与确认都是纯计算；守护的只读查询在未配置时也只会
  如实报告，不会索取授权。
- **需要 root**：`apply`；`linxira-components-guard init|register|unregister`。`apply` 由 GUI 经
  `pkexec linxira-components apply` 调用，终端里用 `sudo` 等价。
- **Polkit 授权**：`linxira-components-guard snapshot|restore` 走系统 D-Bus 的计划与确认，
  Polkit 按管理员身份询问。**agent 可以发起，但不需要自己持有 sudo**。

计划文件与执行之间会做漂移检查：系统状态在两步之间变了，这份计划就作废。
这是刻意的——计划给用户看的是当时的系统，不是现在的系统。

## 已知限制

- 只有来自 `arch` 源、当前可用的 `pacman` 叶子会变成包目标；AUR、Conda、operation
  与不可用叶子只记为 pending / unsupported，永远不会执行。
- `apply` 不做系统升级、不删除包、不接受任意 pacman 参数；`systemUpgradeRequired` 恒为 `false`。
- 确认与执行之间有任何漂移（catalog 字节、计划内容、最终叶子集合）都会让计划作废。
  这是保护，不是缓存失效。
- 计划与确认文件必须写进一个已存在的目录、普通文件名；符号链接目录会被拒绝。
- 软件包自身的安装脚本与 hook 仍在 Arch 包的信任边界内运行，本项目不改写它们。
- 工作区守护的 `snapshot` / `restore` 需要先由
  `linxira-config workspace-guard enable` 建立守护仓库，否则直接报未配置。

## 深入设计

[Direct Arch 架构](https://linxira-os.github.io/linxira-wiki/Linxira%20%E7%89%B9%E6%80%A7/architecture/) ·
事务设计与信任边界见 [`linxira-components`](https://github.com/Linxira-OS/linxira-components) 仓库的 [`docs/TRANSACTION_BACKEND.md`](https://github.com/Linxira-OS/linxira-components/blob/main/docs/TRANSACTION_BACKEND.md)。
