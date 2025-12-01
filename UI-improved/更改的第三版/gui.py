#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理工具 - GUI 界面 (Final Version)
1. 字体: Microsoft YaHei UI
2. 布局: 顶部左右对称 (深色模式/语言切换)
3. 窗口: 960x840 (增高20%)
4. 图标: 仅保留 Logo，移除按钮图标
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import traceback
import os
import sys
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:
    import tkinter.messagebox
    root = tk.Tk()
    root.withdraw()
    tkinter.messagebox.showerror("Error", "缺少依赖: 请运行 pip install customtkinter")
    sys.exit(1)

try:
    from m4s_processor import M4SProcessor
    from ffmpeg_installer import FFmpegInstaller
except ImportError:
    # 简单的错误处理，防止直接闪退
    sys.exit(1)

# --- 翻译字典 ---
TRANS = {
    "en": {
        "title": "M4S Merger GUI",
        "subtitle": "Merge segmented .m4s streams instantly.",
        "video_title": "Video Stream (.m4s)",
        "audio_title": "Audio Stream (.m4s)",
        "placeholder": "Click to select files...",
        "select_btn": "Select Files",
        "output_label": "Output:",
        "output_auto": "Auto (Current Directory)",
        "change_path": "Change Path",
        "format_hint": "Format: Copy Codec (Fast)",
        "btn_merge": "Merge Files",
        "btn_video": "Video Only",
        "btn_audio": "Audio Only",
        "log_title": "PROCESS LOGS",
        "ready": "System initialized. Ready.",
        "success": "Success",
        "error": "Error",
        "saved": "File saved to:",
        "processing": "Processing...",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "lang_btn": "English",
        # 安装相关
        "install_title": "Install FFmpeg",
        "install_desc": "FFmpeg is required for processing media.",
        "install_path": "Install Path:",
        "install_browse": "Browse",
        "install_start": "Install Now",
        "install_status_ready": "Ready to install",
        "install_status_down": "Downloading...",
        "install_status_ext": "Extracting...",
        "install_done": "Installation complete! Please restart."
    },
    "zh": {
        "title": "M4S 合并工具",
        "subtitle": "快速合并分段的 .m4s 音视频流",
        "video_title": "视频流 (.m4s)",
        "audio_title": "音频流 (.m4s)",
        "placeholder": "点击选择文件...",
        "select_btn": "选择文件",
        "output_label": "输出路径:",
        "output_auto": "自动 (当前目录)",
        "change_path": "更改路径",
        "format_hint": "格式: 复制流 (无损极速)",
        "btn_merge": "开始合并",
        "btn_video": "仅视频",
        "btn_audio": "仅音频",
        "log_title": "处理日志",
        "ready": "系统已就绪。",
        "success": "成功",
        "error": "错误",
        "saved": "文件已保存至:",
        "processing": "处理中...",
        "theme_dark": "深色模式",
        "theme_light": "浅色模式",
        "lang_btn": "中文",
        # 安装相关
        "install_title": "安装 FFmpeg",
        "install_desc": "本工具需要 FFmpeg 组件才能运行。",
        "install_path": "安装位置:",
        "install_browse": "浏览",
        "install_start": "立即安装",
        "install_status_ready": "准备安装",
        "install_status_down": "正在下载...",
        "install_status_ext": "正在解压...",
        "install_done": "安装完成！请重启程序。"
    }
}

# 颜色配置 (适应深浅模式)
COLORS = {
    "bg": ("#f1f5f9", "#020617"),          # 浅灰 / 深蓝黑
    "card": ("#ffffff", "#0f172a"),        # 白 / 深蓝灰
    "card_border": ("#cbd5e1", "#1e293b"), # 边框
    "input_bg": ("#e2e8f0", "#1e293b"),    # 输入框背景
    "text_main": ("#0f172a", "#f8fafc"),   # 主文字
    "text_body": ("#64748b", "#94a3b8"),   # 次要文字
    "brand": ("#0ea5e9", "#0ea5e9"),       # 品牌蓝
    "brand_hover": ("#0284c7", "#0284c7"), # 悬停蓝
    "terminal_bg": ("#000000", "#000000"), # 日志背景(黑)
    "terminal_fg": ("#22c55e", "#22c55e")  # 日志文字(绿)
}

