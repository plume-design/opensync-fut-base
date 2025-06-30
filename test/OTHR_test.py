from random import randrange
from time import sleep

import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def othr_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = "dm"
            if manager_name.upper() not in gw_handler.kconfig_managers:
                pytest.skip(f"{manager_name.upper()} not present on device")

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


def test_othr_add_client_freeze(othr_setup, parametrized_test_config, gw_handler, w1_handler):

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        device_mode = parametrized_test_config.get("device_mode", "router")
        client_retry = parametrized_test_config.get("client_retry", 2)

        # GW specific arguments
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        phy_radio_ifnames = gw_handler.capabilities.get_phy_radio_ifnames(return_type=list)
        setup_args = get_command_arguments(*phy_radio_ifnames)

        # W1 specific arguments
        network_namespace = w1_handler.netns
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

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

        internet_block_args = get_command_arguments(
            network_namespace,
            "block",
        )
        internet_unblock_args = get_command_arguments(
            network_namespace,
            "unblock",
        )
        client_freeze_args = get_command_arguments(
            w1_mac,
            lan_br_if_name,
        )

    try:
        with step("Ensure WAN connectivity"):
            assert gw_handler.check_wan_connectivity()
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Client connection"):
            w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=gw_handler)
        with step("Verify client connection"):
            assert w1_mac in gw_handler.get_wifi_associated_clients()
        with step("Test case"):
            assert gw_handler.execute("tests/dm/othr_connect_wifi_client_to_ap_freeze", client_freeze_args)[0] == 0
            assert w1_handler.execute("tools/client/check_internet_traffic", internet_block_args, as_sudo=True)[0] == 0
            assert gw_handler.execute("tests/dm/othr_connect_wifi_client_to_ap_unfreeze")[0] == 0
            sleep(10)
            assert (
                w1_handler.execute("tools/client/check_internet_traffic", internet_unblock_args, as_sudo=True)[0] == 0
            )
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()
            gw_handler.execute("tests/dm/othr_connect_wifi_client_to_ap_unfreeze")
            gw_handler.execute("tests/dm/othr_setup", setup_args)
            gw_handler.configure_device_mode(device_mode="router")


def test_othr_connect_wifi_client_multi_psk(othr_setup, parametrized_test_config, gw_handler, w1_handler):

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        device_mode = parametrized_test_config.get("device_mode", "router")
        client_retry = parametrized_test_config.get("client_retry", 2)
        psk_a = parametrized_test_config.get("psk_a")
        psk_b = parametrized_test_config.get("psk_b")

        # GW specific arguments
        encryption = "WPA2"
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        gw_ap_if_name = gw_handler.capabilities.get_ifname(freq_band=radio_band, iftype="home_ap")

        # W1 specific arguments
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
            wpa_psks=[psk_a, psk_b],
        )

        # Retrieve AP SSID and PSK values
        ssid = gw_handler.interface["home_ap"].ssid_raw

        othr_cleanup_args = get_command_arguments(
            lan_br_if_name,
            gw_ap_if_name,
        )

    try:
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Test case"):
            with step("Client connection #1 PSK"):
                w1_handler.connect(ssid=ssid, psk=psk_a, retry=client_retry, node=gw_handler)
                assert w1_mac in gw_handler.get_wifi_associated_clients()
            with step("Client connection #2 PSK"):
                w1_handler.connect(ssid=ssid, psk=psk_b, retry=client_retry, node=gw_handler)
                assert w1_mac in gw_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()
            gw_handler.execute("tests/dm/othr_cleanup", othr_cleanup_args)
            gw_handler.configure_device_mode(device_mode="router")


