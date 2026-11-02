---
description: Create build configuration, test function, unit tests and ci/run scripts via the build-and-test skill, then run the local build
argument-hint: "[config|tests|scripts]  (default: all sub-steps)"
---

# Command: /create-build

Дій як агент **build-engineer**. Аргументи: `$ARGUMENTS` — підкрок skill
(`config`, `tests`, `scripts`); порожньо → усі три по черзі.

## Передумови
- Існує `src/hello/__main__.py` (результат `/create-project`). Інакше — помилка.
- Доступний Python ≥ 3.10 (`python --version` / `python3 --version`).

## Дії
1. Прочитай і застосуй skill `.claude/skills/build-and-test/SKILL.md` для вибраних підкроків.
2. Для кожного файлу: `CREATE` / `SKIP` / (diff + запит користувачу) — без перезапису.
   У `pyproject.toml` і `requirements-dev.txt` не дублюй секції та залежності.
3. Для нових `*.sh` після `git add` виконай `git update-index --chmod=+x <file>`.
4. Запусти локальну збірку: `ci.bat` на Windows, `./ci.sh` на Linux/macOS.
5. Додай запис у `docs/ai-log.md`: створені файли, результат `ci.*`, помилки та рішення.

## Очікувані файли
`pyproject.toml`, `requirements-dev.txt`, `src/hello/calc.py`, `tests/test_hello.py`,
`ci.sh`, `ci.bat`, `run.sh`, `run.bat`.
Після збірки (не в Git): `.venv/`, `build/bin/hello[.exe]`, `build/test-results/junit.xml`.

## Перевірка
```bash
./ci.sh   # або ci.bat → останній рядок "CI: SUCCESS", exit code 0
# у виводі pytest: tests/test_hello.py::test_BasicAddition PASSED
build/bin/hello   # → Hello, World!
```

## Повідомлення про помилку
- `ERROR [create-build]: src/hello/__main__.py not found — run /create-project first`
- `ERROR [create-build]: ci script failed at step <N>/5 (exit code <rc>)` + останні рядки логу.
  Оркестратор зупиняється; виправлення — через skill `build-and-test`, а не ручну правку результату.

## Повторний запуск
Безпечний: файли не перезаписуються; `ci.*` перестворюють лише ігноровані `.venv/` і `build/`.
