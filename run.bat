@echo off
REM Change to the project directory if needed
cd /d %~dp0

REM Activate virtualenv and run the app
call env\Scripts\activate.bat
python src\vanta_ledger\main.py
