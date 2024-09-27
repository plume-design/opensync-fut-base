#!/usr/bin/python3

import importlib.util
import sys
from pathlib import Path

from mergedeep import merge, Strategy

from framework.generators.DefaultGen import DefaultGenClass
from lib_testbed.generic.pod.generic.pod_api import PodApi
from lib_testbed.generic.util.logger import log


fut_base_dir = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(fut_base_dir)


class FutTestConfigGenClass:
    def __init__(self, gw: "PodApi", leaf: "PodApi", modules=None, test_list=None):
        self.fut_base_dir = fut_base_dir
        self.gw = gw
        self.leaf = leaf
        self.modules = modules
        self.test_list = test_list
        self.test_generators = DefaultGenClass(
            gw=self.gw,
            leaf=self.leaf,
        )
        self.all_inputs = None
        self.combined_configs = None

    def _load_inputs_in_dir(self, path: str, suffix: str = "_inputs.py") -> dict:
        """
        Load test case inputs from the provided path and return as dict.

        The method will find all files with the provided suffix in the provided path. It will load the 'test_inputs'
        dicts within each of these files, and merge them.
        Args:
            path (str): Path to the directory, where test case input files are searched for.
            suffix (str): The file suffix to search for in the provided path

        Returns:
            test_inputs (dict): Test case inputs, loaded from several files, merged into a single dictionary.
        """
        test_inputs = {}
        test_case_dir = Path(f"{self.fut_base_dir}/{path}")
        if not test_case_dir.exists():
            return test_inputs
        test_case_mod = path.replace("/", ".")
        inputs_files = [file.stem for file in test_case_dir.iterdir() if file.name.endswith(suffix)]
        # Filter input files to match only the provided module names
        if self.modules:
            assert isinstance(self.modules, list)
            inputs_files = [
                f"{mod}{suffix}".rsplit(".")[0]
                for mod in self.modules
                if test_case_dir.joinpath(f"{mod}{suffix}").is_file()
            ]
        for cfg_file in inputs_files:
            spec = importlib.util.find_spec(f"{test_case_mod}.{cfg_file}")
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Shallow-merge new module over existing dict
            test_inputs |= module.test_inputs
        return test_inputs

    def _get_test_case_inputs_dirs(self, subdir: str, config_dir: str = "config/test_case") -> list:
        """
        Return a list of paths to the test case inputs directories. The path could be in the internal subdirectory.

        Args:
            subdir (str): The name of the sub-directory
            config_dir (str): The path to the config directory, relative to the top working directory.

        Returns:
            paths (list): List of paths to test case inputs directories.
        """
        paths = [
            cfgpath.as_posix()
            for cfgpath in [Path(f"{config_dir}/{subdir}"), Path(f"internal/{config_dir}/{subdir}")]
            if cfgpath.is_dir()
        ]
        return paths

    def _load_all_inputs(self) -> dict:
        """
        Load, combine and sort inputs from generic, platform and model specific input files.

        Returns:
            combined_inputs (dict): Dict containing all test case inputs in a single dict.
        """
        test_case_generic_dirs = self._get_test_case_inputs_dirs("generic")
        dut_platform_chipset = self.gw.capabilities.get_wifi_vendor()
        test_case_platform_dirs = self._get_test_case_inputs_dirs(f"platform/{dut_platform_chipset}")
        test_case_model_dirs = self._get_test_case_inputs_dirs(
            f"model/{self.gw.model.upper().replace('-', '_')}",
        )

        test_case_inputs = []
        for test_case_dir in test_case_generic_dirs + test_case_platform_dirs + test_case_model_dirs:
            test_case_inputs.append(self._load_inputs_in_dir(test_case_dir))

        combined_inputs = merge(*test_case_inputs, strategy=Strategy.ADDITIVE)
        for _, test_inputs in combined_inputs.items():
            try:
                if test_inputs.get("do_not_sort"):
                    continue
                test_inputs["inputs"].sort()
            except (TypeError, KeyError):
                pass
        return combined_inputs

    def _generate_config_from_inputs(self):
        """Generate test case configuration from test case generator inputs."""
        combined_configs = {}
        all_inputs = self.get_all_inputs()
        for test_name in all_inputs.keys():
            # Exclude all tests not present in list, if list of tests is given as input parameter
            if self.test_list:
                if test_name not in self.test_list:
                    continue
            # Select the generator used for the testcase, use generic if missing
            if not hasattr(self.test_generators, f"gen_{test_name}"):
                log.debug(f"Test generator missing: test_{test_name}. Using default_gen().")
                test_gen = self.test_generators.__getattribute__("default_gen")
            else:
                log.debug(f"Test generator present: test_{test_name}")
                test_gen = self.test_generators.__getattribute__(f"gen_{test_name}")
            if test_gen:
                # Generate configuration from inputs using the selected generator
                combined_configs[test_name] = test_gen(all_inputs.get(test_name))
        return combined_configs

    def get_all_inputs(self):
        if self.all_inputs is None:
            self.all_inputs = self._load_all_inputs()
        return self.all_inputs

    def get_test_configs(self):
        if self.combined_configs is None:
            self.combined_configs = self._generate_config_from_inputs()
        return self.combined_configs


if __name__ == "__main__":
    raise RuntimeError(f"{__file__} should only be imported, not invoked.")