def test_othr_connect_wifi_client_to_ap(othr_setup, parametrized_test_config, gw_handler, w1_handler):

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        device_mode = parametrized_test_config.get("device_mode", "router")
        client_retry = parametrized_test_config.get("client_retry", 2)

        # GW specific arguments
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        gw_ap_if_name = gw_handler.capabilities.get_ifname(freq_band=radio_band, iftype="home_ap")

        # W1 specific arguments
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

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

        othr_cleanup_args = get_command_arguments(
            lan_br_if_name,
            gw_ap_if_name,
        )

    try:
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Test case"):
            w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=gw_handler)
            assert w1_mac in gw_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()
            gw_handler.execute("tests/dm/othr_cleanup", othr_cleanup_args)
            gw_handler.configure_device_mode(device_mode="router")


def test_othr_healthcheck_service(othr_setup, parametrized_test_config, gw_handler):

    if "CONFIG_SERVICE_HEALTHCHECK=y" not in gw_handler.kconfig:
        pytest.skip("Healthcheck service not enabled on device, skipping test case.")

    with step("Test case"):
        healthcheck_script_list = parametrized_test_config.get("healthcheck_script_list")
        test_args = get_command_arguments(healthcheck_script_list, [])
        assert gw_handler.execute("tests/dm/othr_healthcheck_service", test_args)[0] == 0


def test_othr_verify_eth_client_connection(othr_setup, gw_handler, e2_handler):

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        eth_lan_interface = gw_handler.capabilities.get_primary_lan_iface()
        add_eth_port_to_bridge_args = get_command_arguments(
            lan_br_if_name,
            eth_lan_interface,
        )

        # E2 specific arguments
        e2_mac = e2_handler.get_mac()

        verify_eth_client_connection_args = get_command_arguments(
            eth_lan_interface,
            e2_mac,
        )

    try:
        with step("Client eth-connect"):
            e2_handler.eth_connect(pod=gw_handler, dhclient=False, skip_exception=True)
        with step("Add bridge port"):
            assert gw_handler.execute("tools/device/add_port_to_bridge", add_eth_port_to_bridge_args)[0] == 0
        with step("Client start-dhclient"):
            assert e2_handler.refresh_ip_address(reuse=True)
        with step("Test case - validate client association to GW"):
            assert (
                gw_handler.execute_with_logging(
                    "tests/dm/othr_verify_eth_client_connection",
                    verify_eth_client_connection_args,
                )[0]
                == 0
            )
        with step("Test case - validate client internet connection"):
            assert e2_handler.ping_check(ipaddr="8.8.8.8")
    finally:
        with step("Cleanup"):
            e2_handler.eth_disconnect()
            gw_handler.execute("tools/device/remove_port_from_bridge", add_eth_port_to_bridge_args)


def test_othr_verify_eth_lan_iface_wifi_master_state(othr_setup, gw_handler):

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        eth_lan_interface = gw_handler.capabilities.get_primary_lan_iface()

        if not eth_lan_interface:
            pytest.skip("No ethernet LAN interface on this device.")

        test_args = get_command_arguments(
            eth_lan_interface,
        )

    with step("Test case"):
        assert (
            gw_handler.execute_with_logging("tests/dm/othr_verify_eth_lan_iface_wifi_master_state", test_args)[0] == 0
        )


def test_othr_verify_eth_wan_iface_wifi_master_state(othr_setup, gw_handler):

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        eth_wan_interface = gw_handler.capabilities.get_primary_wan_iface()

        if not eth_wan_interface:
            pytest.skip("No ethernet WAN interface on this device.")

        test_args = get_command_arguments(
            eth_wan_interface,
        )

    with step("Test case"):
        assert (
            gw_handler.execute_with_logging("tests/dm/othr_verify_eth_wan_iface_wifi_master_state", test_args)[0] == 0
        )


