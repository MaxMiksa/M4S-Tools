#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FFmpeg 自动安装模块
"""

import os
import sys
import subprocess
import zipfile
import urllib.request
import shutil
import traceback
from pathlib import Path
from typing import Optional, Tuple


class FFmpegInstaller:
    """FFmpeg 安装器"""
    
    # FFmpeg 下载地址（使用 gyan.dev 的构建版本）
    FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    @staticmethod
    def check_ffmpeg(ffmpeg_path: str = "ffmpeg") -> Tuple[bool, Optional[str]]:
        """
        检查 FFmpeg 是否已安装
        
        Args:
            ffmpeg_path: FFmpeg 可执行文件路径
            
        Returns:
            (是否已安装, FFmpeg 路径)
        """
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=10
            )
            # 获取 FFmpeg 的完整路径
            which_result = shutil.which(ffmpeg_path)
            return True, which_result if which_result else ffmpeg_path
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None
        except Exception as e:
            print(f"检查 FFmpeg 时出错: {e}")
            return False, None
    
    @staticmethod
    def download_ffmpeg(download_dir: Path, progress_callback=None) -> Path:
        """
        下载 FFmpeg
        
        Args:
            download_dir: 下载目录
            progress_callback: 进度回调函数 (stage, current, total, message)
            
        Returns:
            下载的 zip 文件路径
        """
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
            zip_path = download_dir / "ffmpeg-release-essentials.zip"
            
            def show_progress(block_num, block_size, total_size):
                if progress_callback:
                    downloaded = block_num * block_size
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        progress_callback('download', downloaded, total_size, 
                                       f"下载中: {downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB ({percent}%)")
                    else:
                        progress_callback('download', downloaded, -1, 
                                       f"下载中: {downloaded // 1024 // 1024}MB")
            
            try:
                urllib.request.urlretrieve(
                    FFmpegInstaller.FFMPEG_URL,
                    str(zip_path),
                    show_progress
                )
                
                # 检查文件是否下载成功
                if not zip_path.exists() or zip_path.stat().st_size == 0:
                    raise RuntimeError("下载的文件为空或不存在")
                
                return zip_path
            except urllib.error.URLError as e:
                raise RuntimeError(f"网络错误，无法下载 FFmpeg: {str(e)}\n请检查网络连接")
            except Exception as e:
                if zip_path.exists():
                    try:
                        zip_path.unlink()
                    except:
                        pass
                raise RuntimeError(f"下载 FFmpeg 失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"下载 FFmpeg 时出错: {str(e)}\n详细信息: {traceback.format_exc()}")
    
    @staticmethod
    def extract_ffmpeg(zip_path: Path, extract_dir: Path, progress_callback=None) -> Path:
        """
        解压 FFmpeg
        
        Args:
            zip_path: zip 文件路径
            extract_dir: 解压目录
            progress_callback: 进度回调函数 (stage, current, total, message)
            
        Returns:
            FFmpeg bin 目录路径
        """
        try:
            if not zip_path.exists():
                raise FileNotFoundError(f"ZIP 文件不存在: {zip_path}")
            
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    total_files = len(file_list)
                    
                    if total_files == 0:
                        raise RuntimeError("ZIP 文件为空")
                    
                    # 找到 bin 目录
                    bin_dir_name = None
                    for name in file_list:
                        if '/bin/ffmpeg.exe' in name or '\\bin\\ffmpeg.exe' in name:
                            # 提取顶层目录名
                            parts = name.replace('\\', '/').split('/')
                            if len(parts) > 0:
                                bin_dir_name = parts[0]
                            break
                    
                    if not bin_dir_name:
                        raise RuntimeError("无法在 ZIP 文件中找到 FFmpeg bin 目录")
                    
                    # 解压文件
                    for i, member in enumerate(file_list):
                        try:
                            zip_ref.extract(member, extract_dir)
                            if progress_callback:
                                progress_callback('extract', i + 1, total_files, 
                                                f"解压中: {i + 1}/{total_files} 文件")
                        except Exception as e:
                            raise RuntimeError(f"解压文件失败: {member}\n错误: {str(e)}")
                    
                    # 返回 bin 目录的完整路径
                    bin_dir = extract_dir / bin_dir_name / "bin"
                    if not bin_dir.exists():
                        raise RuntimeError(f"FFmpeg bin 目录不存在: {bin_dir}")
                    
                    # 检查 ffmpeg.exe 是否存在
                    ffmpeg_exe = bin_dir / "ffmpeg.exe"
                    if not ffmpeg_exe.exists():
                        raise RuntimeError(f"FFmpeg 可执行文件不存在: {ffmpeg_exe}")
                    
                    return bin_dir
                    
            except zipfile.BadZipFile:
                raise RuntimeError(f"ZIP 文件损坏: {zip_path}")
            except Exception as e:
                raise RuntimeError(f"解压 FFmpeg 失败: {str(e)}")
                
        except Exception as e:
            raise RuntimeError(f"解压 FFmpeg 时出错: {str(e)}\n详细信息: {traceback.format_exc()}")
    
    @staticmethod
    def add_to_path(bin_dir: Path) -> bool:
        """
        将 FFmpeg bin 目录添加到用户 PATH 环境变量
        
        Args:
            bin_dir: FFmpeg bin 目录路径
            
        Returns:
            是否成功
        """
        try:
            if not bin_dir.exists():
                raise FileNotFoundError(f"目录不存在: {bin_dir}")
            
            bin_path = str(bin_dir.resolve())
            
            # 获取当前用户 PATH
            try:
                import winreg
                
                # 打开用户环境变量注册表
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    "Environment",
                    0,
                    winreg.KEY_READ | winreg.KEY_WRITE
                )
                
                try:
                    # 读取当前 PATH
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "Path")
                        path_list = current_path.split(os.pathsep) if current_path else []
                    except FileNotFoundError:
                        # PATH 不存在，创建新的
                        path_list = []
                    
                    # 检查是否已存在
                    if bin_path in path_list:
                        return True
                    
                    # 添加到 PATH
                    path_list.append(bin_path)
                    new_path = os.pathsep.join(path_list)
                    
                    # 写入注册表
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    
                    # 通知系统环境变量已更改
                    try:
                        import ctypes
                        ctypes.windll.user32.SendMessageW(
                            0xFFFF,  # HWND_BROADCAST
                            0x001A,  # WM_SETTINGCHANGE
                            0,
                            "Environment"
                        )
                    except:
                        pass  # 通知失败不影响添加 PATH
                    
                    return True
                    
                finally:
                    winreg.CloseKey(key)
                    
            except ImportError:
                # winreg 不可用，尝试使用 setx 命令
                try:
                    result = subprocess.run(
                        ['setx', 'PATH', f'%PATH%;{bin_path}'],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=10
                    )
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    return False
            except Exception as e:
                print(f"添加 PATH 时出错: {e}")
                return False
                
        except Exception as e:
            print(f"添加 PATH 时出错: {str(e)}")
            return False
    
    @staticmethod
    def install_ffmpeg(install_dir: Path, progress_callback=None) -> Tuple[Path, bool]:
        """
        安装 FFmpeg（下载、解压、添加到 PATH）
        
        Args:
            install_dir: 安装目录
            progress_callback: 进度回调函数 (stage, current, total, message)
                              stage: 'download', 'extract', 'path'
        
        Returns:
            (FFmpeg bin 目录路径, 是否成功添加到 PATH)
        """
        temp_dir = None
        try:
            temp_dir = install_dir / ".ffmpeg_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 下载
            if progress_callback:
                progress_callback('download', 0, 100, "正在下载 FFmpeg...")
            
            zip_path = FFmpegInstaller.download_ffmpeg(temp_dir, progress_callback)
            
            # 解压
            if progress_callback:
                progress_callback('extract', 0, 100, "正在解压 FFmpeg...")
            
            bin_dir = FFmpegInstaller.extract_ffmpeg(zip_path, install_dir, progress_callback)
            
            # 添加到 PATH
            if progress_callback:
                progress_callback('path', 0, 100, "正在添加到 PATH...")
            
            path_success = FFmpegInstaller.add_to_path(bin_dir)
            
            if progress_callback:
                progress_callback('path', 100, 100, "安装完成" if path_success else "安装完成（需要手动添加到 PATH）")
            
            return bin_dir, path_success
            
        except Exception as e:
            error_msg = f"安装 FFmpeg 失败: {str(e)}\n详细信息: {traceback.format_exc()}"
            if progress_callback:
                progress_callback('error', 0, 100, error_msg)
            raise RuntimeError(error_msg)
        finally:
            # 清理临时目录
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

