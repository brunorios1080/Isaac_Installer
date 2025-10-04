import subprocess
import os
import sys
import shutil
import time

# ------------------- Configuration -------------------
ISAAC_SIM_REPO = "https://github.com/isaac-sim/IsaacSim.git"
# Define the target directory relative to the current working directory
ISAAC_SIM_DIR = os.path.join(os.getcwd(), "IsaacSim")
# Use the current Python interpreter for consistency
PYTHON_EXEC = sys.executable

# ------------------- Helper Functions -------------------
def run_command(cmd, cwd=None, max_retries=3):
    """
    Run a command using subprocess, printing output in real-time.
    Uses shell=True for reliable execution of Windows batch files and built-in commands.
    """
    # Convert command list to a single string for execution with shell=True
    cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
    
    print(f"\n--- Running: {cmd_str} ---")

    for attempt in range(max_retries):
        try:
            # Use shell=True for Windows compatibility with path resolution and batch files
            process = subprocess.Popen(
                cmd_str,
                cwd=cwd, # This ensures the command runs in the specified directory
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                # creationflags=subprocess.CREATE_NEW_CONSOLE # Removed for cleaner console output
            )

            # Print output in real-time
            for line in process.stdout:
                print(line, end="")

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Command failed with return code {process.returncode}")

            print("--- Command succeeded. ---")
            return # Success, exit the loop

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt + 1 < max_retries:
                sleep_time = 2 ** attempt
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise # Re-raise the exception after the final attempt

def clone_repo():
    """Clones the Isaac Sim repository and executes Git LFS commands."""
    if not os.path.exists(ISAAC_SIM_DIR):
        print(f"Cloning Isaac Sim into {ISAAC_SIM_DIR}...")
        
        # 1. Execute git clone
        run_command(["git", "clone", ISAAC_SIM_REPO, ISAAC_SIM_DIR])
        
        print("\nStarting Git LFS setup...")
        # LFS commands must be run inside the newly cloned directory (ISAAC_SIM_DIR)
        
        # 2. Run git lfs install, executed inside ISAAC_SIM_DIR via cwd
        print("Running 'git lfs install'...")
        run_command(["git", "lfs", "install"], cwd=ISAAC_SIM_DIR)
        
        # 3. Run git lfs pull, executed inside ISAAC_SIM_DIR via cwd
        print("Running 'git lfs pull' to fetch large assets (This may take a while)...")
        run_command(["git", "lfs", "pull"], cwd=ISAAC_SIM_DIR)

        print("Git LFS setup complete.")
    else:
        print(f"Directory {ISAAC_SIM_DIR} already exists. Skipping clone.")

def install_dependencies():
    """Installs required Python packages using pip."""
    req_file = os.path.join(ISAAC_SIM_DIR, "requirements.txt")
    if os.path.exists(req_file):
        print("Installing Python dependencies...")
        # Ensure pip is up to date first
        run_command([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"])
        # Install requirements using the Python interpreter specified
        run_command([PYTHON_EXEC, "-m", "pip", "install", "-r", req_file])
    else:
        print("Warning: No requirements.txt found. Skipping dependency installation.")

def run_build():
    """
    Runs the Isaac Sim build.bat script from the root IsaacSim directory.
    Uses 'build.bat' directly in the root as requested by the user.
    """
    print("building Isaac Sim...")
    run_command("build.bat", cwd=ISAAC_SIM_DIR)


def launch_isaac_sim():
    """Launches the Isaac Sim isaac-sim.bat script."""
    release_dir = os.path.join(ISAAC_SIM_DIR, "_build", "windows-x86_64", "release")
    launch_script = os.path.join(release_dir, "isaac-sim.bat")
    
    if os.path.exists(launch_script):
        print("Launching Isaac Sim...")
        # Run the .bat file from inside the release folder
        run_command("isaac-sim.bat", cwd=release_dir)
    else:
        print(f"Error: Cannot find launch script at {launch_script}")
# ------------------- Main -------------------
def main():
    """Main execution flow for setting up and launching Isaac Sim."""
    print("--- Isaac Sim Setup & Launch Script (Windows) ---")
    
    try:
        clone_repo()
        install_dependencies()
        run_build()
        launch_isaac_sim()
        print("\nIsaac Sim launch command executed. Check the console for logs or a new window for the GUI.")
    except RuntimeError as e:
        print(f"\nSetup FAILED during command execution: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # Keep the console open after execution in case it was run via double-click
        input("\n--- Script finished. Press Enter to exit... ---")

if __name__ == "__main__":
    main()
