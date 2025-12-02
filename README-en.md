---

# M4S Merger Tools v1.1.0 | [For English](https://github.com/MaxMiksa/M4S-Merger-Tools/blob/main/README-en.md)

✅ **GUI Interface, Ready-to-Use EXE! No Manual FFmpeg Installation or Command Line Required!** ✅

Select files via a graphical interface to instantly merge M4S video fragments, audio fragments, and perform the final audio/video muxing. This is a desktop application for Windows designed to handle M4S files (typically sourced from Bilibili video/audio downloads).

<div align="center">
    <!-- Left Image -->
    <img src="Presentation%20Videos/v1.1.0/ScreenShot%201%20-%20M4S%20Merger%20Tools%20v1.1.0.png" 
     alt="M4S Merger Tools v1.1.0 " 
     width="480"/>
    &nbsp;
    <!-- Right Image -->
    <img src="Presentation%20Videos/v1.1.0/ScreenShot%202%20-%20M4S%20Merger%20Tools%20v1.1.0.png" 
     alt="M4S Merger Tools v1.1.0 " 
     width="480"/>
</div>

## Features

| Feature | Description |
| :--- | :--- |
| 🎬 **Video Merging** | Combines multiple M4S video fragments into a single complete video file. |
| 🎵 **Audio Merging** | Combines multiple M4S audio fragments into a single complete audio file. |
| 🎞️ **Audio/Video Muxing (Remixing)**  | Merges separate M4S video and audio files into one complete MP4 file (containing both picture and sound). |
| 🚀 **One-Click Automation** | Fully automated workflow, including environment setup (FFmpeg download), error reporting/resolution, and combined audio/video processing. |
| 💻 **Customizable GUI** | A user-friendly, click-and-run visual interface, eliminating command-line hassle. Supports switching between Chinese/English and light/dark modes. |
| 📝 **Real-time Progress Display** | Shows detailed processing progress and log information in real-time. |
| ⚙️ **Automatic FFmpeg Setup** | Automatically detects and installs FFmpeg on first run if needed (supports custom download and installation paths). |
| 🛡️ **Robust Error Handling** | Provides detailed error prompts at every stage to help users quickly identify and resolve issues. |

## Usage (Run Directly via EXE)

<img src="Presentation%20Videos/v1.1.0/Presentation%20video%20-%20M4S%20Merger%20Tools%20v1.1.0.gif" 
     alt="M4S Merger Tools v1.1.0 Demo Animation" 
     width="1050"/>

### Basic Workflow

1. **Select Video Files**: Click the "Select Video Files" button to choose the M4S video fragments to be merged.
2. **Select Audio Files**: Click the "Select Audio Files" button to choose the M4S audio fragments to be merged.
3. **Select Output Directory**: Click the "Select Output Directory" button to choose the save location for the result file.
4. **Execute Processing**:
   - **Merge Video Only**: Merges video fragments only.
   - **Merge Audio Only**: Merges audio fragments only.
   - **One-Click Muxing**: Automatically completes video merging, audio merging, and muxing (Recommended).

### Output File Description

- `merged_video.mp4`: The merged video file.
- `merged_audio.mp4`: The merged audio file.
- `final_output.mp4`: The final muxed video file (generated when using one-click processing).

## System Requirements

- If downloading the EXE file: Windows 10/11
- If running from source code: Python 3.7 or higher

## Installation

### Recommended: Using the Packaged EXE File (Download and Run)

1. Download `M4S Merger Tools.exe` from the `Release` section on the right side of this interface.
2. Run `M4S Merger Tools.exe`.
   Note: Internet connection is required for the first run (for automatic FFmpeg download).

<details>
<summary> Alternative: Running from Source Code </summary>

#### 1. Install Python

