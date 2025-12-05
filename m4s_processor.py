#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理核心逻辑
M4S File Processing Core Logic
"""

import subprocess
import os
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class M4SProcessor:
    def __init__(self, ffmpeg_path: str = "ffmpeg", check_ffmpeg: bool = True):
        """
        初始化处理器 / Initialize Processor
        
        Args:
            ffmpeg_path: FFmpeg 可执行文件路径，默认为 "ffmpeg"（需要在 PATH 中）
                         FFmpeg executable path, default is "ffmpeg" (must be in PATH)
            check_ffmpeg: 是否在初始化时检查 FFmpeg，默认为 True
                          Whether to check FFmpeg on initialization, default is True
        """
        self.ffmpeg_path = ffmpeg_path
        if check_ffmpeg:
            self._check_ffmpeg()
    
    @staticmethod
    def check_ffmpeg_available(ffmpeg_path: str = "ffmpeg") -> bool:
        """
        检查 FFmpeg 是否可用（静态方法）
        Check if FFmpeg is available (Static method)
        
        Args:
            ffmpeg_path: FFmpeg 可执行文件路径 / FFmpeg executable path
            
        Returns:
            是否可用 / Available status
        """
        try:
            print(f"[FFmpeg] 检查 FFmpeg (路径: {ffmpeg_path})... / Checking FFmpeg...")
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=5  # 缩短超时时间到5秒 / Shorten timeout to 5s
            )
            print("[FFmpeg] FFmpeg 检查成功，已安装 / FFmpeg check successful, installed")
            return True
        except FileNotFoundError:
            print("[FFmpeg] FFmpeg 未找到（不在 PATH 中） / FFmpeg not found (not in PATH)")
            return False
        except subprocess.TimeoutExpired:
            print("[FFmpeg] FFmpeg 检查超时（可能卡住） / FFmpeg check timed out (might be stuck)")
            return False
        except subprocess.CalledProcessError as e:
            print(f"[FFmpeg] FFmpeg 检查失败（返回码: {e.returncode}） / FFmpeg check failed (Return Code: {e.returncode})")
            return False
        except Exception as e:
            # 记录其他异常 / Log other exceptions
            print(f"[FFmpeg] 检查 FFmpeg 时出错: {e} / Error checking FFmpeg: {e}")
            return False
        
    def _check_ffmpeg(self):
        """检查 FFmpeg 是否可用（实例方法） / Check FFmpeg availability (Instance method)"""
        if not self.check_ffmpeg_available(self.ffmpeg_path):
            raise RuntimeError(
                "未找到 FFmpeg！请确保 FFmpeg 已安装并添加到系统 PATH 环境变量中。\n"
                "FFmpeg not found! Please ensure FFmpeg is installed and added to system PATH.\n\n"
                "下载地址 / Download: https://ffmpeg.org/download.html"
            )
    
    def _create_file_list(self, files: List[str], list_file_path: str):
        """
        创建文件列表文件（用于 FFmpeg concat）
        Create file list for FFmpeg concat
        """
        try:
            with open(list_file_path, 'w', encoding='utf-8') as f:
                for file in files:
                    if not os.path.exists(file):
                        raise FileNotFoundError(f"文件不存在 / File not found: {file}")
                    # 使用绝对路径并转义单引号和特殊字符
                    # Use absolute path and escape single quotes and special characters
                    abs_path = os.path.abspath(file).replace('\\', '/')
                    # 转义单引号（如果路径中包含单引号）
                    # Escape single quotes (if path contains single quotes)
                    abs_path = abs_path.replace("'", "'\\''")
                    f.write(f"file '{abs_path}'\n")
        except Exception as e:
            raise RuntimeError(f"创建文件列表失败 / Failed to create file list: {str(e)}")
    
    def _timestamp_str(self) -> str:
        """Generate a filesystem-friendly timestamp accurate to seconds."""
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def _generate_output_name(self, prefix: str, extension: str = ".mp4") -> str:
        """Compose a default output filename using the expected prefix and timestamp."""
        ext = extension if extension.startswith(".") else f".{extension}"
        return f"{prefix}_{self._timestamp_str()}{ext}"

    def _prepare_stream_for_mux(self, files: List[str], temp_dir: str, is_video: bool) -> str:
        """
        Prepare a stream for muxing: reuse the single original file or merge segments
        inside a temporary directory so that no intermediate artifacts remain in the
        user's chosen output location.
        """
        if not files:
            raise ValueError("Stream list is empty / 流列表为空")
        if len(files) == 1:
            return files[0]
        output_name = "temp_video.mp4" if is_video else "temp_audio.mp4"
        merge_func = self.merge_video_segments if is_video else self.merge_audio_segments
        return merge_func(files, temp_dir, output_name=output_name)
    
    def merge_video_segments(self, video_files: List[str], output_dir: str, output_name: Optional[str] = None) -> str:
        """
        合并视频片段 / Merge video segments
        
        Args:
            video_files: 视频文件路径列表 / List of video file paths
            output_dir: 输出目录 / Output directory
            
        Returns:
            输出文件路径 / Output file path
        """
        if not video_files:
            raise ValueError("视频文件列表为空 / Video file list is empty")
        
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            if not output_name:
                output_name = self._generate_output_name("Merged_Video")
            output_file = output_dir / output_name
            
            # 创建临时文件列表
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                list_file = f.name
                self._create_file_list(video_files, list_file)
            
            try:
                # 使用 FFmpeg 合并视频 / Merge video using FFmpeg
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c", "copy",
                    "-y",  # 覆盖输出文件 / Overwrite output
                    str(output_file)
                ]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=3600  # 1小时超时 / 1 hour timeout
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "未知错误 / Unknown error"
                    raise RuntimeError(f"FFmpeg 合并视频失败 / FFmpeg merge video failed: {error_msg}")
                
                if not output_file.exists():
                    raise RuntimeError(f"输出文件未生成 / Output file not generated: {output_file}")
                
                return str(output_file)
                
            finally:
                # 清理临时文件 / Clean up temp file
                if os.path.exists(list_file):
                    try:
                        os.unlink(list_file)
                    except:
                        pass
        except subprocess.TimeoutExpired:
            raise RuntimeError("视频合并超时（超过1小时），请检查文件大小 / Video merge timed out (over 1 hour), please check file size")
        except Exception as e:
            raise RuntimeError(f"合并视频时出错 / Error merging video: {str(e)}\n详细信息 / Details: {traceback.format_exc()}")
    
    def merge_audio_segments(self, audio_files: List[str], output_dir: str, output_name: Optional[str] = None) -> str:
        """
        合并音频片段 / Merge audio segments
        
        Args:
            audio_files: 音频文件路径列表 / List of audio file paths
            output_dir: 输出目录 / Output directory
            
        Returns:
            输出文件路径 / Output file path
        """
        if not audio_files:
            raise ValueError("音频文件列表为空 / Audio file list is empty")
        
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            if not output_name:
                output_name = self._generate_output_name("Merged_Audio")
            output_file = output_dir / output_name
            
            # 创建临时文件列表
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                list_file = f.name
                self._create_file_list(audio_files, list_file)
            
            try:
                # 使用 FFmpeg 合并音频 / Merge audio using FFmpeg
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c", "copy",
                    "-y",  # 覆盖输出文件
                    str(output_file)
                ]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=3600  # 1小时超时
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "未知错误 / Unknown error"
                    raise RuntimeError(f"FFmpeg 合并音频失败 / FFmpeg merge audio failed: {error_msg}")
                
                if not output_file.exists():
                    raise RuntimeError(f"输出文件未生成 / Output file not generated: {output_file}")
                
                return str(output_file)
                
            finally:
                # 清理临时文件
                if os.path.exists(list_file):
                    try:
                        os.unlink(list_file)
                    except:
                        pass
        except subprocess.TimeoutExpired:
            raise RuntimeError("音频合并超时（超过1小时），请检查文件大小 / Audio merge timed out (over 1 hour), please check file size")
        except Exception as e:
            raise RuntimeError(f"合并音频时出错 / Error merging audio: {str(e)}\n详细信息 / Details: {traceback.format_exc()}")
    
    def merge_av(self, video_file: str, audio_file: str, output_dir: str, output_name: Optional[str] = None) -> str:
        """
        合并音视频 / Merge Audio and Video (Muxing)
        
        Args:
            video_file: 视频文件路径 / Video file path
            audio_file: 音频文件路径 / Audio file path
            output_dir: 输出目录 / Output directory
            output_name: 输出文件名 / Output filename
            
        Returns:
            输出文件路径 / Output file path
        """
        try:
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"视频文件不存在 / Video file not found: {video_file}")
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"音频文件不存在 / Audio file not found: {audio_file}")
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            if not output_name:
                output_name = self._generate_output_name("Muxed_Output")
            output_file = output_dir / output_name
            
            # 使用 FFmpeg 合并音视频
            cmd = [
                self.ffmpeg_path,
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",  # 视频流直接复制，不重新编码 / Copy video stream
                "-c:a", "aac",   # 音频编码为 AAC（兼容性更好）/ Encode audio to AAC
                "-strict", "experimental",
                "-y",  # 覆盖输出文件 / Overwrite output
                str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=3600  # 1小时超时
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "未知错误 / Unknown error"
                raise RuntimeError(f"FFmpeg 混流失败 / FFmpeg muxing failed: {error_msg}")
            
            if not output_file.exists():
                raise RuntimeError(f"输出文件未生成 / Output file not generated: {output_file}")
            
            return str(output_file)
        except subprocess.TimeoutExpired:
            raise RuntimeError("音视频混流超时（超过1小时），请检查文件大小 / Muxing timed out (over 1 hour), please check file size")
        except Exception as e:
            raise RuntimeError(f"混流时出错 / Error during muxing: {str(e)}\n详细信息 / Details: {traceback.format_exc()}")
    
    def process_all(self, video_files: List[str], audio_files: List[str], output_dir: str) -> str:
        """
        一键处理：合并视频、合并音频、混流
        One-click processing: Merge video, merge audio, then mux
        
        Args:
            video_files: 视频文件路径列表
            audio_files: 音频文件路径列表
            output_dir: 输出目录
            
        Returns:
            最终输出文件路径 / Final output file path
        """
        try:
            if not video_files and not audio_files:
                raise ValueError("至少需要提供视频文件或音频文件 / At least one video or audio file is required")

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            if video_files and not audio_files:
                return self.merge_video_segments(video_files, str(output_dir))
            if audio_files and not video_files:
                return self.merge_audio_segments(audio_files, str(output_dir))

            with tempfile.TemporaryDirectory() as temp_dir:
                video_input = self._prepare_stream_for_mux(video_files, temp_dir, is_video=True)
                audio_input = self._prepare_stream_for_mux(audio_files, temp_dir, is_video=False)
                return self.merge_av(video_input, audio_input, str(output_dir))
        except Exception as e:
            raise RuntimeError(f"一键处理失败 / Processing failed: {str(e)}\n详细信息 / Details: {traceback.format_exc()}")
