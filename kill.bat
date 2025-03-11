@echo off
taskkill /F /IM cmd.exe
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
echo attempted to kill.
pause
