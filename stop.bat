@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

set "PORT=8000"
set "LOG_DIR=%~dp0logs"
set "PID_FILE=%LOG_DIR%\serve.pid"
set "STOPPED=0"

echo [INFO] 正在停止本地 Web 服务...

REM 1) 按 PID 文件停止（含子进程树）
if exist "%PID_FILE%" (
  set /p SERVE_PID=<"%PID_FILE%"
  if defined SERVE_PID (
    tasklist /FI "PID eq %SERVE_PID%" 2>nul | findstr /I "%SERVE_PID%" >nul
    if not errorlevel 1 (
      echo [INFO] 结束 PID %SERVE_PID% 及其子进程...
      taskkill /F /T /PID %SERVE_PID% >nul 2>&1
      set "STOPPED=1"
    )
  )
)

REM 2) 再按端口清理残留监听进程
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING" 2^>nul') do (
  echo [INFO] 结束占用端口 %PORT% 的进程 PID %%p ...
  taskkill /F /T /PID %%p >nul 2>&1
  set "STOPPED=1"
)

REM 3) 兜底：清理本项目 main.py --serve-only 进程
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |" ^
  "Where-Object { $_.CommandLine -and $_.CommandLine -match 'main\.py\s+--serve-only' -and $_.CommandLine -match [regex]::Escape('%CD%') } |" ^
  "ForEach-Object { Write-Output ('KILL_PID=' + $_.ProcessId); Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul
if not errorlevel 1 (
  echo [ERROR] 端口 %PORT% 仍被占用，请手动检查:
  netstat -ano | findstr ":%PORT% " | findstr "LISTENING"
  exit /b 1
)

if exist "%PID_FILE%" del /Q "%PID_FILE%" >nul 2>&1

if "%STOPPED%"=="1" (
  echo [OK] 服务已停止。
) else (
  echo [OK] 未发现运行中的服务。
)
exit /b 0
