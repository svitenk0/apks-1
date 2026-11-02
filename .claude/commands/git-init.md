---
description: Check the Git repository, create or update .gitignore without duplicates, show git status
---

# Command: /git-init

Дій як агент **build-engineer** (`.claude/agents/build-engineer.md`).

## Передумови
- Встановлено `git` (`git --version`).
- Поточний каталог — корінь репозиторію лабораторної (тут лежить `CLAUDE.md`).

## Дії
1. Виконай `git rev-parse --is-inside-work-tree`.
   - Якщо це не репозиторій — виконай `git init -b main` і повідом про це.
   - Ніколи не виконуй `git reset`, `git clean`, `git push`, не змінюй історію.
2. Покажи поточну гілку (`git branch --show-current`) і remotes (`git remote -v`).
3. Візьми список обов'язкових рядків `.gitignore` зі skill
   `.claude/skills/project-scaffold/SKILL.md` (розділ «Обов'язкові рядки `.gitignore`»).
   - Якщо `.gitignore` немає — створи його з цим списком.
   - Якщо є — додай **лише відсутні** рядки (порівняння по рядку, без дублікатів), не видаляй існуючі.
4. Переконайся, що `.gitattributes` містить `*.sh text eol=lf` і `*.bat text eol=crlf`; додай відсутнє.
5. Перевір, що в індексі немає вже відстежуваних тимчасових файлів:
   `git ls-files | grep -E '^(build|dist|\.venv)/|__pycache__'` — якщо є, **не видаляй**, а покажи
   список і запропонуй користувачу `git rm -r --cached <path>`.
6. Покажи `git status --short`.

## Очікувані файли
- `.gitignore` (містить `build/`, `dist/`, `.venv/`, `__pycache__/`, `.env`, …)
- `.gitattributes`

## Перевірка
```bash
git rev-parse --is-inside-work-tree        # true
git check-ignore -q build/ && git check-ignore -q .venv/ && echo IGNORED
sort .gitignore | uniq -d | grep -v '^$'   # порожньо = немає дублікатів
```

## Повідомлення про помилку
- `ERROR [git-init]: git is not installed or not in PATH` — встанови Git і повтори.
- `ERROR [git-init]: tracked build artifacts found: <list>` — оркестратор зупиняється, доки користувач
  не прибере їх з індексу.

## Повторний запуск
Безпечний: `.gitignore` і `.gitattributes` лише доповнюються відсутніми рядками; інакше — `SKIP`.
