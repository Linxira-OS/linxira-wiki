# 软件目录（linxira-catalog）

## 为什么存在

安装器、Package Center、Component Manager 与 Welcome 都需要知道「有哪些软件、
它们属于哪个类别、默认选什么、是否允许离线安装」。如果每个界面各存一份清单，
同一个软件在不同入口的 ID、默认值和评审状态就会漂移。

`linxira-catalog` 是唯一一份经过评审、带版本的软件组件元数据。它只描述软件与选择
模型，不执行任何包事务。

## 职责边界

**归它**：

- `catalog-v3.json`：`desktops[]`、`applications[]`、`components[]`、`bundles[]`、
  `operations[]`、`categories[]` 的规范图。
- `schema/*.schema.json`：JSON Schema Draft 2020-12 契约，构建时校验。
- 稳定的叶子 ID：安装器、管理器、计划、回执与 CLI 交接都用同一套 ID。
- 离线策略：`included`（镜像自带）、`online-only`（需联网）、
  `defer-with-consent`（可选延后），供每个安装面显示同一枚徽标。
- `catalog-v2.json` 作为既有消费者的兼容输入保留；v3 不替换 v2 的 `profiles[]` 模型。

**不归它**：

- 不做计划、不确认、不执行、不出回执——这些是
  [Components](linxira-components.md) 的职责。
- 不提供用户命令；它安装的是数据与 schema，不是 CLI。
- 不包含可执行命令字符串。`operations[]` 里只有固定的受控操作 ID。
- 不消费下游仓库：安装器与各管理器只读固定路径，不回写目录数据。

## 条目契约

每个叶子（桌面、应用、组件、bundle）都要在数据里声明足以让下游安全显示与默认选择的信息：

| 字段 | 作用 |
|---|---|
| `id` / `kind` / `name` | 稳定 ID、条目类型，以及 `zh_CN` 与 `en` 两种显示名 |
| `primaryCategory` | 唯一归属的类别；类别自己声明 `selection.mode`（`multi` / `exclusive` / `bounded` / `preset`） |
| `provider` / `source` / `artifact` | 由哪个生态提供（`pacman`、`aur`、`flatpak`、`conda`、`pip`、`builtin`）、来自哪个来源、装哪些包标识符 |
| `license` | 许可分类、SPDX 标识、是否可再分发、是否需要用户接受 |
| `review` | 评审状态与日期 |
| `availability` | `available` / `review-channel` / `unavailable`、`offlinePolicy`，以及 `default` 或 `optional-review` 通道 |
| `presentation` | 是否推荐、是否默认选中、排序、是否在安装器可见 |

Schema 是严格的：顶层 `additionalProperties` 为 `false`，契约之外的多余字段会让校验失败。`catalogVersion` 固定为 `3`，`release` 形如 `YYYY.MM`。

## 评审契约

- `review.status` 只有四个值：`reviewed`、`vm-test-pending`、`source-review-pending`、`legal-review-pending`。只有 `reviewed` 的叶子可以被默认选中。
- 安装器可见的叶子还要求 `review.status == "reviewed"`；评审中的候选留在 `review-channel`，绝不被默认选中。
- 外部生态（AUR、Conda、专有软件）默认禁用，必须由用户显式选择加入；`conda-forge` 与 `bioconda` 是显式来源，基础系统从不启用。
- `operations[]` 只放固定的受控操作 ID（`reviewed` 或 `vm-test-pending`），永远不是 shell 字符串。
- 类别根 bundle 的成员必须按顺序恰好镜像该类别子项，全部为 optional 引用；嵌套 bundle 必须构成 DAG。

## 怎么用

普通用户不直接调用这个仓库。`linxira-catalog` 包安装两个文件：

```text
/usr/share/linxira/catalog/catalog-v3.json
/usr/share/linxira/catalog/catalog-v3.schema.json
```

消费方按固定路径读取，再通过各自的界面呈现：

| 消费方 | 用途 |
|---|---|
| 安装器 | 安装期的桌面、应用与组件选择 |
| [Package Center](https://github.com/Linxira-OS/linxira-package-center) | 已安装状态与软件呈现 |
| [Component Manager](https://github.com/Linxira-OS/linxira-component-manager) | 运行时、工具与能力状态 |
| [Completion Agent](https://github.com/Linxira-OS/linxira-completion-agent) | 首次联网后的补齐计划 |
| [Components](linxira-components.md) | 从叶子 ID 生成事务计划 |

维护者的校验入口：

```bash
python -m unittest discover -s tests -v
```

校验覆盖 schema、类别根 ID 对与全局 ID、引用、`primaryCategory` 归属、bundle 表面、
嵌套 bundle 无环性、重复成员、provider/source 边界、评审通道策略、离线策略与选择模式。

## 何时需要 root

不需要，永远不需要。目录是只读数据；写入只发生在仓库开发与打包阶段。

## 已知限制

- 安装包只带 v3 数据与 schema；v2 仍留在仓库中供旧消费者使用，不要在 v3 里复用
  v2 的 `profiles[]` 能力模型。
- 选择与回执以叶子 ID 为键，不是树路径；删除叶子或改稳定 ID 会影响所有下游消费者。
- 目录只给包标识符与元数据，不给安装命令；看到「目录里有」不等于「已经安装」。

## 深入设计

数据与 schema 见
[`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog)；
事务如何消费叶子 ID 见 [Components](linxira-components.md)。
