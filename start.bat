@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

set "HOST=127.0.0.1"
set "PORT=8000"
set "URL=http://%HOST%:%PORT%"
set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "LOG_DIR=%~dp0logs"
set "PID_FILE=%LOG_DIR%\serve.pid"
set "STDOUT_LOG=%LOG_DIR%\serve_stdout.log"
set "STDERR_LOG=%LOG_DIR%\serve_stderr.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

if not exist "%PYTHON%" (
  echo [ERROR] 未找到虚拟环境: "%PYTHON%"
  echo 请先执行: python -m venv .venv ^&^& .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "%~dp0.env" (
  if exist "%~dp0.env.example" (
    echo [INFO] 未找到 .env，正在从 .env.example 复制...
    copy /Y "%~dp0.env.example" "%~dp0.env" >nul
  )
)

REM 若端口已在监听，则复用并打开浏览器
call :is_port_listening
if not errorlevel 1 (
  echo [INFO] 端口 %PORT% 已被占用，检查是否为本项目服务...
  call :check_health
  if not errorlevel 1 (
    echo [OK] 服务已在运行，复用现有进程。
    call :save_listen_pid
    call :open_browser
    exit /b 0
  )
  echo [ERROR] 端口 %PORT% 被其他程序占用，请先运行 stop.bat 或释放端口。
  pause
  exit /b 2
)

echo [INFO] 正在后台启动 Web 服务: %URL%
echo [INFO] 首次启动可能自动构建前端，请耐心等待...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = Start-Process -FilePath '%PYTHON%' -ArgumentList @('main.py','--serve-only','--host','%HOST%','--port','%PORT%') -WorkingDirectory '%CD%' -RedirectStandardOutput '%STDOUT_LOG%' -RedirectStandardError '%STDERR_LOG%' -WindowStyle Hidden -PassThru;" ^
  "Set-Content -Path '%PID_FILE%' -Value $p.Id -NoNewline;" ^
  "Write-Output ('STARTED_PID=' + $p.Id)"
if errorlevel 1 (
  echo [ERROR] 启动失败，请查看: %STDERR_LOG%
  pause
  exit /b 3
)

set /a ATTEMPT=0
:wait_health
set /a ATTEMPT+=1
echo [INFO] 等待健康检查... (!ATTEMPT!/120)
call :check_health
if not errorlevel 1 goto health_ok

set "SERVE_PID="
if exist "%PID_FILE%" set /p SERVE_PID=<"%PID_FILE%"
if defined SERVE_PID (
  call :is_pid_alive !SERVE_PID!
  if errorlevel 1 (
    REM 父进程退出后，uvicorn 子进程可能仍在监听，再确认一次端口/健康
    call :is_port_listening
    if errorlevel 1 (
      echo [ERROR] 启动进程已退出，请查看日志:
      echo   %STDOUT_LOG%
      echo   %STDERR_LOG%
      pause
      exit /b 4
    )
  )
)

if !ATTEMPT! GEQ 120 (
  echo [ERROR] 等待健康检查超时（约 10 分钟）。请查看日志:
  echo   %STDOUT_LOG%
  echo   %STDERR_LOG%
  pause
  exit /b 5
)

timeout /t 5 /nobreak >nul
goto wait_health

:health_ok
echo [OK] 健康检查通过: %URL%/api/health
call :save_listen_pid
call :open_browser
echo [INFO] PID 文件: %PID_FILE%
echo [INFO] 日志: %STDOUT_LOG% / %STDERR_LOG%
exit /b 0

REM ---------- helpers ----------

:is_port_listening
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul
exit /b %ERRORLEVEL%

:save_listen_pid
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
  >"%PID_FILE%" echo %%p
)
exit /b 0

:is_pid_alive
if "%~1"=="" exit /b 1
tasklist /FI "PID eq %~1" 2>nul | findstr /I "%~1" >nul
if errorlevel 1 exit /b 1
exit /b 0

:check_health
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try {" ^
  "  $r = Invoke-WebRequest -Uri '%URL%/api/health' -UseBasicParsing -TimeoutSec 5;" ^
  "  if ($r.StatusCode -ne 200) { exit 1 };" ^
  "  $j = $r.Content | ConvertFrom-Json;" ^
  "  if ($j.status -eq 'ok') { Write-Output $r.Content; exit 0 };" ^
  "  exit 1" ^
  "} catch { exit 1 }"
exit /b %ERRORLEVEL%

:open_browser
echo [INFO] 正在打开浏览器: %URL%
REM 优先用系统 URL 协议处理器，避免 cmd start 标题参数问题
rundll32 url.dll,FileProtocolHandler %URL%
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process '%URL%'" >nul 2>&1
echo [OK] 已请求打开浏览器。若未弹出窗口，请手动访问: %URL%
exit /b 0
