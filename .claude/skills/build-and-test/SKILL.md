---
name: build-and-test
description: Set up the build and test system for the Python Hello World project — pyproject.toml, dev requirements, venv-based ci.sh/ci.bat and run.sh/run.bat scripts, the test function add() and the pytest unit test BasicAddition, PyInstaller build of the `hello` executable. Use after project-scaffold or when /create-build is invoked.
---

# Skill: build-and-test

## Коли застосовувати
- Каркас (`src/hello/`) уже існує, але немає `pyproject.toml`, тестів чи скриптів збірки;
- користувач викликав `/create-build` (чи `/init`);
- `/check` повідомив про відсутність або несправність збірки/тестів.

Skill поділено на три підкроки, які можна виконувати окремо:
`build-and-test:config` → `build-and-test:tests` → `build-and-test:scripts`.

## Вхідні дані
| Параметр         | За замовчуванням | Опис |
|------------------|------------------|------|
| `project_name`   | `hello`          | ім'я пакета з `src/` (має вже існувати) |
| `python_version` | `>=3.10`         | мінімальна версія Python |
| вхідні файли     | `src/hello/__main__.py`, `src/hello/core.py` | результат skill `project-scaffold` |

## Результат (створювані файли)
| Підкрок   | Файл                    | Призначення |
|-----------|-------------------------|-------------|
| `config`  | `pyproject.toml`        | метадані проєкту, налаштування pytest (`pythonpath = src`) |
| `config`  | `requirements-dev.txt`  | закріплені версії `pytest`, `pyinstaller`, `pyyaml` |
| `tests`   | `src/hello/calc.py`     | тестова функція `add(a, b)` |
| `tests`   | `tests/test_hello.py`   | юніт-тести, зокрема **`test_BasicAddition`** |
| `scripts` | `ci.sh` / `ci.bat`      | venv → залежності → pytest → PyInstaller → smoke-тест |
| `scripts` | `run.sh` / `run.bat`    | запуск застосунку з вихідного коду у venv |
| (runtime) | `build/bin/hello[.exe]` | виконуваний файл (НЕ комітиться) |
| (runtime) | `build/test-results/junit.xml` | звіт тестів (НЕ комітиться) |

### Шаблон `pyproject.toml`
```toml
[project]
name = "hello"
version = "1.0.0"
description = "Cross-platform Hello World (lab 1, variant 2: Python + venv + pytest)"
requires-python = ">=3.10"

[project.scripts]
hello = "hello.__main__:main"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-v"
```

### Шаблон `requirements-dev.txt`
```text
pytest==8.3.5
pyinstaller==6.14.1
pyyaml==6.0.2
```

### Шаблон `src/hello/calc.py`
```python
"""Arithmetic helper used to demonstrate unit testing."""


def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b
```

### Шаблон `tests/test_hello.py`
```python
"""Unit tests for the Hello World application (pytest)."""

import pytest

from hello.__main__ import main
from hello.calc import add
from hello.core import greet


def test_BasicAddition():
    """BasicAddition: the test function `add` sums two numbers."""
    assert add(2, 3) == 5


@pytest.mark.parametrize(("a", "b", "expected"), [(0, 0, 0), (-1, 1, 0), (2.5, 0.5, 3.0)])
def test_AdditionCases(a, b, expected):
    assert add(a, b) == expected


def test_Greeting():
    assert greet() == "Hello, World!"


def test_MainPrintsGreeting(capsys):
    assert main() == 0
    assert capsys.readouterr().out == "Hello, World!\n"
```

### Шаблон `ci.sh` (Linux/macOS; LF; біт виконання `git update-index --chmod=+x ci.sh`)
```bash
#!/usr/bin/env bash
# Build & test pipeline for Linux/macOS: venv -> deps -> pytest -> PyInstaller -> smoke test.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV="$ROOT/.venv"
BUILD="$ROOT/build"

echo "==> [1/5] $("$PYTHON" --version)"

echo "==> [2/5] Creating virtual environment in .venv and installing dependencies"
"$PYTHON" -m venv "$VENV"
if [ -f "$VENV/Scripts/python.exe" ]; then   # Git Bash on Windows
  VPY="$VENV/Scripts/python.exe"; EXE="$BUILD/bin/hello.exe"
else
  VPY="$VENV/bin/python"; EXE="$BUILD/bin/hello"
fi
"$VPY" -m pip install --disable-pip-version-check -q -r requirements-dev.txt

echo "==> [3/5] Running unit tests (pytest)"
mkdir -p "$BUILD/test-results"
"$VPY" -m pytest --junitxml="$BUILD/test-results/junit.xml"

echo "==> [4/5] Building executable build/bin/hello (PyInstaller)"
"$VPY" -m PyInstaller --noconfirm --clean --log-level WARN --onefile --name hello \
  --paths "$ROOT/src" --distpath "$BUILD/bin" --workpath "$BUILD/work" --specpath "$BUILD" \
  "$ROOT/src/hello/__main__.py"

echo "==> [5/5] Smoke test of the executable"
OUTPUT="$("$EXE" | tr -d '\r')"
echo "$OUTPUT"
if [ "$OUTPUT" != "Hello, World!" ]; then
  echo "ERROR: unexpected output from $EXE" >&2
  exit 1
fi

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  echo "### $(uname -s): tests passed, executable \`build/bin/$(basename "$EXE")\` built and prints \`$OUTPUT\`" >> "$GITHUB_STEP_SUMMARY"
fi
echo "CI: SUCCESS"
```

