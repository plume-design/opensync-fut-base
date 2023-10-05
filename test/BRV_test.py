import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
brv_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def brv_setup():
    test_class_name = ["TestBrv"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for BRV: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            device_handler.fut_device_setup(test_suite_name="dm")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestBrv:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", brv_config.get("brv_busybox_builtins", []))
    def test_brv_busybox_builtins(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            busybox_builtin = cfg.get("busybox_builtin")
            test_args = gw.get_command_arguments(busybox_builtin)

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/brv_busybox_builtins", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", brv_config.get("brv_is_bcm_license_on_system_fut", []))
    def test_brv_is_bcm_license_on_system_fut(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            license = cfg.get("license")
            service = cfg.get("service")
            test_args = gw.get_command_arguments(
                f"{license}",
                f"'{service}'",
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/brv_is_bcm_license_on_system", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", brv_config.get("brv_is_script_on_system_fut", []))
    def test_brv_is_script_on_system_fut(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            system_script = cfg.get("system_script")
            test_args = gw.get_command_arguments(system_script)

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/brv_is_script_on_system", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "cfg",
        brv_config.get("brv_is_tool_on_system_fut", [])
        + brv_config.get("brv_is_tool_on_system_native_bridge", [])
        + brv_config.get("brv_is_tool_on_system_ovs_bridge", []),
    )
    def test_brv_is_tool_on_system_fut(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            system_tool = cfg.get("system_tool")
            test_args = gw.get_command_arguments(system_tool)

        with step("Check bridge type"):
            bridge_type = gw.get_bridge_type()
            only_ovs_supported_list = [
                item["system_tool"] for item in brv_config.get("brv_is_tool_on_system_ovs_bridge")
            ]
            only_native_supported_list = [
                item["system_tool"] for item in brv_config.get("brv_is_tool_on_system_native_bridge")
            ]

            if (bridge_type == "native_bridge" and system_tool in only_ovs_supported_list) or (
                bridge_type == "ovs_bridge" and system_tool in only_native_supported_list
            ):
                pytest.skip(f"Tool {system_tool} not supported with {bridge_type} bridge type, skipping the test.")

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/brv_is_tool_on_system", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", brv_config.get("brv_is_tool_on_system_opensync", []))
    def test_brv_is_tool_on_system_opensync(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            system_tool = cfg.get("system_tool")
            test_args = gw.get_command_arguments(system_tool)

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/brv_is_tool_on_system", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", brv_config.get("brv_ovs_check_version", []))
    def test_brv_ovs_check_version(self, cfg):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "ovs_bridge":
                pytest.skip(
                    "Test is not applicable when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/brv_ovs_check_version")[0] == ExpectedShellResult
