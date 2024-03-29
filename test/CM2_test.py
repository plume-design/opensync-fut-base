import time

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
cm2_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def cm2_setup():
    test_class_name = ["TestCm2"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for CM2: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            device_wan_iface = device_handler.capabilities.get_primary_wan_iface()
            device_wan_bridge = device_handler.capabilities.get_wan_bridge_ifname()
            setup_args = device_handler.get_command_arguments(device_wan_iface, device_wan_bridge)
            device_handler.fut_device_setup(test_suite_name="cm2", setup_args=setup_args)
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestCm2:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_ble_status_cloud_down", []))
    def test_cm2_ble_status_cloud_down(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            controller_ip = gw.execute_with_logging("tools/device/get_connected_cloud_controller_ip")
            if controller_ip[0] != ExpectedShellResult or controller_ip[1] == "" or controller_ip[1] is None:
                raise RuntimeError("Failed to retrieve IP address of Cloud controller")
            redirector_hostname = gw.execute_with_logging("tools/device/get_redirector_hostname")
            if (
                redirector_hostname[0] != ExpectedShellResult
                or redirector_hostname[1] == ""
                or redirector_hostname[1] is None
            ):
                raise RuntimeError("Failed to retrieve hostname of the redirector")

            cloud_recovered_args = gw.get_command_arguments(
                "cloud_recovered",
            )
            cloud_blocked_args = gw.get_command_arguments(
                "cloud_down",
            )
            cloud_block_args = gw.get_command_arguments(
                redirector_hostname[1],
                controller_ip[1],
                "block",
            )
            cloud_unblock_args = gw.get_command_arguments(
                redirector_hostname[1],
                controller_ip[1],
                "unblock",
            )

        try:
            with step("Test Case"):
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_ble_status_cloud_down", cloud_recovered_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_block_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_ble_status_cloud_down", cloud_blocked_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_unblock_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_ble_status_cloud_down", cloud_recovered_args)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                server.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_unblock_args, as_sudo=True)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_ble_status_internet_block", []))
    def test_cm2_ble_status_internet_block(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            gw_wan_inet_addr = server.wan_ip_dict.get("gw")

            internet_blocked_args = gw.get_command_arguments("internet_blocked")
            internet_recovered_args = gw.get_command_arguments("internet_recovered")
            cloud_block_args = gw.get_command_arguments(gw_wan_inet_addr, "block")
            cloud_unblock_args = gw.get_command_arguments(gw_wan_inet_addr, "unblock")

        try:
            with step("Test Case"):
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_ble_status_internet_block", internet_recovered_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/address_internet_man", cloud_block_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                time.sleep(3)
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_ble_status_internet_block", internet_blocked_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/address_internet_man", cloud_unblock_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_ble_status_internet_block", internet_recovered_args)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                assert server.restart_cloud()
                server.execute("tools/server/cm/address_internet_man", cloud_unblock_args, as_sudo=True)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_cloud_down", []))
    def test_cm2_cloud_down(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            gw_wan_iface = gw.capabilities.get_primary_wan_iface()
            controller_ip = gw.execute_with_logging("tools/device/get_connected_cloud_controller_ip")
            if controller_ip[0] != ExpectedShellResult or controller_ip[1] == "" or controller_ip[1] is None:
                RuntimeError("Failed to retrieve IP address of Cloud controller")
            redirector_hostname = gw.execute_with_logging("tools/device/get_redirector_hostname")
            if (
                redirector_hostname[0] != ExpectedShellResult
                or redirector_hostname[1] == ""
                or redirector_hostname[1] is None
            ):
                raise RuntimeError("Failed to retrieve hostname of the redirector")

            counter = cfg.get("unreachable_cloud_counter")

            cloud_recovered_args = gw.get_command_arguments(
                gw_wan_iface,
                "0",
                "cloud_recovered",
            )
            cloud_check_counter_args = gw.get_command_arguments(
                gw_wan_iface,
                counter,
                "check_counter",
            )
            cloud_block_args = gw.get_command_arguments(
                redirector_hostname[1],
                controller_ip[1],
                "block",
            )
            cloud_unblock_args = gw.get_command_arguments(
                redirector_hostname[1],
                controller_ip[1],
                "unblock",
            )

        try:
            with step("Test Case"):
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_cloud_down", cloud_recovered_args)[0] == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_block_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_cloud_down", cloud_check_counter_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_unblock_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_cloud_down", cloud_recovered_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                server.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_unblock_args, as_sudo=True)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_dns_failure", []))
    def test_cm2_dns_failure(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            gw_wan_inet_addr = server.wan_ip_dict.get("gw")
            dns_blocked_args = gw.get_command_arguments("dns_blocked")
            dns_unblocked_args = gw.get_command_arguments("dns_recovered")
            gw_wan_inet_addr_blocked = gw.get_command_arguments(gw_wan_inet_addr, "block")
            gw_wan_inet_addr_unblocked = gw.get_command_arguments(gw_wan_inet_addr, "unblock")

        try:
            with step("Test Case"):
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_dns_failure", dns_unblocked_args)[0] == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/address_dns_man", gw_wan_inet_addr_blocked, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert gw.execute_with_logging("tests/cm2/cm2_dns_failure", dns_blocked_args)[0] == ExpectedShellResult
                assert (
                    server.execute("tools/server/cm/address_dns_man", gw_wan_inet_addr_unblocked, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_dns_failure", dns_unblocked_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                assert (
                    server.execute("tools/server/cm/address_dns_man", gw_wan_inet_addr_unblocked, as_sudo=True)[0]
                    == ExpectedShellResult
                )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_internet_lost", []))
    def test_cm2_internet_lost(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            gw_wan_inet_addr = server.wan_ip_dict.get("gw")
            gw_wan_iface = gw.capabilities.get_primary_wan_iface()
            counter = cfg.get("unreachable_internet_counter")
            internet_blocked_args = gw.get_command_arguments(gw_wan_iface, counter, "check_counter")
            internet_recovered_args = gw.get_command_arguments(gw_wan_iface, "0", "internet_recovered")
            cloud_block_args = gw.get_command_arguments(gw_wan_inet_addr, "block")
            cloud_unblock_args = gw.get_command_arguments(gw_wan_inet_addr, "unblock")

        try:
            with step("Test Case"):
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_internet_lost", internet_recovered_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/address_internet_man", cloud_block_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                time.sleep(3)
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_internet_lost", internet_blocked_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/cm/address_internet_man", cloud_unblock_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                time.sleep(3)
                assert (
                    gw.execute_with_logging("tests/cm2/cm2_internet_lost", internet_recovered_args)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                assert server.restart_cloud()
                server.execute("tools/server/cm/address_internet_man", cloud_unblock_args, as_sudo=True)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_link_lost", []))
    def test_cm2_link_lost(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            gw_wan_iface = gw.capabilities.get_primary_wan_iface()
            test_args = gw.get_command_arguments(gw_wan_iface)

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cm2/cm2_link_lost", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cm2_config.get("cm2_ssl_check", []))
    def test_cm2_ssl_check(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cm2/cm2_ssl_check")[0] == ExpectedShellResult
