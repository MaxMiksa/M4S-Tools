#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理工具 - GUI 界面 (Final Perfect Version)
修复: 弹窗语言跟随、按钮逻辑、启动阶段双语提示
更新: UI圆角修复、按钮位置交换、分步日志、对齐调整
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import traceback
import os
import sys
from pathlib import Path

# --- 启动阶段异常双语提示 ---
try:
    import customtkinter as ctk
except ImportError:
    import tkinter.messagebox
    root = tk.Tk()
    root.withdraw()
    tkinter.messagebox.showerror(
        "Error / 错误", 
        "Missing dependency / 缺少必要依赖:\n\nPlease run / 请运行:\npip install customtkinter"
    )
    sys.exit(1)

try:
    from m4s_processor import M4SProcessor
    from ffmpeg_installer import FFmpegInstaller
except ImportError:
    sys.exit(1)

# --- 翻译字典 ---
TRANS = {
    "en": {
        "title": "M4S Merger Tool",
        "subtitle": "Merge segmented .m4s streams instantly.",
        "video_title": " Video Stream (.m4s)",
        "audio_title": " Audio Stream (.m4s)",
        "placeholder": "Click to select files...",
        "select_btn": "Select Files",
        "output_label": "Output:",
        "output_auto": "Desktop (Default)",
        "change_path": "Change Path",
        "format_hint": "Format: Copy Codec (Fast)",
        
        # 按钮文案
        "btn_merge": "Mux (Merge all into one file)",
        "btn_video": "Merge Video",
        "btn_audio": "Merge Audio",
        
        # 提示语
        "multi_hint": "💡 Tip: Use Ctrl+Click to select multiple files in the specific order you want them merged.",
        
        # 日志文案
        "log_title": "PROCESS LOGS",
        "log_step_v_end": "视频合并完成。| Video merge completed.",
        "log_step_a_end": "音频合并完成。| Audio merge completed. ",
        "log_step_m_start": "开始混流... | Starting muxing process...",
        
        "theme_dark": "Dark",
        "theme_light": "Light",
        "lang_btn": "中文", 
        
        # 运行时提示
        "processing": "处理中... | Processing...",
        "success": "成功 | Success",
        "error": "Error",
        "saved": "File saved to:",
        "no_video": "Please select video files first.",
        "no_audio": "Please select audio files first.",
        "need_both": "Need both video and audio files.",
    },
    "zh": {
        "title": "M4S 合并工具",
        "subtitle": "一键合并分段的 .m4s 音视频文件",
        "video_title": " 视频文件 (.m4s)",
        "audio_title": " 音频文件 (.m4s)",
        "placeholder": "点击选择文件...",
        "select_btn": "选择文件",
        "output_label": "输出路径:",
        "output_auto": "桌面 (默认)",
        "change_path": "更改路径",
        "format_hint": "格式: 复制流 (无损极速)",
        
        # 按钮文案
        "btn_merge": "混流(合并所有音视频成1个文件)",
        "btn_video": "仅合并视频",
        "btn_audio": "仅合并音频",
        
        # 提示语
        "multi_hint": "💡 提示：在选择文件时按住 Ctrl 键依次点击，软件将按照您选择的先后顺序进行合并。",
        
        # 日志文案
        "log_title": "处理日志",
        "log_step_v_end": "视频合并完成。| Video merge completed.",
        "log_step_a_end": "音频合并完成。| Audio merge completed. ",
        "log_step_m_start": "开始混流... | Starting muxing process...",
        
        "theme_dark": "深色模式",
        "theme_light": "浅色模式",
        "lang_btn": "English",
        
        # 运行时提示
        "processing": "处理中... | Processing...",
        "success": "成功 | Success",
        "error": "错误",
        "saved": "文件已保存至:",
        "no_video": "请先选择视频文件。",
        "no_audio": "请先选择音频文件。",
        "need_both": "需要同时选择视频和音频文件。",
    }
}

# 颜色配置
COLORS = {
    "bg": ("#f1f5f9", "#020617"),          
    "card": ("#ffffff", "#0f172a"),        
    "card_border": ("#cbd5e1", "#1e293b"), 
    "input_bg": ("#e2e8f0", "#1e293b"),    
    "text_main": ("#0f172a", "#f8fafc"),   
    "text_body": ("#64748b", "#94a3b8"),   
    "brand": ("#0ea5e9", "#0ea5e9"),       
    "brand_hover": ("#0284c7", "#0284c7"), 
    "terminal_bg": ("#000000", "#000000"), 
    "terminal_fg": ("#22c55e", "#22c55e")  
}