def test_othr_verify_ethernet_backhaul(othr_setup, switch_handler, gw_handler, l1_handler):

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_eth_lan_if_name = gw_handler.capabilities.get_primary_lan_iface()
        gw_lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()

        # L1 specific arguments
        l1_eth_wan_if_name = l1_handler.capabilities.get_primary_wan_iface()
        l1_wan_iface = "l1_" + l1_eth_wan_if_name

        add_eth_port_to_bridge_args = get_command_arguments(
            gw_lan_br_if_name,
            gw_eth_lan_if_name,
        )

    try:
        with step("VIF reset"):
            assert gw_handler.execute("tools/device/vif_reset")[0] == 0
        with step("Ensure WAN connectivity"):
            assert gw_handler.check_wan_connectivity()
        with step("Put GW into router mode"):
            gw_handler.configure_device_mode(device_mode="router")
        with step("Add LAN ethernet port into LAN bridge"):
            assert gw_handler.execute("tools/device/add_port_to_bridge", add_eth_port_to_bridge_args)[0] == 0
        with step("Network switch configuration"):
            # On Network Switch - Configure Network Switch for LEAF to use VLAN309 of GW device.
            switch_handler.switch_ctrl.vlan_set(port_names=l1_wan_iface, vlan=309, vlan_type="untagged")
            port_names = switch_handler.get_list_of_all_port_names()
            switch_handler.disable_ports_isolation(vlan_port_names=port_names)
            switch_handler.switch_ctrl.switch_info(port_names=l1_wan_iface)
        with step("Test case"):
            l1_handler.check_wan_connectivity()
    finally:
        with step("Cleanup"):
            port_names = switch_handler.get_list_of_all_port_names()
            for port_name in port_names:
                port_alias = switch_handler.switch_ctrl.get_port_alias(port_name)
                port_number = str(port_alias["port"])
                default_port_isolation = switch_handler.switch_isolation.get(port_number)
                switch_handler.switch_ctrl.set_forward_port_isolation(
                    port_names=port_name,
                    forward_ports=default_port_isolation,
                )
            switch_handler.switch_ctrl.vlan_set(port_names=l1_wan_iface, vlan=304, vlan_type="untagged")
            gw_handler.configure_device_mode(device_mode="router")


