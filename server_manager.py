import os
import json
import time
import tomllib as toml
import json
import typer
import logging
import platform
import subprocess
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    executable_windows: str
    executable_linux: str
    log_file: str


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main(config_file: Optional[str] = typer.Option("./configs/server_manager_config.toml", "--config", "-c", help="Path to the configuration file")):
    """Starts or restarts the OpenMP server."""
    
    config: Config | None = load_toml_to_object(toml_file_path=config_file, object_type=Config)

    if config is None:
        exit(1)

    logging.info("Server starting...")
    logging.info("Checking server is running...")
    server_running = check_server_running()

    if server_running:
        logging.info("The server is running! The task will be killed in 5 sec!")
        time.sleep(5)
        kill_server(config)

    delete_log_file(config)

    logging.info("Start OpenMP")
    start_server(config)


def check_server_running() -> bool:
    """Checks if the OpenMP server process is running."""
    try:
        if platform.system() == "Windows":
            process = subprocess.run(["tasklist"], capture_output=True, text=True)
            return "omp-server.exe" in process.stdout
        else:
            process = subprocess.run(["pgrep", "-f", "omp-server"], capture_output=True, text=True)
            return bool(process.stdout.strip())
    except Exception as e:
        logging.info(f"Error checking server process: {e}")
        return False


def kill_server(config: Config):
    """Kills the OpenMP server process."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/IM", config.executable_windows, "/F"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", config.executable_linux], capture_output=True)
    except Exception as e:
        logging.info(f"Error stopping server: {e}")


def delete_log_file(config: Config):
    """Deletes the log file if it exists."""
    if os.path.exists(config.log_file):
        try:
            os.remove(config.log_file)
            logging.info(f"{config.log_file} is deleted!")
        except Exception as e:
            logging.info(f"Failed to delete {config.log_file}: {e}")
    else:
        logging.info(f"{config.log_file} does not exist!")


def start_server(config: Config):
    """Starts the OpenMP server process."""
    try:
        if platform.system() == "Windows":
            subprocess.run([config.executable_windows], text=True)
        else:
            subprocess.run([config.executable_linux], text=True)
        logging.info("Server started successfully")
    except Exception as e:
        logging.error(f"Failed to start server: {e}")


def toml_to_json(toml_string=None, toml_file_path=None, json_file_path=None):
    """
    Converts TOML data to JSON.

    Args:
        toml_string (str, optional): A string containing TOML data.
        toml_file_path (str, optional): Path to a TOML file.
        json_file_path (str, optional): Path to output JSON file.

    Returns:
        str: JSON string if successful, None otherwise.
    """

    data = None

    if toml_string:
        try:
            data = toml.loads(toml_string)
        except Exception as e:
            print(f"Error decoding TOML string: {e}")
            return None

    elif toml_file_path:
        try:
            with open(toml_file_path, 'rb') as f:
                data = toml.load(f)
        except FileNotFoundError:
            print(f"Error: TOML file not found at {toml_file_path}")
            return None
        except Exception as e:
            print(f"Error decoding TOML file: {e}")
            return None

    else:
        print("Error: Either toml_string or toml_file_path must be provided.")
        return None

    if data is not None:
        json_string = json.dumps(data, indent=4) # indent for readability

        if json_file_path:
            try:
                with open(json_file_path, 'w') as f:
                    f.write(json_string)
                return json_string # return the json string even when writing to a file.
            except Exception as e:
                print(f"Error writing to JSON file: {e}")
                return None

        else:
            return json_string

    return None


def load_toml_to_object(toml_string=None, toml_file_path=None, object_type=None) -> Config | None:
    """
    Loads TOML data into a Python object.

    Args:
        toml_string (str, optional): A string containing TOML data.
        toml_file_path (str, optional): Path to a TOML file.
        object_type (type, optional): The dataclass type to load the TOML data into.

    Returns:
        object_type: An instance of the specified object type, or None if an error occurs.
    """
    if object_type is None:
        raise ValueError("object_type must be provided.")

    data = None

    if toml_string:
        try:
            data = toml.loads(toml_string)
        except Exception as e:
            print(f"Error decoding TOML string: {e}")
            return None

    elif toml_file_path:
        try:
            with open(toml_file_path, 'rb') as f:
                data = toml.load(f)
        except FileNotFoundError:
            print(f"Error: TOML file not found at {toml_file_path}")
            return None
        except Exception as e:
            print(f"Error decoding TOML file: {e}")
            return None

    else:
        print("Error: Either toml_string or toml_file_path must be provided.")
        return None

    if data is not None:
        try:
            return object_type(**data)
        except TypeError as e:
             print(f"Error creating object: {e}. Check if TOML data matches object structure.")
             return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    return None


if __name__ == "__main__":
    typer.run(main)
