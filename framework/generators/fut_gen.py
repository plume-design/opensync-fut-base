#!/usr/bin/python3

import importlib.util
import sys
import traceback
from pathlib import Path

import yaml

from framework.generators.DefaultGen import DefaultGenClass
from framework.lib.config import Config
from lib_testbed.generic.util.config import get_model_capabilities
from lib_testbed.generic.util.logger import log


fut_base_dir = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(fut_base_dir)


class FutTestConfigGenClass:
    def __init__(
        self,
        gw_name,
        leaf_name,
        modules=None,
        test_list=None,
    ):
        self.fut_base_dir = fut_base_dir
        self.gw_name = gw_name
        self.leaf_name = leaf_name
        self.gw_model_capabilities = self._load_model_capabilities(self.gw_name)
        self.leaf_model_capabilities = self._load_model_capabilities(self.leaf_name)
        self.modules = modules
        self.test_list = test_list
        self.test_generators = DefaultGenClass(
            gw_capabilities=self.gw_model_capabilities,
            leaf_capabilities=self.leaf_model_capabilities,
        )
        try:
            all_inputs = self._load_all_inputs()
            self.generic_inputs = all_inputs["generic"]
            self.model_inputs = all_inputs["model"]
            self.platform_inputs = all_inputs["platform"]
        except Exception as e:
            print(traceback.format_exc())
            raise Exception("Failed at _load_all_inputs", e)
        try:
            self.combined_inputs = self._load_combined_inputs()
        except Exception as e:
            print(traceback.format_exc())
            raise Exception("Failed at _load_combined_inputs", e)
        try:
            self.combined_configs = self._generate_config_from_inputs()
        except Exception as e:
            print(traceback.format_exc())
            raise Exception("Failed at _generate_config_from_inputs", e)

    def _load_inputs_in_dir(self, path, suffix="_inputs.py"):
        test_inputs = {}
        test_case_dir = Path(f"{self.fut_base_dir}/{path}")
        if not test_case_dir.exists():
            return test_inputs
        test_case_mod = path.replace("/", ".")
        inputs_files = [file.stem for file in test_case_dir.iterdir() if suffix in file.name]
        if self.modules:
            inputs_files = [
                f"{mod}{suffix}".rsplit(".")
                for mod in self.modules
                if test_case_dir.joinpath(f"{mod}{suffix}").is_file()
            ]
        for cfg_file in inputs_files:
            spec = importlib.util.find_spec(f"{test_case_mod}.{cfg_file}")
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Shallow-merge new module over existing dictionary
            test_inputs = {**test_inputs, **module.test_inputs}
        return test_inputs

    def _get_test_case_inputs_dir(self, subdir, config_dir="config/test_case"):
        """Return the path to the test case inputs directory, it could be in internal subdirectory."""
        config_paths = [
            Path(f"{config_dir}/{subdir}"),
            Path(f"internal/{config_dir}/{subdir}"),
        ]
        path = None
        for config_path in config_paths:
            if config_path.is_dir():
                path = config_path.as_posix()
                break
        return path

    def _load_model_capabilities(self, model_name):
        device_config_path = f"{self._get_test_case_inputs_dir(model_name)}/device/config.yaml"
        pod_api_model = None
        try:
            with open(device_config_path) as device_conf_file:
                device_config = yaml.safe_load(device_conf_file)
                pod_api_model = device_config.get("pod_api_model")
        except Exception as e:
            log.debug(f"Failed to open {device_config_path}. FUT configuration for device is missing!\n{e}")
        if not pod_api_model:
            pod_api_model = str(model_name).lower()
        log.info(f"Loading device capabilities for {pod_api_model}")
        return Config(get_model_capabilities(pod_api_model))

    def _load_all_inputs(self):
        test_all_cfg = {}
        # Load generic configurations
        test_case_generic_dir = self._get_test_case_inputs_dir("generic")
        test_generic_cfg = self._load_inputs_in_dir(test_case_generic_dir)
        test_all_cfg["generic"] = Config(test_generic_cfg)
        # Load model configurations
        test_case_model_dir = self._get_test_case_inputs_dir(f"model/{self.gw_name}")
        test_model_cfg = self._load_inputs_in_dir(test_case_model_dir)
        test_all_cfg["model"] = Config(test_model_cfg)
        # Load platform chipset configurations
        dut_platform_chipset = self.gw_model_capabilities.get("wifi_vendor")
        test_case_platform_dir = self._get_test_case_inputs_dir(f"platform/{dut_platform_chipset}")
        test_platform_cfg = self._load_inputs_in_dir(test_case_platform_dir)
        test_all_cfg["platform"] = Config(test_platform_cfg)
        return test_all_cfg

    def _load_combined_inputs(self):
        """Combine and sort inputs from generic, platform and model specific sources."""
        combined_inputs = Config(self.generic_inputs.cfg)
        combined_inputs_keys = sorted(
            set().union(*[self.generic_inputs.cfg, self.platform_inputs.cfg, self.model_inputs.cfg]),
        )
        for test_name in combined_inputs_keys:
            for extra_inputs in [self.platform_inputs, self.model_inputs]:
                # Add keys to combined_inputs if present in extra_inputs
                if test_name not in combined_inputs.cfg:
                    combined_inputs.cfg[test_name] = {}
                if extra_inputs.get(f"{test_name}.inputs"):
                    # Overwrite inputs
                    combined_inputs.cfg[test_name]["inputs"] = extra_inputs.get(f"{test_name}.inputs")
                    del extra_inputs.cfg[test_name]["inputs"]
                elif extra_inputs.get(f"{test_name}.additional_inputs"):
                    # Append inputs with additional_inputs
                    combined_inputs.cfg[test_name]["inputs"] = combined_inputs.cfg[test_name][
                        "inputs"
                    ] + extra_inputs.get(f"{test_name}.additional_inputs")
                    del extra_inputs.cfg[test_name]["additional_inputs"]
                if self.generic_inputs.get(f"{test_name}.default") and extra_inputs.get(f"{test_name}.default"):
                    # Merge default values
                    combined_inputs.cfg[test_name]["default"] = {
                        **combined_inputs.cfg[test_name]["default"],
                        **extra_inputs.get(f"{test_name}.default"),
                    }
                    del extra_inputs.cfg[test_name]["default"]
                if extra_inputs.get(f"{test_name}"):
                    # Merge any remaining inputs not caught above
                    combined_inputs.cfg[test_name] = {
                        **combined_inputs.get(test_name, {}),
                        **extra_inputs.get(test_name),
                    }
        # Sort combined inputs if possible
        for test_name in combined_inputs.cfg.keys():
            if "inputs" in combined_inputs.cfg[test_name]:
                try:
                    combined_inputs.cfg[test_name]["inputs"] = sorted(combined_inputs.cfg[test_name]["inputs"])
                except TypeError:
                    pass
        return combined_inputs

    def _generate_config_from_inputs(self):
        """Generate test case configuration from test case generator inpus."""
        combined_configs = {}
        for test_name in self.combined_inputs.cfg.keys():
            # Exclude all tests not present in list, if list of tests is given
            if self.test_list:
                if test_name not in self.test_list:
                    continue
            # Select the generator used for the testcase, use generic if missing
            if not hasattr(self.test_generators, f"gen_{test_name}"):
                log.debug(f"Missing test generator for test {test_name}, using default_gen")
                test_gen = self.test_generators.__getattribute__("default_gen")
            else:
                log.debug(f"Using gen_{test_name}")
                test_gen = self.test_generators.__getattribute__(f"gen_{test_name}")
            if test_gen:
                # Generate configuration from inputs using the selected generator
                combined_configs[test_name] = test_gen(self.combined_inputs.get(test_name))
        return combined_configs

    def get_test_configs(self):
        return self.combined_configs


if __name__ == "__main__":
    raise RuntimeError(f"{__file__} should only be imported, not invoked.")
