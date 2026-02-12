@echo off
setlocal
echo ===========================================
echo   NL Compiler (nlc) - Global Setup
echo ===========================================
echo.

:: Get the current directory where the batch file is running
set "COMPILER_PATH=%~dp0"
:: Remove trailing backslash
set "COMPILER_PATH=%COMPILER_PATH:~0,-1%"

echo Detected Path: %COMPILER_PATH%
echo.

:: Use PowerShell to safely append the path to the User Environment Variable
:: This avoids the 1024-character limit of the 'setx' command.
powershell -Command ^
    "$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User'); " ^
    "if ($currentPath -notlike '*%COMPILER_PATH%*') { " ^
    "    $newPath = $currentPath + ';' + '%COMPILER_PATH%'; " ^
    "    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User'); " ^
    "    Write-Host 'SUCCESS: nlc added to your PATH.' -ForegroundColor Green; " ^
    "} else { " ^
    "    Write-Host 'NOTICE: nlc is already in your PATH.' -ForegroundColor Yellow; " ^
    "}"

echo.
echo -------------------------------------------
echo  IMPORTANT:
echo  1. Close this window and VS Code.
echo  2. Re-open VS Code / Terminal.
echo  3. Try running: nlc --version
echo -------------------------------------------
pause