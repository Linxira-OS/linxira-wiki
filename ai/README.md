# Linxira Wiki — AI 资产

本目录是 [Linxira 官方手册](https://github.com/Linxira-OS/linxira-wiki) 的机器可读形态。
人读形态是同源的 `docs/`（mkdocs 站点），AI 形态是本目录。人与 AI 读的是同一批内容，没有第二份真相。

## 怎么读

1. `manifest.json` — 索引。先读它，再只打开与请求相关的主题。
2. `topics/*.md` — 每个主题一页，≤ 60 行，只讲「什么时候用、怎么调、要什么权限」。

在已安装 Linxira 的机器上：

```bash
linxira-wiki manifest              # 打印 manifest
linxira-wiki list                  # 列出全部页面
linxira-wiki show workspace-guard  # 读一个主题
linxira-wiki search privilege      # 按关键词定位页面
```

## 边界

本包覆盖**跨项目边界与操作逻辑**：谁拥有什么、该用哪个工具、什么时候需要授权。
具体项目的内部设计、数据结构、实现决策**不在本包**，在各项目自己仓库的 `document/` 目录。

## manifest 是生成物

`manifest.json` 由 `scripts/generate-manifest.py` 生成，不要手工编辑。
改仓库归属就改 `linxira-os/governance/repositories.yaml`，然后重跑生成器。CI 会校验生成物是否与数据源一致。

## front-matter 词汇

| 字段 | 取值 |
|---|---|
| `name` | 主题标识，`linxira-wiki show <name>` 用它定位 |
| `summary` | 一句话说明 |
| `audience` | `human` / `ai` |
| `tools` | 该主题涉及的 CLI 入口名 |
| `privilege` | `none`（只读免授权）/ `user`（需用户本机交互）/ `polkit`（需用户在授权弹窗确认） |
