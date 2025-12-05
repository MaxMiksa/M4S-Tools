# Release Notes

## v1.3.0 – Faster Launch & Mux Performance

### Feature 1: Asynchronous FFmpeg Check Removes Launch Freeze
- **Summary**: UI widgets render immediately while FFmpeg verification runs on a background thread, so the packaged EXE no longer pauses for 2–3 seconds.
- **Pain points solved**: Previously the window stayed blank until `ffmpeg -version` completed, making the app feel sluggish.
- **Change details**:
  - `gui.py` now calls `setup_ui()` right away and defers `_start_ffmpeg_check` via `root.after(200, ...)`.
  - The log console prints “[FFmpeg] 检查中... | Checking FFmpeg availability...” to keep users informed.
- **Technical implementation**:
  - `_start_ffmpeg_check` spins up a `threading.Thread` to run `M4SProcessor.check_ffmpeg_available()` and dispatches results back through `_on_ffmpeg_check_finished`.
  - State flags (`processor_ready`, `ffmpeg_checking`) prevent duplicate checks and keep the workflow thread-safe.

### Feature 2: Processor-Ready Guard Before Every Task
- **Summary**: Buttons call `_ensure_processor_ready()` before kicking off any work, showing a bilingual “FFmpeg is initializing...” notice if the background check or installer is still running.
- **Pain points solved**: Early clicks during startup could fail silently or raise errors because FFmpeg wasn’t ready.
- **Change details**:
  - `_run_task` enforces default output selection and then verifies readiness; if FFmpeg isn’t available yet, it prompts the user and aborts.
  - If a check hasn’t started, `_ensure_processor_ready()` re-triggers `_start_ffmpeg_check()` automatically.
- **Technical implementation**:
  - The guard inspects `self.processor_ready`/`self.processor` and references `self.t["ffmpeg_wait"]` for consistent bilingual copy.
  - Centralizing the logic prevents multiple processors from being spawned under rapid user interactions.

### Feature 3: Stream-Copy Muxing Restores Sub-Second Performance
- **Summary**: The mux command now simply copies video and audio streams (`-c:v copy -c:a copy`), eliminating the heavy AAC re-encode and bringing runtime for a 95 MB + 34 MB pair back down to a couple of seconds.
- **Pain points solved**: The previous `-c:a aac -strict experimental` pipeline forced FFmpeg to transcode the full audio track every time, taking 50–60 seconds.
- **Change details**:
  - Users immediately get a playable MP4 with both picture and sound because FFmpeg just rewraps the sources.
  - The README’s performance section documents the before/after behavior for future reference.
- **Technical implementation**:
  - `merge_av` sets only `-y` plus the stream-copy flags; removing the AAC encode step means CPU usage drops drastically.
  - Since nothing is transcoded, muxing latency is dominated by file I/O rather than processing.

### Feature 4: Unified Log Font & FFmpeg Installer UI
- **Summary**: The log console now uses a Chinese-friendly font and bilingual FFmpeg status strings, while the installer dialog adopts the same rounded card design and color palette as the main GUI.
- **Pain points solved**: Chinese characters previously appeared as `???` in logs, and the installer looked like a plain Tk window that clashed with the modern interface.
- **Change details**:
  - `font_mono` switched to Microsoft YaHei UI, and the startup logs explicitly show “检查中” / “已就绪” alongside English text.
  - The installer modal features a brand-colored icon, path card, bilingual helper text, themed progress bar, and a full-width primary button consistent with the main app.
- **Technical implementation**:
  - `_start_ffmpeg_check` and `_on_ffmpeg_check_finished` write Unicode strings directly, relying on the updated font to render them accurately.
  - `install_ffmpeg_dialog` now composes its layout with `CTkFrame` containers, reused color tokens, and the shared font stack so it visually matches the rest of the UI.

### Feature 5: Cleaner Main UI & Dark-Theme Button Pass
- **Summary**: Removed the largely idle main progress bar (the installer dialog keeps its own) and refreshed dark-mode buttons—“Merge Video/Audio”, both “Select Files”, and “Change Path”—so they all use the same secondary palette with proper hover feedback.
- **Pain points solved**: The progress bar stayed at 0 most of the time while taking up space, and dark-mode buttons blended into their background with no visual feedback on hover.
- **Change details**:
  - Deleted the `CTkProgressBar` widget and its start/stop logic from the main window; layout closes up accordingly.
  - Added `secondary_btn` / `secondary_hover` colors and assigned them to the select buttons, path changer, and the “merge video/audio” buttons to ensure consistent hover cues and sufficient contrast.
