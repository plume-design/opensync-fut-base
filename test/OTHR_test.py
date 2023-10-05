from random import randrange
from time import sleep

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
othr_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def othr_setup():
    test_class_name = ["TestOthr"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for OTHR: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            continue
        try:
            device_handler = getattr(pytest, device)
            if device_handler.device_type == "node":
                phy_radio_ifnames = device_handler.capabilities.get_phy_radio_ifnames(return_type=list)
                setup_args = device_handler.get_command_arguments(*phy_radio_ifnames)
                device_handler.fut_device_setup(test_suite_name="dm", setup_args=setup_args)
            else:
                device_handler.fut_device_setup(test_suite_name="dm")
        except Exception as exception:
            RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestOthr:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_add_client_freeze", []))
    def test_othr_add_client_freeze(self, cfg):
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            device_mode = cfg.get("device_mode", "router")
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            phy_radio_ifnames = gw.capabilities.get_phy_radio_ifnames(return_type=list)
            setup_args = gw.get_command_arguments(*phy_radio_ifnames)

            # W1 specific arguments
            network_namespace = w1.device_config.get("network_namespace")
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            internet_block_args = w1.get_command_arguments(
                network_namespace,
                "block",
            )
            internet_unblock_args = w1.get_command_arguments(
                network_namespace,
                "unblock",
            )
            client_freeze_args = gw.get_command_arguments(
                w1_mac,
                lan_br_if_name,
            )

        try:
            with step("Ensure WAN connectivity"):
                assert gw.check_wan_connectivity()
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Client connection"):
                w1.device_api.connect(ssid=ssid, psk=psk, retry=client_retry)
            with step("Verify client connection"):
                assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
            with step("Test case"):
                assert (
                    gw.execute("tests/dm/othr_connect_wifi_client_to_ap_freeze", client_freeze_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    w1.execute("tools/client/check_internet_traffic", internet_block_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                assert gw.execute("tests/dm/othr_connect_wifi_client_to_ap_unfreeze")[0] == ExpectedShellResult
                sleep(10)
                assert (
                    w1.execute("tools/client/check_internet_traffic", internet_unblock_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                gw.execute("tests/dm/othr_connect_wifi_client_to_ap_unfreeze")
                w1.device_api.reboot()
                gw.execute("tests/dm/othr_setup", setup_args)
                gw.configure_device_mode(device_mode="router")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_connect_wifi_client_multi_psk", []))
    def test_othr_connect_wifi_client_multi_psk(self, cfg):
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            device_mode = cfg.get("device_mode", "router")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 2)
            psk_a = cfg.get("psk_a")
            psk_b = cfg.get("psk_b")

            # GW specific arguments
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            gw_ap_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype="home_ap")

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid = fut_configurator.base_ssid

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": [psk_a, psk_b],
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            othr_cleanup_args = gw.get_command_arguments(
                lan_br_if_name,
                gw_ap_if_name,
            )

        try:
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Test case"):
                with step("Client connection #1 PSK"):
                    w1.device_api.connect(ssid=ssid, psk=psk_a, retry=client_retry)
                    assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
                with step("Client connection #2 PSK"):
                    w1.device_api.connect(ssid=ssid, psk=psk_b, retry=client_retry)
                    assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
        finally:
            with step("Cleanup"):
                gw.execute("tests/dm/othr_cleanup", othr_cleanup_args)
                gw.configure_device_mode(device_mode="router")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_connect_wifi_client_to_ap", []))
    def test_othr_connect_wifi_client_to_ap(self, cfg):
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            device_mode = cfg.get("device_mode", "router")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            gw_ap_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype="home_ap")

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            othr_cleanup_args = gw.get_command_arguments(
                lan_br_if_name,
                gw_ap_if_name,
            )

        try:
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Test case"):
                with step("Client connection #1 PSK"):
                    w1.device_api.connect(ssid=ssid, psk=psk, retry=client_retry)
                    assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
        finally:
            with step("Cleanup"):
                gw.execute("tests/dm/othr_cleanup", othr_cleanup_args)
                gw.configure_device_mode(device_mode="router")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_eth_client_connection", []))
    def test_othr_verify_eth_client_connection(self, cfg):
        gw, e2 = pytest.gw, pytest.e2

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            eth_lan_interface = gw.capabilities.get_primary_lan_iface()
            add_eth_port_to_bridge_args = gw.get_command_arguments(
                lan_br_if_name,
                eth_lan_interface,
            )

            # E2 specific arguments
            e2_mac = e2.device_api.get_mac()

            verify_eth_client_connection_args = gw.get_command_arguments(
                eth_lan_interface,
                e2_mac,
            )

        try:
            with step("Client eth-connect"):
                # This step will fail since lan port is not added into br-home bridge
                e2.device_api.eth_connect(pod=gw.device_api, skip_exception=True)
            with step("Add bridge port"):
                assert gw.execute("tools/device/add_bridge_port", add_eth_port_to_bridge_args)[0] == ExpectedShellResult
            with step("Client start-dhclient"):
                assert e2.device_api.refresh_ip_address(reuse=True)
            with step("Test case - validate client association to GW"):
                assert (
                    gw.execute_with_logging(
                        "tests/dm/othr_verify_eth_client_connection",
                        verify_eth_client_connection_args,
                    )[0]
                    == ExpectedShellResult
                )
            with step("Test case - validate client internet connection"):
                assert e2.device_api.ping_check(ipaddr="8.8.8.8")
        finally:
            with step("Cleanup"):
                e2.device_api.eth_disconnect()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_eth_lan_iface_wifi_master_state", []))
    def test_othr_verify_eth_lan_iface_wifi_master_state(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            eth_lan_interface = gw.capabilities.get_primary_lan_iface()

            if not eth_lan_interface:
                pytest.skip("No ethernet LAN interface on this device.")

            test_args = gw.get_command_arguments(
                eth_lan_interface,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_eth_lan_iface_wifi_master_state", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_eth_wan_iface_wifi_master_state", []))
    def test_othr_verify_eth_wan_iface_wifi_master_state(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            eth_wan_interface = gw.capabilities.get_primary_wan_iface()

            if not eth_wan_interface:
                pytest.skip("No ethernet WAN interface on this device.")

            test_args = gw.get_command_arguments(
                eth_wan_interface,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_eth_wan_iface_wifi_master_state", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_ethernet_backhaul", []))
    def test_othr_verify_ethernet_backhaul(self, cfg):
        server, gw, l1 = pytest.server, pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            gw_eth_lan_if_name = gw.capabilities.get_primary_lan_iface()
            gw_lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()

            # L1 specific arguments
            l1_eth_wan_if_name = l1.capabilities.get_primary_wan_iface()
            l1_wan_iface = "l1_" + l1_eth_wan_if_name

            add_eth_port_to_bridge_args = gw.get_command_arguments(
                gw_lan_br_if_name,
                gw_eth_lan_if_name,
            )

        try:
            with step("VIF reset"):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            with step("Ensure WAN connectivity"):
                assert gw.check_wan_connectivity()
            with step("Put GW into router mode"):
                assert gw.configure_device_mode(device_mode="router")
            with step("Add LAN ethernet port into LAN bridge"):
                assert gw.execute("tools/device/add_bridge_port", add_eth_port_to_bridge_args)[0] == ExpectedShellResult
            with step("Network switch configuration"):
                # On Network Switch - Configure Network Switch for LEAF to use VLAN309 of GW device.
                server.switch.vlan_set(port_names=l1_wan_iface, vlan=309, vlan_type="untagged")
                server.switch.disable_port_isolations()
                server.switch.info(port_names=l1_wan_iface)
            with step("Test case"):
                l1.check_wan_connectivity()
        finally:
            with step("Cleanup"):
                server.switch.enable_port_isolations()
                server.switch.vlan_set(port_names=l1_wan_iface, vlan=304, vlan_type="untagged")
                assert gw.configure_device_mode(device_mode="router")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_gre_iface_wifi_master_state", []))
    def test_othr_verify_gre_iface_wifi_master_state(self, cfg):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # GW specific arguments
            gw_bhaul_interface_type = "backhaul_ap"
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            eth_wan_name = gw.capabilities.get_primary_wan_iface()
            wan_br_if_name = gw.capabilities.get_wan_bridge_ifname()
            patch_h2w = gw.capabilities.get_patch_port_lan_to_wan_iface()
            patch_w2h = gw.capabilities.get_patch_port_wan_to_lan_iface()
            gw_uplink_gre_mtu = gw.capabilities.get_uplink_gre_mtu()
            gw_gre_if_name = f"gre-ifname-{randrange(100, 1000)}"
            gw_bhaul_ap_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=gw_bhaul_interface_type)

            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "interface_type": "backhaul_ap",
                "bridge": False,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            with step("Determine GW network mode and WANO"):
                gw_in_bridge_mode_args = gw.get_command_arguments(
                    eth_wan_name,
                    lan_br_if_name,
                    wan_br_if_name,
                    patch_h2w,
                    patch_w2h,
                )
                gw_in_bridge_mode = (
                    gw.execute("tools/device/check_device_in_bridge_mode", gw_in_bridge_mode_args)[0]
                    == ExpectedShellResult
                )
                wan_handling_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
                has_wano = gw.execute("tools/device/check_kconfig_option", wan_handling_args)[0] == ExpectedShellResult

                gw_lan_br_inet_args_base = [
                    f"-if_name {lan_br_if_name}",
                    "-if_type bridge",
                    "-enabled true",
                    "-network true",
                    "-NAT false",
                ]

                if not gw_in_bridge_mode:
                    gw_lan_br_inet_args_base += [
                        "-ip_assign_scheme static",
                        "-inet_addr 192.168.0.1",
                        "-netmask 255.255.255.0",
                        '-dhcpd \'["map",[["start","192.168.0.10"],["stop","192.168.0.200"]]]\'',
                    ]
                else:
                    ip_assign_scheme = "none" if has_wano else "dhcp"
                    gw_lan_br_inet_args_base.append(f"-ip_assign_scheme {ip_assign_scheme}")

                gw_lan_br_inet_args = gw.get_command_arguments(*gw_lan_br_inet_args_base)

                gw_gre_conf_verify_args = gw.get_command_arguments(
                    gw_bhaul_ap_if_name,
                    gw_gre_if_name,
                    gw_uplink_gre_mtu,
                )

        with step("LAN configuration"):
            assert gw.execute("tools/device/create_inet_interface", gw_lan_br_inet_args)[0] == ExpectedShellResult
        with step("GW AP creation"):
            assert gw.configure_radio_vif_and_network()
        with step("Testcase"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_gre_iface_wifi_master_state", gw_gre_conf_verify_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_iperf3_speedtest", []))
    def test_othr_verify_iperf3_speedtest(self, cfg):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            traffic_type = cfg.get("traffic_type")

            # Server specific arguments
            server_hostname = server.mqtt_hostname

            test_args = gw.get_command_arguments(
                server_hostname,
                traffic_type,
            )

        with step("Test case"):
            assert server.execute("tools/server/run_iperf3_server", as_sudo=True)[0] == ExpectedShellResult
            assert gw.execute_with_logging("tests/dm/othr_verify_iperf3_speedtest", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_lan_bridge_iface_wifi_master_state", []))
    def test_othr_verify_lan_bridge_iface_wifi_master_state(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            lan_bridge_interface = gw.capabilities.get_lan_bridge_ifname()
            test_args = gw.get_command_arguments(
                lan_bridge_interface,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_lan_bridge_iface_wifi_master_state", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_ookla_speedtest", []))
    def test_othr_verify_ookla_speedtest(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            testid = randrange(100, 1000)
            test_args = gw.get_command_arguments(
                testid,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert gw.execute_with_logging("tests/dm/othr_verify_ookla_speedtest", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_ookla_speedtest_bind_options", []))
    def test_othr_verify_ookla_speedtest_bind_options(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            testid = randrange(100, 1000)
            test_args = gw.get_command_arguments(
                testid,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_ookla_speedtest_bind_options", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_ookla_speedtest_bind_reporting", []))
    def test_othr_verify_ookla_speedtest_bind_reporting(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            testid = randrange(100, 1000)
            test_args = gw.get_command_arguments(
                testid,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_ookla_speedtest_bind_reporting", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_ookla_speedtest_sdn_endpoint_config", []))
    def test_othr_verify_ookla_speedtest_sdn_endpoint_config(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            speedtest_config_path = cfg.get("speedtest_config_path")
            test_args = gw.get_command_arguments(
                speedtest_config_path,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_ookla_speedtest_sdn_endpoint_config", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_samknows_process", []))
    def test_othr_verify_samknows_process(self, cfg):
        gw = pytest.gw

        try:
            with step("Test case"):
                assert gw.execute_with_logging("tests/dm/othr_verify_samknows_process")[0] == ExpectedShellResult
        finally:
            with step("Cleanup"):
                assert gw.execute_with_logging("tests/dm/othr_samknows_process_cleanup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_vif_iface_wifi_master_state", []))
    def test_othr_verify_vif_iface_wifi_master_state(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            supported_channels = gw.capabilities.get_bhaul_sta_ifnames()
            supported_bands = supported_channels.keys()

        with step("Test case"):
            for band in supported_bands:
                bhaul_if_name = gw.capabilities.get_bhaul_ap_ifname(freq_band=band)
                assert (
                    gw.execute("tests/dm/othr_verify_vif_iface_wifi_master_state", bhaul_if_name)[0]
                    == ExpectedShellResult
                )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_verify_wan_bridge_iface_wifi_master_state", []))
    def test_othr_verify_wan_bridge_iface_wifi_master_state(self, cfg):
        gw = pytest.gw

        with step("Check device if WANO enabled"):
            check_kconfig_wano_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
            check_kconfig_wano_ec = gw.execute("tools/device/check_kconfig_option", check_kconfig_wano_args)[0]
            if check_kconfig_wano_ec == 0:
                pytest.skip("If WANO is enabled, there should be no WAN bridge")

        with step("Preparation of testcase parameters"):
            wan_bridge_ifname = gw.capabilities.get_wan_bridge_ifname()
            test_args = gw.get_command_arguments(
                wan_bridge_ifname,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/othr_verify_wan_bridge_iface_wifi_master_state", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", othr_config.get("othr_wifi_disabled_after_removing_ap", []))
    def test_othr_wifi_disabled_after_removing_ap(self, cfg):
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            device_mode = cfg.get("device_mode", "router")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            gw_ap_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype="home_ap")
            gw_phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            remove_home_ap_vif_radio_args = gw.get_command_arguments(
                f"-if_name {gw_phy_radio_name}",
                f"-vif_if_name {gw_ap_if_name}",
            )
            othr_cleanup_args = gw.get_command_arguments(
                lan_br_if_name,
                gw_ap_if_name,
            )

        try:
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Client connection"):
                w1.device_api.connect(ssid=ssid, psk=psk, retry=client_retry)
            with step("Verify client connection"):
                assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
            with step("GW AP destruction"):
                assert (
                    gw.execute("tools/device/remove_vif_interface", remove_home_ap_vif_radio_args)[0]
                    == ExpectedShellResult
                )
            with step("Client connection"):
                assert w1.device_api.connect(ssid=ssid, psk=psk, retry=client_retry, skip_exception=True) == ""
            with step("Testcase"):
                # Verify GW has no associated clients
                wifi_associated_clients = gw.device_api.get_wifi_associated_clients()
                assert any(w1_mac not in associated_clients for associated_clients in wifi_associated_clients)
        finally:
            with step("Clenaup"):
                w1.device_api.reboot()
                gw.execute("tests/dm/othr_cleanup", othr_cleanup_args)
                gw.configure_device_mode(device_mode="router")