def test_othr_verify_gre_iface_wifi_master_state(othr_setup, parametrized_test_config, gw_handler):

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        eth_wan_name = gw_handler.capabilities.get_primary_wan_iface()
        wan_br_if_name = gw_handler.capabilities.get_wan_bridge_ifname()
        patch_h2w = gw_handler.capabilities.get_patch_port_lan_to_wan_iface()
        patch_w2h = gw_handler.capabilities.get_patch_port_wan_to_lan_iface()
        gw_uplink_gre_mtu = gw_handler.capabilities.get_uplink_gre_mtu()
        gw_gre_if_name = f"gre-ifname-{randrange(100, 1000)}"

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="backhaul_ap",
        )

        ap_network_if_name = gw_handler.interface["backhaul_ap"].network_if_name

        with step("Determine GW network mode and WANO"):
            gw_in_bridge_mode_args = get_command_arguments(
                eth_wan_name,
                lan_br_if_name,
                wan_br_if_name,
                patch_h2w,
                patch_w2h,
            )
            gw_in_bridge_mode = (
                gw_handler.execute("tools/device/check_device_in_bridge_mode", gw_in_bridge_mode_args)[0] == 0
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
            else:
                ip_assign_scheme = "none" if "WANO" in gw_handler.kconfig_managers else "dhcp"
                gw_lan_br_inet_args_base.append(f"-ip_assign_scheme {ip_assign_scheme}")

            gw_lan_br_inet_args = get_command_arguments(*gw_lan_br_inet_args_base)

            gw_gre_conf_verify_args = get_command_arguments(
                ap_network_if_name,
                gw_gre_if_name,
                gw_uplink_gre_mtu,
            )

    try:
        with step("LAN configuration"):
            assert gw_handler.execute("tools/device/create_inet_interface", gw_lan_br_inet_args)[0] == 0
        with step("GW AP creation"):
            assert gw_handler.interface["backhaul_ap"].configure_interface() == 0
        with step("Testcase"):
            assert (
                gw_handler.execute_with_logging(
                    "tests/dm/othr_verify_gre_iface_wifi_master_state",
                    gw_gre_conf_verify_args,
                )[0]
                == 0
            )
    finally:
        with step("Cleanup"):
            # Reset backhaul AP interface
            gw_handler.interface["backhaul_ap"].vif_reset()
            # Disable all GRE interfaces
            assert gw_handler.execute("tools/device/disable_all_gre_interfaces")[0] == 0


def test_othr_verify_lan_bridge_iface_wifi_master_state(othr_setup, gw_handler):

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        lan_bridge_interface = gw_handler.capabilities.get_lan_bridge_ifname()
        test_args = get_command_arguments(
            lan_bridge_interface,
        )

    with step("Test case"):
        assert (
            gw_handler.execute_with_logging("tests/dm/othr_verify_lan_bridge_iface_wifi_master_state", test_args)[0]
            == 0
        )


def test_othr_verify_vif_iface_wifi_master_state(othr_setup, gw_handler):

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        if gw_handler.mlo_bh:
            bhaul_sta_ifnames = {"backhaul_sta": gw_handler.capabilities.get_mld_iface(iface_type="backhaul_sta")}
        else:
            bhaul_sta_ifnames = gw_handler.capabilities.get_bhaul_sta_ifnames()

    with step("Test case"):
        for _, bhaul_sta_if_name in bhaul_sta_ifnames.items():
            assert gw_handler.execute("tests/dm/othr_verify_vif_iface_wifi_master_state", bhaul_sta_if_name)[0] == 0


def test_othr_verify_wan_bridge_iface_wifi_master_state(othr_setup, gw_handler):

    with step("Check device if WANO enabled"):
        if "WANO" in gw_handler.kconfig_managers:
            pytest.skip("If WANO is enabled, there should be no WAN bridge")

    with step("Preparation of testcase parameters"):
        wan_bridge_ifname = gw_handler.capabilities.get_wan_bridge_ifname()
        test_args = get_command_arguments(
            wan_bridge_ifname,
        )

    with step("Test case"):
        assert (
            gw_handler.execute_with_logging("tests/dm/othr_verify_wan_bridge_iface_wifi_master_state", test_args)[0]
            == 0
        )


def test_othr_wifi_disabled_after_removing_ap(othr_setup, parametrized_test_config, gw_handler, w1_handler):

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        device_mode = parametrized_test_config.get("device_mode", "router")
        client_retry = parametrized_test_config.get("client_retry", 2)

        # GW specific arguments
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        gw_ap_if_name = gw_handler.capabilities.get_ifname(freq_band=radio_band, iftype="home_ap")
        gw_phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)

        # W1 specific arguments
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

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

        remove_home_ap_vif_radio_args = get_command_arguments(
            f"-if_name {gw_phy_radio_name}",
            f"-vif_if_name {gw_ap_if_name}",
        )
        othr_cleanup_args = get_command_arguments(
            lan_br_if_name,
            gw_ap_if_name,
        )

    try:
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Client connection"):
            w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=gw_handler)
        with step("Verify client connection"):
            assert w1_mac in gw_handler.get_wifi_associated_clients()
        with step("GW AP destruction"):
            assert gw_handler.execute("tools/device/remove_vif_interface", remove_home_ap_vif_radio_args)[0] == 0
        with step("Client connection"):
            assert (
                w1_handler.connect(
                    ssid=ssid,
                    psk=psk,
                    retry=client_retry,
                    skip_exception=True,
                )
                == ""
            )
        with step("Testcase"):
            # Verify GW has no associated clients
            assert not gw_handler.get_wifi_associated_clients()
    finally:
        with step("Clenaup"):
            gw_handler.interface["home_ap"].vif_reset()
            gw_handler.execute("tests/dm/othr_cleanup", othr_cleanup_args)
            gw_handler.configure_device_mode(device_mode="router")
