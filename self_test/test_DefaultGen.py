from copy import deepcopy
from pathlib import Path

import allure
import pytest
from mergedeep import merge

from config.defaults import (
    all_bandwidth_list,
    all_pytest_flags,
    def_channel_list,
    def_wifi_args,
    def_wifi_inputs,
    radio_band_list,
)
from framework.generators import DefaultGen
from lib_testbed.generic.util.logger import log


@pytest.fixture(
    params=[
        ("24g", 6, "HT40", None),
        ("5g", 44, "HT40", None),
        ("5gl", 44, "HT40", None),
        ("5gu", 157, "HT40", None),
        ("6g", 5, "HT40", None),
        ("24g", 40, "HT20", False),
        ("5g", 165, "HT40", False),
        ("24g", 13, "HT20", False),
    ],
)
def band_channel_ht_mode(request):
    gw_phy_radio_name = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities["interfaces"][
        "phy_radio_name"
    ]
    gw_bands = [band for band in gw_phy_radio_name.keys() if gw_phy_radio_name[band]]
    (band, channel, ht_mode, compatible) = request.param
    if band not in gw_bands:
        compatible = False
    elif band in gw_bands and compatible is None:
        compatible = True
    if compatible is None:
        raise RuntimeError("Invalid parameters for band_channel_ht_mode() fixture.")
    return band, channel, ht_mode, compatible


@pytest.fixture(
    params=[
        ("24g", "HT20", True),
        ("24g", "HT160", None),
        ("5g", "HT20", True),
        ("5g", "HT160", None),
        ("5gl", "HT20", True),
        ("5gl", "HT160", None),
        ("5gu", "HT20", True),
        ("5gu", "HT160", None),
        ("6g", "HT20", True),
        ("6g", "HT320", None),
    ],
)
def band_max_ht_mode(request):
    gw_phy_radio_name = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities["interfaces"][
        "phy_radio_name"
    ]
    max_channel_width = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities["interfaces"][
        "max_channel_width"
    ]
    gw_bands = [band for band in gw_phy_radio_name.keys() if gw_phy_radio_name[band]]
    (band, ht_mode, compatible) = request.param
    if band not in gw_bands:
        compatible = False
    elif band in gw_bands and compatible is None:
        compatible = int(ht_mode.split("HT")[1]) <= max_channel_width[band]
    if compatible is None:
        raise RuntimeError("Invalid parameters for band_max_ht_mode() fixture.")
    return band, ht_mode, compatible


@pytest.fixture
def default_gen():
    return pytest.fut_configurator.fut_test_config_gen_cls.test_generators


@pytest.fixture(params=["skip", "xfail"])
def flags(request):
    return request.param


@pytest.fixture
def generic_inputs():
    inputs = {
        "args_mapping": ["kconfig", "service"],
        "default": {
            "def_key_1": "def_val_1",
            "def_key_2": True,
            "def_key_3": 12345,
        },
        "inputs": [
            ["KC_1", "serv_1"],
            ["KC_2", False],
            ["KC_3", 53271],
        ],
    }
    return inputs


@pytest.fixture
def if_role_inputs():
    inputs = {
        "args_mapping": ["if_role"],
        "inputs": [
            ["home_ap"],
            ["lan_interfaces"],
            ["primary_wan_interface"],
        ],
    }
    return inputs


@pytest.fixture
def int_str_inputs():
    inputs = {
        "args_mapping": ["value"],
        "inputs": ["serv_1", 53271],
    }
    return inputs


@pytest.fixture
def wifi_inputs():
    inputs = {
        "args_mapping": def_wifi_args.copy(),
        "inputs": def_wifi_inputs + [[None, None, None]],
    }
    return inputs


@pytest.fixture
def mismatch_ht_mode_inputs():
    ht_mode_list = all_bandwidth_list
    inputs = {
        "args_mapping": def_wifi_args.copy(),
        "inputs": [[ch, bw, rb] for ch, bw, rb in zip(def_channel_list, ht_mode_list, radio_band_list)] + [[None] * 3],
    }
    return inputs


@pytest.fixture
def mismatch_channel_inputs():
    inputs = {
        "args_mapping": def_wifi_args.copy(),
        "inputs": [
            [1, "HT40", "24g"],
            [1, "HT40", "5g"],
            [1, "HT40", "5gl"],
            [1, "HT40", "5gu"],
            [1, "HT40", "6g"],
            [None, None, None],
        ],
    }
    return inputs


@pytest.fixture(
    params=[
        {"flag": {"msg": "Flagging all test case inputs"}},
        {
            "flag": {
                "inputs": [
                    ["KC_1", "serv_1"],
                    ["KC_2", False],
                ],
                "msg": "Flagging specific list of inputs",
            },
        },
    ],
)
def flag_inputs(request):
    return request.param


@pytest.fixture(params=radio_band_list)
def radio_band(request):
    return request.param


