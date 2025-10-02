import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform
import os
import tempfile
import time
import sys

# --- Configuration & Global State ---
PYTHON_VERSION = "3.11"
ISAAC_SIM_VERSION = "5.0.0"
PYTORCH_VERSION = "torch==2.2.0 torchvision==0.17.0"
PYTORCH_INDEX = "https://download.pytorch.org/whl/cu121"
ENV_NAME = "isaac_sim_50"

# Shell configuration based on detection (for script generation)
SYSTEM_OS = platform.system().lower()
IS_WINDOWS = SYSTEM_OS == 'windows'

class IsaacSimInstaller(tk.Tk):
    """A Tkinter GUI for initiating a silent, background Isaac Sim installation."""
    
    # Class-level flag to enable or disable actual installation
    # Set to True for testing the GUI/execution flow; set to False for the real installer
    IS_TEST_MODE = True
    
    def __init__(self):
        super().__init__()
        # Adjust title based on test mode
        title_suffix = " (TEST MODE)" if self.IS_TEST_MODE else ""
        self.title(f"Isaac Sim {ISAAC_SIM_VERSION} Silent Installer{title_suffix}")
        self.geometry("600x350")
        self.resizable(False, False)
        
        # Style Configuration
        style = ttk.Style(self)
        style.theme_use('vista')
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=6)
        style.configure('TLabel', font=('Inter', 10), background='white')
        style.configure('TFrame', background='white')
        style.configure('Header.TLabel', font=('Inter', 14, 'bold'), foreground='#003366')
        
        # Main Frame
        self.main_frame = ttk.Frame(self, padding="20", style='TFrame')
        self.main_frame.pack(expand=True, fill='both')

        # Title
        ttk.Label(self.main_frame, text="Isaac Sim Python Environment Setup", style='Header.TLabel').pack(pady=(0, 15))
        
        # Status Label (Dynamic)
        self.status_var = tk.StringVar(self, "Ready to start installation.")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=550)
        self.status_label.pack(pady=(5, 20))

        # Information Text
        if self.IS_TEST_MODE:
            info_text = (
                "🚀 **TEST MODE ACTIVE**: This will run a quick, harmless script to verify the installer GUI "
                "and background execution logic. No actual Conda environment will be created.\n\n"
                "The process should take only a few seconds.\n"
                "DO NOT close this window until the success message appears."
            )
        else:
            info_text = (
                "This will perform a full background installation of the required Conda environment "
                f"('{ENV_NAME}') and install Isaac Sim {ISAAC_SIM_VERSION} and PyTorch {PYTORCH_VERSION}.\n\n"
                "This process may take several minutes and runs silently in the background.\n"
                "DO NOT close this window until the success message appears."
            )
        ttk.Label(self.main_frame, text=info_text, justify=tk.LEFT, wraplength=550).pack(pady=(0, 30))

        # Control Button
        button_text = "Start Quick Test" if self.IS_TEST_MODE else "Start Silent Installation"
        self.install_button = ttk.Button(self.main_frame, text=button_text, command=self.start_installation, style='TButton')
        self.install_button.pack(pady=10)

        # Progress Bar (optional, for visual feedback)
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", length=400, mode="indeterminate")

    def _generate_script_content(self):
        """Generates the full shell script content (e.g., .bat or .sh)."""
        
        commands = []
        
        if self.IS_TEST_MODE:
            # --- Quick Test Script ---
            if IS_WINDOWS:
                commands.append("@echo off")
                commands.append("echo Starting test script...")
                commands.append("timeout /t 5 /nobreak >nul") # Wait 5 seconds
                commands.append("echo Test complete.")
                return "\n".join(commands), "test_script.bat"
            else:
                commands.append("#!/bin/bash")
                commands.append("echo 'Starting test script...'")
                commands.append("sleep 5") # Wait 5 seconds
                commands.append("echo 'Test complete.'")
                return "\n".join(commands), "test_script.sh"
        
        # --- Real Installation Script (Original Logic) ---
        if IS_WINDOWS:
            # Batch file commands
            commands.append("@echo off")
            commands.append(f"echo Starting Isaac Sim Environment Setup for Windows...")
            commands.append(f"conda create -n {ENV_NAME} python={PYTHON_VERSION} -y")
            # Conda activate requires CALL in a batch file
            commands.append(f"CALL conda activate {ENV_NAME}") 
            commands.append("echo Environment activated. Installing dependencies...")
            
            # Use 'pip' directly inside the activated environment
            commands.append("pip install --upgrade pip")
            commands.append(f"pip install {PYTORCH_VERSION} --extra-index-url {PYTORCH_INDEX}")
            commands.append(f"pip install \"isaacsim[all,extscache]=={ISAAC_SIM_VERSION}\" --extra-index-url https://pypi.nvidia.com")
            
            commands.append("echo Installation complete. Launching Isaac Sim...")
            commands.append("isaacsim")
            
            # The installer will report back success after the script finishes
            return "\n".join(commands), "install_script.bat"
        
        else:
            # Bash script commands (Linux/macOS)
            commands.append("#!/bin/bash")
            commands.append(f"echo 'Starting Isaac Sim Environment Setup for Linux/macOS...'")
            commands.append(f"conda create -n {ENV_NAME} python={PYTHON_VERSION} -y")
            # Conda activation requires sourcing the shell init file
            commands.append("source $(conda info --base)/etc/profile.d/conda.sh")
            commands.append(f"conda activate {ENV_NAME}")
            commands.append("echo 'Environment activated. Installing dependencies...'")

            commands.append("pip install --upgrade pip")
            commands.append(f"pip install {PYTORCH_VERSION} --extra-index-url {PYTORCH_INDEX}")
            commands.append(f"pip install 'isaacsim[all,extscache]=={ISAAC_SIM_VERSION}' --extra-index-url https://pypi.nvidia.com")
            
            commands.append("echo 'Installation complete. Launching Isaac Sim...'")
            commands.append("isaacsim")
            
            return "\n".join(commands), "install_script.sh"


    def start_installation(self):
        """Disables the button, shows progress, and executes the installer script silently."""
        
        self.install_button.config(state=tk.DISABLED)
        self.status_var.set("Installation started in the background. Please wait...")
        self.progress.pack(pady=10)
        self.progress.start(10) # Start indeterminate movement

        script_content, filename = self._generate_script_content()
        
        # 1. Write the script to a temporary file
        try:
            temp_dir = tempfile.gettempdir()
            script_path = os.path.join(temp_dir, filename)
            
            with open(script_path, 'w') as f:
                f.write(script_content)
                
            if not IS_WINDOWS:
                # Need execution permission for Linux/macOS scripts
                os.chmod(script_path, 0o755)

        except Exception as e:
            messagebox.showerror("File Error", f"Could not create temporary script: {e}")
            self._reset_gui()
            return
            
        # 2. Execute the script silently
        try:
            if IS_WINDOWS:
                # Use creationflags to suppress the console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # Execute the .bat file using cmd
                process = subprocess.Popen(
                    ['cmd.exe', '/C', script_path], 
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    startupinfo=startupinfo
                )
            else:
                # Use nohup to run in the background (Linux/macOS)
                # Note: This still relies on Conda being initialized in the shell environment.
                # If conda init is missing, the script will fail silently.
                process = subprocess.Popen(
                    ['nohup', script_path, '&'],
                    close_fds=True,
                    stdout=subprocess.DEVNULL, # Direct output to null
                    stderr=subprocess.DEVNULL
                )
            
            # Use a thread or after() to monitor the process without freezing the GUI
            self.after(1000, lambda: self._monitor_process(process, script_path))

        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to start installation process. Check Conda setup: {e}")
            self._reset_gui()

    def _monitor_process(self, process, script_path):
        """Checks the status of the background installation process."""
        if process.poll() is None:
            # Process is still running, check again in 1 second
            self.after(1000, lambda: self._monitor_process(process, script_path))
        else:
            # Process finished
            self.progress.stop()
            self.progress.pack_forget()
            
            # Clean up the temporary script
            try:
                os.remove(script_path)
            except Exception:
                pass # Ignore errors if file is already gone or locked

            if process.returncode == 0:
                # Adjust success message for test mode
                success_msg = "Test completed successfully! The installer logic works." if self.IS_TEST_MODE else "Isaac Sim installation is complete and should now be launched!"
                messagebox.showinfo("Success", success_msg)
                self.status_var.set("Installation finished successfully!")
            else:
                messagebox.showerror("Installation Failed", 
                                     "The installation script finished with errors. "
                                     "Please check your Conda installation and try again.")
                self.status_var.set("Installation failed. Please see the error message.")

            self.install_button.config(state=tk.NORMAL)

    def _reset_gui(self):
        """Resets the GUI state on failure."""
        self.install_button.config(state=tk.NORMAL)
        self.progress.stop()
        self.progress.pack_forget()
        self.status_var.set("Ready to start installation.")


if __name__ == "__main__":
    app = IsaacSimInstaller()
    app.mainloop()
