@echo off
:: ejecutar_incendios.bat
:: Lanzador para el Programador de tareas de Windows.
:: Coloca la ruta de este .bat en la acción de la tarea.

SET PYTHON="C:\Users\Usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe"
SET SCRIPT="C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\2025\Outputs\Output1\Stress Test\3.Data\Scripts Python\scripts_python\incendios_diarios.py"

%PYTHON% %SCRIPT%
