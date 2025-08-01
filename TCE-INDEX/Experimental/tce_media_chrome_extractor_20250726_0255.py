# tce_media_chrome_extractor_20250726_0255.py
# TCE Media Chrome Extractor - Enhanced with Directory Selection & Log Management
# Created: July 26, 2025 - 02:55 Pacific
# Purpose: Extract videos with folder selection, log dump, and summary reports

import subprocess
import os
import sys
import json
import time
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import threading

# Try to import selenium with helpful error if missing
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class TCEMediaChromeExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TCE Media Chrome Extractor - Enhanced")
        self.root.geometry("1100x750")
        
        # TCE-MEDIA directories - all 15 training applications
        self.tce_directories = [
            "21-DAY-BLITZ", "CROPBOT", "DIRECT-EDGE", "DISCORD",
            "DIYTRAX", "FINDING-YOUR-EDGE", "FLEXY", "GIFTSER", 
            "LIVE-QA-CALLS", "METRICMOVER", "PIXELPRESS", 
            "QUICK-START-GUIDE", "SCRAPEBOT", "SOTU", "THE-SEVEN-PILLARS"
        ]
        
        # Base directory and selected output
        self.base_dir = Path("C:/INDEX-PROJECT/TCE-MEDIA")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.selected_output_dir = None
        
        # Create all TCE-MEDIA subdirectories
        for directory in self.tce_directories:
            (self.base_dir / directory).mkdir(exist_ok=True)
        
        # Chrome driver and captured URLs
        self.driver = None
        self.captured_urls = []
        self.automation_running = False
        self.last_activity_time = time.time()
        self.current_lesson = 0
        
        # Extraction statistics for summary
        self.extraction_stats = {
            'start_time': None,
            'end_time': None,
            'total_lessons': 0,
            'successful_lessons': 0,
            'failed_lessons': 0,
            'total_urls': 0,
            'errors': []
        }
        
        # Enhanced logging system
        self.detailed_log = []
        self.summary_messages = []
        
        # Adam's platform configuration
        self.platform_url = "https://experience.cherringtonmedia.com/launchpad-diytrax-training/"
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create the enhanced GUI interface with directory selection"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=45)
        title_frame.pack(fill=tk.X, padx=5, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🎯 TCE MEDIA CHROME EXTRACTOR - ENHANCED v2",
                              bg="#2c3e50", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(expand=True)
        
        # Enhanced status section with heartbeat
        status_frame = tk.LabelFrame(self.root, text="📊 System Status", 
                                    font=("Arial", 9, "bold"), padx=5, pady=3)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = tk.Label(status_frame, text="Checking dependencies...", 
                                    font=("Arial", 9))
        self.status_label.pack(anchor=tk.W)
        
        # Status indicators with heartbeat
        status_indicators = tk.Frame(status_frame)
        status_indicators.pack(fill=tk.X)
        
        self.selenium_status = tk.Label(status_indicators, text="", font=("Arial", 8), fg="#666")
        self.selenium_status.pack(side=tk.LEFT, padx=(0, 20))
        
        self.ytdlp_status = tk.Label(status_indicators, text="", font=("Arial", 8), fg="#666")
        self.ytdlp_status.pack(side=tk.LEFT, padx=(0, 20))
        
        # Live heartbeat indicator
        self.heartbeat_label = tk.Label(status_indicators, text="💚 Ready", font=("Arial", 9, "bold"), fg="#27ae60")
        self.heartbeat_label.pack(side=tk.RIGHT)
        
        # NEW: Directory Selection Section
        dir_frame = tk.LabelFrame(self.root, text="📁 TCE-MEDIA Directory Selection", 
                                 font=("Arial", 9, "bold"), padx=5, pady=3)
        dir_frame.pack(fill=tk.X, padx=5, pady=2)
        
        dir_selection_frame = tk.Frame(dir_frame)
        dir_selection_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(dir_selection_frame, text="Target Folder:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.directory_var = tk.StringVar(value="DIYTRAX")
        self.directory_combo = ttk.Combobox(dir_selection_frame, textvariable=self.directory_var,
                                           values=self.tce_directories, state="readonly",
                                           font=("Arial", 9), width=20)
        self.directory_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.directory_combo.bind('<<ComboboxSelected>>', self.on_directory_change)
        
        # Current path display
        self.path_label = tk.Label(dir_selection_frame, text="", font=("Arial", 8), fg="#666")
        self.path_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Update path display
        self.on_directory_change()
        
        # Configuration section
        config_frame = tk.LabelFrame(self.root, text="⚙️ Extraction Config", 
                                    font=("Arial", 9, "bold"), padx=5, pady=3)
        config_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Platform URL
        platform_frame = tk.Frame(config_frame)
        platform_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(platform_frame, text="Target URL:", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        self.platform_entry = tk.Entry(platform_frame, font=("Arial", 8))
        self.platform_entry.insert(0, self.platform_url)
        self.platform_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Timing controls - optimized for speed
        timing_frame = tk.Frame(config_frame)
        timing_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(timing_frame, text="Video Load Wait:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.wait_time_var = tk.StringVar(value="6")  # Faster - reduced to 6s
        wait_time_spin = tk.Spinbox(timing_frame, from_=4, to=15, textvariable=self.wait_time_var, 
                                   width=4, font=("Arial", 8))
        wait_time_spin.pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(timing_frame, text="Between Lessons:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.between_wait_var = tk.StringVar(value="2")  # Faster - reduced to 2s
        between_wait_spin = tk.Spinbox(timing_frame, from_=1, to=5, textvariable=self.between_wait_var, 
                                      width=4, font=("Arial", 8))
        between_wait_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Real-time progress section
        progress_frame = tk.LabelFrame(self.root, text="📈 Extraction Progress", 
                                      font=("Arial", 9, "bold"), padx=5, pady=3)
        progress_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        self.progress_label = tk.Label(progress_frame, text="Ready to extract videos", 
                                      font=("Arial", 9, "bold"))
        self.progress_label.pack()
        
        # Real-time activity indicator
        self.activity_label = tk.Label(progress_frame, text="", 
                                      font=("Arial", 8), fg="#666")
        self.activity_label.pack()
        
        # Timing display
        self.timing_label = tk.Label(progress_frame, text="", 
                                    font=("Arial", 8), fg="#3498db")
        self.timing_label.pack()
        
        # NEW: Summary Report Section
        summary_frame = tk.LabelFrame(self.root, text="📊 Extraction Summary", 
                                     font=("Arial", 9, "bold"), padx=5, pady=3)
        summary_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Summary display
        summary_display_frame = tk.Frame(summary_frame)
        summary_display_frame.pack(fill=tk.X, pady=2)
        
        self.summary_text = tk.Text(summary_display_frame, height=3, font=("Arial", 9),
                                   bg="#f8f9fa", state='disabled')
        self.summary_text.pack(fill=tk.X)
        
        # Captured URLs section
        urls_frame = tk.LabelFrame(self.root, text="🎯 Extracted Video URLs", 
                                  font=("Arial", 9, "bold"), padx=5, pady=3)
        urls_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Treeview for captured URLs
        columns = ("Lesson", "Video_URL", "Status")
        self.urls_tree = ttk.Treeview(urls_frame, columns=columns, show="headings", height=4)
        
        # Configure columns
        self.urls_tree.heading("Lesson", text="Lesson")
        self.urls_tree.heading("Video_URL", text="Extracted Video URL")
        self.urls_tree.heading("Status", text="Status")
        
        self.urls_tree.column("Lesson", width=80)
        self.urls_tree.column("Video_URL", width=420)
        self.urls_tree.column("Status", width=80)
        
        # Scrollbar for URLs
        urls_scrollbar = ttk.Scrollbar(urls_frame, orient=tk.VERTICAL, command=self.urls_tree.yview)
        self.urls_tree.configure(yscrollcommand=urls_scrollbar.set)
        
        self.urls_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        urls_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced activity log
        log_frame = tk.LabelFrame(self.root, text="📝 Extraction Log", 
                                 font=("Arial", 9, "bold"), padx=5, pady=3)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=4, 
                                                 font=("Consolas", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Enhanced control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Top row buttons
        top_buttons = tk.Frame(button_frame)
        top_buttons.pack(fill=tk.X, pady=(0, 2))
        
        self.start_button = tk.Button(top_buttons, text="🚀 START EXTRACTION", 
                                     command=self.start_extraction,
                                     bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                     height=1)
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        self.stop_button = tk.Button(top_buttons, text="⏹️ STOP", 
                                    command=self.stop_extraction,
                                    bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                                    height=1, state='disabled')
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        # Bottom row buttons
        bottom_buttons = tk.Frame(button_frame)
        bottom_buttons.pack(fill=tk.X)
        
        # NEW: Log Management Buttons
        self.dump_log_button = tk.Button(bottom_buttons, text="📋 DUMP LOG", 
                                        command=self.dump_log_for_claude,
                                        bg="#3498db", fg="white", font=("Arial", 9, "bold"))
        self.dump_log_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        self.clear_all_button = tk.Button(bottom_buttons, text="🗑️ CLEAR ALL", 
                                         command=self.clear_all_data,
                                         bg="#f39c12", fg="white", font=("Arial", 9, "bold"))
        self.clear_all_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        self.install_button = tk.Button(bottom_buttons, text="🔧 INSTALL", 
                                       command=self.install_selenium,
                                       bg="#9b59b6", fg="white", font=("Arial", 9, "bold"))
        self.install_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        # Initialize monitoring
        self.start_time = None
        self.root.after(1000, self.check_dependencies)
        self.root.after(2000, self.heartbeat_monitor)
        
        # Initial log
        self.log_message("🎯 TCE Media Chrome Extractor Enhanced v2 Ready")
        self.log_message(f"📁 Base: {self.base_dir}")
        self.log_message("🚀 New: Directory selection + Log management + Summary reports")
        self.update_summary("Ready for extraction. Select target directory and click START.")
        
    def on_directory_change(self, event=None):
        """Handle directory selection change"""
        selected_dir = self.directory_var.get()
        self.selected_output_dir = self.base_dir / selected_dir
        self.path_label.config(text=f"→ {self.selected_output_dir}")
        self.log_message(f"📁 Target directory: {selected_dir}")
        
    def update_summary(self, message):
        """Update the summary display with user-friendly information"""
        self.summary_messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
        # Keep only last 5 messages
        if len(self.summary_messages) > 5:
            self.summary_messages = self.summary_messages[-5:]
            
        # Update display
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, "\n".join(self.summary_messages))
        self.summary_text.config(state='disabled')
        
    def generate_final_summary(self):
        """Generate final extraction summary in plain English"""
        stats = self.extraction_stats
        
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            mins, secs = divmod(int(duration), 60)
            
            summary = f"""
EXTRACTION COMPLETE - {self.directory_var.get()}

✅ Successfully extracted: {stats['successful_lessons']} lessons
❌ Failed extractions: {stats['failed_lessons']} lessons  
📹 Total video URLs captured: {stats['total_urls']}
⏱️ Total time: {mins:02d}:{secs:02d}
📁 Saved to: {self.selected_output_dir}

QUALITY ASSESSMENT:
• Success rate: {(stats['successful_lessons']/max(1,stats['total_lessons']))*100:.1f}%
• Average URLs per lesson: {stats['total_urls']/max(1,stats['successful_lessons']):.1f}
• Ready for yt-dlp download: {'YES' if stats['total_urls'] > 0 else 'NO'}

STATUS: {'EXCELLENT' if stats['successful_lessons'] >= 7 else 'NEEDS REVIEW' if stats['successful_lessons'] >= 4 else 'FAILED'}
"""
        else:
            summary = "No extraction data available."
            
        return summary.strip()
        
    def dump_log_for_claude(self):
        """Create comprehensive log dump for sharing with Claude"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"extraction_log_{self.directory_var.get()}_{timestamp}.txt"
            
            # Comprehensive log content
            log_content = f"""
# TCE MEDIA EXTRACTION LOG
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Pacific
# Target Directory: {self.directory_var.get()}
# Extractor Version: tce_media_chrome_extractor_20250726_0255.py

## EXTRACTION SUMMARY
{self.generate_final_summary()}

## DETAILED STATISTICS
{json.dumps(self.extraction_stats, indent=2, default=str)}

## CAPTURED URLS ({len(self.captured_urls)} total)
"""
            
            for i, url_data in enumerate(self.captured_urls, 1):
                log_content += f"\n{i:2d}. Lesson {url_data['lesson']}: {url_data['url']}"
                
            log_content += f"""

## DETAILED LOG ENTRIES ({len(self.detailed_log)} entries)
"""
            
            for entry in self.detailed_log:
                log_content += f"\n{entry}"
                
            log_content += f"""

## SYSTEM INFORMATION
- Python: {sys.version}
- Selenium Available: {SELENIUM_AVAILABLE}
- Platform URL: {self.platform_entry.get()}
- Video Load Wait: {self.wait_time_var.get()}s
- Between Lessons Wait: {self.between_wait_var.get()}s

## END OF LOG
"""
            
            # Save to file
            log_path = Path(self.selected_output_dir) / log_filename
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
                
            # Also copy to clipboard if possible
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(log_content)
                clipboard_msg = " (copied to clipboard)"
            except:
                clipboard_msg = ""
                
            self.log_message(f"📋 Log dumped: {log_filename}{clipboard_msg}")
            self.update_summary(f"Log dump created: {log_filename}")
            
            messagebox.showinfo("Log Dump Complete", 
                f"Comprehensive log saved to:\n{log_path}\n\n"
                f"File ready for sharing with Claude!{clipboard_msg}")
                
        except Exception as e:
            self.log_message(f"❌ Log dump failed: {str(e)}")
            messagebox.showerror("Log Dump Error", f"Failed to create log dump:\n{str(e)}")
            
    def clear_all_data(self):
        """Clear all data for fresh extraction run"""
        if messagebox.askyesno("Clear All Data", 
                              "Clear all extraction data for fresh run?\n\n"
                              "This will reset:\n"
                              "• Captured URLs\n"
                              "• Extraction logs\n" 
                              "• Summary statistics\n"
                              "• Progress indicators"):
            
            # Reset all data
            self.captured_urls = []
            self.detailed_log = []
            self.summary_messages = []
            
            # Reset statistics
            self.extraction_stats = {
                'start_time': None,
                'end_time': None,
                'total_lessons': 0,
                'successful_lessons': 0,
                'failed_lessons': 0,
                'total_urls': 0,
                'errors': []
            }
            
            # Clear UI elements
            self.urls_tree.delete(*self.urls_tree.get_children())
            self.log_text.delete(1.0, tk.END)
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready for fresh extraction")
            self.activity_label.config(text="")
            self.timing_label.config(text="")
            
            # Reset summary
            self.update_summary("All data cleared. Ready for fresh extraction run.")
            
            self.log_message("🗑️ All data cleared - ready for fresh extraction")
            
    def log_message(self, message):
        """Add message to log with timestamp and update activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Add to detailed log for dumping
        self.detailed_log.append(log_entry)
        
        # Display in GUI
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Update activity tracking
        self.last_activity_time = time.time()
        
    def heartbeat_monitor(self):
        """Monitor extraction heartbeat and provide real-time feedback"""
        current_time = time.time()
        time_since_activity = current_time - self.last_activity_time
        
        if self.automation_running:
            # Calculate elapsed time
            if self.start_time:
                elapsed = int(current_time - self.start_time)
                mins, secs = divmod(elapsed, 60)
                self.timing_label.config(text=f"⏱️ Elapsed: {mins:02d}:{secs:02d}")
            
            # Heartbeat status
            if time_since_activity > 45:  # 45 second timeout
                self.heartbeat_label.config(text="💔 TIMEOUT", fg="#e74c3c")
                self.log_message("💔 TIMEOUT - Extraction appears hung")
                self.log_message("⚠️ Recommend stopping and restarting")
                self.update_summary("TIMEOUT detected - extraction may be hung")
            elif time_since_activity > 25:  # 25 second warning
                self.heartbeat_label.config(text="⚠️ Working...", fg="#f39c12")
                self.log_message("⚠️ Still extracting... (25s activity gap)")
            elif time_since_activity > 15:  # 15 second info
                self.heartbeat_label.config(text="🔄 Processing", fg="#3498db")
                if self.current_lesson > 0:
                    self.log_message(f"🔄 Processing Lesson {self.current_lesson}/9...")
            else:
                self.heartbeat_label.config(text="💚 Active", fg="#27ae60")
        else:
            self.heartbeat_label.config(text="💤 Ready", fg="#95a5a6")
            self.timing_label.config(text="")
            
        # Schedule next heartbeat
        self.root.after(5000, self.heartbeat_monitor)  # Every 5 seconds
        
    def update_progress_details(self, lesson_num, action):
        """Update detailed progress information"""
        self.current_lesson = lesson_num
        self.activity_label.config(text=f"Lesson {lesson_num}/9: {action}")
        self.progress_label.config(text=f"Extracting Lesson {lesson_num}/9 - {action}")
        self.root.update_idletasks()
        
    def check_dependencies(self):
        """Check system dependencies"""
        self.log_message("🔍 Checking extraction dependencies...")
        
        # Check Selenium
        if SELENIUM_AVAILABLE:
            self.selenium_status.config(text="✅ Selenium Ready", fg="#27ae60")
            self.log_message("✅ Selenium WebDriver available")
        else:
            self.selenium_status.config(text="❌ Selenium Missing", fg="#e74c3c")
            self.log_message("❌ Selenium not available")
            
        # Check yt-dlp
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.ytdlp_status.config(text=f"✅ yt-dlp {version}", fg="#27ae60")
                self.log_message(f"✅ yt-dlp ready: {version}")
            else:
                self.ytdlp_status.config(text="❌ yt-dlp Error", fg="#e74c3c")
        except FileNotFoundError:
            self.ytdlp_status.config(text="❌ yt-dlp Missing", fg="#e74c3c")
        except Exception as e:
            self.ytdlp_status.config(text="❌ yt-dlp Error", fg="#e74c3c")
            
        # Update ready status
        if SELENIUM_AVAILABLE:
            self.status_label.config(text="✅ Ready for TCE Media extraction")
            self.start_button.config(state='normal')
            self.update_summary("System ready. Select directory and start extraction.")
        else:
            self.status_label.config(text="❌ Install Selenium first")
            self.start_button.config(state='disabled')
            self.update_summary("Install Selenium to enable extraction.")
            
    def install_selenium(self):
        """Install Selenium via pip"""
        self.log_message("🔧 Installing Selenium + WebDriver Manager...")
        self.install_button.config(state='disabled')
        self.update_summary("Installing Selenium dependencies...")
        
        def install_thread():
            try:
                # Install selenium
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium'], 
                                      capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    self.log_message("✅ Selenium installed successfully")
                    
                    # Install webdriver-manager
                    result2 = subprocess.run([sys.executable, '-m', 'pip', 'install', 'webdriver-manager'], 
                                           capture_output=True, text=True, timeout=60)
                    
                    if result2.returncode == 0:
                        self.log_message("✅ WebDriver Manager installed")
                    
                    self.log_message("🔄 Restart application to enable extraction")
                    self.root.after(0, lambda: self.update_summary("Selenium installed! Restart application."))
                    messagebox.showinfo("Success", "Selenium installed!\n\nRestart application.")
                    
                else:
                    self.log_message("❌ Selenium installation failed")
                    self.root.after(0, lambda: self.update_summary("Selenium installation failed."))
                    
            except Exception as e:
                self.log_message(f"❌ Installation error: {str(e)}")
                self.root.after(0, lambda: self.update_summary(f"Installation error: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.install_button.config(state='normal'))
                
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
    def setup_chrome_driver(self):
        """Setup Chrome driver for extraction"""
        try:
            self.log_message("🌐 Initializing Chrome for extraction...")
            self.update_progress_details(0, "Setting up Chrome WebDriver")
            self.update_summary("Starting Chrome WebDriver setup...")
            
            # Chrome options optimized for extraction
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Network logging for video URL capture
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            chrome_options.set_capability('goog:loggingPrefs', {
                'performance': 'ALL',
                'browser': 'ALL'
            })
            
            # Create driver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.log_message("✅ Chrome WebDriver ready (WebDriver Manager)")
            except ImportError:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.log_message("✅ Chrome WebDriver ready (System Driver)")
                
            # Configure timeouts
            self.driver.implicitly_wait(8)
            self.driver.set_page_load_timeout(30)
            
            self.update_summary("Chrome WebDriver initialized successfully.")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Chrome setup failed: {str(e)}")
            self.update_progress_details(0, f"Chrome setup failed: {str(e)}")
            self.update_summary(f"Chrome setup failed: {str(e)}")
            messagebox.showerror("Chrome Error", 
                f"Chrome setup failed:\n{str(e)}\n\nEnsure Chrome browser is installed.")
            return False
            
    def extract_video_urls_from_logs(self):
        """Extract video URLs from Chrome performance logs"""
        video_urls = []
        
        try:
            logs = self.driver.get_log('performance')
            
            for log_entry in logs:
                message = json.loads(log_entry['message'])
                
                if (message.get('message', {}).get('method') == 'Network.responseReceived'):
                    response = message.get('message', {}).get('params', {}).get('response', {})
                    url = response.get('url', '')
                    mime_type = response.get('mimeType', '')
                    
                    # Look for video patterns
                    video_patterns = ['.mp4', '.m4v', '.webm', 'video/', 'stream', 'vidalytics']
                    mime_patterns = ['video', 'mp4', 'webm']
                    
                    if any(pattern in url.lower() for pattern in video_patterns) or \
                       any(pattern in mime_type.lower() for pattern in mime_patterns):
                        if url not in video_urls and url.startswith('http'):
                            video_urls.append(url)
                            self.log_message(f"📹 Captured: {url[:50]}...")
                            
        except Exception as e:
            self.log_message(f"⚠️ Log extraction error: {str(e)}")
            self.extraction_stats['errors'].append(f"Log extraction: {str(e)}")
            
        return video_urls
        
    def extract_lesson_videos(self, lesson_num):
        """Extract videos from a specific lesson"""
        try:
            self.log_message(f"🎯 Starting Lesson {lesson_num} extraction...")
            self.update_progress_details(lesson_num, "Locating lesson link")
            
            # Wait for page readiness
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find lesson link
            lesson_selector = f"//a[contains(text(), 'Lesson #{lesson_num}') or contains(@aria-label, 'Lesson #{lesson_num}')]"
            
            try:
                lesson_element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, lesson_selector))
                )
                
                # Scroll and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", lesson_element)
                time.sleep(1)
                
                self.update_progress_details(lesson_num, "Clicking lesson")
                lesson_element.click()
                self.log_message(f"✅ Clicked Lesson {lesson_num}")
                
                # Wait for video to load
                wait_time = int(self.wait_time_var.get())
                self.update_progress_details(lesson_num, f"Loading video ({wait_time}s)")
                
                for i in range(wait_time):
                    time.sleep(1)
                    remaining = wait_time - i - 1
                    if remaining > 0:
                        self.update_progress_details(lesson_num, f"Loading video ({remaining}s)")
                
                # Try to activate video player
                self.update_progress_details(lesson_num, "Activating video player")
                
                play_selectors = [
                    "//button[contains(@class, 'play') or contains(@aria-label, 'play')]",
                    "//div[contains(@class, 'play')]",
                    "//*[contains(@class, 'BigControls')]//button",
                    "//*[contains(@class, 'PlayToggle')]",
                    "//video",
                    "//*[contains(@class, 'video')]"
                ]
                
                for selector in play_selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            element.click()
                            self.log_message("▶️ Activated video player")
                            time.sleep(2)
                            break
                    except:
                        continue
                
                # Extract video URLs
                self.update_progress_details(lesson_num, "Extracting video URLs")
                video_urls = self.extract_video_urls_from_logs()
                
                if video_urls:
                    for url in video_urls:
                        self.captured_urls.append({
                            'lesson': lesson_num,
                            'url': url,
                            'status': 'Extracted'
                        })
                        
                        # Add to display
                        self.urls_tree.insert("", "end", values=(
                            f"Lesson {lesson_num}", 
                            url[:50] + "..." if len(url) > 50 else url, 
                            "✅ Ready"
                        ))
                        
                    self.log_message(f"✅ Lesson {lesson_num}: {len(video_urls)} URLs extracted")
                    self.update_progress_details(lesson_num, f"✅ {len(video_urls)} URLs extracted")
                    
                    # Update statistics
                    self.extraction_stats['successful_lessons'] += 1
                    self.extraction_stats['total_urls'] += len(video_urls)
                    
                    return True
                else:
                    self.log_message(f"⚠️ Lesson {lesson_num}: No video URLs found")
                    self.update_progress_details(lesson_num, "⚠️ No URLs found")
                    self.extraction_stats['failed_lessons'] += 1
                    self.extraction_stats['errors'].append(f"Lesson {lesson_num}: No URLs found")
                    return False
                    
            except Exception as e:
                self.log_message(f"❌ Lesson {lesson_num}: {str(e)}")
                self.update_progress_details(lesson_num, f"❌ Error: {str(e)}")
                self.extraction_stats['failed_lessons'] += 1
                self.extraction_stats['errors'].append(f"Lesson {lesson_num}: {str(e)}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Lesson {lesson_num}: {str(e)}")
            self.update_progress_details(lesson_num, f"❌ Failed: {str(e)}")
            self.extraction_stats['failed_lessons'] += 1
            self.extraction_stats['errors'].append(f"Lesson {lesson_num}: {str(e)}")
            return False
            
    def start_extraction(self):
        """Start the TCE Media extraction process"""
        if not SELENIUM_AVAILABLE:
            messagebox.showerror("Error", "Selenium not available")
            return
            
        if not self.selected_output_dir:
            self.on_directory_change()  # Ensure directory is set
            
        self.log_message(f"🚀 Starting TCE Media extraction to {self.directory_var.get()}...")
        self.update_summary(f"Starting extraction to {self.directory_var.get()} folder...")
        
        # Initialize extraction statistics
        self.extraction_stats = {
            'start_time': time.time(),
            'end_time': None,
            'total_lessons': 9,
            'successful_lessons': 0,
            'failed_lessons': 0,
            'total_urls': 0,
            'errors': []
        }
        
        self.automation_running = True
        self.start_time = time.time()
        
        # Update UI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        def extraction_thread():
            try:
                # Setup Chrome
                if not self.setup_chrome_driver():
                    return
                    
                # Navigate to platform
                platform_url = self.platform_entry.get().strip()
                self.log_message(f"🌐 Navigating to Adam's platform...")
                self.update_progress_details(0, "Loading platform")
                self.update_summary("Loading Adam's training platform...")
                self.driver.get(platform_url)
                time.sleep(5)
                
                # Extract from all 9 lessons
                self.progress_bar['maximum'] = 9
                self.progress_bar['value'] = 0
                
                for lesson_num in range(1, 10):
                    if not self.automation_running:  # Check for stop
                        break
                        
                    self.extract_lesson_videos(lesson_num)
                        
                    # Update progress
                    self.root.after(0, lambda: setattr(self.progress_bar, 'value', lesson_num))
                    
                    # Wait between lessons
                    if lesson_num < 9 and self.automation_running:
                        between_wait = int(self.between_wait_var.get())
                        self.update_progress_details(lesson_num, f"Waiting {between_wait}s before next lesson")
                        time.sleep(between_wait)
                
                # Final results
                if self.automation_running:
                    self.extraction_stats['end_time'] = time.time()
                    
                    self.log_message("🏁 TCE Media extraction completed")
                    summary = self.generate_final_summary()
                    self.update_summary("Extraction completed! Check summary for details.")
                    
                    if self.captured_urls:
                        self.log_message("🚀 Ready for video downloads with yt-dlp!")
                        self.root.after(0, lambda: messagebox.showinfo("Extraction Complete", summary))
                    else:
                        self.root.after(0, lambda: messagebox.showwarning("No Extractions", 
                            "No video URLs were extracted.\n\n"
                            "Verify you're logged into Adam's platform."))
                        
            except Exception as e:
                self.log_message(f"❌ Extraction error: {str(e)}")
                self.extraction_stats['errors'].append(f"Main extraction: {str(e)}")
                self.update_summary(f"Extraction failed: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Extraction failed: {str(e)}"))
                
            finally:
                # Cleanup
                self.automation_running = False
                if self.driver:
                    try:
                        self.driver.quit()
                        self.log_message("🔒 Chrome browser closed")
                    except:
                        pass
                    
                # Reset UI
                self.root.after(0, lambda: self.start_button.config(state='normal'))
                self.root.after(0, lambda: self.stop_button.config(state='disabled'))
                self.root.after(0, lambda: self.progress_label.config(text="Extraction completed"))
                self.root.after(0, lambda: self.activity_label.config(text=""))
                
        # Start extraction in background
        thread = threading.Thread(target=extraction_thread)
        thread.daemon = True
        thread.start()
        
    def stop_extraction(self):
        """Stop the extraction process"""
        self.log_message("⏹️ Stopping TCE Media extraction...")
        self.update_summary("Extraction stopped by user.")
        self.automation_running = False
        
        if self.driver:
            try:
                self.driver.quit()
                self.log_message("🔒 Chrome browser closed")
            except:
                pass
                
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_label.config(text="Extraction stopped")
        self.activity_label.config(text="")
        
    def run(self):
        """Start the TCE Media extractor"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 TCE Media Chrome Extractor - Enhanced v2")
    print("Created: July 26, 2025 - 02:55 Pacific")
    print("Purpose: Extract videos with directory selection + log management")
    print()
    
    try:
        app = TCEMediaChromeExtractor()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Extraction cancelled by user")
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())