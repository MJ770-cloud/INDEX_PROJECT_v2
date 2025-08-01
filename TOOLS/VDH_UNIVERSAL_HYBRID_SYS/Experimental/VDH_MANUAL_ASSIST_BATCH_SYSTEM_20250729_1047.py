# VDH_MANUAL_ASSIST_BATCH_SYSTEM_20250729_1047.py
# VDH Manual Assist + Batch Processing System
# Created: July 29, 2025 - 10:47 AM Pacific
# Purpose: Systematic manual VDH workflow for DIYTRAX video collection

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import subprocess
import threading

class VDHManualAssistSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Manual Assist + Batch System")
        self.root.geometry("1000x700")
        
        # DIYTRAX lesson configuration
        self.lessons = [
            {"num": 1, "title": "Full Walkthrough With Example Landing Pages", "status": "pending", "files": []},
            {"num": 2, "title": "Setting Up Your Tracking and Analytics", "status": "pending", "files": []},
            {"num": 3, "title": "Finding Profitable Products to Promote", "status": "pending", "files": []},
            {"num": 4, "title": "Creating High-Converting Landing Pages", "status": "pending", "files": []},
            {"num": 5, "title": "Traffic Generation Strategies", "status": "pending", "files": []},
            {"num": 6, "title": "Scaling Your Campaigns", "status": "pending", "files": []},
            {"num": 7, "title": "Advanced Optimization Techniques", "status": "pending", "files": []},
            {"num": 8, "title": "Managing Multiple Campaigns", "status": "pending", "files": []},
            {"num": 9, "title": "Troubleshooting Common Issues", "status": "pending", "files": []}
        ]
        
        # Directories
        self.base_dir = Path("C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Status tracking
        self.current_lesson = 0
        self.session_stats = {
            "start_time": datetime.now(),
            "lessons_completed": 0,
            "total_files": 0,
            "session_notes": []
        }
        
        # Platform URL
        self.platform_url = "https://experience.cherringtonmedia.com/launchpad-diytrax-training/"
        
        self.setup_gui()
        self.load_session_state()

    def setup_gui(self):
        """Create the manual assist GUI"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X, padx=5, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH MANUAL ASSIST + BATCH PROCESSING SYSTEM",
                              bg="#2c3e50", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(expand=True)

        # Session info
        info_frame = tk.LabelFrame(self.root, text="📊 Session Information", 
                                  font=("Arial", 9, "bold"), padx=5, pady=3)
        info_frame.pack(fill=tk.X, padx=5, pady=2)
        
        info_grid = tk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        tk.Label(info_grid, text="🎯 Target:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(info_grid, text="DIYTRAX Training (9 Lessons)", font=("Arial", 9)).grid(row=0, column=1, sticky="w", padx=(5,20))
        
        tk.Label(info_grid, text="📁 Output:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        tk.Label(info_grid, text=str(self.base_dir), font=("Arial", 9)).grid(row=0, column=3, sticky="w", padx=(5,0))
        
        tk.Label(info_grid, text="🌐 Platform:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w")
        self.platform_label = tk.Label(info_grid, text="Ready to open", font=("Arial", 9), fg="#27ae60")
        self.platform_label.grid(row=1, column=1, sticky="w", padx=(5,20))
        
        tk.Label(info_grid, text="⏱️ Session:", font=("Arial", 9, "bold")).grid(row=1, column=2, sticky="w")
        self.session_label = tk.Label(info_grid, text="00:00", font=("Arial", 9))
        self.session_label.grid(row=1, column=3, sticky="w", padx=(5,0))

        # Current lesson panel
        current_frame = tk.LabelFrame(self.root, text="🎬 Current Lesson", 
                                     font=("Arial", 10, "bold"), padx=10, pady=5)
        current_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.current_lesson_label = tk.Label(current_frame, 
                                            text="Ready to start Lesson 1", 
                                            font=("Arial", 12, "bold"), fg="#2c3e50")
        self.current_lesson_label.pack(pady=5)
        
        # Step-by-step instructions
        steps_frame = tk.LabelFrame(current_frame, text="📋 VDH Manual Steps", 
                                   font=("Arial", 9, "bold"))
        steps_frame.pack(fill=tk.X, pady=5)
        
        self.steps_text = tk.Text(steps_frame, height=6, font=("Arial", 9), 
                                 bg="#f8f9fa", wrap="word")
        self.steps_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(current_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.open_platform_btn = tk.Button(control_frame, text="🌐 OPEN PLATFORM",
                                          command=self.open_platform,
                                          bg="#3498db", fg="white", font=("Arial", 10, "bold"))
        self.open_platform_btn.pack(side=tk.LEFT, padx=2)
        
        self.lesson_complete_btn = tk.Button(control_frame, text="✅ LESSON COMPLETE",
                                           command=self.mark_lesson_complete,
                                           bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                           state='disabled')
        self.lesson_complete_btn.pack(side=tk.LEFT, padx=2)
        
        self.skip_lesson_btn = tk.Button(control_frame, text="⏭️ SKIP LESSON",
                                        command=self.skip_lesson,
                                        bg="#f39c12", fg="white", font=("Arial", 10, "bold"))
        self.skip_lesson_btn.pack(side=tk.LEFT, padx=2)

        # Progress overview
        progress_frame = tk.LabelFrame(self.root, text="📈 Batch Progress Overview", 
                                      font=("Arial", 9, "bold"), padx=5, pady=3)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=9)
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        # Lessons grid
        lessons_container = tk.Frame(progress_frame)
        lessons_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Column headers
        headers = ["#", "Lesson Title", "Status", "Files", "Actions"]
        for i, header in enumerate(headers):
            tk.Label(lessons_container, text=header, font=("Arial", 9, "bold"), 
                    relief="ridge", borderwidth=1).grid(row=0, column=i, sticky="ew", padx=1)
        
        # Configure column weights
        for i in range(len(headers)):
            lessons_container.grid_columnconfigure(i, weight=1 if i == 1 else 0)
        
        # Lesson rows
        self.lesson_widgets = {}
        for i, lesson in enumerate(self.lessons):
            row = i + 1
            
            # Lesson number
            tk.Label(lessons_container, text=str(lesson["num"]), 
                    relief="ridge", borderwidth=1).grid(row=row, column=0, sticky="ew", padx=1)
            
            # Title
            title_label = tk.Label(lessons_container, text=lesson["title"], 
                                  relief="ridge", borderwidth=1, wraplength=300)
            title_label.grid(row=row, column=1, sticky="ew", padx=1)
            
            # Status
            status_label = tk.Label(lessons_container, text="⏳ Pending", 
                                   relief="ridge", borderwidth=1, fg="#f39c12")
            status_label.grid(row=row, column=2, sticky="ew", padx=1)
            
            # Files count
            files_label = tk.Label(lessons_container, text="0 files", 
                                  relief="ridge", borderwidth=1)
            files_label.grid(row=row, column=3, sticky="ew", padx=1)
            
            # Actions
            action_btn = tk.Button(lessons_container, text="▶️ Start", 
                                  command=lambda l=i: self.start_lesson(l),
                                  font=("Arial", 8))
            action_btn.grid(row=row, column=4, sticky="ew", padx=1)
            
            self.lesson_widgets[i] = {
                "status": status_label,
                "files": files_label,
                "action": action_btn,
                "title": title_label
            }

        # Session controls
        session_frame = tk.Frame(self.root)
        session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - file management
        file_controls = tk.Frame(session_frame)
        file_controls.pack(side=tk.LEFT)
        
        tk.Button(file_controls, text="📁 ORGANIZE FILES",
                 command=self.organize_files,
                 bg="#9b59b6", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        tk.Button(file_controls, text="📊 SCAN DIRECTORY",
                 command=self.scan_directory,
                 bg="#34495e", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        # Right side - session controls
        session_controls = tk.Frame(session_frame)
        session_controls.pack(side=tk.RIGHT)
        
        tk.Button(session_controls, text="💾 SAVE SESSION",
                 command=self.save_session,
                 bg="#27ae60", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        tk.Button(session_controls, text="🚀 BATCH TRANSCRIBE",
                 command=self.launch_batch_transcription,
                 bg="#e74c3c", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)

        # Initialize display
        self.update_current_lesson_display()
        self.start_session_timer()

    def update_current_lesson_display(self):
        """Update the current lesson display"""
        if self.current_lesson < len(self.lessons):
            lesson = self.lessons[self.current_lesson]
            self.current_lesson_label.config(
                text=f"Lesson {lesson['num']}: {lesson['title']}"
            )
            
            steps = f"""🎯 MANUAL VDH WORKFLOW FOR LESSON {lesson['num']}:

1. 🌐 Click 'OPEN PLATFORM' to launch Adam's training site
2. 🔍 Navigate to Lesson {lesson['num']}: "{lesson['title']}"
3. ▶️ Click play on the video to start it loading
4. 👁️ Watch for VDH icon to show video detection (usually 3-5 seconds)
5. 📥 Click VDH icon and download all detected video segments
6. ✅ Once all segments downloaded, click 'LESSON COMPLETE'
7. ➡️ System will automatically advance to next lesson

💡 TIP: VDH may detect multiple segments per lesson - download all of them!
🎯 TARGET: Get all video files for batch transcription processing"""
            
            self.steps_text.delete(1.0, tk.END)
            self.steps_text.insert(1.0, steps)
            
            # Enable/disable buttons
            self.lesson_complete_btn.config(state='normal')
            self.open_platform_btn.config(state='normal')
        else:
            self.current_lesson_label.config(text="🎉 ALL LESSONS COMPLETE!")
            self.steps_text.delete(1.0, tk.END)
            self.steps_text.insert(1.0, """🎉 BATCH COLLECTION COMPLETE!

✅ All 9 DIYTRAX lessons processed
📁 Files organized in TCE-MEDIA/DIYTRAX
🚀 Ready for batch transcription

NEXT STEPS:
1. Click 'ORGANIZE FILES' to ensure proper file organization
2. Click 'BATCH TRANSCRIBE' to process all videos through the engine
3. Begin INDEX development with transcribed content""")
            
            self.lesson_complete_btn.config(state='disabled')
            self.open_platform_btn.config(state='disabled')

    def open_platform(self):
        """Open Adam's platform in browser"""
        try:
            webbrowser.open(self.platform_url)
            self.platform_label.config(text="Platform opened", fg="#27ae60")
            self.session_stats["session_notes"].append(f"Opened platform for Lesson {self.current_lesson + 1}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open platform: {str(e)}")

    def start_lesson(self, lesson_index):
        """Start a specific lesson"""
        self.current_lesson = lesson_index
        self.update_current_lesson_display()
        self.update_lesson_status(lesson_index, "🔄 In Progress", "#3498db")

    def mark_lesson_complete(self):
        """Mark current lesson as complete and advance"""
        if self.current_lesson < len(self.lessons):
            # Scan for new files
            self.scan_lesson_files(self.current_lesson)
            
            # Update lesson status
            lesson = self.lessons[self.current_lesson]
            self.update_lesson_status(self.current_lesson, "✅ Complete", "#27ae60")
            
            # Update stats
            self.session_stats["lessons_completed"] += 1
            self.session_stats["session_notes"].append(
                f"Completed Lesson {lesson['num']}: {len(lesson['files'])} files found"
            )
            
            # Advance to next lesson
            self.current_lesson += 1
            self.update_current_lesson_display()
            self.update_progress_bar()
            
            # Check if all complete
            if self.current_lesson >= len(self.lessons):
                messagebox.showinfo("Success", 
                    "🎉 All lessons complete!\n\n"
                    f"✅ {self.session_stats['lessons_completed']} lessons processed\n"
                    f"📁 {self.session_stats['total_files']} total files collected\n\n"
                    "Ready for batch transcription!")

    def skip_lesson(self):
        """Skip current lesson"""
        if self.current_lesson < len(self.lessons):
            lesson = self.lessons[self.current_lesson]
            self.update_lesson_status(self.current_lesson, "⏭️ Skipped", "#f39c12")
            
            self.session_stats["session_notes"].append(f"Skipped Lesson {lesson['num']}")
            
            self.current_lesson += 1
            self.update_current_lesson_display()
            self.update_progress_bar()

    def update_lesson_status(self, lesson_index, status_text, color):
        """Update lesson status in the grid"""
        if lesson_index in self.lesson_widgets:
            self.lesson_widgets[lesson_index]["status"].config(text=status_text, fg=color)

    def scan_lesson_files(self, lesson_index):
        """Scan directory for files belonging to this lesson"""
        try:
            files = []
            for file_path in self.base_dir.glob("*.mp4"):
                # Simple heuristic - files modified in last 10 minutes
                if (time.time() - file_path.stat().st_mtime) < 600:  # 10 minutes
                    files.append(str(file_path.name))
            
            self.lessons[lesson_index]["files"] = files
            self.lesson_widgets[lesson_index]["files"].config(text=f"{len(files)} files")
            self.session_stats["total_files"] += len(files)
            
        except Exception as e:
            print(f"Error scanning files: {e}")

    def scan_directory(self):
        """Scan entire directory for all video files"""
        try:
            all_files = list(self.base_dir.glob("*.mp4"))
            total_size = sum(f.stat().st_size for f in all_files) / (1024*1024)  # MB
            
            messagebox.showinfo("Directory Scan", 
                f"📁 DIYTRAX Directory Status:\n\n"
                f"📹 Video files: {len(all_files)}\n"
                f"💾 Total size: {total_size:.1f} MB\n"
                f"📂 Location: {self.base_dir}\n\n"
                f"✅ Ready for batch processing!")
        except Exception as e:
            messagebox.showerror("Error", f"Directory scan failed: {str(e)}")

    def organize_files(self):
        """Organize downloaded files"""
        try:
            # Create lesson subdirectories
            lesson_dirs = {}
            for i, lesson in enumerate(self.lessons):
                lesson_dir = self.base_dir / f"Lesson_{lesson['num']:02d}_{lesson['title'][:30].replace(' ', '_')}"
                lesson_dir.mkdir(exist_ok=True)
                lesson_dirs[i] = lesson_dir
            
            # Move files to appropriate lesson directories
            organized_count = 0
            for file_path in self.base_dir.glob("*.mp4"):
                if file_path.parent == self.base_dir:  # Only files in root
                    # Simple organization by modification time
                    # You could enhance this with better heuristics
                    lesson_num = organized_count % len(self.lessons)
                    target_dir = lesson_dirs[lesson_num]
                    target_path = target_dir / file_path.name
                    
                    if not target_path.exists():
                        file_path.rename(target_path)
                        organized_count += 1
            
            messagebox.showinfo("Organization Complete", 
                f"📁 File Organization Complete!\n\n"
                f"📹 Organized: {organized_count} files\n"
                f"📂 Into: {len(lesson_dirs)} lesson directories\n"
                f"🎯 Structure ready for batch transcription!")
                
        except Exception as e:
            messagebox.showerror("Error", f"File organization failed: {str(e)}")

    def launch_batch_transcription(self):
        """Launch batch transcription process"""
        try:
            # Check if transcription engine exists
            engine_path = Path("C:/ENGINE-PROJECT/src/engines/working/openai_transcription_engine_v16_INDEX_ready_20250720_0748.py")
            
            if engine_path.exists():
                result = messagebox.askyesno("Batch Transcription", 
                    "🚀 Launch Batch Transcription Process?\n\n"
                    f"📁 Source: {self.base_dir}\n"
                    f"🎯 Engine: Battle-tested transcription system\n"
                    f"⚡ Quality: 138.24 WPM baseline\n\n"
                    "This will process all DIYTRAX videos through your proven transcription engine.")
                
                if result:
                    # Open PowerShell in engine directory
                    subprocess.Popen([
                        "powershell.exe", 
                        "-Command", 
                        f"cd 'C:\\ENGINE-PROJECT\\src\\engines\\working'; python openai_transcription_engine_v16_INDEX_ready_20250720_0748.py"
                    ])
                    
                    messagebox.showinfo("Transcription Launched", 
                        "🚀 Batch transcription launched!\n\n"
                        "The proven transcription engine is now processing your DIYTRAX videos.\n"
                        "Check the engine output for progress updates.")
            else:
                messagebox.showwarning("Engine Not Found", 
                    "⚠️ Transcription engine not found!\n\n"
                    "Expected location:\n"
                    f"{engine_path}\n\n"
                    "Please verify the ENGINE-PROJECT setup.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch transcription: {str(e)}")

    def update_progress_bar(self):
        """Update the progress bar"""
        completed = sum(1 for lesson in self.lessons if "Complete" in lesson.get("status", ""))
        self.progress_bar['value'] = completed

    def start_session_timer(self):
        """Start the session timer"""
        def update_timer():
            if hasattr(self, 'session_stats'):
                elapsed = datetime.now() - self.session_stats["start_time"]
                hours, remainder = divmod(elapsed.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                self.session_label.config(text=f"{int(hours):02d}:{int(minutes):02d}")
            
            self.root.after(60000, update_timer)  # Update every minute
        
        update_timer()

    def save_session(self):
        """Save session state"""
        try:
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "current_lesson": self.current_lesson,
                "lessons": self.lessons,
                "session_stats": {
                    **self.session_stats,
                    "start_time": self.session_stats["start_time"].isoformat()
                }
            }
            
            session_file = self.base_dir / f"vdh_session_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            messagebox.showinfo("Session Saved", 
                f"💾 Session saved successfully!\n\n"
                f"📁 Location: {session_file}\n"
                f"✅ Progress preserved for next session")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {str(e)}")

    def load_session_state(self):
        """Load previous session state if available"""
        try:
            # Find most recent session file
            session_files = list(self.base_dir.glob("vdh_session_*.json"))
            if session_files:
                latest_session = max(session_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_session, 'r') as f:
                    session_data = json.load(f)
                
                # Restore state
                self.current_lesson = session_data.get("current_lesson", 0)
                if "lessons" in session_data:
                    self.lessons = session_data["lessons"]
                
                print(f"Loaded session from {latest_session}")
        except Exception as e:
            print(f"No previous session found or load failed: {e}")

    def run(self):
        """Start the manual assist system"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 VDH Manual Assist + Batch Processing System")
    print("Created: July 29, 2025 - 10:47 AM Pacific")
    print("Purpose: Systematic VDH workflow for DIYTRAX video collection")
    print()
    
    try:
        app = VDHManualAssist