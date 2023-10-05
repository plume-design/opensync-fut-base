import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
pm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def pm_setup():
    test_class_name = ["TestPm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for PM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            device_handler.fut_device_setup(test_suite_name="pm")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestPm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", pm_config.get("pm_verify_log_severity", []))
    def test_pm_verify_log_severity(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            test_args = gw.get_command_arguments(
                cfg.get("name"),
                cfg.get("log_severity"),
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/pm/pm_verify_log_severity", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", pm_config.get("pm_trigger_cloud_logpull", []))
    def test_pm_trigger_cloud_logpull(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            test_args = gw.get_command_arguments(
                cfg.get("upload_location"),
                cfg.get("upload_token"),
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/pm/pm_trigger_cloud_logpull", test_args)[0] == ExpectedShellResult
