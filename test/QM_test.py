import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
qm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def qm_setup():
    test_class_name = ["TestQm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for QM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            device_handler.fut_device_setup(test_suite_name="qm")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestQm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", qm_config.get("qm_telog_validate", []))
    def test_qm_telog_validate(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            number_of_logs = cfg.get("number_of_logs")
            log_tail_command = gw._get_log_tail_command()
            test_args = gw.get_command_arguments(number_of_logs, log_tail_command)

        with step("Test case"):
            assert gw.execute_with_logging("tests/qm/qm_telog_validate", test_args)[0] == ExpectedShellResult
