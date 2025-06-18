import os
import time
import platform
import subprocess


def restart_server_function():
    kill_server()
    time.sleep(2)
    delete_log_file()
    start_server()
    subprocess.run(["python", "omp-server.py"])


def check_server_running() -> bool:
    try:
        if platform.system() == "Windows":
            process = subprocess.run(["tasklist"], capture_output=True, text=True)
            return "omp-server.exe" in process.stdout
        else:
            process = subprocess.run(["pgrep", "-f", "omp-server"], capture_output=True, text=True)
            return bool(process.stdout.strip())
    except Exception as e:
        print(f"Error checking server status: {e}")
        return False


def kill_server():
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/IM", "../omp-server", "/F"], capture_output=True)
        else:
            subprocess.run(["pkill", "-fc", "../omp-server"], capture_output=True)
    except Exception as e:
        print(f"Error stopping server: {e}")


def start_server():
    try:
        if platform.system() == "Windows":
            subprocess.run(["omp-server.exe"], text=False)
        else:
            subprocess.run(["../omp-server"], text=False)
        print("Server started successfully")
    except Exception as e:
        print(f"Failed to start server: {e}")


def delete_log_file():
    if os.path.exists("../log.txt"):
        try:
            os.remove("../log.txt")
            print(f"log.txt is deleted!")
        except Exception as e:
            print(f"Failed to delete log.txt: {e}")
    else:
        print(f"log.txt does not exist!")

