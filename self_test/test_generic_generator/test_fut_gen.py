#!/usr/bin/python3

import importlib.util
import sys
from pathlib import Path

import allure
import pytest

topdir_path = Path(__file__).absolute().parents[3].as_posix()
sys.path.append(topdir_path)
import framework.tools.logger  # noqa: E402
from config.model.generic.fut_gen import FutTestConfigGenClass  # noqa: E402
from framework.lib.config import Config  # noqa: E402
from lib_testbed.generic.util.config import get_model_capabilities  # noqa: E402

"""
Self-test for generic FUT testcase generator's FutTestConfigGenClass.
Run:
    python3 -m pytest ./self_test/test_generic_generator.py -v --alluredir=./allure-results/ -o log_cli=true
Display results:
    allure generate ./allure-results/ -o allure-report --clean; allure open allure-report
"""

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


@pytest.fixture(params=[
    "BCM947622DVT",
    "BCM947622DVTCH6",
    "MR8300-EXT",
    "PP203X",
    "PP403Z",
    "PP443Z",
    "PP603X",
])
def devices(request):
    return request.param


@pytest.fixture(params=["NEW_TEST_DEVICE", "AB1234X"])
def bad_devices(request):
    return request.param


@pytest.fixture(params=["optimized", "extended"])
def gen_type(request):
    return request.param


