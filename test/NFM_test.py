import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
nfm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def nfm_setup():
    test_class_name = ["TestNfm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for NFM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            device_handler.fut_device_setup(test_suite_name="nfm")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestNfm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nfm_config.get("nfm_native_ebtable_check", []))
    def test_nfm_native_ebtable_check(self, cfg):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            name = cfg.get("name")
            chain_name = cfg.get("chain_name")
            table_name = cfg.get("table_name")
            rule = cfg.get("rule")
            target = cfg.get("target")
            priority = cfg.get("priority")
            update_target = cfg.get("update_target")
            test_args = gw.get_command_arguments(
                name,
                chain_name,
                table_name,
                rule,
                target,
                priority,
                update_target,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nfm/nfm_native_ebtable_check", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nfm_config.get("nfm_native_ebtable_template_check", []))
    def test_nfm_native_ebtable_template_check(self, cfg):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            name = cfg.get("name")
            chain_name = cfg.get("chain_name")
            table_name = cfg.get("table_name")
            target = cfg.get("target")
            priority = cfg.get("priority")
            update_target = cfg.get("update_target")
            test_args = gw.get_command_arguments(
                name,
                chain_name,
                table_name,
                target,
                priority,
                update_target,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nfm/nfm_native_ebtable_template_check", test_args)[0]
                == ExpectedShellResult
            )
