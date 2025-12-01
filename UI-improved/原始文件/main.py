#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理工具 - 主程序入口
"""

import sys
import os
import traceback
from pathlib import Path

def show_error(title, message):
    """显示错误消息框"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # 如果 tkinter 也无法使用，尝试使用 Windows 消息框
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # MB_ICONERROR
        except:
            print(f"错误: {title}\n{message}")
            input("按回车键退出...")

def main():
    """主函数，包含错误处理"""
    try:
        print("[启动] 开始初始化程序...")
        
        # 检查 Python 版本
        print(f"[检查] Python 版本: {sys.version}")
        if sys.version_info < (3, 7):
            error_msg = f"需要 Python 3.7 或更高版本\n当前版本: {sys.version}"
            print(f"[错误] {error_msg}")
            show_error("版本错误", error_msg)
            return
        
        print("[检查] Python 版本检查通过")
        
        # 导入 GUI 模块
        print("[导入] 正在导入 GUI 模块...")
        try:
            from gui import M4SProcessorApp
            print("[导入] GUI 模块导入成功")
        except ImportError as e:
            error_msg = f"无法导入 GUI 模块\n错误: {str(e)}\n\n请确保所有文件都在同一目录下"
            print(f"[错误] {error_msg}")
            print(f"[调试] 当前目录: {os.getcwd()}")
            print(f"[调试] 文件列表: {os.listdir('.')}")
            show_error("导入错误", error_msg)
            return
        except Exception as e:
            error_msg = f"初始化 GUI 模块时出错\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            print(f"[错误] {error_msg}")
            show_error("初始化错误", error_msg)
            return
        
        # 创建并运行应用
        print("[启动] 正在创建应用程序...")
        try:
            app = M4SProcessorApp()
            print("[启动] 应用程序创建成功")
            print("[启动] 检查窗口状态...")
            print(f"[启动] 窗口可见性: {app.root.winfo_viewable()}")
            print(f"[启动] 窗口状态: {app.root.state()}")
            print("[启动] 正在启动 GUI 事件循环...")
            print("[启动] 注意: mainloop() 会阻塞，直到窗口关闭")
            app.run()
            print("[退出] 程序正常退出")
        except Exception as e:
            error_msg = f"程序运行时出错\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            print(f"[错误] {error_msg}")
            show_error("运行时错误", error_msg)
            return
            
    except Exception as e:
        # 捕获所有未处理的异常
        error_msg = f"程序启动失败\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
        print(f"[严重错误] {error_msg}")
        show_error("启动错误", error_msg)

if __name__ == "__main__":
    main()

