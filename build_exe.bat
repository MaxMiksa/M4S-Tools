@echo off
chcp 65001 >nul
echo ========================================
echo M4S 文件处理工具 - 打包脚本
echo ========================================
echo.

REM 检查是否安装了 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误：无法安装 PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo 开始打包...
echo.

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "M4S处理工具.spec" del /q "M4S处理工具.spec"

REM 使用 PyInstaller 打包（使用 ^ 符号进行换行）
pyinstaller --onefile --windowed --name "M4S处理工具" --clean --noconfirm --hidden-import winreg --hidden-import urllib.request --hidden-import zipfile --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.filedialog --hidden-import tkinter.messagebox --hidden-import tkinter.scrolledtext main.py

if errorlevel 1 (
    echo.
    echo 打包失败！
    echo.
    echo 如果遇到命令错误，请尝试使用以下方式：
    echo 1. 运行: python build_exe.py
    echo 2. 或使用: build_exe_simple.bat
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\M4S处理工具.exe
echo.
echo 您可以将此文件复制到任何 Windows 电脑上运行
echo （需要确保目标电脑有网络连接，以便首次运行时下载 FFmpeg）
echo.
echo 注意：如果程序运行无反应，请检查：
echo 1. 是否有错误提示窗口弹出
echo 2. 任务管理器中是否有进程在运行
echo 3. 尝试以管理员权限运行
echo.
pause

