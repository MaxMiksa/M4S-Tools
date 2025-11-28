import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";

// --- Python Script Content ---
const PYTHON_SCRIPT = `import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
import re
import sys

# M4S Merger Tool - Generated Python Script

class M4SMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M4S Merger Tool")
        self.root.geometry("800x650")
        self.root.configure(bg="#f0f0f0")

        # Variables
        self.mode_var = tk.StringVar(value="merge")
        self.output_path_var = tk.StringVar()
        self.output_filename_var = tk.StringVar(value="output.mp4")
        self.files_list = []
        self.video_track = tk.StringVar()
        self.audio_track = tk.StringVar()

        self.create_styles()
        self.create_widgets()
        self.check_ffmpeg()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('TLabel', font=('Segoe UI', 10), background="#f0f0f0")
        style.configure('TLabelframe', font=('Segoe UI', 10, 'bold'), background="#f0f0f0")
        style.configure('TLabelframe.Label', background="#f0f0f0")
        style.configure('TRadiobutton', font=('Segoe UI', 10), background="#f0f0f0")

    def check_ffmpeg(self):
        # Check if ffmpeg exists in current directory or path
        self.ffmpeg_exe = "ffmpeg"
        local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            self.ffmpeg_exe = local_ffmpeg
        else:
            # Try checking system path
            try:
                subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=self.get_startup_info())
            except FileNotFoundError:
                self.log("ERROR: ffmpeg.exe not found! Please place it in the app directory.")
                messagebox.showwarning("Missing Component", "ffmpeg.exe not found.\\nPlease download FFmpeg and place 'ffmpeg.exe' in the same folder as this application.")

    def get_startup_info(self):
        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return info
        return None

    def create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Header
        tk.Label(main_frame, text="M4S Merger Tool", font=("Segoe UI", 20, "bold"), bg="#f0f0f0", fg="#333").pack(pady=(0, 20))

        # 2. Mode Selection
        mode_frame = ttk.LabelFrame(main_frame, text="Operation Mode")
        mode_frame.pack(fill=tk.X, pady=5)
        
        inner_mode = ttk.Frame(mode_frame, padding=10)
        inner_mode.pack(fill=tk.X)
        ttk.Radiobutton(inner_mode, text="Merge M4S Segments (Single Track)", variable=self.mode_var, value="merge", command=self.update_ui).pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(inner_mode, text="Mux Video & Audio (Combine Tracks)", variable=self.mode_var, value="mux", command=self.update_ui).pack(side=tk.LEFT, padx=20)

        # 3. Operations Area
        self.ops_frame = ttk.LabelFrame(main_frame, text="Input Selection")
        self.ops_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.ops_inner = ttk.Frame(self.ops_frame, padding=15)
        self.ops_inner.pack(fill=tk.BOTH, expand=True)

        # 4. Output Settings
        out_frame = ttk.LabelFrame(main_frame, text="Output Configuration")
        out_frame.pack(fill=tk.X, pady=5)
        out_inner = ttk.Frame(out_frame, padding=15)
        out_inner.pack(fill=tk.X)

        ttk.Label(out_inner, text="Output Folder:").grid(row=0, column=0, sticky="e", padx=5)
        ttk.Entry(out_inner, textvariable=self.output_path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(out_inner, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2, padx=5)

        ttk.Label(out_inner, text="Filename:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(out_inner, textvariable=self.output_filename_var, width=50).grid(row=1, column=1, padx=5, pady=5)

        # 5. Execute
        self.btn_run = tk.Button(main_frame, text="START PROCESSING", bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", command=self.start_thread)
        self.btn_run.pack(fill=tk.X, pady=15, ipady=5)

        # 6. Status/Log
        log_frame = ttk.LabelFrame(main_frame, text="Process Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled', font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initial UI render
        self.update_ui()

    def update_ui(self):
        for widget in self.ops_inner.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()
        if mode == "merge":
            ttk.Button(self.ops_inner, text="Select M4S Files / Folder", command=self.browse_m4s_files).pack(anchor="w")
            self.file_list_label = ttk.Label(self.ops_inner, text="No files selected", wraplength=700)
            self.file_list_label.pack(anchor="w", pady=10)
        else:
            # Mux UI
            f1 = ttk.Frame(self.ops_inner)
            f1.pack(fill=tk.X, pady=5)
            ttk.Label(f1, text="Video MP4:", width=15, anchor="e").pack(side=tk.LEFT)
            ttk.Entry(f1, textvariable=self.video_track, width=55).pack(side=tk.LEFT, padx=5)
            ttk.Button(f1, text="Browse", command=lambda: self.browse_file(self.video_track)).pack(side=tk.LEFT)

            f2 = ttk.Frame(self.ops_inner)
            f2.pack(fill=tk.X, pady=5)
            ttk.Label(f2, text="Audio MP4:", width=15, anchor="e").pack(side=tk.LEFT)
            ttk.Entry(f2, textvariable=self.audio_track, width=55).pack(side=tk.LEFT, padx=5)
            ttk.Button(f2, text="Browse", command=lambda: self.browse_file(self.audio_track)).pack(side=tk.LEFT)

    def browse_m4s_files(self):
        files = filedialog.askopenfilenames(title="Select M4S Files", filetypes=[("M4S Files", "*.m4s"), ("All Files", "*.*")])
        if files:
            self.files_list = list(files)
            count = len(self.files_list)
            self.file_list_label.config(text=f"{count} files selected.\\nFirst: {os.path.basename(self.files_list[0])}...")
            if not self.output_path_var.get():
                self.output_path_var.set(os.path.dirname(self.files_list[0]))

    def browse_output_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.output_path_var.set(d)

    def browse_file(self, var):
        f = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
        if f:
            var.set(f)
            if not self.output_path_var.get():
                self.output_path_var.set(os.path.dirname(f))

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def natural_sort_key(self, s):
        # Natural sort helper
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', s)]

    def start_thread(self):
        t = threading.Thread(target=self.run_process)
        t.start()

    def run_process(self):
        self.btn_run.config(state='disabled', text="PROCESSING...")
        try:
            out_dir = self.output_path_var.get()
            out_name = self.output_filename_var.get()
            if not out_dir:
                out_dir = os.getcwd()
            
            output_full_path = os.path.join(out_dir, out_name)
            mode = self.mode_var.get()
            
            if mode == "merge":
                if not self.files_list:
                    messagebox.showerror("Error", "No M4S files selected!")
                    return
                
                self.log(">>> Starting Merge Process")
                self.log(f"Sorting {len(self.files_list)} files...")
                sorted_files = sorted(self.files_list, key=self.natural_sort_key)
                
                list_file = os.path.join(out_dir, "temp_ffmpeg_list.txt")
                self.log(f"Creating list file: {list_file}")
                
                with open(list_file, 'w', encoding='utf-8') as f:
                    for path in sorted_files:
                        safe_path = path.replace("'", "'\\\\''")
                        f.write(f"file '{safe_path}'\\n")
                
                cmd = [
                    self.ffmpeg_exe, "-f", "concat", "-safe", "0",
                    "-i", list_file, "-c", "copy", output_full_path, "-y"
                ]
                self.run_ffmpeg(cmd)
                
                if os.path.exists(list_file):
                    os.remove(list_file)
                    
            elif mode == "mux":
                v = self.video_track.get()
                a = self.audio_track.get()
                if not v or not a:
                    messagebox.showerror("Error", "Select both video and audio files.")
                    return
                
                self.log(">>> Starting Mux Process")
                cmd = [
                    self.ffmpeg_exe, "-i", v, "-i", a,
                    "-c", "copy", output_full_path, "-y"
                ]
                self.run_ffmpeg(cmd)
                
            self.log(">>> SUCCESS!")
            messagebox.showinfo("Success", f"File saved to:\\n{output_full_path}")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_run.config(state='normal', text="START PROCESSING")

    def run_ffmpeg(self, cmd):
        self.log(f"Executing: {' '.join(cmd)}")
        startup_info = self.get_startup_info()
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            startupinfo=startup_info
        )
        for line in process.stdout:
            self.log(line.strip())
        process.wait()
        if process.returncode != 0:
            raise Exception("FFmpeg returned error code")

if __name__ == "__main__":
    root = tk.Tk()
    app = M4SMergerApp(root)
    root.mainloop()
`;

