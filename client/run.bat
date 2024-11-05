@echo off
if not exist "C:\chrome\betplay" mkdir "C:\chrome\betplay"
if not exist "C:\chrome\pinnacle" mkdir "C:\chrome\pinnacle"
echo.
set /p input=Do you have browsers open for Betplay and Pinnacle?(y/n):
if /I "%input%"=="n" (
    start chrome.exe -remote-debugging-port=9015 --user-data-dir="C:\chrome\betplay"
    start chrome.exe -remote-debugging-port=9020 --user-data-dir="C:\chrome\pinnacle"
)
echo.
set /p input=Make sure you are logged in to the bookmakers.(y/n):
echo.
if /I "%input%"=="y" (
    python main.py
)
pause