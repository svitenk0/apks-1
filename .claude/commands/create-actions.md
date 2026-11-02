---
description: Create the GitHub Actions CI workflow (Windows/Linux/macOS matrix) via the github-actions skill
---

# Command: /create-actions

Дій як агент **build-engineer**.

## Передумови
- Існують `ci.sh` і `ci.bat` (результат `/create-build`), і локальна збірка проходила.

## Дії
1. Прочитай і застосуй skill `.claude/skills/github-actions/SKILL.md`.
2. `CREATE .github/workflows/ci.yml`, якщо його немає; `SKIP`, якщо збігається з шаблоном;
   при відмінностях — diff і запит користувачу. Другий workflow-файл не створювати.
3. Перевір YAML і структуру (див. «Перевірка»).
4. **Не** виконуй `git push` автоматично — лише підкажи користувачу команду.
5. Додай запис у `docs/ai-log.md`.

## Очікувані файли
`.github/workflows/ci.yml`

## Перевірка
```bash
python .claude/scripts/check.py --only workflow
```
Очікувано: `[PASS] workflow: ...` для YAML, тригерів, матриці з 3 ОС, виклику `ci.sh`/`ci.bat`,
відсутності `continue-on-error` і секретів.

## Повідомлення про помилку
- `ERROR [create-actions]: ci.sh/ci.bat not found — run /create-build first`
- `ERROR [create-actions]: workflow check failed: <details>`

## Повторний запуск
Безпечний: існуючий `ci.yml` не перезаписується і не дублюється.
