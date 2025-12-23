import configparser
import os
import sys
from pathlib import Path


class ConfigReader:
    def __init__(
        self,
        config_filename=None,
    ):
        """
        Initialize the ConfigReader with the configuration file path. If no path
        is provided, defaults to a preset configuration file ("settings.cfg").

        :param config_filename: Optional path to a configuration file.
        """
        self.config = configparser.ConfigParser()

        self.config_filename = Path(os.getcwd() + "/settings.cfg")
        if config_filename is not None:
            self.config_filename = Path(config_filename)
        try:
            self.config_filename.resolve(strict=True)
        except FileNotFoundError as fe:
            print(f"{fe}")
            sys.exit(1)
        self._load_config()

    def _load_config(self):
        """Loads INI data from the specified config file."""
        try:
            self.config.read(self.config_filename)
        except configparser.Error as ce:
            print(f"[ERROR] Failed to load configuration file: {ce}")
            sys.exit(1)

    def get(self, section, option):
        """Retrieve a specific configuration option."""
        return self.config.get(section, option)

    def get_all(self):
        """Retrieve all configuration options."""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
        return config_dict

    def set(self, section, option, value):
        """Override a specific configuration option."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
