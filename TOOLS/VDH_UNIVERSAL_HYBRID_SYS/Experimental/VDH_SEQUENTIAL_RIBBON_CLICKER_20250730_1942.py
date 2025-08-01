# VDH_SEQUENTIAL_RIBBON_CLICKER_20250730_1942.py
# VDH Sequential Ribbon Clicker - Smart Download Manager
# Created: July 30, 2025 - 7:42 PM Pacific
# Purpose: Sequential clicking of VDH ribbon download buttons with completion monitoring

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import cv2
import numpy as np
import time
import os
import threading
from pathlib import Path
from datetime import datetime
import json
import psutil

class VDHSequentialClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Sequential Ribbon Clicker")
        self.root.geometry("800x600")
        
        # Configuration
        self.download_directory = ""
        self.video_count = 9  # DIYTRAX has 9 videos
        self.current_video = 0
        self.session_active = False
        
        # Monitoring settings
        self.check_interval = 2  # seconds between file checks
        self.completion_wait = 5  # seconds to confirm completion
        self.max_wait_time = 300  # 5 minutes max per video
        
        # Session tracking
        self.session_stats = {
            "start_time": None,
            "completed_videos": 0,
            "failed_videos": [],
            "total_files_downloaded": 0,
            "total_size_mb": 0,
            "session_log": []
        }
        
        # File monitoring
        self.last_file_sizes = {}
        self.monitoring_thread = None
        
        self.setup_gui()
        self.load_session_config()

    def setup_gui(self):
        """Create the main interface"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH SEQUENTIAL RIBBON CLICKER",
                              bg="#2c3e50", fg="white", font=("Arial", 14, "bold"))
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
        
        tk.Button(dir_frame, text="📁 SELECT DIRECTORY",
                 command=self.select_download_directory,
                 bg="#3498db", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # Video count configuration
        count_frame = tk.Frame(config_frame)
        count_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(count_frame, text="🎬 Expected Videos:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.video_count_var = tk.IntVar(value=9)
        video_spin = tk.Spinbox(count_frame, from_=1, to=20, width=5,
                               textvariable=self.video_count_var,
                               command=self.update_video_count)
        video_spin.pack(side=tk.LEFT, padx=(10, 0))

        # Instructions panel
        instructions_frame = tk.LabelFrame(self.root, text="📋 Setup Instructions", 
                                          font=("Arial", 10, "bold"), padx=10, pady=5)
        instructions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        instructions = """🎯 SETUP SEQUENCE:
