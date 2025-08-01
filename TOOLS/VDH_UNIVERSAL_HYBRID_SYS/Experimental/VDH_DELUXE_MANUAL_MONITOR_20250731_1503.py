# VDH_DELUXE_MANUAL_MONITOR_20250731_1300.py
# VDH Deluxe Manual Monitor - Full Featured Download Tracking
# Created: July 31, 2025 - 1:00 PM Pacific
# Purpose: Premium manual VDH monitoring with comprehensive features

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading
from pathlib import Path
from datetime import datetime
import json
import glob
import winsound
from mutagen import File as MutagenFile

class VDHDeluxeMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Deluxe Manual Monitor")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        
        # Configuration
        self.download_directory = ""
        self.is_monitoring = False
        self.videos_found = 0
        self.videos_completed = 0
        self.session_start_time = None
        
        # Progress tracking
        self.current_video = ""
        self.total_progress = 0
        self.current_file_progress = 0
        
        # File tracking with enhanced features
        self.completed_files = set()
        self.in_progress_files = {}
        self.file_history = []
        self.download_speeds = []
        self.completion_times = []
        
        # Enhanced monitoring settings
        self.scan_interval = 1.5  # seconds between scans
        self.size_stable_threshold = 3  # scans with same size = complete
        self.sound_notifications = True
        self.auto_analysis = True
        
        # Statistics tracking
        self.session_stats = {
            'start_time': None,
            'files_at_start': 0,
            'new_downloads': 0,
            'total_mb_downloaded': 0,
            'average_speed': 0,
            'estimated_completion': None
        }
        
        self.setup_gui()

    def setup_gui(self):
        """Create deluxe monitor interface with premium features"""
        # Premium title banner with gradient effect
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH DELUXE MANUAL MONITOR",
                              bg="#2c3e50", fg="white", font=("Arial", 14, "bold"))
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Premium Download Tracking & Analysis System",
                                 bg="#2c3e50", fg="#bdc3c7", font=("Arial", 9))
        subtitle_label.pack()

        # Enhanced directory configuration
        config_frame = tk.LabelFrame(self.root, text="📁 Directory Configuration", 
                                    font=("Arial", 10, "bold"), padx=10, pady=8)
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

        # Premium progress tracking panel with enhanced visuals
        progress_frame = tk.LabelFrame(self.root, text="📊 Premium Progress Tracking", 
                                      font=("Arial", 10, "bold"), padx=10, pady=8)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Session progress with time estimation
        session_frame = tk.Frame(progress_frame)
        session_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(session_frame, text="📊 Session Progress:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.session_progress = ttk.Progressbar(session_frame, mode='determinate', length=350)
        self.session_progress.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        self.session_percent = tk.Label(session_frame, text="0%", 
                                       font=("Arial", 9, "bold"), fg="#3498db", 
                                       relief=tk.SUNKEN, width=6, bg="#ecf0f1")
        self.session_percent.pack(side=tk.RIGHT)
        
        # Current download with speed indicator
        current_frame = tk.Frame(progress_frame)
        current_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(current_frame, text="📹 Current Download:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.current_progress = ttk.Progressbar(current_frame, mode='determinate', length=350)
        self.current_progress.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        self.current_percent = tk.Label(current_frame, text="0%", 
                                       font=("Arial", 9, "bold"), fg="#27ae60", 
                                       relief=tk.SUNKEN, width=6, bg="#ecf0f1")
        self.current_percent.pack(side=tk.RIGHT)

        # Enhanced real-time statistics dashboard
        stats_frame = tk.LabelFrame(self.root, text="📊 Live Statistics Dashboard", 
                                   font=("Arial", 10, "bold"), padx=10, pady=8)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Top row statistics
        stats_top = tk.Frame(stats_frame)
        stats_top.pack(fill=tk.X, pady=3)
        
        tk.Label(stats_top, text="📁 Total Files:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.total_label = tk.Label(stats_top, text="0", 
                                   font=("Arial", 9), fg="#3498db")
        self.total_label.grid(row=0, column=1, sticky="w", padx=(5, 15))
        
        tk.Label(stats_top, text="✅ Completed:", 
                font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.completed_label = tk.Label(stats_top, text="0", 
                                       font=("Arial", 9), fg="#27ae60")
        self.completed_label.grid(row=0, column=3, sticky="w", padx=(5, 15))
        
        tk.Label(stats_top, text="⏳ Downloading:", 
                font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="w")
        self.downloading_label = tk.Label(stats_top, text="0", 
                                         font=("Arial", 9), fg="#f39c12")
        self.downloading_label.grid(row=0, column=5, sticky="w", padx=(5, 15))
        
        tk.Label(stats_top, text="💾 Total Size:", 
                font=("Arial", 9, "bold")).grid(row=0, column=6, sticky="w")
        self.size_label = tk.Label(stats_top, text="0 MB", 
                                  font=("Arial", 9), fg="#9b59b6")
        self.size_label.grid(row=0, column=7, sticky="w", padx=(5, 0))
        
        # Bottom row statistics
        stats_bottom = tk.Frame(stats_frame)
        stats_bottom.pack(fill=tk.X, pady=3)
        
        tk.Label(stats_bottom, text="🚀 Avg Speed:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.speed_label = tk.Label(stats_bottom, text="0 MB/s", 
                                   font=("Arial", 9), fg="#e67e22")
        self.speed_label.grid(row=0, column=1, sticky="w", padx=(5, 15))
        
        tk.Label(stats_bottom, text="⏱️ Session Time:", 
                font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.time_label = tk.Label(stats_bottom, text="00:00:00", 
                                  font=("Arial", 9), fg="#34495e")
        self.time_label.grid(row=0, column=3, sticky="w", padx=(5, 15))
        
        tk.Label(stats_bottom, text="📈 New Downloads:", 
                font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="w")
        self.new_label = tk.Label(stats_bottom, text="0", 
                                 font=("Arial", 9), fg="#8e44ad")
        self.new_label.grid(row=0, column=5, sticky="w", padx=(5, 15))
        
        tk.Label(stats_bottom, text="🎯 Success Rate:", 
                font=("Arial", 9, "bold")).grid(row=0, column=6, sticky="w")
        self.success_label = tk.Label(stats_bottom, text="100%", 
                                     font=("Arial", 9), fg="#27ae60")
        self.success_label.grid(row=0, column=7, sticky="w", padx=(5, 0))

        # Dynamic status display with enhanced messaging
        status_frame = tk.Frame(stats_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="🔍 Ready for premium monitoring", 
                                    font=("Arial", 11, "bold"), fg="#f39c12",
                                    relief=tk.SUNKEN, bg="#ecf0f1", pady=5)
        self.status_label.pack(fill=tk.X)

        # Premium activity log with enhanced formatting
        log_frame = tk.LabelFrame(self.root, text="📋 Premium Activity Log", 
                                 font=("Arial", 10, "bold"), padx=10, pady=8)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        log_container = tk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=8, font=("Consolas", 8),
                               bg="#f8f9fa", wrap="word", relief=tk.SUNKEN, bd=2)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Enhanced text formatting
        self.log_text.tag_config("success", foreground="#27ae60", font=("Consolas", 8, "bold"))
        self.log_text.tag_config("error", foreground="#e74c3c", font=("Consolas", 8, "bold"))
        self.log_text.tag_config("info", foreground="#3498db", font=("Consolas", 8))
        self.log_text.tag_config("warning", foreground="#f39c12", font=("Consolas", 8, "bold"))
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Premium control panel with enhanced buttons
        control_frame = tk.Frame(self.root, bg="#ecf0f1", pady=8)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main controls with premium styling
        main_controls = tk.Frame(control_frame, bg="#ecf0f1")
        main_controls.pack(side=tk.LEFT)
        
        self.start_btn = tk.Button(main_controls, text="🔍 START PREMIUM MONITORING",
                                  command=self.start_monitoring,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  state='disabled', relief=tk.RAISED, bd=3)
        self.start_btn.pack(side=tk.LEFT, padx=3)
        
        self.stop_btn = tk.Button(main_controls, text="⏹️ STOP",
                                 command=self.stop_monitoring,
                                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                 state='disabled', relief=tk.RAISED, bd=3)
        self.stop_btn.pack(side=tk.LEFT, padx=3)
        
        self.analyze_btn = tk.Button(main_controls, text="📊 INSTANT ANALYSIS",
                                    command=self.instant_analysis,
                                    bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                                    state='disabled', relief=tk.RAISED, bd=3)
        self.analyze_btn.pack(side=tk.LEFT, padx=3)
        
        # Premium utility controls
        utility_controls = tk.Frame(control_frame, bg="#ecf0f1")
        utility_controls.pack(side=tk.RIGHT)
        
        tk.Button(utility_controls, text="📋 EXPORT LOG",
                 command=self.export_premium_log,
                 bg="#e67e22", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="📊 DELUXE REPORT",
                 command=self.generate_deluxe_report,
                 bg="#8e44ad", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="🔧 SETTINGS",
                 command=self.show_settings,
                 bg="#34495e", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="📁 OPEN FOLDER",
                 command=self.open_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)

        # Initialize premium features
        self.check_default_directory()
        self.update_session_timer()

    def check_default_directory(self):
        """Check for default DIYTRAX directory with premium initialization"""
        default_dir = "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX"
        if os.path.exists(default_dir):
            self.download_directory = default_dir
            self.dir_label.config(text=default_dir, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.analyze_btn.config(state='normal')
            self.log_message("📁 Premium directory initialized: " + default_dir, "success")
            
            # Auto-analyze existing files with premium features
            self.instant_analysis()

    def select_directory(self):
        """Select download directory with premium validation"""
        directory = filedialog.askdirectory(
            title="Select Premium VDH Download Directory",
            initialdir="C:/INDEX-PROJECT/TCE-MEDIA"
        )
        
        if directory:
            self.download_directory = directory
            self.dir_label.config(text=directory, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.analyze_btn.config(state='normal')
            self.log_message("📁 Premium directory selected: " + directory, "success")

    def update_progress(self, session_percent, current_percent=0):
        """Update premium progress bars with enhanced visuals"""
        self.session_progress['value'] = min(100, max(0, session_percent))
        self.session_percent.config(text=str(int(session_percent)) + "%")
        
        self.current_progress['value'] = min(100, max(0, current_percent))
        self.current_percent.config(text=str(int(current_percent)) + "%")
        
        # Enhanced visual feedback
        if session_percent >= 100:
            self.session_percent.config(bg="#d5f4e6", fg="#27ae60")
        elif session_percent >= 75:
            self.session_percent.config(bg="#fff3cd", fg="#856404")
        
        self.root.update_idletasks()

    def update_stats(self, total=None, completed=None, downloading=None, 
                    total_size=None, avg_speed=None, new_downloads=None):
        """Update premium statistics with enhanced calculations"""
        if total is not None:
            self.videos_found = total
            self.total_label.config(text=str(total))
        
        if completed is not None:
            self.videos_completed = completed
            self.completed_label.config(text=str(completed))
        
        if downloading is not None:
            self.downloading_label.config(text=str(downloading))
        
        if total_size is not None:
            size_mb = total_size / (1024 * 1024)
            self.size_label.config(text=str(round(size_mb, 1)) + " MB")
        
        if avg_speed is not None:
            speed_mb = avg_speed / (1024 * 1024)
            self.speed_label.config(text=str(round(speed_mb, 2)) + " MB/s")
        
        if new_downloads is not None:
            self.new_label.config(text=str(new_downloads))
        
        # Calculate and update success rate
        if self.videos_found > 0:
            success_rate = (self.videos_completed / self.videos_found) * 100
            self.success_label.config(text=str(round(success_rate, 1)) + "%")

    def get_enhanced_file_info(self, file_path):
        """Get comprehensive file information with premium features"""
        try:
            stat = os.stat(file_path)
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'extension': os.path.splitext(file_path)[1].lower()
            }
            
            # Enhanced metadata extraction
            try:
                audio_file = MutagenFile(file_path)
                if audio_file and hasattr(audio_file, 'info'):
                    info = audio_file.info
                    file_info['duration'] = getattr(info, 'length', 0)
                    file_info['bitrate'] = getattr(info, 'bitrate', 0)
                    file_info['codec'] = str(type(audio_file).__name__)
                    
                    # Calculate quality metrics
                    if file_info['duration'] > 0:
                        file_info['quality_score'] = (file_info['bitrate'] * file_info['duration']) / 1000
                    else:
                        file_info['quality_score'] = 0
            except:
                file_info['duration'] = 0
                file_info['bitrate'] = 0
                file_info['codec'] = 'Unknown'
                file_info['quality_score'] = 0
            
            return file_info
            
        except Exception as e:
            self.log_message("⚠️ Error reading file info: " + str(e), "error")
            return None

    def premium_scan_directory(self):
        """Enhanced directory scanning with premium analytics"""
        if not self.download_directory or not os.path.exists(self.download_directory):
            return [], [], 0, {}
        
        try:
            # Enhanced file detection
            video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.mp3', '*.wav', '*.m4a', '*.flv', '*.webm']
            all_files = []
            
            for ext in video_extensions:
                pattern = os.path.join(self.download_directory, ext)
                all_files.extend(glob.glob(pattern))
            
            # Premium file analysis
            completed_files = []
            downloading_files = []
            total_size = 0
            analytics = {
                'file_types': {},
                'size_distribution': {'small': 0, 'medium': 0, 'large': 0},
                'download_speeds': [],
                'completion_rate': 0
            }
            
            for file_path in all_files:
                file_info = self.get_enhanced_file_info(file_path)
                if not file_info:
                    continue
                
                total_size += file_info['size']
                
                # Analytics tracking
                ext = file_info['extension']
                analytics['file_types'][ext] = analytics['file_types'].get(ext, 0) + 1
                
                # Size categorization
                size_mb = file_info['size'] / (1024 * 1024)
                if size_mb < 10:
                    analytics['size_distribution']['small'] += 1
                elif size_mb < 100:
                    analytics['size_distribution']['medium'] += 1
                else:
                    analytics['size_distribution']['large'] += 1
                
                # Enhanced download progress detection
                file_key = file_path
                current_size = file_info['size']
                current_time = time.time()
                
                if file_key in self.in_progress_files:
                    prev_size, prev_time, stability_count = self.in_progress_files[file_key]
                    
                    if current_size == prev_size:
                        # Size hasn't changed
                        stability_count += 1
                        self.in_progress_files[file_key] = (current_size, current_time, stability_count)
                        
                        if stability_count >= self.size_stable_threshold:
                            # File appears complete
                            completed_files.append(file_info)
                            del self.in_progress_files[file_key]
                            self.completed_files.add(file_key)
                            
                            # Premium completion notification
                            self.log_message("✅ Premium download completed: " + file_info['name'] + 
                                           " (" + str(round(size_mb, 1)) + " MB)", "success")
                            
                            if self.sound_notifications:
                                try:
                                    winsound.MessageBeep(winsound.MB_OK)
                                except:
                                    pass
                        else:
                            downloading_files.append(file_info)
                    else:
                        # Size changed, still downloading
                        time_diff = current_time - prev_time
                        if time_diff > 0:
                            speed = (current_size - prev_size) / time_diff
                            analytics['download_speeds'].append(speed)
                        
                        self.in_progress_files[file_key] = (current_size, current_time, 0)
                        downloading_files.append(file_info)
                        
                        # Enhanced progress reporting
                        if prev_size > 0:
                            growth_mb = (current_size - prev_size) / (1024 * 1024)
                            self.log_message("📥 Premium download progress: " + file_info['name'] + 
                                           " (+" + str(round(growth_mb, 1)) + " MB)", "info")
                
                elif file_key in self.completed_files:
                    # Already completed
                    completed_files.append(file_info)
                
                else:
                    # New file detected
                    if current_size > 0:
                        self.in_progress_files[file_key] = (current_size, current_time, 0)
                        downloading_files.append(file_info)
                        self.session_stats['new_downloads'] += 1
                        
                        self.log_message("🆕 Premium download detected: " + file_info['name'] + 
                                       " (" + str(round(size_mb, 1)) + " MB)", "success")
            
            # Calculate completion rate
            total_files = len(completed_files) + len(downloading_files)
            if total_files > 0:
                analytics['completion_rate'] = (len(completed_files) / total_files) * 100
            
            return completed_files, downloading_files, total_size, analytics
            
        except Exception as e:
            self.log_message("❌ Premium scan error: " + str(e), "error")
            return [], [], 0, {}

    def premium_monitoring_loop(self):
        """Enhanced monitoring loop with premium features"""
        while self.is_monitoring:
            try:
                completed, downloading, total_size, analytics = self.premium_scan_directory()
                
                total_files = len(completed) + len(downloading)
                completed_count = len(completed)
                downloading_count = len(downloading)
                
                # Calculate average download speed
                avg_speed = 0
                if analytics['download_speeds']:
                    avg_speed = sum(analytics['download_speeds']) / len(analytics['download_speeds'])
                
                # Update premium statistics
                self.root.after(0, lambda: self.update_stats(
                    total=total_files,
                    completed=completed_count,
                    downloading=downloading_count,
                    total_size=total_size,
                    avg_speed=avg_speed,
                    new_downloads=self.session_stats['new_downloads']
                ))
                
                # Enhanced progress calculation
                if total_files > 0:
                    session_progress = (completed_count / total_files) * 100
                    
                    # Current download progress estimation
                    current_progress = 0
                    if downloading:
                        # Use the largest downloading file as current
                        current_file = max(downloading, key=lambda x: x['size'])
                        current_name = current_file['name']
                        
                        # Estimate progress based on average completed file size
                        if completed:
                            avg_completed_size = sum(f['size'] for f in completed) / len(completed)
                            if avg_completed_size > 0:
                                current_progress = min(100, (current_file['size'] / avg_completed_size) * 100)
                        
                        self.root.after(0, lambda: self.status_label.config(
                            text="📥 Premium downloading: " + current_name[:35] + "...", fg="#3498db"))
                    else:
                        if completed_count > 0:
                            self.root.after(0, lambda: self.status_label.config(
                                text="✅ Premium session complete - All downloads finished!", fg="#27ae60"))
                        else:
                            self.root.after(0, lambda: self.status_label.config(
                                text="🔍 Premium monitoring active - Waiting for downloads...", fg="#f39c12"))
                    
                    self.root.after(0, lambda: self.update_progress(session_progress, current_progress))
                
                # Enhanced session statistics
                self.session_stats['total_mb_downloaded'] = total_size / (1024 * 1024)
                self.session_stats['average_speed'] = avg_speed
                
                # Wait before next scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message("❌ Premium monitoring error: " + str(e), "error"))
                time.sleep(self.scan_interval)

    def start_monitoring(self):
        """Start premium folder monitoring"""
        if not self.download_directory:
            messagebox.showerror("Premium Monitor", "Please select a directory first!")
            return
        
        self.is_monitoring = True
        self.session_start_time = datetime.now()
        self.session_stats['start_time'] = self.session_start_time
        
        # Get initial file count
        completed, downloading, _, _ = self.premium_scan_directory()
        self.session_stats['files_at_start'] = len(completed) + len(downloading)
        self.session_stats['new_downloads'] = 0
        
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.log_message("🚀 Premium monitoring session started!", "success")
        self.status_label.config(text="🔍 Premium monitoring active...", fg="#27ae60")
        
        # Premium notification
        if self.sound_notifications:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass
        
        # Start premium monitoring in thread
        monitor_thread = threading.Thread(target=self.premium_monitoring_loop, daemon=True)
        monitor_thread.start()

    def stop_monitoring(self):
        """Stop premium folder monitoring"""
        self.is_monitoring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        # Calculate session summary
        if self.session_start_time:
            session_duration = datetime.now() - self.session_start_time
            duration_str = str(session_duration).split('.')[0]  # Remove microseconds
            
            self.log_message("⏹️ Premium session stopped after " + duration_str, "info")
            self.log_message("📊 Session summary: " + str(self.session_stats['new_downloads']) + 
                           " new downloads, " + str(round(self.session_stats['total_mb_downloaded'], 1)) + " MB total", "success")
        
        self.status_label.config(text="⏹️ Premium monitoring stopped", fg="#e74c3c")
        
        # Premium notification
        if self.sound_notifications:
            try:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except:
                pass

    def instant_analysis(self):
        """Perform instant premium analysis"""
        if not self.download_directory:
            messagebox.showwarning("Premium Monitor", "Please select a directory first!")
            return
        
        self.log_message("📊 Running premium instant analysis...", "info")
        
        completed, downloading, total_size, analytics = self.premium_scan_directory()
        
        total_files = len(completed) + len(downloading)
        
        # Update all statistics
        avg_speed = 0
        if analytics['download_speeds']:
            avg_speed = sum(analytics['download_speeds']) / len(analytics['download_speeds'])
        
        self.update_stats(
            total=total_files,
            completed=len(completed),
            downloading=len(downloading),
            total_size=total_size,
            avg_speed=avg_speed,
            new_downloads=self.session_stats['new_downloads']
        )
        
        # Premium analysis results
        self.log_message("📊 Premium analysis complete:", "success")
        self.log_message("   📁 Total files: " + str(total_files), "info")
        self.log_message("   ✅ Completed: " + str(len(completed)), "success")
        self.log_message("   ⏳ In progress: " + str(len(downloading)), "warning")
        self.log_message("   💾 Total size: " + str(round(total_size/(1024*1024), 1)) + " MB", "info")
        
        # File type breakdown
        if analytics['file_types']:
            self.log_message("   📋 File types: " + str(analytics['file_types']), "info")
        
        # Update progress
        if total_files > 0:
            session_progress = (len(completed) / total_files) * 100
            self.update_progress(session_progress, 0)

    def update_session_timer(self):
        """Update session timer display"""
        if self.session_start_time and self.is_monitoring:
            elapsed = datetime.now() - self.session_start_time
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
            self.time_label.config(text=elapsed_str)
        elif not self.is_monitoring:
            self.time_label.config(text="00:00:00")
        
        # Schedule next update
        self.root.after(1000, self.update_session_timer)

    def show_settings(self):
        """Show premium settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("🔧 Premium Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Settings content
        tk.Label(settings_window, text="🔧 Premium Monitor Settings", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Sound notifications
        sound_frame = tk.Frame(settings_window)
        sound_frame.pack(fill=tk.X, padx=20, pady=5)
        
        sound_var = tk.BooleanVar(value=self.sound_notifications)
        tk.Checkbutton(sound_frame, text="🔊 Sound Notifications", 
                      variable=sound_var, font=("Arial", 10)).pack(anchor="w")
        
        # Scan interval
        interval_frame = tk.Frame(settings_window)
        interval_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(interval_frame, text="⏱️ Scan Interval (seconds):", 
                font=("Arial", 10)).pack(anchor="w")
        interval_var = tk.DoubleVar(value=self.scan_interval)
        tk.Scale(interval_frame, from_=0.5, to=5.0, resolution=0.1, orient=tk.HORIZONTAL,
                variable=interval_var).pack(fill=tk.X)
        
        # Apply button
        def apply_settings():
            self.sound_notifications = sound_var.get()
            self.scan_interval = interval_var.get()
            self.log_message("🔧 Premium settings updated", "success")
            settings_window.destroy()
        
        tk.Button(settings_window, text="✅ Apply Settings", command=apply_settings,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def generate_deluxe_report(self):
        """Generate comprehensive deluxe analysis report"""
        if not self.download_directory:
            messagebox.showwarning("Premium Monitor", "Please select a directory first!")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = os.path.join(self.download_directory, "VDH_DELUXE_REPORT_" + timestamp + ".txt")
            
            completed, downloading, total_size, analytics = self.premium_scan_directory()
            
            # Generate premium report
            report_content = "🎯 VDH DELUXE MANUAL MONITOR - PREMIUM ANALYSIS REPORT\n"
            report_content += "=" * 70 + "\n"
            report_content += "📅 Report Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
            report_content += "📁 Monitor Directory: " + self.download_directory + "\n"
            
            if self.session_start_time:
                session_duration = datetime.now() - self.session_start_time
                report_content += "⏱️ Session Duration: " + str(session_duration).split('.')[0] + "\n"
            
            report_content += "\n📊 EXECUTIVE SUMMARY:\n"
            report_content += "-" * 30 + "\n"
            report_content += "📁 Total Files Detected: " + str(len(completed) + len(downloading)) + "\n"
            report_content += "✅ Downloads Completed: " + str(len(completed)) + "\n"
            report_content += "⏳ Currently Downloading: " + str(len(downloading)) + "\n"
            report_content += "💾 Total Content Size: " + str(round(total_size/(1024*1024), 1)) + " MB\n"
            report_content += "📈 Completion Rate: " + str(round(analytics.get('completion_rate', 0), 1)) + "%\n"
            report_content += "🆕 New Downloads This Session: " + str(self.session_stats['new_downloads']) + "\n"
            
            if analytics['download_speeds']:
                avg_speed = sum(analytics['download_speeds']) / len(analytics['download_speeds'])
                report_content += "🚀 Average Download Speed: " + str(round(avg_speed/(1024*1024), 2)) + " MB/s\n"
            
            report_content += "\n📋 FILE TYPE ANALYSIS:\n"
            report_content += "-" * 30 + "\n"
            for file_type, count in analytics.get('file_types', {}).items():
                report_content += file_type + ": " + str(count) + " files\n"
            
            report_content += "\n📊 SIZE DISTRIBUTION:\n"
            report_content += "-" * 30 + "\n"
            size_dist = analytics.get('size_distribution', {})
            report_content += "Small files (<10MB): " + str(size_dist.get('small', 0)) + "\n"
            report_content += "Medium files (10-100MB): " + str(size_dist.get('medium', 0)) + "\n"
            report_content += "Large files (>100MB): " + str(size_dist.get('large', 0)) + "\n"
            
            # Detailed file listings
            if completed:
                report_content += "\n✅ COMPLETED DOWNLOADS:\n"
                report_content += "-" * 40 + "\n"
                for i, file_info in enumerate(completed, 1):
                    size_mb = file_info['size'] / (1024 * 1024)
                    mod_time = datetime.fromtimestamp(file_info['modified'])
                    report_content += str(i) + ". " + file_info['name'] + "\n"
                    report_content += "   📁 Size: " + str(round(size_mb, 1)) + " MB\n"
                    report_content += "   📅 Completed: " + mod_time.strftime("%m/%d %H:%M:%S") + "\n"
                    if file_info.get('duration', 0) > 0:
                        duration_min = int(file_info['duration'] // 60)
                        duration_sec = int(file_info['duration'] % 60)
                        report_content += "   ⏱️ Duration: " + str(duration_min) + "m " + str(duration_sec) + "s\n"
                    if file_info.get('bitrate', 0) > 0:
                        report_content += "   📡 Bitrate: " + str(file_info['bitrate']) + " bps\n"
                    report_content += "\n"
            
            if downloading:
                report_content += "\n⏳ CURRENTLY DOWNLOADING:\n"
                report_content += "-" * 40 + "\n"
                for i, file_info in enumerate(downloading, 1):
                    size_mb = file_info['size'] / (1024 * 1024)
                    report_content += str(i) + ". " + file_info['name'] + "\n"
                    report_content += "   📥 Current Size: " + str(round(size_mb, 1)) + " MB\n\n"
            
            # Session activity log
            report_content += "\n📋 PREMIUM SESSION LOG:\n"
            report_content += "-" * 40 + "\n"
            report_content += self.log_text.get(1.0, tk.END)
            
            # Premium recommendations
            report_content += "\n💡 PREMIUM RECOMMENDATIONS:\n"
            report_content += "-" * 40 + "\n"
            if len(completed) > 0:
                report_content += "✅ Download session successful with " + str(len(completed)) + " completed files\n"
                report_content += "✅ Ready for transcription processing pipeline\n"
                report_content += "✅ Total content: " + str(round(total_size/(1024*1024), 1)) + " MB ready for INDEX development\n"
            if len(downloading) > 0:
                report_content += "⏳ " + str(len(downloading)) + " downloads still in progress\n"
                report_content += "⏳ Continue monitoring for completion status\n"
            
            report_content += "🎯 Premium monitoring session complete - Ready for next phase!\n"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            success_msg = ("📊 Deluxe Report Generated!\n\n" +
                          "✅ Premium analysis report saved\n" +
                          "✅ File: " + os.path.basename(report_file) + "\n" +
                          "✅ " + str(len(completed) + len(downloading)) + " files analyzed\n" +
                          "✅ " + str(round(total_size/(1024*1024), 1)) + " MB total content\n\n" +
                          "Report includes comprehensive analytics and session log!")
            
            messagebox.showinfo("Deluxe Report Complete", success_msg)
            self.log_message("📊 Deluxe report generated: " + report_file, "success")
            
        except Exception as e:
            messagebox.showerror("Report Error", "Failed to generate deluxe report: " + str(e))

    def export_premium_log(self):
        """Export premium activity log with enhanced formatting"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_file = os.path.join(self.download_directory or ".", 
                                   "VDH_PREMIUM_LOG_" + timestamp + ".txt")
            
            log_content = self.log_text.get(1.0, tk.END)
            
            header = "🎯 VDH DELUXE MANUAL MONITOR - PREMIUM ACTIVITY LOG\n"
            header += "=" * 60 + "\n"
            header += "📅 Export Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
            header += "📁 Monitor Directory: " + (self.download_directory or "Not selected") + "\n"
            header += "📊 Session Statistics:\n"
            header += "   📁 Files Detected: " + str(self.videos_found) + "\n"
            header += "   ✅ Completed: " + str(self.videos_completed) + "\n"
            header += "   🆕 New Downloads: " + str(self.session_stats['new_downloads']) + "\n"
            header += "   💾 Total Downloaded: " + str(round(self.session_stats['total_mb_downloaded'], 1)) + " MB\n"
            
            if self.session_start_time:
                session_duration = datetime.now() - self.session_start_time
                header += "   ⏱️ Session Duration: " + str(session_duration).split('.')[0] + "\n"
            
            header += "\n📋 PREMIUM ACTIVITY LOG:\n"
            header += "-" * 60 + "\n"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(header + log_content)
            
            messagebox.showinfo("Premium Export Complete", 
                              "Premium log exported: " + os.path.basename(log_file))
            self.log_message("📋 Premium log exported: " + log_file, "success")
            
        except Exception as e:
            messagebox.showerror("Export Error", "Failed to export premium log: " + str(e))

    def open_directory(self):
        """Open download directory with premium features"""
        if self.download_directory and os.path.exists(self.download_directory):
            os.startfile(self.download_directory)
            self.log_message("📁 Premium directory opened: " + self.download_directory, "info")
        else:
            messagebox.showwarning("Premium Monitor", "Directory not found")

    def log_message(self, message, level="info"):
        """Add message to premium activity log with enhanced formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = "[" + timestamp + "] " + message + "\n"
        
        # Apply formatting based on level
        tag = level if level in ["success", "error", "info", "warning"] else "info"
        
        self.log_text.insert(tk.END, log_entry, tag)
        self.log_text.see(tk.END)
        print(log_entry.strip())

    def run(self):
        """Start the premium application"""
        self.root.mainloop()

def main():
    """Main entry point for premium monitor"""
    print("🎯 VDH Deluxe Manual Monitor")
    print("Created: July 31, 2025 - 1:00 PM Pacific")
    print("Purpose: Premium manual VDH monitoring with comprehensive features")
    print("Features: Real-time progress, premium analytics, deluxe reporting")
    print()
    
    try:
        app = VDHDeluxeMonitor()
        app.run()
    except Exception as e:
        print("❌ Error: " + str(e))
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())