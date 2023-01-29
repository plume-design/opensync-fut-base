#!/usr/bin/python3

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.append('../../../')

import yaml

import framework.tools.logger
from config.model.generic.generators.DefaultGen import DefaultGenClass
from framework.lib.config import Config
from lib_testbed.generic.util.config import get_model_capabilities

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


class FutTestConfigGenClass:
    def __init__(
            self,
            dut_gw_name,
            ref_leaf_name,
            modules=None,
            test_list=None,
            gen_type='optimized',
    ):
        self.fut_base_dir = Path(__file__).absolute().parents[3].as_posix()
        self.dut_gw_name = dut_gw_name
        self.ref_leaf_name = ref_leaf_name
        self.gen_type = gen_type
        self.dut_gw_model_capabilities = self._load_model_capabilities(self.dut_gw_name)
        self.ref_leaf_model_capabilities = self._load_model_capabilities(self.ref_leaf_name)
        self.modules = modules
        self.test_list = test_list
        self.test_generators = DefaultGenClass(
            dut_gw_capabilities=self.dut_gw_model_capabilities,
            ref_leaf_capabilities=self.ref_leaf_model_capabilities,
            gen_type=self.gen_type,
        )
        # Load all default generic configurations here
        self.generic_inputs, self.model_inputs, self.vendor_inputs = self._load_configurations()
        self.combined_inputs = self._load_combined_inputs()
        self.combined_configs = self._load_combined_config()

    def _load_module(self, cfg_files, mod):
        test_inputs = {}
        for cfg_file in cfg_files:
            if self.modules:
                found = False
                for module in self.modules:
                    if module in cfg_file:
                        found = True
                if not found:
                    continue
            spec = importlib.util.find_spec(f'{mod}.{cfg_file}')
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Shallow-merge new module over existing dictionary
                test_inputs = {**test_inputs, **module.test_inputs}
        return test_inputs

    def get_model_config_dir(self, model_name):
        """Return the path to the model config directory, it could be in internal subdirectory."""
        model_config_subdir = 'config/model'
        model_config_paths = [
            Path(f"{self.fut_base_dir}/{model_config_subdir}/{model_name}"),
            Path(f"{self.fut_base_dir}/internal/{model_config_subdir}/{model_name}"),
        ]
        model_config_path = None
        for model_config_path in model_config_paths:
            if model_config_path.is_dir():
                break
        else:
            log.error(f"FUT configuration for device {model_name} is missing!. Please make sure it exists.")
        return None if not model_config_path else model_config_path.as_posix()

    def _load_model_capabilities(self, model_name):
        device_config_path = f'{self.get_model_config_dir(model_name)}/device/config.yaml'
        pod_api_model = None
        try:
            with open(device_config_path) as device_conf_file:
                device_config = yaml.safe_load(device_conf_file)
                pod_api_model = device_config.get('pod_api_model')
        except Exception as e:
            log.error(f'Failed to open {device_config_path}. FUT configuration for device is missing!\n{e}')
        if not pod_api_model:
            pod_api_model = str(model_name).lower()
        log.info(f'Loading device capabilities for {pod_api_model}')
        return Config(get_model_capabilities(pod_api_model))

    def _load_configurations(self):
        # Load generic configurations
        testcase_generic_dir = f'config/model/generic/inputs/{self.gen_type}'
        testcase_generic_mod = testcase_generic_dir.replace('/', '.')
        tc_generic_dir = Path(f'{self.fut_base_dir}/{testcase_generic_dir}')
        config_generic_files = [f.stem for f in tc_generic_dir.iterdir() if '_inputs.py' in f.name]
        test_generic_cfg = self._load_module(config_generic_files, testcase_generic_mod)

        # Load model configurations
        testcase_model_dir = f'config/model/{self.dut_gw_name}/inputs'
        testcase_model_mod = testcase_model_dir.replace('/', '.')
        tc_model_dir = Path(f'{self.fut_base_dir}/{testcase_model_dir}')
        test_model_cfg = {}
        if Path.exists(tc_model_dir):
            config_model_files = [f.stem for f in tc_model_dir.iterdir() if '_inputs.py' in f.name]
            test_model_cfg = self._load_module(config_model_files, testcase_model_mod)
        else:
            log.error(f'FUT configuration {tc_model_dir} does not exist, make sure that FUT configuration is created')

        # Load vendor chipset configurations
        test_vendor_cfg = {}
        dut_vendor_chipset = self.dut_gw_model_capabilities.get('wifi_vendor')
        if not dut_vendor_chipset or dut_vendor_chipset == '':
            log.error('Missing DUT wifi_vendor model capability entry')
        else:
            testcase_vendor_dir = f'config/model/generic/inputs/{dut_vendor_chipset}'
            testcase_vendor_mod = testcase_vendor_dir.replace('/', '.')
            tc_vendor_dir = Path(f'{self.fut_base_dir}/{testcase_vendor_dir}')
            if Path.exists(tc_vendor_dir):
                config_vendor_files = [f.stem for f in tc_vendor_dir.iterdir() if '_inputs.py' in f.name]
                test_vendor_cfg = self._load_module(config_vendor_files, testcase_vendor_mod)
            else:
                log.error(f'DUT wifi_vendor {dut_vendor_chipset} generic inputs definitions does not exits, skipping')
        return Config(test_generic_cfg), Config(test_model_cfg), Config(test_vendor_cfg)

    def _load_combined_inputs(self):
        combined_inputs = Config(self.generic_inputs.cfg)
        for test_name in self.generic_inputs.cfg.keys():
            if self.model_inputs.get(f'{test_name}.inputs'):
                combined_inputs.cfg[test_name]['inputs'] = self.model_inputs.get(f'{test_name}.inputs')
                del (self.model_inputs.cfg[test_name]['inputs'])
            elif self.model_inputs.get(f'{test_name}.additional_inputs'):
                combined_inputs.cfg[test_name]['inputs'] = \
                    combined_inputs.cfg[test_name]['inputs'] + self.model_inputs.get(f'{test_name}.additional_inputs')
                del (self.model_inputs.cfg[test_name]['additional_inputs'])
            if self.generic_inputs.get(f'{test_name}.default') and self.model_inputs.get(f'{test_name}.default'):
                combined_inputs.cfg[test_name]['default'] = {
                    **combined_inputs.cfg[test_name]['default'],
                    **self.model_inputs.get(f'{test_name}.default'),
                }
                del (self.model_inputs.cfg[test_name]['default'])
            if self.model_inputs.get(f'{test_name}'):
                combined_inputs.cfg[test_name] = {
                    **combined_inputs.cfg[test_name],
                    **self.model_inputs.get(f'{test_name}'),
                }
            if self.vendor_inputs.get(f'{test_name}.additional_inputs'):
                combined_inputs.cfg[test_name]['inputs'] = \
                    combined_inputs.cfg[test_name]['inputs'] + self.vendor_inputs.get(f'{test_name}.additional_inputs')
        for test_name, test_config in self.model_inputs.cfg.items():
            if test_name not in combined_inputs.cfg:
                combined_inputs.cfg[test_name] = test_config
        return combined_inputs

    def _load_combined_config(self):
        combined_configs = {}
        for test_name in self.combined_inputs.cfg.keys():
            if self.test_list:
                if test_name not in self.test_list:
                    continue
            if not hasattr(self.test_generators, f'gen_{test_name}'):
                log.warning(f'Missing test generator for test {test_name}, using default_gen')
                test_gen = self.test_generators.__getattribute__('default_gen')
            else:
                log.info(f'Using gen_{test_name}')
                test_gen = self.test_generators.__getattribute__(f'gen_{test_name}')
            if test_gen:
                combined_configs[test_name] = test_gen(self.combined_inputs.get(test_name))
        return combined_configs

    def get_test_configs(self):
        return self.combined_configs


