import json
import os
import subprocess
from pathlib import Path

import yaml

from framework.generators.fut_gen import FutTestConfigGenClass
from framework.lib.fut_lib import load_reg_rule, map_dict_key_path
from lib_testbed.generic.pod.pod import Pod
from lib_testbed.generic.util.config import load_tb_config
from lib_testbed.generic.util.logger import log


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FutConfigurator(metaclass=Singleton):
    testbed_cfg: dict
    regulatory_shell_file: str

    def __init__(self):
        log.debug(msg="Entered FutConfigurator class.")
        self.fut_base_dir = Path(__file__).absolute().parents[1].as_posix()
        self.fut_config_from_json = (
            False
            if os.getenv("FUT_CONFIG_FROM_JSON", "False").lower() in (False, None, "false", "none", "")
            else os.getenv("FUT_CONFIG_FROM_JSON")
        )
        self.fut_version_map = self._load_fut_version_map()
        self.fut_release_version = self._get_release_version()
        self.fut_test_hostname = "fut.opensync.io"
        self.curl_port_rate_limit = 8000
        self.regulatory_rule = load_reg_rule()
        self.regulatory_shell_file = self._create_regulatory_shell_file()
        self.testbed_name = os.getenv("OPENSYNC_TESTBED", self.get_testbed_name())
        self.testbed_cfg = load_tb_config(location_file=f"{self.testbed_name}.yaml", skip_deployment=True)
        self.base_ssid = f"FUT_ssid_{self.testbed_cfg['user_name']}"
        self.base_psk = f"FUT_psk_{self.testbed_cfg['user_name']}"
        self.fut_test_config_gen_cls = self._get_fut_test_config_generator()
        self.wireless_manager_names = ["wm", "owm"]

    @staticmethod
    def get_testbed_name() -> str:
        """
        Get the testbed name.

        Returns:
            (str): Testbed name.
        """
        testbed_name = subprocess.run(["cat", "/etc/hostname"], stdout=subprocess.PIPE)

        return testbed_name.stdout.decode("utf-8").strip()

    def _get_release_version(self) -> str | None:
        """
        Return the release version of the FUT sources.

        Returns:
            version (str): FUT release version.
        """
        version_file = Path(self.fut_base_dir).joinpath(".version")
        if not version_file.is_file():
            return None
        with open(version_file, "r") as version_fd:
            version = version_fd.read().strip()
        return version

    @staticmethod
    def _load_fut_version_map():
        """
        Load FUT version map.

        Loads the version map containing recommended and legacy client
        and server versions.

        Returns:
            (dict): FUT version dictionary.
            (None): If Fut version map dictionary cannot be loaded.
        """
        try:
            with open("config/rules/fut_version_map.yaml") as reg_rule_file:
                fut_version_map = yaml.safe_load(reg_rule_file)
        except Exception as exception:
            log.warning(f"Failed to load FUT version map: {exception}")
            return None

        return fut_version_map

    def _create_regulatory_shell_file(self) -> str:
        """
        Create regulatory file.

        Creates the regulatory file in the 'shell/config/' directory and
        names the file as 'regulatory.txt'.

        Returns:
            (str): Path to regulatory shell file.
        """
        reg_map_shell_path = f"{self.fut_base_dir}/shell/config/regulatory.txt"
        reg_map_shell_file = open(reg_map_shell_path, "w")

        for reg_key_value in map_dict_key_path(self.regulatory_rule):
            # Remove ',' from list, for easier shell retrieval
            ini_line = f"{reg_key_value[0].upper()}= {' '.join(str(x) for x in reg_key_value[1])}\n"
            reg_map_shell_file.write(ini_line)
        reg_map_shell_file.close()

        return reg_map_shell_path

    def _get_fut_test_config_generator(self) -> FutTestConfigGenClass:
        device_obj = Pod()
        gw_obj = device_obj.resolve_obj(**{"config": self.testbed_cfg, "nickname": "gw"})
        leaf_obj = device_obj.resolve_obj(**{"config": self.testbed_cfg, "nickname": "l1"})

        for obj in [gw_obj, leaf_obj]:
            if hasattr(obj, "override_version_specific_ifnames"):
                obj.override_version_specific_ifnames()

        fut_test_config_generator = FutTestConfigGenClass(
            gw=gw_obj,
            leaf=leaf_obj,
        )

        return fut_test_config_generator

    def get_test_config(self) -> dict:
        """
        Import test configuration for GW.

        This method uses the FUT generic test configuration generator.
        If the FUT_CONFIG_FROM_JSON environment variable is set, then
        the  method will load the JSON file from the
        FUT_CONFIG_FROM_JSON path as the configuration.

        Raises:
            RuntimeError: Failed to import FUT test configuration

        Returns:
            dict: Testcase configuration dictionary.
        """
        if self.fut_config_from_json:
            log.debug(msg=f"Using JSON configuration file: {self.fut_config_from_json}")
            try:
                if os.path.isabs(self.fut_config_from_json):
                    json_load_path = self.fut_config_from_json
                else:
                    json_load_path = f"{self.fut_base_dir}/{self.fut_config_from_json}"
                with open(json_load_path) as jf:
                    json_dict = json.load(jf)
                return json_dict
            except Exception as exception:
                raise RuntimeError(f"Failed to import the FUT test configuration: {exception}") from exception
        else:
            log.debug(msg="Using FUT generic test configuration generator")
            return self.fut_test_config_gen_cls.get_test_configs()
