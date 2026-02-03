import logging
import os

def setup_logging(log_file="timer_cli.log"):
    """
    Configures the logging system to write to a file.
    Logs are appended to the file.
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Also log to console if needed for debugging, but typically for TUI apps
    # we avoid stdout/stderr as it messes up the display.
    # So we strictly log to file.
    logging.info("Logging system initialized.")

def log_action(category, action, details=""):
    """
    Helper to log structured actions.
    Example: log_action("Timer", "Start", "ID: 12345")
    """
    logging.info(f"[{category}] {action} - {details}")
