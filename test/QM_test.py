import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices
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


class TestQm:
    log.debug("The QM suite is not implemented.")
    pass
