#!/usr/bin/python3

import importlib.util

import allure
import pytest

from framework.generators.fut_gen import FutTestConfigGenClass  # noqa: E402
from framework.lib.config import Config  # noqa: E402
from lib_testbed.generic.util.config import get_model_capabilities  # noqa: E402
from lib_testbed.generic.util.logger import log  # noqa: E402


all_suites = ["BRV", "CM", "CPM", "DM", "FSM", "NFM", "NM", "ONBRD", "OTHR", "PM", "QM", "SM", "UM", "VPNM", "WM"]
ref_model_list = ["BCM947622DVT", "PP203X", "PP403Z", "PP443Z", "PP603X"]
min_model_list = ["PP603X"]
model_list = ref_model_list
mock_model = "NEW_TEST_DEVICE"


@pytest.fixture(scope="module", params=model_list)
def test_config_gen(request):
    model = request.param
    return FutTestConfigGenClass(model, model)


@allure.title("Validate FutTestConfigGenClass")
class TestFutTestConfigGenClass:
    @allure.title("Validate FutTestConfigGenClass() constructor")
    def test_FutTestConfigGenClass_constructor(self):
        with pytest.raises(FileNotFoundError):
            FutTestConfigGenClass(mock_model, mock_model)

    @allure.title("Validate _get_test_case_inputs_dir() method returns path to model dir")
    def test__get_test_case_inputs_dir(self, test_config_gen):
        model = test_config_gen.gw_name
        expected = f"config/test_case/model/{model}"
        actual = test_config_gen._get_test_case_inputs_dir(f"model/{model}")
        log.info(f"model:{model}, expected:{expected}, actual:{actual}")
        assert expected == actual

    @allure.title("Validate _load_model_capabilities() methods returns correct Config")
    def test_load_model_capabilities(self, test_config_gen):
        model = test_config_gen.gw_name
        expected = Config(get_model_capabilities(model))
        actual = test_config_gen._load_model_capabilities(model)
        log.info(f"model:{model}, expected:{expected.cfg}, actual:{actual.cfg}")
        assert expected.cfg == actual.cfg

    @allure.title("Validate _load_inputs_in_dir() method for generic inputs")
    def test__load_inputs_in_dir_generic(self):
        test_config_gen = pytest.fut_configurator.fut_test_config_gen_cls
        test_case_generic_dir = test_config_gen._get_test_case_inputs_dir("generic")
        test_case_module = test_case_generic_dir.replace("/", ".")
        errors = []
        for suite in all_suites:
            spec = importlib.util.find_spec(f"{test_case_module}.{suite}_inputs")
            if not spec:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Manipulate modules attribute before calling _load_inputs_in_dir()
            test_config_gen.modules = [suite]
            actual = test_config_gen._load_inputs_in_dir(test_case_generic_dir)
            log.info(f"suite:{suite}, expected:{module.test_inputs}, actual:{actual}")
            if not module.test_inputs == actual:
                errors.append(f"suite:{suite}, expected:{module.test_inputs}, actual:{actual}")
        assert not errors, f"errors:{errors}"

    @allure.title("Validate _load_inputs_in_dir() method for platform specific inputs")
    def test__load_inputs_in_dir_platform(self, test_config_gen):
        platform_chipset = test_config_gen.gw_model_capabilities.get("wifi_vendor")
        test_case_generic_dir = test_config_gen._get_test_case_inputs_dir(f"platform/{platform_chipset}")
        test_case_module = test_case_generic_dir.replace("/", ".")
        errors = []
        for suite in all_suites:
            spec = importlib.util.find_spec(f"{test_case_module}.{suite}_inputs")
            if not spec:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Manipulate modules attribute before calling _load_inputs_in_dir()
            test_config_gen.modules = [suite]
            actual = test_config_gen._load_inputs_in_dir(test_case_generic_dir)
            log.info(f"suite:{suite}, expected:{module.test_inputs}, actual:{actual}")
            if not module.test_inputs == actual:
                errors.append(f"suite:{suite}, expected:{module.test_inputs}, actual:{actual}")
        assert not errors, f"errors:{errors}"

    @allure.title("Validate _load_inputs_in_dir() method for model specific inputs")
    def test__load_inputs_in_dir_model(self, test_config_gen):
        model = test_config_gen.gw_name
        test_case_generic_dir = test_config_gen._get_test_case_inputs_dir(f"model/{model}")
        test_case_module = test_case_generic_dir.replace("/", ".")
        errors = []
        for suite in all_suites:
            spec = importlib.util.find_spec(f"{test_case_module}.{suite}_inputs")
            if not spec:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Manipulate modules attribute before calling _load_inputs_in_dir()
            test_config_gen.modules = [suite]
            actual = test_config_gen._load_inputs_in_dir(test_case_generic_dir)
            log.info(f"suite:{suite}, expected:{module.test_inputs}, actual:{actual}")
            if not module.test_inputs == actual:
                errors.append(f"suite:{suite}, expected:{module.test_inputs}, actual:{actual}")
        assert not errors, f"errors:{errors}"

    @allure.title("Validate _load_inputs_in_dir() returns empty dict for non-existing modules")
    def test_load_inputs_in_dir_no_module_fallback(self):
        test_config_gen = pytest.fut_configurator.fut_test_config_gen_cls
        test_case_generic_dir = test_config_gen._get_test_case_inputs_dir("generic")
        # Manipulate modules attribute before calling _load_inputs_in_dir()
        test_config_gen.modules = ["MISSING_inputs"]
        actual = test_config_gen._load_inputs_in_dir(test_case_generic_dir)
        log.info(f"actual:{actual}")
        assert isinstance(actual, dict) and not actual

    @allure.title("Validate _load_inputs_in_dir() method returns empty dict for models without specific inputs")
    def test__load_inputs_in_dir_no_model_specifics(self):
        test_config_gen = pytest.fut_configurator.fut_test_config_gen_cls
        # Regardless of the model in test_config_gen.gw_model, use mock_model to simulate missing inputs
        test_case_generic_dir = test_config_gen._get_test_case_inputs_dir(f"model/{mock_model}")
        actual = test_config_gen._load_inputs_in_dir(test_case_generic_dir)
        log.info(f"actual:{actual}")
        assert isinstance(actual, dict) and not actual

    @allure.title("Validate _load_all_inputs() method produces generic, platform and model specific inputs")
    def test__load_all_inputs_generic_cfg(self):
        test_config_gen = pytest.fut_configurator.fut_test_config_gen_cls
        all_inputs = test_config_gen._load_all_inputs()
        assert sorted(all_inputs.keys()) == ["generic", "model", "platform"]

    @allure.title("Validate get_test_configs() method")
    def test_get_test_configs(self):
        test_config_gen = pytest.fut_configurator.fut_test_config_gen_cls
        test_configs = test_config_gen.get_test_configs()
        assert test_configs
