from copy import deepcopy
from pathlib import Path

import allure
import pytest

from framework.generators import DefaultGen
from lib_testbed.generic.util.logger import log


@pytest.fixture(
    params=[
        ("24g", 6, "HT40", None),
        ("5g", 44, "HT40", None),
        ("5gl", 44, "HT40", None),
        ("5gu", 157, "HT40", None),
        ("6g", 5, "HT40", None),
        ("2.4g", 40, "HT20", False),
        ("5g", 165, "HT40", False),
        ("2.4g", 13, "HT20", False),
    ],
)
def band_channel_ht_mode(request):
    gw_phy_radio_name = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities.get(
        "interfaces.phy_radio_name",
    )
    gw_bands = [band for band in gw_phy_radio_name.keys() if gw_phy_radio_name[band]]
    (band, channel, ht_mode, compatible) = request.param
    if band not in gw_bands:
        compatible = False
    elif band in gw_bands and compatible is None:
        compatible = True
    if compatible is None:
        raise RuntimeError("Invalid parameters for band_channel_ht_mode() fixture.")
    return (band, channel, ht_mode, compatible)


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
    gw_phy_radio_name = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities.get(
        "interfaces.phy_radio_name",
    )
    max_channel_width = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities.get(
        "interfaces.max_channel_width",
    )
    gw_bands = [band for band in gw_phy_radio_name.keys() if gw_phy_radio_name[band]]
    (band, ht_mode, compatible) = request.param
    if band not in gw_bands:
        compatible = False
    elif band in gw_bands and compatible is None:
        compatible = int(ht_mode.split("HT")[1]) <= max_channel_width[band]
    if compatible is None:
        raise RuntimeError("Invalid parameters for band_max_ht_mode() fixture.")
    return (band, ht_mode, compatible)


@pytest.fixture
def default_gen():
    return pytest.fut_configurator.fut_test_config_gen_cls.test_generators


@pytest.fixture(params=["skip", "xfail"])
def fut_option(request):
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


