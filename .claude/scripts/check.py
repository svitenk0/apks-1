#!/usr/bin/env python3
"""Read-only verification used by the /check command of the build-engineer agent.

Groups: agent, structure, git, build, workflow.
Exit code 0 when every check passes, 1 otherwise. Tracked files are never modified;
the build group runs ci.sh / ci.bat, which only write to the ignored .venv/ and build/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IS_WINDOWS = os.name == "nt"
GROUPS = ("agent", "structure", "git", "build", "workflow")

SKILLS = ("project-scaffold", "build-and-test", "github-actions")
SKILL_SECTIONS = (
    "## Коли застосовувати",
    "## Вхідні дані",
    "## Результат",
    "## Перевірки",
    "## Приклад",
    "## Типовий сценарій помилки",
)
COMMANDS = ("git-init", "create-project", "create-build", "create-actions", "check", "init")
COMMAND_SECTIONS = (
    "## Передумови",
    "## Дії",
    "## Очікувані файли",
    "## Перевірка",
    "## Повідомлення про помилку",
)
MANIFEST_SECTIONS = (
    "## Роль",
    "## Область відповідальності",
    "## Правила роботи з файлами",
    "## Заборонені дії",
    "## Критерії успішного завершення",
)
INIT_ORDER = ("/git-init", "/create-project", "/create-build", "/create-actions", "/check")

PROJECT_FILES = (
    "README.md",
    "docs/architecture.md",
    "docs/usage.md",
    "pyproject.toml",
    "requirements-dev.txt",
    "src/hello/__init__.py",
    "src/hello/__main__.py",
    "src/hello/core.py",
    "src/hello/calc.py",
    "tests/test_hello.py",
    "ci.sh",
    "ci.bat",
    "run.sh",
    "run.bat",
    ".github/workflows/ci.yml",
    ".gitignore",
)
GITIGNORE_REQUIRED = ("build/", "dist/", ".venv/", "__pycache__/", ".pytest_cache/", ".env")
FORBIDDEN_TRACKED = re.compile(r"(^|/)(build|dist|\.venv|venv|__pycache__|\.pytest_cache)/|\.pyc$")
SECRET_PATTERNS = re.compile(
    r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gho_[A-Za-z0-9]{30,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[baprs]-[A-Za-z0-9-]{10,}"
)
OS_MATRIX = {"ubuntu-latest", "windows-latest", "macos-latest"}


class Report:
    def __init__(self) -> None:
        self.results: list[tuple[bool, str, str]] = []

    def add(self, ok: bool, name: str, detail: str = "") -> bool:
        self.results.append((ok, name, detail))
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""), flush=True)
        return ok

    @property
    def failed(self) -> int:
        return sum(1 for ok, _, _ in self.results if not ok)


def read(rel: str) -> str | None:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return out.stdout


def venv_python() -> Path:
    return ROOT / ".venv" / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


# --------------------------------------------------------------------------- groups


def check_agent(r: Report) -> None:
    manifest = read(".claude/agents/build-engineer.md")
    if r.add(manifest is not None, "agent: manifest .claude/agents/build-engineer.md exists"):
        missing = [s for s in MANIFEST_SECTIONS if s not in manifest]
        r.add(not missing, "agent: manifest sections", f"missing {missing}" if missing else "")

    for skill in SKILLS:
        text = read(f".claude/skills/{skill}/SKILL.md")
        if not r.add(text is not None, f"agent: skill {skill} exists"):
            continue
        missing = [s for s in SKILL_SECTIONS if s not in text]
        r.add(not missing, f"agent: skill {skill} sections", f"missing {missing}" if missing else "")

    for cmd in COMMANDS:
        text = read(f".claude/commands/{cmd}.md")
        if not r.add(text is not None, f"agent: command /{cmd} exists"):
            continue
        missing = [s for s in COMMAND_SECTIONS if s not in text]
        r.add(not missing, f"agent: command /{cmd} sections", f"missing {missing}" if missing else "")

    init = read(".claude/commands/init.md") or ""
    actions = init.split("## Дії", 1)[-1].split("## Обробка помилок", 1)[0]
    positions = [actions.find(c + "`") for c in INIT_ORDER]
    ordered = all(p >= 0 for p in positions) and positions == sorted(positions)
    r.add(ordered, "agent: /init calls commands in order", " → ".join(INIT_ORDER))
    r.add("зупинись" in init.lower(), "agent: /init stops on errors")


def check_structure(r: Report) -> None:
    missing = [f for f in PROJECT_FILES if not (ROOT / f).is_file()]
    r.add(not missing, "structure: required project files", f"missing {missing}" if missing else f"{len(PROJECT_FILES)} files")
    tests = read("tests/test_hello.py") or ""
    r.add("def test_BasicAddition" in tests, "structure: unit test BasicAddition defined")
    readme = read("README.md") or ""
    r.add("## Запуск проєкту" in readme, "structure: README has run instructions")


def check_git(r: Report) -> None:
    ignore = {line.strip() for line in (read(".gitignore") or "").splitlines()}
    missing = [p for p in GITIGNORE_REQUIRED if p not in ignore]
    r.add(not missing, "git: .gitignore covers build/venv/caches/secrets", f"missing {missing}" if missing else "")

    tracked = git("ls-files").splitlines()
    bad = [f for f in tracked if FORBIDDEN_TRACKED.search(f)]
    r.add(not bad, "git: no build dirs / caches tracked", f"tracked: {bad[:5]}" if bad else f"{len(tracked)} tracked files")

    leaks = []
    for f in tracked:
        path = ROOT / f
        if path.suffix in {".exe", ".png", ".jpg", ".pdf"} or not path.is_file():
            continue
        try:
            if SECRET_PATTERNS.search(path.read_text(encoding="utf-8", errors="ignore")):
                leaks.append(f)
        except OSError:
            pass
    r.add(not leaks, "git: no secrets in tracked files", f"suspicious: {leaks}" if leaks else "")


def check_build(r: Report) -> None:
    script = ["cmd", "/c", str(ROOT / "ci.bat")] if IS_WINDOWS else ["bash", str(ROOT / "ci.sh")]
    if not r.add(Path(script[-1]).is_file(), f"build: {Path(script[-1]).name} exists"):
        return
    # Reuse the interpreter running /check: a bare `python` may be missing or a Store stub
    env = {**os.environ, "PYTHON": os.environ.get("PYTHON") or sys.executable}
    print(f"----- running {Path(script[-1]).name} (PYTHON={env['PYTHON']}) -----", flush=True)
    rc = subprocess.run(script, cwd=ROOT, env=env).returncode
    print(f"----- {Path(script[-1]).name} exit code {rc} -----", flush=True)
    if not r.add(rc == 0, "build: ci script succeeded", f"exit code {rc}"):
        return

    exe = ROOT / "build" / "bin" / ("hello.exe" if IS_WINDOWS else "hello")
    if r.add(exe.is_file(), f"build: executable {exe.relative_to(ROOT).as_posix()} exists"):
        out = subprocess.run([str(exe)], capture_output=True, text=True).stdout.strip()
        r.add(out == "Hello, World!", "build: executable prints greeting", repr(out))

    junit = ROOT / "build" / "test-results" / "junit.xml"
    if r.add(junit.is_file(), "build: junit report exists"):
        cases = ET.parse(junit).getroot().iter("testcase")
        basic = [c for c in cases if c.get("name") == "test_BasicAddition"]
        passed = bool(basic) and not any(len(list(c)) for c in basic)
        r.add(passed, "build: test BasicAddition passed")


def load_yaml(rel: str) -> object:
    code = "import json,sys,yaml; print(json.dumps(yaml.safe_load(open(sys.argv[1], encoding='utf-8')), default=str))"
    try:
        import yaml  # noqa: F401

        python = sys.executable
    except ImportError:
        python = str(venv_python())
        if not Path(python).is_file():
            raise RuntimeError("PyYAML not available: run ci script first (creates .venv)")
    out = subprocess.run([python, "-c", code, str(ROOT / rel)], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip().splitlines()[-1] if out.stderr else "yaml error")
    return json.loads(out.stdout)


def check_workflow(r: Report) -> None:
    rel = ".github/workflows/ci.yml"
    text = read(rel)
    if not r.add(text is not None, f"workflow: {rel} exists"):
        return
    try:
        data = load_yaml(rel)
    except RuntimeError as exc:
        r.add(False, "workflow: valid YAML", str(exc))
        return
    r.add(isinstance(data, dict), "workflow: valid YAML")
    if not isinstance(data, dict):
        return

    triggers = data.get("on", data.get("true")) or {}  # PyYAML parses `on` as True -> JSON "true"
    r.add(isinstance(triggers, dict) and {"push", "pull_request"} <= set(triggers), "workflow: triggers push + pull_request")
    if isinstance(triggers, dict):
        pr = (triggers.get("pull_request") or {}).get("branches", [])
        r.add(bool({"develop", "master"} & set(pr)), "workflow: pull_request targets develop/master", str(pr))

    jobs = data.get("jobs") or {}
    r.add(len(jobs) == 1, "workflow: single job", f"{list(jobs)}")
    job = next(iter(jobs.values()), {}) if jobs else {}
    matrix = set(((job.get("strategy") or {}).get("matrix") or {}).get("os") or [])
    r.add(OS_MATRIX <= matrix, "workflow: matrix ubuntu/windows/macos", str(sorted(matrix)))

    steps = job.get("steps") or []
    uses = " ".join(str(s.get("uses", "")) for s in steps)
    runs = [str(s.get("run", "")) for s in steps if "run" in s]
    r.add("actions/checkout" in uses, "workflow: checkout step")
    r.add(any("ci.sh" in x for x in runs) and any("ci.bat" in x for x in runs), "workflow: build via ci.sh / ci.bat")
    only_scripts = all(re.fullmatch(r"\s*(call\s+|bash\s+)?\.?/?ci\.(sh|bat)\s*", x) for x in runs)
    r.add(only_scripts, "workflow: run steps only call ci scripts", str(runs))
    r.add("continue-on-error" not in text, "workflow: errors are not suppressed")
    r.add("secrets." not in text, "workflow: no secrets referenced")


# --------------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", choices=GROUPS, action="append", help="run only these groups")
    parser.add_argument("--no-build", action="store_true", help="skip the (slow) build group")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Ukrainian text on Windows consoles

    groups = args.only or [g for g in GROUPS if not (args.no_build and g == "build")]
    status_before = git("status", "--porcelain")
    report = Report()
    for group in GROUPS:
        if group in groups:
            print(f"\n=== {group} ===", flush=True)
            globals()[f"check_{group}"](report)

    print("\n=== read-only guarantee ===")
    report.add(git("status", "--porcelain") == status_before, "check: tracked files unchanged by /check")

    total = len(report.results)
    if report.failed:
        print(f"\nRESULT: FAIL ({report.failed} of {total} checks failed)")
        return 1
    print(f"\nRESULT: PASS ({total} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
