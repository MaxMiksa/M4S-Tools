# M4S 合并工具 v1.0.0 | [For English](https://github.com/MaxMiksa/M4S-Merger-Tools/blob/main/README-en.md)

通过图形界面选择文件，一键完成 M4S 视频片段合并、音频片段合并以及最终的音视频混流工作。  
一款适用于 Windows 平台的桌面 GUI 应用程序，用于处理 M4S 文件（通常来自哔哩哔哩/Bilibili流媒体下载）。

<img width="679" height="552" alt="20251129_180902_811" src="https://github.com/user-attachments/assets/02b1319e-4321-4a9e-b941-c0efbbd6deaa" />

## 功能特性

- 🎬 **视频片段合并**：将多个 M4S 视频片段合并为一个完整的视频文件
- 🎵 **音频片段合并**：将多个 M4S 音频片段合并为一个完整的音频文件
- 🎞️ **音视频混流**：将合并后的视频和音频文件混合为最终输出
- 🚀 **一键处理**：自动完成视频合并、音频合并和混流的全部流程
- 💻 **图形界面**：友好的 GUI 界面，操作简单直观
- 📝 **实时日志**：显示处理进度和日志信息
- ⚙️ **自动安装 FFmpeg**：首次运行时自动检测并安装 FFmpeg（如未安装）
- 🛡️ **完善的错误处理**：每个环节都有详细的错误提示，帮助用户快速定位问题

## 系统要求

- 若下载EXE文件：Windows 10/11
- 若使用源代码运行：Python 3.7 或更高版本

## 安装

### 推荐：使用打包好的 EXE 文件（下载即用）

1. 下载本界面右侧`Release`中的 `M4S Merger Tools.exe`
2. 运行 `M4S Merger Tools.exe`  
   注意：首次运行需要网络连接（自动下载 FFmpeg）

<details>
<summary> 备用：通过源代码运行 </summary>

#### 1. 安装 Python

