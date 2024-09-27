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
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "PM" not in node_handler.get_kconfig_managers():
            pytest.skip("PM not present on device")
        node_handler.fut_device_setup(test_suite_name="pm")
        service_status = node_handler.get_node_services_and_status()
        if service_status["pm"]["status"] != "enabled":
            pytest.skip("PM not enabled on device")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestPm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", pm_config.get("pm_verify_log_severity", []))
    def test_pm_verify_log_severity(self, cfg: dict):
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
    def test_pm_trigger_cloud_logpull(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            test_args = gw.get_command_arguments(
                cfg.get("upload_location"),
                cfg.get("upload_token"),
                cfg.get("name"),
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/pm/pm_trigger_cloud_logpull", test_args)[0] == ExpectedShellResult
