@echo off
setlocal

set REPO_DIR=C:\Users\%USERNAME%\kl2.1

if exist "%REPO_DIR%" (
    echo Repository already exists.
    cd "%REPO_DIR%"
    pythonw main.py
    exit
) else (
    echo Cloning repository...
    git clone https://github.com/Henrycsharp/kl2.1 "%REPO_DIR%"
)

cd "%REPO_DIR%"
call run.bat
exit
