#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本
推荐使用此脚本进行打包，避免批处理脚本的命令行长度限制
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_exe():
    """构建 EXE 文件"""
    
    # 获取脚本目录
    script_dir = Path(__file__).parent
    
    # PyInstaller 参数
    args = [
        'main.py',
        '--onefile',              # 打包成单个文件
        '--windowed',             # 不显示控制台窗口（但错误会通过消息框显示）
        '--name=M4S处理工具',      # 输出文件名
        '--clean',                # 清理临时文件
        '--noconfirm',            # 覆盖输出目录而不询问
        # 隐藏导入（确保这些模块被包含）
        '--hidden-import=winreg',
        '--hidden-import=urllib.request',
        '--hidden-import=zipfile',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
    ]
    
    # 如果有图标文件，添加图标
    icon_path = script_dir / 'icon.ico'
    if icon_path.exists():
        args.append(f'--icon={icon_path}')
    
    print("=" * 50)
    print("M4S 文件处理工具 - 打包脚本")
    print("=" * 50)
    print()
    print("开始打包...")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 50)
        print("打包完成！")
        print("=" * 50)
        print()
        print(f"可执行文件位置: {script_dir / 'dist' / 'M4S处理工具.exe'}")
        print()
        print("您可以将此文件复制到任何 Windows 电脑上运行")
        print("（需要确保目标电脑有网络连接，以便首次运行时下载 FFmpeg）")
        print()
        print("注意：程序已添加完善的错误处理，如果出现问题会弹出提示窗口")
        print()
    except Exception as e:
        print(f"打包失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    build_exe()

