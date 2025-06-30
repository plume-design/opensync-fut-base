import pytest

from framework.lib.fut_lib import reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def vpnm_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = module_name.lower()
            if manager_name.upper() not in gw_handler.kconfig_managers:
                pytest.skip(f"{manager_name.upper()} not present on device")

            kconfig = dict(item.split("=", 1) for item in gw_handler.kconfig)
            if kconfig.get("CONFIG_OSN_BACKEND_IPSEC_NULL") is not None:
                pytest.skip(f"Null IPSec implementation on device, {module_name} tests not supported.")
            if kconfig.get("CONFIG_OSN_BACKEND_VPN_NULL") is not None:
                pytest.skip(f"Null VPN implementation on device, {module_name} tests not supported.")
            if kconfig.get("CONFIG_OSN_LINUX_TUNNEL_IFACE") != "y":
                pytest.skip(f"Linux tunnel interface not configured on device, {module_name} tests not supported.")

        if "l1_handler" in fixturenames:
            l1_handler = request.getfixturevalue("l1_handler")
            handlers.append(l1_handler)

        if "l2_handler" in fixturenames:
            l2_handler = request.getfixturevalue("l2_handler")
            handlers.append(l2_handler)

        reboot_pods_and_wait_available(handlers)

        if "gw_handler" in fixturenames:
            gw_handler.device_test_setup(test_suite_name=module_name.lower())
    yield


def test_vpnm_ipsec_vpn_healthcheck(vpnm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/vpnm/vpnm_ipsec_vpn_healthcheck")[0] == 0


def test_vpnm_ipsec_point_2_site(vpnm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/vpnm/vpnm_ipsec_point_2_site")[0] == 0


def test_vpnm_ipsec_site_2_site(vpnm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/vpnm/vpnm_ipsec_site_2_site")[0] == 0


def test_vpnm_ipsec_tunnel_interface(vpnm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/vpnm/vpnm_ipsec_tunnel_interface")[0] == 0
