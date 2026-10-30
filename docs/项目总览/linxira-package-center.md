# 快速配置系统软件（linxira-package-center）

## 为什么存在

通用软件中心（Shelly）负责「什么都能装」；这台工作站还需要一个只放经过审核的
精选应用的地方。`linxira-package-center` 就是那个地方：一个安装专用的 PySide6
界面，默认读取 Catalog v3，把应用按可展开的类别树摊开，生成一份与 catalog
绑定的计划，把未改动的计划原样给你看，确认之后再让 `linxira-components`
以 root 执行。

它从不拼装包命令，从不直接调用 pacman，也不复制后端已有的校验逻辑。

## 职责边界

**归它**：选择界面、事务呈现、进度、已安装状态展示、延后安装的续装提示。

**不归它**：

- **计划、确认与特权执行不归它**。这三步由 [`linxira-components`](linxira-components.md)
  拥有，界面只调用它。
- **元数据与策略不归它**。哪些应用可选、属于哪个类别、是否推荐，由
  [`linxira-catalog`](https://github.com/Linxira-OS/linxira-catalog) 决定。
- **配置与诊断不归它**。镜像、SSH、防火墙等在 [Config CLI](linxira-config.md)。
- **移除不归它**。Phase 1 只安装；共享后端还没有归属台账、依赖归因与漂移检测之前，
  没有包移除入口。

## 怎么用

```bash
linxira-package-center
```

没有命令行参数，应用菜单里的「快速配置系统软件」执行的就是
`/usr/bin/linxira-package-center`。可用环境变量：

| 变量 | 默认值 | 作用 |
|---|---|---|
| `LINXIRA_CATALOG_PATH` | `/usr/share/linxira/catalog/catalog-v3.json` | 读取的 catalog |
| `LINXIRA_INSTALLED_STATE_PATH` | 未设置 | 可选的已安装状态文档；不提供时「已安装」视图为空，catalog 其余功能照常 |
| `LINXIRA_PENDING_INSTALL_PATH` | `/var/lib/linxira/pending-install.json` | 安装时因缺网延后的应用列表；装完后这个文件会被删除 |

事务后端固定为 `/usr/bin/linxira-components`，提权固定为 `/usr/bin/pkexec`。

主流程：

1. 用顶部「显示」筛选器切换视图：已审核且可安装、镜像自带（离线可装）、
   需联网、已安装、第三方审核频道（仅查看，需 opt-in）。
2. 展开类别勾选应用。类别按 `multi`、`exclusive`（最多一项）或 `bounded`
   （`maxSelected`）约束选择，半选状态表示只选了部分子项。已安装项显示为
   锁定的选中叶子，不能被勾掉，也不会被当作移除提交。
3. 点「安装所选软件」。若选择里有需要接受许可的专有软件，会先弹出确认对话框，
   接受记录随计划一起写入。
4. 界面在临时目录里生成 `org.linxira.component-selection.v1` 选择文档（绑定
   catalog 的 SHA-256 与 release），调用 `linxira-components plan`，然后弹出
   「确认安装计划」窗口，原样显示不可变的 `request-plan.json`。
5. 确认后依次执行 `linxira-components confirm` 与
   `pkexec linxira-components apply --confirmation ...`，进度显示在状态栏。
   取消或失败时临时事务目录会被删除。

已安装状态文档是可选的：可以是 `installedApplications: [id, ...]`，也可以是一张
`applications` 映射，值是带安装状态的对象。`partial`（部分安装）的应用会被预选
并在安装时补全缺失的包；`LINXIRA_PENDING_INSTALL_PATH` 里列出的续装应用同样会被预选。

## 何时需要 root

界面本身以普通用户运行。`plan` 与 `confirm` 是纯计算，不提权；只有 `apply`
通过 `pkexec` 请求管理员授权，由 Polkit 弹窗向用户确认。你不需要在终端里
自己 `sudo`，也不应该用 root 启动这个界面。

## 已知限制

- **Phase 1 仅安装**。没有卸载、降级或回滚入口；已安装的应用只作为锁定状态展示。
- **第三方审核频道只读**。AUR、WPS、专有/混合许可等候选会标出来源、许可证、
  审核状态与 opt-in 要求，但保持禁用，不表示为「可安装」。
- **v3 类别根需要 catalog 配合**。以应用类别作为事务根时，需要 catalog 同时提供
  一个同 ID、直接子项完全相同且全部标记为 `optional` 的 bundle；当前独立
  Catalog v3 没有这个契约，因此计划会在调用后端之前就失败（fail closed）。
  界面不会伪造 bundle 路径。
- Catalog v2 仍受支持，但要求条目 `installer: true` 且 `review.status: reviewed`。
- 不安装驱动、内核或系统更新；这些有各自的工具与事务边界。

## 深入设计

产品边界见仓库的 `docs/BOUNDARIES.md`；事务形状见
[Components](linxira-components.md)，内部实现见
[`linxira-package-center`](https://github.com/Linxira-OS/linxira-package-center)。
