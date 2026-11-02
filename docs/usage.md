# Інструкція з використання

## 1. Передумови
| Інструмент | Версія | Перевірка |
|------------|--------|-----------|
| Git        | будь-яка сучасна | `git --version` |
| Python     | ≥ 3.10 (перевірено 3.12.10) | `python --version` / `python3 --version` |
| Claude Code | остання | `claude --version` (потрібен лише для запуску агента) |

> **Windows:** якщо `python` відкриває Microsoft Store, вимкніть псевдонім у
> *Settings → Apps → Advanced app settings → App execution aliases* або вкажіть інтерпретатор явно:
> `set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe`.

## 2. Запуск AI-агента (відтворення гілки feature з develop)
```bash
git clone https://github.com/svitenk0/apks-1.git
cd apks-1
git switch develop
git switch -c feature/lab1-python-hello
claude
```
Команди в сесії Claude Code:

| Команда | Дія |
|---------|-----|
| `/init` | оркестратор: `/git-init` → `/create-project` → `/create-build` → `/create-actions` → документація → `/check` |
| `/git-init` | перевірка репозиторію, доповнення `.gitignore` |
| `/create-project` | каркас `src/hello` (skill `project-scaffold`) |
| `/create-build` | `pyproject.toml`, тести, `ci.*`, `run.*` + локальна збірка (skill `build-and-test`) |
| `/create-build tests` | лише підкрок skill (`config` / `tests` / `scripts`) |
| `/create-actions` | `.github/workflows/ci.yml` (skill `github-actions`) |
| `/check` | лише перевірка, нічого не змінює |

Агента можна викликати й явно як субагента: «use the build-engineer agent to run /init».

## 3. Локальна перевірка (без AI)
```bash
# повна перевірка: агент, структура, git, збірка, workflow
python  .claude/scripts/check.py             # Windows
python3 .claude/scripts/check.py             # Linux/macOS

python .claude/scripts/check.py --no-build           # швидко, без збірки
python .claude/scripts/check.py --only workflow      # лише одна група
```
Успіх — останній рядок `RESULT: PASS (N checks)` і код виходу `0`.

## 4. Збірка і тести
| ОС | Команда | Результат |
|----|---------|-----------|
| Windows (cmd/PowerShell) | `ci.bat` | `build\bin\hello.exe`, `build\test-results\junit.xml` |
| Linux / macOS | `./ci.sh` | `build/bin/hello`, `build/test-results/junit.xml` |

Скрипт виконує 5 кроків: перевірка Python → venv `.venv` + залежності з `requirements-dev.txt` →
`pytest` → збірка виконуваного файлу PyInstaller → smoke-тест (вивід `Hello, World!`).
Останній рядок при успіху — `CI: SUCCESS`, при помилці — `CI: FAILED` і код виходу 1.

Окремі операції після першого запуску `ci.*` (venv уже існує):
```bash
.venv/bin/python -m pytest                     # усі тести (Windows: .venv\Scripts\python -m pytest)
.venv/bin/python -m pytest -k BasicAddition    # лише тест BasicAddition
```

## 5. Запуск застосунку
```bash
./run.sh            # з вихідного коду у venv (Linux/macOS)
run.bat             # з вихідного коду у venv (Windows)
build/bin/hello     # зібраний виконуваний файл (Windows: build\bin\hello.exe)
```
Очікуваний вивід: `Hello, World!`

Готові виконувані файли для всіх ОС можна завантажити з GitHub Actions: вкладка **Actions** →
запуск workflow **CI** → артефакти `hello-ubuntu-latest`, `hello-windows-latest`, `hello-macos-latest`.

## 6. Демонстрація реакції на зламану перевірку
```bash
# 1. навмисно зламати функцію
sed -i 's/return a + b/return a + b + 1/' src/hello/calc.py   # або змінити вручну
# 2. перевірка падає
python .claude/scripts/check.py --only build
#   tests/test_hello.py::test_BasicAddition FAILED ... assert 6 == 5
#   CI: FAILED
#   [FAIL] build: ci script succeeded — exit code 1
#   RESULT: FAIL
# 3. повернути
git checkout -- src/hello/calc.py
```
Аналогічно в GitHub Actions: push зі зламаним `add()` дає червоні jobs на всіх трьох ОС.

## 7. Що не потрапляє в Git
`.venv/`, `build/`, `dist/`, `*.spec`, `__pycache__/`, `.pytest_cache/`, `.env*`, ключі. Див. `.gitignore`;
`/check` (група `git`) перевіряє, що нічого з цього не відстежується.
