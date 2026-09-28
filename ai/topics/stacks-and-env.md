---
name: stacks-and-env
summary: 软件栈安装与环境变量的一站式入口（config 转发 component-manager）
audience: [human, ai]
tools: [linxira-config, linxira-component-manager]
privilege: root
---

# 软件栈与环境变量（stacks-and-env）

## 何时查这页

用户想在装好的系统（含 WSL）上快速配置常用开发环境：LaTeX、Python、
Java、容器（podman）、Rust、Node.js 等，或设置环境变量（GOPROXY、
EDITOR、代理等）。全部经 `linxira-config` 一个入口完成。

## 命令面（agent 可直接调用）

```bash
linxira-config stack list [--json]              # 列可安装项(含安装状态)
linxira-config stack status <id...> [--json]    # 查询安装状态
linxira-config stack install <id...> --yes [--json] [--dry-run]
linxira-config stack tui                         # 交互 TUI(人用)

linxira-config env set KEY VALUE                 # 写 /etc/profile.d/linxira-env.sh
linxira-config env get KEY [--json]
linxira-config env list [--json]
linxira-config env unset KEY
```

## 架构事实（agent 需要知道）

- `stack` 是**转发桥**：真正的事务链（plan → confirm → apply）在
  `linxira-component-manager`，与 GUI、AI agent 走同一条链；安装逻辑
  单点，config 不自带 pacman 安装。
- 直连 `linxira-config install <pkg>` 被拒止——这是刻意的边界。
- `install` 默认交互确认；非交互场景（agent）必须 `--yes`。退出码：
  0 成功 / 2 计划被拒 / 3 执行失败 / 64 用法错误。
- 选一个组件会带出其所属 bundle 的 required/recommended 集（与 GUI
  勾选语义一致），`--dry-run` 可先看包清单。
- `env` 只管理 `/etc/profile.d/linxira-env.sh`（0644，root），不碰用户
  shell 配置；新登录会话生效。

## 常用栈 id（catalog 3.x）

component-python / component-python-venv / component-uv / component-nodejs /
component-rust / component-java / component-latex / component-lyx /
component-jupyterlab / component-podman / component-buildah / component-skopeo /
component-distrobox / component-apptainer，及数据科学全家桶
（component-python-data / -numeric / -plot / -geo 等）。
以 `stack list` 实时输出为准。

## 权限

WSL 默认 root 直接执行；桌面非 root 走 pkexec 授权（与 GUI 相同）。
