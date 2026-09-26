"""linxira-wiki 阅读器与 manifest 的一致性测试。

CLI 全部只读, 所以测试直接用 --root 指向仓库检出副本, 不需要装包。
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
CLI = REPOSITORY_ROOT / "cli" / "linxira-wiki"
PACKAGE_ROOT = Path("/usr/share/linxira/wiki")


def run_cli(*arguments: str, root: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = ["bash", str(CLI)]
    if root is not None:
        command += ["--root", str(root)]
    return subprocess.run([*command, *arguments], capture_output=True, text=True, check=False)


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_manifest", REPOSITORY_ROOT / "scripts" / "generate-manifest.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def installed_manifest() -> Path:
    return PACKAGE_ROOT / "ai" / "manifest.json"


# ── 装包后的产物 ────────────────────────────────────────────────


def test_manifest_is_installed_and_parses():
    if not installed_manifest().is_file():
        pytest.skip(f"{installed_manifest()} not installed; test the packaged result on a Linxira system")
    document = json.loads(installed_manifest().read_text(encoding="utf-8"))
    assert document["schema"] == "org.linxira.wiki.manifest.v1"
    assert document["repositories"]
    assert document["topics"]


def test_manifest_covers_every_repository():
    if not installed_manifest().is_file():
        pytest.skip(f"{installed_manifest()} not installed; test the packaged result on a Linxira system")
    document = json.loads(installed_manifest().read_text(encoding="utf-8"))
    generator = load_generator()
    expected = generator.parse_repositories(generator.fetch_repositories())
    assert [entry["name"] for entry in document["repositories"]] == [e["name"] for e in expected]


# ── 阅读器行为 ──────────────────────────────────────────────────


def test_show_rejects_path_traversal():
    result = run_cli("show", "../../etc/shadow", root=REPOSITORY_ROOT)
    assert result.returncode == 4
    assert "no such topic" in result.stderr
    assert "root:" not in result.stdout


def test_show_missing_topic_exits_4():
    result = run_cli("show", "no-such-topic", root=REPOSITORY_ROOT)
    assert result.returncode == 4
    assert "no such topic: no-such-topic" in result.stderr


def test_search_handles_dash_prefix():
    result = run_cli("search", "--version", root=REPOSITORY_ROOT)
    assert "unrecognized option" not in result.stderr
    assert result.returncode == 0


def test_show_reads_topic_and_docs_page():
    topic = run_cli("show", "workspace-guard", root=REPOSITORY_ROOT)
    assert topic.returncode == 0
    assert topic.stdout.startswith("---")
    assert "name: workspace-guard" in topic.stdout

    page = run_cli("show", "linxira-config", root=REPOSITORY_ROOT)
    assert page.returncode == 0
    assert "## 为什么存在" in page.stdout


def test_list_covers_every_docs_page():
    result = run_cli("list", root=REPOSITORY_ROOT)
    assert result.returncode == 0
    listed = {Path(line).name for line in result.stdout.splitlines() if line}
    on_disk = {path.name for path in (REPOSITORY_ROOT / "docs").rglob("*.md")}
    assert on_disk <= listed


def test_reader_has_no_elevation_surface():
    forbidden = ("shell=True", "os.system", "sudo", "pkexec")
    text = CLI.read_text(encoding="utf-8")
    for needle in forbidden:
        assert needle not in text


# ── manifest 与数据源一致 ───────────────────────────────────────


def sibling_workspace() -> Path:
    for candidate in (Path(os.environ.get("LINXIRA_WORKSPACE", "")), REPOSITORY_ROOT.parent):
        if candidate and (candidate / "packages" / "packages").is_dir():
            return candidate
    pytest.skip("sibling checkouts absent; the manifest workflow checks this with them present")


def test_generated_manifest_is_current():
    workspace = sibling_workspace()
    generator = load_generator()
    repositories = generator.parse_repositories(generator.fetch_repositories())
    generated = generator.build_manifest(REPOSITORY_ROOT, workspace, repositories)
    rendered = json.dumps(generated, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    committed = (REPOSITORY_ROOT / "ai" / "manifest.json").read_text(encoding="utf-8")
    assert rendered == committed, "ai/manifest.json is stale; re-run scripts/generate-manifest.py"


def test_privilege_rules_match_topic_page():
    generator = load_generator()
    page = (REPOSITORY_ROOT / "ai" / "topics" / "privilege.md").read_text(encoding="utf-8")
    listed = [
        line.split(". ", 1)[1]
        for line in page.splitlines()
        if line[:1].isdigit() and ". " in line
    ]
    assert listed == generator.PRIVILEGE_RULES
