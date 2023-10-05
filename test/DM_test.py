from time import sleep

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.rpower.rpower_tool import PowerControllerTool
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
dm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def dm_setup():
    test_class_name = ["TestDm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for DM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            phy_radio_ifnames = device_handler.capabilities.get_phy_radio_ifnames(return_type=list)
            setup_args = device_handler.get_command_arguments(*phy_radio_ifnames)
            device_handler.fut_device_setup(test_suite_name="dm", setup_args=setup_args)
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestDm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_awlan_node_params", []))
    def test_dm_verify_awlan_node_params(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            awlan_field_name = cfg.get("awlan_field_name")
            awlan_field_val = cfg.get("awlan_field_val")
            test_args = gw.get_command_arguments(
                awlan_field_name,
                awlan_field_val,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/dm_verify_awlan_node_params", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_count_reboot_status", []))
    def test_dm_verify_count_reboot_status(self, cfg):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/dm_verify_count_reboot_status")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_counter_inc_reboot_status", []))
    def test_dm_verify_counter_inc_reboot_status(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            device_reboot_timeout = gw.capabilities.get_boot_time_kpi()

            if not isinstance(device_reboot_timeout, int):
                log.warning("Unable to acquire device boot time. Will use default time of 120 seconds.")

        try:
            with step("Reboot GW"):
                count_before_reboot = gw.execute("tools/device/get_count_reboot_status")
                gw.device_api.reboot()
            with step("Wait for GW after reboot"):
                # Hardcoded sleep to allow devices to actually trigger reboot. Do not optimize.
                sleep(20)
                gw.device_api.lib.wait_available(timeout=max(device_reboot_timeout, 120))
                count_after_reboot = gw.execute("tools/device/get_count_reboot_status")
            with step("Test case"):
                test_args = gw.get_command_arguments(
                    count_before_reboot[1],
                    count_after_reboot[1],
                )
                assert (
                    gw.execute_with_logging("tests/dm/dm_verify_counter_inc_reboot_status", test_args)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Wait for GW after reboot"):
                gw.device_api.lib.wait_available(timeout=max(device_reboot_timeout, 120))

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_device_mode_awlan_node", []))
    def test_dm_verify_device_mode_awlan_node(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            device_mode = cfg.get("device_mode")
            test_args = gw.get_command_arguments(
                device_mode,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/dm/dm_verify_device_mode_awlan_node", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_enable_node_services", []))
    def test_dm_verify_enable_node_services(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            service = cfg.get("service")
            kconfig_val = cfg.get("kconfig_val")
            test_args = gw.get_command_arguments(
                service,
                kconfig_val,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/dm/dm_verify_enable_node_services", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_node_services", []))
    def test_dm_verify_node_services(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            service = cfg.get("service")
            kconfig_val = cfg.get("kconfig_val")
            test_args = gw.get_command_arguments(
                service,
                kconfig_val,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/dm_verify_node_services", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_opensync_version_awlan_node", []))
    def test_dm_verify_opensync_version_awlan_node(self, cfg):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/dm_verify_opensync_version_awlan_node")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_reboot_file_exists", []))
    def test_dm_verify_reboot_file_exists(self, cfg):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/dm/dm_verify_reboot_file_exists")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", dm_config.get("dm_verify_reboot_reason", []))
    def test_dm_verify_reboot_reason(self, cfg):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            opensync_rootdir = gw.capabilities.get_opensync_rootdir()
            device_reboot_timeout = gw.capabilities.get_boot_time_kpi()

            if not isinstance(device_reboot_timeout, int):
                raise RuntimeError("Unable to acquire device boot time.")

            # Arguments from test case configuration
            reboot_reason = cfg.get("reboot_reason")

            test_args_base = [
                reboot_reason,
            ]

            if reboot_reason == "COLD_BOOT":
                rpower_tool = PowerControllerTool(fut_configurator.testbed_cfg, device_names="gw")
            elif reboot_reason == "CLOUD":
                test_args_base += [
                    opensync_rootdir,
                ]

            test_args = gw.get_command_arguments(*test_args_base)

        try:
            with step("Verify GW capability to record reboot reason"):
                if not gw.execute("tools/device/check_reboot_file_exists")[0] == ExpectedShellResult:
                    pytest.skip("Reboot file does not exist, skipping dm_verify_reboot_reason test case.")
            with step("Reboot GW"):
                if reboot_reason == "COLD_BOOT":
                    rpower_tool.cycle(timeout=15)
                else:
                    assert gw.execute("tools/device/reboot_dut_w_reason", test_args)[0] == ExpectedShellResult
                    # Hardcoded sleep to allow devices to actually trigger reboot. Do not optimize
                    sleep(20)
            with step("Wait for GW after reboot"):
                gw.device_api.lib.wait_available(timeout=device_reboot_timeout)
                # Allows device to recover after reboot
                sleep(10)
            with step("Test case"):
                assert gw.execute_with_logging("tests/dm/dm_verify_reboot_reason", test_args)[0] == ExpectedShellResult
        finally:
            with step("Wait for GW after reboot"):
                gw.device_api.lib.wait_available(timeout=max(device_reboot_timeout, 120))