// --- React App Components ---

const App = () => {
  const [activeTab, setActiveTab] = useState<"gui" | "code">("gui");

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={{ 
        backgroundColor: "#2d2d2d", 
        padding: "1rem 2rem", 
        borderBottom: "1px solid #3d3d3d",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{ 
            width: "32px", height: "32px", 
            background: "linear-gradient(135deg, #FF6B6B, #4ECDC4)", 
            borderRadius: "6px" 
          }}></div>
          <h1 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 600 }}>M4S Merger Tool</h1>
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <TabButton active={activeTab === "gui"} onClick={() => setActiveTab("gui")}>
            Web Preview
          </TabButton>
          <TabButton active={activeTab === "code"} onClick={() => setActiveTab("code")}>
            Get Python Code
          </TabButton>
        </div>
      </header>

      <main style={{ flex: 1, overflow: "hidden", display: "flex" }}>
        {activeTab === "gui" ? <GuiPreview /> : <CodeView />}
      </main>
    </div>
  );
};

const TabButton = ({ active, children, onClick }: { active: boolean, children?: React.ReactNode, onClick: () => void }) => (
  <button
    onClick={onClick}
    style={{
      background: active ? "#444" : "transparent",
      border: "none",
      color: active ? "#fff" : "#aaa",
      padding: "0.5rem 1rem",
      borderRadius: "4px",
      cursor: "pointer",
      fontWeight: 500,
      transition: "all 0.2s"
    }}
  >
    {children}
  </button>
);