class M4SProcessorApp:
    def __init__(self):
        # 默认外观
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.lang = "zh"
        self.current_theme = "Dark"
        self.t = TRANS[self.lang]
        
        self.root.title("M4S Merger GUI")
        
        # 窗口尺寸 (960x840)
        self.root.geometry("960x840") 
        self.root.minsize(900, 700)
        
        self.root.configure(fg_color=COLORS["bg"])
        
        # --- 字体配置 (微软雅黑 UI) ---
        FONT_NAME = "Microsoft YaHei UI"
        self.font_title = (FONT_NAME, 32, "bold") 
        self.font_subtitle = (FONT_NAME, 16)
        self.font_header = (FONT_NAME, 16, "bold")
        self.font_body = (FONT_NAME, 15)
        self.font_btn = (FONT_NAME, 16, "bold")
        self.font_mono = ("Consolas", 13)
        
        self.video_files = []
        self.audio_files = []
        self.output_dir = ""
        self.is_processing = False
        
        # UI 引用字典
        self.ui_refs = {} 

        # 检查 FFmpeg
        if not M4SProcessor.check_ffmpeg_available():
            self.root.withdraw()
            self.install_ffmpeg_dialog()
        else:
            self.processor = M4SProcessor(check_ffmpeg=False)
            self.setup_ui()

    def toggle_language(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.t = TRANS[self.lang]
        self.refresh_text()

    def toggle_theme(self):
        if self.current_theme == "Dark":
            ctk.set_appearance_mode("Light")
            self.current_theme = "Light"
        else:
            ctk.set_appearance_mode("Dark")
            self.current_theme = "Dark"
        self.refresh_text()

    def refresh_text(self):
        """刷新所有文本"""
        t = self.t
        # 顶部按钮
        theme_text = t["theme_dark"] if self.current_theme == "Dark" else t["theme_light"]
        self.ui_refs["theme_btn"].configure(text=theme_text)
        self.ui_refs["lang_btn"].configure(text=t["lang_btn"])
        
        # 标题
        self.ui_refs["title"].configure(text=t["title"])
        self.ui_refs["subtitle"].configure(text=t["subtitle"])
        
        # 模块标题
        self.ui_refs["video_header"].configure(text=t["video_title"])
        self.ui_refs["audio_header"].configure(text=t["audio_title"])
        
        # 按钮文字
        self.ui_refs["video_sel_btn"].configure(text=t["select_btn"])
        self.ui_refs["audio_sel_btn"].configure(text=t["select_btn"])
        self.ui_refs["change_path_btn"].configure(text=t["change_path"])
        self.ui_refs["btn_merge"].configure(text=t["btn_merge"])
        self.ui_refs["btn_v"].configure(text=t["btn_video"])
        self.ui_refs["btn_a"].configure(text=t["btn_audio"])
        
        # 标签
        self._update_path_label()
        self.ui_refs["format_hint"].configure(text=t["format_hint"])
        self.ui_refs["log_title"].configure(text=f">_ {t['log_title']}")
        
        # 刷新占位符
        if not self.video_files: self._show_placeholder(self.video_list_ui, self.select_video_files)
        if not self.audio_files: self._show_placeholder(self.audio_list_ui, self.select_audio_files)

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # --- 顶部栏 ---
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 20))
        
        # 左侧：主题切换 (纯文字)
        self.ui_refs["theme_btn"] = ctk.CTkButton(
            top_bar, text="", width=80, height=32,
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"],
            text_color=COLORS["text_main"], font=self.font_body, 
            command=self.toggle_theme
        )
        self.ui_refs["theme_btn"].pack(side="left", anchor="n")

        # 右侧：语言切换 (纯文字)
        self.ui_refs["lang_btn"] = ctk.CTkButton(
            top_bar, text="", width=80, height=32,
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"],
            text_color=COLORS["text_main"], font=self.font_body, 
            command=self.toggle_language
        )
        self.ui_refs["lang_btn"].pack(side="right", anchor="n")

        # 中间：Logo 和 标题
        center_head = ctk.CTkFrame(top_bar, fg_color="transparent")
        center_head.pack(side="top", anchor="center")

        icon_box = ctk.CTkFrame(center_head, fg_color=COLORS["card_border"], corner_radius=12, width=48, height=48)
        icon_box.pack(pady=(0, 5))
        icon_box.pack_propagate(False)
        # 这里的 Emoji 可以保留作为 Logo，或者也去掉
        ctk.CTkLabel(icon_box, text="📚", font=("Segoe UI Emoji", 24)).place(relx=0.5, rely=0.5, anchor="center")
        
        self.ui_refs["title"] = ctk.CTkLabel(center_head, text="", font=self.font_title, text_color=COLORS["text_main"])
        self.ui_refs["title"].pack()
        self.ui_refs["subtitle"] = ctk.CTkLabel(center_head, text="", font=self.font_subtitle, text_color=COLORS["text_body"])
        self.ui_refs["subtitle"].pack()

        # --- 主卡片 ---
        main_card = ctk.CTkFrame(self.main_frame, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["card_border"])
        main_card.pack(fill="both", expand=True, pady=10)

        # 文件区域
        files_grid = ctk.CTkFrame(main_card, fg_color="transparent")
        files_grid.pack(fill="x", padx=20, pady=20)
        files_grid.grid_columnconfigure(0, weight=1)
        files_grid.grid_columnconfigure(1, weight=1)

        self._create_drop_zone(files_grid, "video", 0, 0)
        self._create_drop_zone(files_grid, "audio", 0, 1)

        # --- 控制区 ---
        control_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 路径栏
        path_frame = ctk.CTkFrame(control_frame, fg_color=COLORS["input_bg"], corner_radius=8, height=45)
        path_frame.pack(fill="x", pady=(0, 20))
        path_frame.pack_propagate(False)
        
        self.ui_refs["output_label"] = ctk.CTkLabel(path_frame, text="", text_color=COLORS["text_body"], font=self.font_body, anchor="w")
        self.ui_refs["output_label"].pack(side="left", padx=15, fill="x", expand=True)
        
        self.ui_refs["change_path_btn"] = ctk.CTkButton(
            path_frame, text="", width=110, height=32,
            fg_color=COLORS["card_border"], hover_color="#94a3b8",
            text_color=COLORS["text_main"],
            font=self.font_body, command=self.select_output_dir
        )
        self.ui_refs["change_path_btn"].pack(side="right", padx=10)

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(control_frame, height=8, corner_radius=4, progress_color=COLORS["brand"], fg_color=COLORS["input_bg"])
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.set(0)

        # 按钮行
        action_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_frame.pack(fill="x")
        
        self.ui_refs["format_hint"] = ctk.CTkLabel(action_frame, text="", text_color=COLORS["text_body"], font=self.font_body)
        self.ui_refs["format_hint"].pack(side="left")

        btn_box = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_box.pack(side="right")
        
        self.ui_refs["btn_merge"] = ctk.CTkButton(
            btn_box, text="", font=self.font_btn, height=45, width=180,
            fg_color=COLORS["brand"], hover_color=COLORS["brand_hover"], 
            text_color="#ffffff",
            command=self.merge_av_direct
        )
        self.ui_refs["btn_merge"].pack(side="right", padx=5)
        
        self.ui_refs["btn_v"] = ctk.CTkButton(
            btn_box, text="", font=self.font_body, height=45, width=110,
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"], 
            text_color=COLORS["text_main"],
            command=self.merge_video
        )
        self.ui_refs["btn_v"].pack(side="right", padx=5)
        
        self.ui_refs["btn_a"] = ctk.CTkButton(
            btn_box, text="", font=self.font_body, height=45, width=110,
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"], 
            text_color=COLORS["text_main"],
            command=self.merge_audio
        )
        self.ui_refs["btn_a"].pack(side="right", padx=5)

        # --- 日志 ---
        self._create_log_viewer(main_card)
        self.refresh_text()

    def _create_drop_zone(self, parent, type_key, row, col):
        container = ctk.CTkFrame(parent, fg_color=COLORS["input_bg"], corner_radius=10)
        container.grid(row=row, column=col, sticky="ew", padx=10, pady=0)
        
        top = ctk.CTkFrame(container, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(15, 5))
        
        lbl = ctk.CTkLabel(top, text="", font=self.font_header, text_color=COLORS["text_main"])
        lbl.pack(side="left")
        self.ui_refs[f"{type_key}_header"] = lbl
        
        cmd_clear = self.clear_video_files if type_key == "video" else self.clear_audio_files
        # 移除图标，改用文字 "x"
        ctk.CTkButton(
            top, text="×", width=30, height=30, fg_color="transparent", 
            hover_color=COLORS["card_border"], text_color=COLORS["text_body"], 
            font=("Arial", 22), command=cmd_clear
        ).pack(side="right")
        
        # 列表
        list_frame = ctk.CTkScrollableFrame(container, height=120, fg_color="transparent", scrollbar_button_color=COLORS["card_border"])
        list_frame.pack(fill="both", expand=True, padx=5)
        
        cmd_add = self.select_video_files if type_key == "video" else self.select_audio_files
        if type_key == "video": self.video_list_ui = list_frame
        else: self.audio_list_ui = list_frame
            
        bot = ctk.CTkFrame(container, fg_color="transparent")
        bot.pack(fill="x", padx=15, pady=15)
        
        btn = ctk.CTkButton(
            bot, text="", fg_color=COLORS["card_border"], hover_color="#94a3b8", 
            text_color=COLORS["text_main"],
            height=36, font=self.font_body, command=cmd_add
        )
        btn.pack(fill="x")
        self.ui_refs[f"{type_key}_sel_btn"] = btn

    def _show_placeholder(self, frame, cmd):
        for w in frame.winfo_children(): w.destroy()
        wrap = ctk.CTkFrame(frame, fg_color="transparent")
        wrap.pack(expand=True, fill="both", pady=15)
        ctk.CTkButton(
            wrap, text=self.t["placeholder"], fg_color="transparent", 
            text_color=COLORS["text_body"], hover=False, font=self.font_body, command=cmd
        ).pack(expand=True)

    def _update_file_list(self, list_ui, files, add_cmd):
        for w in list_ui.winfo_children(): w.destroy()
        if not files:
            self._show_placeholder(list_ui, add_cmd)
            return
        for f in files:
            path = Path(f)
            size_mb = os.path.getsize(f) / 1024 / 1024
            row = ctk.CTkFrame(list_ui, fg_color="transparent")
            row.pack(fill="x", pady=2)
            name = path.name
            if len(name) > 28: name = name[:25] + "..."
            ctk.CTkLabel(row, text=name, text_color=COLORS["text_main"], anchor="w", font=self.font_body).pack(side="left")
            ctk.CTkLabel(row, text=f"{size_mb:.1f} MB", text_color=COLORS["text_body"], font=("Consolas", 12)).pack(side="right")

    def _create_log_viewer(self, parent):
        cont = ctk.CTkFrame(parent, fg_color=COLORS["terminal_bg"], corner_radius=8)
        cont.pack(fill="both", padx=20, pady=(0, 20))
        
        head = ctk.CTkFrame(cont, fg_color="#1e1e1e", corner_radius=8, height=30)
        head.pack(fill="x")
        head.pack_propagate(False)
        
        lbl = ctk.CTkLabel(head, text="", text_color="#64748b", font=("Consolas", 12, "bold"))
        lbl.pack(side="left", padx=10)
        self.ui_refs["log_title"] = lbl
        
        self.log_text = ctk.CTkTextbox(
            cont, height=120, 
            fg_color=COLORS["terminal_bg"], text_color=COLORS["terminal_fg"], 
            font=self.font_mono, activate_scrollbars=True
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.configure(state="disabled")

    def _update_path_label(self):
        prefix = self.t["output_label"]
        val = self.output_dir if self.output_dir else self.t["output_auto"]
        self.ui_refs["output_label"].configure(text=f"{prefix} {val}")

    # --- 逻辑层 ---
    def log(self, message):
        self.log_text.configure(state="normal")
        import datetime
        t_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{t_str}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def select_video_files(self):
        files = filedialog.askopenfilenames(filetypes=[("M4S", "*.m4s"), ("All", "*.*")])
        if files:
            self.video_files = list(files)
            self._update_file_list(self.video_list_ui, self.video_files, self.select_video_files)

    def select_audio_files(self):
        files = filedialog.askopenfilenames(filetypes=[("M4S", "*.m4s"), ("All", "*.*")])
        if files:
            self.audio_files = list(files)
            self._update_file_list(self.audio_list_ui, self.audio_files, self.select_audio_files)

    def clear_video_files(self):
        self.video_files = []
        self._update_file_list(self.video_list_ui, [], self.select_video_files)

    def clear_audio_files(self):
        self.audio_files = []
        self._update_file_list(self.audio_list_ui, [], self.select_audio_files)

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path
            self._update_path_label()

    def _run_task(self, name_key, task_func):
        if self.is_processing: return
        if "video" in name_key.lower() and not self.video_files:
            messagebox.showwarning(self.t["error"], "No Video Files")
            return
        if "audio" in name_key.lower() and not self.audio_files:
            messagebox.showwarning(self.t["error"], "No Audio Files")
            return
        if not self.output_dir: self.output_dir = os.getcwd()

        self.is_processing = True
        self.progress_bar.start()
        self.log(f"{self.t['processing']} ({name_key})")
        
        def run():
            try:
                res = task_func()
                self.root.after(0, lambda: self._on_finish(True, res))
            except Exception as e:
                self.root.after(0, lambda: self._on_finish(False, str(e)))
        threading.Thread(target=run, daemon=True).start()

    def _on_finish(self, success, msg):
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_bar.set(0)
        if success:
            self.log(f"{self.t['success']}! {msg}")
            messagebox.showinfo(self.t["success"], f"{self.t['saved']}\n{msg}")
            try: os.startfile(os.path.dirname(msg))
            except: pass
        else:
            self.log(f"{self.t['error']}: {msg}")
            messagebox.showerror(self.t["error"], msg)

    def merge_video(self): self._run_task("video", lambda: self.processor.merge_video_segments(self.video_files, self.output_dir))
    def merge_audio(self): self._run_task("audio", lambda: self.processor.merge_audio_segments(self.audio_files, self.output_dir))
    def merge_av_direct(self): 
        if not self.video_files or not self.audio_files:
             messagebox.showwarning(self.t["error"], "Need both video and audio files")
             return
        self._run_task("full", lambda: self.processor.process_all(self.video_files, self.audio_files, self.output_dir))

    # --- 完整的安装弹窗逻辑 ---
    def install_ffmpeg_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.t["install_title"])
        dialog.geometry("600x350")
        
        # 居中弹窗
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 300
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 175
        dialog.geometry(f"+{x}+{y}")
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set() # 模态窗口

        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(content, text=self.t["install_title"], font=self.font_title, text_color=COLORS["text_main"]).pack(pady=(0, 10))
        ctk.CTkLabel(content, text=self.t["install_desc"], font=self.font_body, text_color=COLORS["text_body"]).pack(pady=(0, 20))
        
        # 路径选择
        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(path_frame, text=self.t["install_path"], font=self.font_body, text_color=COLORS["text_main"]).pack(side="left")
        
        install_path_var = tk.StringVar(value=str(Path.home() / "ffmpeg"))
        entry = ctk.CTkEntry(path_frame, textvariable=install_path_var, font=self.font_body)
        entry.pack(side="left", fill="x", expand=True, padx=10)
        
        def browse():
            d = filedialog.askdirectory()
            if d: install_path_var.set(d)
        
        ctk.CTkButton(path_frame, text=self.t["install_browse"], width=80, command=browse).pack(side="right")
        
        # 进度条
        progress_bar = ctk.CTkProgressBar(content, height=10)
        progress_bar.pack(fill="x", pady=20)
        progress_bar.set(0)
        
        status_lbl = ctk.CTkLabel(content, text=self.t["install_status_ready"], font=self.font_body, text_color=COLORS["text_body"])
        status_lbl.pack()
        
        # 安装按钮
        def start_install():
            install_btn.configure(state="disabled")
            target_dir = Path(install_path_var.get())
            
            def run():
                try:
                    def cb(stage, curr, total, msg):
                        # 更新UI
                        val = 0
                        if total > 0: val = curr / total
                        self.root.after(0, lambda: progress_bar.set(val))
                        self.root.after(0, lambda: status_lbl.configure(text=msg))
                    
                    FFmpegInstaller.install_ffmpeg(target_dir, cb)
                    
                    self.root.after(0, lambda: status_lbl.configure(text=self.t["install_done"]))
                    self.root.after(0, lambda: messagebox.showinfo("Done", self.t["install_done"]))
                    self.root.after(0, lambda: sys.exit(0)) # 重启
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                    self.root.after(0, lambda: install_btn.configure(state="normal"))
            
            threading.Thread(target=run, daemon=True).start()
            
        install_btn = ctk.CTkButton(content, text=self.t["install_start"], height=40, font=self.font_btn, command=start_install)
        install_btn.pack(pady=20)
        
        self.root.wait_window(dialog)

    def run(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth()//2) - (w//2)
        y = (self.root.winfo_screenheight()//2) - (h//2)
        self.root.geometry(f"+{x}+{y}")
        self.root.mainloop()