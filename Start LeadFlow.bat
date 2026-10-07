@echo off
cd /d "%~dp0"
python -m leadflow.web
if errorlevel 1 pause
