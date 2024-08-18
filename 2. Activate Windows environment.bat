@echo off

REM Set script path
set "script_path=%~dp0"

REM Activate virual environment
call "%script_path%venv\Scripts\activate"

REM Change to base path
cd "%script_path%"

REM Keep the command prompt open, that the virtual environment remains activated
cmd /k