- **Technical implementation**:
  - Only the installer modal still instantiates a progress bar; `_run_task` / `_on_finish` no longer reference `self.progress_bar`.
  - Centralized secondary colors in the `COLORS` mapping so both light and dark themes pick the right tone, keeping hover handling declarative.

## v1.2.0 – Precise Exports & Desktop-Friendly Defaults

### Feature 1: Timestamped and Traceable Outputs
- **Summary**: Every exported file is now named `Merged_*` / `Muxed_*_YYYY-MM-DD_HH-MM-SS.mp4`, making each run unique and easy to trace.
- **Pain points solved**: Fixed filenames were constantly overwritten, and users struggled to identify which MP4 corresponded to a given operation.
- **Change details**:
  - Video merge, audio merge, and mux routines emit timestamped filenames by default.
  - README (ZH/EN) highlights the naming scheme and final-only artifacts.
  - Advanced users can still pass custom `output_name` values when scripting.
- **Technical implementation**:
  - `_timestamp_str` and `_generate_output_name` were added to `m4s_processor.py` and invoked from `merge_video_segments`, `merge_audio_segments`, and `merge_av`.
  - The timestamp format `"%Y-%m-%d_%H-%M-%S"` remains filesystem friendly on Windows/macOS/Linux.
  - Optional parameters keep backward compatibility with automated pipelines that require deterministic names.

### Feature 2: Temp-Directory Muxing & Single-File Shortcuts
- **Summary**: The pipeline now skips redundant merging when only one file exists and moves all multi-part merges into a temporary directory that auto-cleans.
- **Pain points solved**: Intermediate `merged_video.mp4` / `merged_audio.mp4` polluted output folders and confused users about which file to share.
- **Change details**:
  - `process_all` no longer writes intermediate files to the target folder; it directly returns the sole existing stream or the final mux.
  - The GUI’s “Mux” button mirrors this logic, logging the familiar steps but only persisting the muxed MP4.
- **Technical implementation**:
  - `_prepare_stream_for_mux` inspects `len(files)` to decide between pass-through and invoking the merge helpers.
  - `tempfile.TemporaryDirectory()` scopes the intermediate storage, guaranteeing cleanup.
  - The mux command still uses `-c:v copy -c:a aac`, only the source paths differ (original vs. temp).

### Feature 3: Desktop-First Output Policy
- **Summary**: The app auto-selects the current user’s Desktop as the output folder and falls back to `os.getcwd()` if the Desktop is missing.
- **Pain points solved**: Users frequently forgot to browse for an output location and later had trouble locating results in deep working directories.
- **Change details**:
  - UI copy now states “Desktop (Default)” / “桌面 (默认)” so expectations are clear.
  - `_run_task` ensures `self.output_dir` is populated before any processing begins.
- **Technical implementation**:
  - `_get_default_output_dir` checks `Path.home() / "Desktop"` and only returns CWD when the path does not exist.
  - Initialization and task execution both call this helper and immediately refresh the label via `_update_path_label`.

### Feature 4: Documentation Refresh
- **Summary**: The README pair reflects v1.2.0 screenshots/GIFs, the Desktop default, and timestamped file naming.
- **Pain points solved**: Without updated docs, new users would assume older behavior (current-directory outputs, generic filenames).
- **Technical implementation**:
  - Media links moved to `Presentation Videos/v1.2.0/...`.
  - Output descriptions explicitly mention the new naming convention and the fact that only the final mux is left in the destination folder.

## v1.1.0 – Complete UI/UX Overhaul with Bilingual Support

### Feature 1: Modernized Layout & Visual Refresh
- **Summary**: Rebuilt the interface with card-style panels, consistent typography, and better spacing so it looks and feels modern on 860×930 displays and above.
- **Pain points solved**: The legacy Tk layout was cramped, visually dated, and hard to navigate.
- **Change details**:
  - Introduced `main_card`, scrollable file panes, rounded buttons, and better font pairings (Microsoft YaHei UI + Consolas).
  - File entries show size hints, truncation for long names, and clear separators.
