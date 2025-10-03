import subprocess
import os
import sys
import shutil

# ------------------- Configuration -------------------
ISAAC_SIM_REPO = "https://github.com/isaac-sim/IsaacSim.git"
ISAAC_SIM_DIR = os.path.join(os.getcwd(), "IsaacSim")  # where to clone
PYTHON_EXEC = sys.executable  # ensures the script uses the current Python interpreter

# ------------------- Helper Functions -------------------
def run_command(cmd, cwd=None):
    """Run a command and print output in real-time."""
    print(f"Running: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def clone_repo():
    if not os.path.exists(ISAAC_SIM_DIR):
        print(f"Cloning Isaac Sim into {ISAAC_SIM_DIR}...")
        run_command(["git", "clone", ISAAC_SIM_REPO, ISAAC_SIM_DIR])
    else:
        print(f"{ISAAC_SIM_DIR} already exists. Skipping clone.")

def install_dependencies():
    req_file = os.path.join(ISAAC_SIM_DIR, "requirements.txt")
    if os.path.exists(req_file):
        print("Installing Python dependencies...")
        run_command([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([PYTHON_EXEC, "-m", "pip", "install", "-r", req_file])
    else:
        print("No requirements.txt found. Check Isaac Sim docs for dependencies.")

def run_build():
    build_script = os.path.join(ISAAC_SIM_DIR, "engine", "build_scripts", "build.sh")
    if os.path.exists(build_script):
        print("Running Isaac Sim build script...")
        run_command(["bash", build_script])
    else:
        print("No build script found. Isaac Sim may be launchable as-is.")

def launch_isaac_sim():
    launch_script = os.path.join(ISAAC_SIM_DIR, "run.py")  # adjust if the launcher is elsewhere
    if os.path.exists(launch_script):
        print("Launching Isaac Sim...")
        run_command([PYTHON_EXEC, launch_script])
    else:
        print("Cannot find launch script. Check the Isaac Sim directory.")

# ------------------- Main -------------------
def main():
    try:
        clone_repo()
        install_dependencies()
        run_build()
        launch_isaac_sim()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")  # so the console doesn't close immediately if .exe

if __name__ == "__main__":
    main()
