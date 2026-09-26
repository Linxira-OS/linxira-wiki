#!/usr/bin/env python3
"""生成 ai/manifest.json —— 官方手册的机器可读索引。

数据源:
  * linxira-os/governance/repositories.yaml —— 仓库归属与 lifecycle(公网免 token)
  * packages 仓的 packages/*/PKGBUILD —— 包描述、主页 URL
  * 各项目 pyproject.toml 的 [project.scripts] / [project.gui-scripts] —— CLI 入口
  * 本仓 docs/ 与 ai/topics/ 的 front-matter —— 主题索引

只用标准库。输出确定性: 相同输入产生逐字节相同的文件, CI 直接与仓库内文件比对。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

REPOSITORIES_URL = (
    "https://raw.githubusercontent.com/Linxira-OS/linxira-os/master/governance/repositories.yaml"
)

# 对 AI 的行为约定。来源是 ai/topics/privilege.md 的「行为约定」一节,
# 两处必须逐字一致 —— tests/test_cli.py::test_privilege_rules_match_topic_page 锁定。
PRIVILEGE_RULES = [
    "Never invoke sudo, su, doas, or run0 directly.",
    "Root work goes through linxira-components; Polkit prompts the user for each action.",
    "Read-only commands (list, status, show) never need root.",
    "If authorization is denied, stop and report — do not retry or find another path.",
]

# 本次随手册一起交付的 4 个包。CLI 入口能从 pyproject 抽的抽, 抽不到的写死
# (shell 项目与本包自身没有 pyproject)。privilege 描述该入口的提权方式。
CLI_PACKAGES: dict[str, dict[str, Any]] = {
    "linxira-components": {"pyproject": "linxira-components/pyproject.toml", "privilege": "polkit"},
    "linxira-config-hub": {"binaries": ["/usr/bin/linxira-config"], "privilege": "polkit"},
    "linxira-recovery-diagnostics": {
        "pyproject": "linxira-recovery-diagnostics/pyproject.toml",
        "privilege": "polkit",
    },
    "linxira-wiki": {"binaries": ["/usr/bin/linxira-wiki"], "privilege": "none"},
}

_ENTRY_RE = re.compile(r"^\s*-\s+name:\s*(?P<name>\S+)\s*$")
_FIELD_RE = re.compile(r"^\s+(?P<key>[A-Za-z][A-Za-z0-9]*):\s*(?P<value>.*?)\s*$")
_BLOCK_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9]*):\s*$")
_INLINE_LIST_RE = re.compile(r"^\[(?P<items>.*)\]$")
_ASSIGNMENT_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*?)\s*$")
_QUOTED_RE = re.compile(r"^['\"](?P<value>.*)['\"]$")
_HEADING_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$")
_FRONTMATTER_RE = re.compile(r"\A---\r?\n(?P<body>.*?)\r?\n---", re.DOTALL)
_MAPPING_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*)\s*:\s*(?P<value>.*?)\s*$")

REPOSITORY_FIELDS = ("lifecycle", "owns", "upstream")


def fetch_repositories(url: str = REPOSITORIES_URL) -> str:
    try:
        with urllib.request.urlopen(url, timeout=15) as response:  # noqa: S310 - 固定 https 常量
            return response.read().decode("utf-8")
    except OSError as exc:
        print(f"ERROR: cannot fetch repositories.yaml: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def _unquote(value: str) -> str:
    match = _QUOTED_RE.match(value)
    return match.group("value") if match else value


def _inline_list(value: str) -> list[str]:
    match = _INLINE_LIST_RE.match(value)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group("items").split(",") if item.strip()]


def parse_repositories(text: str) -> list[dict[str, Any]]:
    """抽取 repositories 块。每条以 '- name:' 起头, 其余字段是它的缩进续行。"""
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_block = False
    for line in text.splitlines():
        if not in_block:
            in_block = bool(_BLOCK_RE.match(line)) and line.rstrip() == "repositories:"
            continue
        entry = _ENTRY_RE.match(line)
        if entry:
            current = {"name": entry.group("name")}
            entries.append(current)
            continue
        if current is None:
            continue
        if line and not line[0].isspace() and not line.lstrip().startswith("-"):
            break  # 下一个顶层键, repositories 块结束
        field = _FIELD_RE.match(line)
        if not field:
            continue
        key, value = field.group("key"), field.group("value")
        if key == "owns":
            current["owns"] = _inline_list(value)
        elif key in REPOSITORY_FIELDS:
            current[key] = _unquote(value) if value else None
    for entry in entries:
        entry.setdefault("owns", [])
        entry.setdefault("lifecycle", None)
    return entries


def parse_pkgbuild(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = _ASSIGNMENT_RE.match(line.strip())
        if match and match.group("key") in ("pkgname", "pkgdesc", "url") and match.group("key") not in result:
            result[match.group("key")] = _unquote(match.group("value"))
    return result


def collect_pkgbuilds(workspace: Path) -> dict[str, dict[str, str]]:
    packages_root = workspace / "packages" / "packages"
    found: dict[str, dict[str, str]] = {}
    for pkgbuild in sorted(packages_root.glob("*/PKGBUILD")):
        record = parse_pkgbuild(pkgbuild)
        if record.get("pkgname"):
            found[record["pkgname"]] = record
    if not found:
        print(
            f"ERROR: no PKGBUILD found under {packages_root}; "
            "point --workspace at the directory holding the sibling checkouts",
            file=sys.stderr,
        )
        raise SystemExit(3)
    return found


def parse_pyproject_scripts(path: Path) -> list[str]:
    scripts: list[str] = []
    section: str | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            name = stripped[1:-1]
            section = name if name in ("project.scripts", "project.gui-scripts") else None
            continue
        if section and "=" in stripped:
            scripts.append(f"/usr/bin/{stripped.split('=', 1)[0].strip()}")
    return sorted(set(scripts))


def resolve_cli(workspace: Path, pkgname: str) -> list[str]:
    spec = CLI_PACKAGES[pkgname]
    if spec.get("binaries"):
        return sorted(spec["binaries"])
    pyproject = workspace / spec["pyproject"]
    if not pyproject.is_file():
        print(f"ERROR: cannot read {pyproject}", file=sys.stderr)
        raise SystemExit(3)
    return parse_pyproject_scripts(pyproject)


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        entry = _MAPPING_RE.match(line)
        if entry:
            fields[entry.group("key")] = _unquote(entry.group("value"))
    return fields


def collect_topics(repository_root: Path) -> list[dict[str, str]]:
    topics: dict[str, dict[str, str]] = {}
    for directory in (repository_root / "ai" / "topics", repository_root / "docs"):
        if not directory.is_dir():
            continue
        for markdown in sorted(directory.rglob("*.md")):
            fields = parse_frontmatter(markdown)
            if not fields or "name" not in fields:
                continue
            name = fields["name"]
            topics[name] = {
                "name": name,
                "summary": fields.get("summary", ""),
                "path": markdown.relative_to(repository_root).as_posix(),
            }
    return [topics[name] for name in sorted(topics)]


def build_manifest(repository_root: Path, workspace: Path, repositories: list[dict[str, Any]]) -> dict[str, Any]:
    pkgbuilds = collect_pkgbuilds(workspace)
    cli_packages = {pkgname: resolve_cli(workspace, pkgname) for pkgname in sorted(CLI_PACKAGES)}
    entries: list[dict[str, Any]] = []
    for repository in repositories:
        name = repository["name"]
        pkgbuild = pkgbuilds.get(name, {})
        entry: dict[str, Any] = {
            "name": name,
            "lifecycle": repository["lifecycle"],
            "owns": repository["owns"],
            "detail": pkgbuild.get("url") or f"https://github.com/Linxira-OS/{name}",
        }
        if pkgbuild.get("pkgdesc"):
            entry["desc"] = pkgbuild["pkgdesc"]
        if "upstream" in repository:
            entry["upstream"] = repository["upstream"]
        if name in cli_packages:
            entry["cli"] = cli_packages[name]
            entry["privilege"] = CLI_PACKAGES[name]["privilege"]
        entries.append(entry)
    return {
        "schema": "org.linxira.wiki.manifest.v1",
        "wiki_version": (repository_root / "VERSION").read_text(encoding="utf-8").strip(),
        "audience": ["human", "ai"],
        "how_to_use": {
            "for_agents": (
                "Read this manifest, then only the topics relevant to the request. "
                "深入设计不在本包 — 去该项目仓库的 document/ 目录。"
            ),
            "for_humans": "mkdocs 站点，或 linxira-wiki list / show <topic>",
        },
        "boundary": (
            "本包覆盖跨项目边界与操作逻辑。各项目内部设计、数据结构、实现决策"
            "在其自身仓库的 document/ 目录。"
        ),
        "repositories": entries,
        "topics": collect_topics(repository_root),
        "privilege_rules": list(PRIVILEGE_RULES),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(os.environ.get("LINXIRA_WORKSPACE", Path(__file__).resolve().parent.parent.parent)),
        help="directory holding the sibling checkouts (default: the parent of this repository)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="manifest path to write (default: <repository>/ai/manifest.json)",
    )
    args = parser.parse_args(argv)

    repository_root = Path(__file__).resolve().parent.parent
    output = args.output or repository_root / "ai" / "manifest.json"
    manifest = build_manifest(repository_root, args.workspace.resolve(), parse_repositories(fetch_repositories()))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output} ({len(manifest['repositories'])} repositories, {len(manifest['topics'])} topics)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
