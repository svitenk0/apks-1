---
name: github-actions
description: Create .github/workflows/ci.yml — one job with an OS matrix (ubuntu, windows, macos) that checks out the repo, configures Python and only calls ci.sh / ci.bat to build and test, then uploads the executable and test report. Use after build-and-test or when /create-actions is invoked.
---

# Skill: github-actions

## Коли застосовувати
- Скрипти `ci.sh` і `ci.bat` уже існують і локально проходять;
- немає `.github/workflows/ci.yml` або він не відповідає вимогам;
- користувач викликав `/create-actions` (чи `/init`).

## Вхідні дані
| Параметр         | За замовчуванням | Опис |
|------------------|------------------|------|
| `os_matrix`      | `ubuntu-latest, windows-latest, macos-latest` | має містити всі три ОС |
| `python_version` | `3.12`           | версія для `actions/setup-python` |
| `branches`       | `develop, master, main` | цільові гілки push / pull_request |
| вхідні файли     | `ci.sh`, `ci.bat` | результат skill `build-and-test` |

## Результат
`.github/workflows/ci.yml`. **Вимога методички:** workflow не містить логіки збірки — лише
checkout, налаштування інтерпретатора (конфігурація), виклик `ci.sh` / `ci.bat` і публікацію
артефактів. Уся збірка, тести та генерація виконуваного файлу — у скриптах.

### Шаблон `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [develop, master, main, "feature/**"]
  pull_request:
    branches: [develop, master, main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build-and-test:
    name: build-and-test (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Build and test (Linux/macOS)
        if: runner.os != 'Windows'
        shell: bash
        run: bash ./ci.sh

      - name: Build and test (Windows)
        if: runner.os == 'Windows'
        shell: cmd
        run: call ci.bat

      - name: Upload executable
        uses: actions/upload-artifact@v4
        with:
          name: hello-${{ matrix.os }}
          path: build/bin/
          if-no-files-found: error

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}
          path: build/test-results/
          if-no-files-found: warn
```

Пояснення рішень:
- `fail-fast: false` — падіння на одній ОС не скасовує інші, видно повну картину.
- `permissions: contents: read` — мінімальні права токена; секрети не використовуються.
- `feature/**` у `push` — щоб результат був видимий і в гілці feature до створення PR.
- Звіт тестів вивантажується навіть при падінні (`if: always()`), виконуваний файл — лише при успіху.
- `ci.sh`/`ci.bat` самі пишуть короткий підсумок у `$GITHUB_STEP_SUMMARY` — «зрозумілий результат job».

## Порядок дій
1. Переконайся, що `ci.sh` і `ci.bat` існують (інакше — зупинка, спершу `/create-build`).
2. Якщо `ci.yml` не існує — створи за шаблоном. Якщо існує — порівняй; при відмінностях не
   перезаписуй, а покажи diff і запитай користувача. Не створюй другий workflow-файл.
3. Виконай перевірки.

## Перевірки
```bash
# валідний YAML (pyyaml є в .venv після ci.sh/ci.bat)
.venv/bin/python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
grep -E "ubuntu-latest|windows-latest|macos-latest" .github/workflows/ci.yml   # 3 збіги
grep -E "ci\.sh|ci\.bat" .github/workflows/ci.yml                              # обидва скрипти
grep -E "continue-on-error|secrets\." .github/workflows/ci.yml                 # 0 збігів
```
Повну перевірку структури виконує `/check` (розділ «workflow»). Після `git push` — переглянути
вкладку **Actions**: 3 зелені jobs і артефакти `hello-<os>`.

## Приклад
**Вхід:** `os_matrix` за замовчуванням, `ci.sh`/`ci.bat` проходять локально.
**Очікуваний результат:**
```
CREATE .github/workflows/ci.yml
CHECK  YAML valid                         OK
CHECK  triggers: push, pull_request       OK
CHECK  matrix: ubuntu, windows, macos     OK
CHECK  build steps call ci.sh / ci.bat    OK
```
У GitHub: `build-and-test (ubuntu-latest) ✓`, `build-and-test (windows-latest) ✓`,
`build-and-test (macos-latest) ✓`.

## Типовий сценарій помилки
| Симптом | Причина | Дія |
|---------|---------|-----|
| Workflow не запускається | гілку не вказано в `on.push.branches` / PR не в `develop` | додати гілку до тригерів |
| `./ci.sh: Permission denied` на Linux | нема біта виконання | запуск `bash ./ci.sh` (як у шаблоні) |
| Job на Windows «зелений», хоча тести впали | `ci.bat` не повертає код помилки | у `ci.bat` кожен крок має `|| goto :fail` і `exit /b 1` |
| `Unable to find any artifacts` | збірка не створила `build/bin/` | дивитися лог кроку `Build and test`; не вимикати `if-no-files-found: error` |
| YAML parse error | невірні відступи | виправити відступи (2 пробіли), повторити перевірку |
