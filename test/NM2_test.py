import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.common import compare_fw_versions
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
nm2_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def nm2_setup():
    test_class_name = ["TestNm2"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for NM2: {nodes + clients}")
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "NM" not in node_handler.get_kconfig_managers():
            pytest.skip("NM not present on device")
        phy_radio_ifnames = node_handler.capabilities.get_phy_radio_ifnames(return_type=list)
        setup_args = node_handler.get_command_arguments(*phy_radio_ifnames)
        node_handler.fut_device_setup(test_suite_name="nm2", setup_args=setup_args)
        service_status = node_handler.get_node_services_and_status()
        if service_status["nm"]["status"] != "enabled":
            pytest.skip("NM not enabled on device")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestNm2:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_configure_nonexistent_iface", []))
    def test_nm2_configure_nonexistent_iface(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            inet_addr = cfg.get("inet_addr")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                inet_addr,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_configure_nonexistent_iface", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_configure_verify_native_tap_interface", []))
    def test_nm2_configure_verify_native_tap_interface(self, cfg: dict):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_configure_verify_native_tap_interface", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_enable_disable_iface_network", []))
    def test_nm2_enable_disable_iface_network(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")

            if if_type == "vif":
                # GW AP arguments
                channel = cfg.get("channel")
                ht_mode = cfg.get("ht_mode")
                radio_band = cfg.get("radio_band")
                encryption = cfg.get("encryption")
                if_name = gw.capabilities.get_bhaul_ap_ifname(freq_band=radio_band)

                # GW interface creation
                gw.create_interface_object(
                    channel=channel,
                    ht_mode=ht_mode,
                    radio_band=radio_band,
                    encryption=encryption,
                    interface_role="backhaul_ap",
                )

                with step("GW AP configuration"):
                    assert gw.interfaces["backhaul_ap"].configure_interface() == ExpectedShellResult

            test_args = gw.get_command_arguments(
                if_name,
                if_type,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_enable_disable_iface_network", test_args)[0]
                == ExpectedShellResult
            )
        if if_type == "vif":
            with step("Cleanup"):
                gw.interfaces["backhaul_ap"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_ovsdb_configure_interface_dhcpd", []))
    def test_nm2_ovsdb_configure_interface_dhcpd(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            start_pool = cfg.get("start_pool")
            end_pool = cfg.get("end_pool")

            if if_type == "vif":
                channel = cfg.get("channel")
                ht_mode = cfg.get("ht_mode")
                radio_band = cfg.get("radio_band")
                encryption = cfg["encryption"]

                # GW AP arguments
                if_name = gw.capabilities.get_home_ap_ifname(freq_band=radio_band)

                # GW interface creation
                gw.create_interface_object(
                    channel=channel,
                    ht_mode=ht_mode,
                    radio_band=radio_band,
                    encryption=encryption,
                    interface_role="home_ap",
                )

                with step("GW AP creation"):
                    assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult

            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                start_pool,
                end_pool,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_ovsdb_configure_interface_dhcpd", test_args)[0]
                == ExpectedShellResult
            )
        if if_type == "vif":
            with step("Cleanup"):
                gw.interfaces["home_ap"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_ovsdb_ip_port_forward", []))
    def test_nm2_ovsdb_ip_port_forward(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            src_port = cfg.get("src_port")
            dst_ipaddr = cfg.get("dst_ipaddr")
            dst_port = cfg.get("dst_port")
            protocol = cfg.get("protocol")
            pf_table = cfg.get("pf_table")

            if if_name == gw.capabilities.get_wan_bridge_ifname():
                with step("Check device if WANO enabled"):
                    if "WANO" in gw.get_kconfig_managers():
                        pytest.skip(f"If WANO is enabled, there should be no WAN bridge {if_name}")

            test_args = gw.get_command_arguments(
                if_name,
                src_port,
                dst_ipaddr,
                dst_port,
                protocol,
                pf_table,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_ovsdb_ip_port_forward", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_ovsdb_remove_reinsert_iface", []))
    def test_nm2_ovsdb_remove_reinsert_iface(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_ovsdb_remove_reinsert_iface", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_broadcast", []))
    def test_nm2_set_broadcast(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            broadcast = cfg.get("broadcast")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                broadcast,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_broadcast", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_dns", []))
    def test_nm2_set_dns(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            primary_dns = cfg.get("primary_dns")
            secondary_dns = cfg.get("secondary_dns")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                primary_dns,
                secondary_dns,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_dns", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_gateway", []))
    def test_nm2_set_gateway(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            gateway = cfg.get("gateway")

            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                gateway,
            )

            if if_type == "vif":
                channel = cfg.get("channel")
                ht_mode = cfg.get("ht_mode")
                radio_band = cfg.get("radio_band")
                encryption = cfg["encryption"]

                # GW interface creation
                gw.create_interface_object(
                    channel=channel,
                    ht_mode=ht_mode,
                    radio_band=radio_band,
                    encryption=encryption,
                    interface_role="home_ap",
                )

                with step("GW AP configuration"):
                    assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_gateway", test_args)[0] == ExpectedShellResult
        with step("Cleanup"):
            if type == "vif":
                gw.interfaces["home_ap"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_inet_addr", []))
    def test_nm2_set_inet_addr(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            inet_addr = cfg.get("inet_addr")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                inet_addr,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_inet_addr", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_ip_assign_scheme", []))
    def test_nm2_set_ip_assign_scheme(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            radio_band = cfg.get("radio_band")
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            if_type = cfg.get("if_type")
            if_name = cfg.get("if_name")
            ip_assign_scheme = cfg.get("ip_assign_scheme")

            # GW specific arguments
            gw_bhaul_interface_type = "backhaul_ap"
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            eth_wan_name = gw.capabilities.get_primary_wan_iface()
            wan_br_if_name = gw.capabilities.get_wan_bridge_ifname()
            patch_h2w = gw.capabilities.get_patch_port_lan_to_wan_iface()
            patch_w2h = gw.capabilities.get_patch_port_wan_to_lan_iface()
            gw_uplink_gre_mtu = gw.capabilities.get_uplink_gre_mtu()

            if radio_band:
                gw_bhaul_ap_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=gw_bhaul_interface_type)
                encryption = cfg["encryption"]

                # GW interface creation
                gw.create_interface_object(
                    channel=channel,
                    ht_mode=ht_mode,
                    radio_band=radio_band,
                    encryption=encryption,
                    interface_role="backhaul_ap",
                )

            else:
                gw_bhaul_ap_if_name = "None"

            gw_in_bridge_mode = (
                gw.execute(
                    "tools/device/check_device_in_bridge_mode",
                    gw.get_command_arguments(
                        eth_wan_name,
                        lan_br_if_name,
                        wan_br_if_name,
                        patch_w2h,
                        patch_h2w,
                    ),
                )
                == ExpectedShellResult
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
                ip_assign_scheme = "none" if "WANO" in gw.get_kconfig_managers() else "dhcp"
                gw_lan_br_inet_args_base.append(f"-ip_assign_scheme {ip_assign_scheme}")
            else:
                raise RuntimeError("Invalid device state.")

            gw_lan_br_inet_args = gw.get_command_arguments(*gw_lan_br_inet_args_base)

            test_args = gw.get_command_arguments(
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
                    assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
                    assert (
                        gw.execute("tools/device/create_inet_interface", gw_lan_br_inet_args)[0] == ExpectedShellResult
                    )
            if if_type in ["gre"]:
                with step("GW AP creation"):
                    assert gw.interfaces["backhaul_ap"].configure_interface() == ExpectedShellResult
            with step("Test case"):
                assert (
                    gw.execute_with_logging("tests/nm2/nm2_set_ip_assign_scheme", test_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                gw.interfaces["home_ap"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_mtu", []))
    def test_nm2_set_mtu(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            mtu = cfg.get("mtu")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                mtu,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_mtu", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_nat", []))
    def test_nm2_set_nat(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            nat = cfg.get("NAT")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                nat,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_nat", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_netmask", []))
    def test_nm2_set_netmask(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            netmask = cfg.get("netmask")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                netmask,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_netmask", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_upnp_mode", []))
    def test_nm2_set_upnp_mode(self, cfg: dict):
        server, gw, w1 = pytest.server, pytest.gw, pytest.w1
        required_opensync_version = "5.6.0.0"
        opensync_version = gw.get_opensync_version()

        if not compare_fw_versions(opensync_version, required_opensync_version, "<="):
            pytest.skip(
                f"Insufficient OpenSync version:{opensync_version}. Required {required_opensync_version} or lower.",
            )

        with step("Put GW into router mode"):
            assert gw.configure_device_mode(device_mode="router")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            device_type = gw.capabilities.get_device_type()

            # W1 specific arguments
            network_namespace = w1.device_config.get("network_namespace")
            wlan_if_name = w1.device_config.get("wlan_if_name")
            client_ip = w1.device_api.get_client_ips(interface=wlan_if_name)

            # Constant arguments
            tcp_port = cfg.get("port", 5201)

            with step("Validate retrieved and W1 IP addresses"):
                if client_ip is not False:
                    log.info(f"Successfully retrieved the WI IP address: {client_ip}")
                else:
                    raise ValueError("Unable to retrieve client IP addresses.")

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Retrieve AP SSID and PSK values
            ssid = gw.interfaces["home_ap"].ssid_raw
            psk = gw.interfaces["home_ap"].psk_raw

            if "WANO" in gw.get_kconfig_managers() or device_type == "residential_gateway":
                wan_if_name = gw.capabilities.get_primary_wan_iface()
            else:
                wan_if_name = gw.capabilities.get_wan_bridge_ifname()

            if not wan_if_name:
                raise RuntimeError("Could not determine WAN interface name from device configuration.")

            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()

            if not lan_br_if_name:
                raise RuntimeError("Could not determine LAN bridge interface name from device configuration.")

            check_chan_args = gw.get_command_arguments(
                channel,
                phy_radio_name,
            )
            client_upnp_args = w1.get_command_arguments(
                network_namespace,
                client_ip.get("ipv4"),
                tcp_port,
            )
            check_iptable_args = gw.get_command_arguments(
                client_ip.get("ipv4"),
                tcp_port,
            )
            w1_cleanup_args = w1.get_command_arguments(
                network_namespace,
                tcp_port,
            )

        try:
            with step("Determine GW WAN IP"):
                gw_wan_iface = gw.capabilities.get_primary_wan_iface()
                gw_wan_inet_addr = gw.device_api.get_ips(iface=gw_wan_iface)["ipv4"]
                if gw_wan_inet_addr is not False:
                    log.info(f"Successfully retrieved the IP addresses -> GW: {gw_wan_inet_addr}")
                else:
                    raise ValueError("Unable to retrieve GW WAN IP address.")
            with step("Set UPnP mode on GW"):
                upnp_mode_args = gw.get_command_arguments(
                    wan_if_name,
                    lan_br_if_name,
                    gw_wan_inet_addr,
                )
                assert gw.execute_with_logging("tests/nm2/nm2_set_upnp_mode", upnp_mode_args)[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step("Check channel readiness"):
                assert gw.execute("tools/device/check_channel_is_ready", check_chan_args)[0] == ExpectedShellResult
            with step("Client connection"):
                w1.device_api.connect(
                    ssid=ssid,
                    psk=psk,
                    retry=client_retry,
                )
            with step("Verify client connectivity"):
                assert w1.device_api.ping_check(ipaddr="192.168.7.1")
            with step("Testcase"):
                check_traffic_args = server.get_command_arguments(
                    gw_wan_inet_addr,
                    tcp_port,
                )
                assert (
                    w1.execute("tools/client/run_upnp_client", client_upnp_args, as_sudo=True)[0] == ExpectedShellResult
                )
                assert (
                    gw.execute("tools/device/validate_port_forward_entry_in_iptables", check_iptable_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    server.execute("tools/server/check_traffic_to_client", check_traffic_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                w1.execute("tools/client/stop_upnp_client", w1_cleanup_args, as_sudo=True)
                gw.execute("tools/device/ovsdb/empty_ovsdb_table", "Netfilter")
                gw.interfaces["home_ap"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_verify_linux_traffic_control_rules", []))
    def test_nm2_verify_linux_traffic_control_rules(self, cfg: dict):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            ingress_action_args = f"{cfg['ingress_action']} dev {lan_br_if_name}"
            egress_action_args = f"{cfg['egress_action']} dev {lan_br_if_name}"
            test_args = gw.get_command_arguments(
                cfg["if_name"],
                cfg["ingress_match"],
                ingress_action_args,
                cfg["ingress_expected_str"],
                cfg["egress_match"],
                egress_action_args,
                cfg["egress_expected_str"],
                cfg["priority"],
                cfg["ingress_updated_match"],
                cfg["ingress_expected_str_after_update"],
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_verify_linux_traffic_control_rules", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_verify_linux_traffic_control_template_rules", []))
    def test_nm2_verify_linux_traffic_control_template_rules(self, cfg: dict):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            ingress_action_args = f"{cfg['ingress_action']} dev {lan_br_if_name}"
            egress_action_args = f"{cfg['egress_action']} dev {lan_br_if_name}"
            test_args = gw.get_command_arguments(
                cfg["if_name"],
                cfg["ingress_match"],
                ingress_action_args,
                cfg["ingress_tag_name"],
                cfg["egress_match"],
                egress_action_args,
                cfg["egress_match_with_tag"],
                cfg["egress_expected_str"],
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_verify_linux_traffic_control_template_rules", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_verify_native_bridge", []))
    def test_nm2_verify_native_bridge(self, cfg: dict):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            bridge = cfg.get("bridge")
            interface = cfg.get("interface")
            test_args = gw.get_command_arguments(
                bridge,
                interface,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_verify_native_bridge", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_vlan_interface", []))
    def test_nm2_vlan_interface(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            vlan_id = cfg.get("vlan_id")
            test_args = gw.get_command_arguments(
                if_name,
                vlan_id,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_vlan_interface", test_args)[0] == ExpectedShellResult
