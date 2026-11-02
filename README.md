# Лабораторна робота №1 — AI-агент для автоматизації розробки та CI/CD

| | |
|---|---|
| **Студент** | Світенко Павло Ігорович |
| **Група** | КІ-408 |
| **Варіант** | 20 → варіант 2: **Python**, `venv` + скрипт запуску, **pytest** |
| **AI-інструмент** | Claude Code (агент `build-engineer`) |

## Опис
Репозиторій містить AI-агента **build-engineer** для Claude Code. Агент складається з
manifest, трьох skills, шести commands і оркестратора `/init`. Він генерує, збирає,
тестує й підключає до GitHub Actions мінімальний кросплатформний застосунок **Hello World**
на Python. Застосунок пакується у виконуваний файл `hello` (PyInstaller) і тестується через `pytest`
на Windows, Linux і macOS.

- Гілка `develop` — лише агент та інструкції.
- Гілка `feature/lab1-python-hello` — результат запуску `/init`: код, тести, скрипти, CI, документація.

## Структура агента
```
CLAUDE.md                               # вхідна точка: підключає manifest агента
.claude/
├── agents/build-engineer.md            # agent manifest
├── skills/
│   ├── project-scaffold/SKILL.md       # створення проєкту
│   ├── build-and-test/SKILL.md         # складання і тестування
│   └── github-actions/SKILL.md         # GitHub Actions
├── commands/
│   ├── git-init.md                     # /git-init
│   ├── create-project.md               # /create-project
│   ├── create-build.md                 # /create-build
│   ├── create-actions.md               # /create-actions
│   ├── check.md                        # /check (лише перевірка)
│   └── init.md                         # /init — оркестратор
└── scripts/check.py                    # детермінована реалізація перевірок /check
docs/architecture.md                    # архітектура агента
```

## Запуск агента
Потрібні: [Claude Code](https://claude.com/claude-code), Git, Python ≥ 3.10.

```bash
git clone https://github.com/svitenk0/apks-1.git && cd apks-1
git switch develop
git switch -c feature/lab1-python-hello   # агент працює лише у feature-гілці
claude                                    # запустити Claude Code у корені репозиторію
```
У сесії Claude Code:
```
/init          # повний сценарій: git-init → create-project → create-build → create-actions → check
/check         # лише перевірка (нічого не змінює)
```
Окремі кроки: `/git-init`, `/create-project`, `/create-build [config|tests|scripts]`, `/create-actions`.

Перевірку можна запустити й без AI:
```bash
python .claude/scripts/check.py            # усі групи
python .claude/scripts/check.py --no-build # без збірки
```

Докладніше — у [docs/architecture.md](docs/architecture.md).

## Запуск проєкту

| ОС            | Запуск з вихідного коду | Збірка + тести + виконуваний файл |
|---------------|-------------------------|-----------------------------------|
| Linux / macOS | `./run.sh`              | `./ci.sh` → `build/bin/hello`     |
| Windows       | `run.bat`               | `ci.bat` → `build\bin\hello.exe`  |

Детальніше — у [docs/usage.md](docs/usage.md).