// --- GUI Preview Mockup ---
const GuiPreview = () => {
  const [mode, setMode] = useState<"merge" | "mux">("merge");
  const [logs, setLogs] = useState<string[]>([]);
  const [files, setFiles] = useState<FileList | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleStart = async () => {
    setIsProcessing(true);
    setLogs([]);
    addLog(">>> Starting Process");

    if (mode === "merge") {
      if (!files || files.length === 0) {
        addLog("ERROR: No files selected.");
        setIsProcessing(false);
        return;
      }
      addLog(`Selected ${files.length} files.`);
      await delay(800);
      addLog("Sorting files naturally...");
      
      // Simulate sorting logic for demo
      const fileNames = Array.from(files).map((f: any) => f.name);
      const sortedNames = fileNames.sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }));
      
      addLog(`First file: ${sortedNames[0]}`);
      addLog(`Last file: ${sortedNames[sortedNames.length - 1]}`);
      
      await delay(1000);
      addLog("Generating temp_ffmpeg_list.txt...");
      await delay(800);
      addLog("Executing FFmpeg concat (simulation)...");
      addLog("Command: ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4");
    } else {
      addLog("Validating inputs...");
      await delay(600);
      addLog("Executing FFmpeg mux (simulation)...");
      addLog("Command: ffmpeg -i video.mp4 -i audio.mp4 -c copy output.mp4");
    }

    await delay(1500);
    addLog("---------------------------------------------------");
    addLog("NOTE: Browser cannot execute local FFmpeg binaries.");
    addLog("To run this for real, please download the Python Script");
    addLog("from the 'Get Python Code' tab and run it locally.");
    addLog("---------------------------------------------------");
    setIsProcessing(false);
  };

  return (
    <div style={{ flex: 1, display: "flex", justifyContent: "center", padding: "2rem", overflowY: "auto", background: "#252526" }}>
      <div style={{ 
        width: "100%", maxWidth: "800px", 
        background: "#f0f0f0", color: "#333", 
        borderRadius: "8px", boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
        display: "flex", flexDirection: "column",
        minHeight: "600px"
      }}>
        {/* Mock Window Title Bar */}
        <div style={{ 
          background: "#e0e0e0", padding: "0.5rem 1rem", 
          borderTopLeftRadius: "8px", borderTopRightRadius: "8px",
          borderBottom: "1px solid #ccc", display: "flex", alignItems: "center"
        }}>
          <span style={{ fontSize: "0.9rem", fontWeight: 600, color: "#555" }}>M4S Merger Tool (Preview)</span>
        </div>

        <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "20px", flex: 1 }}>
          
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: "10px" }}>
            <h2 style={{ margin: 0, fontSize: "24px", color: "#333" }}>M4S Merger Tool</h2>
          </div>

          {/* Mode Selection */}
          <fieldset style={{ border: "1px solid #ccc", padding: "15px", borderRadius: "4px" }}>
            <legend style={{ padding: "0 5px", fontWeight: "bold", color: "#555" }}>Operation Mode</legend>
            <div style={{ display: "flex", gap: "30px" }}>
              <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                <input type="radio" checked={mode === "merge"} onChange={() => setMode("merge")} style={{ marginRight: "8px" }} />
                Merge M4S Segments
              </label>
              <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                <input type="radio" checked={mode === "mux"} onChange={() => setMode("mux")} style={{ marginRight: "8px" }} />
                Mux Video & Audio
              </label>
            </div>
          </fieldset>

          {/* Input Area */}
          <fieldset style={{ border: "1px solid #ccc", padding: "15px", borderRadius: "4px", flex: 1 }}>
            <legend style={{ padding: "0 5px", fontWeight: "bold", color: "#555" }}>Input Selection</legend>
            
            {mode === "merge" ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                  <label 
                    htmlFor="file-upload"
                    style={{ 
                      background: "#e1e1e1", border: "1px solid #999", 
                      padding: "5px 15px", cursor: "pointer", borderRadius: "2px",
                      fontSize: "13px"
                    }}
                  >
                    Select M4S Files...
                  </label>
                  <input 
                    id="file-upload" 
                    type="file" 
                    multiple 
                    accept=".m4s"
                    onChange={(e) => setFiles(e.target.files)}
                    style={{ display: "none" }} 
                  />
                  <span style={{ fontSize: "13px", color: "#666" }}>
                    {files ? `${files.length} files selected` : "No files selected"}
                  </span>
                </div>
                {files && files.length > 0 && (
                   <div style={{ fontSize: "12px", color: "#888", maxHeight: "60px", overflow: "hidden" }}>
                     Example: {files[0].name}, ...
                   </div>
                )}
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ width: "80px", textAlign: "right", fontSize: "14px" }}>Video MP4:</span>
                  <input type="text" readOnly placeholder="C:\path\to\video.mp4" style={{ flex: 1, padding: "4px" }} />
                  <button style={{ padding: "2px 10px" }}>Browse</button>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ width: "80px", textAlign: "right", fontSize: "14px" }}>Audio MP4:</span>
                  <input type="text" readOnly placeholder="C:\path\to\audio.mp4" style={{ flex: 1, padding: "4px" }} />
                  <button style={{ padding: "2px 10px" }}>Browse</button>
                </div>
              </div>
            )}
          </fieldset>

          {/* Output Config */}
          <fieldset style={{ border: "1px solid #ccc", padding: "15px", borderRadius: "4px" }}>
            <legend style={{ padding: "0 5px", fontWeight: "bold", color: "#555" }}>Output Configuration</legend>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ width: "80px", textAlign: "right", fontSize: "14px" }}>Folder:</span>
                  <input type="text" readOnly placeholder="C:\Output" style={{ flex: 1, padding: "4px" }} />
                  <button style={{ padding: "2px 10px" }}>Browse</button>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ width: "80px", textAlign: "right", fontSize: "14px" }}>Filename:</span>
                  <input type="text" defaultValue="output.mp4" style={{ flex: 1, padding: "4px" }} />
                </div>
              </div>
          </fieldset>

          {/* Action Button */}
          <button 
            onClick={handleStart}
            disabled={isProcessing}
            style={{ 
              background: isProcessing ? "#999" : "#28a745", 
              color: "white", border: "none", padding: "12px", 
              fontSize: "16px", fontWeight: "bold", cursor: "pointer",
              borderRadius: "4px",
              opacity: isProcessing ? 0.7 : 1
            }}
          >
            {isProcessing ? "PROCESSING..." : "START PROCESSING"}
          </button>

          {/* Log Area */}
          <div style={{ border: "1px solid #999", height: "120px", background: "white", padding: "5px", overflowY: "scroll", fontFamily: "Consolas, monospace", fontSize: "12px" }}>
            {logs.length === 0 && <span style={{ color: "#aaa" }}>Ready...</span>}
            {logs.map((log, i) => <div key={i}>{log}</div>)}
            <div ref={logEndRef} />
          </div>

        </div>
      </div>
    </div>
  );
};

