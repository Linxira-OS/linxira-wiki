# linxira-wiki · Agent 开发规范

> **档位:S(治理与发布核心)**
> 本仓职责:Linxira OS 官方用户文档仓 —— 人读 MkDocs 站点 + AI 可读形态;同时是**系统源仓**
> (有 `VERSION` + `release.yml`,进全自动发布链)。
> 通用条款(全局硬约束、发布链、文档纪律等)**一律见**工作区总纲 `f:\Linxira-OS\AGENTS.md`
> 与发布规范 `linxira-os/docs/RELEASE_STANDARD.md`,本文件不复述,只写本仓特有事项。
> 冲突时以本文件为准。

## 职责与边界
- 只记录 Linxira OS **独有**内容(安装器、Welcome、Shelly、Config Hub、软件目录、工作流、品牌);
  通用 Arch/KDE/systemd/pacman/硬件话题外链 Arch Wiki。
- 两种同源形态,唯一真相源:`docs/`(人读,中文 MkDocs)与 `ai/`(AI 读:`manifest.json` + `topics/*.md`)。
- 项目内部设计/数据结构/实现决策属各项目自己的仓库,不写在本 wiki。
- 归属(`repositories.yaml`):`owns: [user-documentation]`,lifecycle `active`。

## 目录布局
- `docs/` —— MkDocs 站点内容(中文)。
- `ai/` —— `manifest.json`(AI 入口索引)+ `topics/*.md`(每主题一页)。
- `cli/linxira-wiki` —— 已安装手册的只读 Bash 阅读器,子命令 `list` / `manifest` / `show` / `search` / `path` / `help`,全部只读、免提权。
- `scripts/generate-manifest.py` —— 生成 `ai/manifest.json`。
- `tests/` —— pytest 用例;`mkdocs.yml` / `requirements.txt` / `VERSION`。

## 构建与校验
```bash
pip install -r requirements.txt      # mkdocs + mkdocs-material
mkdocs build --strict                # 与 CI pages.yml 一致
mkdocs serve                         # 本地预览 http://localhost:8000
python -m pytest -q tests/           # 全部测试(CI pages.yml)
python -m pytest -q tests/ -k "generated_manifest or privilege_rules"   # CI ci.yml 子集
```

## 发布与签名
- 系统源仓:`VERSION`(当前 `0.1.0`)变动 → `.github/workflows/release.yml` 自动打 `v<VERSION>` tag Release(触发分支 `master`)。
- 打包:PKGBUILD 在 `packages/packages/linxira-wiki/PKGBUILD`(git source、`_commit` 固定;
  装 `cli/linxira-wiki` 到 `/usr/bin`,`ai/`+`docs/`+`mkdocs.yml` 到 `/usr/share/linxira/wiki`)。
- 站点发布:`.github/workflows/pages.yml`(push `master`)→ `mkdocs build --strict` → GitHub Pages
  `https://linxira-os.github.io/linxira-wiki/`。

## 禁区
- **不要手改 `ai/manifest.json`** —— 它是生成物。正确流程:改数据源(如 `linxira-os/governance/repositories.yaml`)
  → push → 重跑 `scripts/generate-manifest.py`。CI `ci.yml`(push `master` + 每日 `17 3 * * *` 定时)会校验其与数据源一致。
- 不要把项目内部实现细节写进本 wiki。
- 分支为 `master`,勿推 `main`。

## 关联文档
- 工作区总纲 `f:\Linxira-OS\AGENTS.md`;发布规范 `linxira-os/docs/RELEASE_STANDARD.md`。
- `README.md`;`linxira-os/governance/repositories.yaml`;`packages/docs/AGENT-GUIDELINES.md`。