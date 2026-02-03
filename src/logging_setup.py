import logging
import os

def get_log_path(log_filename="timer_cli.log"):
    """Returns the absolute path to the log file in the user's home directory."""
    home_dir = os.path.expanduser("~")
    log_dir = os.path.join(home_dir, ".timer_cli")
    os.makedirs(log_dir, exist_ok=True)
        
    return os.path.join(log_dir, log_filename)

def setup_logging(log_filename="timer_cli.log"):
    """
    Configures the logging system to write to a centralized file in the user's home directory.
    """
    log_path = get_log_path(log_filename)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info(f"Logging system initialized at {log_path}")

def log_action(category, action, details=""):
    """
    Helper to log structured actions.
    Example: log_action("Timer", "Start", "ID: 12345")
    """
    logging.info(f"[{category}] {action} - {details}")
