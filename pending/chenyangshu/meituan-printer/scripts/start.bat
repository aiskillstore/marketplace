@echo off
chcp 65001 >nul 2>nul
title 美团打印机 Web 管理界面

cd /d "%~dp0"

echo.
echo ======================================
echo   美团打印机 Web 管理界面
echo ======================================
echo.

:: 检测 Python
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON=python
    goto :found
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON=python3
    goto :found
)

echo 未找到 Python，请先安装 Python 3
echo https://www.python.org/downloads/
echo.
pause
exit /b 1

:found
echo 使用 Python: %PYTHON%
%PYTHON% --version

:: 检查依赖
echo.
echo 检查依赖...
%PYTHON% -c "import flask" 2>nul || (
    echo 正在安装 flask...
    %PYTHON% -m pip install flask
)
%PYTHON% -c "import apscheduler" 2>nul || (
    echo 正在安装 apscheduler...
    %PYTHON% -m pip install apscheduler
)

:: 启动服务
echo.
echo 访问地址: http://localhost:5000
echo （如果 5000 被占用则自动使用 5001）
echo 按 Ctrl+C 停止服务
echo.

%PYTHON% web_admin.py

echo.
echo 服务已停止。
pause