If Python is not installed, download and install it from the [Python official website](https://www.python.org/downloads/).

#### 2. Run the Program

1. Download or clone this project.
2. Double-click `start.bat`.

### 3. Automatic FFmpeg Installation (If Needed)

**Upon the first run**, if the program detects that FFmpeg is not installed, an installation dialog will pop up:

1. Select the installation directory for FFmpeg (defaults to the `ffmpeg` folder in the user's home directory).
2. Click the "Install" button.
3. The program will:
   - **Automatically** download FFmpeg (approx. 100MB, takes about 10 seconds).
   - **Automatically** extract it to the specified directory.
   - **Automatically** add it to the system PATH environment variable.
4. After installation, **restart the program** to use it.

<details>
<summary> Alternative: Detailed Steps (Manual FFmpeg Installation) </summary>
1. Download the Windows version from the [FFmpeg official website](https://ffmpeg.org/download.html).
2. Extract it to any directory (e.g., `C:\ffmpeg`).
3. Add FFmpeg's `bin` directory to the system PATH environment variable:
   - Right-click "This PC" → "Properties" → "Advanced system settings" → "Environment Variables".
   - Under "System variables," find `Path` and click "Edit".
   - Add the path to the FFmpeg `bin` directory (e.g., `C:\ffmpeg\bin`).
   - Click "OK" to save.
</details>

</details>

## Notes

1. **File Order**: Merging is performed according to the order in which files were selected in the dialog; please ensure the file sequence is correct.
2. **File Format**: Currently, the primary support is for M4S format; other formats may work but have not been fully tested.
3. **FFmpeg Path**: If FFmpeg is not in the system PATH, you can modify the `ffmpeg_path` parameter in the source code.
4. **Processing Time**: Processing large files may take a significant amount of time; please be patient.
5. **Network Connection**: An internet connection is required for the first run to download FFmpeg.

## Others

<details>
<summary>Packaging as an Executable (If running from source code, not using the downloaded EXE)</summary>

The program provides three methods to package it into a standalone `.exe` file, allowing it to run without Python installed.

### Method 1: Using the Batch Script (Recommended)

1. Double-click `build_exe.bat`.
2. The script will automatically install PyInstaller (if not installed) and begin packaging.
3. The executable file will be located in `dist\M4S Merger Tools v1.x.0.exe`.

### Method 2: Using the Python Script

```bash
python build_exe.py
```

### Method 3: Manual Packaging

```bash
# Install PyInstaller
pip install pyinstaller

# Package (using the batch script)
build_exe.bat

# Or directly use PyInstaller
pyinstaller --onefile --windowed --name "M4S Merger Tools v1.x.0" main.py
```

### Distribution Notes

The packaged `.exe` file can be:
- Copied to any Windows computer and run directly.
- Shared with other users via USB drives or cloud storage.
- Upon first run, the program automatically detects and installs FFmpeg as needed (requires network connection).

</details>

<details>
<summary>Comprehensive Error Prompts and Handling Mechanism</summary>

The program includes a comprehensive error handling mechanism, displaying detailed error prompts at every stage.

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
   
   **If the program fails to respond**:
   1. Check for error pop-up windows (they might be hidden behind other windows).
   2. Check if a process is running in the Task Manager.
   3. Try running as administrator.
   4. Check the program's log output (if running from source code).

</details>

<details>
<summary>FAQ</summary>

### Q: Why does it prompt "FFmpeg not found"?

A: The program automatically checks for FFmpeg on the first run. If it's not installed, an installation dialog will appear—follow the instructions. If it is installed but the program can't detect it, ensure FFmpeg is added to the system PATH environment variable, and then restart the program.

### Q: What if FFmpeg installation fails?

A: Possible reasons include:
- Network connection issues: Check your internet connection.
- Insufficient disk space: FFmpeg requires about 200MB of space.
- Permission issues: Ensure you have write permissions for the installation directory.

If automatic installation fails, you can install FFmpeg manually (refer to the manual installation instructions in the "Installation" section).

### Q: The program is unresponsive?

A: Please check:
1. Whether an error prompt window appeared (it might be hidden).
2. If a process is running in the Task Manager.
3. Try running as administrator.
4. If using the EXE file, ensure the file is complete and not blocked by antivirus software.

### Q: The merged video has no sound?

A: Please ensure that you have selected both video and audio files and used the "One-Click Muxing" feature to combine the streams.

### Q: What if processing fails?

A: Check the error message in the log output area. Common causes include:
- File paths containing special characters.
- Corrupted files.
- Insufficient disk space.
- FFmpeg version incompatibility.
- Network connection issues (during FFmpeg download).

</details>

<details>
<summary>Technical Details</summary>
   
- **GUI Framework**: Python tkinter
- **Video Processing**: FFmpeg
- **Error Handling**: Comprehensive exception capturing and user notification mechanism

</details>

<details>
<summary>License</summary>

This project is licensed under the MIT License.

</details>

## Contribution and Contact

Welcome to submit Issues and Pull Requests!  
Any questions or suggestions? Please contact Max Kong (Carnegie Mellon University, Pittsburgh, PA).

Max Kong: kongzheyuan@outlook.com | zheyuank@andrew.cmu.edu
