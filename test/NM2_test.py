import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.common import compare_fw_versions
from lib_testbed.generic.util.logger import log


@pytest.fixture(scope="module")
def nm2_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = "nm"
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
            gw_handler.device_test_setup(test_suite_name=module_name.lower())
    yield


def test_nm2_configure_nonexistent_iface(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        inet_addr = parametrized_test_config.get("inet_addr")
        test_args = get_command_arguments(
            if_name,
            if_type,
            inet_addr,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_configure_nonexistent_iface", test_args)[0] == 0


def test_nm2_configure_verify_native_tap_interface(nm2_setup, parametrized_test_config, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "native_bridge":
            pytest.skip(
                "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        test_args = get_command_arguments(
            if_name,
            if_type,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_configure_verify_native_tap_interface", test_args)[0] == 0


def test_nm2_enable_disable_iface_network(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_role = parametrized_test_config.get("if_role")
        if_type = parametrized_test_config.get("if_type")

        if if_type == "vif":
            # GW AP arguments
            channel = parametrized_test_config.get("channel")
            ht_mode = parametrized_test_config.get("ht_mode")
            radio_band = parametrized_test_config.get("radio_band")
            encryption = parametrized_test_config.get("encryption")

            # GW interface creation
            gw_handler.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role=if_role,
            )
            if_name = gw_handler.interface[if_role].network_if_name

            with step("GW AP configuration"):
                assert gw_handler.interface[if_role].configure_interface() == 0

        test_args = get_command_arguments(
            if_name,
            if_type,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_enable_disable_iface_network", test_args)[0] == 0
    if if_type == "vif":
        with step("Cleanup"):
            gw_handler.interface[if_role].vif_reset()


def test_nm2_ovsdb_configure_interface_dhcpd(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_role = parametrized_test_config.get("if_role")
        if_type = parametrized_test_config.get("if_type")
        start_pool = parametrized_test_config.get("start_pool")
        end_pool = parametrized_test_config.get("end_pool")

        if if_type == "vif":
            channel = parametrized_test_config.get("channel")
            ht_mode = parametrized_test_config.get("ht_mode")
            radio_band = parametrized_test_config.get("radio_band")
            encryption = parametrized_test_config["encryption"]

            # GW interface creation
            gw_handler.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role=if_role,
            )
            if_name = gw_handler.interface[if_role].network_if_name

            with step("GW AP configuration"):
                assert gw_handler.interface[if_role].configure_interface() == 0

        test_args = get_command_arguments(
            if_name,
            if_type,
            start_pool,
            end_pool,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_ovsdb_configure_interface_dhcpd", test_args)[0] == 0
    if if_type == "vif":
        with step("Cleanup"):
            gw_handler.interface[if_role].vif_reset()


def test_nm2_ovsdb_ip_port_forward(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        src_port = parametrized_test_config.get("src_port")
        dst_ipaddr = parametrized_test_config.get("dst_ipaddr")
        dst_port = parametrized_test_config.get("dst_port")
        protocol = parametrized_test_config.get("protocol")
        pf_table = parametrized_test_config.get("pf_table")

        if if_name == gw_handler.capabilities.get_wan_bridge_ifname():
            with step("Check device if WANO enabled"):
                if "WANO" in gw_handler.kconfig_managers:
                    pytest.skip(f"If WANO is enabled, there should be no WAN bridge {if_name}")

        test_args = get_command_arguments(
            if_name,
            src_port,
            dst_ipaddr,
            dst_port,
            protocol,
            pf_table,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_ovsdb_ip_port_forward", test_args)[0] == 0


def test_nm2_ovsdb_remove_reinsert_iface(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        test_args = get_command_arguments(
            if_name,
            if_type,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_ovsdb_remove_reinsert_iface", test_args)[0] == 0


def test_nm2_set_broadcast(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        broadcast = parametrized_test_config.get("broadcast")
        test_args = get_command_arguments(
            if_name,
            if_type,
            broadcast,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_set_broadcast", test_args)[0] == 0


def test_nm2_set_dns(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        primary_dns = parametrized_test_config.get("primary_dns")
        secondary_dns = parametrized_test_config.get("secondary_dns")
        test_args = get_command_arguments(
            if_name,
            if_type,
            primary_dns,
            secondary_dns,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_set_dns", test_args)[0] == 0


def test_nm2_set_gateway(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = gw_handler.capabilities.get_primary_wan_iface()
        test_args = get_command_arguments(if_name)
    try:
        with step("Test Case"):
            assert gw_handler.execute_with_logging("tests/nm2/nm2_set_gateway", test_args)[0] == 0
    finally:
        with step("Cleanup"):
            gw_handler.configure_device_mode(device_mode="router")


def test_nm2_set_inet_addr(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        inet_addr = parametrized_test_config.get("inet_addr")
        test_args = get_command_arguments(
            if_name,
            if_type,
            inet_addr,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_set_inet_addr", test_args)[0] == 0


def test_nm2_set_ip_assign_scheme(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        radio_band = parametrized_test_config.get("radio_band")
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        if_type = parametrized_test_config.get("if_type")
        if_name = parametrized_test_config.get("if_name")
        ip_assign_scheme = parametrized_test_config.get("ip_assign_scheme")

        # GW specific arguments
        gw_bhaul_interface_type = "backhaul_ap"
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        eth_wan_name = gw_handler.capabilities.get_primary_wan_iface()
        wan_br_if_name = gw_handler.capabilities.get_wan_bridge_ifname()
        patch_h2w = gw_handler.capabilities.get_patch_port_lan_to_wan_iface()
        patch_w2h = gw_handler.capabilities.get_patch_port_wan_to_lan_iface()
        gw_uplink_gre_mtu = gw_handler.capabilities.get_uplink_gre_mtu()

        if radio_band:
            gw_bhaul_ap_if_name = gw_handler.capabilities.get_ifname(
                freq_band=radio_band,
                iftype=gw_bhaul_interface_type,
            )
            encryption = parametrized_test_config["encryption"]

            # GW interface creation
            gw_handler.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="backhaul_ap",
            )

        else:
            gw_bhaul_ap_if_name = "None"

        gw_in_bridge_mode = (
            gw_handler.execute(
                "tools/device/check_device_in_bridge_mode",
                get_command_arguments(
                    eth_wan_name,
                    lan_br_if_name,
                    wan_br_if_name,
                    patch_w2h,
                    patch_h2w,
                ),
            )
            == 0
        )

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
        elif gw_in_bridge_mode:
            ip_assign_scheme = "none" if "WANO" in gw_handler.kconfig_managers else "dhcp"
            gw_lan_br_inet_args_base.append(f"-ip_assign_scheme {ip_assign_scheme}")
        else:
            raise RuntimeError("Invalid device state.")

        gw_lan_br_inet_args = get_command_arguments(*gw_lan_br_inet_args_base)

        test_args = get_command_arguments(
            if_name,
            if_type,
            ip_assign_scheme,
            eth_wan_name,
            lan_br_if_name,
            gw_bhaul_ap_if_name,
            gw_uplink_gre_mtu,
            gw_uplink_gre_mtu,
        )

    try:
        if if_type in ["bridge", "gre"]:
            with step("LAN configuration"):
                assert gw_handler.execute("tools/device/vif_reset")[0] == 0
                assert gw_handler.execute("tools/device/create_inet_interface", gw_lan_br_inet_args)[0] == 0
        if if_type in ["gre"]:
            with step("GW AP creation"):
                assert gw_handler.interface["backhaul_ap"].configure_interface() == 0
        with step("Test case"):
            assert gw_handler.execute_with_logging("tests/nm2/nm2_set_ip_assign_scheme", test_args)[0] == 0
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()


def test_nm2_set_mtu(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        mtu = parametrized_test_config.get("mtu")
        test_args = get_command_arguments(
            if_name,
            if_type,
            mtu,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_set_mtu", test_args)[0] == 0


def test_nm2_set_nat(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        nat = parametrized_test_config.get("NAT")
        test_args = get_command_arguments(
            if_name,
            if_type,
            nat,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_set_nat", test_args)[0] == 0


def test_nm2_set_netmask(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        if_type = parametrized_test_config.get("if_type")
        netmask = parametrized_test_config.get("netmask")
        test_args = get_command_arguments(
            if_name,
            if_type,
            netmask,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_set_netmask", test_args)[0] == 0


def test_nm2_set_upnp_mode(nm2_setup, parametrized_test_config, server_handler, gw_handler, w1_handler):
    max_opensync_version = "5.6.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, max_opensync_version, ">"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {max_opensync_version} or lower.")

    with step("Put GW into router mode"):
        gw_handler.configure_device_mode(device_mode="router")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        client_retry = parametrized_test_config.get("client_retry", 2)

        # GW specific arguments
        phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)

        # W1 specific arguments
        network_namespace = w1_handler.netns
        wlan_if_name = w1_handler.wlan_ifname
        client_ip = w1_handler.get_client_ips(interface=wlan_if_name)

        # Constant arguments
        tcp_port = parametrized_test_config.get("port", 5201)

        with step("Validate retrieved and W1 IP addresses"):
            if client_ip is not False:
                log.info(f"Successfully retrieved the W1 IP address: {client_ip}")
            else:
                raise ValueError("Unable to retrieve client IP addresses.")

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Retrieve AP SSID and PSK values
        ssid = gw_handler.interface["home_ap"].ssid_raw
        psk = gw_handler.interface["home_ap"].psk_raw

        wan_link_selection = gw_handler.capabilities.is_wan_link_selection_enabled()
        if "WANO" in gw_handler.kconfig_managers or not wan_link_selection:
            wan_if_name = gw_handler.capabilities.get_primary_wan_iface()
        else:
            wan_if_name = gw_handler.capabilities.get_wan_bridge_ifname()

        if not wan_if_name:
            raise RuntimeError("Could not determine WAN interface name from device configuration.")

        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()

        if not lan_br_if_name:
            raise RuntimeError("Could not determine LAN bridge interface name from device configuration.")

        check_chan_args = get_command_arguments(
            channel,
            phy_radio_name,
        )
        client_upnp_args = get_command_arguments(
            network_namespace,
            client_ip.get("ipv4"),
            tcp_port,
        )
        check_iptable_args = get_command_arguments(
            client_ip.get("ipv4"),
            tcp_port,
        )
        w1_cleanup_args = get_command_arguments(
            network_namespace,
            tcp_port,
        )

    try:
        with step("Determine GW WAN IP"):
            gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
            gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]
            if gw_wan_inet_addr is not False:
                log.info(f"Successfully retrieved the IP addresses -> GW: {gw_wan_inet_addr}")
            else:
                raise ValueError("Unable to retrieve GW WAN IP address.")
        with step("Set UPnP mode on GW"):
            upnp_mode_args = get_command_arguments(
                wan_if_name,
                lan_br_if_name,
                gw_wan_inet_addr,
            )
            assert gw_handler.execute_with_logging("tests/nm2/nm2_set_upnp_mode", upnp_mode_args)[0] == 0
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Check channel readiness"):
            assert gw_handler.execute("tools/device/check_channel_is_ready", check_chan_args)[0] == 0
        with step("Client connection"):
            w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=gw_handler)
        with step("Verify client connectivity"):
            assert w1_handler.ping_check(ipaddr="192.168.7.1")
        with step("Testcase"):
            check_traffic_args = get_command_arguments(
                gw_wan_inet_addr,
                tcp_port,
            )
            assert w1_handler.execute("tools/client/run_upnp_client", client_upnp_args, as_sudo=True)[0] == 0
            assert (
                gw_handler.execute("tools/device/validate_port_forward_entry_in_iptables", check_iptable_args)[0] == 0
            )
            assert (
                server_handler.execute("tools/server/check_traffic_to_client", check_traffic_args, as_sudo=True)[0] == 0
            )
    finally:
        with step("Cleanup"):
            w1_handler.execute("tools/client/stop_upnp_client", w1_cleanup_args, as_sudo=True)
            gw_handler.execute("tools/device/ovsdb/empty_ovsdb_table", "Netfilter")
            gw_handler.interface["home_ap"].vif_reset()


def test_nm2_verify_native_bridge(nm2_setup, parametrized_test_config, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "native_bridge":
            pytest.skip(
                "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        bridge = parametrized_test_config.get("bridge")
        interface = parametrized_test_config.get("interface")
        test_args = get_command_arguments(
            bridge,
            interface,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_verify_native_bridge", test_args)[0] == 0


def test_nm2_vlan_interface(nm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        vlan_id = parametrized_test_config.get("vlan_id")
        test_args = get_command_arguments(
            if_name,
            vlan_id,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/nm2/nm2_vlan_interface", test_args)[0] == 0
