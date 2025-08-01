# tce_chrome_extractor_fixed_20250727_0805.py
# Quick fix for Chrome driver issues - simplified configuration
# Created: July 27, 2025 - 08:05 Pacific

import subprocess
import os
import sys
import json
import time
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading

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

class TCEChromeExtractorFixed:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TCE Chrome Extractor - Fixed")
        self.root.geometry("900x600")
        
        # Fixed target directory
        self.output_dir = Path("C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.driver = None
        self.captured_urls = []
        self.automation_running = False
        
        self.platform_url = "https://experience.cherringtonmedia.com/launchpad-diytrax-training/"
        
        self.setup_gui()
        
    def setup_gui(self):
        """Simplified GUI setup"""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=40)
        title_frame.pack(fill=tk.X, padx=5, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🔧 TCE CHROME EXTRACTOR - QUICK FIX",
                              bg="#2c3e50", fg="white", font=("Arial", 12, "bold"))
        title_label.pack(expand=True)
        
        # Status
        self.status_label = tk.Label(self.root, text="Checking system...", 
                                    font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Progress
        progress_frame = tk.LabelFrame(self.root, text="Progress", font=("Arial", 9, "bold"))
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="Ready to extract", font=("Arial", 9))
        self.progress_label.pack()
        
        # URLs display
        urls_frame = tk.LabelFrame(self.root, text="Extracted URLs", font=("Arial", 9, "bold"))
        urls_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.urls_text = scrolledtext.ScrolledText(urls_frame, height=10, font=("Consolas", 8))
        self.urls_text.pack(fill=tk.BOTH, expand=True)
        
        # Log
        log_frame = tk.LabelFrame(self.root, text="Activity Log", font=("Arial", 9, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, font=("Consolas", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = tk.Button(button_frame, text="🚀 START EXTRACTION", 
                                     command=self.start_extraction,
                                     bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_button = tk.Button(button_frame, text="⏹️ STOP", 
                                    command=self.stop_extraction,
                                    bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                                    state='disabled')
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Check dependencies
        self.root.after(1000, self.check_dependencies)
        self.log_message("🔧 TCE Chrome Extractor - Quick Fix Version")
        
    def log_message(self, message):
        """Add timestamped message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def check_dependencies(self):
        """Check if Selenium is available"""
        if SELENIUM_AVAILABLE:
            self.status_label.config(text="✅ Ready - Selenium available", fg="#27ae60")
            self.start_button.config(state='normal')
            self.log_message("✅ Selenium WebDriver ready")
        else:
            self.status_label.config(text="❌ Selenium not available", fg="#e74c3c")
            self.start_button.config(state='disabled')
            self.log_message("❌ Selenium not available - install required")
            
    def setup_chrome_driver(self):
        """Setup Chrome with minimal options to avoid conflicts"""
        try:
            self.log_message("🌐 Setting up Chrome WebDriver...")
            
            # Minimal Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Enable network logging
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            
            # Set logging preferences
            chrome_options.set_capability('goog:loggingPrefs', {
                'performance': 'ALL',
                'browser': 'ALL'
            })
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(60)
            
            self.log_message("✅ Chrome WebDriver ready")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Chrome setup failed: {str(e)}")
            return False
            
    def extract_video_urls_from_logs(self):
        """Extract video URLs from Chrome performance logs"""
        video_urls = []
        
        try:
            logs = self.driver.get_log('performance')
            self.log_message(f"📊 Analyzing {len(logs)} log entries...")
            
            for log_entry in logs:
                try:
                    message = json.loads(log_entry['message'])
                    
                    if message.get('message', {}).get('method') == 'Network.responseReceived':
                        response = message.get('message', {}).get('params', {}).get('response', {})
                        url = response.get('url', '')
                        mime_type = response.get('mimeType', '')
                        
                        # Look for video patterns
                        if any(pattern in url.lower() for pattern in ['.mp4', '.m4v', '.webm', 'video/', 'vidalytics']):
                            if url not in video_urls and url.startswith('http') and len(url) > 30:
                                video_urls.append(url)
                                self.log_message(f"📹 Found: {url[:60]}...")
                                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.log_message(f"⚠️ Log extraction error: {str(e)}")
            
        return video_urls
        
    def extract_lesson_videos(self, lesson_num):
        """Extract videos from specific lesson with simplified approach"""
        try:
            self.log_message(f"🎯 Processing Lesson {lesson_num}...")
            self.progress_label.config(text=f"Processing Lesson {lesson_num}/9")
            
            # Find and click lesson
            lesson_xpath = f"//a[contains(text(), 'Lesson #{lesson_num}')]"
            
            try:
                # Wait for lesson link
                lesson_element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, lesson_xpath))
                )
                
                # Scroll to and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", lesson_element)
                time.sleep(2)
                lesson_element.click()
                self.log_message(f"✅ Clicked Lesson {lesson_num}")
                
                # Wait for video to load
                time.sleep(8)
                
                # Try to activate video player
                play_buttons = [
                    "//button[contains(@class, 'play')]",
                    "//div[contains(@class, 'play')]",
                    "//*[contains(@class, 'BigControls')]//button",
                    "//video"
                ]
                
                for selector in play_buttons:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        if element.is_displayed():
                            element.click()
                            self.log_message(f"▶️ Activated video player for Lesson {lesson_num}")
                            time.sleep(3)
                            break
                    except:
                        continue
                
                # Extract URLs
                video_urls = self.extract_video_urls_from_logs()
                
                if video_urls:
                    for url in video_urls:
                        if url not in [item['url'] for item in self.captured_urls]:
                            self.captured_urls.append({
                                'lesson': lesson_num,
                                'url': url
                            })
                            
                            # Display in GUI
                            self.urls_text.insert(tk.END, f"Lesson {lesson_num}: {url}\n")
                            self.urls_text.see(tk.END)
                            
                    self.log_message(f"✅ Lesson {lesson_num}: {len(video_urls)} new URLs extracted")
                    return True
                else:
                    self.log_message(f"⚠️ Lesson {lesson_num}: No video URLs found")
                    return False
                    
            except Exception as e:
                self.log_message(f"❌ Lesson {lesson_num} error: {str(e)}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Lesson {lesson_num} failed: {str(e)}")
            return False
            
    def start_extraction(self):
        """Start video extraction process"""
        if not SELENIUM_AVAILABLE:
            messagebox.showerror("Error", "Selenium not available")
            return
            
        self.log_message("🚀 Starting TCE Media extraction...")
        self.automation_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        def extraction_thread():
            try:
                # Setup Chrome
                if not self.setup_chrome_driver():
                    return
                    
                # Navigate to platform
                self.log_message("🌐 Loading Adam's platform...")
                self.progress_label.config(text="Loading platform...")
                self.driver.get(self.platform_url)
                time.sleep(5)
                
                # Process all 9 lessons
                self.progress_bar['maximum'] = 9
                successful_extractions = 0
                
                for lesson_num in range(1, 10):
                    if not self.automation_running:
                        break
                        
                    if self.extract_lesson_videos(lesson_num):
                        successful_extractions += 1
                        
                    # Update progress
                    self.root.after(0, lambda: setattr(self.progress_bar, 'value', lesson_num))
                    
                    # Wait between lessons
                    if lesson_num < 9 and self.automation_running:
                        time.sleep(3)
                
                # Final results
                total_urls = len(self.captured_urls)
                self.log_message(f"🏁 Extraction complete!")
                self.log_message(f"📊 Processed: {successful_extractions}/9 lessons")
                self.log_message(f"📹 Total URLs: {total_urls}")
                
                if total_urls > 0:
                    self.root.after(0, lambda: self.progress_label.config(text=f"Complete! {total_urls} URLs extracted"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", 
                        f"Extraction complete!\n\n"
                        f"Successfully processed: {successful_extractions}/9 lessons\n"
                        f"Total video URLs extracted: {total_urls}\n\n"
                        f"URLs are ready for yt-dlp download!"))
                else:
                    self.root.after(0, lambda: messagebox.showwarning("No Results", 
                        "No video URLs were extracted.\n\n"
                        "Please ensure you're logged into Adam's platform."))
                        
            except Exception as e:
                self.log_message(f"❌ Extraction error: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Extraction failed: {str(e)}"))
                
            finally:
                self.automation_running = False
                if self.driver:
                    try:
                        self.driver.quit()
                        self.log_message("🔒 Chrome browser closed")
                    except:
                        pass
                        
                self.root.after(0, lambda: self.start_button.config(state='normal'))
                self.root.after(0, lambda: self.stop_button.config(state='disabled'))
                
        # Start extraction
        thread = threading.Thread(target=extraction_thread)
        thread.daemon = True
        thread.start()
        
    def stop_extraction(self):
        """Stop extraction process"""
        self.log_message("⏹️ Stopping extraction...")
        self.automation_running = False
        
        if self.driver:
            try:
                self.driver.quit()
                self.log_message("🔒 Chrome closed")
            except:
                pass
                
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_label.config(text="Extraction stopped")
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🔧 TCE Chrome Extractor - Quick Fix")
    print("Created: July 27, 2025 - 08:05 Pacific")
    
    try:
        app = TCEChromeExtractorFixed()
        app.run()
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())