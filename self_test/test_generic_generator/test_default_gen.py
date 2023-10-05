import sys
from pathlib import Path

import allure
import pytest

from framework.generators import DefaultGen
from framework.generators.DefaultGen import generator_names
from framework.generators.fut_gen import FutTestConfigGenClass

sys.path.append("../../../")


@pytest.fixture(params=["WPA2", "WPA3"])  # WPA-PERSONAL?
def encryption(request):
    return request.param


@pytest.fixture(
    params=[
        "BCM947622DVT",
        "BCM947622DVTCH6",
        "MR8300-EXT",
        "PP203X",
        "PP403Z",
        "PP443Z",
        "PP603X",
    ],
)
def device_dut(request):
    return request.param


@pytest.fixture(params=["PP203X", "PP403Z", "PP443Z", "PP603X"])
def device_leaf(request):
    return request.param


@pytest.fixture(params=["skip", "xfail"])
def fut_option(request):
    return request.param


def default_gen_instance(device_dut, device_leaf):
    return FutTestConfigGenClass(device_dut, device_leaf).test_generators


class MockResponse:
    @staticmethod
    def values():
        return ["value_1", "value_2", "11ax"]


@allure.title("Validate DefaultGenClass")
class TestDefaultGenClass:
    @allure.title("Validate _check_encryption_compatible() method")
    def test_check_encryption_compatible(self, monkeypatch, encryption):
        def mock_get(*args, **kwargs):
            return MockResponse()

        default_gen = default_gen_instance("PP603X", "PP203X")
        monkeypatch.setattr(default_gen.gw_capabilities, "get", mock_get)

        assert default_gen._check_encryption_compatible(encryption)

    @allure.title("Validate generator modules are collected")
    def test_generator_names_collected(self):
        generators_dir = "framework/generators"
        file_path = Path(__file__).absolute().parents[2].joinpath(generators_dir)
        generators = [f.stem for f in file_path.iterdir() if not f.is_dir()]
        actual = generator_names
        for generator in generators:
            if generator in ["__init__", "DefaultGen", "TemplateGen", "BadGenerator"]:
                assert generator not in actual
            else:
                assert generator in actual

    @allure.title("Validate _get_default_options() method.")
    def test_get_default_options(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {"default": "default_value_1", "key": "value"}
        assert default_gen._get_default_options(inputs=inputs) == "default_value_1"

    @allure.title("Validate _get_default_options() method for empty dict.")
    def test_get_default_options_no_default(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        assert default_gen._get_default_options(inputs={}) == {}

    @allure.title("Validate _check_band_compatible() method.")
    def test_check_band_compatible(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        assert default_gen._check_band_compatible("24g", "gw")
        assert not default_gen._check_band_compatible("9g", "gw")

    @allure.title("Validate _check_band_channel_compatible() method.")
    def test_check_band_channel_compatible(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return str([36, 40, 44, 48, 52, 56, 60, 64, 100])

        def mock_reg_check(*args, **kwargs):
            return True

        default_gen = default_gen_instance("PP603X", "PP203X")
        monkeypatch.setattr(default_gen.gw_capabilities, "get", mock_get)
        monkeypatch.setattr(DefaultGen, "validate_channel_ht_mode_band", mock_reg_check)

        assert default_gen._check_band_channel_compatible("5g", "44", "gw")

    @allure.title("Validate _check_band_channel_compatible() method.")
    def test_check_band_channel_compatible_no_channels(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return ""

        default_gen = default_gen_instance("PP603X", "PP203X")
        monkeypatch.setattr(default_gen.gw_capabilities, "get", mock_get)

        assert not default_gen._check_band_channel_compatible("5g", "44", "gw")

    @allure.title("Validate _check_ht_mode_band_support() method ")
    def test_check_ht_mode_band_support(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        radio_band = "24g"
        ht_mode = "HT40"
        assert default_gen._check_ht_mode_band_support(radio_band, ht_mode)

    @allure.title("Validate _check_ht_mode_band_support() method ")
    def test_check_ht_mode_band_support_bad_radio(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        radio_band = "12g"
        ht_mode = "HT40"
        assert not default_gen._check_ht_mode_band_support(radio_band, ht_mode)

    @allure.title("Validate _check_ht_mode_band_support() method ")
    def test_check_ht_mode_band_support_bad_ht_mode(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        radio_band = "24g"
        ht_mode = "HT42"
        assert not default_gen._check_ht_mode_band_support(radio_band, ht_mode)

    @allure.title("Validate _check_ht_mode_band_support() method ")
    def test_check_ht_mode_band_support_exception(self):
        with pytest.raises(Exception):
            default_gen = default_gen_instance("PP603X", "PP203X")
            radio_band = "24g"
            ht_mode = "HT40"
            assert not default_gen._check_ht_mode_band_support(radio_band, ht_mode)

    @allure.title("Validate _parse_fut_opts() method")
    def test_parse_fut_opts(self, fut_option):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["kconfig", "service"],
            "inputs": [
                ["KC_1", "serv_1"],
                ["KC_2", "serv_2"],
            ],
            fut_option: [{"input": ["KC_1", "serv_1"]}],
        }
        i = ["KC_1", "serv_1"]
        cfg = {"kconfig": "KC_1", "service": "serv_1"}

        expected = {
            "kconfig": "KC_1",
            "service": "serv_1",
            f"{fut_option}": True,
            f"{fut_option}_msg": f"{fut_option.upper()}: Uncommented {fut_option.upper()}",
        }
        actual = default_gen._parse_fut_opts(inputs, i=i, cfg=cfg)
        assert actual == expected

    @allure.title("Validate _parse_fut_opts() method")
    def test_parse_fut_opts_with_msg(self, fut_option):
        default_gen = default_gen_instance("PP603X", "PP203X")
        message = "Ignore this test"
        inputs = {
            "args_mapping": ["kconfig", "service"],
            "inputs": [
                ["KC_1", "serv_1"],
                ["KC_2", "serv_2"],
            ],
            fut_option: [{"input": ["KC_1", "serv_1"], "msg": message}],
        }
        i = ["KC_1", "serv_1"]
        cfg = {"kconfig": "KC_1", "service": "serv_1"}

        expected = {
            "kconfig": "KC_1",
            "service": "serv_1",
            f"{fut_option}": True,
            f"{fut_option}_msg": message,
        }
        actual = default_gen._parse_fut_opts(inputs, i=i, cfg=cfg)
        assert actual == expected

    @allure.title("Validate _parse_fut_opts() method")
    def test_parse_fut_opts_no_opts(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["kconfig", "service"],
            "inputs": [
                ["KC_1", "serv_1"],
                ["KC_2", "serv_2"],
            ],
        }
        i = ["KC_1", "serv_1"]
        cfg = {"kconfig": "KC_1", "service": "serv_1"}
        actual = default_gen._parse_fut_opts(inputs, i=i, cfg=cfg)
        assert actual == cfg

    @allure.title("Validate _parse_fut_opts() method")
    def test_parse_fut_opts_empty_inputs(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {"inputs": [{}]}
        i = None
        cfg = None
        assert default_gen._parse_fut_opts(inputs, i=i, cfg=cfg) == cfg

    @allure.title("Validate _parse_fut_opts() method")
    def test_parse_fut_opts_empty_inputs_empyt_cfg(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {"inputs": [{}]}
        i = None
        cfg = {}
        assert default_gen._parse_fut_opts(inputs, i=i, cfg=cfg) == cfg

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_empty_inputs(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {"inputs": [{}]}
        assert default_gen._do_args_mapping(inputs) == inputs

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_no_inputs_key(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["kconfig", "service"],
            "values": [
                ["KC_1", "serv_1"],
                ["KC_2", "serv_2"],
            ],
        }
        assert default_gen._do_args_mapping(inputs) == inputs

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_empty_inputs_value(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["kconfig", "service"],
            "inputs": [],
        }
        assert default_gen._do_args_mapping(inputs) == inputs

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_string_value_in_inputs(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["arg"],
            "inputs": ["foo"],
        }
        actual = default_gen._do_args_mapping(inputs)
        expected = {
            "args_mapping": ["arg"],
            "inputs": [{"arg": "foo"}],
        }
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_int_value_in_inputs(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["arg"],
            "inputs": [42],
        }
        actual = default_gen._do_args_mapping(inputs)
        expected = {"args_mapping": ["arg"], "inputs": [{"arg": 42}]}
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_no_args_mapping_key(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "not_args_mapping": ["args"],
            "inputs": [42],
        }
        actual = default_gen._do_args_mapping(inputs)
        expected = {
            "not_args_mapping": ["args"],
            "inputs": [{}],
        }
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_encryption_compatible(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["some_key", "encryption"],
            "inputs": [["some_value", "WPA2"]],
        }
        expected = {
            "args_mapping": ["some_key", "encryption"],
            "inputs": [
                {
                    "some_key": "some_value",
                    "encryption": "WPA2",
                },
            ],
        }
        actual = default_gen._do_args_mapping(inputs)
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_encryption_incompatible(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["some_key", "encryption"],
            "inputs": [["some_value", "WPA42"]],
        }
        expected = {
            "args_mapping": ["some_key", "encryption"],
            "inputs": [],
        }
        actual = default_gen._do_args_mapping(inputs)
        assert actual == expected

    @allure.title("validate _do_args_mapping() method")
    def test_do_args_mapping_radio_band_compatible(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["some_key", "radio_band"],
            "inputs": [["some_value", "24g"]],
        }
        expected = {
            "args_mapping": ["some_key", "radio_band"],
            "inputs": [
                {
                    "some_key": "some_value",
                    "radio_band": "24g",
                },
            ],
        }
        actual = default_gen._do_args_mapping(inputs)
        assert actual == expected

    @allure.title("Validate _do_args_mapping() method")
    def test_do_args_mapping_radio_band_incompatible(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = {
            "args_mapping": ["some_key", "encryption", "radio_band"],
            "inputs": [["some_value", "WPA3", "42g"]],
        }
        expected = {
            "args_mapping": ["some_key", "encryption", "radio_band"],
            "inputs": [],
        }
        actual = default_gen._do_args_mapping(inputs)
        assert actual == expected

    @allure.title("Validate default_gen() method")
    def test_default_gen_empty_inputs_list(self):
        default_gen = default_gen_instance("PP603X", "PP203X")
        inputs = []
        assert default_gen.default_gen(inputs) == inputs
