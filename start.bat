@echo off
chcp 65001 > nul
title 学习通实习打卡脚本启动器

:: 检查 Python 是否安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python
    echo 您可以从 https://www.python.org/downloads/ 下载安装
    pause
    exit
)

:: 检查 Python 版本
echo [信息] 检查 Python 版本...
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
for /f "tokens=1 delims=." %%I in ("%PYTHON_VERSION%") do set PYTHON_MAJOR=%%I
if %PYTHON_MAJOR% lss 3 (
    echo [错误] Python 版本必须是 3.x 或更高
    echo 当前版本: %PYTHON_VERSION%
    pause
    exit
)

:: 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 检查并安装必要的库
echo [信息] 检查必要的库...

:: 检查并安装缺失的库
python -c "import requests" 2>nul || pip install requests
python -c "import filetype" 2>nul || pip install filetype
python -c "import schedule" 2>nul || pip install schedule

:: 清屏
cls

:: 显示启动信息
echo ================================
echo    学习通实习打卡脚本启动器
echo ================================
echo.
echo [信息] 环境检查完成
echo [信息] Starting script...
echo.

:: 启动 Python 脚本
python start.py

:: 如果脚本异常退出，暂停显示错误信息
if %errorlevel% neq 0 (
    echo.
    echo [错误] 脚本异常退出，错误代码：%errorlevel%
    pause
)

:: 退出虚拟环境
deactivate 