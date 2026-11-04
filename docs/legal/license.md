# 许可与法律

本页回答两件事：这份 Wiki、Linxira 的代码分别按什么许可发布，以及使用这些内容与软件时你需要自己承担哪些风险。官网法律页 <https://linxira-os.github.io/zh/legal/license/> 是权威版本；本页只是 Wiki 内的解释与入口，两者不一致时以官网为准。

## 本 Wiki 的许可

Wiki 里同时存在两种内容，许可不同：

| 内容 | 许可 | 说明 |
|---|---|---|
| `docs/**` 下的页面正文 | **CC BY-SA 4.0** | 署名 + 相同方式共享 |
| 站点代码（构建脚本、主题组件、wiki CLI） | **MIT** | 见仓库根目录的 `LICENSE` |
| 正文里引用的源码片段 | 随片段所属仓库 | 引用不改写原仓库的许可 |

换句话说：读、转载、翻译这些页面是允许的，但必须保留署名，并且修改后的版本要继续以 CC BY-SA 4.0 发布。

### CC BY-SA 4.0 在实践中意味着什么

- **署名**：转载、翻译、摘编时保留来源（Linxira OS 文档）、原页面链接与许可声明。
- **相同方式共享**：修改后的文档必须以 CC BY-SA 4.0（或与之兼容的许可）发布，不能追加更严格的条款。
- **允许商用**：CC BY-SA 不禁止商业使用，但署名与相同方式共享的义务不变。
- **不是背书**：署名只表示来源，不表示项目认可你的版本或服务。
- **代码片段看仓库**：页面里贴出的命令和配置片段若来自某个代码仓库，以该仓库的 `LICENSE` 为准。

!!! note "文档与代码的边界"
    同一个仓库里可能同时存在两种许可。`linxira-wiki` 的构建脚本与 CLI 是 MIT，而 `docs/**` 下的正文是 CC BY-SA 4.0。判断依据是文件位置与仓库声明，不是仓库名。

## 代码许可按仓库决定

每个仓库自带 `LICENSE`，没有“整个项目一个许可”这回事：

| 仓库 | 许可 | 依据 |
|---|---|---|
| `linxira-catalog`、`linxira-config-hub`、`linxira-component-manager`、`linxira-welcome`、`linxira-crash-watch`、`linxira-package-center` 等多数第一方仓库 | MIT | 仓库 `LICENSE` |
| `linxira-update` | GPL-3.0-or-later | `LICENSE` 为 GNU GPL v3 全文；README 与源码 SPDX 头声明「或任何更新版本」 |
| `linxira-hooks` | GPL-3.0-or-later | `LICENSE` 为 GNU GPL v3 全文；`PKGBUILD` 的 `license=` 字段为 `GPL-3.0-or-later` |
| `linxira-hwd-detector` | GPL-3.0-only | `LICENSE` 为 GNU GPL v3 全文；`Cargo.toml` 与 README 均为 `GPL-3.0-only` |
| `linxira-bio-sdk` | AGPL-3.0-or-later | `LICENSE` 为 GNU AGPL v3 全文；`Cargo.toml` 为 `AGPL-3.0-or-later` |

修改过上游代码的仓库（例如 `linxira-update`、`linxira-hwd-detector`）另有 `UPSTREAM.md`，记录上游项目、上游许可与本地改动。

!!! warning "「or later」要逐个仓库确认"
    `linxira-update` 与 `linxira-hooks` 的 `LICENSE` 文件本身是 GNU GPL v3 全文，「或任何更新版本」来自仓库元数据与源码声明（README、SPDX 头、`PKGBUILD` 的 `license=` 字段）。`linxira-hwd-detector` 则明确写为 `GPL-3.0-only`，不提供升级到后续版本的选项。判断某个仓库时，请读它的 `LICENSE`、包元数据与源码头，不要只看本表。

## 品牌资产

