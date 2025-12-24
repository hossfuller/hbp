import os
import pathlib
import platform

## -------------------------------------------------------------------------- ##
## CONSTANTS
## -------------------------------------------------------------------------- ##

# fmt: off
DEFAULT_CONFIG_INI_FILE = "config/settings.ini"
SYSTEM_NAME             = platform.system()
# fmt: on

## -------------------------------------------------------------------------- ##
## FUNCTIONS
## -------------------------------------------------------------------------- ##


def sanitize_path(path_string, return_path_obj=False):
    """
    Takes a directory path string and converts it into an OS-appropriate path.

    Args:
        path_string (str): The directory path we want to sanitize.
        return_path_obj (bool): Whether or not we should return the path obj.

    Returns:
        str: The OS-sanitized directory path.
        obj: The OS-dependent Path object.
    """
    if SYSTEM_NAME == "Windows":
        # path_obj = pathlib.PureWindowsPath(path_string)
        path_obj = pathlib.WindowsPath(path_string)
        path_str = str(path_obj)
    else:
        path_obj = pathlib.Path(path_string)
        path_str = str(path_obj)

    if return_path_obj:
        return path_obj
    else:
        return path_str


def verify_directory_path(path_string):
    """
    Determine whether or not a directory exists. Attempts to smoothly handle the
    difference between Windows and Linux paths.

    Args:
        path_string (str): The directory path we want to check.

    Returns:
        str: The OS-sanitized directory path.
    """
    path_str = sanitize_path(path_string)
    if not os.path.isdir(path_str):
        raise TypeError(f"'{path_str}' is not an existing directory.")
    return path_str


def verify_file_path(filepath):
    """
    Checks if a file exists and is a regular file.
    """
    if not os.path.exists(filepath):
        raise TypeError(f"Error: File '{filepath}' not found.")
    elif not os.path.isfile(filepath):
        raise TypeError(f"Error: '{filepath}' is not a regular file.")
    return filepath
