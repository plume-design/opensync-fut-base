import configparser
import os
from pathlib import Path

from lib_testbed.generic.util.logger import log


class FutAllureClass:
    def __init__(self, allure_dir):
        self.default_section = "Global"
        self.config_parser = configparser.ConfigParser()
        self.config_parser.add_section(self.default_section)
        self.envlist_filepath = Path(__file__).absolute().parents[2].joinpath("docker/env.list")
        if not self.envlist_filepath.is_file():
            self.envlist_filepath = Path(__file__).absolute().parents[2].joinpath("docker/env.list.base")
        self.properties_file = Path(f"{allure_dir}/environment.properties")
        # Determine which file to use to read existing config from file
        if self.properties_file.is_file():
            self.config_parser.read(self.properties_file)
        else:
            # Read from docker environment variable list
            with open(self.envlist_filepath, "r") as envlist_file:
                raw_lines = [line.rstrip("\n") for line in envlist_file.readlines()]
            # Remove any trailing equals signs
            env_vars = [line.split("=")[0] for line in raw_lines]
            # Get environment variables from system
            for env_var in env_vars:
                env_value = os.getenv(env_var)
                self.add_environment(env_var, env_value)
        # Write config parser values to file
        self.write_config()

    def add_environment(self, name, value, optional_suffix=None):
        if value in [None, ""] or name in [None, ""]:
            return
        # Update value if name exists
        prev_value = self.get_environment(name)
        if prev_value and prev_value != value:
            log.info(msg=f"Overriding: {name}, previous value: {prev_value}, value: {value}")
        self.config_parser.set(self.default_section, name, value)

    def get_environment(self, name):
        try:
            value = self.config_parser.get(self.default_section, name)
        except configparser.NoOptionError:
            value = None
        return value

    def set_device_bridge_type(self, device_type, bridge_type):
        self.add_environment(f"fut_{device_type}_bridge_type", bridge_type)
        self.write_config()

    def set_device_version(self, device_type, device_model, version):
        self.add_environment(f"fut_{device_type}_model", device_model)
        self.add_environment(f"fut_{device_type}_version", version)
        self.write_config()

    def set_release_version(self, version):
        self.add_environment("fut_release_version", version)
        self.write_config()

    def set_server_version(self, version):
        self.add_environment("server_device_version", version)
        self.write_config()

    def write_config(self):
        with open(self.properties_file, "w") as configfile:
            self.config_parser.write(configfile)
