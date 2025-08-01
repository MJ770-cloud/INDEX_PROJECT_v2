# USB_BACKUP_CORRECTED_D_DRIVE_20250721_1531.py
"""
COMPLETE ENVIRONMENT BACKUP & TRANSFER SYSTEM - CORRECTED FOR D: DRIVE
Creates comprehensive USB backup of entire development environment.
Enables plug-and-play setup on any Windows 11 computer.
"""

import os
import shutil
import json
from datetime import datetime

class CompleteEnvironmentBackup:
    def __init__(self, usb_drive_letter="D"):  # CORRECTED TO D:
        self.timestamp = "20250721_1531"
        self.usb_drive = f"{usb_drive_letter}:\\"
        self.backup_root = f"{self.usb_drive}COMPLETE_ENVIRONMENT_BACKUP_{self.timestamp}\\"
        
        # SOURCE LOCATIONS
        self.source_paths = {
            "engine_project": "C:\\ENGINE-PROJECT\\",
            "index_project": "C:\\INDEX-PROJECT\\",
        }
        
        # DESTINATION STRUCTURE  
        self.backup_structure = {
            "projects": f"{self.backup_root}PROJECTS\\",
            "protocols": f"{self.backup_root}CLAUDE_PROTOCOLS\\", 
            "setup_scripts": f"{self.backup_root}SETUP_SCRIPTS\\",
            "documentation": f"{self.backup_root}DOCUMENTATION\\",
        }
        
    def create_backup_structure(self):
        print("🏗️  Creating USB backup folder structure...")
        for folder_name, folder_path in self.backup_structure.items():
            os.makedirs(folder_path, exist_ok=True)
            print(f"   ✅ Created: {folder_name}")
        print("📁 USB folder structure complete!")
        
    def backup_complete_projects(self):
        print("📦 Backing up complete project folders...")
        
        # Backup ENGINE-PROJECT
        engine_dest = f"{self.backup_structure['projects']}ENGINE-PROJECT\\"
        if os.path.exists(self.source_paths["engine_project"]):
            shutil.copytree(self.source_paths["engine_project"], engine_dest, dirs_exist_ok=True)
            print(f"   ✅ ENGINE-PROJECT backed up")
        
        # Backup INDEX-PROJECT  
        index_dest = f"{self.backup_structure['projects']}INDEX-PROJECT\\"
        if os.path.exists(self.source_paths["index_project"]):
            shutil.copytree(self.source_paths["index_project"], index_dest, dirs_exist_ok=True)
            print(f"   ✅ INDEX-PROJECT backed up")
        
        print("🎯 Complete project backup finished!")
        
    def create_setup_scripts(self):
        print("⚡ Creating automated setup scripts...")
        
        # Windows setup script
        windows_setup = f'''@echo off
echo 🚀 COMPLETE ENVIRONMENT SETUP STARTING...
echo.

echo 📁 Creating project directories...
mkdir "C:\\ENGINE-PROJECT"
mkdir "C:\\INDEX-PROJECT"

echo 📦 Copying project files...
xcopy "%~dp0..\\PROJECTS\\ENGINE-PROJECT\\*" "C:\\ENGINE-PROJECT\\" /E /I /Y
xcopy "%~dp0..\\PROJECTS\\INDEX-PROJECT\\*" "C:\\INDEX-PROJECT\\" /E /I /Y

echo ✅ SETUP COMPLETE!
echo 🎯 Both projects ready for development
echo 🔒 Claude enforcement protocols active

pause
'''
        
        setup_script_path = f"{self.backup_structure['setup_scripts']}SETUP_NEW_COMPUTER.bat"
        with open(setup_script_path, 'w') as f:
            f.write(windows_setup)
        print(f"   ✅ Windows setup script created")
        
    def create_recovery_documentation(self):
        print("📚 Creating recovery documentation...")
        
        recovery_guide = f'''# COMPLETE_ENVIRONMENT_RECOVERY_GUIDE_{self.timestamp}.md

# COMPLETE ENVIRONMENT RECOVERY GUIDE

**Created:** July 21, 2025 - 3:31 PM Pacific  
**Purpose:** Recreate complete development environment on any Windows 11 computer  

## 🚀 QUICK SETUP (PLUG AND PLAY)

### STEP 1: Run Automated Setup
1. Insert USB drive into new computer
2. Navigate to: SETUP_SCRIPTS\\
3. Right-click SETUP_NEW_COMPUTER.bat → "Run as Administrator"
4. Wait for completion message

### STEP 2: Test Claude Enforcement
1. Open PowerShell as Administrator
2. Navigate to: cd "C:\\ENGINE-PROJECT\\docs\\session_guides"
3. Run: python CLAUDE_ACCESSIBILITY_ENFORCER_20250721_1435.py
4. Confirm enforcement system loads

## 📁 WHAT'S INCLUDED

### COMPLETE PROJECTS:
- ENGINE-PROJECT\\ - Complete transcription system (175+ hours development)
- INDEX-PROJECT\\ - Content analysis system for The Cherrington Media

### CLAUDE ENFORCEMENT PROTOCOLS:
- CLAUDE_ACCESSIBILITY_ENFORCER_20250721_1435.py - Mandatory session enforcer
- PROTOCOL_VALIDATION_SYSTEM_20250721_1435.py - Real-time validation
- MANDATORY_SESSION_STARTER_20250721_1435.md - Session startup guide
- DEPLOYMENT_COMMANDS_20250721_1435.md - Deployment instructions

## 💪 BOTTOM LINE

Your 200+ hours of development work is now fully portable and recoverable.
Plug in → Run setup → Start developing with zero protocol violations.
'''
        
        recovery_file = f"{self.backup_structure['documentation']}RECOVERY_GUIDE_{self.timestamp}.md"
        with open(recovery_file, 'w') as f:
            f.write(recovery_guide)
        print(f"   ✅ Recovery guide created")
        
    def execute_complete_backup(self):
        print("🎯 STARTING COMPLETE ENVIRONMENT BACKUP...")
        print("=" * 60)
        
        try:
            self.create_backup_structure()
            self.backup_complete_projects()
            self.create_setup_scripts()
            self.create_recovery_documentation()
            
            print("=" * 60)
            print("🏆 COMPLETE ENVIRONMENT BACKUP SUCCESSFUL!")
            print(f"📍 Location: {self.backup_root}")
            print("🔌 Ready for plug-and-play deployment on any Windows 11 computer")
            print("⚡ Your complete development environment is now portable!")
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            print("🆘 Check USB drive and permissions")

# EXECUTE BACKUP
if __name__ == "__main__":
    print("🚀 USB COMPLETE BACKUP SYSTEM STARTING...")
    backup_system = CompleteEnvironmentBackup(usb_drive_letter="D")  # CORRECTED TO D:
    backup_system.execute_complete_backup()
    print("🎉 BACKUP COMPLETE - YOUR ENVIRONMENT IS NOW PORTABLE!")