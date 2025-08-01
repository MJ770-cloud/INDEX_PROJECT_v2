# VDH_SMART_DETECTOR_20250730_2215.py
# VDH Smart Status Detector - Completion Detection
# Created: July 30, 2025 - 10:15 PM Pacific
# Purpose: Detect VDH completion status and organize files for transcription

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading
from pathlib import Path
from datetime import datetime
import json
import shutil

class VDHSmartDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Smart Status Detector")
        self.root.geometry("750x550")
        
        # Configuration
        self.download_directory = ""
        self.transcription_ready = False
        
        # File analysis
        self.video_files = []
        self.total_size_mb = 0
        self.analysis_complete = False
        
        # Session tracking
        self.session_stats = {
            "scan_time": None,
            "total_files": 0,
            "total_size_mb": 0,
            "average_file_size": 0,
            "ready_for_transcription": False
        }
        
        self.setup_gui()

    def setup_gui(self):
        """Create smart detector interface"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH SMART STATUS DETECTOR",
                              bg="#2c3e50", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(expand=True)

        # Directory configuration
        config_frame = tk.LabelFrame(self.root, text="📁 Directory Configuration", 
                                    font=("Arial", 10, "bold"), padx=10, pady=5)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        dir_frame = tk.Frame(config_frame)
        dir_frame.pack(fill=tk.X)
        
        tk.Label(dir_frame, text="📁 DIYTRAX Directory:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.dir_label = tk.Label(dir_frame, text="Not selected", 
                                 fg="#e74c3c", font=("Arial", 9))
        self.dir_label.pack(side=tk.LEFT, padx=(10, 20))
        
        tk.Button(dir_frame, text="📁 SELECT",
                 command=self.select_directory,
                 bg="#3498db", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # Status detection panel
        status_frame = tk.LabelFrame(self.root, text="📊 VDH Status Detection", 
                                    font=("Arial", 10, "bold"), padx=10, pady=5)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status indicators
        indicators_frame = tk.Frame(status_frame)
        indicators_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(indicators_frame, text="🔍 Ready to scan", 
                                    font=("Arial", 11, "bold"), fg="#f39c12")
        self.status_label.pack()
        
        # File summary
        summary_frame = tk.Frame(status_frame)
        summary_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(summary_frame, text="📹 Files Found:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.files_label = tk.Label(summary_frame, text="0", 
                                   font=("Arial", 9), fg="#27ae60")
        self.files_label.grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        tk.Label(summary_frame, text="💾 Total Size:", 
                font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.size_label = tk.Label(summary_frame, text="0.0 MB", 
                                  font=("Arial", 9), fg="#9b59b6")
        self.size_label.grid(row=0, column=3, sticky="w", padx=(5, 20))
        
        tk.Label(summary_frame, text="📊 Avg Size:", 
                font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="w")
        self.avg_label = tk.Label(summary_frame, text="0.0 MB", 
                                 font=("Arial", 9), fg="#3498db")
        self.avg_label.grid(row=0, column=5, sticky="w", padx=(5, 0))

        # File analysis results
        analysis_frame = tk.LabelFrame(self.root, text="📋 File Analysis Results", 
                                      font=("Arial", 10, "bold"), padx=10, pady=5)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results text area
        self.results_text = tk.Text(analysis_frame, height=12, font=("Consolas", 8),
                                   bg="#f8f9fa", wrap="word")
        results_scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, 
                                         command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main actions
        main_actions = tk.Frame(action_frame)
        main_actions.pack(side=tk.LEFT)
        
        self.scan_btn = tk.Button(main_actions, text="🔍 SCAN VDH STATUS",
                                 command=self.scan_vdh_status,
                                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                                 state='disabled')
        self.scan_btn.pack(side=tk.LEFT, padx=2)
        
        self.organize_btn = tk.Button(main_actions, text="📁 ORGANIZE FILES",
                                     command=self.organize_for_transcription,
                                     bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                     state='disabled')
        self.organize_btn.pack(side=tk.LEFT, padx=2)
        
        self.transcribe_btn = tk.Button(main_actions, text="🚀 LAUNCH TRANSCRIPTION",
                                       command=self.launch_transcription,
                                       bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                       state='disabled')
        self.transcribe_btn.pack(side=tk.LEFT, padx=2)
        
        # Utility actions
        utility_actions = tk.Frame(action_frame)
        utility_actions.pack(side=tk.RIGHT)
        
        tk.Button(utility_actions, text="📁 OPEN FOLDER",
                 command=self.open_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_actions, text="💾 SAVE REPORT",
                 command=self.save_analysis_report,
                 bg="#34495e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        # Initialize
        self.check_default_directory()

    def check_default_directory(self):
        """Check for default DIYTRAX directory"""
        default_dir = "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX"
        if os.path.exists(default_dir):
            self.download_directory = default_dir
            self.dir_label.config(text=default_dir, fg="#27ae60")
            self.scan_btn.config(state='normal')
            self.log_result("📁 Found DIYTRAX directory: " + default_dir)
            
            # Auto-scan if files exist
            self.auto_initial_scan()

    def select_directory(self):
        """Select download directory"""
        directory = filedialog.askdirectory(
            title="Select VDH Download Directory",
            initialdir="C:/INDEX-PROJECT/TCE-MEDIA"
        )
        
        if directory:
            self.download_directory = directory
            self.dir_label.config(text=directory, fg="#27ae60")
            self.scan_btn.config(state='normal')
            self.log_result("📁 Directory selected: " + directory)

    def auto_initial_scan(self):
        """Automatically scan if files are found"""
        if self.download_directory and os.path.exists(self.download_directory):
            try:
                video_files = [f for f in os.listdir(self.download_directory) 
                              if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                
                if video_files:
                    self.log_result("🔍 Found " + str(len(video_files)) + " video files - running initial scan...")
                    self.root.after(1000, self.scan_vdh_status)  # Auto-scan after 1 second
            except Exception:
                pass

    def scan_vdh_status(self):
        """Scan current VDH download status"""
        if not self.download_directory or not os.path.exists(self.download_directory):
            messagebox.showerror("Error", "Please select a valid directory first!")
            return
        
        self.status_label.config(text="🔍 Scanning VDH status...", fg="#3498db")
        self.results_text.delete(1.0, tk.END)
        
        # Run scan in thread to prevent GUI freezing
        scan_thread = threading.Thread(target=self.perform_scan, daemon=True)
        scan_thread.start()

    def perform_scan(self):
        """Perform the actual file scan"""
        try:
            self.session_stats["scan_time"] = datetime.now()
            
            # Find all video files
            video_files = []
            for filename in os.listdir(self.download_directory):
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                    file_path = os.path.join(self.download_directory, filename)
                    file_info = {
                        'name': filename,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': os.path.getmtime(file_path)
                    }
                    video_files.append(file_info)
            
            # Sort by modification time (newest first)
            video_files.sort(key=lambda x: x['modified'], reverse=True)
            
            self.video_files = video_files
            total_size = sum(f['size'] for f in video_files)
            self.total_size_mb = total_size / (1024 * 1024)
            
            # Update session stats
            self.session_stats["total_files"] = len(video_files)
            self.session_stats["total_size_mb"] = self.total_size_mb
            self.session_stats["average_file_size"] = (self.total_size_mb / len(video_files)) if video_files else 0
            
            # Update UI on main thread
            self.root.after(0, self.update_scan_results)
            
        except Exception as e:
            self.root.after(0, lambda: self.log_result("❌ Scan error: " + str(e)))

    def update_scan_results(self):
        """Update UI with scan results"""
        file_count = len(self.video_files)
        
        # Update summary labels
        self.files_label.config(text=str(file_count))
        self.size_label.config(text=str(round(self.total_size_mb, 1)) + " MB")
        avg_size = self.session_stats["average_file_size"]
        self.avg_label.config(text=str(round(avg_size, 1)) + " MB")
        
        # Generate detailed analysis
        analysis_text = "🎯 VDH DOWNLOAD STATUS ANALYSIS\n"
        analysis_text += "=" * 50 + "\n"
        analysis_text += "📅 Scan Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        analysis_text += "📁 Directory: " + self.download_directory + "\n\n"
        
        analysis_text += "📊 SUMMARY:\n"
        analysis_text += "📹 Total Video Files: " + str(file_count) + "\n"
        analysis_text += "💾 Total Size: " + str(round(self.total_size_mb, 1)) + " MB\n"
        analysis_text += "📊 Average File Size: " + str(round(avg_size, 1)) + " MB\n\n"
        
        # Determine VDH status
        if file_count >= 5:
            vdh_status = "✅ VDH DOWNLOADS DETECTED - READY FOR PROCESSING"
            self.status_label.config(text="✅ Files ready for transcription", fg="#27ae60")
            self.organize_btn.config(state='normal')
            self.transcription_ready = True
        elif file_count > 0:
            vdh_status = "⏳ PARTIAL DOWNLOADS - MAY NEED MORE FILES"
            self.status_label.config(text="⏳ Partial downloads detected", fg="#f39c12")
        else:
            vdh_status = "❌ NO VIDEO FILES FOUND"
            self.status_label.config(text="❌ No video files found", fg="#e74c3c")
        
        analysis_text += "🎯 VDH STATUS: " + vdh_status + "\n\n"
        
        # File details
        if self.video_files:
            analysis_text += "📋 FILE DETAILS (newest first):\n"
            analysis_text += "-" * 50 + "\n"
            
            for i, file_info in enumerate(self.video_files, 1):
                size_mb = file_info['size'] / (1024 * 1024)
                mod_time = datetime.fromtimestamp(file_info['modified'])
                
                analysis_text += str(i) + ". " + file_info['name'] + "\n"
                analysis_text += "   Size: " + str(round(size_mb, 1)) + " MB\n"
                analysis_text += "   Modified: " + mod_time.strftime("%m/%d %H:%M:%S") + "\n\n"
        
        # Recommendations
        analysis_text += "💡 RECOMMENDATIONS:\n"
        if self.transcription_ready:
            analysis_text += "✅ Files are ready for transcription processing\n"
            analysis_text += "✅ Click 'ORGANIZE FILES' to prepare for batch transcription\n"
            analysis_text += "✅ Use 'LAUNCH TRANSCRIPTION' to start processing\n"
        else:
            analysis_text += "⚠️ Consider downloading more content if incomplete\n"
            analysis_text += "⚠️ Check VDH interface for remaining downloads\n"
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, analysis_text)
        
        self.analysis_complete = True
        self.log_result("🔍 Scan completed: " + str(file_count) + " files found")

    def organize_for_transcription(self):
        """Organize files for transcription processing"""
        if not self.transcription_ready:
            messagebox.showwarning("Not Ready", "Files are not ready for organization yet")
            return
        
        try:
            # Create organized structure
            base_path = Path(self.download_directory)
            organized_path = base_path / "organized_for_transcription"
            organized_path.mkdir(exist_ok=True)
            
            # Create transcription input list
            input_file_path = base_path / "transcription_batch_input.txt"
            
            with open(input_file_path, 'w') as f:
                for file_info in self.video_files:
                    f.write(file_info['path'] + "\n")
            
            success_msg = ("📁 Files organized for transcription!\n\n" +
                          "✅ Batch input file created: transcription_batch_input.txt\n" +
                          "✅ " + str(len(self.video_files)) + " files ready for processing\n" +
                          "✅ Total size: " + str(round(self.total_size_mb, 1)) + " MB\n\n" +
                          "Ready to launch transcription engine!")
            
            messagebox.showinfo("Organization Complete", success_msg)
            self.transcribe_btn.config(state='normal')
            self.log_result("📁 Files organized for transcription")
            
        except Exception as e:
            messagebox.showerror("Organization Error", "Failed to organize files: " + str(e))

    def launch_transcription(self):
        """Launch the transcription engine"""
        engine_path = Path("C:/ENGINE-PROJECT/src/engines/working/openai_transcription_engine_v16_INDEX_ready_20250720_0748.py")
        
        if not engine_path.exists():
            messagebox.showwarning("Engine Not Found", 
                "Transcription engine not found at expected location:\n" + str(engine_path))
            return
        
        try:
            import subprocess
            
            # Launch transcription engine
            subprocess.Popen([
                "powershell.exe", 
                "-Command", 
                "cd '" + str(engine_path.parent) + "'; python '" + engine_path.name + "'"
            ])
            
            success_msg = ("🚀 Transcription Engine Launched!\n\n" +
                          "✅ Processing " + str(len(self.video_files)) + " video files\n" +
                          "✅ Expected output: High-quality transcripts with timestamps\n" +
                          "✅ Monitor engine output for progress\n\n" +
                          "Files will be ready for INDEX development!")
            
            messagebox.showinfo("Transcription Started", success_msg)
            self.log_result("🚀 Transcription engine launched successfully")
            
        except Exception as e:
            messagebox.showerror("Launch Error", "Failed to launch transcription: " + str(e))

    def save_analysis_report(self):
        """Save analysis report to file"""
        if not self.analysis_complete:
            messagebox.showwarning("No Analysis", "Please run a scan first")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = "VDH_analysis_report_" + timestamp + ".txt"
            
            with open(report_file, 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))
            
            self.log_result("💾 Analysis report saved: " + report_file)
            messagebox.showinfo("Report Saved", "Analysis report saved as: " + report_file)
            
        except Exception as e:
            messagebox.showerror("Save Error", "Failed to save report: " + str(e))

    def open_directory(self):
        """Open download directory"""
        if self.download_directory and os.path.exists(self.download_directory):
            os.startfile(self.download_directory)
        else:
            messagebox.showwarning("Error", "Directory not found")

    def log_result(self, message):
        """Log a result message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print("[" + timestamp + "] " + message)
        
        # Also update status if it's a significant event
        if "error" in message.lower():
            self.status_label.config(text="❌ Error occurred", fg="#e74c3c")
        elif "completed" in message.lower() or "found" in message.lower():
            pass  # Status is handled elsewhere for these

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 VDH Smart Status Detector")
    print("Created: July 30, 2025 - 10:15 PM Pacific") 
    print("Purpose: Detect VDH completion and organize for transcription")
    print()
    
    try:
        app = VDHSmartDetector()
        app.run()
    except Exception as e:
        print("❌ Error: " + str(e))
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())