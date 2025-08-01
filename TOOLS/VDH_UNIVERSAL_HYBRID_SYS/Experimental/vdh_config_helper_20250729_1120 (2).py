# vdh_config_helper_20250729_1120.py
# VDH Configuration Helper for DIYTRAX Collection
# Created: July 29, 2025 - 11:20 AM Pacific
# Purpose: Configure VDH settings for optimal DIYTRAX video capture

import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

class VDHConfigHelper:
    def __init__(self):
        self.config_dir = Path("C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.vdh_settings = {
            "platform_url": "https://experience.cherringtonmedia.com/launchpad-diytrax-training/",
            "download_directory": "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX",
            "video_quality": "best[height<=720]",
            "file_naming": "%(title)s_L%(playlist_index)02d.%(ext)s",
            "detection_wait": 5,  # seconds to wait for VDH detection
            "segment_detection": True,
            "auto_download": False,  # manual control preferred
            "batch_mode": True
        }
        
        self.lessons_config = [
            {"id": 1, "title": "Full_Walkthrough_With_Example_Landing_Pages", "expected_segments": 1},
            {"id": 2, "title": "Setting_Up_Your_Tracking_and_Analytics", "expected_segments": 1},
            {"id": 3, "title": "Finding_Profitable_Products_to_Promote", "expected_segments": 1},
            {"id": 4, "title": "Creating_High_Converting_Landing_Pages", "expected_segments": 1},
            {"id": 5, "title": "Traffic_Generation_Strategies", "expected_segments": 1},
            {"id": 6, "title": "Scaling_Your_Campaigns", "expected_segments": 1},
            {"id": 7, "title": "Advanced_Optimization_Techniques", "expected_segments": 1},
            {"id": 8, "title": "Managing_Multiple_Campaigns", "expected_segments": 1},
            {"id": 9, "title": "Troubleshooting_Common_Issues", "expected_segments": 1}
        ]

    def create_vdh_download_config(self):
        """Create VDH download configuration file"""
        try:
            config_file = self.config_dir / "vdh_download_config.json"
            
            full_config = {
                "platform_settings": self.vdh_settings,
                "lessons": self.lessons_config,
                "directory_structure": {
                    "base": "C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX",
                    "raw_downloads": "raw_downloads",
                    "organized": "lessons",
                    "transcripts": "transcripts",
                    "logs": "logs"
                },
                "quality_preferences": {
                    "video_format": "mp4",
                    "max_resolution": "720p",
                    "audio_quality": "best",
                    "prefer_combined": True
                },
                "manual_workflow": {
                    "step_1": "Open platform URL",
                    "step_2": "Navigate to specific lesson",
                    "step_3": "Play video to trigger VDH detection",
                    "step_4": "Wait for VDH icon to appear",
                    "step_5": "Click VDH and download all segments",
                    "step_6": "Verify files in download directory",
                    "step_7": "Mark lesson complete in tracking system"
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(full_config, f, indent=2)
            
            print(f"✅ VDH configuration created: {config_file}")
            return config_file
            
        except Exception as e:
            print(f"❌ Config creation failed: {str(e)}")
            return None

    def create_browser_bookmarks(self):
        """Create browser bookmarks for easy lesson navigation"""
        try:
            bookmarks_file = self.config_dir / "diytrax_lesson_bookmarks.html"
            
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>DIYTRAX Lesson Bookmarks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .lesson { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
        .lesson-title { font-weight: bold; color: #2c3e50; }
        .lesson-url { color: #3498db; }
    </style>
</head>
<body>
    <h1>🎯 DIYTRAX Training Lessons - VDH Collection</h1>
    <p><strong>Base URL:</strong> https://experience.cherringtonmedia.com/launchpad-diytrax-training/</p>
    
"""
            
            for lesson in self.lessons_config:
                html_content += f"""
    <div class="lesson">
        <div class="lesson-title">Lesson {lesson['id']}: {lesson['title'].replace('_', ' ')}</div>
        <div class="lesson-url">
            <a href="{self.vdh_settings['platform_url']}lesson-{lesson['id']}" target="_blank">
                Direct Link to Lesson {lesson['id']}
            </a>
        </div>
        <div>Expected segments: {lesson['expected_segments']}</div>
    </div>
"""
            
            html_content += """
</body>
</html>"""
            
            with open(bookmarks_file, 'w') as f:
                f.write(html_content)
            
            print(f"✅ Browser bookmarks created: {bookmarks_file}")
            return bookmarks_file
            
        except Exception as e:
            print(f"❌ Bookmark creation failed: {str(e)}")
            return None

    def validate_download_directory(self):
        """Validate and prepare download directory structure"""
        try:
            base_dir = Path(self.vdh_settings["download_directory"])
            
            # Create subdirectories
            subdirs = ["raw_downloads", "lessons", "transcripts", "logs", "config"]
            created_dirs = []
            
            for subdir in subdirs:
                dir_path = base_dir / subdir
                dir_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(dir_path))
            
            # Create lesson-specific directories
            for lesson in self.lessons_config:
                lesson_dir = base_dir / "lessons" / f"Lesson_{lesson['id']:02d}_{lesson['title']}"
                lesson_dir.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(lesson_dir))
            
            print(f"✅ Directory structure validated: {len(created_dirs)} directories ready")
            return created_dirs
            
        except Exception as e:
            print(f"❌ Directory validation failed: {str(e)}")
            return []

    def create_progress_tracker(self):
        """Create JSON file for tracking collection progress"""
        try:
            tracker_file = self.config_dir / "collection_progress.json"
            
            progress_data = {
                "session_info": {
                    "created": "2025-07-29T11:20:00",
                    "platform": "DIYTRAX",
                    "total_lessons": len(self.lessons_config),
                    "status": "initialized"
                },
                "lessons_progress": {},
                "statistics": {
                    "completed_lessons": 0,
                    "total_files_collected": 0,
                    "total_size_mb": 0,
                    "average_time_per_lesson": 0
                }
            }
            
            # Initialize lesson progress
            for lesson in self.lessons_config:
                progress_data["lessons_progress"][str(lesson["id"])] = {
                    "title": lesson["title"],
                    "status": "pending",
                    "files_collected": [],
                    "collection_time": None,
                    "notes": ""
                }
            
            with open(tracker_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            print(f"✅ Progress tracker created: {tracker_file}")
            return tracker_file
            
        except Exception as e:
            print(f"❌ Progress tracker creation failed: {str(e)}")
            return None

    def run_full_config_setup(self):
        """Execute complete configuration setup"""
        print("🎯 VDH Configuration Helper - Setting up DIYTRAX collection")
        print("=" * 60)
        
        results