@pytest.fixture(params=["24g", "5g", "5gl", "5gu", "6g"])
def radio_band(request):
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

    @allure.title("Validate _get_default_options() method returns the content of default key.")
    def test__get_default_options(self, default_gen, generic_inputs):
        inputs = generic_inputs
        log.info(f"inputs:{inputs}")
        expected = inputs["default"]
        log.info(f"expected:{expected}")
        actual = default_gen._get_default_options(inputs=inputs)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _check_band_compatible() method and assert 2-3 bands per device.")
    def test__check_band_compatible(self, default_gen):
        gw_model_capabilities = pytest.fut_configurator.fut_test_config_gen_cls.gw_model_capabilities
        bands = list(gw_model_capabilities.get("interfaces.phy_radio_name").keys())
        is_band_compatible = [default_gen._check_band_compatible(band, "gw") for band in bands]
        log.info(f"Compatible bands:{list(zip(bands, is_band_compatible))}")
        assert 2 <= is_band_compatible.count(True) <= 3

    @allure.title("Validate _check_band_compatible() method returns empty for invalid band.")
    def test__check_band_compatible_invalid_band(self, default_gen):
        is_band_compatible = default_gen._check_band_compatible("9g", "gw")
        assert not is_band_compatible

    @allure.title("Validate _check_band_channel_compatible() method.")
    def test__check_band_channel_compatible(self, default_gen, band_channel_ht_mode):
        (band, channel, ht_mode, compatible) = band_channel_ht_mode
        log.info(f"band:{band}, channel:{channel}, ht_mode:{ht_mode}, compatible:{compatible}")
        assert default_gen._check_band_channel_compatible(band, channel, "gw", ht_mode) == compatible

    @allure.title("Validate _check_ht_mode_band_support() method ")
    def test__check_ht_mode_band_support(self, default_gen, band_max_ht_mode):
        (band, ht_mode, compatible) = band_max_ht_mode
        log.info(f"band:{band}, ht_mode:{ht_mode}, compatible:{compatible}")
        assert default_gen._check_ht_mode_band_support(band, ht_mode) == compatible

    @allure.title("Validate _parse_fut_opts() method for all custom flags")
    def test__parse_fut_opts(self, default_gen, generic_inputs, fut_option):
        inputs = generic_inputs
        args_mapping = ["kconfig", "service"]
        single_input = ["KC_1", "serv_1"]
        cfg = dict(zip(args_mapping, single_input))
        message = f"{fut_option.upper()}: Uncommented {fut_option.upper()}"
        inputs[fut_option] = [{"inputs": [single_input]}]
        log.info(f"inputs:{inputs}")
        expected = {
            **cfg,
            f"{fut_option}": True,
            f"{fut_option}_msg": message,
        }
        log.info(f"expected:{expected}")
        actual = default_gen._parse_fut_opts(inputs, single_input=single_input, cfg=cfg)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _parse_fut_opts() method for the 'ignore' custom flag")
    def test__parse_fut_opts_ignore(self, default_gen, generic_inputs):
        fut_option = "ignore"
        inputs = generic_inputs
        args_mapping = ["kconfig", "service"]
        single_input = ["KC_1", "serv_1"]
        cfg = dict(zip(args_mapping, single_input))
        inputs[fut_option] = [{"inputs": [single_input]}]
        log.info(f"inputs:{inputs}")
        expected = None
        log.info(f"expected:{expected}")
        actual = default_gen._parse_fut_opts(inputs, single_input=single_input, cfg=cfg)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _parse_fut_opts() method with option message")
    def test__parse_fut_opts_with_msg(self, default_gen, generic_inputs, fut_option):
        inputs = generic_inputs
        args_mapping = ["kconfig", "service"]
        single_input = ["KC_1", "serv_1"]
        cfg = dict(zip(args_mapping, single_input))
        message = f"test message for {fut_option} option"
        inputs[fut_option] = [{"inputs": [single_input], "msg": message}]
        log.info(f"inputs:{inputs}")
        expected = {
            **cfg,
            f"{fut_option}": True,
            f"{fut_option}_msg": message,
        }
        log.info(f"expected:{expected}")
        actual = default_gen._parse_fut_opts(inputs, single_input=single_input, cfg=cfg)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _parse_fut_opts() method when there are no added options")
    def test__parse_fut_opts_no_opts(self, default_gen, generic_inputs):
        inputs = generic_inputs
        log.info(f"inputs:{inputs}")
        args_mapping = ["kconfig", "service"]
        single_input = ["KC_1", "serv_1"]
        cfg = dict(zip(args_mapping, single_input))
        expected = {**cfg}
        log.info(f"expected:{expected}")
        # Content of inputs and single-input is irrelevant if inputs does not have added options, it simply returns cfg
        actual = default_gen._parse_fut_opts(inputs, cfg=cfg)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _parse_fut_opts() method with empty inputs and cfg parameters")
    def test__parse_fut_opts_empty_inputs_empty_cfg(self, default_gen, fut_option):
        message = f"test message for {fut_option} option"
        inputs = {fut_option: {"msg": message}}
        log.info(f"inputs:{inputs}")
        cfg = {}
        expected = {f"{fut_option}": True, f"{fut_option}_msg": message}
        log.info(f"expected:{expected}")
        actual = default_gen._parse_fut_opts(inputs, cfg=cfg)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method with generic_inputs")
    def test__do_args_mapping_generic_inputs(self, default_gen, generic_inputs):
        inputs = generic_inputs
        log.info(f"inputs:{inputs}")
        # Always copy, as the method may alter arguments
        expected = deepcopy(inputs)
        expected["inputs"] = [dict(zip(expected["args_mapping"], single_input)) for single_input in inputs["inputs"]]
        log.info(f"expected:{expected}")
        actual = default_gen._do_args_mapping(inputs)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method when there is no inputs key")
    def test__do_args_mapping_no_inputs_key(self, default_gen, generic_inputs):
        inputs = generic_inputs
        del inputs["inputs"]
        log.info(f"inputs:{inputs}")
        with pytest.raises(KeyError):
            default_gen._do_args_mapping(inputs)

    @allure.title("Validate _do_args_mapping() method")
    def test__do_args_mapping_no_args_mapping_key(self, default_gen, generic_inputs):
        inputs = generic_inputs
        # Always copy, as the method may alter arguments
        expected = deepcopy(inputs)
        del inputs["args_mapping"]
        log.info(f"inputs:{inputs}")
        del expected["args_mapping"]
        expected["inputs"] = []
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
        log.info(f"expected:{expected}")
        actual = default_gen._do_args_mapping(inputs)
        log.info(f"actual:{actual}")
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method when args_mapping has the key radio_band but not encryption")
    def test__do_args_mapping_get_encryption(self, default_gen, generic_inputs, radio_band):
        gw_phy_radio_name = default_gen.gw_capabilities.get("interfaces.phy_radio_name")
        inputs = generic_inputs
        inputs["args_mapping"].append("radio_band")
        [single_input.append(radio_band) for single_input in inputs["inputs"]]
        log.info(f"inputs:{inputs}")
        # Always copy, as the method may alter arguments
        expected = deepcopy(inputs)
        expected["args_mapping"].append("encryption")
        encryption = "WPA3" if radio_band == "6g" else "WPA2"
        [single_input.append(encryption) for single_input in expected["inputs"]]
        if gw_phy_radio_name[radio_band]:
            expected["inputs"] = [
                dict(zip(expected["args_mapping"], single_input)) for single_input in expected["inputs"]
            ]
        else:
            expected["inputs"] = []
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
