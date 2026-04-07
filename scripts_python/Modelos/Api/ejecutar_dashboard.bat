@echo off
:: ejecutar_dashboard.bat
:: Lanzador para el Programador de tareas de Windows.
:: Corre todos los scripts del dashboard ERIS en orden.

SET PYTHON="C:\Users\Usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe"
SET SCRIPT="C:\Users\Usuario\OneDrive - Global Green Growth Institute\Documentos\2025\Outputs\Output1\Stress Test\3.Data\Scripts Python\scripts_python\Modelos\Api\actualizar_dashboard.py"

%PYTHON% %SCRIPT%
