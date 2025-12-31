@echo off
chcp 65001 > nul
cd /d "%~dp0"
python update_checker.py
pause
