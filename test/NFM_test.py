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
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "NFM" not in node_handler.get_kconfig_managers():
            pytest.skip("NFM not present on device")
        node_handler.fut_device_setup(test_suite_name="nfm")
        service_status = node_handler.get_node_services_and_status()
        if service_status["nfm"]["status"] != "enabled":
            pytest.skip("NFM not enabled on device")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestNfm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nfm_config.get("nfm_native_ebtable_check", []))
    def test_nfm_native_ebtable_check(self, cfg: dict):
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
    def test_nfm_native_ebtable_template_check(self, cfg: dict):
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

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nfm_config.get("nfm_nat_loopback_check", []))
    def test_nfm_nat_loopback_check(self, cfg: dict):
        fut_configurator, gw, l1, w1, w2 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.w1, pytest.w2

        with step("Put GW into router mode"):
            assert gw.configure_device_mode(device_mode="router")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg["channel"]
            ht_mode = cfg["ht_mode"]
            gw_radio_band = cfg["radio_band"]
            topology = cfg["topology"]
            encryption = cfg.get("encryption", "WPA2")
            client_retry = cfg.get("client_retry", 2)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            l1_home_ap_ssid, l1_home_ap_psk = f"{ssid}_home", f"{psk}_home"
            port = 55687

            # GW specific arguments
            gw_lan_ip_addr = gw.device_api.get_ips(iface="br-home")["ipv4"]

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)

            # W1 specific arguments
            w1_wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=w1_wlan_if_name)

            # W2 specific arguments
            w2_wlan_if_name = w2.device_config.get("wlan_if_name")
            w2_mac = w2.device_api.get_mac(if_name=w2_wlan_if_name)

            # Topology-based arguments
            if topology == "line":
                w1_node, w2_node = gw, l1
                w1_ssid, w2_ssid = ssid, l1_home_ap_ssid
                w1_psk, w2_psk = psk, l1_home_ap_psk
            elif topology == "tree":
                w1_node, w2_node = l1, l1
                w1_ssid, w2_ssid = l1_home_ap_ssid, l1_home_ap_ssid
                w1_psk, w2_psk = l1_home_ap_psk, l1_home_ap_psk

            iperf3_server_args = w2.get_command_arguments(port)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=gw_radio_band,
                encryption=encryption,
                interface_role="home_ap",
                ssid=ssid,
                wpa_psks=psk,
            )

            # L1 interface creation
            l1.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=l1_radio_band,
                encryption=encryption,
                interface_role="home_ap",
                ssid=l1_home_ap_ssid,
                wpa_psks=l1_home_ap_psk,
            )

        try:
            with step("Determine GW WAN IP"):
                gw_wan_iface = gw.capabilities.get_primary_wan_iface()
                gw_wan_inet_addr = gw.device_api.get_ips(iface=gw_wan_iface)["ipv4"]
                if gw_wan_inet_addr is not False:
                    log.info(f"Successfully retrieved the IP addresses -> GW: {gw_wan_inet_addr}")
                else:
                    raise ValueError("Unable to retrieve GW WAN IP address")
            with step("GW backhaul AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                )
            with step("GW Home AP configuration"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step("L1 Home AP configuration"):
                assert l1.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step(f"W1 client connection to {w1_node.name.upper()}"):
                w1.device_api.connect(
                    ssid=w1_ssid,
                    psk=w1_psk,
                    retry=client_retry,
                )
            with step(f"Verify W1 client connection to {w1_node.name.upper()}"):
                assert w1_mac in w1_node.device_api.get_wifi_associated_clients()
            with step(f"W2 client connection to {w2_node.name.upper()}"):
                w2.device_api.connect(
                    ssid=w2_ssid,
                    psk=w2_psk,
                    retry=client_retry,
                )
            with step(f"Verify W2 client connection to {w2_node.name.upper()}"):
                assert w2_mac in w2_node.device_api.get_wifi_associated_clients()
            with step("Retrieve W1 and W2 IPs"):
                w1_client_ip = w1.device_api.get_client_ips(interface=w1_wlan_if_name)["ipv4"]
                w2_client_ip = w2.device_api.get_client_ips(interface=w2_wlan_if_name)["ipv4"]
                if w1_client_ip is not False and w2_client_ip is not False:
                    log.info(f"Successfully retrieved the IP addresses -> W1: {w1_client_ip}, W2: {w2_client_ip}")
                else:
                    raise ValueError("Unable to retrieve W1 and W2 IP addresses")
            with step("GW NAT loopback configuration"):
                nat_loopback_args = gw.get_command_arguments(
                    gw_lan_ip_addr,
                    w2_client_ip,
                    port,
                )
                assert (
                    gw.execute_with_logging("tests/nfm/nfm_nat_loopback_check", nat_loopback_args)[0]
                    == ExpectedShellResult
                )
            with step("Testcase"):
                # Start Iperf3 server on W2
                assert (
                    w2.execute("tools/server/run_iperf3_server", iperf3_server_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                # Check NAT loopback functionality
                check_traffic_args = w1.get_command_arguments(
                    gw_wan_inet_addr,
                    port,
                )
                assert (
                    w1.execute("tools/server/check_traffic_to_client", check_traffic_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                # GW, L1: complete VIF reset
                gw.vif_reset()
                l1.vif_reset()
                # Remove Netfilter entries
                assert gw.execute("tools/device/ovsdb/empty_ovsdb_table", "Netfilter")[0] == ExpectedShellResult
