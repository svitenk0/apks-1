@echo off
rem Build & test pipeline for Windows: venv -> deps -> pytest -> PyInstaller -> smoke test.
setlocal EnableExtensions
cd /d "%~dp0"

if "%PYTHON%"=="" set "PYTHON=python"
set "ROOT=%CD%"
set "VENV=%ROOT%\.venv"
set "BUILD=%ROOT%\build"
set "VPY=%VENV%\Scripts\python.exe"
set "EXE=%BUILD%\bin\hello.exe"

echo ==^> [1/5] Python version:
"%PYTHON%" --version || goto :fail

echo ==^> [2/5] Creating virtual environment in .venv and installing dependencies
"%PYTHON%" -m venv "%VENV%" || goto :fail
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements-dev.txt || goto :fail

echo ==^> [3/5] Running unit tests (pytest)
if not exist "%BUILD%\test-results" mkdir "%BUILD%\test-results"
"%VPY%" -m pytest --junitxml="%BUILD%\test-results\junit.xml" || goto :fail

echo ==^> [4/5] Building executable build\bin\hello.exe (PyInstaller)
"%VPY%" -m PyInstaller --noconfirm --clean --log-level WARN --onefile --name hello --paths "%ROOT%\src" --distpath "%BUILD%\bin" --workpath "%BUILD%\work" --specpath "%BUILD%" "%ROOT%\src\hello\__main__.py" || goto :fail

echo ==^> [5/5] Smoke test of the executable
set "OUTPUT="
for /f "delims=" %%L in ('"%EXE%"') do set "OUTPUT=%%L"
echo %OUTPUT%
if not "%OUTPUT%"=="Hello, World!" (
  echo ERROR: unexpected output from build\bin\hello.exe 1>&2
  goto :fail
)

if defined GITHUB_STEP_SUMMARY echo ### Windows: tests passed, executable `build\bin\hello.exe` built and prints `%OUTPUT%`>>"%GITHUB_STEP_SUMMARY%"
echo CI: SUCCESS
exit /b 0

:fail
echo CI: FAILED 1>&2
exit /b 1
