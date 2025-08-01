# VDH_SIMPLE_CLICKER_20250730_2008.py
# VDH Simple Sequential Clicker - Clean Version
# Created: July 30, 2025 - 8:08 PM Pacific
# Purpose: Simple sequential clicking with file monitoring - Triple Checked

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
        self.check_interval = 3
        self.completion_wait = 10
        self.max_wait_time = 180
        
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
            self.log_message("📁 Found DIYTRAX directory: " + default_dir)

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
            self.log_message("📁 Download directory set: " + directory)

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
        
        # Count existing files
        try:
            existing_files = [f for f in os.listdir(self.download_directory) 
                             if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
            self.last_file_count = len(existing_files)
        except Exception:
            self.last_file_count = 0
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.log_message("🚀 Starting download sequence...")
        self.log_message("📁 Monitoring: " + self.download_directory)
        self.log_message("🎬 Expected videos: " + str(self.video_count))
        self.log_message("📊 Current files: " + str(self.last_file_count))
        
        # Start the sequence
        self.next_video()

    def next_video(self):
        """Process next video in sequence"""
        if not self.session_active or self.current_video >= self.video_count:
            self.complete_session()
            return
        
        self.current_video += 1
        video_text = "🎬 Video " + str(self.current_video) + "/" + str(self.video_count) + " - READY TO CLICK"
        self.current_video_label.config(text=video_text)
        
        self.log_message("\n" + "="*40)
        self.log_message("🎯 READY FOR VIDEO " + str(self.current_video))
        self.log_message("👆 Click the VDH download button for video " + str(self.current_video))
        self.log_message("⏳ Tool will detect when download completes...")
        
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
                        self.log_message("📥 Detected " + str(new_files) + " new file(s)")
                        
                        # Wait for download to complete
                        if self.wait_for_file_stability():
                            self.session_stats["completed_videos"] += 1
                            self.session_stats["total_files_downloaded"] = current_count
                            self.last_file_count = current_count
                            
                            self.log_message("✅ Video " + str(self.current_video) + " completed!")
                            self.progress_bar['value'] = self.current_video
                            
                            # Small delay then next video
                            time.sleep(2)
                            if self.session_active:
                                self.root.after(0, self.next_video)
                            return
                        
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.log_message("❌ Monitoring error: " + str(e))
                    break
            
            # Timeout or error
            if self.session_active:
                self.log_message("⏰ Timeout waiting for video " + str(self.current_video))
                self.log_message("❓ Click 'STOP' and check VDH manually")
        
        self.monitoring_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitoring_thread.start()

    def wait_for_file_stability(self):
        """Wait for file download to stabilize"""
        try:
            self.log_message("⏳ Waiting for download completion...")
            
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
            
            for check_count in range(self.completion_wait):
                if not self.session_active:
                    return False
                
                try:
                    current_size = os.path.getsize(newest_file)
                    
                    if current_size == last_size and current_size > 1024:
                        stable_count += 1
                        if stable_count >= 3:
                            size_mb = current_size / (1024 * 1024)
                            filename = os.path.basename(newest_file)
                            self.log_message("📁 File stable: " + filename + " (" + str(round(size_mb, 1)) + " MB)")
                            return True
                    else:
                        stable_count = 0
                        last_size = current_size
                    
                    time.sleep(1)
                except Exception:
                    break
            
            return False
            
        except Exception as e:
            self.log_message("❌ Stability check error: " + str(e))
            return False

    def stop_session(self):
        """Stop the current session"""
        self.session_active = False
        self.log_message("⏹️ Session stopped by user")
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.current_video_label.config(text="Session stopped")

    def complete_session(self):
        """Complete the download session"""
        self.session_active = False
        
        if self.session_stats["start_time"]:
            duration = datetime.now() - self.session_stats["start_time"]
            duration_str = str(duration).split('.')[0]
        else:
            duration_str = "Unknown"
        
        self.log_message("\n" + "="*40)
        self.log_message("🎉 DOWNLOAD SEQUENCE COMPLETE!")
        completed_text = "✅ Completed: " + str(self.session_stats["completed_videos"]) + "/" + str(self.video_count) + " videos"
        self.log_message(completed_text)
        self.log_message("📁 Total files: " + str(self.session_stats["total_files_downloaded"]))
        self.log_message("⏱️ Duration: " + duration_str)
        
        # Reset UI
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.current_video_label.config(text="🎉 Sequence complete!")
        
        # Show completion dialog
        completion_msg = ("🎉 Download sequence completed!\n\n" +
                         "✅ Videos: " + str(self.session_stats["completed_videos"]) + "/" + str(self.video_count) + "\n" +
                         "📁 Total files: " + str(self.session_stats["total_files_downloaded"]) + "\n" +
                         "⏱️ Duration: " + duration_str + "\n\n" +
                         "📂 Files saved to: " + self.download_directory)
        messagebox.showinfo("Sequence Complete", completion_msg)

    def open_download_directory(self):
        """Open download directory"""
        if self.download_directory and os.path.exists(self.download_directory):
            os.startfile(self.download_directory)
        else:
            messagebox.showwarning("Error", "Download directory not found")

    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = "[" + timestamp + "] " + message + "\n"
        
        self.log_text.insert(tk.END, full_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 VDH Simple Sequential Clicker")
    print("Created: July 30, 2025 - 8:08 PM Pacific") 
    print("Purpose: Simple VDH download assistance")
    print()
    
    try:
        app = VDHSimpleClicker()
        app.run()
    except Exception as e:
        print("❌ Error: " + str(e))
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())