@echo off
chcp 65001
echo ========================================
echo M4S 文件处理工具 - 启动脚本
echo ========================================
echo.
echo 正在启动程序...
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo 请确保已安装 Python 3.7 或更高版本
    echo.
    pause
    exit /b 1
)

REM 检查 main.py 是否存在
if not exist main.py (
    echo [错误] 未找到 main.py 文件！
    echo 请确保在正确的目录下运行此脚本
    echo.
    pause
    exit /b 1
)

REM 检查必要的模块文件
if not exist gui.py (
    echo [错误] 未找到 gui.py 文件！
    echo 请确保所有文件都在同一目录下
    echo.
    pause
    exit /b 1
)

if not exist m4s_processor.py (
    echo [错误] 未找到 m4s_processor.py 文件！
    echo 请确保所有文件都在同一目录下
    echo.
    pause
    exit /b 1
)

if not exist ffmpeg_installer.py (
    echo [错误] 未找到 ffmpeg_installer.py 文件！
    echo 请确保所有文件都在同一目录下
    echo.
    pause
    exit /b 1
)

echo [信息] 文件检查通过
echo [信息] 正在启动程序...
echo.
echo ========================================
echo 程序输出（调试信息）
echo ========================================
echo.

REM 运行程序并捕获输出（不重定向错误，让错误也显示在控制台）
python main.py

REM 如果程序正常退出，会立即关闭窗口，所以添加延迟
if errorlevel 1 (
    REM 有错误，已经 pause 了
) else (
    REM 正常退出，等待一下让用户看到
    timeout /t 2 >nul
)

REM 检查退出代码
if errorlevel 1 (
    echo.
    echo ========================================
    echo [错误] 程序运行失败（退出代码: %errorlevel%）
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. Python 版本不兼容（需要 3.7 或更高版本）
    echo 2. 缺少必要的 Python 模块
    echo 3. 程序运行时出错
    echo.
    echo 请查看上方的错误信息以获取更多详情
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [信息] 程序已正常退出
)


