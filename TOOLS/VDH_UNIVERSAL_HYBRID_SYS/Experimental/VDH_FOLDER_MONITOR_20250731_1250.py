# VDH_FOLDER_MONITOR_20250731_1250.py
# VDH Folder Monitor - Real-time Download Progress Tracking
# Created: July 31, 2025 - 12:50 PM Pacific
# Purpose: Monitor VDH downloads with progress bars - no Selenium conflicts

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading
from pathlib import Path
from datetime import datetime
import json
import glob
from mutagen import File as MutagenFile

class VDHFolderMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Folder Monitor")
        self.root.geometry("800x650")
        
        # Configuration
        self.download_directory = ""
        self.is_monitoring = False
        self.videos_found = 0
        self.videos_completed = 0
        self.last_file_count = 0
        
        # Progress tracking
        self.current_video = ""
        self.total_progress = 0
        self.current_file_progress = 0
        
        # File tracking
        self.completed_files = set()
        self.in_progress_files = {}
        self.file_history = []
        
        # Monitoring settings
        self.scan_interval = 2  # seconds between scans
        self.size_stable_threshold = 3  # scans with same size = complete
        
        self.setup_gui()

    def setup_gui(self):
        """Create folder monitor interface"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH FOLDER MONITOR",
                              bg="#2c3e50", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(expand=True)

        # Directory configuration
        config_frame = tk.LabelFrame(self.root, text="📁 Directory Configuration", 
                                    font=("Arial", 10, "bold"), padx=10, pady=5)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        dir_frame = tk.Frame(config_frame)
        dir_frame.pack(fill=tk.X)
        
        tk.Label(dir_frame, text="📁 Monitor Directory:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.dir_label = tk.Label(dir_frame, text="Not selected", 
                                 fg="#e74c3c", font=("Arial", 9))
        self.dir_label.pack(side=tk.LEFT, padx=(10, 20))
        
        tk.Button(dir_frame, text="📁 SELECT DIRECTORY",
                 command=self.select_directory,
                 bg="#3498db", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # Progress tracking panel  
        progress_frame = tk.LabelFrame(self.root, text="📊 Download Progress", 
                                      font=("Arial", 10, "bold"), padx=10, pady=5)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Overall progress
        overall_frame = tk.Frame(progress_frame)
        overall_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(overall_frame, text="📊 Session Progress:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.overall_progress = ttk.Progressbar(overall_frame, mode='determinate', length=400)
        self.overall_progress.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        self.overall_percent = tk.Label(overall_frame, text="0%", 
                                       font=("Arial", 9, "bold"), fg="#3498db", 
                                       relief=tk.SUNKEN, width=5)
        self.overall_percent.pack(side=tk.RIGHT)
        
        # Current file progress
        current_frame = tk.Frame(progress_frame)
        current_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(current_frame, text="📹 Current File:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.current_progress = ttk.Progressbar(current_frame, mode='determinate', length=400)
        self.current_progress.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        self.current_percent = tk.Label(current_frame, text="0%", 
                                       font=("Arial", 9, "bold"), fg="#27ae60", 
                                       relief=tk.SUNKEN, width=5)
        self.current_percent.pack(side=tk.RIGHT)

        # Real-time statistics
        stats_frame = tk.LabelFrame(self.root, text="📊 Real-time Statistics", 
                                   font=("Arial", 10, "bold"), padx=10, pady=5)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, pady=5)
        
        tk.Label(stats_grid, text="📁 Files Found:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.found_label = tk.Label(stats_grid, text="0", 
                                   font=("Arial", 9), fg="#3498db")
        self.found_label.grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        tk.Label(stats_grid, text="✅ Completed:", 
                font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.completed_label = tk.Label(stats_grid, text="0", 
                                       font=("Arial", 9), fg="#27ae60")
        self.completed_label.grid(row=0, column=3, sticky="w", padx=(5, 20))
        
        tk.Label(stats_grid, text="⏳ In Progress:", 
                font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="w")
        self.progress_label = tk.Label(stats_grid, text="0", 
                                      font=("Arial", 9), fg="#f39c12")
        self.progress_label.grid(row=0, column=5, sticky="w", padx=(5, 20))
        
        tk.Label(stats_grid, text="💾 Total Size:", 
                font=("Arial", 9, "bold")).grid(row=0, column=6, sticky="w")
        self.size_label = tk.Label(stats_grid, text="0 MB", 
                                  font=("Arial", 9), fg="#9b59b6")
        self.size_label.grid(row=0, column=7, sticky="w", padx=(5, 0))

        # Status display
        status_frame = tk.Frame(stats_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="🔍 Ready to monitor", 
                                    font=("Arial", 11, "bold"), fg="#f39c12")
        self.status_label.pack()

        # Activity log
        log_frame = tk.LabelFrame(self.root, text="📋 Activity Log", 
                                 font=("Arial", 10, "bold"), padx=10, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        log_container = tk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=8, font=("Consolas", 8),
                               bg="#f8f9fa", wrap="word")
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main controls
        main_controls = tk.Frame(control_frame)
        main_controls.pack(side=tk.LEFT)
        
        self.start_btn = tk.Button(main_controls, text="🔍 START MONITORING",
                                  command=self.start_monitoring,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  state='disabled')
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(main_controls, text="⏹️ STOP",
                                 command=self.stop_monitoring,
                                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                 state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.analyze_btn = tk.Button(main_controls, text="📊 ANALYZE CURRENT",
                                    command=self.analyze_current_files,
                                    bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                                    state='disabled')
        self.analyze_btn.pack(side=tk.LEFT, padx=2)
        
        # Utility controls
        utility_controls = tk.Frame(control_frame)
        utility_controls.pack(side=tk.RIGHT)
        
        tk.Button(utility_controls, text="📋 EXPORT LOG",
                 command=self.export_log,
                 bg="#e67e22", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="💾 SAVE REPORT",
                 command=self.generate_report,
                 bg="#34495e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="📁 OPEN FOLDER",
                 command=self.open_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        # Initialize
        self.check_default_directory()

    def check_default_directory(self):
        """Check for default DIYTRAX directory"""
        default_dir = "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX"
        if os.path.exists(default_dir):
            self.download_directory = default_dir
            self.dir_label.config(text=default_dir, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.analyze_btn.config(state='normal')
            self.log_message("📁 Found DIYTRAX directory: " + default_dir)
            
            # Auto-analyze existing files
            self.analyze_current_files()

    def select_directory(self):
        """Select download directory"""
        directory = filedialog.askdirectory(
            title="Select VDH Download Directory",
            initialdir="C:/INDEX-PROJECT/TCE-MEDIA"
        )
        
        if directory:
            self.download_directory = directory
            self.dir_label.config(text=directory, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.analyze_btn.config(state='normal')
            self.log_message("📁 Directory selected: " + directory)

    def update_progress(self, overall_percent, current_percent=0):
        """Update progress bars and percentages"""
        self.overall_progress['value'] = min(100, max(0, overall_percent))
        self.overall_percent.config(text=str(int(overall_percent)) + "%")
        
        self.current_progress['value'] = min(100, max(0, current_percent))
        self.current_percent.config(text=str(int(current_percent)) + "%")
        
        self.root.update_idletasks()

    def update_stats(self, found=None, completed=None, in_progress=None, total_size=None):
        """Update statistics display"""
        if found is not None:
            self.videos_found = found
            self.found_label.config(text=str(found))
        
        if completed is not None:
            self.videos_completed = completed
            self.completed_label.config(text=str(completed))
        
        if in_progress is not None:
            self.progress_label.config(text=str(in_progress))
        
        if total_size is not None:
            size_mb = total_size / (1024 * 1024)
            self.size_label.config(text=str(round(size_mb, 1)) + " MB")

    def get_file_info(self, file_path):
        """Get comprehensive file information"""
        try:
            stat = os.stat(file_path)
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime
            }
            
            # Try to extract duration for progress estimation
            try:
                audio_file = MutagenFile(file_path)
                if audio_file and hasattr(audio_file, 'info'):
                    file_info['duration'] = getattr(audio_file.info, 'length', 0)
                    file_info['bitrate'] = getattr(audio_file.info, 'bitrate', 0)
            except:
                file_info['duration'] = 0
                file_info['bitrate'] = 0
            
            return file_info
            
        except Exception as e:
            self.log_message("⚠️ Error reading file info: " + str(e))
            return None

    def scan_directory(self):
        """Scan directory for video files and track progress"""
        if not self.download_directory or not os.path.exists(self.download_directory):
            return [], [], 0
        
        try:
            # Find all video files
            video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.mp3', '*.wav', '*.m4a']
            all_files = []
            
            for ext in video_extensions:
                pattern = os.path.join(self.download_directory, ext)
                all_files.extend(glob.glob(pattern))
            
            # Analyze each file
            completed_files = []
            in_progress_files = []
            total_size = 0
            
            for file_path in all_files:
                file_info = self.get_file_info(file_path)
                if not file_info:
                    continue
                
                total_size += file_info['size']
                
                # Check if file is still being downloaded
                file_key = file_path
                current_size = file_info['size']
                
                if file_key in self.in_progress_files:
                    prev_size, stability_count = self.in_progress_files[file_key]
                    
                    if current_size == prev_size:
                        # Size hasn't changed
                        stability_count += 1
                        self.in_progress_files[file_key] = (current_size, stability_count)
                        
                        if stability_count >= self.size_stable_threshold:
                            # File appears complete
                            completed_files.append(file_info)
                            del self.in_progress_files[file_key]
                            self.completed_files.add(file_key)
                            
                            self.log_message("✅ Download completed: " + file_info['name'])
                        else:
                            in_progress_files.append(file_info)
                    else:
                        # Size changed, still downloading
                        self.in_progress_files[file_key] = (current_size, 0)
                        in_progress_files.append(file_info)
                        
                        # Estimate progress if we have previous size
                        if prev_size > 0:
                            growth_rate = current_size - prev_size
                            self.log_message("📥 Downloading: " + file_info['name'] + 
                                           " (+" + str(round(growth_rate/(1024*1024), 1)) + " MB)")
                
                elif file_key in self.completed_files:
                    # Already completed
                    completed_files.append(file_info)
                
                else:
                    # New file detected
                    if current_size > 0:
                        self.in_progress_files[file_key] = (current_size, 0)
                        in_progress_files.append(file_info)
                        self.log_message("🆕 New download detected: " + file_info['name'])
            
            return completed_files, in_progress_files, total_size
            
        except Exception as e:
            self.log_message("❌ Directory scan error: " + str(e))
            return [], [], 0

    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                completed, in_progress, total_size = self.scan_directory()
                
                total_files = len(completed) + len(in_progress)
                completed_count = len(completed)
                in_progress_count = len(in_progress)
                
                # Update statistics
                self.root.after(0, lambda: self.update_stats(
                    found=total_files,
                    completed=completed_count,
                    in_progress=in_progress_count,
                    total_size=total_size
                ))
                
                # Calculate progress
                if total_files > 0:
                    overall_progress = (completed_count / total_files) * 100
                    
                    # Current file progress estimation
                    current_progress = 0
                    if in_progress:
                        # Use the largest in-progress file as current
                        current_file = max(in_progress, key=lambda x: x['size'])
                        current_name = current_file['name']
                        
                        # Estimate progress based on typical file sizes
                        if completed:
                            avg_completed_size = sum(f['size'] for f in completed) / len(completed)
                            if avg_completed_size > 0:
                                current_progress = min(100, (current_file['size'] / avg_completed_size) * 100)
                        
                        self.root.after(0, lambda: self.status_label.config(
                            text="📥 Downloading: " + current_name[:40] + "...", fg="#3498db"))
                    else:
                        self.root.after(0, lambda: self.status_label.config(
                            text="✅ All downloads complete", fg="#27ae60"))
                    
                    self.root.after(0, lambda: self.update_progress(overall_progress, current_progress))
                
                # Wait before next scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message("❌ Monitoring error: " + str(e)))
                time.sleep(self.scan_interval)

    def start_monitoring(self):
        """Start folder monitoring"""
        if not self.download_directory:
            messagebox.showerror("Error", "Please select a directory first!")
            return
        
        self.is_monitoring = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.log_message("🔍 Starting real-time folder monitoring...")
        self.status_label.config(text="🔍 Monitoring active...", fg="#27ae60")
        
        # Start monitoring in thread
        monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        monitor_thread.start()

    def stop_monitoring(self):
        """Stop folder monitoring"""
        self.is_monitoring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.log_message("