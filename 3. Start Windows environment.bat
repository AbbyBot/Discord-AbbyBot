@echo off

REM Set script path
set "script_path=%~dp0"

REM Activate virual environment
call "%script_path%venv\Scripts\activate"

REM Change bot directory
cd "%script_path%Python_AbbyBot_Second_phase"

REM Start discord bot
python "AbbyBot.py" run

REM Once the bot is closed, deactivate the virtual environment
deactivate