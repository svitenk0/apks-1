---
description: Read-only verification of agent files, project structure, git hygiene, build, tests and the CI workflow
argument-hint: "[--no-build] [--only agent|structure|git|build|workflow]"
---

# Command: /check

Дій як агент **build-engineer**. Ця команда **нічого не змінює** у відстежуваних Git файлах.
Вона лише запускає збірку (яка пише в ігноровані `.venv/` і `build/`) та звітує.

## Передумови
- Доступний Python ≥ 3.10.

## Дії
1. Виконай скрипт перевірки (аргументи передай як є: `$ARGUMENTS`):
   ```bash
   python .claude/scripts/check.py $ARGUMENTS      # Windows
   python3 .claude/scripts/check.py $ARGUMENTS     # Linux/macOS
   ```
2. Скрипт перевіряє групи:
   | Група       | Що перевіряється |
   |-------------|------------------|
   | `agent`     | manifest має роль, заборонені дії, критерії завершення; 3 skills мають розділи «Коли застосовувати / Вхідні дані / Результат / Перевірки / Приклад / Типовий сценарій помилки»; 6 commands мають «Передумови / Дії / Очікувані файли / Перевірка / Повідомлення про помилку»; `/init` викликає команди в порядку `git-init → create-project → create-build → create-actions → check` |
   | `structure` | наявність файлів проєкту, `docs/usage.md`, `README.md` |
   | `git`       | `.gitignore` містить `build/`, `.venv/`…; у Git немає `build/`, `dist/`, `.venv/`, `__pycache__`; немає схожих на секрети рядків у відстежуваних файлах |
   | `build`     | запуск `ci.bat`/`ci.sh`, код виходу 0, існує `build/bin/hello[.exe]` і друкує `Hello, World!`, у `junit.xml` тест `test_BasicAddition` пройшов |
   | `workflow`  | `ci.yml` — валідний YAML, тригери `push` + `pull_request`, матриця з 3 ОС, кроки викликають `ci.sh` і `ci.bat`, немає `continue-on-error` і `secrets.` |
   Наприкінці скрипт порівнює `git status --porcelain` до і після — доказ, що check нічого не змінив.
3. Покажи користувачу підсумкову таблицю `[PASS]/[FAIL]` і рядок `RESULT: PASS|FAIL`.
4. **Не виправляй** нічого в цій команді. Для кожного `[FAIL]` назви command/skill, який треба
   перезапустити.

## Очікувані файли
Нових відстежуваних файлів немає. Побічні (ігноровані): `.venv/`, `build/`.

## Перевірка
Код виходу скрипта: `0` — усе пройшло, `1` — є хоча б один `[FAIL]`.

## Повідомлення про помилку
- `[FAIL] <group>: <check> — <details>` для кожної проблеми.
- `RESULT: FAIL (<n> failed)` і код виходу 1.

## Повторний запуск
Завжди безпечний.
