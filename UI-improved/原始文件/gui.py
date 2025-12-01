#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理工具 - GUI 界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import traceback
import os
import sys
from pathlib import Path

try:
    from m4s_processor import M4SProcessor
    from ffmpeg_installer import FFmpegInstaller
except ImportError as e:
    # 如果导入失败，显示错误
    import sys
    print(f"[错误] 无法导入必要的模块: {e}")
    print(f"[调试] 当前目录: {os.getcwd()}")
    print(f"[调试] Python 路径: {sys.path}")
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("导入错误", f"无法导入必要的模块\n错误: {str(e)}\n\n请确保所有文件都在同一目录下")
        root.destroy()
    except:
        print("[错误] 无法显示错误对话框，请检查 tkinter 是否正常工作")
    sys.exit(1)


class M4SProcessorApp:
    def __init__(self):
        try:
            print("[GUI] 步骤 1: 创建主窗口...")
            self.root = tk.Tk()
            print("[GUI] 步骤 2: 设置窗口属性...")
            self.root.title("M4S 文件处理工具")
            self.root.geometry("900x700")
            self.root.resizable(True, True)
            
            # 设置 Win11 风格
            try:
                # 尝试使用 Segoe UI 字体（Win11 默认字体）
                self.default_font = ("Segoe UI", 9)
                self.title_font = ("Segoe UI", 11, "bold")
                self.button_font = ("Segoe UI", 9)
            except:
                # 如果 Segoe UI 不可用，使用系统默认
                self.default_font = ("Microsoft YaHei UI", 9)
                self.title_font = ("Microsoft YaHei UI", 11, "bold")
                self.button_font = ("Microsoft YaHei UI", 9)
            print("[GUI] 步骤 3: 初始化变量...")
            
            # 文件路径变量
            self.video_files = []
            self.audio_files = []
            self.output_dir = ""
            
            # 检查 FFmpeg
            print("[GUI] 步骤 4: 检查 FFmpeg...")
            ffmpeg_available = M4SProcessor.check_ffmpeg_available()
            print(f"[GUI] FFmpeg 检查结果: {ffmpeg_available}")
            
            if not ffmpeg_available:
                print("[GUI] FFmpeg 未安装，显示安装对话框...")
                self.root.withdraw()  # 隐藏主窗口
                self.install_ffmpeg_dialog()
            else:
                print("[GUI] FFmpeg 已安装，初始化处理器...")
                # 初始化处理器
                try:
                    self.processor = M4SProcessor(check_ffmpeg=False)
                    print("[GUI] 处理器初始化成功，设置 UI...")
                    self.setup_ui()
                    print("[GUI] UI 设置完成")
                    self.log("程序启动成功")
                    print("[GUI] 初始化完成，准备显示窗口...")
                except Exception as e:
                    error_msg = f"初始化处理器失败\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
                    print(f"[GUI] 错误: {error_msg}")
                    self.show_error("初始化错误", error_msg)
                    self.root.destroy()
        except Exception as e:
            # 如果初始化失败，显示错误
            error_msg = f"程序启动失败\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            print(f"[GUI] 严重错误: {error_msg}")
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("启动错误", error_msg)
                root.destroy()
            except Exception as e2:
                print(f"[GUI] 无法显示错误对话框: {e2}")
            raise
        
    def show_error(self, title, message):
        """显示错误消息"""
        try:
            messagebox.showerror(title, message)
            self.log(f"错误: {title} - {message}")
        except:
            self.log(f"错误: {title} - {message}")
        
    def setup_ui(self):
        """设置用户界面 - Win11 风格"""
        try:
            print("[UI] 开始创建用户界面...")
            # 主框架 - 使用更大的内边距
            print("[UI] 创建主框架...")
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # 配置网格权重
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            
            # 标题区域
            title_label = ttk.Label(
                main_frame, 
                text="M4S 文件处理工具", 
                font=self.title_font
            )
            title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))
            
            # 视频文件选择区域 - 卡片式设计
            video_card = ttk.LabelFrame(main_frame, text="视频文件 (M4S)", padding="15")
            video_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
            video_card.columnconfigure(0, weight=1)
            
            # 视频文件列表和按钮
            video_list_frame = ttk.Frame(video_card)
            video_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            video_list_frame.columnconfigure(0, weight=1)
            
            self.video_listbox = tk.Listbox(video_list_frame, height=5, selectmode=tk.EXTENDED, font=self.default_font)
            self.video_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
            
            video_scrollbar = ttk.Scrollbar(video_list_frame, orient=tk.VERTICAL, command=self.video_listbox.yview)
            video_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            self.video_listbox.config(yscrollcommand=video_scrollbar.set)
            
            video_btn_frame = ttk.Frame(video_card)
            video_btn_frame.grid(row=1, column=0, sticky=tk.W)
            
            ttk.Button(video_btn_frame, text="选择视频文件", command=self.select_video_files, width=16).grid(
                row=0, column=0, padx=(0, 8)
            )
            ttk.Button(video_btn_frame, text="清空", command=self.clear_video_files, width=12).grid(
                row=0, column=1
            )
            
            # 音频文件选择区域 - 卡片式设计
            audio_card = ttk.LabelFrame(main_frame, text="音频文件 (M4S)", padding="15")
            audio_card.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
            audio_card.columnconfigure(0, weight=1)
            
            # 音频文件列表和按钮
            audio_list_frame = ttk.Frame(audio_card)
            audio_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            audio_list_frame.columnconfigure(0, weight=1)
            
            self.audio_listbox = tk.Listbox(audio_list_frame, height=5, selectmode=tk.EXTENDED, font=self.default_font)
            self.audio_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
            
            audio_scrollbar = ttk.Scrollbar(audio_list_frame, orient=tk.VERTICAL, command=self.audio_listbox.yview)
            audio_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            self.audio_listbox.config(yscrollcommand=audio_scrollbar.set)
            
            audio_btn_frame = ttk.Frame(audio_card)
            audio_btn_frame.grid(row=1, column=0, sticky=tk.W)
            
            ttk.Button(audio_btn_frame, text="选择音频文件", command=self.select_audio_files, width=16).grid(
                row=0, column=0, padx=(0, 8)
            )
            ttk.Button(audio_btn_frame, text="清空", command=self.clear_audio_files, width=12).grid(
                row=0, column=1
            )
            
            # 输出目录选择 - 卡片式设计
            output_card = ttk.LabelFrame(main_frame, text="输出设置", padding="15")
            output_card.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
            output_card.columnconfigure(1, weight=1)
            
            ttk.Label(output_card, text="输出目录:", font=self.default_font).grid(
                row=0, column=0, sticky=tk.W, padx=(0, 10)
            )
            
            self.output_dir_var = tk.StringVar(value="未选择")
            output_path_label = ttk.Label(
                output_card, 
                textvariable=self.output_dir_var, 
                foreground="gray",
                font=self.default_font
            )
            output_path_label.grid(row=0, column=1, sticky=tk.W)
            
            ttk.Button(output_card, text="选择目录", command=self.select_output_dir, width=14).grid(
                row=0, column=2, padx=(10, 0)
            )
            
            # 操作按钮区域 - 更大的按钮，更好的间距
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=4, column=0, pady=(0, 20))
            
            ttk.Button(
                button_frame, 
                text="合并视频", 
                command=self.merge_video, 
                width=20
            ).grid(row=0, column=0, padx=8)
            
            ttk.Button(
                button_frame, 
                text="合并音频", 
                command=self.merge_audio, 
                width=20
            ).grid(row=0, column=1, padx=8)
            
            ttk.Button(
                button_frame, 
                text="合并音频视频 (混流)", 
                command=self.merge_av_direct, 
                width=24
            ).grid(row=0, column=2, padx=8)
            
            # 日志输出区域 - 卡片式设计
            log_card = ttk.LabelFrame(main_frame, text="处理日志", padding="15")
            log_card.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
            log_card.columnconfigure(0, weight=1)
            log_card.rowconfigure(0, weight=1)
            
            self.log_text = scrolledtext.ScrolledText(
                log_card, 
                height=8, 
                wrap=tk.WORD,
                font=self.default_font,
                relief=tk.FLAT,
                borderwidth=1
            )
            self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # 配置行权重
            main_frame.rowconfigure(5, weight=1)
            
            # 状态栏
            status_frame = ttk.Frame(main_frame)
            status_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
            status_frame.columnconfigure(0, weight=1)
            
            self.progress_var = tk.StringVar(value="就绪")
            self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=400)
            self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
            
            self.status_label = ttk.Label(
                status_frame, 
                textvariable=self.progress_var,
                font=self.default_font
            )
            self.status_label.grid(row=0, column=1, sticky=tk.W)
            
            print("[UI] 用户界面创建完成")
            
        except Exception as e:
            error_msg = f"创建用户界面时出错\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            print(f"[UI] 错误: {error_msg}")
            self.show_error("界面初始化错误", error_msg)
            raise
        
    def log(self, message):
        """添加日志消息"""
        try:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            # 如果日志写入失败，至少尝试打印
            print(f"日志: {message}")
            print(f"日志写入错误: {e}")
        
    def select_video_files(self):
        """选择视频文件"""
        try:
            files = filedialog.askopenfilenames(
                title="选择视频 M4S 文件",
                filetypes=[("M4S 文件", "*.m4s"), ("所有文件", "*.*")]
            )
            if files:
                self.video_files = list(files)
                self.video_listbox.delete(0, tk.END)
                for file in self.video_files:
                    self.video_listbox.insert(tk.END, Path(file).name)
                self.log(f"已选择 {len(self.video_files)} 个视频文件")
        except Exception as e:
            self.show_error("文件选择错误", f"选择视频文件时出错\n错误: {str(e)}")
            
    def select_audio_files(self):
        """选择音频文件"""
        try:
            files = filedialog.askopenfilenames(
                title="选择音频 M4S 文件",
                filetypes=[("M4S 文件", "*.m4s"), ("所有文件", "*.*")]
            )
            if files:
                self.audio_files = list(files)
                self.audio_listbox.delete(0, tk.END)
                for file in self.audio_files:
                    self.audio_listbox.insert(tk.END, Path(file).name)
                self.log(f"已选择 {len(self.audio_files)} 个音频文件")
        except Exception as e:
            self.show_error("文件选择错误", f"选择音频文件时出错\n错误: {str(e)}")
            
    def clear_video_files(self):
        """清空视频文件列表"""
        try:
            self.video_files = []
            self.video_listbox.delete(0, tk.END)
            self.log("已清空视频文件列表")
        except Exception as e:
            self.show_error("操作错误", f"清空视频文件列表时出错\n错误: {str(e)}")
        
    def clear_audio_files(self):
        """清空音频文件列表"""
        try:
            self.audio_files = []
            self.audio_listbox.delete(0, tk.END)
            self.log("已清空音频文件列表")
        except Exception as e:
            self.show_error("操作错误", f"清空音频文件列表时出错\n错误: {str(e)}")
        
    def select_output_dir(self):
        """选择输出目录"""
        try:
            dir_path = filedialog.askdirectory(title="选择输出目录")
            if dir_path:
                self.output_dir = dir_path
                self.output_dir_var.set(dir_path)
                self.log(f"输出目录: {dir_path}")
        except Exception as e:
            self.show_error("目录选择错误", f"选择输出目录时出错\n错误: {str(e)}")
            
    def merge_video(self):
        """合并视频文件"""
        if not self.video_files:
            messagebox.showwarning("警告", "请先选择视频文件！")
            return
        if not self.output_dir:
            messagebox.showwarning("警告", "请先选择输出目录！")
            return
            
        self.progress_bar.start()
        self.progress_var.set("正在合并视频...")
        
        def process():
            try:
                self.root.after(0, lambda: self.log("开始合并视频文件..."))
                output_file = self.processor.merge_video_segments(
                    self.video_files, 
                    self.output_dir
                )
                self.root.after(0, lambda: self.on_process_complete(
                    f"视频合并完成: {output_file}", True
                ))
            except Exception as e:
                error_msg = str(e)
                error_detail = traceback.format_exc()
                self.root.after(0, lambda: self.log(f"错误: {error_msg}"))
                self.root.after(0, lambda: self.log(f"详细信息:\n{error_detail}"))
                self.root.after(0, lambda: self.on_process_complete(
                    f"视频合并失败: {error_msg}", False
                ))
                
        threading.Thread(target=process, daemon=True).start()
        
    def merge_audio(self):
        """合并音频文件"""
        if not self.audio_files:
            messagebox.showwarning("警告", "请先选择音频文件！")
            return
        if not self.output_dir:
            messagebox.showwarning("警告", "请先选择输出目录！")
            return
            
        self.progress_bar.start()
        self.progress_var.set("正在合并音频...")
        
        def process():
            try:
                self.root.after(0, lambda: self.log("开始合并音频文件..."))
                output_file = self.processor.merge_audio_segments(
                    self.audio_files,
                    self.output_dir
                )
                self.root.after(0, lambda: self.on_process_complete(
                    f"音频合并完成: {output_file}", True
                ))
            except Exception as e:
                error_msg = str(e)
                error_detail = traceback.format_exc()
                self.root.after(0, lambda: self.log(f"错误: {error_msg}"))
                self.root.after(0, lambda: self.log(f"详细信息:\n{error_detail}"))
                self.root.after(0, lambda: self.on_process_complete(
                    f"音频合并失败: {error_msg}", False
                ))
                
        threading.Thread(target=process, daemon=True).start()
        
    def merge_av_direct(self):
        """合并音频视频（混流）：先合并视频和音频，然后混流"""
        if not self.video_files:
            messagebox.showwarning("警告", "请先选择视频文件！")
            return
        if not self.audio_files:
            messagebox.showwarning("警告", "请先选择音频文件！")
            return
        if not self.output_dir:
            messagebox.showwarning("警告", "请先选择输出目录！")
            return
            
        self.progress_bar.start()
        self.progress_var.set("正在处理...")
        
        def process():
            try:
                self.root.after(0, lambda: self.log("开始合并音频视频（混流）..."))
                self.root.after(0, lambda: self.log(f"合并 {len(self.video_files)} 个视频文件..."))
                self.root.after(0, lambda: self.log(f"合并 {len(self.audio_files)} 个音频文件..."))
                self.root.after(0, lambda: self.log("开始音视频混流..."))
                result = self.processor.process_all(
                    self.video_files,
                    self.audio_files,
                    self.output_dir
                )
                self.root.after(0, lambda: self.on_process_complete(
                    f"混流完成: {result}", True
                ))
            except Exception as e:
                error_msg = str(e)
                error_detail = traceback.format_exc()
                self.root.after(0, lambda: self.log(f"错误: {error_msg}"))
                self.root.after(0, lambda: self.log(f"详细信息:\n{error_detail}"))
                self.root.after(0, lambda: self.on_process_complete(
                    f"混流失败: {error_msg}", False
                ))
                
        threading.Thread(target=process, daemon=True).start()
        
    def on_process_complete(self, message, success):
        """处理完成回调"""
        try:
            self.progress_bar.stop()
            self.progress_var.set("就绪" if success else "失败")
            self.log(message)
            if success:
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("错误", message)
        except Exception as e:
            self.log(f"完成回调错误: {str(e)}")
            
    def install_ffmpeg_dialog(self):
        """显示 FFmpeg 安装对话框"""
        try:
            dialog = tk.Toplevel()
            dialog.title("安装 FFmpeg")
            dialog.geometry("500x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                main_frame,
                text="未检测到 FFmpeg",
                font=("Arial", 12, "bold")
            ).pack(pady=(0, 10))
            
            ttk.Label(
                main_frame,
                text="此程序需要 FFmpeg 才能运行。\n请选择安装目录：",
                justify=tk.LEFT
            ).pack(pady=(0, 20))
            
            # 安装目录选择
            dir_frame = ttk.Frame(main_frame)
            dir_frame.pack(fill=tk.X, pady=(0, 10))
            
            self.install_dir_var = tk.StringVar(value=str(Path.home() / "ffmpeg"))
            ttk.Entry(dir_frame, textvariable=self.install_dir_var, width=40).pack(
                side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
            )
            ttk.Button(
                dir_frame,
                text="浏览",
                command=lambda: self.select_install_dir(dialog)
            ).pack(side=tk.LEFT)
            
            # 进度显示
            self.install_progress_var = tk.StringVar(value="")
            ttk.Label(main_frame, textvariable=self.install_progress_var).pack(pady=(10, 5))
            
            self.install_progress_bar = ttk.Progressbar(
                main_frame,
                mode='determinate',
                length=400
            )
            self.install_progress_bar.pack(pady=(0, 20))
            
            # 按钮
            button_frame = ttk.Frame(main_frame)
            button_frame.pack()
            
            ttk.Button(
                button_frame,
                text="安装",
                command=lambda: self.start_install_ffmpeg(dialog)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="取消",
                command=lambda: self.cancel_install(dialog)
            ).pack(side=tk.LEFT, padx=5)
            
            # 绑定关闭事件
            dialog.protocol("WM_DELETE_WINDOW", lambda: self.cancel_install(dialog))
        except Exception as e:
            self.show_error("对话框错误", f"创建安装对话框时出错\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}")
    
    def select_install_dir(self, parent):
        """选择安装目录"""
        try:
            dir_path = filedialog.askdirectory(
                parent=parent,
                title="选择 FFmpeg 安装目录",
                initialdir=self.install_dir_var.get()
            )
            if dir_path:
                self.install_dir_var.set(dir_path)
        except Exception as e:
            self.show_error("目录选择错误", f"选择安装目录时出错\n错误: {str(e)}")
    
    def start_install_ffmpeg(self, dialog):
        """开始安装 FFmpeg"""
        try:
            install_dir = Path(self.install_dir_var.get())
            
            if not install_dir.parent.exists():
                messagebox.showerror("错误", "所选目录的父目录不存在！")
                return
            
            # 禁用按钮
            for widget in dialog.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.config(state=tk.DISABLED)
            
            def install():
                try:
                    def progress_callback(stage, current, total, message):
                        if total > 0:
                            # 切换到确定模式并设置进度
                            self.root.after(0, lambda: self.install_progress_bar.config(mode='determinate', maximum=100))
                            percent = int((current / total) * 100)
                            self.root.after(0, lambda: self.install_progress_bar.config(value=percent))
                        elif stage == 'download' and total < 0:
                            # 下载阶段，如果不知道总大小，使用不确定模式
                            self.root.after(0, lambda: self.install_progress_bar.config(mode='indeterminate'))
                            self.root.after(0, lambda: self.install_progress_bar.start())
                        self.root.after(0, lambda: self.install_progress_var.set(message))
                    
                    bin_dir, path_success = FFmpegInstaller.install_ffmpeg(
                        install_dir,
                        progress_callback
                    )
                    
                    if path_success:
                        msg = f"FFmpeg 安装成功！\n安装位置: {bin_dir}\n已自动添加到 PATH 环境变量。\n\n请重启程序以使更改生效。"
                    else:
                        msg = f"FFmpeg 安装成功！\n安装位置: {bin_dir}\n\n注意：未能自动添加到 PATH，请手动添加以下路径到系统 PATH：\n{bin_dir}\n\n然后重启程序。"
                    
                    self.root.after(0, lambda: self.on_install_complete(dialog, msg, True))
                    
                except Exception as e:
                    error_msg = f"安装失败: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
                    self.root.after(0, lambda: self.on_install_complete(dialog, error_msg, False))
            
            threading.Thread(target=install, daemon=True).start()
        except Exception as e:
            self.show_error("安装启动错误", f"启动 FFmpeg 安装时出错\n错误: {str(e)}")
    
    def on_install_complete(self, dialog, message, success):
        """安装完成回调"""
        try:
            if success:
                messagebox.showinfo("安装完成", message)
                dialog.destroy()
                self.root.destroy()  # 关闭程序，提示用户重启
            else:
                messagebox.showerror("安装失败", message)
                # 重新启用按钮
                for widget in dialog.winfo_children():
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.config(state=tk.NORMAL)
        except Exception as e:
            self.log(f"安装完成回调错误: {str(e)}")
    
    def cancel_install(self, dialog):
        """取消安装"""
        try:
            if messagebox.askokcancel("确认", "取消安装将退出程序。是否继续？"):
                dialog.destroy()
                self.root.destroy()
        except Exception as e:
            self.log(f"取消安装错误: {str(e)}")
    
    def run(self):
        """运行应用程序"""
        try:
            print("[GUI] 准备启动事件循环...")
            print(f"[GUI] 窗口对象: {self.root}")
            print(f"[GUI] 窗口标题: {self.root.title()}")
            
            # 确保窗口可见
            try:
                is_viewable = self.root.winfo_viewable()
                print(f"[GUI] 窗口可见性: {is_viewable}")
                if not is_viewable:
                    print("[GUI] 窗口不可见，尝试显示...")
                    self.root.deiconify()
                    self.root.update()
                    print(f"[GUI] 显示后可见性: {self.root.winfo_viewable()}")
            except Exception as e:
                print(f"[GUI] 检查窗口可见性时出错: {e}")
            
            # 强制更新窗口
            try:
                print("[GUI] 更新窗口...")
                self.root.update_idletasks()
                self.root.update()
                print("[GUI] 窗口更新完成")
            except Exception as e:
                print(f"[GUI] 更新窗口时出错: {e}")
            
            print("[GUI] 调用 mainloop() 启动事件循环...")
            print("[GUI] 注意: 如果程序在这里卡住，可能是 tkinter 事件循环的问题")
            print("[GUI] 请检查是否有窗口弹出（可能被其他窗口遮挡）")
            
            # 尝试在后台线程中检查窗口状态
            import threading
            def check_window():
                import time
                time.sleep(2)
                try:
                    if hasattr(self.root, 'winfo_exists') and self.root.winfo_exists():
                        print(f"[GUI-后台] 窗口仍然存在，可见性: {self.root.winfo_viewable()}")
                except:
                    pass
            
            check_thread = threading.Thread(target=check_window, daemon=True)
            check_thread.start()
            
            self.root.mainloop()
            print("[GUI] 事件循环已退出")
        except Exception as e:
            error_msg = f"程序运行时出错\n错误: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
            print(f"[GUI] 运行错误: {error_msg}")
            self.show_error("运行错误", error_msg)

