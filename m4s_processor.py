#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4S 文件处理核心逻辑
"""

import subprocess
import os
import tempfile
import traceback
from pathlib import Path
from typing import List, Optional


class M4SProcessor:
    def __init__(self, ffmpeg_path: str = "ffmpeg", check_ffmpeg: bool = True):
        """
        初始化处理器
        
        Args:
            ffmpeg_path: FFmpeg 可执行文件路径，默认为 "ffmpeg"（需要在 PATH 中）
            check_ffmpeg: 是否在初始化时检查 FFmpeg，默认为 True
        """
        self.ffmpeg_path = ffmpeg_path
        if check_ffmpeg:
            self._check_ffmpeg()
    
    @staticmethod
    def check_ffmpeg_available(ffmpeg_path: str = "ffmpeg") -> bool:
        """
        检查 FFmpeg 是否可用（静态方法）
        
        Args:
            ffmpeg_path: FFmpeg 可执行文件路径
            
        Returns:
            是否可用
        """
        try:
            print(f"[FFmpeg] 检查 FFmpeg (路径: {ffmpeg_path})...")
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=5  # 缩短超时时间到5秒
            )
            print("[FFmpeg] FFmpeg 检查成功，已安装")
            return True
        except FileNotFoundError:
            print("[FFmpeg] FFmpeg 未找到（不在 PATH 中）")
            return False
        except subprocess.TimeoutExpired:
            print("[FFmpeg] FFmpeg 检查超时（可能卡住）")
            return False
        except subprocess.CalledProcessError as e:
            print(f"[FFmpeg] FFmpeg 检查失败（返回码: {e.returncode}）")
            return False
        except Exception as e:
            # 记录其他异常
            print(f"[FFmpeg] 检查 FFmpeg 时出错: {e}")
            return False
        
    def _check_ffmpeg(self):
        """检查 FFmpeg 是否可用（实例方法）"""
        if not self.check_ffmpeg_available(self.ffmpeg_path):
            raise RuntimeError(
                "未找到 FFmpeg！请确保 FFmpeg 已安装并添加到系统 PATH 环境变量中。\n"
                "下载地址: https://ffmpeg.org/download.html"
            )
    
    def _create_file_list(self, files: List[str], list_file_path: str):
        """创建文件列表文件（用于 FFmpeg concat）"""
        try:
            with open(list_file_path, 'w', encoding='utf-8') as f:
                for file in files:
                    if not os.path.exists(file):
                        raise FileNotFoundError(f"文件不存在: {file}")
                    # 使用绝对路径并转义单引号和特殊字符
                    abs_path = os.path.abspath(file).replace('\\', '/')
                    # 转义单引号（如果路径中包含单引号）
                    abs_path = abs_path.replace("'", "'\\''")
                    f.write(f"file '{abs_path}'\n")
        except Exception as e:
            raise RuntimeError(f"创建文件列表失败: {str(e)}")
    
    def merge_video_segments(self, video_files: List[str], output_dir: str) -> str:
        """
        合并视频片段
        
        Args:
            video_files: 视频文件路径列表
            output_dir: 输出目录
            
        Returns:
            输出文件路径
        """
        if not video_files:
            raise ValueError("视频文件列表为空")
        
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "merged_video.mp4"
            
            # 创建临时文件列表
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                list_file = f.name
                self._create_file_list(video_files, list_file)
            
            try:
                # 使用 FFmpeg 合并视频
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
                    error_msg = result.stderr if result.stderr else "未知错误"
                    raise RuntimeError(f"FFmpeg 合并视频失败: {error_msg}")
                
                if not output_file.exists():
                    raise RuntimeError(f"输出文件未生成: {output_file}")
                
                return str(output_file)
                
            finally:
                # 清理临时文件
                if os.path.exists(list_file):
                    try:
                        os.unlink(list_file)
                    except:
                        pass
        except subprocess.TimeoutExpired:
            raise RuntimeError("视频合并超时（超过1小时），请检查文件大小")
        except Exception as e:
            raise RuntimeError(f"合并视频时出错: {str(e)}\n详细信息: {traceback.format_exc()}")
    
    def merge_audio_segments(self, audio_files: List[str], output_dir: str) -> str:
        """
        合并音频片段
        
        Args:
            audio_files: 音频文件路径列表
            output_dir: 输出目录
            
        Returns:
            输出文件路径
        """
        if not audio_files:
            raise ValueError("音频文件列表为空")
        
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "merged_audio.mp4"
            
            # 创建临时文件列表
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                list_file = f.name
                self._create_file_list(audio_files, list_file)
            
            try:
                # 使用 FFmpeg 合并音频
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
                    error_msg = result.stderr if result.stderr else "未知错误"
                    raise RuntimeError(f"FFmpeg 合并音频失败: {error_msg}")
                
                if not output_file.exists():
                    raise RuntimeError(f"输出文件未生成: {output_file}")
                
                return str(output_file)
                
            finally:
                # 清理临时文件
                if os.path.exists(list_file):
                    try:
                        os.unlink(list_file)
                    except:
                        pass
        except subprocess.TimeoutExpired:
            raise RuntimeError("音频合并超时（超过1小时），请检查文件大小")
        except Exception as e:
            raise RuntimeError(f"合并音频时出错: {str(e)}\n详细信息: {traceback.format_exc()}")
    
    def merge_av(self, video_file: str, audio_file: str, output_dir: str, output_name: str = "final_output.mp4") -> str:
        """
        合并音视频
        
        Args:
            video_file: 视频文件路径
            audio_file: 音频文件路径
            output_dir: 输出目录
            output_name: 输出文件名
            
        Returns:
            输出文件路径
        """
        try:
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"视频文件不存在: {video_file}")
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"音频文件不存在: {audio_file}")
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / output_name
            
            # 使用 FFmpeg 合并音视频
            cmd = [
                self.ffmpeg_path,
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",  # 视频流直接复制，不重新编码
                "-c:a", "aac",   # 音频编码为 AAC（兼容性更好）
                "-strict", "experimental",
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
                error_msg = result.stderr if result.stderr else "未知错误"
                raise RuntimeError(f"FFmpeg 混流失败: {error_msg}")
            
            if not output_file.exists():
                raise RuntimeError(f"输出文件未生成: {output_file}")
            
            return str(output_file)
        except subprocess.TimeoutExpired:
            raise RuntimeError("音视频混流超时（超过1小时），请检查文件大小")
        except Exception as e:
            raise RuntimeError(f"混流时出错: {str(e)}\n详细信息: {traceback.format_exc()}")
    
    def process_all(self, video_files: List[str], audio_files: List[str], output_dir: str) -> str:
        """
        一键处理：合并视频、合并音频、混流
        
        Args:
            video_files: 视频文件路径列表
            audio_files: 音频文件路径列表
            output_dir: 输出目录
            
        Returns:
            最终输出文件路径
        """
        try:
            merged_video = None
            merged_audio = None
            
            # 合并视频
            if video_files:
                merged_video = self.merge_video_segments(video_files, output_dir)
            
            # 合并音频
            if audio_files:
                merged_audio = self.merge_audio_segments(audio_files, output_dir)
            
            # 如果只有视频或只有音频，直接返回
            if not merged_video and merged_audio:
                return merged_audio
            if merged_video and not merged_audio:
                return merged_video
            
            # 如果两者都有，进行混流
            if merged_video and merged_audio:
                return self.merge_av(merged_video, merged_audio, output_dir)
            
            raise ValueError("至少需要提供视频文件或音频文件")
        except Exception as e:
            raise RuntimeError(f"一键处理失败: {str(e)}\n详细信息: {traceback.format_exc()}")

