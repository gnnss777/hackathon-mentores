@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "atualizar_ranking.ps1"
pause
