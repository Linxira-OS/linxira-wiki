# 签名密钥环（linxira-keys / linxira-keyring）

## 为什么存在

pacman 要验证 `[linxira]` 仓库的包与数据库，系统里必须先有一把被本地信任的发布公钥。
让用户自己下载 ASCII 公钥、手工导入、再逐条设置信任，既容易出错，也无法审计。
密钥环把「公钥 + 指纹 + 本地签名」做成一个普通软件包，随系统一起交付。

私钥不在这个链路里：包只分发公钥，签名发生在维护者的构建环境。

## 职责边界

**归它**：

- `linxira-keyring` 包安装公钥与指纹：
  `/usr/share/keyrings/linxira.gpg`、`/usr/share/keyrings/linxira-release-fingerprint`。
  包只带二进制公钥与指纹文件，不带 ASCII 公钥。
- 安装脚本以 root 身份把公钥加入 pacman 的 keyring，并对发布密钥做本地签名
  （`pacman-key --add`、`pacman-key --lsign-key`）。
- 密钥金库（私有仓库 `linxira-keys`）保管加密的私钥材料与公钥源文件；加密口令由
  密钥持有者单独保管，不在任何仓库里。

**不归它**：

- 不签名软件包；包与仓库数据库的签名由维护者的签名环境完成，发布流程在
  `packages` 仓库（`scripts/publish-repo.sh`）。
- 不托管仓库；`linxira-packages` 由 GitHub Pages 提供，且不产生签名。
- 不启用 `[linxira]` 仓库；仓库配置在 `/etc/pacman.conf`。
- 不清除旧密钥；卸载包时 `post_remove` 是空操作。
- 不托管私钥恢复步骤。本 wiki 不记录解密、导入私钥或口令处理流程。

## 谁做什么

| 参与方 | 负责 | 不负责 |
|---|---|---|
| 私有金库 `linxira-keys` | 加密的私钥（`linxira-master-secret.asc.enc`、`linxira-signing-subkey.asc.enc`）、公钥源文件（`linxira.asc`、`linxira.gpg`） | 不签名、不分发、不含任何口令 |
| `packages` 仓库的 `linxira-keyring` 包 | 打包公钥与指纹，`post_install` 与 `post_upgrade` 导入并本地签名 | 不签名软件包、不托管仓库、不启用仓库 |
| `linxira-packages`（GitHub Pages） | 托管包、`.sig`、签名数据库、`SHA256SUMS` 与仓库版 `x86_64/linxira.gpg` | 不产生签名；发布自动化推入已签产物 |
| ISO 与 WSL 镜像 | 预装 `linxira-keyring`，作为首次信任的引导来源 | 不代替仓库对后续包验签 |

签名在维护者的签名环境里、用从金库恢复的签名子密钥完成。私钥与口令永远不进
`[linxira]` 仓库，也不进任何镜像。

## 怎么用

新装系统上，密钥环由 ISO 提供并由 pacman 正常安装（WSL 镜像的包清单同样包含
`linxira-keyring`）。之后启用仓库：

```ini
[linxira]
Server = https://linxira-os.github.io/linxira-packages/$arch
SigLevel = Required DatabaseOptional
```

公钥信息：

| 属性 | 值 |
|---|---|
| UID | `Linxira OS Release Signing <release@linxira.org>` |
| 主密钥指纹 | `E1A4155F457D1481CA85EE6BF9D157739534BC29` |
| 签名子密钥指纹 | `D477286C296F1E1C35735E52B22DF3E636274191` |

这些是公开信息，可以写进脚本或核对清单；私钥材料不是。

用户不需要手动导入公钥，也不需要在每台机器上重新设置信任——`post_install` 与
`post_upgrade` 都会重新执行导入与本地签名。

## 何时需要 root

- 读取 `/usr/share/keyrings/` 下的公钥与指纹不需要 root；它们本来就是公开信息。
- 安装或升级 `linxira-keyring` 是普通的 root 包操作（`pacman` 执行）。
- 包脚本里的 `pacman-key` 调用由 pacman 以 root 身份运行，用户不直接执行。
- 日常装包仍是 root 操作，但密钥信任已经在系统层完成。

## 已知限制

- **首次信任是自举的**：密钥环包本身无法由它将要启用的 `[linxira]` 仓库验证。
  它必须来自 ISO 或其他已受信任的渠道；不要从未知镜像首次安装密钥环。
- 安装脚本对 `pacman-key` 的失败不报错（调用后接 `|| true`），所以装完应自行确认
  该指纹已出现在本地 keyring 中，而不是假定信任一定建立。
- 卸载包不会删除 pacman keyring 里的密钥（`post_remove` 是空操作）；需要撤销信任时
  由管理员显式删除（`pacman-key --delete <指纹>`）。
- 私钥与口令只存在于私有密钥仓库和密钥持有者手中；本 wiki 不提供恢复流程，
  也不应把私钥材料写进文档、脚本或 issue。
- 指纹轮换必须发新的密钥环包；安装新包只添加并本地签名当前公钥，不会自动删除本机
  仍存在的旧公钥。
- 包里的公钥不是仓库的完整信任来源：`linxira-packages` 还会提供 `x86_64/linxira.gpg`，
  两者都来自同一把发布密钥。

## 深入设计

仓库托管与签名说明见
[`linxira-packages`](https://github.com/Linxira-OS/linxira-packages)；
密钥环包定义见
[`packages/packages/linxira-keyring`](https://github.com/Linxira-OS/packages/tree/main/packages/linxira-keyring)。
