# VDH_ENHANCED_DETECTOR_20250731_1212.py
# Enhanced VDH Smart Status Detector - Progress Bars & Log Export
# Created: July 31, 2025 - 12:12 PM Pacific
# Purpose: Analyze VDH downloads with progress tracking and comprehensive metadata

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading
from pathlib import Path
from datetime import datetime
import json
import subprocess
from mutagen import File as MutagenFile
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3

class VDHEnhancedDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH Enhanced Status Detector")
        self.root.geometry("800x650")
        
        # Configuration
        self.download_directory = ""
        self.analysis_ready = False
        
        # File analysis
        self.video_files = []
        self.total_size_mb = 0
        self.analysis_complete = False
        self.current_file_index = 0
        
        # Progress tracking
        self.total_progress = 0
        self.current_file_progress = 0
        
        # Session tracking
        self.session_stats = {
            "scan_time": None,
            "total_files": 0,
            "total_size_mb": 0,
            "average_file_size": 0,
            "metadata_extracted": False
        }
        
        # Log content for export
        self.log_content = []
        
        self.setup_gui()

    def setup_gui(self):
        """Create enhanced detector interface with progress bars"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH ENHANCED STATUS DETECTOR",
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
        
        tk.Button(dir_frame, text="📁 SELECT DIRECTORY",
                 command=self.select_directory,
                 bg="#3498db", fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # Progress tracking panel
        progress_frame = tk.LabelFrame(self.root, text="📊 Analysis Progress", 
                                      font=("Arial", 10, "bold"), padx=10, pady=5)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Overall progress
        overall_frame = tk.Frame(progress_frame)
        overall_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(overall_frame, text="📊 Overall Progress:", 
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
        
        # Results text area with improved scrolling
        text_frame = tk.Frame(analysis_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=10, font=("Consolas", 8),
                                   bg="#f8f9fa", wrap="word")
        results_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
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
        
        self.report_btn = tk.Button(main_actions, text="📊 GENERATE REPORT",
                                   command=self.generate_analysis_report,
                                   bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                   state='disabled')
        self.report_btn.pack(side=tk.LEFT, padx=2)
        
        # Utility actions
        utility_actions = tk.Frame(action_frame)
        utility_actions.pack(side=tk.RIGHT)
        
        tk.Button(utility_actions, text="📁 OPEN FOLDER",
                 command=self.open_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(utility_actions, text="📋 EXPORT LOG",
                 command=self.export_log_content,
                 bg="#e67e22", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
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
                              if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.mp3'))]
                
                if video_files:
                    self.log_result("🔍 Found " + str(len(video_files)) + " media files - ready for scan...")
                    # Don't auto-scan, let user initiate
            except Exception:
                pass

    def update_progress(self, overall_percent, current_percent=0, current_file=""):
        """Update progress bars and percentages"""
        self.overall_progress['value'] = overall_percent
        self.overall_percent.config(text=str(int(overall_percent)) + "%")
        
        self.current_progress['value'] = current_percent
        self.current_percent.config(text=str(int(current_percent)) + "%")
        
        if current_file:
            self.status_label.config(text="🔍 Analyzing: " + current_file[:40] + "...", fg="#3498db")
        
        self.root.update_idletasks()

    def scan_vdh_status(self):
        """Scan current VDH download status with progress tracking"""
        if not self.download_directory or not os.path.exists(self.download_directory):
            messagebox.showerror("Error", "Please select a valid directory first!")
            return
        
        self.status_label.config(text="🔍 Starting VDH status scan...", fg="#3498db")
        self.results_text.delete(1.0, tk.END)
        self.log_content.clear()
        
        # Reset progress bars
        self.update_progress(0, 0)
        
        # Run scan in thread to prevent GUI freezing
        scan_thread = threading.Thread(target=self.perform_enhanced_scan, daemon=True)
        scan_thread.start()

    def extract_media_metadata(self, file_path):
        """Extract comprehensive metadata from media files"""
        try:
            metadata = {}
            
            # Basic file info
            stat = os.stat(file_path)
            metadata['size_mb'] = stat.st_size / (1024 * 1024)
            metadata['modified'] = datetime.fromtimestamp(stat.st_mtime)
            metadata['created'] = datetime.fromtimestamp(stat.st_ctime)
            
            # Try to extract audio/video metadata using mutagen
            try:
                audio_file = MutagenFile(file_path)
                if audio_file is not None:
                    if hasattr(audio_file, 'info'):
                        info = audio_file.info
                        metadata['duration'] = getattr(info, 'length', 0)
                        metadata['bitrate'] = getattr(info, 'bitrate', 0)
                        
                        # Format-specific metadata
                        if isinstance(audio_file, MP4):
                            metadata['codec'] = 'MP4'
                            metadata['video_codec'] = str(getattr(info, 'codec', 'Unknown'))
                        elif isinstance(audio_file, MP3):
                            metadata['codec'] = 'MP3'
                            metadata['version'] = str(getattr(info, 'version', 'Unknown'))
                        else:
                            metadata['codec'] = str(type(audio_file).__name__)
            except Exception:
                # If mutagen fails, try basic ffprobe approach
                try:
                    result = subprocess.run([
                        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                        '-show_format', '-show_streams', file_path
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        import json
                        probe_data = json.loads(result.stdout)
                        if 'format' in probe_data:
                            format_info = probe_data['format']
                            metadata['duration'] = float(format_info.get('duration', 0))
                            metadata['bitrate'] = int(format_info.get('bit_rate', 0))
                            metadata['format_name'] = format_info.get('format_name', 'Unknown')
                except Exception:
                    pass
            
            # Set defaults for missing values
            metadata.setdefault('duration', 0)
            metadata.setdefault('bitrate', 0)
            metadata.setdefault('codec', 'Unknown')
            
            return metadata
            
        except Exception as e:
            self.log_result("⚠️ Metadata extraction failed for " + os.path.basename(file_path) + ": " + str(e))
            return {
                'size_mb': 0,
                'modified': datetime.now(),
                'created': datetime.now(),
                'duration': 0,
                'bitrate': 0,
                'codec': 'Unknown'
            }

    def perform_enhanced_scan(self):
        """Perform the actual file scan with progress tracking and metadata"""
        try:
            self.session_stats["scan_time"] = datetime.now()
            
            # Find all media files
            media_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.m4a')
            all_files = [f for f in os.listdir(self.download_directory) 
                        if f.lower().endswith(media_extensions)]
            
            if not all_files:
                self.root.after(0, lambda: self.log_result("❌ No media files found in directory"))
                self.root.after(0, lambda: self.update_progress(100, 100))
                return
            
            video_files = []
            total_files = len(all_files)
            
            for i, filename in enumerate(all_files):
                file_path = os.path.join(self.download_directory, filename)
                
                # Update progress
                overall_progress = (i / total_files) * 100
                self.root.after(0, lambda p=overall_progress, f=filename: self.update_progress(p, 0, f))
                
                # Extract metadata with progress simulation
                for progress_step in [25, 50, 75, 100]:
                    self.root.after(0, lambda p=overall_progress, c=progress_step: self.update_progress(p, c))
                    time.sleep(0.1)  # Simulate processing time
                
                metadata = self.extract_media_metadata(file_path)
                
                file_info = {
                    'name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': os.path.getmtime(file_path),
                    'metadata': metadata
                }
                video_files.append(file_info)
                
                # Log progress
                self.root.after(0, lambda i=i+1, t=total_files: 
                    self.log_result("📹 Analyzed file " + str(i) + "/" + str(t) + ": " + filename))
            
            # Sort by modification time (newest first)
            video_files.sort(key=lambda x: x['modified'], reverse=True)
            
            self.video_files = video_files
            total_size = sum(f['size'] for f in video_files)
            self.total_size_mb = total_size / (1024 * 1024)
            
            # Update session stats
            self.session_stats["total_files"] = len(video_files)
            self.session_stats["total_size_mb"] = self.total_size_mb
            self.session_stats["average_file_size"] = (self.total_size_mb / len(video_files)) if video_files else 0
            self.session_stats["metadata_extracted"] = True
            
            # Complete progress
            self.root.after(0, lambda: self.update_progress(100, 100))
            
            # Update UI on main thread
            self.root.after(0, self.update_scan_results)
            
        except Exception as e:
            self.root.after(0, lambda: self.log_result("❌ Scan error: " + str(e)))
            self.root.after(0, lambda: self.update_progress(100, 100))

    def update_scan_results(self):
        """Update UI with enhanced scan results"""
        file_count = len(self.video_files)
        
        # Update summary labels
        self.files_label.config(text=str(file_count))
        self.size_label.config(text=str(round(self.total_size_mb, 1)) + " MB")
        avg_size = self.session_stats["average_file_size"]
        self.avg_label.config(text=str(round(avg_size, 1)) + " MB")
        
        # Generate detailed analysis with metadata
        analysis_text = "🎯 VDH ENHANCED DOWNLOAD ANALYSIS\n"
        analysis_text += "=" * 55 + "\n"
        analysis_text += "📅 Scan Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        analysis_text += "📁 Directory: " + self.download_directory + "\n\n"
        
        analysis_text += "📊 SUMMARY:\n"
        analysis_text += "📹 Total Media Files: " + str(file_count) + "\n"
        analysis_text += "💾 Total Size: " + str(round(self.total_size_mb, 1)) + " MB\n"
        analysis_text += "📊 Average File Size: " + str(round(avg_size, 1)) + " MB\n"
        
        # Calculate total duration if available
        total_duration = sum(f['metadata'].get('duration', 0) for f in self.video_files)
        if total_duration > 0:
            hours = int(total_duration // 3600)
            minutes = int((total_duration % 3600) // 60)
            analysis_text += "⏱️ Total Duration: " + str(hours) + "h " + str(minutes) + "m\n"
        
        analysis_text += "\n"
        
        # Determine VDH status
        if file_count >= 5:
            vdh_status = "✅ VDH DOWNLOADS DETECTED - READY FOR PROCESSING"
            self.status_label.config(text="✅ Files ready for transcription", fg="#27ae60")
            self.report_btn.config(state='normal')
            self.analysis_ready = True
        elif file_count > 0:
            vdh_status = "⏳ PARTIAL DOWNLOADS - MAY NEED MORE FILES"
            self.status_label.config(text="⏳ Partial downloads detected", fg="#f39c12")
            self.report_btn.config(state='normal')
        else:
            vdh_status = "❌ NO MEDIA FILES FOUND"
            self.status_label.config(text="❌ No media files found", fg="#e74c3c")
        
        analysis_text += "🎯 VDH STATUS: " + vdh_status + "\n\n"
        
        # Enhanced file details with metadata
        if self.video_files:
            analysis_text += "📋 DETAILED FILE ANALYSIS (newest first):\n"
            analysis_text += "-" * 55 + "\n"
            
            for i, file_info in enumerate(self.video_files, 1):
                metadata = file_info['metadata']
                size_mb = file_info['size'] / (1024 * 1024)
                mod_time = datetime.fromtimestamp(file_info['modified'])
                
                analysis_text += str(i) + ". " + file_info['name'] + "\n"
                analysis_text += "   📁 Size: " + str(round(size_mb, 1)) + " MB\n"
                analysis_text += "   📅 Modified: " + mod_time.strftime("%m/%d %H:%M:%S") + "\n"
                analysis_text += "   🎬 Codec: " + str(metadata.get('codec', 'Unknown')) + "\n"
                
                if metadata.get('duration', 0) > 0:
                    duration = metadata['duration']
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    analysis_text += "   ⏱️ Duration: " + str(minutes) + "m " + str(seconds) + "s\n"
                
                if metadata.get('bitrate', 0) > 0:
                    bitrate_kbps = metadata['bitrate'] // 1000
                    analysis_text += "   📡 Bitrate: " + str(bitrate_kbps) + " kbps\n"
                
                analysis_text += "\n"
        
        # Enhanced recommendations
        analysis_text += "💡 RECOMMENDATIONS:\n"
        if self.analysis_ready:
            analysis_text += "✅ Files are ready for transcription processing\n"
            analysis_text += "✅ Click 'GENERATE REPORT' to create detailed analysis file\n"
            analysis_text += "✅ Use 'EXPORT LOG' to save processing log\n"
            analysis_text += "✅ Total content: " + str(round(self.total_size_mb, 1)) + " MB ready for INDEX pipeline\n"
        else:
            analysis_text += "⚠️ Consider downloading more content if incomplete\n"
            analysis_text += "⚠️ Check VDH interface for remaining downloads\n"
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, analysis_text)
        
        # Store content for export
        self.log_content.append(analysis_text)
        
        self.analysis_complete = True
        self.log_result("🔍 Enhanced scan completed: " + str(file_count) + " files analyzed with metadata")

    def generate_analysis_report(self):
        """Generate comprehensive analysis report in same directory"""
        if not self.analysis_ready:
            messagebox.showwarning("Not Ready", "Please run a scan first")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = os.path.join(self.download_directory, "VDH_analysis_report_" + timestamp + ".txt")
            
            # Create comprehensive report
            report_content = self.results_text.get(1.0, tk.END)
            report_content += "\n" + "=" * 55 + "\n"
            report_content += "📊 PROCESSING LOG:\n"
            report_content += "-" * 55 + "\n"
            
            for log_entry in self.log_content:
                report_content += log_entry + "\n"
            
            # Add technical summary
            report_content += "\n📋 TECHNICAL SUMMARY:\n"
            report_content += "• Files analyzed with comprehensive metadata extraction\n"
            report_content += "• Ready for OpenAI Whisper transcription processing\n"
            report_content += "• Compatible with INDEX development pipeline\n"
            report_content += "• Report saved in same directory as media files\n"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            success_msg = ("📊 Analysis Report Generated!\n\n" +
                          "✅ Comprehensive report saved in media directory\n" +
                          "✅ File: " + os.path.basename(report_file) + "\n" +
                          "✅ " + str(len(self.video_files)) + " files analyzed with metadata\n" +
                          "✅ Total size: " + str(round(self.total_size_mb, 1)) + " MB\n\n" +
                          "Ready for transcription processing!")
            
            messagebox.showinfo("Report Generated", success_msg)
            self.log_result("📊 Analysis report generated: " + report_file)
            
        except Exception as e:
            messagebox.showerror("Report Error", "Failed to generate report: " + str(e))

    def export_log_content(self):
        """Export GUI log content to text file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_file = os.path.join(self.download_directory or ".", "VDH_processing_log_" + timestamp + ".txt")
            
            # Export current results display
            log_content = self.results_text.get(1.0, tk.END)
            
            # Add processing timestamp
            export_header = "🎯 VDH ENHANCED DETECTOR - LOG EXPORT\n"
            export_header += "=" * 50 + "\n"
            export_header += "📅 Export Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
            export_header += "📁 Directory: " + (self.download_directory or "Not selected") + "\n\n"
            
            full_content = export_header + log_content
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            success_msg = ("📋 Log Content Exported!\n\n" +
                          "✅ Processing log saved successfully\n" +
                          "✅ File: " + os.path.basename(log_file) + "\n" +
                          "✅ Location: " + (self.download_directory or "Current directory") + "\n\n" +
                          "Log content is now available for review!")
            
            messagebox.showinfo("Export Complete", success_msg)
            self.log_result("📋 Log exported: " + log_file)
            
        except Exception as e:
            messagebox.showerror("Export Error", "Failed to export log: " + str(e))

    def save_analysis_report(self):
        """Save analysis report to file (legacy function)"""
        if not self.analysis_complete:
            messagebox.showwarning("No Analysis", "Please run a scan first")
            return
        
        # Use the enhanced report generation
        self.generate_analysis_report()

    def open_directory(self):
        """Open download directory"""
        if self.download_directory and os.path.exists(self.download_directory):
            os.startfile(self.download_directory)
        else:
            messagebox.showwarning("Error", "Directory not found")

    def log_result(self, message):
        """Log a result message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = "[" + timestamp + "] " + message
        print(log_entry)
        
        # Store for export
        self.log_content.append(log_entry)

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 VDH Enhanced Status Detector")
    print("Created: July 31, 2025 - 12:12 PM Pacific") 
    print("Purpose: Enhanced VDH analysis with progress tracking and metadata")
    print()
    
    try:
        app = VDHEnhancedDetector()
        app.run()
    except Exception as e:
        print("❌ Error: " + str(e))
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())