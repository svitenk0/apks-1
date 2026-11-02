---
name: project-scaffold
description: Create the minimal cross-platform Python "Hello World" project — directory layout, package with greet() and entry point, README run section and baseline .gitignore. Use when the repository has no src/ project yet or /create-project is invoked.
---

# Skill: project-scaffold

## Коли застосовувати
- У репозиторії ще немає `src/<project_name>/`, або
- користувач викликав `/create-project` (чи `/init`), або
- `/check` повідомив, що бракує файлів каркаса.

Не застосовувати для створення системи збірки, тестів або CI — це skills
`build-and-test` і `github-actions`.

## Вхідні дані
| Параметр       | Обов'язковий | За замовчуванням | Опис                               |
|----------------|--------------|------------------|------------------------------------|
| `language`     | так          | `python`         | мова варіанту; для цього skill — лише `python` |
| `project_name` | так          | `hello`          | ім'я пакета і виконуваного файлу (`[a-z_][a-z0-9_]*`) |

Якщо `language` ≠ `python` або `project_name` не відповідає шаблону — зупинись з помилкою
(див. «Типовий сценарій помилки»).

## Результат (створювані файли)
| Файл                                | Призначення                         |
|-------------------------------------|-------------------------------------|
| `src/<project_name>/__init__.py`    | пакет, версія                       |
| `src/<project_name>/core.py`        | функція `greet()` → `"Hello, World!"` |
| `src/<project_name>/__main__.py`    | точка входу `main()`, друкує привітання |
| `tests/` (каталог)                  | місце для тестів (заповнює `build-and-test`) |
| `.gitignore`                        | гарантує наявність усіх рядків зі списку нижче |
| `README.md`                         | розділ `## Запуск проєкту` (додається, якщо його нема) |

### Шаблон `src/hello/__init__.py`
```python
"""Cross-platform Hello World package (lab 1, variant 2)."""

__version__ = "1.0.0"
```

### Шаблон `src/hello/core.py`
```python
"""Core logic of the Hello World application."""

GREETING = "Hello, World!"


def greet() -> str:
    """Return the greeting printed by the application."""
    return GREETING
```

### Шаблон `src/hello/__main__.py`
Імпорт абсолютний (`from hello.core ...`), бо цей файл також є точкою входу PyInstaller.
```python
"""Entry point: `python -m hello` and the PyInstaller executable `hello`."""

import sys

from hello.core import greet


def main() -> int:
    """Print the greeting and return the process exit code."""
    print(greet())
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Обов'язкові рядки `.gitignore`
Додавай лише ті рядки, яких ще немає (порівняння по рядку без пробілів на краях):
```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
.pytest_cache/

# Build output
build/
dist/
*.spec

# Test / coverage reports
.coverage
htmlcov/

# Secrets and local environment
.env
.env.*
*.pem
*.key

# IDE / OS
.idea/
.vscode/
.DS_Store
Thumbs.db

# Claude Code local settings
.claude/settings.local.json
```

### Розділ README
Додай у кінець `README.md`, якщо заголовка `## Запуск проєкту` ще немає:
```markdown
## Запуск проєкту

| ОС            | Запуск з вихідного коду | Збірка + тести + виконуваний файл |
|---------------|-------------------------|-----------------------------------|
| Linux / macOS | `./run.sh`              | `./ci.sh` → `build/bin/hello`     |
| Windows       | `run.bat`               | `ci.bat` → `build\bin\hello.exe`  |

Детальніше — у [docs/usage.md](docs/usage.md).
```

## Порядок дій
1. Перевір вхідні параметри.
2. Створи каталоги `src/<project_name>/` і `tests/`.
3. Для кожного файлу з таблиці: якщо не існує — створи за шаблоном; якщо існує й збігається —
   `SKIP`; якщо відрізняється — не перезаписуй, покажи різницю та запитай користувача.
4. Доповни `.gitignore` відсутніми рядками.
5. Доповни `README.md` розділом запуску (якщо його нема).
6. Виконай перевірки.

## Перевірки
```bash
test -f src/hello/__main__.py && test -f src/hello/core.py && test -f src/hello/__init__.py
# команда запуску працює і друкує привітання
PYTHONPATH=src python -m hello          # Linux/macOS → Hello, World!
set PYTHONPATH=src && python -m hello   # Windows cmd  → Hello, World!
git check-ignore -q build/ .venv/       # обидва шляхи ігноруються
```
Успіх: усі файли існують, вивід рівно `Hello, World!`, код виходу 0.

## Приклад
**Вхід:** `language=python`, `project_name=hello`, порожній репозиторій з `README.md`.
**Очікуваний результат:**
```
CREATE src/hello/__init__.py
CREATE src/hello/core.py
CREATE src/hello/__main__.py
CREATE tests/
UPDATE .gitignore (+24 lines)
UPDATE README.md (+section "Запуск проєкту")
CHECK  python -m hello -> "Hello, World!"  OK
```
**Повторний запуск** того самого кроку: усі рядки `SKIP`, `.gitignore` не змінюється.

## Типовий сценарій помилки
| Симптом | Причина | Дія |
|---------|---------|-----|
| `ModuleNotFoundError: No module named 'hello'` | не задано `PYTHONPATH=src` | запускати з `PYTHONPATH=src` або через `run.sh`/`run.bat` |
| `ImportError: attempted relative import with no known parent package` у збірці | у `__main__.py` використано `from .core import greet` | використовувати абсолютний імпорт, як у шаблоні |
| `language=java` | невідповідність варіанту | зупинитись: `ERROR: project-scaffold supports only language=python (variant 2)` |
| `python` не знайдено | Python не встановлений / не в `PATH` | зупинитись і попросити встановити Python ≥ 3.10 |
