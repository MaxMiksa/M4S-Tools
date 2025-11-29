@echo off
chcp 65001
echo ========================================
echo M4S 文件处理工具 - 调试启动脚本
echo ========================================
echo.
echo 此脚本会显示详细的调试信息
echo.

REM 显示 Python 版本
echo [调试] 检查 Python...
python --version
if errorlevel 1 (
    echo [错误] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

echo.
echo [调试] 当前目录: %CD%
echo.
echo [调试] 检查必要文件...
if exist main.py (echo [OK] main.py) else (echo [缺失] main.py)
if exist gui.py (echo [OK] gui.py) else (echo [缺失] gui.py)
if exist m4s_processor.py (echo [OK] m4s_processor.py) else (echo [缺失] m4s_processor.py)
if exist ffmpeg_installer.py (echo [OK] ffmpeg_installer.py) else (echo [缺失] ffmpeg_installer.py)
echo.

echo [调试] 列出当前目录所有文件:
dir /b *.py
echo.

echo [调试] 开始运行程序...
echo ========================================
echo.

REM 运行程序，显示所有输出
python -u main.py

echo.
echo ========================================
echo [调试] 程序已退出（退出代码: %errorlevel%）
echo ========================================
echo.
pause

