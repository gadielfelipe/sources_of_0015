@echo off
set NOTEBOOK_PATH="C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\2025\Outputs\Output1\Stress Test\3.Data\Scripts Python\scripts_python\Modelos\Api\appi diaria datos precipitacion.ipynb"
set PYTHON=C:\Users\Usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe
set LOG="C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\2025\Outputs\Output1\Stress Test\3.Data\Scripts Python\scripts_python\Modelos\Api\appi_log.txt"

echo [%date% %time%] Iniciando ejecucion >> %LOG%
%PYTHON% -m jupyter nbconvert --to notebook --execute --inplace %NOTEBOOK_PATH% >> %LOG% 2>&1
if %ERRORLEVEL% == 0 (
    echo [%date% %time%] Ejecucion exitosa >> %LOG%
) else (
    echo [%date% %time%] ERROR en la ejecucion >> %LOG%
)
