@echo off
rem Launch Hello World from source inside the project's virtual environment.
setlocal
cd /d "%~dp0"
if "%PYTHON%"=="" set "PYTHON=python"
if not exist ".venv\Scripts\python.exe" (
  "%PYTHON%" -m venv .venv || exit /b 1
)
cd src
"..\.venv\Scripts\python.exe" -m hello %*
