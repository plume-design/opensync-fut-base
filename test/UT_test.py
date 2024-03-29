from pathlib import Path

import allure
import pytest

from config.defaults import unit_test_resource_dir, unit_test_subdir
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log

ExpectedShellResult = pytest.expected_shell_result


@pytest.fixture(scope="class", autouse=True)
def ut_setup():
    test_class_name = ["TestUt"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for UT: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            device_handler.fut_device_setup(test_suite_name="ut")
        except FileNotFoundError as exception:
            log.warning(f"Unable to transfer unit tests: {exception}.")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    _ut_transfer_files(device_handler)
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


def _ut_transfer_files(node_handler):
    transfer_dir = Path(unit_test_resource_dir).joinpath(unit_test_subdir)
    if not transfer_dir.is_dir():
        raise FileNotFoundError(f"Can not transfer {transfer_dir} to {node_handler.name}, directory does not exist.")
    log.debug(f"Transfer {transfer_dir} to {node_handler.name}.")
    node_handler.file_transfer(folders=[transfer_dir], as_sudo=False, skip_env_file=True)


class TestUt:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.no_process_restart_detection
    @pytest.mark.parametrize("cfg", getattr(pytest, "unit_test_files", []))
    def test_device_unit_test(self, cfg: dict):
        gw = pytest.gw
        with step("Preparation of testcase parameters"):
            unit_test_file = cfg.get("unit_test_file")
        with step("Test case"):
            assert (
                gw.execute(Path(unit_test_file).name, suffix="", folder=Path(unit_test_file).parent)[0]
                == ExpectedShellResult
            )