Logo、壁纸、图标等品牌资产属于 Linxira 保留权利的资产，**不随文档的 CC BY-SA 4.0 授权**，也不按通用公共许可发布。二次分发、修改或在其他项目中使用前，先读[品牌资产政策](https://linxira-os.github.io/zh/docs/brand-assets/)。

## 上游组件与非自由组件

- **上游组件各自持证**：基础系统、内核、GNU 工具、浏览器、办公套件等仍由各自的上游项目授权。把它们一起装进一个发行版，不意味着整台系统变成单一许可。
- **GPL copyleft 的边界**：本地运行 Linxira OS 不受 copyleft 限制；基于它制作衍生发行版时才需要遵守相应上游许可；你自己的配置和脚本不受影响，除非其中包含 GPL 代码。
- **非自由组件是可选项**：部分硬件的专有固件、NVIDIA 驱动、VS Code、Chrome 等并非自由软件，由用户自行选择安装，Linxira OS 不强制使用。它们各自的许可条款优先于本文。
- 完整的上游组件清单、许可文本与逐项说明，见[官方许可页](https://linxira-os.github.io/zh/legal/license/)。

## 法律风险与免责

!!! warning "软件按「原样」提供"
    Linxira OS 不提供任何形式的担保。项目由个人/小团队维护，背后没有基金会或公司作为法律主体，也不提供 SLA 或商业支持。因使用本系统造成的数据丢失、业务中断或其他损失，由使用者自行承担。

| 风险 | 具体表现 | 建议动作 |
|---|---|---|
| 测试镜像与滚动发布 | 镜像可能是测试版；滚动更新会持续引入上游变化，个别更新可能让某个功能暂时失效 | 不要在唯一的生产设备上追新；升级前确认有可回滚的快照 |
| 更新本身的破坏性 | `pacman -Syu` 是系统级事务 | 更新前备份重要数据；保留更新前的 Timeshift 快照 |
| root 操作 | 提权后的命令（分区、删除、覆盖配置）没有撤销键 | 执行前读清命令；不要整段复制粘贴来源不明的 root 命令 |
| 第三方与专有软件 | 专有驱动、闭源应用有自己的条款与支持渠道 | 安装前确认许可与来源 |
| AUR | AUR 包不是官方仓库，默认未启用，包由本机编译，没有签名背书 | 读完整 PKGBUILD 与 `.install`；只用你愿意承担风险的包 |
| 没有法律实体 | 无法提供商业合同、赔偿或合规承诺 | 有合规要求时自行评估 |

## 使用条款

以下是本项目对外表达的使用规则，不构成合同：

- **合法使用**：不得将 Linxira OS 或其组件用于违法用途。
- **不滥用共享资源**：镜像、包仓库、CI 与 Issue 跟踪是公开资源，不要用自动化流量、刷量或滥用行为影响其他人。
- **不冒充官方**：转载或二次分发时不得暗示获得 Linxira 官方认可。
- **第三方条款优先**：一旦你安装第三方或专有软件（含 AUR 包），它们的许可与条款即对你生效，本项目不为它们背书。
- **无担保**：软件与文档均按「原样」提供，不附带任何明示或暗示的担保。
- 条款的权威表述见[官方法律页](https://linxira-os.github.io/zh/legal/license/)；本页不新增任何合同义务。

## 延伸阅读

- [官方许可页](https://linxira-os.github.io/zh/legal/license/)
- [品牌资产政策](https://linxira-os.github.io/zh/docs/brand-assets/)
- [安全与贡献](security.md)
- [维护、信任与软件安全](https://linxira-os.github.io/zh/docs/maintenance-security/)
- [贡献指南](https://linxira-os.github.io/zh/docs/contributing/)
- [更新助手（linxira-update）](../software/update.md)：更新前快照的行为边界
- [软件索引](../software/index.md)

---

[返回 Wiki 首页](../index.md)
