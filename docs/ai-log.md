# Журнал взаємодії з AI

- **AI-інструмент:** Claude Code (модель Claude Opus 5.5), агент `build-engineer`
- **Дата:** 2026-11-02
- **Студент:** Світенко Павло Ігорович, КІ-408, варіант 20 → 2 (Python, venv, pytest)

Формат: запит → важлива відповідь/дія AI → помилки → прийняте рішення.

---

## 1. Аналіз завдання
**Запит:** «вивчи task1.pdf з папки загрузок»

**Відповідь AI:** прочитав методичку (9 сторінок) і стисло описав мету, варіанти, вимоги до
репозиторію (гілки `develop` / `feature/...`, PR `lab1/finish`), склад агента (manifest, 3 skills,
5+ commands, orchestrator `init`), вимоги до CI (матриця 3 ОС, `ci.yml` лише викликає `ci.sh`/`ci.bat`).
Звернув увагу, що методичка описує формат GitHub Copilot, а для Claude Code каталоги інші.

## 2. Постановка задачі
**Запит:** «в мене 20 варіант, отже це 2 варіант (python), твоя задача — зробити все те, що написано
в pdf файлі, крім створення звіту і розділу 0 (GitHub Copilot Student); замість GitHub Copilot будеш ти».

**Рішення:**
- Мова/збірка/тести: Python 3.12, `venv` + `ci.sh`/`ci.bat`/`run.sh`/`run.bat`, `pytest`.
- Формат агента — Claude Code: `.claude/agents`, `.claude/skills`, `.claude/commands`. Відповідність
  структурі методички наведена в `docs/architecture.md`, розділ 2.
- «Виконуваний файл `hello`» для Python — збірка PyInstaller `--onefile` у `build/bin/hello[.exe]`.
  Каталог `build/` ігнорується Git, як вимагає методичка.
- Тест `BasicAddition` → `tests/test_hello.py::test_BasicAddition`.
- Логіку перевірок `/check` винесено в детермінований скрипт `.claude/scripts/check.py`.
  Так результат перевірки не залежить від «думки» моделі.

## 3. Підготовка середовища
| Помилка | Причина | Рішення |
|---------|---------|---------|
| `Python was not found; run without arguments to install from the Microsoft Store` | Python не встановлено, у `PATH` лише заглушка Store | AI встановив Python 3.12.10 через `winget install Python.Python.3.12 --scope user` |
| `gh: command not found` | немає GitHub CLI (потрібен для PR) | встановлено `winget install GitHub.cli` (2.103.3) |
| `git config user.name` порожній | не налаштована ідентичність Git | AI запитав у студента ПІП, групу та git-ідентичність; встановлено локально (`git config user.name/user.email`) |

**Безпека:** у відповіді студента, крім імені та email, був рядок, схожий на пароль. AI його **не
використав і не зберіг** ні в конфігурації, ні в репозиторії, і порадив студенту змінити пароль
(правило 4.3 методички: секрети не передаються AI).

## 4. Створення агента (гілка `develop`)
Згенеровано та закомічено трьома комітами:
1. `agent: add build-engineer manifest, README and architecture` — `CLAUDE.md`,
   `.claude/agents/build-engineer.md`, `README.md`, `docs/architecture.md`, мінімальний `.gitignore`.
2. `agent: add project-scaffold, build-and-test and github-actions skills`.
3. `agent: add commands, init orchestrator and check script`.

**Перевірка:** `python .claude/scripts/check.py --only agent` → `RESULT: PASS (23 checks)`.

