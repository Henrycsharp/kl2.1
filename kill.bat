@echo off
for /f "tokens=1" %%i in ('tasklist ^| findstr cmd.exe') do (
    if not "%%i" == "python.exe" taskkill /F /IM %%i
)
exit