1. Open Chrome and navigate to Adam's DIYTRAX training page
2. Activate VDH extension - verify it detects all 9 videos
3. Set download directory in VDH settings (match directory selected above)
4. Ensure VDH ribbon is visible with all download buttons
5. Click 'START SEQUENTIAL DOWNLOAD' below"""
        
        tk.Label(instructions_frame, text=instructions, justify=tk.LEFT,
                font=("Arial", 9), wraplength=750).pack(anchor=tk.W)

        # Progress panel
        progress_frame = tk.LabelFrame(self.root, text="📈 Download Progress", 
                                      font=("Arial", 10, "bold"), padx=10, pady=5)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Current video status
        current_frame = tk.Frame(progress_frame)
        current_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(current_frame, text="🎬 Current Video:", 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.current_video_label = tk.Label(current_frame, text="Ready to start", 
                                           font=("Arial", 10), fg="#f39c12")
        self.current_video_label.pack(side=tk.LEFT, padx=(10, 0))

        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Session log
        log_frame = tk.Frame(progress_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(log_frame, text="📊 Session Log:", 
                font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        # Create log text with scrollbar
        log_container = tk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=8, font=("Consolas", 8),
                               bg="#f8f9fa", wrap="word")
        log_scrollbar = tk.Scrollbar(log_container, orient=tk.VERTICAL, 
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
        
        self.start_btn = tk.Button(main_controls, text="🚀 START SEQUENTIAL DOWNLOAD",
                                  command=self.start_sequential_download,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  state='disabled')
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = tk.Button(main_controls, text="⏸️ PAUSE",
                                  command=self.pause_session,
                                  bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
                                  state='disabled')
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(main_controls, text="⏹️ STOP",
                                 command=self.stop_session,
                                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                 state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Utility controls
        utility_controls = tk.Frame(control_frame)
        utility_controls.pack(side=tk.RIGHT)
        
        tk.Button(utility_controls, text="📁 OPEN DOWNLOADS",
                 command=self.open_download_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="💾 SAVE LOG",
                 command=self.save_session_log,
                 bg="#34495e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

    def select_download_directory(self):
        """Select download directory"""
        directory = filedialog.askdirectory(
            title="Select VDH Download Directory",
            initialdir="C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX"
        )
        
        if directory:
            self.download_directory = directory
            self.dir_label.config(text=directory, fg="#27ae60")
            self.log_message(f"📁 Download directory set: {directory}")
            self.check_ready_state()

    def update_video_count(self):
        """Update expected video count"""
        self.video_count = self.video_count_var.get()
        self.progress_bar.config(maximum=self.video_count)
        self.log_message(f"🎬 Expected videos updated: {self.video_count}")

    def check_ready_state(self):
        """Check if system is ready to start"""
        if self.download_directory and not self.session_active:
            self.start_btn.config(state='normal')
        else:
            self.start_btn.config(state='disabled')

    def start_sequential_download(self):
        """Start the sequential download process"""
        if not self.download_directory:
            messagebox.showerror("Error", "Please select download directory first!")
            return
        
        # Confirm VDH setup
        result = messagebox.askyesno("Confirm VDH Setup", 
            "🎯 CONFIRM VDH SETUP:\n\n"
            "✅ Chrome open with Adam's DIYTRAX page?\n"
            "✅ VDH extension activated and detecting videos?\n"
            "✅ VDH ribbon showing all download buttons?\n"
            "✅ VDH download directory matches selected directory?\n\n"
            "Ready to start sequential downloading?")
        
        if not result:
            return
        
        # Initialize session
        self.session_active = True
        self.current_video = 0
        self.session_stats["start_time"] = datetime.now()
        self.session_stats["completed_videos"] = 0
        self.session_stats["failed_videos"] = []
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        
        self.log_message("🚀 Starting sequential download session...")
        self.log_message(f"📁 Target directory: {self.download_directory}")
        self.log_message(f"🎬 Expected videos: {self.video_count}")
        
        # Start the download sequence
        self.start_download_sequence()

    def start_download_sequence(self):
        """Start the main download sequence in a separate thread"""
        def download_worker():
            try:
                for video_num in range(1, self.video_count + 1):
                    if not self.session_active:
                        break
                    
                    self.current_video = video_num
                    self.update_current_video_display(f"Video {video_num}/{self.video_count}")
                    
                    self.log_message(f"🎬 Starting download of video {video_num}...")
                    
                    # Click the VDH download button for this video
                    if self.click_vdh_download_button(video_num):
                        # Monitor for completion
                        if self.wait_for_download_completion(video_num):
                            self.session_stats["completed_videos"] += 1
                            self.log_message(f"✅ Video {video_num} completed successfully")
                        else:
                            self.session_stats["failed_videos"].append(video_num)
                            self.log_message(f"❌ Video {video_num} failed or timed out")
                    else:
                        self.session_stats["failed_videos"].append(video_num)
                        self.log_message(f"❌ Could not click download button for video {video_num}")
                    
                    # Update progress
                    self.progress_bar['value'] = video_num
                    
                    # Small delay between videos
                    time.sleep(2)
                
                # Session complete
                self.complete_session()
                
            except Exception as e:
                self.log_message(f"❌ Download sequence error: {str(e)}")
                self.stop_session()
        
        # Start worker thread
        self.monitoring_thread = threading.Thread(target=download_worker, daemon=True)
        self.monitoring_thread.start()

    def click_vdh_download_button(self, video_number):
        """Click the VDH download button for specified video number"""
        try:
            self.log_message(f"🖱️ Looking for download button {video_number}...")
            
            # Give user time to position if needed
            time.sleep(1)
            
            # This is where you'd implement the actual button clicking
            # For now, we'll simulate the click
            self.log_message(f"🖱️ Clicking download button for video {video_number}")
            
            # TODO: Implement actual VDH button detection and clicking
            # Could use pyautogui.locateOnScreen() to find VDH buttons
            # For now, return True to simulate successful click
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Failed to click button {video_number}: {str(e)}")
            return False

    def wait_for_download_completion(self, video_number):
        """Monitor download directory for completion of current video"""
        try:
            start_time = time.time()
            initial_files = set(os.listdir(self.download_directory))
            
            self.log_message(f"⏳ Monitoring for video {video_number} completion...")
            
            while time.time() - start_time < self.max_wait_time:
                if not self.session_active:
                    return False
                
                current_files = set(os.listdir(self.download_directory))
                new_files = current_files - initial_files
                
                if new_files:
                    # Check if any new files have stopped growing
                    for filename in new_files:
                        file_path = os.path.join(self.download_directory, filename)
                        if self.is_file_download_complete(file_path):
                            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                            self.session_stats["total_files_downloaded"] += 1
                            self.session_stats["total_size_mb"] += file_size
                            
                            self.log_message(f"📥 File completed: {filename} ({file_size:.1f} MB)")
                            return True
                
                time.sleep(self.check_interval)
            
            self.log_message(f"⏰ Timeout waiting for video {video_number}")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Monitoring error for video {video_number}: {str(e)}")
            return False

    def is_file_download_complete(self, file_path):
        """Check if file download is complete by monitoring size stability"""
        try:
            if not os.path.exists(file_path):
                return False
            
            current_size = os.path.getsize(file_path)
            
            # First time seeing this file
            if file_path not in self.last_file_sizes:
                self.last_file_sizes[file_path] = current_size
                return False
            
            # Check if size has changed
            if current_size != self.last_file_sizes[file_path]:
                self.last_file_sizes[file_path] = current_size
                return False
            
            # Size stable for completion_wait seconds
            time.sleep(self.completion_wait)
            final_size = os.path.getsize(file_path)
            
            if final_size == current_size and final_size > 1024:  # At least 1KB
                return True
            
            return False
            
        except Exception:
            return False

    def update_current_video_display(self, text):
        """Update current video display"""
        self.current_video_label.config(text=text)
        self.root.update_idletasks()

    def pause_session(self):
        """Pause the current session"""
        self.session_active = False
        self.log_message("⏸️ Session paused")
        
        self.start_btn.config(state='normal', text="▶️ RESUME DOWNLOAD")
        self.pause_btn.config(state='disabled')

    def stop_session(self):
        """Stop the current session"""
        self.session_active = False
        self.log_message("⏹️ Session stopped")
        
        self.start_btn.config(state='normal', text="🚀 START SEQUENTIAL DOWNLOAD")
        self.pause_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        
        self.update_current_video_display("Session stopped")

    def complete_session(self):
        """Complete the download session"""
        self.session_active = False
        
        duration = datetime.now() - self.session_stats["start_time"]
        
        self.log_message("🎉 DOWNLOAD SESSION COMPLETE!")
        self.log_message(f"✅ Completed: {self.session_stats['completed_videos']}/{self.video_count} videos")
        self.log_message(f"📁 Total files: {self.session_stats['total_files_downloaded']}")
        self.log_message(f"💾 Total size: {self.session_stats['total_size_mb']:.1f} MB")
        self.log_message(f"⏱️ Duration: {str(duration).split('.')[0]}")
        
        if self.session_stats["failed_videos"]:
            self.log_message(f"❌ Failed videos: {self.session_stats['failed_videos']}")
        
        # Reset UI
        self.start_btn.config(state='normal', text="🚀 START SEQUENTIAL DOWNLOAD")
        self.pause_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        self.update_current_video_display("Session complete")
        
        # Show completion dialog
        messagebox.showinfo("Session Complete", 
            f"🎉 Download session completed!\n\n"
            f"✅ Completed: {self.session_stats['completed_videos']}/{self.video_count} videos\n"
            f"📁 Files downloaded: {self.session_stats['total_files_downloaded']}\n"
            f"💾 Total size: {self.session_stats['total_size_mb']:.1f} MB\n"
            f"⏱️ Duration: {str(duration).split('.')[0]}")

    def open_download_directory(self):
        """Open download directory in explorer"""
        if self.download_directory and os.path.exists(self.download_directory):
            os.startfile(self.download_directory)
        else:
            messagebox.showwarning("Directory Not Found", "Download directory not set or doesn't exist")

    def save_session_log(self):
        """Save session log to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_file = f"VDH_session_log_{timestamp}.txt"
            
            with open(log_file, 'w') as f:
                f.write(f"VDH Sequential Download Session Log\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"{'='*50}\n\n")
                f.write(self.log_text.get(1.0, tk.END))
            
            self.log_message(f"💾 Session log saved: {log_file}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save log: {str(e)}")

    def log_message(self, message):
        """Add message to session log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def load_session_config(self):
        """Load previous session configuration"""
        try:
            config_file = "vdh_clicker_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if "download_directory" in config:
                    self.download_directory = config["download_directory"]
                    self.dir_label.config(text=self.download_directory, fg="#27ae60")
                    self.check_ready_state()
                
                if "video_count" in config:
                    self.video_count = config["video_count"]
                    self.video_count_var.set(self.video_count)
                
                self.log_message("⚙️ Previous configuration loaded")
                
        except Exception as e:
            self.log_message(f"⚠️ Could not load previous config: {str(e)}")

    def save_session_config(self):
        """Save current session configuration"""
        try:
            config = {
                "download_directory": self.download_directory,
                "video_count": self.video_count,
                "last_updated": datetime.now().isoformat()
            }
            
            with open("vdh_clicker_config.json", 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception:
            pass  # Silent fail for config save

    def on_closing(self):
        """Handle application closing"""
        if self.session_active:
            result = messagebox.askyesno("Active Session", 
                "Download session is active. Stop and exit?")
            if not result:
                return
        
        self.save_session_config()
        self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 VDH Sequential Ribbon Clicker")
    print("Created: July 30, 2025 - 7:42 PM Pacific")
    print("Purpose: Sequential clicking of VDH download buttons")
    print()
    
    try:
        app = VDHSequentialClicker()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Application cancelled by user")
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())