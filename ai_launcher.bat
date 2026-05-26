@echo off
setlocal enabledelayedexpansion
title proxyMa_AI Dynamic Launcher
mode 80,30

:: performance settings
set PORT=8080
set CONTEXT=1536
set KEEP=64
set THREADS=3
set BATCH=64
set UBATCH=32
set NP=1

set MODEL_DIR=models

:MENU
cls
echo ================================
echo       proxyMa_AI Launcher
echo ================================
echo.

set count=0

for %%f in ("%MODEL_DIR%\*.gguf") do (
    set /a count+=1
    set model!count!=%%~nxf
    echo [!count!] %%~nxf
)

if %count%==0 (
    echo No models found.
    pause
    exit
)

set /a exitOption=count+1
echo [!exitOption!] Exit
echo.

set /p choice=Select model:

if "%choice%"=="!exitOption!" exit

if not defined model%choice% (
    echo Invalid choice
    timeout /t 2 >nul
    goto MENU
)

set MODEL=!model%choice%!

cls
echo Launching !MODEL!...
echo.

:: Launch llamafile in separate window
start "Llama Server" cmd /k llamafile.exe ^
--server ^
--host 127.0.0.1 ^
--port %PORT% ^
--model "%MODEL_DIR%\!MODEL!" ^
-c %CONTEXT% ^
--keep %KEEP% ^
-t %THREADS% ^
-b %BATCH% ^
-ub %UBATCH% ^
-np %NP% ^
--mmap

timeout /t 5 >nul

echo Starting proxy...

:: keeps batch waiting properly
call python context_proxy.py

echo.
echo Proxy closed.
pause
goto MENU