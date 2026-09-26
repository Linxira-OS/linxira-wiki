# Components（linxira-components）

## 为什么存在

系统里任何会改机器的动作都需要一个统一的形状：先算出一份计划，让用户看清，
用户确认之后再由 root 执行，执行完留下可核对的凭据。没有这个形状，
每个功能各自 `sudo` 一次，用户既看不懂要发生什么，也无法事后核对到底发生了什么。

`linxira-components` 就是那个形状本身。它是**唯一**拥有
transaction-planning、confirmation、privileged-apply、receipts 的项目。

## 职责边界

**归它**：catalog 读取、目标选择、计划生成（plan）、计划确认（confirm）、
以 root 执行（apply）、receipt 产出、库存与已安装状态查询、Timeshift 类快照后端、
工作区守护的快照与恢复执行。

**不归它**：

- **不决定「装什么」**。软件与组件的清单在 [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog)。
- **不做 UI**。界面在 `linxira-package-center` 与 `linxira-component-manager`，它们调用本项目，不复制本项目的逻辑。
- **不做通用设置**。镜像源、SSH、防火墙等在 [`linxira-config`](linxira-config.md)。

## 怎么用

计划三步走，每一步的产物都是文件，可以被人读过再交给下一步：

```bash
# 1. 计划
linxira-components list --catalog /usr/share/linxira/catalog/catalog-v3.json --json
linxira-components plan --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --profile workstation --output-dir ./out

# 2. 确认（确认一个未改动的计划）
linxira-components confirm --catalog /usr/share/linxira/catalog/catalog-v3.json \
    --plan ./out/request-plan.json --output-dir ./out

# 3. 执行（需要 root 与授权）
linxira-components apply --confirmation ./out/confirmation.json
```

工作区守护是同一套形状下的另一组动作：

```bash
linxira-components guard status                                  # 只读，免授权
linxira-components guard register ~/Linxira-OS                  # 弹 Polkit
linxira-components guard snapshot ~/Linxira-OS
linxira-components guard restore <id> --target ~/ws-restored
```

详见 [工作区守护](workspace-guard.md)。

## 何时需要 root

- **不需要**：`list`、`inventory`、`plan`、`confirm`。计划与确认都是纯计算。
- **需要**：`apply` 与 `guard` 的 `init` / `register` / `unregister` / `snapshot` / `restore`。
  这些走 D-Bus，由 Polkit 弹窗向用户授权，**不需要 agent 自己持有 sudo**。

计划文件与执行之间会做漂移检查：系统状态在两步之间变了，这份计划就作废。
这是刻意的——计划给用户看的是当时的系统，不是现在的系统。

## 深入设计

[Direct Arch 架构](https://linxira-os.github.io/linxira-wiki/Linxira%20%E7%89%B9%E6%80%A7/architecture/) ·
内部实现见 [`linxira-components`](https://github.com/Linxira-OS/linxira-components) 仓库的 `document/` 目录。
