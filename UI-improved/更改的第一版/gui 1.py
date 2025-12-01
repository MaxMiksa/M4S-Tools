#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理工具 - GUI 界面 (Modern Design)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk  # 保留原生引用作为类型提示或常量
import threading
import traceback
import os
import sys
from pathlib import Path

# 尝试导入 ttkbootstrap 以实现现代化 UI
# 如果用户没有安装，则回退到原生 ttk，但使用自定义样式美化
try:
    import ttkbootstrap as ttk_boot
    from ttkbootstrap.constants import *
    HAS_BOOTSTRAP = True
except ImportError:
    HAS_BOOTSTRAP = False
    print("[提示] 未检测到 ttkbootstrap，将使用原生界面。建议运行 pip install ttkbootstrap 以获得更好的视觉体验。")

try:
    from m4s_processor import M4SProcessor
    from ffmpeg_installer import FFmpegInstaller
except ImportError as e:
    import sys
    # 错误处理逻辑保持不变
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("导入错误", f"无法导入必要的模块\n错误: {str(e)}\n\n请确保所有文件都在同一目录下")
        root.destroy()
    except:
        pass
    sys.exit(1)


class M4SProcessorApp:
    def __init__(self):
        try:
            print("[GUI] 初始化主窗口...")
            
            # --- 窗口初始化 ---
            if HAS_BOOTSTRAP:
                # 使用 'cosmo' (浅色) 或 'darkly' (深色) 主题
                # 其他好看的主题推荐: 'yeti', 'journal', 'superhero'
                self.root = ttk_boot.Window(themename="cosmo")
            else:
                self.root = tk.Tk()
            
            self.root.title("M4S 音视频合并工具 Pro")
            self.root.geometry("950x780")
            self.root.minsize(800, 600)
            
            # --- 字体配置 ---
            # 定义一套现代字体
            self.fonts = {
                "h1": ("Segoe UI", 16, "bold"),
                "h2": ("Segoe UI", 11, "bold"),
                "body": ("Segoe UI", 10),
                "mono": ("Consolas", 9),  # 日志字体
                "icon": ("Segoe UI Emoji", 10) # 确保图标显示
            }

            # 如果没有 bootstrap，手动配置一些原生样式来美化
            if not HAS_BOOTSTRAP:
                style = ttk.Style()
                try:
                    style.theme_use('clam') # clam 主题比默认的好看
                except:
                    pass
                style.configure("TButton", font=self.fonts["body"], padding=5)
                style.configure("TLabel", font=self.fonts["body"])
                style.configure("TLabelframe", font=self.fonts["h2"])
                style.configure("TLabelframe.Label", foreground="#007bff") # 蓝色标题

            # --- 变量初始化 (逻辑不变) ---
            self.video_files = []
            self.audio_files = []
            self.output_dir = ""
            
            # --- FFmpeg 检查 (逻辑不变) ---
            ffmpeg_available = M4SProcessor.check_ffmpeg_available()
            
            if not ffmpeg_available:
                self.root.withdraw()
                self.install_ffmpeg_dialog()
            else:
                self.processor = M4SProcessor(check_ffmpeg=False)
                self.setup_ui()
                self.log("✨ 程序就绪，等待操作...")
                
        except Exception as e:
            error_msg = f"程序启动失败\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            print(f"[GUI] 严重错误: {error_msg}")
            messagebox.showerror("启动错误", error_msg)
            raise
        
    def show_error(self, title, message):
        """显示错误消息"""
        messagebox.showerror(title, message)
        self.log(f"❌ 错误: {title} - {message}")
        
    def setup_ui(self):
        """构建现代化用户界面"""
        
        # 主容器 - 增加外边距，让界面呼吸
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # --- 1. 顶部标题区 ---
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_lbl = ttk.Label(
            header_frame, 
            text="🎥 M4S 文件极速处理工具", 
            font=self.fonts["h1"],
            foreground="#2c3e50" if not HAS_BOOTSTRAP else None, # 原生模式下手动指定颜色
            bootstyle="primary" if HAS_BOOTSTRAP else None
        )
        title_lbl.pack(side=tk.LEFT)
        
        ver_lbl = ttk.Label(header_frame, text="v2.0", font=("Segoe UI", 9), foreground="gray")
        ver_lbl.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))

        # --- 2. 核心操作区 (左右分栏或上下分栏) ---
        # 这里使用上下分栏，但把 视频和音频做得更像"卡片"
        
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # === 视频卡片 ===
        self._create_file_card(
            parent=content_frame,
            title="视频轨道 (Video Track)",
            icon="🎞️",
            color="primary",
            list_attr_name="video_listbox",
            add_cmd=self.select_video_files,
            clear_cmd=self.clear_video_files,
            row=0
        )
        
        # === 音频卡片 ===
        self._create_file_card(
            parent=content_frame,
            title="音频轨道 (Audio Track)",
            icon="🎵",
            color="success",
            list_attr_name="audio_listbox",
            add_cmd=self.select_audio_files,
            clear_cmd=self.clear_audio_files,
            row=1
        )

        # === 输出设置区 ===
        output_card = ttk.LabelFrame(
            content_frame, 
            text="📂 输出设置", 
            padding=15,
            bootstyle="info" if HAS_BOOTSTRAP else None
        )
        output_card.pack(fill=tk.X, pady=(0, 20))
        
        output_inner = ttk.Frame(output_card)
        output_inner.pack(fill=tk.X)
        
        self.output_dir_var = tk.StringVar(value="未选择 (默认保存到当前目录)")
        
        path_entry = ttk.Entry(
            output_inner, 
            textvariable=self.output_dir_var, 
            state="readonly",
            font=self.fonts["body"]
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_browse = ttk.Button(
            output_inner, 
            text="浏览文件夹", 
            command=self.select_output_dir,
            cursor="hand2",
            bootstyle="info-outline" if HAS_BOOTSTRAP else None
        )
        btn_browse.pack(side=tk.RIGHT)

        # === 底部操作栏 (大按钮) ===
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 使用 Grid 布局让按钮等宽分布
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=2) # 混流按钮大一点
        
        # 按钮样式配置
        btn_pad = 10
        
        self.btn_merge_v = ttk.Button(
            action_frame,
            text="仅合并视频",
            command=self.merge_video,
            width=15,
            cursor="hand2",
            bootstyle="primary-outline" if HAS_BOOTSTRAP else None
        )
        self.btn_merge_v.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_merge_a = ttk.Button(
            action_frame,
            text="仅合并音频",
            command=self.merge_audio,
            width=15,
            cursor="hand2",
            bootstyle="success-outline" if HAS_BOOTSTRAP else None
        )
        self.btn_merge_a.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.btn_merge_all = ttk.Button(
            action_frame,
            text="🚀 一键混流 (音频+视频)",
            command=self.merge_av_direct,
            width=25,
            cursor="hand2",
            bootstyle="danger" if HAS_BOOTSTRAP else None # 醒目的颜色
        )
        self.btn_merge_all.grid(row=0, column=2, padx=5, sticky="ew")

        # === 日志和状态区 ===
        log_frame = ttk.LabelFrame(main_container, text="📝 处理日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条和文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            font=self.fonts["mono"],
            state='normal',
            cursor="arrow"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 美化日志背景 (终端风格)
        self.log_text.configure(bg="#f0f0f0", fg="#333333", relief=tk.FLAT, padx=5, pady=5)
        if HAS_BOOTSTRAP:
            # 如果是 bootstrap，根据主题可能需要调整颜色，这里保持通用淡灰色
            pass

        # === 底部状态栏 ===
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_var = tk.StringVar(value="准备就绪")
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            status_frame, 
            mode='indeterminate', 
            bootstyle="striped-success" if HAS_BOOTSTRAP else "horizontal"
        )
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 状态文字
        status_lbl = ttk.Label(
            status_frame, 
            textvariable=self.progress_var,
            font=("Segoe UI", 9),
            foreground="gray"
        )
        status_lbl.pack(side=tk.LEFT)

    def _create_file_card(self, parent, title, icon, color, list_attr_name, add_cmd, clear_cmd, row):
        """辅助函数：创建统一风格的文件选择卡片"""
        card = ttk.LabelFrame(
            parent, 
            text=f"{icon} {title}", 
            padding=15,
            bootstyle=color if HAS_BOOTSTRAP else None
        )
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 内部布局：左侧列表，右侧按钮
        inner = ttk.Frame(card)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # 列表区域
        list_frame = ttk.Frame(inner)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            list_frame,
            height=4,
            font=self.fonts["body"],
            selectmode=tk.EXTENDED,
            relief=tk.FLAT,
            borderwidth=1,
            bg="#ffffff" if not HAS_BOOTSTRAP else None,
            highlightthickness=1,
            highlightcolor="#bdc3c7",
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.config(command=listbox.yview)
        
        # 绑定到实例变量 (关键：保持逻辑兼容性)
        setattr(self, list_attr_name, listbox)
        
        # 按钮区域 (垂直排列)
        btn_frame = ttk.Frame(inner)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        add_btn = ttk.Button(
            btn_frame, 
            text="➕ 添加文件", 
            command=add_cmd,
            width=12,
            cursor="hand2",
            bootstyle=f"{color}" if HAS_BOOTSTRAP else None
        )
        add_btn.pack(pady=(0, 5))
        
        clear_btn = ttk.Button(
            btn_frame, 
            text="🗑️ 清空", 
            command=clear_cmd,
            width=12,
            cursor="hand2",
            bootstyle="secondary-outline" if HAS_BOOTSTRAP else None
        )
        clear_btn.pack()

    # -------------------------------------------------------------------------
    # 以下逻辑方法保持不变，直接复制原有逻辑以确保功能一致
    # -------------------------------------------------------------------------

    def log(self, message):
        """添加日志消息"""
        try:
            self.log_text.insert(tk.END, f"[{self._get_time()}] {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"日志: {message}")

    def _get_time(self):
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def select_video_files(self):
        try:
            files = filedialog.askopenfilenames(
                title="选择视频 M4S 文件",
                filetypes=[("M4S 文件", "*.m4s"), ("所有文件", "*.*")]
            )
            if files:
                self.video_files = list(files)
                self.video_listbox.delete(0, tk.END)
                for file in self.video_files:
                    # 显示文件名和大小
                    size_mb = os.path.getsize(file) / 1024 / 1024
                    self.video_listbox.insert(tk.END, f"{Path(file).name} ({size_mb:.2f} MB)")
                self.log(f"已加载 {len(self.video_files)} 个视频片段")
        except Exception as e:
            self.show_error("文件选择错误", str(e))
            
    def select_audio_files(self):
        try:
            files = filedialog.askopenfilenames(
                title="选择音频 M4S 文件",
                filetypes=[("M4S 文件", "*.m4s"), ("所有文件", "*.*")]
            )
            if files:
                self.audio_files = list(files)
                self.audio_listbox.delete(0, tk.END)
                for file in self.audio_files:
                    size_mb = os.path.getsize(file) / 1024 / 1024
                    self.audio_listbox.insert(tk.END, f"{Path(file).name} ({size_mb:.2f} MB)")
                self.log(f"已加载 {len(self.audio_files)} 个音频片段")
        except Exception as e:
            self.show_error("文件选择错误", str(e))
            
    def clear_video_files(self):
        self.video_files = []
        self.video_listbox.delete(0, tk.END)
        self.log("🗑️ 已清空视频列表")
        
    def clear_audio_files(self):
        self.audio_files = []
        self.audio_listbox.delete(0, tk.END)
        self.log("🗑️ 已清空音频列表")
        
    def select_output_dir(self):
        try:
            dir_path = filedialog.askdirectory(title="选择输出保存位置")
            if dir_path:
                self.output_dir = dir_path
                self.output_dir_var.set(dir_path)
                self.log(f"📂 输出目录设置为: {dir_path}")
        except Exception as e:
            self.show_error("目录选择错误", str(e))

    def _check_inputs(self, check_video=False, check_audio=False):
        if check_video and not self.video_files:
            messagebox.showwarning("提示", "请先添加视频 M4S 文件！")
            return False
        if check_audio and not self.audio_files:
            messagebox.showwarning("提示", "请先添加音频 M4S 文件！")
            return False
        if not self.output_dir:
            # 如果未选择，默认当前目录
            self.output_dir = os.getcwd()
            self.output_dir_var.set(f"{self.output_dir} (自动默认)")
            self.log("未选择目录，将默认输出到程序运行目录")
        return True

    def merge_video(self):
        if not self._check_inputs(check_video=True): return
        self._run_task("视频合并", lambda: self.processor.merge_video_segments(self.video_files, self.output_dir))
        
    def merge_audio(self):
        if not self._check_inputs(check_audio=True): return
        self._run_task("音频合并", lambda: self.processor.merge_audio_segments(self.audio_files, self.output_dir))
        
    def merge_av_direct(self):
        if not self._check_inputs(check_video=True, check_audio=True): return
        self._run_task("一键混流", lambda: self.processor.process_all(self.video_files, self.audio_files, self.output_dir))

    def _run_task(self, task_name, task_func):
        """统一的任务执行包装器"""
        self.progress_bar.start(10)
        self.progress_var.set(f"正在执行: {task_name}...")
        self._set_buttons_state(tk.DISABLED)
        
        def process():
            try:
                self.root.after(0, lambda: self.log(f"🚀 开始任务: {task_name}"))
                result = task_func()
                self.root.after(0, lambda: self.on_process_complete(f"✅ {task_name}成功！\n文件保存于: {result}", True))
                # 尝试打开文件夹
                try:
                    os.startfile(os.path.dirname(result))
                except:
                    pass
            except Exception as e:
                error_detail = traceback.format_exc()
                self.root.after(0, lambda: self.log(f"❌ 失败: {str(e)}"))
                print(error_detail)
                self.root.after(0, lambda: self.on_process_complete(f"❌ {task_name}失败: {str(e)}", False))
                
        threading.Thread(target=process, daemon=True).start()

    def _set_buttons_state(self, state):
        self.btn_merge_v.configure(state=state)
        self.btn_merge_a.configure(state=state)
        self.btn_merge_all.configure(state=state)

    def on_process_complete(self, message, success):
        self.progress_bar.stop()
        self.progress_var.set("就绪" if success else "发生错误")
        self._set_buttons_state(tk.NORMAL)
        self.log(message)
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)

    # --- FFmpeg 安装对话框优化 ---
    
    def install_ffmpeg_dialog(self):
        dialog = tk.Toplevel() if not HAS_BOOTSTRAP else ttk_boot.Toplevel()
        dialog.title("🔧 环境配置")
        dialog.geometry("550x350")
        
        # 居中
        x = (self.root.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.root.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        content = ttk.Frame(dialog, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content, text="⚠️ 未检测到 FFmpeg 组件", font=("Segoe UI", 14, "bold"), foreground="#e74c3c" if not HAS_BOOTSTRAP else None, bootstyle="danger").pack(pady=(0, 10))
        ttk.Label(content, text="本工具需要 FFmpeg 才能进行音视频合并。\n程序可以自动为您下载并安装。", font=("Segoe UI", 10)).pack(pady=(0, 20))
        
        # 路径选择
        path_frame = ttk.LabelFrame(content, text="安装位置", padding=10)
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.install_dir_var = tk.StringVar(value=str(Path.home() / "ffmpeg"))
        ttk.Entry(path_frame, textvariable=self.install_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="更改", command=lambda: self.select_install_dir(dialog), bootstyle="secondary-outline" if HAS_BOOTSTRAP else None).pack(side=tk.RIGHT)
        
        # 进度条
        self.install_progress_var = tk.StringVar(value="等待开始...")
        ttk.Label(content, textvariable=self.install_progress_var, font=("Segoe UI", 9)).pack(anchor="w")
        
        self.install_progress_bar = ttk.Progressbar(content, mode='determinate', bootstyle="striped" if HAS_BOOTSTRAP else None)
        self.install_progress_bar.pack(fill=tk.X, pady=(5, 20))
        
        # 按钮
        btn_frame = ttk.Frame(content)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🚀 立即安装", command=lambda: self.start_install_ffmpeg(dialog), bootstyle="success" if HAS_BOOTSTRAP else None, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="退出程序", command=lambda: self.cancel_install(dialog), bootstyle="secondary" if HAS_BOOTSTRAP else None).pack(side=tk.LEFT, padx=10)
        
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.cancel_install(dialog))
        self.root.wait_window(dialog)

    # 安装相关的辅助方法保持原有逻辑
    def select_install_dir(self, parent):
        dir_path = filedialog.askdirectory(parent=parent, title="选择 FFmpeg 安装目录")
        if dir_path: self.install_dir_var.set(dir_path)

    def start_install_ffmpeg(self, dialog):
        # 逻辑与原版相同，省略重复代码，直接调用线程
        install_dir = Path(self.install_dir_var.get())
        if not install_dir.parent.exists():
            messagebox.showerror("错误", "所选目录的父目录不存在！")
            return
            
        # 锁定按钮
        for widget in dialog.winfo_children(): # 简单粗暴锁定
             if isinstance(widget, ttk.Button): widget.configure(state="disabled")

        def install():
            try:
                def progress_callback(stage, current, total, message):
                    if total > 0:
                        self.root.after(0, lambda: self.install_progress_bar.config(mode='determinate', maximum=100, value=int((current/total)*100)))
                    else:
                        self.root.after(0, lambda: self.install_progress_bar.config(mode='indeterminate'))
                        self.root.after(0, lambda: self.install_progress_bar.start())
                    self.root.after(0, lambda: self.install_progress_var.set(message))
                
                bin_dir, path_success = FFmpegInstaller.install_ffmpeg(install_dir, progress_callback)
                msg = f"安装成功！\n位置: {bin_dir}\n{'环境变量设置成功' if path_success else '请手动添加环境变量'}\n\n请重启程序。"
                self.root.after(0, lambda: self.on_install_complete(dialog, msg, True))
            except Exception as e:
                self.root.after(0, lambda: self.on_install_complete(dialog, str(e), False))
        
        threading.Thread(target=install, daemon=True).start()

    def on_install_complete(self, dialog, message, success):
        if success:
            messagebox.showinfo("完成", message)
            dialog.destroy()
            self.root.destroy()
        else:
            messagebox.showerror("失败", message)
            # 恢复按钮状态代码略

    def cancel_install(self, dialog):
        if messagebox.askokcancel("退出", "需要 FFmpeg 才能运行。确定退出吗？"):
            dialog.destroy()
            self.root.destroy()

    def run(self):
        # 居中显示主窗口
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()