// --- Code Viewer & Downloader ---
const CodeView = () => {
  const downloadCode = () => {
    const blob = new Blob([PYTHON_SCRIPT], { type: "text/x-python" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "m4s_merger.py";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "#1e1e1e", color: "#d4d4d4" }}>
      <div style={{ padding: "1.5rem", borderBottom: "1px solid #333", background: "#252526" }}>
        <h2 style={{ marginTop: 0, color: "#fff" }}>Python Source Code</h2>
        <p style={{ color: "#aaa", marginBottom: "1rem" }}>
          This script implements the full requirement using <code>tkinter</code> and <code>subprocess</code>.
          It is designed to run on Windows and requires FFmpeg.
        </p>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button 
            onClick={downloadCode}
            style={{
              background: "#0e639c", color: "white", border: "none",
              padding: "0.6rem 1.2rem", borderRadius: "4px", cursor: "pointer",
              fontSize: "14px", fontWeight: "bold", display: "flex", alignItems: "center", gap: "8px"
            }}
          >
            Download .py File
          </button>
        </div>
        <div style={{ marginTop: "1rem", fontSize: "13px", color: "#aaa", background: "#333", padding: "10px", borderRadius: "4px" }}>
            <strong>Build Instructions (PyInstaller):</strong>
            <br />
            <code>pip install pyinstaller</code>
            <br />
            <code>pyinstaller --noconsole --onefile m4s_merger.py</code>
        </div>
      </div>
      <div style={{ flex: 1, overflow: "auto", padding: "1rem" }}>
        <pre style={{ margin: 0, fontFamily: "Consolas, 'Courier New', monospace", fontSize: "13px", lineHeight: "1.5" }}>
          {PYTHON_SCRIPT}
        </pre>
      </div>
    </div>
  );
};

const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

const root = createRoot(document.getElementById("root")!);
root.render(<App />);