import subprocess
import os
import sys
import shutil
import time
import json

# ------------------- Configuration -------------------
ISAAC_SIM_REPO = "https://github.com/isaac-sim/IsaacSim.git"
LAUNCHER_REPO = "https://github.com/brunorios1080/isaacsim_launcher_ui.git"

# Define directories
ISAAC_SIM_DIR = os.path.join(os.getcwd(), "IsaacSim")
LAUNCHER_DIR = os.path.join(os.getcwd(), "IsaacSim_Launcher")

# Use current Python interpreter
PYTHON_EXEC = sys.executable


# ------------------- Helper Functions -------------------
def run_command(cmd, cwd=None, max_retries=3):
    """
    Run a command using subprocess, printing output in real-time.
    Uses shell=True for reliable execution of Windows batch files and built-in commands.
    """
    cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
    print(f"\n--- Running: {cmd_str} ---")

    for attempt in range(max_retries):
        try:
            process = subprocess.Popen(
                cmd_str,
                cwd=cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            for line in process.stdout:
                print(line, end="")

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Command failed with return code {process.returncode}")

            print("--- Command succeeded. ---")
            return  # Success
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt + 1 < max_retries:
                sleep_time = 2 ** attempt
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise


# ------------------- Isaac Sim Setup -------------------
def clone_repo():
    """Clones the Isaac Sim repository and executes Git LFS commands."""
    if not os.path.exists(ISAAC_SIM_DIR):
        print(f"Cloning Isaac Sim into {ISAAC_SIM_DIR}...")
        run_command(["git", "clone", ISAAC_SIM_REPO, ISAAC_SIM_DIR])

        print("\nStarting Git LFS setup...")
        run_command(["git", "lfs", "install"], cwd=ISAAC_SIM_DIR)
        run_command(["git", "lfs", "pull"], cwd=ISAAC_SIM_DIR)
        print("Git LFS setup complete.")
    else:
        print(f"Directory {ISAAC_SIM_DIR} already exists. Skipping clone.")


def install_dependencies():
    """Installs required Python packages using pip."""
    req_file = os.path.join(ISAAC_SIM_DIR, "requirements.txt")
    if os.path.exists(req_file):
        print("Installing Python dependencies...")
        run_command([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([PYTHON_EXEC, "-m", "pip", "install", "-r", req_file])
    else:
        print("Warning: No requirements.txt found. Skipping dependency installation.")


def run_build():
    """Runs the Isaac Sim build.bat script from the root IsaacSim directory."""
    print("Building Isaac Sim...")
    run_command("build.bat", cwd=ISAAC_SIM_DIR)


def launch_isaac_sim():
    """Launches the Isaac Sim isaac-sim.bat script."""
    release_dir = os.path.join(ISAAC_SIM_DIR, "_build", "windows-x86_64", "release")
    launch_script = os.path.join(release_dir, "isaac-sim.bat")

    if os.path.exists(launch_script):
        print("Launching Isaac Sim...")
        run_command("isaac-sim.bat", cwd=release_dir)
    else:
        print(f"Error: Cannot find launch script at {launch_script}")


# ------------------- Launcher Setup -------------------
def install_launcher():
    """Downloads the Isaac Sim Launcher and configures it."""
    if not os.path.exists(LAUNCHER_DIR):
        print(f"\nCloning Isaac Sim Launcher into {LAUNCHER_DIR}...")
        run_command(["git", "clone", LAUNCHER_REPO, LAUNCHER_DIR])
    else:
        print("Launcher directory already exists. Skipping clone.")

    settings_path = os.path.join(LAUNCHER_DIR, "dist", "IsaacSimLauncher", "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            settings = json.load(f)
        settings["isaac_sim_path"] = os.path.abspath(ISAAC_SIM_DIR)
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
        print(f"Updated launcher settings.json with Isaac Sim path: {ISAAC_SIM_DIR}")
    else:
        print("Warning: settings.json not found in launcher repository.")


# ------------------- Main -------------------
def main():
    """Main execution flow for setup and launcher installation."""
    print("--- Isaac Sim Setup & Launcher Installer (Windows) ---")

    try:
        clone_repo()
        install_dependencies()
        run_build()
        launch_isaac_sim()
        install_launcher()
        print("\n✅ Isaac Sim and Launcher installed successfully.")
    except RuntimeError as e:
        print(f"\n❌ Setup FAILED during command execution: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
    finally:
        input("\n--- Script finished. Press Enter to exit... ---")


if __name__ == "__main__":
    main()
