import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
vpnm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def vpnm_setup():
    test_class_name = ["TestVpnm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for VPNM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            if device_handler.name == "gw":
                check_kconfig_args = device_handler.get_command_arguments("CONFIG_MANAGER_VPNM", "y")
                check_kconfig_ec = device_handler.execute("tools/device/check_kconfig_option", check_kconfig_args)[0]
                if check_kconfig_ec != 0:
                    pytest.skip("VPNM not present on device")
            device_handler.fut_device_setup(test_suite_name="vpnm")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestVpnm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", vpnm_config.get("vpnm_ipsec_vpn_healthcheck", []))
    def test_vpnm_ipsec_vpn_healthcheck(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/vpnm/vpnm_ipsec_vpn_healthcheck")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", vpnm_config.get("vpnm_ipsec_point_2_site", []))
    def test_vpnm_ipsec_point_2_site(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/vpnm/vpnm_ipsec_point_2_site")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", vpnm_config.get("vpnm_ipsec_site_2_site", []))
    def test_vpnm_ipsec_site_2_site(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/vpnm/vpnm_ipsec_site_2_site")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", vpnm_config.get("vpnm_ipsec_tunnel_interface", []))
    def test_vpnm_ipsec_tunnel_interface(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/vpnm/vpnm_ipsec_tunnel_interface")[0] == ExpectedShellResult
