#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 tkinter 是否正常工作
"""

import sys
import traceback

print("=" * 50)
print("测试 tkinter 功能")
print("=" * 50)
print()

try:
    print("[1] 导入 tkinter...")
    import tkinter as tk
    from tkinter import messagebox
    print("[1] ✓ tkinter 导入成功")
except Exception as e:
    print(f"[1] ✗ tkinter 导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("[2] 创建根窗口...")
    root = tk.Tk()
    print("[2] ✓ 根窗口创建成功")
except Exception as e:
    print(f"[2] ✗ 根窗口创建失败: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("[3] 设置窗口属性...")
    root.title("测试窗口")
    root.geometry("400x300")
    print("[3] ✓ 窗口属性设置成功")
except Exception as e:
    print(f"[3] ✗ 窗口属性设置失败: {e}")
    traceback.print_exc()
    root.destroy()
    sys.exit(1)

try:
    print("[4] 添加标签...")
    label = tk.Label(root, text="如果看到这个窗口，说明 tkinter 正常工作！", font=("Arial", 12))
    label.pack(pady=50)
    print("[4] ✓ 标签添加成功")
except Exception as e:
    print(f"[4] ✗ 标签添加失败: {e}")
    traceback.print_exc()
    root.destroy()
    sys.exit(1)

try:
    print("[5] 更新窗口...")
    root.update_idletasks()
    root.update()
    print("[5] ✓ 窗口更新成功")
except Exception as e:
    print(f"[5] ✗ 窗口更新失败: {e}")
    traceback.print_exc()
    root.destroy()
    sys.exit(1)

print()
print("[6] 窗口应该已经显示，请检查是否有窗口弹出")
print("[6] 5秒后自动关闭窗口...")
print()

try:
    # 5秒后自动关闭
    def close_window():
        print("[7] 关闭窗口...")
        root.quit()
        root.destroy()
        print("[7] ✓ 窗口已关闭")
    
    root.after(5000, close_window)
    
    print("[6] 启动事件循环...")
    root.mainloop()
    print("[6] ✓ 事件循环已退出")
except Exception as e:
    print(f"[6] ✗ 事件循环失败: {e}")
    traceback.print_exc()
    try:
        root.destroy()
    except:
        pass
    sys.exit(1)

print()
print("=" * 50)
print("测试完成！如果看到窗口，说明 tkinter 正常工作")
print("=" * 50)

