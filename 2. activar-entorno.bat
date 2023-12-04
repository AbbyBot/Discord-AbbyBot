@echo off

REM Definir la ruta del script actual
set "script_path=%~dp0"

REM Activar el entorno virtual (Windows)
call "%script_path%venv\Scripts\activate"

REM Cambiar al directorio base
cd "%script_path%"

REM Mantener la ventana de comando abierta para que el entorno virtual permanezca activado
cmd /k
