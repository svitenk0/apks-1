# CLAUDE.md

Цей репозиторій — лабораторна робота №1 (варіант 2: Python, venv + скрипт запуску, pytest).
Роботу в ньому виконує агент **build-engineer**: перед будь-якою дією прочитай його manifest
`.claude/agents/build-engineer.md` і дотримуйся описаних там правил, заборонених дій і критеріїв завершення.

- Skills: `.claude/skills/<name>/SKILL.md`
- Commands: `.claude/commands/<name>.md` (викликаються як `/<name>`)
- Оркестратор: `/init`; перевірка: `/check`
- Журнал взаємодії з AI: `docs/ai-log.md` — доповнюй його після кожної команди.
