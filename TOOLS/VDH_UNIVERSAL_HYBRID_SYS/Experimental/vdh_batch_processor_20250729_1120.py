# vdh_batch_processor_20250729_1120.py
# VDH Batch Processor for Post-Collection Organization
# Created: July 29, 2025 - 11:20 AM Pacific  
# Purpose: Process collected DIYTRAX videos for transcription pipeline

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib

class VDHBatchProcessor:
    def __init__(self):
        self.base_dir = Path("C:/INDEX-PROJECT/TCE-MEDIA/DIYTRAX")
        self.config_dir = self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
        self.transcripts_dir = self.base_dir / "transcripts"
        
        # Ensure directories exist
        for directory in [self.config_dir, self.logs_dir, self.transcripts_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Processing statistics
        self.stats = {
            "files_processed": 0,
            "files_organized": 0,
            "duplicates_found": 0,
            "transcription_ready": 0,
            "errors": []
        }
        
        # Load progress tracker if exists
        self.progress_file = self.config_dir / "collection_progress.json"
        self.progress_data = self.load_progress_data()

    def load_progress_data(self):
        """Load existing progress data"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load progress data: {e}")
        
        # Default structure
        return {
            "session_info": {"total_lessons": 9},
            "lessons_progress": {},
            "statistics": {"completed_lessons": 0, "total_files_collected": 0}
        }

    def scan_downloaded_files(self):
        """Scan and catalog all downloaded video files"""
        print("🔍 Scanning downloaded files...")
        
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']
        found_files = []
        
        # Scan main directory and subdirectories
        for ext in video_extensions:
            found_files.extend(self.base_dir.glob(f"**/*{ext}"))
        
        # Categorize files
        categorized_files = {
            "raw_downloads": [],
            "organized": [],
            "duplicates": [],
            "unknown": []
        }
        
        file_hashes = {}  # For duplicate detection
        
        for file_path in found_files:
            try:
                # Calculate file hash for duplicate detection
                file_hash = self.calculate_file_hash(file_path)
                
                if file_hash in file_hashes:
                    categorized_files["duplicates"].append({
                        "file": str(file_path),
                        "original": file_hashes[file_hash],
                        "size": file_path.stat().st_size
                    })
                    self.stats["duplicates_found"] += 1
                else:
                    file_hashes[file_hash] = str(file_path)
                    
                    # Categorize based on location
                    if "lessons" in str(file_path):
                        categorized_files["organized"].append(str(file_path))
                    elif "raw_downloads" in str(file_path):
                        categorized_files["raw_downloads"].append(str(file_path))
                    else:
                        categorized_files["unknown"].append(str(file_path))
                
                self.stats["files_processed"] += 1
                
            except Exception as e:
                self.stats["errors"].append(f"Error processing {file_path}: {str(e)}")
        
        print(f"✅ File scan complete: {self.stats['files_processed']} files processed")
        return categorized_files

    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None

    def organize_files_by_lesson(self, categorized_files):
        """Organize files into lesson-specific directories"""
        print("📁 Organizing files by lesson...")
        
        # Create lesson directories
        lessons_dir = self.base_dir / "lessons"
        lessons_dir.mkdir(exist_ok=True)
        
        lesson_patterns = [
            ("Lesson_01", ["lesson 1", "walkthrough", "example", "landing"]),
            ("Lesson_02", ["lesson 2", "tracking", "analytics"]),
            ("Lesson_03", ["lesson 3", "profitable", "products", "promote"]),
            ("Lesson_04", ["lesson 4", "converting", "landing", "pages"]),
            ("Lesson_05", ["lesson 5", "traffic", "generation", "strategies"]),
            ("Lesson_06", ["lesson 6", "scaling", "campaigns"]),
            ("Lesson_07", ["lesson 7", "advanced", "optimization"]),
            ("Lesson_08", ["lesson 8", "multiple", "campaigns", "managing"]),
            ("Lesson_09", ["lesson 9", "troubleshooting", "issues"])
        ]
        
        organized_count = 0
        
        # Process raw downloads and unknown files
        files_to_organize = categorized_files["raw_downloads"] + categorized_files["unknown"]
        
        for file_path_str in files_to_organize:
            file_path = Path(file_path_str)
            
            # Try to match file to lesson based on filename
            lesson_matched = False
            filename_lower = file_path.name.lower()
            
            for lesson_dir, keywords in lesson_patterns:
                if any(keyword in filename_lower for keyword in keywords):
                    # Create lesson directory
                    target_dir = lessons_dir / lesson_dir
                    target_dir.mkdir(exist_ok=True)
                    
                    # Move file to lesson directory
                    target_file = target_dir / file_path.name
                    
                    try:
                        if not target_file.exists():
                            shutil.move(str(file_path), str(target_file))
                            organized_count += 1
                            lesson_matched = True
                            print(f"✅ Moved {file_path.name} → {lesson_dir}")
                            break
                    except Exception as e:
                        self.stats["errors"].append(f"Error moving {file_path.name}: {str(e)}")
            
            # If no lesson match, move to general folder
            if not lesson_matched:
                general_dir = lessons_dir / "General"
                general_dir.mkdir(exist_ok=True)
                target_file = general_dir / file_path.name
                
                try:
                    if not target_file.exists():
                        shutil.move(str(file_path), str(target_file))
                        organized_count += 1
                        print(f"✅ Moved {file_path.name} → General")
                except Exception as e:
                    self.stats["errors"].append(f"Error moving to General: {str(e)}")
        
        self.stats["files_organized"] = organized_count
        print(f"✅ File organization complete: {organized_count} files organized")

    def prepare_transcription_batch(self):
        """Prepare organized files for batch transcription"""
        print("🚀 Preparing transcription batch...")
        
        lessons_dir = self.base_dir / "lessons"
        batch_files = []
        
        # Scan all lesson directories
        for lesson_dir in lessons_dir.glob("Lesson_*"):
            if lesson_dir.is_dir():
                video_files = []
                for ext in ['.mp4', '.avi', '.mkv', '.mov']:
                    video_files.extend(lesson_dir.glob(f"*{ext}"))
                
                if video_files:
                    batch_files.extend(video_files)
        
        # Create transcription input file
        if batch_files:
            input_file = self.base_dir / "transcription_input_batch.txt"
            
            with open(input_file, 'w') as f:
                for file_path in batch_files:
                    f.write(f"{file_path}\n")
            
            self.stats["transcription_ready"] = len(batch_files)
            
            print(f"✅ Transcription batch prepared: {len(batch_files)} files")
            print(f"📄 Input file: {input_file}")
            
            return input_file
        else:
            print("⚠️ No video files found for transcription")
            return None

    def generate_processing_report(self):
        """Generate comprehensive processing report"""
        report_time = datetime.now().strftime("%Y%m%d_%H%M")
        report_file = self.logs_dir / f"batch_processing_report_{report_time}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "processing_statistics": self.stats,
            "directory_structure": self.get_directory_structure(),
            "file_summary": self.get_file_summary(),
            "next_steps": [
                "Files organized by lesson",
                "Transcription batch file created",
                "Ready for batch transcription processing",
                "Use openai_transcription_engine_v16_INDEX_ready_20250720_0748.py"
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Processing report saved: {report_file}")
        return report_file

    def get_directory_structure(self):
        """Get current directory structure"""
        structure = {}
        for item in self.base_dir.rglob("*"):
            if item.is_dir():
                rel_path = item.relative_to(self.base_dir)
                file_count = len([f for f in item.glob("*") if f.is_file()])
                structure[str(rel_path)] = file_count
        return structure

    def get_file_summary(self):
        """Get file summary by type"""
        summary = {"video_files": 0, "audio_files": 0, "other_files": 0}
        
        video_exts = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']
        audio_exts = ['.mp3', '.wav', '.m4a', '.aac']
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in video_exts:
                    summary["video_files"] += 1
                elif ext in audio_exts:
                    summary["audio_files"] += 1
                else:
                    summary["other_files"] += 1
        
        return summary

    def launch_transcription_engine(self, input_file):
        """Launch the transcription engine with batch input"""
        engine_path = Path("C:/ENGINE-PROJECT/src/engines/working/openai_transcription_engine_v16_INDEX_ready_20250720_0748.py")
        
        if not engine_path.exists():
            messagebox.showwarning("Engine Not Found", 
                f"⚠️ Transcription engine not found at:\n{engine_path}\n\n"
                "Please verify ENGINE-PROJECT setup.")
            return False
        
        try:
            # Prepare command for batch transcription  
            cmd = [
                "python", 
                str(engine_path),
                "--batch-file", str(input_file),
                "--output-dir", str(self.transcripts_dir)
            ]
            
            print(f"🚀 Launching transcription engine...")
            print(f"📄 Input file: {input_file}")
            print(f"📁 Output directory: {self.transcripts_dir}")
            
            # Launch in new PowerShell window
            subprocess.Popen([
                "powershell.exe", 
                "-Command", 
                f"cd '{engine_path.parent}'; python '{engine_path.name}'"
            ])
            
            print("✅ Transcription engine launched successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch transcription engine: {str(e)}")
            return False

    def run_full_batch_processing(self):
        """Execute complete batch processing workflow"""
        print("🎯 VDH Batch Processor - Processing DIYTRAX Collection")
        print("=" * 60)
        
        try:
            # Step 1: Scan files
            categorized_files = self.scan_downloaded_files()
            
            # Step 2: Organize files
            self.organize_files_by_lesson(categorized_files)
            
            # Step 3: Handle duplicates
            if self.stats["duplicates_found"] > 0:
                print(f"⚠️ Found {self.stats['duplicates_found']} duplicate files")
                # Could add duplicate removal logic here
            
            # Step 4: Prepare transcription batch
            input_file = self.prepare_transcription_batch()
            
            # Step 5: Generate report
            report_file = self.generate_processing_report()
            
            print(f"\n📊 BATCH PROCESSING COMPLETE")
            print("=" * 60)
            print(f"✅ Files processed: {self.stats['files_processed']}")
            print(f"📁 Files organized: {self.stats['files_organized']}")
            print(f"🚀 Ready for transcription: {self.stats['transcription_ready']}")
            print(f"📊 Report saved: {report_file}")
            
            if input_file and self.stats['transcription_ready'] > 0:
                print(f"\n💡 NEXT STEPS:")
                print(f"1. Review organized files in: {self.base_dir}/lessons")
                print(f"2. Launch transcription engine for batch processing")
                print(f"3. Monitor transcription progress")
                print(f"4. Begin INDEX development with transcribed content")
                
                # Optionally launch transcription automatically
                launch_transcription = input("\n🚀 Launch transcription engine now? (y/n): ").lower().strip()
                if launch_transcription == 'y':
                    self.launch_transcription_engine(input_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Batch processing failed: {str(e)}")
            self.stats["errors"].append(f"Critical error: {str(e)}")
            return False

def main():
    """Main batch processing entry point"""
    try:
        processor = VDHBatchProcessor()
        success = processor.run_full_batch_processing()
        
        if success:
            print(f"\n🎉 DIYTRAX batch processing completed successfully!")
            return 0
        else:
            print(f"\n❌ Batch processing completed with errors")
            return 1
            
    except Exception as e:
        print(f"❌ Fatal error in batch processor: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())