class M4SProcessorApp:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.lang = "zh" 
        self.current_theme = "Dark"
        self.t = TRANS[self.lang]
        
        self.root.title("M4S Merger GUI")
        self.root.geometry("860x930") 
        self.root.minsize(860, 700)
        self.root.configure(fg_color=COLORS["bg"])
        
        # 字体配置
        FONT_NAME = "Microsoft YaHei UI"
        self.font_title = (FONT_NAME, 32, "bold") 
        self.font_subtitle = (FONT_NAME, 16)
        self.font_header = (FONT_NAME, 16, "bold")
        self.font_body = (FONT_NAME, 15)
        self.font_small = (FONT_NAME, 14)
        self.font_btn = (FONT_NAME, 16, "bold")
        self.font_mono = ("Consolas", 14)
        
        self.video_files = []
        self.audio_files = []
        self.output_dir = self._get_default_output_dir()
        self.is_processing = False
        
        self.ui_refs = {} 

        # ⭐ 关键修改：先启动主窗口，然后延迟检查 FFmpeg
        self.root.after(100, self.check_and_setup)

    def check_and_setup(self):
        """检查 FFmpeg 并设置 UI"""
        if not M4SProcessor.check_ffmpeg_available():
            print("[安装/Install] FFmpeg 未安装，显示安装对话框 / FFmpeg not installed, showing installation dialog")
            self.install_ffmpeg_dialog()
        else:
            print("[初始化/Init] FFmpeg 已安装，初始化处理器 / FFmpeg installed, initializing processor")
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
        """刷新所有界面文本"""
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
        
        # 标签和提示
        self._update_path_label()
        self.ui_refs["format_hint"].configure(text=t["format_hint"])
        self.ui_refs["multi_hint"].configure(text=t["multi_hint"])
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
        
        # 左侧：主题切换
        self.ui_refs["theme_btn"] = ctk.CTkButton(
            top_bar, text="", width=100, height=40,
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"],
            text_color=COLORS["text_main"], font=self.font_body, 
            command=self.toggle_theme
        )
        self.ui_refs["theme_btn"].pack(side="left", anchor="n")

        # 右侧：语言切换
        self.ui_refs["lang_btn"] = ctk.CTkButton(
            top_bar, text="", width=100, height=40,
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"],
            text_color=COLORS["text_main"], font=self.font_body, 
            command=self.toggle_language
        )
        self.ui_refs["lang_btn"].pack(side="right", anchor="n")

        # 中间：Logo 和 标题
        center_head = ctk.CTkFrame(top_bar, fg_color="transparent")
        center_head.pack(side="top", anchor="center")

        icon_box = ctk.CTkFrame(center_head, fg_color=COLORS["card_border"], corner_radius=12, width=50, height=50)
        icon_box.pack(pady=(0, 8))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="📚", font=("Segoe UI Emoji", 24)).place(relx=0.5, rely=0.5, anchor="center")
        
        self.ui_refs["title"] = ctk.CTkLabel(center_head, text="", font=self.font_title, text_color=COLORS["text_main"])
        self.ui_refs["title"].pack()
        self.ui_refs["subtitle"] = ctk.CTkLabel(center_head, text="", font=self.font_subtitle, text_color=COLORS["text_body"])
        self.ui_refs["subtitle"].pack()

        # --- 主卡片 ---
        main_card = ctk.CTkFrame(self.main_frame, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["card_border"])
        main_card.pack(fill="both", expand=True, pady=10)

        # 文件区域 (修改：padx=10，对齐更准确)
        files_grid = ctk.CTkFrame(main_card, fg_color="transparent")
        files_grid.pack(fill="x", padx=10, pady=(20,10))
        files_grid.grid_columnconfigure(0, weight=1)
        files_grid.grid_columnconfigure(1, weight=1)

        self._create_drop_zone(files_grid, "video", 0, 0)
        self._create_drop_zone(files_grid, "audio", 0, 1)

        # --- 控制区 ---
        control_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 新增：合并顺序提示语 (修改：pady=(10, 15)，垂直居中)
        self.ui_refs["multi_hint"] = ctk.CTkLabel(
            control_frame, text="", text_color=COLORS["text_body"], 
            font=self.font_body, anchor="w"
        )
        self.ui_refs["multi_hint"].pack(fill="x", pady=(0, 15), padx=5)

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
        self.ui_refs["format_hint"].pack(side="left", padx=6, pady=(0, 5))

        btn_box = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_box.pack(side="right")
        
        # 修改：位置交换，先 pack 混流(右)，再 pack 音频(中)，最后 pack 视频(左)
        self.ui_refs["btn_merge"] = ctk.CTkButton(
            btn_box, text="", font=self.font_btn, height=45, width=260, 
            fg_color=COLORS["brand"], hover_color=COLORS["brand_hover"], 
            text_color="#ffffff",
            command=self.merge_av_direct
        )
        self.ui_refs["btn_merge"].pack(side="right", padx=5)
        
        # 修改：位置交换，现在 Audio 按钮在混流按钮左边
        self.ui_refs["btn_a"] = ctk.CTkButton(
            btn_box, text="", font=self.font_body, height=45, width=120, # 宽度增加到 140
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"], 
            text_color=COLORS["text_main"],
            command=self.merge_audio
        )
        self.ui_refs["btn_a"].pack(side="right", padx=5)

        # 修改：位置交换，现在 Video 按钮在最左边 (视觉上)
        self.ui_refs["btn_v"] = ctk.CTkButton(
            btn_box, text="", font=self.font_body, height=45, width=120, # 宽度增加到 140
            fg_color=COLORS["input_bg"], hover_color=COLORS["card_border"], 
            text_color=COLORS["text_main"],
            command=self.merge_video
        )
        self.ui_refs["btn_v"].pack(side="right", padx=5)

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
        ctk.CTkButton(
            top, text="×", width=30, height=30, fg_color="transparent", 
            hover_color=COLORS["card_border"], text_color=COLORS["text_body"], 
            font=("Arial", 22), command=cmd_clear
        ).pack(side="right")
        
        # 列表
        list_frame = ctk.CTkScrollableFrame(container, height=90, fg_color="transparent", scrollbar_button_color=COLORS["card_border"])
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
        wrap.pack(expand=True, fill="both", pady=(90,0))
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
            if len(name) > 45: name = name[:42] + "..."
            ctk.CTkLabel(row, text=name, text_color=COLORS["text_main"], anchor="w", font=self.font_body).pack(side="left")
            ctk.CTkLabel(row, text=f"{size_mb:.1f} MB", text_color=COLORS["text_body"], font=("Consolas", 12)).pack(side="right")

    def _create_log_viewer(self, parent):
        # 修改：日志框背景纯黑，统一圆角
        cont = ctk.CTkFrame(parent, fg_color=COLORS["terminal_bg"], corner_radius=8)
        cont.pack(fill="both", padx=20, pady=(0, 20))
        
        # 修改：Header背景透明，使顶部圆角显示正常
        head = ctk.CTkFrame(cont, fg_color="transparent", height=30)
        head.pack(fill="x")
        head.pack_propagate(False)
        
        lbl = ctk.CTkLabel(head, text="", text_color="#64748b", font=("Consolas", 12, "bold"))
        lbl.pack(side="left", padx=10, pady=(5,0))
        self.ui_refs["log_title"] = lbl
        
        self.log_text = ctk.CTkTextbox(
            cont, height=120, 
            fg_color=COLORS["terminal_bg"], text_color=COLORS["terminal_fg"], 
            font=self.font_mono, activate_scrollbars=True, corner_radius=6
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.log_text.configure(state="disabled")

    def _get_default_output_dir(self) -> str:
        """Return the user's Desktop path when available, otherwise fallback to CWD."""
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return str(desktop)
        return os.getcwd()

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
            messagebox.showwarning(self.t["error"], self.t["no_video"])
            return
        if "audio" in name_key.lower() and not self.audio_files:
            messagebox.showwarning(self.t["error"], self.t["no_audio"])
            return
            
        if not self.output_dir:
            self.output_dir = self._get_default_output_dir()
            self._update_path_label()

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
             messagebox.showwarning(self.t["error"], self.t["need_both"])
             return
             
        # 修改：分步处理并记录日志
        def full_task():
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                if len(self.video_files) > 1:
                    v_path = self.processor.merge_video_segments(
                        self.video_files, temp_dir, output_name="temp_video.mp4"
                    )
                    self.root.after(0, lambda: self.log(self.t["log_step_v_end"]))
                else:
                    v_path = self.video_files[0]
                
                if len(self.audio_files) > 1:
                    a_path = self.processor.merge_audio_segments(
                        self.audio_files, temp_dir, output_name="temp_audio.mp4"
                    )
                    self.root.after(0, lambda: self.log(self.t["log_step_a_end"]))
                else:
                    a_path = self.audio_files[0]
                
                self.root.after(0, lambda: self.log(self.t["log_step_m_start"]))
                final_path = self.processor.merge_av(v_path, a_path, self.output_dir)
                return final_path

        self._run_task("full", full_task)

    # --- 安装弹窗 (强制双语，因为此时用户无法切换语言) ---
    def install_ffmpeg_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Install FFmpeg / 安装 FFmpeg")
        dialog.geometry("600x350")
        
        # 居中显示
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 300
        y = (self.root.winfo_screenheight() // 2) - 175
        dialog.geometry(f"+{x}+{y}")
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set() 

        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(content, text="Install FFmpeg / 安装 FFmpeg", 
                    font=self.font_title, text_color=COLORS["text_main"]).pack(pady=(0, 10))
        ctk.CTkLabel(content, text="FFmpeg is required. / 本工具需要 FFmpeg 组件。", 
                    font=self.font_body, text_color=COLORS["text_body"]).pack(pady=(0, 20))
        
        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(path_frame, text="Path / 路径:", 
                    font=self.font_body, text_color=COLORS["text_main"]).pack(side="left")
        
        install_path_var = tk.StringVar(value=str(Path.home() / "ffmpeg"))
        entry = ctk.CTkEntry(path_frame, textvariable=install_path_var, font=self.font_body)
        entry.pack(side="left", fill="x", expand=True, padx=10)
        
        def browse():
            d = filedialog.askdirectory()
            if d: install_path_var.set(d)
        
        ctk.CTkButton(path_frame, text="Browse / 浏览", width=80, command=browse).pack(side="right")
        
        progress_bar = ctk.CTkProgressBar(content, height=10)
        progress_bar.pack(fill="x", pady=20)
        progress_bar.set(0)
        
        status_lbl = ctk.CTkLabel(content, text="Ready / 准备就绪", 
                                font=self.font_body, text_color=COLORS["text_body"])
        status_lbl.pack()
        
        def start_install():
            print("[安装/Install] 开始安装 FFmpeg... / Starting FFmpeg installation...")
            install_btn.configure(state="disabled")
            target_dir = Path(install_path_var.get())
            
            def run():
                try:
                    def cb(stage, curr, total, msg):
                        # ⭐ 修改：使用线程安全的方式更新 UI
                        val = 0
                        if total > 0: 
                            val = curr / total
                        
                        # 使用 dialog 而不是 self.root
                        dialog.after(0, lambda v=val, m=msg: update_ui(v, m))
                    
                    def update_ui(val, msg):
                        """在主线程中更新 UI"""
                        try:
                            progress_bar.set(val)
                            status_lbl.configure(text=msg)
                            print(f"[安装进度/Progress] {msg}")
                        except Exception as e:
                            print(f"[UI更新错误/UI Update Error] {e}")
                    
                    print(f"[安装/Install] 目标目录 / Target directory: {target_dir}")
                    FFmpegInstaller.install_ffmpeg(target_dir, cb)
                    
                    dialog.after(0, lambda: status_lbl.configure(text="Complete! / 完成!"))
                    dialog.after(0, lambda: show_success_and_restart(dialog))
                    print("[安装/Install] 安装完成 / Installation completed")
                    
                except Exception as e:
                    error_msg = f"安装失败 / Installation failed:\n{str(e)}"
                    print(f"[错误/Error] {error_msg}")
                    print(f"[错误详情/Error Details] {traceback.format_exc()}")
                    dialog.after(0, lambda: show_error_and_enable(error_msg))
            
            def show_success_and_restart(dlg):
                messagebox.showinfo("Done", 
                                "Installation complete. Please restart.\n安装完成,请重启程序。",
                                parent=dlg)
                sys.exit(0)
            
            def show_error_and_enable(msg):
                messagebox.showerror("Error", msg, parent=dialog)
                install_btn.configure(state="normal")
            
            print("[安装/Install] 启动安装线程 / Starting installation thread...")
            threading.Thread(target=run, daemon=True).start()
        
        install_btn = ctk.CTkButton(
            content, 
            text="Install Now / 立即安装", 
            height=40, 
            font=self.font_btn, 
            command=start_install
        )
        install_btn.pack(pady=20)
        
        dialog.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))


    def run(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth()//2) - (w//2)
        y = (self.root.winfo_screenheight()//2) - (h//2)
        self.root.geometry(f"+{x}+{y}")
        self.root.mainloop()
