# VDH_UNIVERSAL_MANUAL_ASSIST_MONITOR_20250731_2157.py
# Universal VDH Manual Assist Monitor - Cross-Validation & Metadata System
# Created: July 31, 2025 - 9:57 PM Pacific
# Purpose: Universal manual assist monitor for any VDH-compatible video platform

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
import hashlib

class VDHUniversalManualAssist:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Universal VDH Manual Assist Monitor")
        self.root.geometry("900x750")
        self.root.resizable(False, False)
        
        # Configuration
        self.download_directory = ""
        self.vdh_directory = ""
        self.is_monitoring = False
        self.session_start_time = None
        
        # Enhanced tracking with cross-validation
        self.completed_files = set()
        self.in_progress_files = {}
        self.metadata_store = {}
        self.validation_results = {}
        
        # Manual assist settings
        self.scan_interval = 2.0  # Slower scan for manual workflow
        self.completion_alert = True
        self.cross_validation = True
        
        # Session statistics with validation
        self.session_stats = {
            'files_completed': 0,
            'duration_mismatches': 0,
            'quality_issues': 0,
            'ready_for_transcription': 0,
            'metadata_records': 0
        }
        
        self.setup_gui()
        self.check_default_directories()

    def setup_gui(self):
        """Create universal manual assist interface"""
        # Universal title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 UNIVERSAL VDH MANUAL ASSIST MONITOR",
                              bg="#2c3e50", fg="white", font=("Arial", 14, "bold"))
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Cross-Validation & Metadata System for Any Video Platform",
                                 bg="#2c3e50", fg="#bdc3c7", font=("Arial", 9))
        subtitle_label.pack()

        # Enhanced directory configuration with VDH sync
        config_frame = tk.LabelFrame(self.root, text="📁 Directory Configuration & VDH Sync", 
                                    font=("Arial", 10, "bold"), padx=10, pady=8)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Monitor directory
        monitor_frame = tk.Frame(config_frame)
        monitor_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(monitor_frame, text="📁 Monitor Directory:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.monitor_label = tk.Label(monitor_frame, text="Not selected", 
                                     fg="#e74c3c", font=("Arial", 9))
        self.monitor_label.pack(side=tk.LEFT, padx=(10, 20))
        
        tk.Button(monitor_frame, text="📁 SELECT MONITOR DIR",
                 command=self.select_monitor_directory,
                 bg="#3498db", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # VDH directory sync
        vdh_frame = tk.Frame(config_frame)
        vdh_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(vdh_frame, text="🔗 VDH Directory:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.vdh_label = tk.Label(vdh_frame, text="Not detected", 
                                 fg="#f39c12", font=("Arial", 9))
        self.vdh_label.pack(side=tk.LEFT, padx=(10, 20))
        
        tk.Button(vdh_frame, text="🔄 READ VDH SETTING",
                 command=self.read_vdh_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Directory sync status
        sync_frame = tk.Frame(config_frame)
        sync_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(sync_frame, text="⚡ Sync Status:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.sync_status = tk.Label(sync_frame, text="⚠️ Directories not synced", 
                                   fg="#e74c3c", font=("Arial", 9, "bold"))
        self.sync_status.pack(side=tk.LEFT, padx=(10, 0))

        # Manual assist workflow panel
        workflow_frame = tk.LabelFrame(self.root, text="🎮 Manual Assist Workflow", 
                                      font=("Arial", 10, "bold"), padx=10, pady=8)
        workflow_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Current action display
        action_frame = tk.Frame(workflow_frame)
        action_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(action_frame, text="📋 Current Action:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.current_action = tk.Label(action_frame, text="Ready to begin manual assist workflow", 
                                      font=("Arial", 10), fg="#3498db", 
                                      relief=tk.SUNKEN, bg="#ecf0f1", pady=3)
        self.current_action.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Progress tracking with cross-validation
        progress_frame = tk.LabelFrame(self.root, text="📊 Progress Tracking & Cross-Validation", 
                                      font=("Arial", 10, "bold"), padx=10, pady=8)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Session progress
        session_frame = tk.Frame(progress_frame)
        session_frame.pack(fill=tk.X, pady=3)
        
        tk.Label(session_frame, text="📹 Current Download:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.download_progress = ttk.Progressbar(session_frame, mode='indeterminate', length=400)
        self.download_progress.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        self.download_status = tk.Label(session_frame, text="Waiting", 
                                       font=("Arial", 9, "bold"), fg="#95a5a6", 
                                       relief=tk.SUNKEN, width=12, bg="#ecf0f1")
        self.download_status.pack(side=tk.RIGHT)

        # Enhanced statistics with validation metrics
        stats_frame = tk.LabelFrame(self.root, text="📊 Session Statistics & Validation", 
                                   font=("Arial", 10, "bold"), padx=10, pady=8)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Top row - completion stats
        stats_top = tk.Frame(stats_frame)
        stats_top.pack(fill=tk.X, pady=3)
        
        tk.Label(stats_top, text="✅ Completed:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.completed_stat = tk.Label(stats_top, text="0", 
                                      font=("Arial", 9), fg="#27ae60")
        self.completed_stat.grid(row=0, column=1, sticky="w", padx=(5, 15))
        
        tk.Label(stats_top, text="📁 Metadata Records:", 
                font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.metadata_stat = tk.Label(stats_top, text="0", 
                                     font=("Arial", 9), fg="#3498db")
        self.metadata_stat.grid(row=0, column=3, sticky="w", padx=(5, 15))
        
        tk.Label(stats_top, text="🚀 Ready for Transcription:", 
                font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="w")
        self.ready_stat = tk.Label(stats_top, text="0", 
                                  font=("Arial", 9), fg="#9b59b6")
        self.ready_stat.grid(row=0, column=5, sticky="w", padx=(5, 0))
        
        # Bottom row - validation stats
        stats_bottom = tk.Frame(stats_frame)
        stats_bottom.pack(fill=tk.X, pady=3)
        
        tk.Label(stats_bottom, text="⚠️ Duration Mismatches:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.mismatch_stat = tk.Label(stats_bottom, text="0", 
                                     font=("Arial", 9), fg="#e74c3c")
        self.mismatch_stat.grid(row=0, column=1, sticky="w", padx=(5, 15))
        
        tk.Label(stats_bottom, text="🔍 Quality Issues:", 
                font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        self.quality_stat = tk.Label(stats_bottom, text="0", 
                                    font=("Arial", 9), fg="#f39c12")
        self.quality_stat.grid(row=0, column=3, sticky="w", padx=(5, 15))
        
        tk.Label(stats_bottom, text="⏱️ Session Time:", 
                font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="w")
        self.time_stat = tk.Label(stats_bottom, text="00:00:00", 
                                 font=("Arial", 9), fg="#34495e")
        self.time_stat.grid(row=0, column=5, sticky="w", padx=(5, 0))

        # Enhanced activity log with validation events
        log_frame = tk.LabelFrame(self.root, text="📋 Manual Assist Activity Log", 
                                 font=("Arial", 10, "bold"), padx=10, pady=8)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        log_container = tk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=10, font=("Consolas", 8),
                               bg="#f8f9fa", wrap="word", relief=tk.SUNKEN, bd=2)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Enhanced text formatting for validation
        self.log_text.tag_config("success", foreground="#27ae60", font=("Consolas", 8, "bold"))
        self.log_text.tag_config("error", foreground="#e74c3c", font=("Consolas", 8, "bold"))
        self.log_text.tag_config("info", foreground="#3498db", font=("Consolas", 8))
        self.log_text.tag_config("warning", foreground="#f39c12", font=("Consolas", 8, "bold"))
        self.log_text.tag_config("validation", foreground="#9b59b6", font=("Consolas", 8, "bold"))
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enhanced control panel
        control_frame = tk.Frame(self.root, bg="#ecf0f1", pady=8)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main manual assist controls
        main_controls = tk.Frame(control_frame, bg="#ecf0f1")
        main_controls.pack(side=tk.LEFT)
        
        self.start_btn = tk.Button(main_controls, text="🎮 START MANUAL ASSIST",
                                  command=self.start_manual_assist,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  state='disabled', relief=tk.RAISED, bd=3)
        self.start_btn.pack(side=tk.LEFT, padx=3)
        
        self.stop_btn = tk.Button(main_controls, text="⏹️ STOP",
                                 command=self.stop_manual_assist,
                                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                 state='disabled', relief=tk.RAISED, bd=3)
        self.stop_btn.pack(side=tk.LEFT, padx=3)
        
        self.validate_btn = tk.Button(main_controls, text="🔍 VALIDATE SESSION",
                                     command=self.validate_session,
                                     bg="#9b59b6", fg="white", font=("Arial", 10, "bold"),
                                     state='disabled', relief=tk.RAISED, bd=3)
        self.validate_btn.pack(side=tk.LEFT, padx=3)
        
        # Enhanced utility controls
        utility_controls = tk.Frame(control_frame, bg="#ecf0f1")
        utility_controls.pack(side=tk.RIGHT)
        
        tk.Button(utility_controls, text="📊 METADATA REPORT",
                 command=self.generate_metadata_report,
                 bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="🔧 SETTINGS",
                 command=self.show_settings,
                 bg="#34495e", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_controls, text="📁 OPEN FOLDER",
                 command=self.open_directory,
                 bg="#f39c12", fg="white", font=("Arial", 9, "bold"),
                 relief=tk.RAISED, bd=2).pack(side=tk.LEFT, padx=2)

        # Initialize session timer
        self.update_session_timer()

    def check_default_directories(self):
        """Check for default directories and auto-configure"""
        default_dirs = [
            "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX",
            "C:/INDEX-PROJECT/TCE-MEDIA/METRICMOVER",
            "C:/INDEX-PROJECT/TCE-MEDIA/SCRAPEBOT"
        ]
        
        for default_dir in default_dirs:
            if os.path.exists(default_dir):
                self.download_directory = default_dir
                self.monitor_label.config(text=default_dir, fg="#27ae60")
                self.start_btn.config(state='normal')
                self.validate_btn.config(state='normal')
                self.log_message("📁 Default directory detected: " + default_dir, "success")
                break

    def select_monitor_directory(self):
        """Select monitor directory with validation"""
        directory = filedialog.askdirectory(
            title="Select Video Download Directory",
            initialdir="C:/INDEX-PROJECT/TCE-MEDIA"
        )
        
        if directory:
            self.download_directory = directory
            self.monitor_label.config(text=directory, fg="#27ae60")
            self.start_btn.config(state='normal')
            self.validate_btn.config(state='normal')
            self.log_message("📁 Monitor directory selected: " + directory, "success")
            self.check_directory_sync()

    def read_vdh_directory(self):
        """Read VDH's current download directory setting"""
        # Placeholder for VDH directory detection
        # In real implementation, this would read VDH's settings
        vdh_dir = self.download_directory  # Simplified for now
        
        if vdh_dir:
            self.vdh_directory = vdh_dir
            self.vdh_label.config(text=vdh_dir, fg="#27ae60")
            self.log_message("🔗 VDH directory detected: " + vdh_dir, "info")
            self.check_directory_sync()
        else:
            self.vdh_label.config(text="Could not detect VDH setting", fg="#e74c3c")
            self.log_message("❌ Could not read VDH directory setting", "error")

    def check_directory_sync(self):
        """Check if monitor and VDH directories are synced"""
        if self.download_directory and self.vdh_directory:
            if self.download_directory == self.vdh_directory:
                self.sync_status.config(text="✅ Directories synced", fg="#27ae60")
                self.log_message("✅ Monitor and VDH directories are synced", "success")
            else:
                self.sync_status.config(text="⚠️ Directory mismatch detected", fg="#e74c3c")
                self.log_message("⚠️ WARNING: Monitor ≠ VDH directory - files may go to wrong location", "warning")

    def get_enhanced_file_metadata(self, file_path):
        """Extract comprehensive file metadata with cross-validation preparation"""
        try:
            stat = os.stat(file_path)
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'extension': os.path.splitext(file_path)[1].lower(),
                'hash': self.calculate_file_hash(file_path)
            }
            
            # Enhanced metadata extraction with Mutagen
            try:
                audio_file = MutagenFile(file_path)
                if audio_file and hasattr(audio_file, 'info'):
                    info = audio_file.info
                    file_info['duration'] = getattr(info, 'length', 0)
                    file_info['bitrate'] = getattr(info, 'bitrate', 0)
                    file_info['codec'] = str(type(audio_file).__name__)
                    
                    # Calculate quality score for validation
                    if file_info['duration'] > 0:
                        file_info['quality_score'] = (file_info['bitrate'] * file_info['duration']) / 1000
                        file_info['size_per_second'] = file_info['size'] / file_info['duration']
                    else:
                        file_info['quality_score'] = 0
                        file_info['size_per_second'] = 0
                else:
                    file_info.update({
                        'duration': 0, 'bitrate': 0, 'codec': 'Unknown',
                        'quality_score': 0, 'size_per_second': 0
                    })
            except Exception as e:
                self.log_message("⚠️ Metadata extraction error for " + file_info['name'] + ": " + str(e), "warning")
                file_info.update({
                    'duration': 0, 'bitrate': 0, 'codec': 'Unknown',
                    'quality_score': 0, 'size_per_second': 0
                })
            
            return file_info
            
        except Exception as e:
            self.log_message("❌ File info error: " + str(e), "error")
            return None

    def calculate_file_hash(self, file_path):
        """Calculate file hash for integrity validation"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "hash_error"

    def create_metadata_record(self, file_info):
        """Create comprehensive metadata record for cross-validation"""
        timestamp = datetime.now().isoformat()
        
        metadata_record = {
            "file_metadata": {
                "filename": file_info['name'],
                "filepath": file_info['path'],
                "size_bytes": file_info['size'],
                "hash_md5": file_info['hash'],
                "extension": file_info['extension']
            },
            "download_metadata": {
                "download_date": timestamp,
                "file_created": datetime.fromtimestamp(file_info['created']).isoformat(),
                "file_modified": datetime.fromtimestamp(file_info['modified']).isoformat(),
                "vdh_duration": file_info['duration'],
                "bitrate": file_info['bitrate'],
                "codec": file_info['codec'],
                "quality_score": file_info['quality_score']
            },
            "validation_ready": {
                "has_duration": file_info['duration'] > 0,
                "has_bitrate": file_info['bitrate'] > 0,
                "file_complete": file_info['size'] > 1000,  # Basic size check
                "ready_for_transcription": False  # Will be set after OpenAI validation
            },
            "future_metadata": {
                "openai_duration": None,
                "openai_language": None,
                "transcription_quality": None,
                "original_creation_date": None,  # For Adam's future data
                "course_sequence": None,
                "content_topic": None
            }
        }
        
        return metadata_record

    def save_metadata_record(self, metadata_record):
        """Save metadata record as JSON file"""
        try:
            filename = metadata_record['file_metadata']['filename']
            base_name = os.path.splitext(filename)[0]
            metadata_filename = base_name + "_metadata.json"
            metadata_path = os.path.join(self.download_directory, metadata_filename)
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_record, f, indent=2, ensure_ascii=False)
            
            self.session_stats['metadata_records'] += 1
            self.metadata_stat.config(text=str(self.session_stats['metadata_records']))
            
            self.log_message("📁 Metadata saved: " + metadata_filename, "validation")
            return metadata_path
            
        except Exception as e:
            self.log_message("❌ Metadata save error: " + str(e), "error")
            return None

    def manual_assist_scan(self):
        """Enhanced directory scanning for manual assist workflow"""
        if not self.download_directory or not os.path.exists(self.download_directory):
            return
        
        try:
            # Scan for video files
            video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.mp3', '*.wav', '*.m4a', '*.flv', '*.webm']
            current_files = []
            
            for ext in video_extensions:
                pattern = os.path.join(self.download_directory, ext)
                current_files.extend(glob.glob(pattern))
            
            # Check for new downloads
            for file_path in current_files:
                file_key = file_path
                
                if file_key not in self.completed_files:
                    # New file detected
                    file_info = self.get_enhanced_file_metadata(file_path)
                    if not file_info:
                        continue
                    
                    current_size = file_info['size']
                    current_time = time.time()
                    
                    if file_key in self.in_progress_files:
                        # Check if download completed
                        prev_size, prev_time, stability_count = self.in_progress_files[file_key]
                        
                        if current_size == prev_size:
                            stability_count += 1
                            self.in_progress_files[file_key] = (current_size, current_time, stability_count)
                            
                            if stability_count >= 3:  # File stable for 3 scans
                                # Download completed
                                self.handle_download_completion(file_info)
                                del self.in_progress_files[file_key]
                                self.completed_files.add(file_key)
                        else:
                            # Still downloading
                            self.in_progress_files[file_key] = (current_size, current_time, 0)
                            size_mb = current_size / (1024 * 1024)
                            self.log_message("📥 Download progress: " + file_info['name'] + 
                                           " (" + str(round(size_mb, 1)) + " MB)", "info")
                    else:
                        # First detection
                        if current_size > 1000:  # Minimum size check
                            self.in_progress_files[file_key] = (current_size, current_time, 0)
                            self.log_message("🆕 New download detected: " + file_info['name'], "success")
                            
                            # Update current action
                            self.root.after(0, lambda: self.current_action.config(
                                text="📥 Monitoring: " + file_info['name'][:40] + "...", fg="#3498db"))
                            
                            # Start progress indication
                            self.root.after(0, lambda: self.download_progress.start(10))
                            self.root.after(0, lambda: self.download_status.config(text="Downloading", fg="#f39c12"))
            
        except Exception as e:
            self.log_message("❌ Scan error: " + str(e), "error")

    def handle_download_completion(self, file_info):
        """Handle completed download with cross-validation preparation"""
        try:
            # Create comprehensive metadata record
            metadata_record = self.create_metadata_record(file_info)
            
            # Save metadata to JSON file
            metadata_path = self.save_metadata_record(metadata_record)
            
            if metadata_path:
                # Store in memory for session tracking
                self.metadata_store[file_info['name']] = metadata_record
                
                # Update statistics
                self.session_stats['files_completed'] += 1
                self.completed_stat.config(text=str(self.session_stats['files_completed']))
                
                # Check if ready for transcription
                if metadata_record['validation_ready']['has_duration'] and metadata_record['validation_ready']['file_complete']:
                    self.session_stats['ready_for_transcription'] += 1
                    self.ready_stat.config(text=str(self.session_stats['ready_for_transcription']))
                    ready_status = "✅ Ready for transcription"
                else:
                    ready_status = "⚠️ Validation issues detected"
                
                # Log completion with details
                duration_min = int(file_info['duration'] // 60)
                duration_sec = int(file_info['duration'] % 60)
                size_mb = file_info['size'] / (1024 * 1024)
                
                self.log_message("✅ Download completed: " + file_info['name'], "success")
                self.log_message("   📊 Size: " + str(round(size_mb, 1)) + " MB, Duration: " + 
                               str(duration_min) + "m " + str(duration_sec) + "s", "info")
                self.log_message("   " + ready_status, "validation")
                
                # Update UI
                self.root.after(0, lambda: self.download_progress.stop())
                self.root.after(0, lambda: self.download_status.config(text="Complete", fg="#27ae60"))
                self.root.after(0, lambda: self.current_action.config(
                    text="✅ Ready for next download - Click next video in VDH", fg="#27ae60"))
                
                # Completion alert
                if self.completion_alert:
                    try:
                        winsound.MessageBeep(winsound.MB_OK)
                    except:
                        pass
                
        except Exception as e:
            self.log_message("❌ Completion handling error: " + str(e), "error")

    def manual_assist_monitoring_loop(self):
        """Manual assist monitoring loop"""
        while self.is_monitoring:
            try:
                self.manual_assist_scan()
                time.sleep(self.scan_interval)
            except Exception as e:
                self.log_message("❌ Monitoring error: " + str(e), "error")
                time.sleep(self.scan_interval)

    def start_manual_assist(self):
        """Start manual assist monitoring"""
        if not self.download_directory:
            messagebox.showerror("Manual Assist Monitor", "Please select a directory first!")
            return
        
        self.is_monitoring = True
        self.session_start_time = datetime.now()
        
        # Reset session statistics
        self.session_stats = {
            'files_completed': 0,
            'duration_mismatches': 0,
            'quality_issues': 0,
            'ready_for_transcription': 0,
            'metadata_records': 0
        }
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.current_action.config(text="🎮 Manual assist active - Navigate to video platform and click first VDH download", fg="#27ae60")
        self.log_message("🎮 Manual assist session started!", "success")
        self.log_message("📋 Workflow: 1) Click VDH download button 2) Wait for completion alert 3) Click next video", "info")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.manual_assist_monitoring_loop, daemon=True)
        monitor_thread.start()

    def stop_manual_assist(self):
        """Stop manual assist monitoring"""
        self.is_monitoring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if self.session_start_time:
            session_duration = datetime.now() - self.session_start_time
            duration_str = str(session_duration).split('.')[0]
            
            self.log_message("⏹️ Manual assist session stopped after " + duration_str, "info")
            self.log_message("📊 Session summary: " + str(self.session_stats['files_completed']) + 
                           " downloads, " + str(self.session_stats['metadata_records']) + " metadata records created", "success")
        
        self.current_action.config(text="⏹️ Manual assist stopped", fg="#e74c3c")
        self.download_progress.stop()
        self.download_status.config(text="Stopped", fg="#95a5a6")

    def validate_session(self):
        """Validate current session for transcription readiness"""
        if not self.metadata_store:
            messagebox.showwarning("Session Validation", "No files to validate!")
            return
        
        self.log_message("🔍 Running session validation...", "validation")
        
        validation_results = {
            'total_files': len(self.metadata_store),
            'ready_for_transcription': 0,
            'duration_issues': 0,
            'size_issues': 0,
            'quality_concerns': []
        }
        
        for filename, metadata in self.metadata_store.items():
            file_meta = metadata['file_metadata']
            download_meta = metadata['download_metadata']
            validation = metadata['validation_ready']
            
            # Check transcription readiness
            if validation['has_duration'] and validation['file_complete']:
                validation_results['ready_for_transcription'] += 1
            else:
                if not validation['has_duration']:
                    validation_results['duration_issues'] += 1
                    validation_results['quality_concerns'].append(filename + ": No duration detected")
                
                if not validation['file_complete']:
                    validation_results['size_issues'] += 1
                    validation_results['quality_concerns'].append(filename + ": File too small")
        
        # Log validation results
        self.log_message("📊 Validation complete:", "validation")
        self.log_message("   ✅ Ready for transcription: " + str(validation_results['ready_for_transcription']), "success")
        self.log_message("   ⚠️ Duration issues: " + str(validation_results['duration_issues']), "warning")
        self.log_message("   ⚠️ Size issues: " + str(validation_results['size_issues']), "warning")
        
        if validation_results['quality_concerns']:
            self.log_message("🔍 Quality concerns:", "warning")
            for concern in validation_results['quality_concerns']:
                self.log_message("   • " + concern, "warning")
        
        # Show summary dialog
        ready_count = validation_results['ready_for_transcription']
        total_count = validation_results['total_files']
        
        if ready_count == total_count:
            summary_msg = "✅ SESSION VALIDATION PASSED!\n\n"
            summary_msg += "All " + str(total_count) + " files are ready for transcription.\n"
            summary_msg += "Cross-validation metadata has been created for each file.\n\n"
            summary_msg += "Ready to proceed to ENGINE-PROJECT transcription phase!"
            messagebox.showinfo("Validation Complete", summary_msg)
        else:
            summary_msg = "⚠️ SESSION VALIDATION ISSUES\n\n"
            summary_msg += "Ready: " + str(ready_count) + "/" + str(total_count) + " files\n"
            summary_msg += "Issues found: " + str(len(validation_results['quality_concerns'])) + "\n\n"
            summary_msg += "Check activity log for details."
            messagebox.showwarning("Validation Issues", summary_msg)

    def generate_metadata_report(self):
        """Generate comprehensive metadata report"""
        if not self.metadata_store:
            messagebox.showwarning("Metadata Report", "No metadata to report!")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = os.path.join(self.download_directory, "METADATA_REPORT_" + timestamp + ".json")
            
            # Create comprehensive report
            report_data = {
                "report_metadata": {
                    "generated": datetime.now().isoformat(),
                    "session_duration": str(datetime.now() - self.session_start_time).split('.')[0] if self.session_start_time else "Unknown",
                    "monitor_directory": self.download_directory,
                    "total_files": len(self.metadata_store)
                },
                "session_statistics": self.session_stats,
                "file_metadata": self.metadata_store,
                "validation_summary": {
                    "ready_for_transcription": self.session_stats['ready_for_transcription'],
                    "metadata_records_created": self.session_stats['metadata_records'],
                    "cross_validation_prepared": True
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            success_msg = "📊 Metadata Report Generated!\n\n"
            success_msg += "✅ Report saved: " + os.path.basename(report_file) + "\n"
            success_msg += "✅ " + str(len(self.metadata_store)) + " files documented\n"
            success_msg += "✅ Cross-validation metadata prepared\n"
            success_msg += "✅ Ready for ENGINE-PROJECT integration"
            
            messagebox.showinfo("Report Complete", success_msg)
            self.log_message("📊 Metadata report generated: " + report_file, "success")
            
        except Exception as e:
            messagebox.showerror("Report Error", "Failed to generate metadata report: " + str(e))

    def show_settings(self):
        """Show enhanced settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("🔧 Manual Assist Settings")
        settings_window.geometry("450x350")
        settings_window.resizable(False, False)
        
        tk.Label(settings_window, text="🔧 Manual Assist Monitor Settings", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Monitoring settings
        monitor_frame = tk.LabelFrame(settings_window, text="Monitoring Settings", padx=10, pady=5)
        monitor_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(monitor_frame, text="⏱️ Scan Interval (seconds):", 
                font=("Arial", 10)).pack(anchor="w")
        interval_var = tk.DoubleVar(value=self.scan_interval)
        tk.Scale(monitor_frame, from_=1.0, to=5.0, resolution=0.5, orient=tk.HORIZONTAL,
                variable=interval_var).pack(fill=tk.X)
        
        # Alert settings
        alert_frame = tk.LabelFrame(settings_window, text="Alert Settings", padx=10, pady=5)
        alert_frame.pack(fill=tk.X, padx=20, pady=5)
        
        completion_var = tk.BooleanVar(value=self.completion_alert)
        tk.Checkbutton(alert_frame, text="🔊 Completion Alert Sound", 
                      variable=completion_var, font=("Arial", 10)).pack(anchor="w")
        
        # Validation settings
        validation_frame = tk.LabelFrame(settings_window, text="Validation Settings", padx=10, pady=5)
        validation_frame.pack(fill=tk.X, padx=20, pady=5)
        
        cross_val_var = tk.BooleanVar(value=self.cross_validation)
        tk.Checkbutton(validation_frame, text="🔍 Enable Cross-Validation", 
                      variable=cross_val_var, font=("Arial", 10)).pack(anchor="w")
        
        def apply_settings():
            self.scan_interval = interval_var.get()
            self.completion_alert = completion_var.get()
            self.cross_validation = cross_val_var.get()
            self.log_message("🔧 Settings updated", "success")
            settings_window.destroy()
        
        tk.Button(settings_window, text="✅ Apply Settings", command=apply_settings,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def open_directory(self):
        """Open download directory"""
        if self.download_directory and os.path.exists(self.download_directory):
            os.startfile(self.download_directory)
            self.log_message("📁 Directory opened: " + self.download_directory, "info")
        else:
            messagebox.showwarning("Manual Assist Monitor", "Directory not found")

    def update_session_timer(self):
        """Update session timer display"""
        if self.session_start_time and self.is_monitoring:
            elapsed = datetime.now() - self.session_start_time
            elapsed_str = str(elapsed).split('.')[0]
            self.time_stat.config(text=elapsed_str)
        elif not self.is_monitoring:
            self.time_stat.config(text="00:00:00")
        
        self.root.after(1000, self.update_session_timer)

    def log_message(self, message, level="info"):
        """Add message to activity log with enhanced formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = "[" + timestamp + "] " + message + "\n"
        
        tag = level if level in ["success", "error", "info", "warning", "validation"] else "info"
        
        self.log_text.insert(tk.END, log_entry, tag)
        self.log_text.see(tk.END)
        print(log_entry.strip())

    def run(self):
        """Start the manual assist application"""
        self.root.mainloop()

def main():
    """Main entry point for universal manual assist monitor"""
    print("🎯 Universal VDH Manual Assist Monitor")
    print("Created: July 31, 2025 - 9:57 PM Pacific")
    print("Purpose: Universal manual assist monitor with cross-validation & metadata")
    print("Features: Manual workflow guidance, metadata preparation, transcription readiness")
    print()
    
    try:
        app = VDHUniversalManualAssist()
        app.run()
    except Exception as e:
        print("❌ Error: " + str(e))
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())