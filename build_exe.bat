@echo off
chcp 65001 >nul
echo ========================================================
echo M4S 文件处理工具 - 打包脚本
echo M4S File Processing Tool - Packaging Script
echo ========================================================
echo.

REM 检查是否安装了 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误：无法安装 PyInstaller
        echo Error: Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

echo.
echo 开始打包...
echo Starting packaging process...
echo.

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "M4S Merger Tools v1.0.0.spec" del /q "M4S Merger Tools v1.0.0.spec"
if exist "M4S Merger Tools v1.2.0.spec" del /q "M4S Merger Tools v1.2.0.spec"

REM 使用 PyInstaller 打包
pyinstaller --onefile --windowed --name "M4S Merger Tools v1.2.0" --clean --noconfirm --hidden-import winreg --hidden-import urllib.request --hidden-import zipfile --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.filedialog --hidden-import tkinter.messagebox --hidden-import tkinter.scrolledtext main.py

if errorlevel 1 (
    echo.
    echo [失败] 打包失败！
    echo [Failed] Packaging failed!
    echo.
    echo 如果遇到命令错误，请尝试使用以下方式：
    echo If you encounter command errors, please try the following:
    echo 1. 运行: python build_exe.py
    echo    Run: python build_exe.py
    echo 2. 或使用: build_exe_simple.bat
    echo    Or use: build_exe_simple.bat
    pause
    exit /b 1
)

echo.
echo ========================================================
echo 打包完成！
echo Packaging completed!
echo ========================================================
echo.
echo 可执行文件位置: dist\M4S Merger Tools v1.2.0.exe
echo Executable location: dist\M4S Merger Tools v1.2.0.exe
echo.
echo 您可以将此文件复制到任何 Windows 电脑上运行
echo You can copy this file to any Windows computer to run.
echo （需要确保目标电脑有网络连接，以便首次运行时下载 FFmpeg）
echo (Ensure target computer has internet access for downloading FFmpeg on first run)
echo.
echo 注意：如果程序运行无反应，请检查：
echo Note: If the program does not respond, please check:
echo 1. 是否有错误提示窗口弹出
echo    1. Is there an error popup window?
echo 2. 任务管理器中是否有进程在运行
echo    2. Is the process running in Task Manager?
echo 3. 尝试以管理员权限运行
echo    3. Try running as administrator.
echo.
pause