## 5. Запуск оркестратора `/init` (гілка `feature/lab1-python-hello`)
| Крок | Результат |
|------|-----------|
| 1 `/git-init` | репозиторій валідний; `.gitattributes` — SKIP; `.gitignore` доповнено відсутніми рядками (`__pycache__/` і `.claude/settings.local.json` не дублювались); `git check-ignore build/ .venv/` → IGNORED |
| 2 `/create-project` | CREATE `src/hello/{__init__,core,__main__}.py`, `tests/`; README + розділ «Запуск проєкту»; `python -m hello` → `Hello, World!` |
| 3 `/create-build` | CREATE `pyproject.toml`, `requirements-dev.txt`, `calc.py`, `tests/test_hello.py`, `ci.*`, `run.*`; `ci.bat` → 6 passed, `build\bin\hello.exe` → `Hello, World!`, `CI: SUCCESS`; `ci.sh` (Git Bash) → `CI: SUCCESS`; `run.bat` → `Hello, World!` |
| 4 `/create-actions` | CREATE `.github/workflows/ci.yml`; `check.py --only workflow` → `RESULT: PASS (12 checks)` |
| 5 `/check` | **FAIL** (див. помилки 5.4, 5.5) → виправлено інструкції → повторний запуск (див. розділ 6) |

### Помилки під час `/init` та їх виправлення
**5.1. `ci.bat` з LF-закінченнями рядків.** Інструмент запису файлів створив `.bat` з LF;
`cmd.exe` з LF-файлами нестабільно обробляє мітки `goto`.
*Рішення:* файли конвертовано в CRLF. У репозиторії це закріплює `.gitattributes`
(`*.bat text eol=crlf`, `*.sh text eol=lf`), тож при checkout на будь-якій ОС закінчення правильні.

**5.2. `'ci.bat' is not recognized` при запуску з Git Bash через `cmd //c`.** Проблема інструмента
запуску, а не проєкту. *Рішення:* `.bat` запускаються з PowerShell за повним шляхом.

**5.3. Навмисно зламаний тест (перевірка, що помилки не маскуються).** `add()` змінено на
`a + b + 1`:
```
tests/test_hello.py::test_BasicAddition FAILED   assert 6 == 5
========================= 4 failed, 2 passed in 0.14s =========================
CI: FAILED
ci.bat (broken add) exit=1
```
Функцію повернуто. PowerShell 5.1 `Set-Content -Encoding utf8` додав BOM у `calc.py`, тож файл
перезаписано чистим UTF-8 за шаблоном skill.

**5.4. `/check`: `[FAIL] structure: required project files — missing ['docs/usage.md']`.**
*Причина — помилка в інструкції оркестратора:* `init.md` створював `docs/usage.md` **після** кроку
`/check`, а `/check` вимагає цей файл.
*Рішення (через AI, в інструкціях, а не в результаті):* у `.claude/commands/init.md` додано крок
**4a** (документація) **перед** `/check`.

**5.5. `/check`: `[FAIL] build: ci script succeeded — exit code 1`** з виводом
`Python was not found; ... Microsoft Store`.
*Причина:* `check.py` запускав `ci.bat` без змінної `PYTHON`, і `ci.bat` брав `python` з `PATH`,
тобто заглушку Store. Під час ручного запуску `PYTHON` задавали явно, тому проблема не проявлялась.
*Рішення:* `check.py` передає скриптам свій інтерпретатор (`PYTHON=sys.executable`, якщо змінна не
задана). У skill `build-and-test` додано рядок у таблицю типових помилок.

Обидва виправлення агента (5.4, 5.5) закомічено також у `develop`, щоб запуск агента з `develop`
відтворював цей результат.

## 6. Повторний `/check` після виправлень
Запуск без явного `PYTHON`, тобто в тих самих умовах, де раніше була помилка 5.5:
```
----- running ci.bat (PYTHON=C:\Users\svite\AppData\Local\Programs\Python\Python312\python.exe) -----
tests/test_hello.py::test_BasicAddition PASSED
CI: SUCCESS
----- ci.bat exit code 0 -----
[PASS] build: ci script succeeded — exit code 0
[PASS] build: executable build/bin/hello.exe exists
[PASS] build: executable prints greeting — 'Hello, World!'
[PASS] build: test BasicAddition passed
[PASS] check: tracked files unchanged by /check
RESULT: PASS (46 checks)
```
```
INIT OK: git-init ✓ create-project ✓ create-build ✓ create-actions ✓ check ✓ (RESULT: PASS)
```
