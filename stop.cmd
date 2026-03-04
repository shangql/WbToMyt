@echo off
chcp 65001 >nul
echo ==================================================
echo 停止 Web 服务...
echo ==================================================

REM 查找并终止占用 8080 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo 终止进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo 服务已停止
pause