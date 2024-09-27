import allure
import pytest

from framework import device_handler
from lib_testbed.generic.util.logger import log

device_handler_object = device_handler.DeviceHandler("gw")

sanitize_test_string_list = [
    "test string",
    "teststring",
    "'foo'",
    '"bar"',
    "-opt",
    "'-opt'",
    '"-opt"',
    "'f oo'",
    '"b ar"',
    "-o pt",
    "'-o pt'",
    '"-o pt"',
]
sanitized_test_string_list = [f'"{sanitize_test_string_list[0]}"'] + sanitize_test_string_list[1:]


@pytest.fixture(params=zip(sanitize_test_string_list, sanitized_test_string_list))
def sanitize_test_strings(request):
    return request.param


@allure.title("Validate DeviceHandler class")
class TestDeviceHandler:
    @allure.title("Validate sanitize_arg method")
    def test_sanitize_arg(self, sanitize_test_strings):
        test_string, expected = sanitize_test_strings
        log.info(f"test_string:{test_string}")
        log.info(f"expected:{expected}")
        actual = device_handler_object.sanitize_arg(test_string)
        log.info(f"actual:{actual}")
        assert actual == expected
