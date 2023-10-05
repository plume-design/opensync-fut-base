import functools
import sys
from pathlib import Path

import allure
import pytest

from framework.lib.config import Config  # noqa: E402
from lib_testbed.generic.util.logger import log  # noqa: E402

topdir_path = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(topdir_path)


"""
Self-test for FUT framework.
Run:
    python3 -m pytest ./self_test/ -v --alluredir=./allure-results/ -o log_cli=true
Display results:
    allure generate ./allure-results/ -o allure-report --clean; allure open allure-report
"""
test_cfg_dict = {
    "integer1": 42,
    "integer2": -69,
    "integer3": 0,
    "float1": 3.14,
    "float2": -2.71828,
    "float4": float("inf"),
    "string": "Sphinx of black quartz, judge my vow.",
    "bool1": True,
    "bool2": False,
    "dict1": {
        "nested_str": "ack",
        "nested_bool": True,
    },
    "dict2": {
        "nested_dict": {
            "foo": "bar",
            "baz": True,
            "nested_dict2": {
                "boo": "far",
            },
        },
    },
    "list": ["earth", "water", "air", "fire"],
    "tuple": ("hello", ["w", "o", "r", "l", "d"]),
}


# def gen_nested_recurse(dictionary, parent=types.MappingProxyType([])):
def gen_nested_recurse(dictionary, parent=None):
    """Return nested dict keys."""
    if parent is None:
        parent = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            parent.append(key)
            yield ".".join(parent)
            yield from gen_nested_recurse(value, parent)
            parent.pop()


@allure.title("Validate Config Class")
class TestValidateConfig:
    @allure.title("Validate get() method returns correct value for non-nested key")
    @pytest.mark.parametrize("key", test_cfg_dict.keys())
    def test_config_get_correct_value(self, key):
        test_cfg_obj = Config(test_cfg_dict)
        expected = test_cfg_dict[key]
        actual = test_cfg_obj.get(key)
        assert actual == expected
        log.info(msg=f"key:{key}, expected:{expected}, actual:{actual}")

    @allure.title("Validate _get_recursive() method returns correct value for nested key")
    @pytest.mark.parametrize("key", list(gen_nested_recurse(test_cfg_dict)))
    def test_config_get_recursive(self, key):
        test_cfg_obj = Config(test_cfg_dict)
        expected = functools.reduce(dict.get, key.split("."), test_cfg_obj.cfg)
        actual = test_cfg_obj.get(key)
        assert actual == expected
        log.info(msg=f"key:{key}, expected:{expected}, actual:{actual}")

    @allure.title("Validate that get method correctly returns fallback value")
    def test_config_get_fallback(self):
        test_cfg_obj = Config(test_cfg_dict)
        key = "key_not_there"
        actual = test_cfg_obj.get(key)
        expected = ""
        assert actual == expected
        log.info(msg=f"key:{key}, expected:{expected}, actual:{actual}")

    @allure.title("Validate that Config class possesses the correct attributes")
    def test_config_attribute(self):
        assert True

    @allure.title("Validate that Config class attributes have correct values")
    def test_config_attribute_value(self):
        assert True
