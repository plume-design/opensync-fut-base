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
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "VPNM" not in node_handler.get_kconfig_managers():
            pytest.skip("VPNM not present on device")
        kconfig = node_handler.get_kconfig()
        dconfig = dict(item.split("=", 1) for item in kconfig)
        if dconfig.get("CONFIG_OSN_BACKEND_IPSEC_NULL") is not None:
            pytest.skip("Null IPSec implementation on device, VPNM tests not supported.")
        if dconfig.get("CONFIG_OSN_BACKEND_VPN_NULL") is not None:
            pytest.skip("Null VPN implementation on device, VPNM tests not supported.")
        if dconfig.get("CONFIG_OSN_LINUX_TUNNEL_IFACE") != "y":
            pytest.skip("Linux tunnel interface not configured on device, VPNM tests not supported.")
        node_handler.fut_device_setup(test_suite_name="vpnm")
        service_status = node_handler.get_node_services_and_status()
        if service_status["vpnm"]["status"] != "enabled":
            pytest.skip("VPNM not enabled on device")
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
