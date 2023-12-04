@echo off
setlocal enabledelayedexpansion

REM Definir la ruta del script actual
set "script_path=%~dp0"

REM Crear un entorno virtual en Python
python -m venv "%script_path%venv"

REM Activar el entorno virtual (Windows)
call "%script_path%venv\Scripts\activate"

REM Instalar las dependencias desde el archivo dependences.txt usando pip
pip install -r "%script_path%dependences.txt"

REM Desactivar el entorno virtual
deactivate

echo "Entorno virtual creado y dependencias instaladas correctamente."
pause
