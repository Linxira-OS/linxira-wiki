# 快速配置系统运行时（linxira-component-manager）

## 为什么存在

应用之下还有一层东西：能力捆绑包、运行时、工具链、领域工作区。它们有依赖、
有互斥、有「必需」项，逐个 `pacman -S` 既看不清关系，也没法解释为什么要装。
`linxira-component-manager` 把这一层做成类似 Windows「启用或关闭功能」的
可展开三态树：勾选即请求安装，展开即可看到嵌套关系，确认前还能看到完整的计划。

图形界面、TUI 和命令行共用同一条事务核，四条入口（GUI、TUI、CLI、agent）
走的是同一个 `plan → confirm → apply` 链。

## 职责边界

**归它**：Catalog v3 捆绑包树的选择界面（GUI / TUI / CLI）、节点元数据与
选择文档预览、confirmation 之前的计划展示。

**不归它**：

- **不把组件 ID 展开成包名**，也不直接调用任何包管理器。
- **不做计划、确认与特权执行**。那三步在 [`linxira-components`](linxira-components.md)。
- **不做移除**。Phase 1 只安装已就绪的软件包目标。
- **不定义元数据**。bundle、角色、选择策略都来自 catalog。

## 怎么用

### 图形界面

```bash
linxira-component-manager                          # 用默认 catalog
linxira-component-manager --catalog ./catalog-v3.json
linxira-component-manager --select component-fish  # 预选叶子，可重复
```

默认依次查找 `/usr/share/linxira/catalog/catalog-v3.json` 与
`/usr/share/linxira/catalog/catalog.json`；都没有时会打开空界面，用 `Ctrl+O`
选择文件，`Ctrl+S` 保存选择 JSON。`--select ID` 只做预选，真正的安装事务仍在
界面里完成——欢迎中心的终端页就是这样把某个 shell 预选好后交过来的。

界面只展示 `surface` 为 `components` 的顶层 bundle（省略时按 `components` 处理）。
右侧标签页分别显示节点详情、实时选择 JSON 和「Backend plan」。点
**Plan with linxira-components** 后：

1. 把完整的 `org.linxira.component-selection.v1` 文档写进私有临时目录；
2. 运行 `linxira-components plan --catalog ... --selection ... --output-dir ...`；
3. 显示不可变的 `request-plan.json`，分别列出 ready 包目标、pending 与 unsupported；
4. 你确认后，对这份确切的计划运行 `linxira-components confirm`；
5. 若 `directPackageTargets` 非空，运行
   `pkexec linxira-components apply --catalog ... --confirmation ...`。

没有任何直接包目标、只有 pending / unsupported 时，只确认，不请求 `pkexec`。
pending 与 unsupported 永远不参与应用。

### 终端界面

```bash
linxira-component-manager --tui
linxira-component-manager --tui --catalog ./catalog-v3.json
```

按键：↑/↓（或 `k`/`j`）移动，空格切换选择，`a` 全选/全不选，Enter 生成计划并确认
安装，`q` 或 Esc 退出。授权模式为 `auto`：以 root 运行就直接执行，否则走 `pkexec`。

### 指令模式

```bash
linxira-component-manager list
linxira-component-manager list --json
linxira-component-manager status component-fish
linxira-component-manager status component-fish --json
linxira-component-manager install component-fish --dry-run
linxira-component-manager install component-fish --yes
linxira-component-manager --catalog ./catalog-v3.json install component-fish
```

- `list` 只列 `component` 与 `application` 中可用（`available`）的叶子，
  并从 `linxira-components inventory` 读取安装状态；后端不可用时状态显示 `unknown`。
- `status` 接受一个或多个叶子 ID。
- `install` 走同一条 `plan → confirm → apply` 链。`--dry-run` 只打印计划中的
  包目标；`--yes` 跳过交互确认（供 agent 使用）；`--json` 输出机器可读结果。
  未安装的 pending 项会在输出里单独说明并跳过。
- 退出码：`0` 成功，`2` 选择或计划被拒，`3` 授权或执行失败，`64` 用法错误。

## 何时需要 root

GUI、TUI 与 CLI 的授权模式默认是 `auto`：**以 root 运行时直接执行 apply，
普通用户运行时通过 `pkexec` 请求 Polkit 授权**。计划与确认两步都不提权。
你不需要自己写 `sudo`；也不应该用 root 启动图形界面。

## 已知限制

- **Phase 1 只安装**：已就绪的软件包目标可以装，移除尚未支持。
- pending 与 unsupported 叶子会在确认前明确列出，但永远不会被应用。
- 没有 `--component`、profile/application、包管理器、remove 或 shell 回退；
  这些不是「还没写文档」，而是刻意不存在。
- 只消费 Catalog v3，不翻译 v2 的 profile 或包数组。bundle 图出现直接或间接循环
  会被拒绝。
- required 叶子被锁定并说明原因；`exclusive` 会清掉同级互斥项；`bounded` 超过
  `maxSelected` 时会拒绝，而不是静默截断。
- 无可用 catalog 时 CLI 直接报错，需要 `--catalog PATH` 或安装 `linxira-catalog`。

## 深入设计

嵌套示例见仓库的 `examples/catalog-v3.example.json`；事务形状见
[Components](linxira-components.md)，内部实现见
[`linxira-component-manager`](https://github.com/Linxira-OS/linxira-component-manager)。
