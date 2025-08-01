# VDH_SIMPLE_CLICKER_20250730_1955.py
# VDH Simple Sequential Clicker - Minimal Dependencies
# Created: July 30, 2025 - 7:55 PM Pacific
# Purpose: Simple sequential clicking with file monitoring

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading
from pathlib import Path
from datetime import datetime
import json

class VDHSimpleClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Simple Sequential Clicker")
        self.root.geometry("700x500")
        
        # Configuration
        self.download_directory = ""
        self.video_count = 9
        self.current_video = 0
        self.session_active = False
        
        # Monitoring settings
        self.check_interval = 3  # seconds between file checks
        self.completion_wait = 10  # seconds to confirm completion
        self.max_wait_time = 180  # 3 minutes max per video
        
        # Session tracking
        self.session_stats = {
            "start_time": None,
            "completed_videos": 0,
            "total_files_downloaded": 0,
            "session_log": []
        }
        
        # File monitoring
        self.last_file_count = 0
        self.monitoring_thread = None
        
        self.setup_gui()

    def setup_gui(self):
        """Create the main interface"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH SIMPLE SEQUENTIAL CLICKER",
                              bg="#2c3e50", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(expand=True)

        # Configuration panel
        config_frame = tk.LabelFrame(self.root, text="⚙️ Configuration", 
                                    font=("Arial", 10, "bold"), padx=10, pady=5)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Download directory selection
        dir_frame = tk.Frame(config_frame)
        dir_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(dir_frame, text="📁 Download Directory:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.dir_label = tk.Label(dir_frame, text="Not selected", 
                                 fg="#e74c3c", font=("Arial", 9))
        self.dir_label.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Button(dir_frame, text="📁 SELECT",
                 command=self.select_download_directory,
                 bg="#3498db", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # Video count
        count_frame = tk.Frame(config_frame)
        count_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(count_frame, text="🎬 Expected Videos:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.video_count_var = tk.IntVar(value=9)
        video_spin = tk.Spinbox(count_frame, from_=1, to=20, width=5,
                               textvariable=self.video_count_var)
        video_spin.pack(side=tk.LEFT, padx=(10, 0))

        # Instructions panel
        instructions_frame = tk.LabelFrame(self.root, text="📋 Simple Manual Process", 
                                          font=("Arial", 10, "bold"), padx=10, pady=5)
        instructions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        instructions = """🎯 WORKFLOW:
