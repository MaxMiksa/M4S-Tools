# M4S文件处理工具 | M4S Tools (Demo)

<div align="center">
<img width="1244" height="1167" alt="image" src="https://github.com/user-attachments/assets/b6859e70-8a69-4748-af89-4f44625f20d8" />

</div>

# 1. 设计目标

## 1.1 核心功能模块
软件需包含几个主要操作模式（通过单选按钮切换）：

### 功能 A：M4S 片段合并 (单轨道重建)
*此功能用于将成百上千个分散的 .m4s 文件合并为一个完整的 .mp4 文件。*
- **输入:** 允许用户多选 .m4s 文件，或选择一个包含 .m4s 文件的文件夹。
- **逻辑:**
    1. 获取所有选中的文件。
    2. **关键步骤:** 对文件名进行**自然排序** (例如：确保 `1.m4s` 排在 `10.m4s` 之前)，以保证合并顺序正确。
    3. 生成一个临时的 `file_list.txt` (格式为 `file 'path/to/001.m4s'`) 以避免命令行长度限制。
    4. 调用 FFmpeg `concat` 协议进行无损合并 (`-c copy`)。
- **输出:** 用户指定输出文件名（例如 `video_track.mp4` 或 `audio_track.mp4`）。

### 功能 B：音视频混流 (Muxing)
*此功能用于将已经合并好的“纯视频文件”和“纯音频文件”合二为一。*
- **输入 1:** 选择视频文件 (如 `video_track.mp4`)。
- **输入 2:** 选择音频文件 (如 `audio_track.mp4`)。
- **逻辑:** 调用 FFmpeg 将两路流封装在一起 (`-c copy`)，不进行重新编码。
- **输出:** 最终的可播放文件 (如 `Final_Movie.mp4`)。

## 1.2 通用功能
- **FFmpeg 检测:** 软件启动时检测目录下是否存在 `ffmpeg.exe`。如果不存在，提示用户下载或将 `ffmpeg.exe` 内置在软件资源中。
- **输出路径:** 允许用户选择输出文件的保存位置。
- **进度反馈:** 界面显示当前处理状态（"正在排序...", "正在合并...", "完成"）或简单的进度条。
- **日志显示:** 底部保留一个文本框，显示 FFmpeg 的输出日志（方便排错）。

# 运行和部署此应用

## 在线预览

在 Gemini AI Studio 中查看 Demo：https://ai.studio/apps/drive/1bBh4Hi4XWLAzjC47PDUdHofpu6Aj8TVs

## 本地运行

**必备条件：** Node.js

1. 安装依赖项：
   `npm install`
2. 将 [.env.local](.env.local) 文件中的 `GEMINI_API_KEY` 设置为您的 Gemini API 密钥
3. 运行应用：
   `npm run dev`
