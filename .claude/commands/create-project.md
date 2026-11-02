---
description: Create the initial Hello World project via the project-scaffold skill
argument-hint: "[project_name=hello] [language=python]"
---

# Command: /create-project

Дій як агент **build-engineer**. Аргументи: `$ARGUMENTS` (порожньо → `project_name=hello language=python`).

## Передумови
- `/git-init` виконано успішно (існує `.gitignore`).
- `language` = `python` (варіант 2). Інша мова → помилка.

## Дії
1. Прочитай і застосуй skill `.claude/skills/project-scaffold/SKILL.md` з параметрами
   `language`, `project_name`.
2. Для кожного файлу: `CREATE`, якщо його немає; `SKIP`, якщо він уже відповідає шаблону;
   при відмінностях — не перезаписуй, покажи diff і запитай користувача.
3. Виконай перевірки зі skill.
4. Додай запис у `docs/ai-log.md` (створи файл, якщо його немає): що створено/пропущено, результат перевірки.

## Очікувані файли
`src/hello/__init__.py`, `src/hello/core.py`, `src/hello/__main__.py`, `tests/`,
оновлені `.gitignore` і `README.md` (розділ «Запуск проєкту»).

## Перевірка
```bash
cd src && python -m hello     # → Hello, World!
```

## Повідомлення про помилку
- `ERROR [create-project]: language '<x>' is not supported, variant 2 requires python`
- `ERROR [create-project]: python -m hello printed '<out>', expected 'Hello, World!'`
- `ERROR [create-project]: <file> differs from template — waiting for user decision`

## Повторний запуск
Безпечний: існуючі файли не перезаписуються, розділ README і рядки `.gitignore` не дублюються.