@pytest.fixture(params=all_pytest_flags)
def pytest_flags(request):
    return request.param


@pytest.fixture(
    params=[
        "backhaul_ap",
        "backhaul_sta",
        "home_ap",
        "lan_bridge",
        "lan_interfaces",
        "management_interface",
        "onboard_ap",
        "ppp_wan_interface",
        "primary_lan_interface",
        "primary_wan_interface",
        "uplink_gre",
        "wan_bridge",
        "wan_interfaces",
    ],
)
def if_role(request):
    return request.param


@allure.title("Validate DefaultGenClass")
class TestDefaultGenClass:
    @allure.title("Validate generator modules are collected")
    def test_generator_names_collected(self):
        file_path = Path(pytest.fut_configurator.fut_base_dir).joinpath("framework/generators")
        generators = [fn.stem for fn in file_path.iterdir() if not fn.is_dir() and fn.stem.endswith("Gen")]
        log.info(f"expected:{generators}")
        actual = DefaultGen.generator_names
        results = [
            generator not in actual if generator in ["__init__", "DefaultGen", "TemplateGen"] else generator in actual
            for generator in generators
        ]
        log.info(f"actual:{actual}")
        assert all(results)

    @allure.title("Validate _check_band_compatible() method and assert 2-3 bands per device.")
    def test__check_band_compatible(self, default_gen):
        gw_model_capabilities = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities
        bands = list(gw_model_capabilities["interfaces"]["phy_radio_name"].keys())
        is_band_compatible = [default_gen._check_band_compatible(band, "gw") for band in bands]
        log.info(f"Compatible bands:{list(zip(bands, is_band_compatible))}")
        assert 2 <= is_band_compatible.count(True) <= 3

    @allure.title("Validate _check_band_compatible() method returns false for invalid band.")
    def test__check_band_compatible_invalid_band(self, default_gen):
        assert not default_gen._check_band_compatible("9g", "gw")

    @allure.title("Validate _check_band_channel_compatible() method.")
    def test__check_band_channel_compatible(self, default_gen, band_channel_ht_mode):
        (band, channel, ht_mode, compatible) = band_channel_ht_mode
        log.info(f"band:{band}, channel:{channel}, ht_mode:{ht_mode}, compatible:{compatible}")
        assert default_gen._check_band_channel_compatible(band, channel, "gw", ht_mode) == compatible

    @allure.title("Validate get_if_name_type_from_if_role() method ")
    def test_get_if_name_type_from_if_role(self, default_gen, if_role):
        if_name_type_list = default_gen.get_if_name_type_from_if_role(if_role)
        if_type_list = ["bridge", "eth", "gre", "vif"]
        results = []
        for if_name, if_type in if_name_type_list:
            log.info(f"if_name:{if_name}, if_type:{if_type}")
            results.append(if_type in if_type_list)
        assert all(results)

    @allure.title("Validate _check_ht_mode_band_support() method.")
    def test__check_ht_mode_band_support(self, default_gen, band_max_ht_mode):
        (band, ht_mode, compatible) = band_max_ht_mode
        log.info(f"band:{band}, ht_mode:{ht_mode}, compatible:{compatible}")
        assert default_gen._check_ht_mode_band_support(band, ht_mode) == compatible

    @allure.title("Validate _replace_if_role_with_if_name_type() method.")
    def test__replace_if_role_with_if_name_type(self, default_gen, if_role_inputs):
        log.info(f"if_role_inputs:{if_role_inputs}")
        result_inputs = default_gen._replace_if_role_with_if_name_type(if_role_inputs)
        log.info(f"result_inputs:{result_inputs}")
        assert "if_name" in result_inputs["args_mapping"] and "if_type" in result_inputs["args_mapping"]
        assert all(len(single_input) == len(result_inputs["args_mapping"]) for single_input in result_inputs["inputs"])

    @allure.title("Validate _inputs_int_or_str_to_list() method.")
    def test__inputs_int_or_str_to_list(self, default_gen, int_str_inputs):
        log.info(f"int_str_inputs:{int_str_inputs}")
        result_inputs = default_gen._inputs_int_or_str_to_list(int_str_inputs)
        log.info(f"result_inputs:{result_inputs}")
        assert all(isinstance(single_input, list) for single_input in result_inputs["inputs"])

    @allure.title("Validate _implicit_insert_encryption() method.")
    def test__implicit_insert_encryption(self, default_gen, wifi_inputs):
        inputs = deepcopy(wifi_inputs)
        log.info(f"inputs:{inputs}")
        actual = default_gen._implicit_insert_encryption(inputs)
        log.info(f"actual:{actual}")
        assert "encryption" in actual["args_mapping"]
        assert all(len(single_input) == len(actual["args_mapping"]) for single_input in actual["inputs"])

    @allure.title("Validate _filter_device_incompatible_bands() method.")
    def test__filter_device_incompatible_bands(self, default_gen, wifi_inputs):
        log.info(f"wifi_inputs:{wifi_inputs}")
        result_inputs = default_gen._filter_device_incompatible_bands(wifi_inputs.copy())
        log.info(f"result_inputs:{result_inputs}")
        assert len(result_inputs["inputs"]) < len(wifi_inputs["inputs"])

    @allure.title("Validate _filter_device_incompatible_bandwidths() method.")
    def test__filter_device_incompatible_bandwidths(self, default_gen, mismatch_ht_mode_inputs):
        log.info(f"mismatch_ht_mode_inputs:{mismatch_ht_mode_inputs}")
        result_inputs = default_gen._filter_device_incompatible_bandwidths(mismatch_ht_mode_inputs.copy())
        log.info(f"result_inputs:{result_inputs}")
        assert len(result_inputs["inputs"]) < len(mismatch_ht_mode_inputs["inputs"])

    @allure.title("Validate _filter_regulatory_incompatible_wifi_params() method.")
    def test__filter_regulatory_incompatible_wifi_params(self, default_gen, mismatch_channel_inputs):
        log.info(f"mismatch_channel_inputs:{mismatch_channel_inputs}")
        result_inputs = default_gen._filter_regulatory_incompatible_wifi_params(mismatch_channel_inputs.copy())
        log.info(f"result_inputs:{result_inputs}")
        assert len(result_inputs["inputs"]) < len(mismatch_channel_inputs["inputs"])

    @allure.title("Validate _ignore_test_cases() method where specific or all inputs are ignored.")
    def test__ignore_test_cases_specific_inputs(self, default_gen, generic_inputs, flag_inputs):
        flag_inputs["ignore"] = flag_inputs.copy().pop("flag")
        combined_inputs = merge(generic_inputs, flag_inputs)
        log.info(f"combined_inputs:{combined_inputs}")
        result_inputs = default_gen._ignore_test_cases(combined_inputs.copy())
        log.info(f"result_inputs:{result_inputs}")
        assert len(result_inputs["inputs"]) < len(combined_inputs["inputs"])

    @allure.title("Validate _do_args_mapping() method with generic_inputs")
    def test__do_args_mapping_generic_inputs(self, default_gen, generic_inputs):
        inputs = generic_inputs
        log.info(f"inputs:{inputs}")
        # Always copy, as the method may alter arguments
        expected = deepcopy(inputs)
        expected["configs"] = [dict(zip(expected["args_mapping"], single_input)) for single_input in expected["inputs"]]
        log.info(f"expected:{expected}")
        actual = default_gen._do_args_mapping(inputs)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method with generic_inputs and custom flags")
    def test__do_args_mapping_custom_flags(self, default_gen, generic_inputs, flag_inputs, pytest_flags):
        flag_inputs[pytest_flags] = flag_inputs.copy().pop("flag")
        inputs = merge(generic_inputs, flag_inputs)
        log.info(f"inputs:{inputs}")
        actual = default_gen._do_args_mapping(inputs)
        log.info(f"actual:{actual}")
        assert any(f"{pytest_flags}_msg" in single_input for single_input in actual["configs"])
        assert any(pytest_flags in single_input for single_input in actual["configs"])

    @allure.title("Validate _do_args_mapping() method when there is no inputs key")
    def test__do_args_mapping_no_inputs_key(self, default_gen, generic_inputs):
        inputs = generic_inputs
        del inputs["inputs"]
        log.info(f"inputs:{inputs}")
        with pytest.raises(KeyError):
            default_gen._do_args_mapping(inputs)

    @allure.title("Validate _do_args_mapping() method when the args_mapping key is missing")
    def test__do_args_mapping_no_args_mapping_key(self, default_gen, generic_inputs):
        inputs = generic_inputs
        del inputs["args_mapping"]
        # Always copy, as the method may alter arguments
        expected = deepcopy(inputs)
        log.info(f"inputs:{inputs}")
        expected["configs"] = expected["inputs"]
        log.info(f"expected:{expected}")
        actual = default_gen._do_args_mapping(inputs)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method when the value to the inputs key is empty")
    def test__do_args_mapping_empty_inputs_value(self, default_gen, generic_inputs):
        inputs = generic_inputs
        inputs["inputs"] = []
        log.info(f"inputs:{inputs}")
        # Always copy, as the method may alter arguments
        expected = deepcopy(inputs)
        expected["configs"] = []
        log.info(f"expected:{expected}")
        actual = default_gen._do_args_mapping(inputs)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate default_gen() method")
    def test_default_gen(self, default_gen, generic_inputs):
        inputs = generic_inputs
        log.info(f"inputs:{inputs}")
        expected = [
            {**dict(zip(inputs["args_mapping"], single_input)), **inputs["default"]}
            for single_input in inputs["inputs"]
        ]
        log.info(f"expected:{expected}")
        actual = default_gen.default_gen(inputs)
        log.info(f"actual:{actual}")
        assert actual == expected