如果尚未安装 Python，请从 [Python 官网](https://www.python.org/downloads/) 下载并安装。

#### 2. 运行程序

1. 下载或克隆本项目
2. 双击 `start.bat`

### 3. 自动安装 FFmpeg（如需要）

**首次运行时**，如果程序检测到未安装 FFmpeg，会自动弹出安装对话框：

1. 选择 FFmpeg 的安装目录（默认为用户主目录下的 `ffmpeg` 文件夹）
2. 点击"安装"按钮
3. 程序会：
   - **自动**下载 FFmpeg（100MB，大概下载10秒）
   - **自动**解压到指定目录
   - **自动**添加到系统 PATH 环境变量
4. 安装完成后，**重启程序**即可使用

<details>
<summary> 备用：详细步骤（手动安装FFmpeg） </summary>
1. 从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载 Windows 版本
2. 解压到任意目录（例如 `C:\ffmpeg`）
3. 将 FFmpeg 的 `bin` 目录添加到系统 PATH 环境变量：
   - 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 在"系统变量"中找到 `Path`，点击"编辑"
   - 添加 FFmpeg 的 `bin` 目录路径（例如 `C:\ffmpeg\bin`）
   - 点击"确定"保存
</details>

</details>

## 使用

### 基本操作流程

1. **选择视频文件**：点击"选择视频文件"按钮，选择需要合并的 M4S 视频片段
2. **选择音频文件**：点击"选择音频文件"按钮，选择需要合并的 M4S 音频片段
3. **选择输出目录**：点击"选择输出目录"按钮，选择结果文件的保存位置
4. **执行处理**：
   - **合并视频**：仅合并视频片段
   - **合并音频**：仅合并音频片段
   - **一键处理**：自动完成视频合并、音频合并和混流（推荐）

### 输出文件说明

- `merged_video.mp4`：合并后的视频文件
- `merged_audio.mp4`：合并后的音频文件
- `final_output.mp4`：最终混流后的完整视频文件（使用一键处理时生成）

## 注意事项

1. **文件顺序**：合并时会按照文件选择对话框中的顺序进行合并，请确保文件顺序正确
2. **文件格式**：目前主要支持 M4S 格式，其他格式可能也能处理，但未经过充分测试
3. **FFmpeg 路径**：如果 FFmpeg 不在系统 PATH 中，可以在代码中修改 `ffmpeg_path` 参数
4. **处理时间**：大文件处理可能需要较长时间，请耐心等待
5. **网络连接**：首次运行需要网络连接以下载 FFmpeg

## 其他

<details>
<summary>打包为可执行文件（若使用源代码运行，而非下载EXE文件）</summary>

程序提供了三种打包方式，可以将程序打包为独立的 `.exe` 文件，无需安装 Python 即可运行。

### 方式一：使用批处理脚本（推荐）

1. 双击运行 `build_exe.bat`
2. 脚本会自动安装 PyInstaller（如未安装）并开始打包
3. 打包完成后，可执行文件位于 `dist\M4S处理工具.exe`

### 方式二：使用 Python 脚本

```bash
python build_exe.py
```

### 方式三：手动打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包（使用批处理脚本）
build_exe.bat

# 或直接使用 PyInstaller
pyinstaller --onefile --windowed --name "M4S处理工具" main.py
```

### 分发说明

打包后的 `.exe` 文件可以：
- 复制到任何 Windows 电脑上直接运行
- 通过 U盘、网盘等方式分享给其他用户
- 首次运行时，程序会自动检测并按需安装 FFmpeg（需要网络连接）

</details>

<details>
<summary>完善的错误提示与处理机制</summary>

程序已添加完善的错误处理机制，每个环节都会显示详细的错误提示。
   ### 启动阶段
   - Python 版本检查
   - 模块导入检查
   - GUI 初始化检查
   
   ### 运行阶段
   - 文件选择错误提示
   - FFmpeg 调用错误提示
   - 文件处理错误提示
   - 网络连接错误提示
   
   ### 安装阶段
   - FFmpeg 下载错误提示
   - 解压错误提示
   - PATH 添加错误提示
   
   **如果程序运行无反应**：
   1. 检查是否有错误提示窗口弹出（可能被其他窗口遮挡）
   2. 检查任务管理器中是否有进程在运行
   3. 尝试以管理员权限运行
   4. 查看程序日志输出（如果使用源代码运行）

</details>

<details>
<summary>常见问题</summary>

### Q: 提示"未找到 FFmpeg"？

A: 程序首次运行时会自动检测 FFmpeg。如果未安装，会弹出安装对话框，按照提示操作即可。如果已安装但程序仍无法检测到，请确保 FFmpeg 已添加到系统 PATH 环境变量中，并重启程序。

### Q: FFmpeg 安装失败怎么办？

A: 可能的原因：
- 网络连接问题：请检查网络连接，确保能访问互联网
- 磁盘空间不足：FFmpeg 需要约 200MB 空间
- 权限问题：确保对安装目录有写入权限

如果自动安装失败，可以手动安装 FFmpeg（参考"安装步骤"中的手动安装说明）。

### Q: 程序运行无反应？

A: 请检查：
1. 是否有错误提示窗口弹出（可能被其他窗口遮挡）
2. 任务管理器中是否有进程在运行
3. 尝试以管理员权限运行
4. 如果使用 EXE 文件，确保文件完整且未被杀毒软件拦截

### Q: 合并后的视频没有声音？

A: 请确保同时选择了视频文件和音频文件，并使用"一键处理"功能进行混流。

### Q: 处理失败怎么办？

A: 查看日志输出区域中的错误信息，常见原因包括：
- 文件路径包含特殊字符
- 文件已损坏
- 磁盘空间不足
- FFmpeg 版本不兼容
- 网络连接问题（下载 FFmpeg 时）

</details>

<details>
<summary>技术说明</summary>
   
- **GUI 框架**：Python tkinter
- **视频处理**：FFmpeg
- **错误处理**：完善的异常捕获和用户提示机制

</details>

<details>
<summary>许可证</summary>

本项目采用 MIT 许可证。

</details>

## 贡献与联系

欢迎提交 Issue 和 Pull Request！  
如有任何问题或建议，请联系Max Kong (卡内基梅隆大学，宾夕法尼亚州)。

Welcome to submit Issues and Pull Requests!  
Any questions or suggestions？Please contact Max Kong (Carnegie Mellon University, Pittsburgh, PA).

Max Kong: kongzheyuan@outlook.com | zheyuank@andrew.cmu.edu
