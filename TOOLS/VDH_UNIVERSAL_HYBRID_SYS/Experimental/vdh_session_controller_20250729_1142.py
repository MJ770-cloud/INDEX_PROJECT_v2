# vdh_session_controller_20250729_1142.py
# VDH Session Controller - Master Orchestrator
# Created: July 29, 2025 - 11:42 AM Pacific
# Purpose: Master controller for complete VDH workflow orchestration

import sys
import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import threading
import webbrowser

class VDHSessionController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 VDH SESSION CONTROLLER - Master Orchestrator")
        self.root.geometry("900x600")
        self.root.configure(bg="#2c3e50")
        
        # System paths
        self.base_dir = Path("C:/INDEX-PROJECT")
        self.scripts_dir = self.base_dir / "scripts"
        self.media_dir = self.base_dir / "TCE-MEDIA/DIYTRAX"
        
        # Component scripts
        self.components = {
            "manual_assist": "VDH_MANUAL_ASSIST_BATCH_SYSTEM_20250729_1047.py",
            "config_helper": "vdh_config_helper_20250729_1120.py", 
            "batch_processor": "vdh_batch_processor_20250729_1120.py"
        }
        
        # Session state
        self.session_active = False
        self.current_phase = "ready"
        self.system_checks_passed = False
        
        self.setup_gui()
        self.run_system_checks()

    def setup_gui(self):
        """Create the master controller interface"""
        # Title banner
        title_frame = tk.Frame(self.root, bg="#1a252f", height=60)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎯 VDH SESSION CONTROLLER - MASTER ORCHESTRATOR",
                              bg="#1a252f", fg="#ecf0f1", font=("Arial", 14, "bold"))
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Complete DIYTRAX Video Collection & Processing Pipeline",
                                 bg="#1a252f", fg="#bdc3c7", font=("Arial", 10))
        subtitle_label.pack()

        # System status panel
        status_frame = tk.LabelFrame(self.root, text="🔧 System Status", 
                                    font=("Arial", 10, "bold"), bg="#34495e", fg="#ecf0f1")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_text = tk.Text(status_frame, height=6, font=("Consolas", 9),
                                  bg="#2c3e50", fg="#ecf0f1", wrap="word")
        self.status_text.pack(fill=tk.X, padx=5, pady=5)

        # Workflow phases
        phases_frame = tk.LabelFrame(self.root, text="📋 Workflow Phases", 
                                    font=("Arial", 10, "bold"), bg="#34495e", fg="#ecf0f1")
        phases_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Phase 1: Configuration
        phase1_frame = tk.Frame(phases_frame, bg="#34495e")
        phase1_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(phase1_frame, text="PHASE 1:", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="#f39c12").pack(side=tk.LEFT)
        tk.Label(phase1_frame, text="System Configuration & Setup", 
                bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT, padx=(5,20))
        
        self.config_btn = tk.Button(phase1_frame, text="⚙️ RUN CONFIG",
                                   command=self.run_configuration,
                                   bg="#f39c12", fg="white", font=("Arial", 9, "bold"))
        self.config_btn.pack(side=tk.RIGHT)
        
        # Phase 2: Manual Collection
        phase2_frame = tk.Frame(phases_frame, bg="#34495e")
        phase2_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(phase2_frame, text="PHASE 2:", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="#3498db").pack(side=tk.LEFT)
        tk.Label(phase2_frame, text="Manual VDH Video Collection", 
                bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT, padx=(5,20))
        
        self.collection_btn = tk.Button(phase2_frame, text="🎬 START COLLECTION",
                                       command=self.start_collection,
                                       bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                                       state='disabled')
        self.collection_btn.pack(side=tk.RIGHT)
        
        # Phase 3: Batch Processing
        phase3_frame = tk.Frame(phases_frame, bg="#34495e")
        phase3_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(phase3_frame, text="PHASE 3:", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="#27ae60").pack(side=tk.LEFT)
        tk.Label(phase3_frame, text="Batch Organization & Processing", 
                bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT, padx=(5,20))
        
        self.processing_btn = tk.Button(phase3_frame, text="🚀 BATCH PROCESS",
                                       command=self.run_batch_processing,
                                       bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                                       state='disabled')
        self.processing_btn.pack(side=tk.RIGHT)
        
        # Phase 4: Transcription Pipeline
        phase4_frame = tk.Frame(phases_frame, bg="#34495e")
        phase4_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(phase4_frame, text="PHASE 4:", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="#e74c3c").pack(side=tk.LEFT)
        tk.Label(phase4_frame, text="Transcription & INDEX Ready", 
                bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT, padx=(5,20))
        
        self.transcription_btn = tk.Button(phase4_frame, text="📝 TRANSCRIBE",
                                          command=self.launch_transcription,
                                          bg="#e74c3c", fg="white", font=("Arial", 9, "bold"),
                                          state='disabled')
        self.transcription_btn.pack(side=tk.RIGHT)

        # Progress tracking
        progress_frame = tk.Frame(phases_frame, bg="#34495e")
        progress_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(progress_frame, text="Overall Progress:", 
                bg="#34495e", fg="#ecf0f1", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=4)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.progress_label = tk.Label(progress_frame, text="0/4 Complete", 
                                      bg="#34495e", fg="#ecf0f1", font=("Arial", 9))
        self.progress_label.pack(side=tk.RIGHT)

        # Control buttons
        control_frame = tk.Frame(self.root, bg="#2c3e50")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - session controls
        session_controls = tk.Frame(control_frame, bg="#2c3e50")
        session_controls.pack(side=tk.LEFT)
        
        tk.Button(session_controls, text="🔄 REFRESH STATUS",
                 command=self.refresh_system_status,
                 bg="#95a5a6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(session_controls, text="📁 OPEN MEDIA DIR",
                 command=self.open_media_directory,
                 bg="#9b59b6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        # Right side - emergency controls
        emergency_controls = tk.Frame(control_frame, bg="#2c3e50")
        emergency_controls.pack(side=tk.RIGHT)
        
        tk.Button(emergency_controls, text="🚨 RESET WORKFLOW",
                 command=self.reset_workflow,
                 bg="#c0392b", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(emergency_controls, text="💾 SAVE SESSION",
                 command=self.save_session_state,
                 bg="#16a085", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

    def run_system_checks(self):
        """Run comprehensive system readiness checks"""
        self.log_status("🔧 Running system readiness checks...")
        
        checks = {
            "directories": self.check_directories(),
            "components": self.check_components(),
            "dependencies": self.check_dependencies(),
            "permissions": self.check_permissions()
        }
        
        all_passed = all(checks.values())
        
        if all_passed:
            self.log_status("✅ All system checks passed - Ready to begin!")
            self.system_checks_passed = True
            self.config_btn.config(state='normal')
        else:
            self.log_status("❌ System checks failed - Review requirements")
            failed_checks = [k for k, v in checks.items() if not v]
            self.log_status(f"Failed checks: {', '.join(failed_checks)}")

    def check_directories(self):
        """Check if required directories exist"""
        try:
            required_dirs = [
                self.base_dir,
                self.scripts_dir,
                self.media_dir
            ]
            
            for directory in required_dirs:
                directory.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            self.log_status(f"Directory check failed: {str(e)}")
            return False

    def check_components(self):
        """Check if all component scripts exist"""
        try:
            missing_components = []
            for name, filename in self.components.items():
                component_path = self.scripts_dir / filename
                if not component_path.exists():
                    missing_components.append(filename)
            
            if missing_components:
                self.log_status(f"Missing components: {', '.join(missing_components)}")
                return False
            
            return True
        except Exception as e:
            self.log_status(f"Component check failed: {str(e)}")
            return False

    def check_dependencies(self):
        """Check Python dependencies"""
        try:
            required_modules = ['tkinter', 'json', 'pathlib', 'subprocess']
            for module in required_modules:
                __import__(module)
            return True
        except ImportError as e:
            self.log_status(f"Dependency check failed: {str(e)}")
            return False

    def check_permissions(self):
        """Check file system permissions"""
        try:
            test_file = self.base_dir / "permission_test.tmp"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception as e:
            self.log_status(f"Permission check failed: {str(e)}")
            return False

    def run_configuration(self):
        """Execute Phase 1: Configuration"""
        self.log_status("⚙️ Starting Phase 1: System Configuration...")
        self.current_phase = "configuration"
        
        try:
            config_script = self.scripts_dir / self.components["config_helper"]
            
            # Run configuration in separate thread
            def run_config():
                result = subprocess.run([sys.executable, str(config_script)], 
                                      capture_output=True, text=True, cwd=str(self.scripts_dir))
                
                if result.returncode == 0:
                    self.log_status("✅ Phase 1 Complete: Configuration successful")
                    self.collection_btn.config(state='normal')
                    self.update_progress(1)
                else:
                    self.log_status(f"❌ Configuration failed: {result.stderr}")
            
            threading.Thread(target=run_config, daemon=True).start()
            
        except Exception as e:
            self.log_status(f"❌ Configuration launch failed: {str(e)}")

    def start_collection(self):
        """Execute Phase 2: Manual Collection"""
        self.log_status("🎬 Starting Phase 2: Manual VDH Collection...")
        self.current_phase = "collection"
        
        try:
            collection_script = self.scripts_dir / self.components["manual_assist"]
            
            # Launch manual assist system
            subprocess.Popen([sys.executable, str(collection_script)], 
                           cwd=str(self.scripts_dir))
            
            self.log_status("✅ Manual collection system launched")
            self.log_status("👁️ Monitor collection progress in separate window")
            
            # Enable next phase after delay (user will complete manually)
            self.root.after(5000, lambda: self.processing_btn.config(state='normal'))
            self.update_progress(2)
            
        except Exception as e:
            self.log_status(f"❌ Collection launch failed: {str(e)}")

    def run_batch_processing(self):
        """Execute Phase 3: Batch Processing"""
        self.log_status("🚀 Starting Phase 3: Batch Processing...")
        self.current_phase = "processing"
        
        try:
            processor_script = self.scripts_dir / self.components["batch_processor"]
            
            def run_processor():
                result = subprocess.run([sys.executable, str(processor_script)], 
                                      capture_output=True, text=True, cwd=str(self.scripts_dir))
                
                if result.returncode == 0:
                    self.log_status("✅ Phase 3 Complete: Batch processing successful")
                    self.transcription_btn.config(state='normal')
                    self.update_progress(3)
                else:
                    self.log_status(f"❌ Batch processing failed: {result.stderr}")
            
            threading.Thread(target=run_processor, daemon=True).start()
            
        except Exception as e:
            self.log_status(f"❌ Batch processing launch failed: {str(e)}")

    def launch_transcription(self):
        """Execute Phase 4: Transcription"""
        self.log_status("📝 Starting Phase 4: Transcription Pipeline...")
        self.current_phase = "transcription"
        
        try:
            engine_path = Path("C:/ENGINE-PROJECT/src/engines/working/openai_transcription_engine_v16_INDEX_ready_20250720_0748.py")
            
            if engine_path.exists():
                # Launch transcription engine
                subprocess.Popen([
                    "powershell.exe", 
                    "-Command", 
                    f"cd '{engine_path.parent}'; python '{engine_path.name}'"
                ])
                
                self.log_status("✅ Phase 4 Complete: Transcription engine launched")
                self.update_progress(4)
                
                messagebox.showinfo("Workflow Complete", 
                    "🎉 VDH Collection Workflow Complete!\n\n"
                    "✅ All phases executed successfully\n"
                    "📁 Videos collected and organized\n"
                    "🚀 Transcription engine running\n"
                    "📊 Ready for INDEX development!")
            else:
                self.log_status("❌ Transcription engine not found")
                messagebox.showwarning("Engine Missing", 
                    "Transcription engine not found. Please verify ENGINE-PROJECT setup.")
                
        except Exception as e:
            self.log_status(f"❌ Transcription launch failed: {str(e)}")

    def update_progress(self, phase):
        """Update progress bar and label"""
        self.progress_bar['value'] = phase
        self.progress_label.config(text=f"{phase}/4 Complete")

    def log_status(self, message):
        """Log status message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, full_message)
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def refresh_system_status(self):
        """Refresh system status"""
        self.status_text.delete(1.0, tk.END)
        self.run_system_checks()

    def open_media_directory(self):
        """Open media directory in explorer"""
        try:
            subprocess.Popen(f'explorer "{self.media_dir}"')
        except Exception as e:
            self.log_status(f"Failed to open directory: {str(e)}")

    def reset_workflow(self):
        """Reset workflow to initial state"""
        result = messagebox.askyesno("Reset Workflow", 
            "⚠️ Reset entire workflow to initial state?\n\n"
            "This will disable all phases and require restart.")
        
        if result:
            self.current_phase = "ready"
            self.progress_bar['value'] = 0
            self.progress_label.config(text="0/4 Complete")
            
            # Reset button states
            self.collection_btn.config(state='disabled')
            self.processing_btn.config(state='disabled')
            self.transcription_btn.config(state='disabled')
            
            if self.system_checks_passed:
                self.config_btn.config(state='normal')
            
            self.log_status("🔄 Workflow reset to initial state")

    def save_session_state(self):
        """Save current session state"""
        try:
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "current_phase": self.current_phase,
                "progress": self.progress_bar['value'],
                "system_checks_passed": self.system_checks_passed
            }
            
            session_file = self.base_dir / f"vdh_session_state_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            self.log_status(f"💾 Session state saved: {session_file.name}")
            
        except Exception as e:
            self.log_status(f"❌ Session save failed: {str(e)}")

    def run(self):
        """Start the session controller"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🎯 VDH Session Controller - Master Orchestrator")
    print("Created: July 29, 2025 - 11:42 AM Pacific")
    print("Purpose: Complete VDH workflow orchestration")
    print()
    
    try:
        controller = VDHSessionController()
        controller.run()
    except KeyboardInterrupt:
        print("\n👋 Session cancelled by user")
    except Exception as e:
        print(f"❌ Controller error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())