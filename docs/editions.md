# 多底座与构建策略

本页说明 Linxira 在多条底座上的边界、承诺与更新节奏。站点公告见
[多底座路线预告](https://linxira-os.github.io/zh/blog/editions-and-build-strategy/)。

## 定位

Linxira 不是从零构建的发行版，而是**上游发行版之上的可移除层**：catalog、
事务计划/确认/回执、签名仓库、配置入口、更新提醒、崩溃监视与欢迎中心。
每种底座只负责提供内核、硬件 enablement 与基础用户态；Linxira 负责把常用
软件、权限边界与可复现的环境装好。

## 三条线

| 线 | 底座 | 定位 | 更新节奏 | 退出方式 | 状态 |
|---|---|---|---|---|---|
| **Arch x86_64** | Arch Linux | 主力开发机，也可推理 | 滚动；计划每月一次 ISO 快照 | 卸掉 `linxira-*` 回到原生 Arch | 当前主线 |
| **Ubuntu x86_64 / ARM64** | Ubuntu 26.04 LTS | 推理机、科学计算、国产 GPU；ARM 面向 DGX Spark、N1X 等 | LTS 定点 + 上游安全；HWE 随点版本 | 衍生层可移除，但不是滚动退出 | 调研中 |
| **NixOS** | NixOS（VM / 容器） | 可复现参考环境、benchmark、工具链 | flake 锁定，按需更新 | 只交付配置与 flake | 实验性，无 SLA |

## Ubuntu 时间线（避免等待不存在的版本）

- 26.04 LTS：2026-04-23 发布，标准安全维护到 2031-05，ESM 到 2036。
- 26.10：2026-10 发布，9 个月支持，2027-07 结束。
- 27.04 “Tenacious T-Rex”：2027-04-22，仍是 9 个月 interim。
- 27.10：2027-10，interim。
- 下一个 LTS：28.04（2028-04）。

因此不存在“2027 年 7 月之后发长期版”的选项。要 LTS + 7.3 内核，目标是
**26.04.2 点版本（2027-02-18）**：按 Ubuntu HWE 节奏，它会把 26.10 的 7.3
带进 26.04 LTS，最终以 Ubuntu release notes 为准。

## 中国网络与镜像

- **Arch**：国内镜像完整（TUNA、USTC、阿里云等）；月度 ISO 计划放
  GitCode / 国内对象存储。
- **Ubuntu**：官方归档有国内镜像（TUNA、USTC、阿里云、华为云等）；apt 源与
  ISO 可走国内。安装器会提供国内源选项。
- **NixOS**：TUNA、USTC、SJTU 提供 nix-channels 与 binary cache 镜像，但覆盖
  与稳定性不保证；在访问稳定前，NixOS 只做实验性 VM 参考环境，不作承诺。
- **国产 GPU**：摩尔线程、昇腾等驱动与工具链以 Ubuntu 为主。
- **DGX Spark / N1X**：NVIDIA DGX OS 基于 Ubuntu 26.04 LTS ARM64，但下载可能
  受账号/网络限制；只对白名单机型支持，不承诺通用 ARM。

## 构建与事务契约

- **catalog** 是软件与目标平台的唯一真相；每个应用的目标包按 edition 映射，
  不在 UI 或安装器里硬编码包名。
- **components** 保留 `plan → confirm → apply → receipt`；执行层按 edition
  选择后端：
  - Arch：固定 argv `pacman`；
  - Ubuntu：固定 argv `apt-get` / `dpkg-query`。
- **update / config-hub** 通过 edition 适配器选择源与更新方式，UI 共用同一套
  状态 schema。
- **ISO** 两条线各自维护构建脚本，但共用选择/确认/回执的 UX。

## 边界

1. 薄层、可退出：Arch 卸掉 `linxira-*` 后仍是原生 Arch；Ubuntu 同样保持层可
   移除，但不是滚动发行版。
2. 只带常用软件，不塞赞助商软件或奇怪的系统组件。
3. 默认保守的供应链：Arch 不开 AUR；Ubuntu 不开未审核 PPA；厂商 deb 审核后
   进入签名仓库；不推荐 `curl | sh`。
4. 不自建内核：Arch 用官方最新；Ubuntu 用 HWE/厂商内核；没有完整自动化流水线
   之前不做 v3 / CachyOS 派生内核。
5. AI 可选：默认不自动运行 agent；crash-watch 默认 0 token 分流，用户触发才
   启动，本地只读、不上传。

## 下一步

- Ubuntu：调研 26.04 LTS + 7.3 HWE、国产 GPU、DGX Spark / N1X 白名单；完成前
  不承诺发布日期。
- NixOS：只做 flake / VM 配置。
- Arch：继续主线，推进月度 ISO 快照与可退出性验收。
