# M4S Merger Tools v1.0.0 | [中文版本](https://github.com/MaxMiksa/M4S-Merger-Tools/blob/main/README-zh.md)

A desktop GUI application for Windows that provides a one-click solution for merging M4S video segments, audio segments, and performing the final audio-video muxing. This tool is designed primarily for handling M4S files (typically sourced from Bilibili/B站 streams).

<img src="presentation/Presentation%20video%20-%20M4S%20Merger%20Tools%20v1.0.0.gif" 
     alt="M4S Merger Tools 演示动画" 
     width="1000"/>
[Clearer Video of this](https://github.com/MaxMiksa/M4S-Merger-Tools/blob/main/presentation/Presentation%20video%20-%20M4S%20Merger%20Tools%20v1.0.0.MP4)

## Key Features

- 🎬 **Video Segment Merging**: Combines multiple M4S video segments into a complete video file.
- 🎵 **Audio Segment Merging**: Combines multiple M4S audio segments into a complete audio file.
- 🎞️ **Audio-Video Muxing**: Mixes the merged video and audio files into the final output.
- 🚀 **One-Click Processing**: Automatically executes the entire workflow: video merging, audio merging, and muxing.
- 💻 **Graphical User Interface (GUI)**: Intuitive and simple operation.
- 📝 **Real-time Logging**: Displays processing progress and logs.
- ⚙️ **Automatic FFmpeg Installation**: Automatically detects and installs FFmpeg upon first run (if not found).
- 🛡️ **Robust Error Handling**: Provides detailed error prompts at every stage for easy troubleshooting.

## System Requirements

- If using the EXE file: Windows 10/11
- If running from source code: Python 3.7 or higher

## Installation

### Recommended: Use the Compiled EXE File (Download and Run)

1. Download the `M4S-Tools.exe` file from the **`Release`** section on the right sidebar of the GitHub interface.
2. Run `M4S-Tools.exe`.
   Note: Internet connection is required for the first run (to automatically download FFmpeg).

<details>
<summary> Alternative: Run via Source Code </summary>

#### 1. Install Python

If you do not have Python installed, download and install it from the [Python official website](https://www.python.org/downloads/).

#### 2. Run the Program

1. Download or clone this project.
2. Double-click `start.bat` to run the application.
</details>

### Automatic FFmpeg Setup (If Needed)

**On first run**, if the program detects that FFmpeg is not installed, an installation dialog will pop up automatically:

1. Select the installation directory for FFmpeg (default is the `ffmpeg` folder under the user's home directory).
2. Click the "Install" button.
3. The program will:
   - **Automatically** download FFmpeg (approx. 100MB, usually takes about 10 seconds).
   - **Automatically** extract it to the specified directory.
   - **Automatically** add the FFmpeg `bin` directory to the System PATH environment variable.
4. After installation is complete, **restart the program** to begin using it.

<details>
<summary> Alternative: Manual FFmpeg Installation (Detailed Steps) </summary>
1. Download the Windows version of FFmpeg from the [FFmpeg official website](https://ffmpeg.org/download.html).
2. Extract the downloaded archive to any location (e.g., `C:\ffmpeg`).
3. Add the FFmpeg `bin` directory to your System PATH environment variables:
   - Right-click "This PC" → "Properties" → "Advanced system settings" → "Environment Variables".
   - In the "System variables" section, find `Path` and click "Edit".
   - Add the path to the FFmpeg `bin` directory (e.g., `C:\ffmpeg\bin`).
   - Click "OK" to save the changes.
</details>

## Usage

### Basic Operation Flow

1. **Select Video Files**: Click "Select Video Files" to choose the M4S video segments to be merged.
2. **Select Audio Files**: Click "Select Audio Files" to choose the M4S audio segments to be merged.
3. **Select Output Directory**: Click "Select Output Directory" to choose where the result file will be saved.
4. **Execute Processing**:
   - **Merge Video**: Only merges the video segments.
   - **Merge Audio**: Only merges the audio segments.
   - **One-Click Process**: Automatically performs video merge, audio merge, and muxing (Recommended).

### Output Files Explained

- `merged_video.mp4`: The resulting merged video file.
- `merged_audio.mp4`: The resulting merged audio file.
- `final_output.mp4`: The final, muxed complete video file (generated when using "One-Click Process").

## Important Notes

1. **File Order**: Merging is performed based on the order in which files are selected in the dialog box. Please ensure the file order is correct.
2. **File Format**: The tool primarily supports the M4S format. Other formats might work but have not been extensively tested.
3. **FFmpeg Path**: If FFmpeg is not in the System PATH, the `ffmpeg_path` parameter can be modified in the source code.
4. **Processing Time**: Processing large files may take considerable time. Please be patient.
5. **Network Connection**: Internet connection is required for the initial automatic FFmpeg download.

## Advanced Topics

<details>
<summary>Building the Executable File (EXE) (If running from source code)</summary>

The program provides three methods to package the application into a standalone `.exe` file, allowing it to run without a separate Python installation.

### Method 1: Using the Batch Script (Recommended)

1. Double-click `build_exe.bat`.
2. The script will automatically install PyInstaller (if needed) and start the packaging process.
3. The executable file will be located in `dist\M4S-Merger-Tools.exe`.

### Method 2: Using the Python Script

```bash
python build_exe.py
```

### Method 3: Manual Packaging

```bash
# Install PyInstaller
pip install pyinstaller

# Package using the batch script
build_exe.bat

# Or directly using PyInstaller
pyinstaller --onefile --windowed --name "M4S-Merger-Tools" main.py
```

### Distribution Notes

The compiled `.exe` file can be:
- Copied and run directly on any Windows computer.
- Shared via USB drives, cloud storage, etc.
- Upon first run, the program will automatically detect and install FFmpeg as required (requires internet connection).

</details>

<details>
<summary>Robust Error Prompts and Handling Mechanism</summary>

The program includes a comprehensive error handling system, displaying detailed error messages at every stage:
   ### Startup Phase
   - Python version check
   - Module import check
   - GUI initialization check
   
   ### Runtime Phase
   - File selection error prompts
   - FFmpeg call error prompts
   - File processing error prompts
   - Network connection error prompts
   
   ### Installation Phase
   - FFmpeg download error prompts
   - Extraction error prompts
   - PATH addition error prompts
   
   **If the program fails to launch:**
   1. Check if an error window has popped up (it might be hidden behind other windows).
   2. Check the Task Manager for running processes.
   3. Try running with administrator privileges.
   4. Check the program log output (if running from source code).

</details>

<details>
<summary>Frequently Asked Questions (FAQ)</summary>

### Q: I receive a prompt "FFmpeg not found"?

A: The program automatically detects FFmpeg on first run. If it's not installed, an installation dialog will appear; follow the prompts. If it is installed but the program still can't detect it, ensure FFmpeg's `bin` directory is added to your System PATH environment variables and restart the program.

### Q: What if FFmpeg installation fails?

A: Possible causes:
- Network connectivity issues: Check your internet connection.
- Insufficient disk space: FFmpeg requires about 200MB of space.
- Permissions issues: Ensure you have write permissions to the installation directory.

If automatic installation fails, you can manually install FFmpeg (refer to the "Manual FFmpeg Installation" steps above).

### Q: The program doesn't launch or respond?

A: Please check:
1. If an error prompt window appeared (possibly hidden).
2. If any related process is running in the Task Manager.
3. Try running with administrator privileges.
4. If using the EXE file, ensure the file is complete and not blocked by antivirus software.

### Q: The merged video has no sound?

A: Please ensure you have selected both video and audio files and used the "One-Click Process" function to perform the final muxing.

### Q: What should I do if processing fails?

A: Check the log output area for error messages. Common causes include:
- File paths containing special characters.
- Corrupted source files.
- Insufficient disk space.
- FFmpeg version incompatibility.
- Network connection issues (during FFmpeg download).

</details>

<details>
<summary>Technical Specifications</summary>

- **GUI Framework**: Python tkinter
- **Video Processing**: FFmpeg
- **Error Handling**: Comprehensive exception catching and user prompting mechanism

</details>

<details>
<summary>License</summary>

This project is licensed under the MIT License.

</details>

## Contribution and Contact

Welcome to submit Issues and Pull Requests!
Any questions or suggestions? Please contact Max Kong (Carnegie Mellon University, Pittsburgh, PA).

Max Kong: kongzheyuan@outlook.com | zheyuank@andrew.cmu.edu
