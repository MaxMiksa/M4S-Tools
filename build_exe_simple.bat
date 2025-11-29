@echo off
chcp 65001 >nul
echo ========================================
echo M4S 文件处理工具 - 打包脚本（简化版）
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

REM 创建临时 spec 文件来避免命令行过长的问题
echo 正在创建打包配置...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=[
echo         'winreg',
echo         'urllib.request',
echo         'zipfile',
echo         'tkinter',
echo         'tkinter.ttk',
echo         'tkinter.filedialog',
echo         'tkinter.messagebox',
echo         'tkinter.scrolledtext',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='M4S处理工具',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon=None,
echo ^)
) > build_temp.spec

REM 使用 spec 文件打包
pyinstaller build_temp.spec

if errorlevel 1 (
    echo.
    echo 打包失败！
    if exist build_temp.spec del /q build_temp.spec
    pause
    exit /b 1
)

REM 清理临时文件
if exist build_temp.spec del /q build_temp.spec

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