@allure.title("Validate FutTestConfigGenClass")
class TestFutTestConfigGenClass():
    @allure.title("Validate get_model_config_dir() method returns path to model dir")
    def test_get_model_config_dir(self, devices):
        fut_base_dir = f"{Path(__file__).absolute().parents[2].as_posix()}"
        expected = f"{fut_base_dir}/config/model/{devices}"
        actual = FutTestConfigGenClass(devices, devices).get_model_config_dir(devices)
        assert expected == actual
        log.info(msg=f'model:{devices}, expected:{expected}, actual:{actual}')

    @allure.title("Validate get_model_config_dir() method returns path to model dir")
    def test_get_model_config_dir_bad_device(self, bad_devices):
        with pytest.raises(Exception):
            FutTestConfigGenClass(bad_devices, bad_devices).get_model_config_dir(bad_devices)

    @allure.title("Validate _load_model_capabilities() methods returns correct Config")
    def test_load_model_capabilities(self, devices):
        expected = Config(get_model_capabilities(devices))
        actual = FutTestConfigGenClass(devices, devices)._load_model_capabilities(devices)
        assert expected.cfg == actual.cfg
        log.info(msg=f"model:{devices}, expected:{expected.cfg}, actual:{actual.cfg}")

    @allure.title("Validate _load_model_capabilities() methods fails for unknown device")
    def test_load_model_capabilities_fail_bad_device(self, bad_devices):
        with pytest.raises(Exception):
            FutTestConfigGenClass(bad_devices, bad_devices)._load_model_capabilities(bad_devices)

    @allure.title("Validate _load_module() method")
    def test_load_module(self, gen_type):
        testcase_module = f"config.model.generic.inputs.{gen_type}"
        expected = {}
        test_config_files = [
            'FSM_inputs',
            'UM_inputs',
            'OTHR_inputs',
            'SM_inputs',
            'NG_inputs',
            'WM_inputs',
            'BRV_inputs',
            'LM_inputs',
            'NM_inputs',
            'CM_inputs',
            'DM_inputs',
            'QM_inputs',
            'ONBRD_inputs',
            'UT_inputs',
        ]
        for cfg_file in test_config_files:
            spec = importlib.util.find_spec(f"{testcase_module}.{cfg_file}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            expected = {**expected, **module.test_inputs}
        actual = FutTestConfigGenClass("PP403Z", "PP203X", gen_type=gen_type)._load_module(test_config_files, testcase_module)
        assert expected == actual

    @allure.title("Validate _load_module() returns empty dict for non-existing modules")
    def test_load_module_no_module_fallback(self, gen_type):
        testcase_module = f"config.model.generic.inputs.{gen_type}"
        test_invalid_config_files = [
            'FOO_inputs',
            'BAR_inputs',
        ]
        expected = {}
        actual = FutTestConfigGenClass("PP403Z", "PP203X")._load_module(test_invalid_config_files, testcase_module)
        assert expected == actual

    @allure.title("Validate _load_module() loads modules from self.modules")
    def test_load_module_with_modules_list(self, gen_type):
        testcase_module = f"config.model.generic.inputs.{gen_type}"
        expected = {}
        test_config_files = [
            'FSM_inputs',
            'UM_inputs',
        ]
        for cfg_file in test_config_files:
            spec = importlib.util.find_spec(f"{testcase_module}.{cfg_file}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            expected = {**expected, **module.test_inputs}
        actual = FutTestConfigGenClass("PP403Z", "PP203X", modules=['FSM', 'UM'], gen_type=gen_type)._load_module(test_config_files, testcase_module)
        assert expected == actual

    @allure.title("Validate _load_configuration() method")
    def test_load_configurations_generic_cfg(self, gen_type):
        fut_base_dir = f"{Path(__file__).absolute().parents[2].as_posix()}"
        testcase_generic_dir = f'config/model/generic/inputs/{gen_type}'
        testcase_generic_mod = testcase_generic_dir.replace('/', '.')
        tc_generic_dir = Path(f'{fut_base_dir}/{testcase_generic_dir}')
        config_generic_files = [f.stem for f in tc_generic_dir.iterdir() if '_inputs.py' in f.name]
        test_generic_cfg = FutTestConfigGenClass("PP403Z", "PP203X")._load_module(config_generic_files, testcase_generic_mod)
        expected = Config(test_generic_cfg)
        actual, _, _ = FutTestConfigGenClass("PP403Z", "PP203X", gen_type=gen_type)._load_configurations()
        assert expected.cfg == actual.cfg

    @allure.title("Validate _load_configuration() method")
    def test_load_configurations_model_cfg(self, devices):
        fut_base_dir = f"{Path(__file__).absolute().parents[2].as_posix()}"
        testcase_model_dir = f'config/model/{devices}/inputs'
        testcase_model_mod = testcase_model_dir.replace('/', '.')
        tc_model_dir = Path(f"{fut_base_dir}/{testcase_model_dir}")
        test_model_cfg = {}
        config_model_files = [f.stem for f in tc_model_dir.iterdir() if '_inputs.py' in f.name]
        test_model_cfg = FutTestConfigGenClass(devices, "PP203X")._load_module(config_model_files, testcase_model_mod)
        expected = Config(test_model_cfg)
        _, actual, _ = FutTestConfigGenClass(devices, "PP203X")._load_configurations()
        assert expected.cfg == actual.cfg

    @allure.title("Validate _load_configuration() method")
    def test_load_configurations_vendor_cfg(self, devices):
        fut_base_dir = f"{Path(__file__).absolute().parents[2].as_posix()}"
        test_vendor_cfg = {}
        dut_vendor_chipset = FutTestConfigGenClass(devices, "PP203X")._load_model_capabilities(devices).get('wifi_vendor')
        testcase_vendor_dir = f'config/model/generic/inputs/{dut_vendor_chipset}'
        testcase_vendor_mod = testcase_vendor_dir.replace('/', '.')
        tc_vendor_dir = Path(f'{fut_base_dir}/{testcase_vendor_dir}')
        config_vendor_files = [f.stem for f in tc_vendor_dir.iterdir() if '_inputs.py' in f.name]
        test_vendor_cfg = FutTestConfigGenClass(devices, "PP203X")._load_module(config_vendor_files, testcase_vendor_mod)
        expected = Config(test_vendor_cfg)
        _, _, actual = FutTestConfigGenClass(devices, "PP203X")._load_configurations()
        assert expected.cfg == actual.cfg

    @allure.title("Validate _load_configuration() method")
    def test_load_configurations_no_model_path(self, bad_devices):
        with pytest.raises(Exception):
            FutTestConfigGenClass(bad_devices, "PP203X")._load_configurations()

    @allure.title("Validate _load_configuration() method")
    def test_load_configurations_no_vendor(self, bad_devices):
        with pytest.raises(Exception):
            FutTestConfigGenClass(bad_devices, "PP203X")._load_configurations()

    @allure.title("Validate get_test_configs() method")
    def test_get_test_configs(self, gen_type, devices):
        expected = FutTestConfigGenClass(devices, "PP203X", gen_type=gen_type).combined_configs
        actual = FutTestConfigGenClass(devices, "PP203X", gen_type=gen_type).get_test_configs()
        assert expected == actual