if __name__ == '__main__':
    tool_description = """
    Generate FUT test configuration
    Tool generates FUT test configuration and outputs in JSON file if specified

    Example of usage:
    python3 fut_gen.py --dut PP203X -ref PP203X -j test.config.json
    """

    # Instantiate the parser
    parser = argparse.ArgumentParser(
        description=tool_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Define options
    parser.add_argument(
        '-d', '--dut',
        required=True,
        type=str,
        help='Model name DUT/GW',
    )
    parser.add_argument(
        '-r', '--ref',
        required=True,
        type=str,
        help='Model name REF/LEAF #1',
    )
    parser.add_argument(
        '-j', '--json',
        required=False,
        default=None,
        type=str,
        help='Model name REF/LEAF #1',
    )
    parser.add_argument(
        '-m', '--module',
        required=False,
        default=None,
        type=str,
        nargs='+',
        help='Output test configuration for given test module(s)',
    )
    parser.add_argument(
        '-t', '--test',
        required=False,
        default=None,
        type=str,
        nargs='+',
        help='Output test configuration for given test name(s)',
    )
    parser.add_argument(
        '-gn', '--gen_type',
        metavar='gen-type',
        required=False,
        type=str,
        default='optimized',
        choices=['optimized', 'extended'],
        help='Generation type of test configurations',
    )
    opts = parser.parse_args()

    try:
        res = FutTestConfigGenClass(
            dut_gw_name=opts.dut,
            ref_leaf_name=opts.ref,
            modules=opts.module,
            test_list=opts.test,
            gen_type=opts.gen_type,
        ).get_test_configs()
        if opts.json:
            print(f'Saving test configuration to output {opts.json}')
            with open(opts.json, 'w') as json_f:
                json_f.write(json.dumps({'data': res}, sort_keys=True, indent=4))
        else:
            print('Test configuration output')
            print(json.dumps({'data': res}, sort_keys=True, indent=4))
        sys.exit(0)
    except Exception as e:
        print(f'Exception caught during test config generation\n{e}')
        sys.exit(1)