### Шаблон `ci.bat` (Windows; CRLF)
```bat
@echo off
rem Build & test pipeline for Windows: venv -> deps -> pytest -> PyInstaller -> smoke test.
setlocal EnableExtensions
cd /d "%~dp0"

if "%PYTHON%"=="" set "PYTHON=python"
set "ROOT=%CD%"
set "VENV=%ROOT%\.venv"
set "BUILD=%ROOT%\build"
set "VPY=%VENV%\Scripts\python.exe"
set "EXE=%BUILD%\bin\hello.exe"

echo ==^> [1/5] Python version:
"%PYTHON%" --version || goto :fail

echo ==^> [2/5] Creating virtual environment in .venv and installing dependencies
"%PYTHON%" -m venv "%VENV%" || goto :fail
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements-dev.txt || goto :fail

echo ==^> [3/5] Running unit tests (pytest)
if not exist "%BUILD%\test-results" mkdir "%BUILD%\test-results"
"%VPY%" -m pytest --junitxml="%BUILD%\test-results\junit.xml" || goto :fail

echo ==^> [4/5] Building executable build\bin\hello.exe (PyInstaller)
"%VPY%" -m PyInstaller --noconfirm --clean --log-level WARN --onefile --name hello --paths "%ROOT%\src" --distpath "%BUILD%\bin" --workpath "%BUILD%\work" --specpath "%BUILD%" "%ROOT%\src\hello\__main__.py" || goto :fail

echo ==^> [5/5] Smoke test of the executable
set "OUTPUT="
for /f "delims=" %%L in ('"%EXE%"') do set "OUTPUT=%%L"
echo %OUTPUT%
if not "%OUTPUT%"=="Hello, World!" (
  echo ERROR: unexpected output from build\bin\hello.exe 1>&2
  goto :fail
)

if defined GITHUB_STEP_SUMMARY echo ### Windows: tests passed, executable `build\bin\hello.exe` built and prints `%OUTPUT%`>>"%GITHUB_STEP_SUMMARY%"
echo CI: SUCCESS
exit /b 0

:fail
echo CI: FAILED 1>&2
exit /b 1
```

### Шаблон `run.sh`
```bash
#!/usr/bin/env bash
# Launch Hello World from source inside the project's virtual environment.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"

if [ ! -d "$ROOT/.venv" ]; then
  "$PYTHON" -m venv "$ROOT/.venv"
fi
if [ -f "$ROOT/.venv/Scripts/python.exe" ]; then
  VPY="$ROOT/.venv/Scripts/python.exe"
else
  VPY="$ROOT/.venv/bin/python"
fi

cd "$ROOT/src"
exec "$VPY" -m hello "$@"
```

### Шаблон `run.bat`
```bat
@echo off
rem Launch Hello World from source inside the project's virtual environment.
setlocal
cd /d "%~dp0"
if "%PYTHON%"=="" set "PYTHON=python"
if not exist ".venv\Scripts\python.exe" (
  "%PYTHON%" -m venv .venv || exit /b 1
)
cd src
"..\.venv\Scripts\python.exe" -m hello %*
```

## Порядок дій
1. Переконайся, що існує `src/hello/__main__.py` (інакше — зупинка, спершу `/create-project`).
2. `config`: створи `pyproject.toml`, `requirements-dev.txt` (якщо вже є — не дублюй секцію
   `[tool.pytest.ini_options]` і рядки залежностей).
3. `tests`: створи `src/hello/calc.py`, `tests/test_hello.py`.
4. `scripts`: створи `ci.sh`, `ci.bat`, `run.sh`, `run.bat`; для `*.sh` виконай
   `git update-index --add --chmod=+x <file>` після першого `git add`.
5. Запусти `ci.sh` (Linux/macOS) або `ci.bat` (Windows) і виконай перевірки.

## Перевірки
```bash
./ci.sh            # або ci.bat; останній рядок — "CI: SUCCESS", код виходу 0
.venv/bin/python -m pytest -k BasicAddition       # 1 passed
build/bin/hello    # → Hello, World!   (Windows: build\bin\hello.exe)
git check-ignore -q build/bin/hello               # виконуваний файл ігнорується
```

## Приклад
**Вхід:** `project_name=hello`, існує каркас від `project-scaffold`.
**Очікуваний результат (фрагмент виводу `ci.bat`):**
```
==> [3/5] Running unit tests (pytest)
tests/test_hello.py::test_BasicAddition PASSED
...
6 passed
==> [4/5] Building executable build\bin\hello.exe (PyInstaller)
==> [5/5] Smoke test of the executable
Hello, World!
CI: SUCCESS
```

## Типовий сценарій помилки
| Симптом | Причина | Дія |
|---------|---------|-----|
| `test_BasicAddition FAILED: assert 6 == 5` | помилка в `add()` | виправити `calc.py`, не змінювати очікування тесту |
| `Python was not found; run without arguments to install from the Microsoft Store` | у `PATH` лише заглушка Windows Store | задати інтерпретатор явно: `set PYTHON=C:\...\python.exe` / `PYTHON=/path/python3 ./ci.sh` (`/check` робить це автоматично) |
| `ModuleNotFoundError: hello` у pytest | нема `pythonpath = ["src"]` у `pyproject.toml` | додати ключ (без дублювання секції) |
| `./ci.sh: Permission denied` | нема біта виконання | `git update-index --chmod=+x ci.sh` або запуск `bash ci.sh` |
| `/usr/bin/env: 'bash\r'` | CRLF у `ci.sh` | перевірити `.gitattributes` (`*.sh eol=lf`) |
| `ERROR: No matching distribution found for pyinstaller==…` | версія не підтримує поточний Python | оновити версію в `requirements-dev.txt`, записати рішення в `docs/ai-log.md` |
| Скрипт завершився з кодом ≠ 0 | будь-який крок упав | **зупинка**; не додавати `|| true`, показати лог |