- **Technical implementation**:
  - Everything runs on `customtkinter`; `COLORS` centralizes light/dark palettes.
  - `self.ui_refs` keeps widget handles for later refreshes (language/theme toggles).

### Feature 2: Bilingual Prompts, Logs, and Installer
- **Summary**: Every major text string—buttons, tooltips, logs, message boxes, installer screens—can switch between Chinese and English instantly.
- **Pain points solved**: International users could not understand Chinese-only prompts, and bilingual documentation could not point to matching UI text.
- **Change details**:
  - The `TRANS` dictionary houses all texts; `toggle_language` + `refresh_text` propagate changes.
  - Logs and installer copy display “中文 | English” pairs to speed up troubleshooting across teams.
- **Technical implementation**:
  - Language swaps happen on the main thread to avoid Tk race conditions.
  - Message boxes reuse `self.t[...]` translations to match on-screen copy.

### Feature 3: Theme Switching & Visual Consistency
- **Summary**: Added a one-click Light/Dark toggle with synchronized button labels and palette changes.
- **Pain points solved**: Users working in bright offices or dark studios had to rely on OS-level tweaks instead of adjusting the app.
- **Technical implementation**:
  - `toggle_theme` flips `ctk.set_appearance_mode` and rewrites button text (Dark ↔ Light).
  - Each entry in `COLORS` supplies `(light, dark)` tuples so widgets always use the right color for the active theme.

### Feature 4: Installation UX & Error Handling Enhancements
- **Summary**: The FFmpeg installer dialog is center-aligned, grabs focus, reports progress bilingually, and surfaces errors with detailed logs.
- **Pain points solved**: Earlier windows could hide behind the main app, and single-language errors were hard to interpret.
- **Technical implementation**:
  - Installer callbacks post updates via `dialog.after`, keeping UI thread-safe.
  - Success/failure flows show bilingual message boxes and call `sys.exit(0)` when a restart is required.

## v1.0.0 – Initial Feature Set

### Feature 1: M4S Video/Audio Segment Merging
- **Summary**: Users can select multiple `.m4s` fragments and merge them into a full MP4 in the chosen order.
- **Pain points solved**: Manual concat via command line was error-prone and required FFmpeg expertise.
- **Change details**:
  - Dedicated “Merge Video” and “Merge Audio” buttons provide independent outputs.
  - The file list UI highlights selection order and size so users can double-check before processing.
- **Technical implementation**:
  - `m4s_processor.merge_video_segments/merge_audio_segments` rely on FFmpeg concat with a generated file list.
  - Temporary `.txt` manifests are deleted immediately after processing.
  - A one-hour timeout guards against runaway FFmpeg jobs.

### Feature 2: Audio/Video Muxing & One-Click Automation
- **Summary**: Combine processed video/audio into one MP4 or use “One-Click” to chain video merge, audio merge, and mux automatically.
- **Pain points solved**: Multi-step CLI workflows were intimidating and easy to misconfigure.
- **Technical implementation**:
  - `merge_av` executes `ffmpeg -c:v copy -c:a aac` while surfacing stderr on failure.
  - `process_all` decides which steps are needed based on available inputs and returns the resulting file path for the GUI to display.

### Feature 3: GUI Experience
- **Summary**: Built a `customtkinter` + `tkinter` desktop UI with file pickers, progress bars, logs, and completion dialogs.
- **Pain points solved**: Non-technical users no longer need to memorize FFmpeg commands.
- **Technical implementation**:
  - `_run_task` centralizes background-thread execution, progress indicators, and success/error handling.
  - Logs show timestamps, and message boxes report saved locations or detailed failure reasons.

### Feature 4: Automatic FFmpeg Setup & Robust Error Prompts
- **Summary**: Detects FFmpeg on launch, provides an installer when missing, and surfaces bilingual error prompts for everything from Python version checks to runtime issues.
- **Pain points solved**: Installing FFmpeg manually or editing PATH settings deterred new users.
- **Technical implementation**:
  - `FFmpegInstaller` handles download, extraction, and environment-variable updates with callbacks for progress.
  - `main.py` wraps startup in layered try/except blocks, falling back to Windows MessageBox or console output if Tk isn’t available.

> Starting with v1.2.0, every new release must append a section here to keep feature evolution and technical notes in sync.

> Starting with v1.2.0, every new release must append its section here to keep feature evolution and technical notes in sync.
