import logging
import os
import sys
import time

from colorama import Fore, Style


class PrintLogger:
    def __init__(self, log_dir=".", log_file_prefix=""):
        """
        Initialize the PrintLogger with an log directory. If no directory is
        provided, defaults to the current directory. The resulting log files
        will be timestamped with the script's current runtime.

        :param log_dir: Optional path to a directory for holding log files.
        """
        timestamp = int(time.time())  # Get current unix epoch time
        self.log_filename = os.path.join(log_dir, f"{log_file_prefix}{timestamp}.log")
        os.makedirs(log_dir, exist_ok=True)  # Ensure directory exists
        logging.basicConfig(
            filename=self.log_filename,
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding='utf-8',
        )

    def write(self, message):
        """Write the message to both stdout and the log file. Colorize if need be."""
        if message.strip():  # Avoid logging empty newlines
            logging.info(message.strip())
        color_message = self._colorize_message(message.strip())
        sys.__stdout__.write(color_message + "\n")  # Print to console with color

    def _colorize_message(self, message):
        """
        Colorizes text printed to the screen. Do not add any print statements to
        this method! Triggers a recursion nightmare.
        """
        if "error" in message.lower():
            return Style.BRIGHT + Fore.RED + message + Style.RESET_ALL
        elif "warning" in message.lower():
            return Style.BRIGHT + Fore.YELLOW + message + Style.RESET_ALL
        elif "success" in message.lower():
            return Style.BRIGHT + Fore.GREEN + message + Style.RESET_ALL
        elif "debug" in message.lower():
            return Style.BRIGHT + Fore.CYAN + message + Style.RESET_ALL
        else:
            return message

    def flush(self):
        """
        Flushes messages to stdout.
        """
        sys.__stdout__.flush()
