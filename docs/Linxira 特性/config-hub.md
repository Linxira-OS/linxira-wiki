# 配置中心

Linxira Config Hub 是一个跨生态的配置管理工具，帮助用户快速设置开发和科研环境。

## 功能概览

### 源管理

一键配置各类包管理器的镜像源：

- apt (系统包)
- mise (语言版本)
- Miniforge (科学计算)
- npm / bun (JavaScript)

### 镜像测速

自动测试各镜像源的响应速度，推荐最快的源。

### 系统服务配置

- SSH 服务启停与密钥管理
- 远程桌面连接配置
- 防火墙规则管理

## 使用方式

### GUI 版本

从应用菜单启动 "Linxira Config Hub"。

### CLI 版本

```bash
# 查看所有可用命令
linxira-config --help

# 配置 apt 镜像
linxira-config mirror apt

# 配置 mise 源
linxira-config mirror mise

# 启用 SSH 服务
linxira-config service ssh enable
```
