@echo off
setlocal enabledelayedexpansion

REM Set script path
set "script_path=%~dp0"

REM Create new enviroment called "venv"
python -m venv "%script_path%venv"

REM Activate virual environment
call "%script_path%venv\Scripts\activate"

REM install requirements.txt
pip install -r "%script_path%requirements.txt"

REM Disable environment
deactivate

echo "Environment and requirements successfully installed!"
pause
