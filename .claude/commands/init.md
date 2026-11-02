---
description: Orchestrator — run git-init, create-project, create-build, create-actions and check in order, stopping on the first error
argument-hint: "[project_name=hello]"
---

# Command: /init (orchestrator)

Дій як агент **build-engineer** (`.claude/agents/build-engineer.md`). Аргументи: `$ARGUMENTS`.

## Передумови
- Встановлені `git` і Python ≥ 3.10.
- Поточна гілка — не `main`/`master`/`develop`. Якщо так — запропонуй користувачу створити
  `feature/<name>` (`git switch -c feature/lab1-python-hello`) і дочекайся згоди.
- Робоче дерево чисте або користувач підтвердив продовження з незакоміченими змінами.

## Дії
Виконуй кроки **строго по черзі**. Кожен крок — це відповідна command з `.claude/commands/`;
результат попереднього кроку є передумовою наступного.

| Крок | Command           | Вхід від попереднього кроку            | Вихід для наступного кроку |
|------|-------------------|----------------------------------------|----------------------------|
| 1    | `/git-init`       | —                                      | репозиторій, `.gitignore`  |
| 2    | `/create-project` | `.gitignore`, `project_name`           | `src/hello/`               |
| 3    | `/create-build`   | `src/hello/__main__.py`                | `ci.sh`, `ci.bat`, тести, `build/bin/hello` |
| 4    | `/create-actions` | `ci.sh`, `ci.bat`                      | `.github/workflows/ci.yml` |
| 5    | `/check`          | усе вище                               | `RESULT: PASS` / `FAIL`    |

Після кроків 2–4 (якщо команда створила або змінила файли) запропонуй окремий змістовний коміт:
- крок 1+2: `feat: scaffold Python Hello World project`
- крок 3: `build: add venv build scripts, pytest tests and PyInstaller packaging`
- крок 4: `ci: add GitHub Actions matrix for Windows, Linux and macOS`

Коміти виконуй лише локально; `git push` і створення PR — тільки на прохання користувача.

Наприкінці:
6. Створи `docs/usage.md`, якщо його немає: точні команди запуску агента (`/init`, `/check`, окремі
   commands), локальної збірки (`ci.sh`/`ci.bat`), запуску застосунку (`run.*`, `build/bin/hello`).
7. Допиши `docs/ai-log.md`: запуск оркестратора, результат кожного кроку, помилки та рішення.
8. Виведи підсумковий звіт.

## Обробка помилок
- Якщо крок завершився помилкою — **зупинись**. Не виконуй наступні кроки, не позначай роботу успішною.
- Виведи: номер і назву кроку, повідомлення про помилку команди, останні рядки логу, яку
  command/skill треба виправити.
- Не приховуй помилку (`|| true`, пропуск тестів, ручна правка згенерованого результату).
- Після виправлення інструкцій можна перезапустити `/init`: усі кроки ідемпотентні й пропускають
  вже готові файли.

## Очікувані файли
Усі файли з команд 1–4, а також `docs/usage.md` і `docs/ai-log.md`.

## Перевірка
Крок 5 (`/check`) повертає `RESULT: PASS`. Без цього `/init` вважається невдалим.

## Повідомлення про помилку
```
INIT FAILED at step <N>/5 (<command>): <message>
Fix: <skill/command to update>, then re-run /init
```
Успіх:
```
INIT OK: git-init ✓ create-project ✓ create-build ✓ create-actions ✓ check ✓ (RESULT: PASS)
```
