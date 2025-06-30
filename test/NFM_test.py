import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.logger import log


@pytest.fixture(scope="module")
def nfm_setup(request: pytest.FixtureRequest):
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

            if gw_handler.node_service_status[manager_name]["status"] != "enabled":
                pytest.skip(f"{manager_name.upper()} not enabled on device")

        if "l1_handler" in fixturenames:
            l1_handler = request.getfixturevalue("l1_handler")
            handlers.append(l1_handler)

        if "l2_handler" in fixturenames:
            l2_handler = request.getfixturevalue("l2_handler")
            handlers.append(l2_handler)

        reboot_pods_and_wait_available(handlers)

        if "gw_handler" in fixturenames:
            gw_handler.device_test_setup(test_suite_name=manager_name)
    yield


def test_nfm_native_ebtable_check(nfm_setup, parametrized_test_config, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "native_bridge":
            pytest.skip(
                "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        name = parametrized_test_config.get("name")
        chain_name = parametrized_test_config.get("chain_name")
        table_name = parametrized_test_config.get("table_name")
        rule = parametrized_test_config.get("rule")
        target = parametrized_test_config.get("target")
        priority = parametrized_test_config.get("priority")
        update_target = parametrized_test_config.get("update_target")
        test_args = get_command_arguments(
            name,
            chain_name,
            table_name,
            rule,
            target,
            priority,
            update_target,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nfm/nfm_native_ebtable_check", test_args)[0] == 0


def test_nfm_native_ebtable_template_check(nfm_setup, parametrized_test_config, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "native_bridge":
            pytest.skip(
                "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        name = parametrized_test_config.get("name")
        chain_name = parametrized_test_config.get("chain_name")
        table_name = parametrized_test_config.get("table_name")
        target = parametrized_test_config.get("target")
        priority = parametrized_test_config.get("priority")
        update_target = parametrized_test_config.get("update_target")
        test_args = get_command_arguments(
            name,
            chain_name,
            table_name,
            target,
            priority,
            update_target,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nfm/nfm_native_ebtable_template_check", test_args)[0] == 0


def test_nfm_nat_loopback_check(nfm_setup, parametrized_test_config, gw_handler, l1_handler, w1_handler, w2_handler):
    with step("Put GW into router mode"):
        gw_handler.configure_device_mode(device_mode="router")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config["channel"]
        ht_mode = parametrized_test_config["ht_mode"]
        gw_radio_band = parametrized_test_config["radio_band"]
        encryption = parametrized_test_config.get("encryption", "WPA2")
        client_retry = parametrized_test_config.get("client_retry", 2)

        # Constant arguments
        ssid, psk = gw_handler.base_ssid, gw_handler.base_psk
        l1_home_ap_ssid, l1_home_ap_psk = f"{ssid}_home", f"{psk}_home"
        port = 55687

        # GW specific arguments
        gw_lan_ip_addr = gw_handler.get_ips(iface="br-home")["ipv4"]

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)

        # W1 specific arguments
        w1_wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=w1_wlan_if_name)

        # W2 specific arguments
        w2_wlan_if_name = w2_handler.wlan_ifname
        w2_mac = w2_handler.get_mac(if_name=w2_wlan_if_name)

        # Topology-based arguments
        w1_node, w2_node = gw_handler, l1_handler
        w1_ssid, w2_ssid = ssid, l1_home_ap_ssid
        w1_psk, w2_psk = psk, l1_home_ap_psk

        iperf3_server_args = get_command_arguments(port)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=gw_radio_band,
            encryption=encryption,
            interface_role="home_ap",
            ssid=ssid,
            wpa_psks=psk,
        )

        # L1 interface creation
        l1_handler.create_interface_object(
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
            gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
            gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]
            if gw_wan_inet_addr is not False:
                log.info(f"Successfully retrieved the IP addresses -> GW: {gw_wan_inet_addr}")
            else:
                raise ValueError("Unable to retrieve GW WAN IP address")
        with step("GW backhaul AP and L1 STA creation"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
            )
        with step("GW Home AP configuration"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("L1 Home AP configuration"):
            assert l1_handler.interface["home_ap"].configure_interface() == 0
        with step(f"W1 client connection to {w1_node.nickname.upper()}"):
            w1_handler.connect(ssid=w1_ssid, psk=w1_psk, retry=client_retry, node=w1_node)
        with step(f"Verify W1 client connection to {w1_node.nickname.upper()}"):
            assert w1_mac in w1_node.get_wifi_associated_clients()
        with step(f"W2 client connection to {w2_node.nickname.upper()}"):
            w2_handler.connect(ssid=w2_ssid, psk=w2_psk, retry=client_retry, node=w2_node)
        with step(f"Verify W2 client connection to {w2_node.nickname.upper()}"):
            assert w2_mac in w2_node.get_wifi_associated_clients()
        with step("Retrieve W1 and W2 IPs"):
            w1_client_ip = w1_handler.get_client_ips(interface=w1_wlan_if_name)["ipv4"]
            w2_client_ip = w2_handler.get_client_ips(interface=w2_wlan_if_name)["ipv4"]
            if w1_client_ip is not False and w2_client_ip is not False:
                log.info(f"Successfully retrieved the IP addresses -> W1: {w1_client_ip}, W2: {w2_client_ip}")
            else:
                raise ValueError("Unable to retrieve W1 and W2 IP addresses")
        with step("GW NAT loopback configuration"):
            nat_loopback_args = get_command_arguments(
                gw_lan_ip_addr,
                w2_client_ip,
                port,
            )
            assert gw_handler.execute_with_logging("tests/nfm/nfm_nat_loopback_check", nat_loopback_args)[0] == 0
        with step("Testcase"):
            # Start Iperf3 server on W2
            assert w2_handler.execute("tools/server/run_iperf3_server", iperf3_server_args, as_sudo=True)[0] == 0
            # Check NAT loopback functionality
            check_traffic_args = get_command_arguments(
                gw_wan_inet_addr,
                port,
            )
            assert w1_handler.execute("tools/server/check_traffic_to_client", check_traffic_args, as_sudo=True)[0] == 0
    finally:
        with step("Cleanup"):
            # GW, L1: complete VIF reset
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            # Remove Netfilter entries
            assert gw_handler.execute("tools/device/ovsdb/empty_ovsdb_table", "Netfilter")[0] == 0
