#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本
PyInstaller Packaging Script

推荐使用此脚本进行打包，避免批处理脚本的命令行长度限制
Recommended to use this script for packaging to avoid batch script command line length limits
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_exe():
    """构建 EXE 文件 / Build EXE file"""
    
    # 获取脚本目录 / Get script directory
    script_dir = Path(__file__).parent
    
    # PyInstaller 参数 / PyInstaller arguments
    args = [
        'main.py',
        '--onefile',              # 打包成单个文件 / Single file
        '--windowed',             # 不显示控制台窗口 / No console window
        '--name=M4S Merger Tools v1.2.0',      # 输出文件名 / Output filename
        '--clean',                # 清理临时文件 / Clean cache
        '--noconfirm',            # 覆盖输出目录 / Overwrite output
        # 隐藏导入（确保这些模块被包含） / Hidden imports
        '--hidden-import=winreg',
        '--hidden-import=urllib.request',
        '--hidden-import=zipfile',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
    ]
    
    # 如果有图标文件，添加图标 / Add icon if exists
    icon_path = script_dir / 'icon.ico'
    if icon_path.exists():
        args.append(f'--icon={icon_path}')
    
    print("=" * 60)
    print("M4S 文件处理工具 - 打包脚本")
    print("M4S File Processing Tool - Packaging Script")
    print("=" * 60)
    print()
    print("开始打包... / Starting packaging process...")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 60)
        print("打包完成！/ Packaging completed!")
        print("=" * 60)
        print()
        print(f"可执行文件位置 / Executable location: {script_dir / 'dist' / 'M4S Merger Tools v1.2.0.exe'}")
        print()
        print("您可以将此文件复制到任何 Windows 电脑上运行")
        print("You can copy this file to any Windows computer to run.")
        print("（需要确保目标电脑有网络连接，以便首次运行时下载 FFmpeg）")
        print("(Ensure the target computer has internet access for downloading FFmpeg on first run)")
        print()
        print("注意：程序已添加完善的错误处理，如果出现问题会弹出提示窗口")
        print("Note: Comprehensive error handling included; a popup will appear if issues occur.")
        print()
    except Exception as e:
        print(f"打包失败 / Packaging failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