1. Set download directory (match your VDH setting)
2. Open Chrome → Adam's DIYTRAX → Activate VDH
3. Click START - tool will prompt for each video
4. Tool monitors downloads and tracks progress
5. Manually click each VDH download button when prompted"""
        
        tk.Label(instructions_frame, text=instructions, justify=tk.LEFT,
                font=("Arial", 9), wraplength=650).pack(anchor=tk.W)

        # Progress panel
        progress_frame = tk.LabelFrame(self.root, text="📈 Progress", 
                                      font=("Arial", 10, "bold"), padx=10, pady=5)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Current video status
        self.current_video_label = tk.Label(progress_frame, text="Ready to start", 
                                           font=("Arial", 11, "bold"), fg="#f39c12")
        self.current_video_label.pack(pady=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=9)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Session log
        tk.Label(progress_frame, text="📊 Session Log:", 
                font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10,0))
        
        self.log_text = tk.Text(progress_frame, height=10, font=("Consolas", 8),
                               bg="#f8f9fa", wrap="word")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=2)

        # Control buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = tk.Button(control_frame, text="🚀 START SEQUENCE",
                                  command=self.start_sequence,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  state='disabled')
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP",
                                 command=self.stop_session,
                                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                 state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="📁 OPEN FOLDER",
                 command=self.open_download_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.RIGHT, padx=2)

        # Check if ready
        self.check_default_directory()

    def check_default_directory(self):
        """Check for default DIYTRAX directory"""
        default_dir = "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX"
        if os.path.exists(default_dir):
            self.download_directory = default_dir
            self.dir_label.config(text=default_dir, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.log_message(f"📁 Found DIYTRAX directory: {default_dir}")

    def select_download_directory(self):
        """Select download directory"""
        directory = filedialog.askdirectory(
            title="Select VDH Download Directory",
            initialdir="C:/INDEX-PROJECT/TCE-MEDIA"
        )
        
        if directory:
            self.download_directory = directory
            self.dir_label.config(text=directory, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.log_message(f"📁 Download directory set: {directory}")

    def start_sequence(self):
        """Start the download sequence"""
        if not self.download_directory:
            messagebox.showerror("Error", "Please select download directory first!")
            return
        
        self.video_count = self.video_count_var.get()
        self.progress_bar.config(maximum=self.video_count)
        
        # Initialize session
        self.session_active = True
        self.current_video = 0
        self.session_stats["start_time"] = datetime.now()
        self.session_stats["completed_videos"] = 0
        self.last_file_count = len([f for f in os.listdir(self.download_directory) 
                                   if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))])
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.log_message("🚀 Starting download sequence...")
        self.log_message(f"📁 Monitoring: {self.download_directory}")
        self.log_message(f"🎬 Expected videos: {self.video_count}")
        self.log_message(f"📊 Current files: {self.last_file_count}")
        
        # Start the sequence
        self.next_video()

    def next_video(self):
        """Process next video in sequence"""
        if not self.session_active or self.current_video >= self.video_count:
            self.complete_session()
            return
        
        self.current_video += 1
        self.current_video_label.config(text=f"🎬 Video {self.current_video}/{self.video_count} - READY TO CLICK")
        
        self.log_message(f"\n{'='*40}")
        self.log_message(f"🎯 READY FOR VIDEO {self.current_video}")
        self.log_message(f"👆 Click the VDH download button for video {self.current_video}")
        self.log_message(f"⏳ Tool will detect when download completes...")
        
        # Start monitoring for new file
        self.start_file_monitoring()

    def start_file_monitoring(self):
        """Start monitoring for new downloaded file"""
        def monitor_worker():
            start_time = time.time()
            
            while self.session_active and (time.time() - start_time) < self.max_wait_time:
                try:
                    current_files = [f for f in os.listdir(self.download_directory) 
                                   if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                    current_count = len(current_files)
                    
                    if current_count > self.last_file_count:
                        # New file detected
                        new_files = current_count - self.last_file_count
                        self.log_message(f"📥 Detected {new_files} new file(s)")
                        
                        # Wait for download to complete
                        if self.wait_for_file_stability():
                            self.session_stats["completed_videos"] += 1
                            self.session_stats["total_files_downloaded"] = current_count
                            self.last_file_count = current_count
                            
                            self.log_message(f"✅ Video {self.current_video} completed!")
                            self.progress_bar['value'] = self.current_video
                            
                            # Small delay then next video
                            time.sleep(2)
                            if self.session_active:
                                self.root.after(0, self.next_video)
                            return
                        
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.log_message(f"❌ Monitoring error: {str(e)}")
                    break
            
            # Timeout or error
            if self.session_active:
                self.log_message(f"⏰ Timeout waiting for video {self.current_video}")
                self.log_message(f"❓ Click 'STOP' and check VDH manually")
        
        self.monitoring_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitoring_thread.start()

    def wait_for_file_stability(self):
        """Wait for file download to stabilize"""
        try:
            self.log_message(f"⏳ Waiting for download completion...")
            
            # Get newest file
            files = []
            for f in os.listdir(self.download_directory):
                if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                    file_path = os.path.join(self.download_directory, f)
                    files.append((file_path, os.path.getmtime(file_path)))
            
            if not files:
                return False
            
            # Sort by modification time, get newest
            newest_file = max(files, key=lambda x: x[1])[0]
            
            # Monitor file size stability
            stable_count = 0
            last_size = 0
            
            for _ in range(self.completion_wait):
                if not self.session_active:
                    return False
                
                current_size = os.path.getsize(newest_file)
                
                if current_size == last_size and current_size > 1024:  # Stable and > 1KB
                    stable_count += 1
                    if stabl