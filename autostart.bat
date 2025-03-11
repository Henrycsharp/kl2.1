@echo off
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "batFilePath=C:\users\%USERNAME%\kl2\runos.bat"

:: Check if the batch file already exists in the Startup folder
if not exist "%startupFolder%\runos.bat" (
    copy "%batFilePath%" "%startupFolder%"
    echo run.bat has been added to the Startup folder.
) else (
    echo run.bat is already in the Startup folder.
)
