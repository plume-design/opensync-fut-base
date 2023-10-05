import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
nm2_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def nm2_setup():
    test_class_name = ["TestNm2"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for NM2: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            if device_handler.device_type == "node":
                phy_radio_ifnames = device_handler.capabilities.get_phy_radio_ifnames(return_type=list)
                setup_args = device_handler.get_command_arguments(*phy_radio_ifnames)
                device_handler.fut_device_setup(test_suite_name="nm2", setup_args=setup_args)
            else:
                device_handler.fut_device_setup(test_suite_name="nm2")
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestNm2:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_configure_nonexistent_iface", []))
    def test_nm2_configure_nonexistent_iface(self, cfg):
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
    def test_nm2_configure_verify_native_tap_interface(self, cfg):
        gw = pytest.gw

        with step("Check bridge type"):
            if not gw.get_bridge_type() == "native_bridge":
                pytest.skip(
                    "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
                )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            interface = cfg.get("interface")
            if_type = cfg.get("if_type")
            test_args = gw.get_command_arguments(
                interface,
                if_type,
            )

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_configure_verify_native_tap_interface", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_enable_disable_iface_network", []))
    def test_nm2_enable_disable_iface_network(self, cfg):
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
                gw.execute_with_logging("tests/nm2/nm2_enable_disable_iface_network", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_ovsdb_configure_interface_dhcpd", []))
    def test_nm2_ovsdb_configure_interface_dhcpd(self, cfg):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            start_pool = cfg.get("start_pool")
            end_pool = cfg.get("end_pool")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                start_pool,
                end_pool,
            )

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            if if_type == "vif":
                channel = cfg.get("channel")
                ht_mode = cfg.get("ht_mode")
                radio_band = cfg.get("radio_band")

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

                with step("GW AP creation"):
                    assert gw.configure_radio_vif_and_network()

        with step("Test Case"):
            assert (
                gw.execute_with_logging("tests/nm2/nm2_ovsdb_configure_interface_dhcpd", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_ovsdb_ip_port_forward", []))
    def test_nm2_ovsdb_ip_port_forward(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            src_ifname = cfg.get("src_ifname")
            src_port = cfg.get("src_port")
            dst_ipaddr = cfg.get("dst_ipaddr")
            dst_port = cfg.get("dst_port")
            protocol = cfg.get("protocol")

            if src_ifname == gw.capabilities.get_wan_bridge_ifname():
                with step("Check device if WANO enabled"):
                    check_kconfig_wano_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
                    check_kconfig_wano_ec = gw.execute("tools/device/check_kconfig_option", check_kconfig_wano_args)
                    if check_kconfig_wano_ec == 0:
                        pytest.skip(f"If WANO is enabled, there should be no WAN bridge {src_ifname}")

            test_args = gw.get_command_arguments(
                src_ifname,
                src_port,
                dst_ipaddr,
                dst_port,
                protocol,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_ovsdb_ip_port_forward", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_ovsdb_remove_reinsert_iface", []))
    def test_nm2_ovsdb_remove_reinsert_iface(self, cfg):
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
    def test_nm2_set_broadcast(self, cfg):
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
    def test_nm2_set_dns(self, cfg):
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
    def test_nm2_set_gateway(self, cfg):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            if_type = cfg.get("if_type")
            gateway = cfg.get("gateway")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            test_args = gw.get_command_arguments(
                if_name,
                if_type,
                gateway,
            )

            if if_type == "vif":
                channel = cfg.get("channel")
                ht_mode = cfg.get("ht_mode")
                radio_band = cfg.get("radio_band")

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

                with step("GW AP creation"):
                    assert gw.configure_radio_vif_and_network()

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_set_gateway", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_inet_addr", []))
    def test_nm2_set_inet_addr(self, cfg):
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
    def test_nm2_set_ip_assign_scheme(self, cfg):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            radio_band = cfg.get("radio_band")
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            if_type = cfg.get("if_type")
            if_name = cfg.get("if_name")
            ip_assign_scheme = cfg.get("ip_assign_scheme")

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

            if radio_band:
                gw_bhaul_ap_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=gw_bhaul_interface_type)
                # GW AP arguments
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

            wan_handling_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
            has_wano = gw.execute("tools/device/check_kconfig_option", wan_handling_args) == ExpectedShellResult

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
                ip_assign_scheme = "none" if has_wano else "dhcp"
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
                            gw.execute("tools/device/create_inet_interface", gw_lan_br_inet_args)[0]
                            == ExpectedShellResult
                        )
                if if_type in ["gre"]:
                    with step("GW AP creation"):
                        assert gw.configure_radio_vif_and_network()
                with step("Test case"):
                    assert (
                        gw.execute_with_logging("tests/nm2/nm2_set_ip_assign_scheme", test_args)[0]
                        == ExpectedShellResult
                    )
            finally:
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_set_mtu", []))
    def test_nm2_set_mtu(self, cfg):
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
    def test_nm2_set_nat(self, cfg):
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
    def test_nm2_set_netmask(self, cfg):
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
    def test_nm2_set_upnp_mode(self, cfg):
        fut_configurator, server, gw, w1 = pytest.fut_configurator, pytest.server, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            lan_ip_addr = "10.10.10.30"
            eth_wan_ip_addr = server.wan_ip_dict.get("gw")
            device_type = gw.capabilities.get_device_type()

            # W1 specific arguments
            network_namespace = w1.device_config.get("network_namespace")
            wlan_if_name = w1.device_config.get("wlan_if_name")
            ip_addr = "10.10.10.40"

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            tcp_port = 5201

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

            wan_handling_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
            has_wano = gw.execute("tools/device/check_kconfig_option", wan_handling_args)[0] == ExpectedShellResult

            if has_wano or device_type == "residential_gateway":
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
                wlan_if_name,
                network_namespace,
                ip_addr,
                lan_ip_addr,
                tcp_port,
            )
            router_mode_args = gw.get_command_arguments(
                wan_if_name,
                lan_br_if_name,
            )
            upnp_mode_args = gw.get_command_arguments(
                wan_if_name,
                lan_br_if_name,
                lan_ip_addr,
            )
            check_traffic_args = server.get_command_arguments(
                eth_wan_ip_addr,
                tcp_port,
            )
            check_iptable_args = gw.get_command_arguments(
                ip_addr,
                tcp_port,
            )
            w1_cleanup_args = w1.get_command_arguments(
                network_namespace,
                tcp_port,
            )

        try:
            with step("Verify router mode on GW"):
                assert (
                    gw.execute_with_logging("tests/nm2/nm2_verify_router_mode", router_mode_args)[0]
                    == ExpectedShellResult
                )
            with step("Set UPnP mode on GW"):
                assert gw.execute_with_logging("tests/nm2/nm2_set_upnp_mode", upnp_mode_args)[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Check channel readiness"):
                assert gw.execute("tools/device/check_channel_is_ready", check_chan_args)[0] == ExpectedShellResult
            with step("Client connection"):
                w1.device_api.connect(ssid=ssid, psk=psk, retry=client_retry)
            with step("Testcase"):
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
                gw.execute("tools/device/clear_port_forward_in_iptables")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("nm2_verify_linux_traffic_control_rules", []))
    def test_nm2_verify_linux_traffic_control_rules(self, cfg):
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
    def test_nm2_verify_linux_traffic_control_template_rules(self, cfg):
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
    def test_nm2_verify_native_bridge(self, cfg):
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
    def test_nm2_vlan_interface(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            parent_ifname = cfg.get("parent_ifname")
            vlan_id = cfg.get("vlan_id")
            test_args = gw.get_command_arguments(
                parent_ifname,
                vlan_id,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/nm2/nm2_vlan_interface", test_args)[0] == ExpectedShellResult
