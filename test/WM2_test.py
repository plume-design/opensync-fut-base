import time
from itertools import cycle
from pathlib import Path

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import (
    allure_attach_to_report,
    determine_required_devices,
    multi_device_script_execution,
    step,
)
from lib_testbed.generic.util import sniffing_utils
from lib_testbed.generic.util.common import compare_fw_versions
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
wm2_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def wm2_setup():
    test_class_name = ["TestWm2"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for WM2: {nodes + clients}")
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        wireless_manager_name = node_handler.get_wireless_manager_name()
        if wireless_manager_name.upper() not in node_handler.get_kconfig_managers():
            pytest.skip(f"{wireless_manager_name.upper()} not present on device")
        node_handler.fut_device_setup(test_suite_name="wm2", setup_args=wireless_manager_name)
        service_status = node_handler.get_node_services_and_status()
        if service_status[wireless_manager_name.lower()]["status"] != "enabled":
            pytest.skip(f"{wireless_manager_name.upper()} not enabled on device")
    # L1: configure an AP with the purpose of lowering the default TX power level for the 6GHz radio (if applicable)
    if "6G" in pytest.l1.capabilities.get_supported_bands():
        pytest.l1.create_interface_object(
            channel=5,
            ht_mode="HT40",
            radio_band="6g",
            encryption="WPA3",
            interface_role="home_ap",
        )
        assert pytest.l1.interfaces["home_ap"].configure_interface() == ExpectedShellResult
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestWm2:
    pytest.test_wm2_dfs_cac_aborted_first_run = False
    pytest.test_wm2_immutable_radio_hw_mode_first_run = False
    pytest.test_wm2_immutable_radio_freq_band_first_run = False
    pytest.test_wm2_immutable_radio_hw_type_first_run = False
    pytest.test_wm2_set_radio_country_first_run = False
    pytest.wm2_last_channel_and_radio_band_used = None

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_check_wpa3_with_wpa2_multi_psk", []))
    def test_wm2_check_wpa3_with_wpa2_multi_psk(self, cfg: dict):
        gw, w1 = pytest.gw, pytest.w1
        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            ping_check_wan_ip = cfg.get("ping_check_wan_ip", "1.1.1.1")

            with step("Testcase compatibility check"):
                if radio_band == "6g":
                    pytest.skip("This testcase is not applicable for the 6GHz radio band.")

            if w1.model not in ["linux", "debian"]:
                pytest.skip("A WiFi6 client is required for this testcase, skipping.")

            if not gw.get_wpa3_support():
                pytest.skip(f"Device {gw.name} does not support WPA3.")

            # Constant arguments
            client_retry = 3
            secondary_vap_psks = ["FUT_secondary_PSK0", "FUT_secondary_PSK1"]

            # Primary VAP arguments
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption="WPA3",
                interface_role="home_ap",
            )

            # Secondary VAP arguments
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption="WPA2",
                interface_role="fhaul_ap",
                wpa_psks=secondary_vap_psks,
            )

            # Extract VAP arguments and ensure they are compliant with the OVSDB format
            primary_vap_ssid = gw.interfaces["home_ap"].ssid_raw
            primary_vap_psk = gw.interfaces["home_ap"].psk_raw

            secondary_vap_ssid = gw.interfaces["fhaul_ap"].ssid_raw

            primary_vap_args = gw.interfaces["home_ap"].combined_args
            secondary_vap_args = gw.interfaces["fhaul_ap"].combined_args

            ovsdb_primary_vap_args = {
                key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in primary_vap_args.items()
            }
            ovsdb_secondary_vap_args = {
                key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in secondary_vap_args.items()
            }

            test_args = gw.get_command_arguments(
                f"-if_name {ovsdb_primary_vap_args['radio_if_name']}",
                f"-bridge {ovsdb_primary_vap_args['bridge']}",
                f"-enabled {ovsdb_primary_vap_args['enabled']}",
                f"-primary_vif_if_name {ovsdb_primary_vap_args['vif_if_name']}",
                f"-secondary_vif_if_name {ovsdb_secondary_vap_args['vif_if_name']}",
                f"-mode {ovsdb_primary_vap_args['mode']}",
                f"-primary_ssid {ovsdb_primary_vap_args['ssid']}",
                f"-secondary_ssid {ovsdb_secondary_vap_args['ssid']}",
                f"-ssid_broadcast {ovsdb_primary_vap_args['ssid_broadcast']}",
                f"-primary_vif_radio_idx {ovsdb_primary_vap_args['vif_radio_idx']}",
                f"-secondary_vif_radio_idx {ovsdb_secondary_vap_args['vif_radio_idx']}",
                "-wpa true",
                f"-primary_wpa_key_mgmt {ovsdb_primary_vap_args['wpa_key_mgmt']}",
                f"-secondary_wpa_key_mgmt {ovsdb_secondary_vap_args['wpa_key_mgmt']}",
                f"-primary_wpa_psks {ovsdb_primary_vap_args['wpa_psks']}",
                f"-secondary_wpa_psks {ovsdb_secondary_vap_args['wpa_psks']}",
                f"-primary_wpa_oftags {ovsdb_primary_vap_args['wpa_oftags']}",
                f"-secondary_wpa_oftags {ovsdb_secondary_vap_args['wpa_oftags']}",
            )

            secondary_vap_network_args = gw.get_command_arguments(
                f"-if_type {ovsdb_primary_vap_args['if_type']}",
                f"-inet_enabled {ovsdb_primary_vap_args['inet_enabled']}",
                f"-ip_assign_scheme {ovsdb_primary_vap_args['ip_assign_scheme']}",
                f"-mtu {ovsdb_primary_vap_args['mtu']}",
                f"-NAT {ovsdb_primary_vap_args['NAT']}",
                f"-network {ovsdb_primary_vap_args['network']}",
                f"-network_if_name {ovsdb_primary_vap_args['network_if_name']}",
            )

            add_port_to_bridge_args = gw.get_command_arguments(
                ovsdb_primary_vap_args["bridge"],
                ovsdb_secondary_vap_args["vif_if_name"],
            )

        try:
            with step("GW: VIF reset"):
                gw.vif_reset()
            with step("Configure primary VAP"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step("Testcase"):
                assert (
                    gw.execute_with_logging("tests/wm2/wm2_check_wpa3_with_wpa2_multi_psk", test_args)[0]
                    == ExpectedShellResult
                )
            with step("Configure secondary VAP network"):
                assert (
                    gw.execute("tools/device/create_inet_interface", secondary_vap_network_args)[0]
                    == ExpectedShellResult
                )
                assert gw.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == ExpectedShellResult
            with step("Client connectivity check - WPA2 encryption with multi-PSK"):
                for psk in secondary_vap_psks:
                    w1.device_api.connect(
                        ssid=secondary_vap_ssid,
                        psk=psk,
                        retry=client_retry,
                    )
                    assert w1.device_api.ping_check(ipaddr=ping_check_wan_ip)
            with step("Client connectivity check - WPA3 encryption"):
                w1.device_api.connect(
                    ssid=primary_vap_ssid,
                    psk=primary_vap_psk,
                    retry=client_retry,
                )
                assert w1.device_api.ping_check(ipaddr=ping_check_wan_ip)
        finally:
            with step("Cleanup"):
                gw.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_check_wifi_credential_config", []))
    def test_wm2_check_wifi_credential_config(self, cfg: dict):
        gw = pytest.gw

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_check_wifi_credential_config")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_connect_wpa3_client", []))
    def test_wm2_connect_wpa3_client(self, cfg: dict):
        gw, w1 = pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            client_retry = cfg.get("client_retry", 2)
            encryption = cfg["encryption"]

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            if w1.model not in ["linux", "debian"]:
                pytest.skip("A WiFi6 client is required for this testcase, skipping.")

            if not gw.get_wpa3_support():
                pytest.skip(f"Device {gw.name} does not support WPA3.")

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

        try:
            with step("GW AP creation"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step("Client connection"):
                w1.device_api.connect(
                    ssid=ssid,
                    psk=psk,
                    retry=client_retry,
                )
            with step("Test case"):
                assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
        finally:
            with step("Cleanup"):
                gw.interfaces["home_ap"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_connect_wpa3_leaf", []))
    def test_wm2_connect_wpa3_leaf(self, cfg: dict):
        gw, l1 = pytest.gw, pytest.l1

        if not gw.get_wpa3_support():
            pytest.skip(f"Device {gw.name} does not support WPA3.")
        if not l1.get_wpa3_support():
            pytest.skip(f"Device {l1.name} does not support WPA3.")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            device_mode = cfg.get("device_mode", "router")
            encryption = cfg["encryption"]

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
            l1_mac = l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name)[0]

        try:
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type=None,
                )
            with step("Test case"):
                assert l1_mac in gw.device_api.get_wifi_associated_clients()[0]
        finally:
            with step("Cleanup"):
                gw.interfaces["backhaul_ap"].vif_reset()
                l1.interfaces["backhaul_sta"].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.timeout(720)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_create_all_aps_per_radio", []))
    def test_wm2_create_all_aps_per_radio(self, cfg: dict):
        gw, l1, w1 = pytest.gw, pytest.l1, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            if_list = cfg.get("if_list")
            encryption = cfg["encryption"]
            client_retry = cfg.get("client_retry", None)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

        try:
            with step("Test case"):
                for interface in if_list:
                    if interface == "backhaul_ap":
                        assert gw.create_and_configure_backhaul(
                            channel=channel,
                            leaf_device=l1,
                            radio_band=radio_band,
                            ht_mode=ht_mode,
                            encryption=encryption,
                            mesh_type=None,
                        )
                    else:
                        ssid, psk = f"FUT_ssid_{interface}", f"FUT_psk_{interface}"
                        gw.create_interface_object(
                            channel=channel,
                            ht_mode=ht_mode,
                            radio_band=radio_band,
                            encryption=encryption,
                            interface_role=interface,
                            ssid=ssid,
                            wpa_psks=psk,
                        )
                        with step(f"GW AP creation - {interface}"):
                            assert gw.interfaces[interface].configure_interface() == ExpectedShellResult
                        with step("Client connection"):
                            w1.device_api.connect(
                                ssid=ssid,
                                psk=psk,
                                retry=client_retry,
                            )
                        with step("Verify client connection"):
                            client_connection_args = {
                                "state": "active",
                            }
                            assert (
                                gw.ovsdb.wait_for_value(
                                    table="Wifi_Associated_Clients",
                                    value=client_connection_args,
                                    where=f"mac=={w1_mac}",
                                )[0]
                                == ExpectedShellResult
                            )
        finally:
            with step("Cleanup"):
                gw.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_create_wpa3_ap", []))
    def test_wm2_create_wpa3_ap(self, cfg: dict):
        gw = pytest.gw
        if not gw.get_wpa3_support():
            pytest.skip(f"Device {gw.name} does not support WPA3.")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            interface_type = cfg.get("interface_type")
            encryption = cfg["encryption"]

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role=interface_type,
            )

        try:
            with step("Test case"):
                assert gw.interfaces[interface_type].configure_interface() == ExpectedShellResult
        finally:
            with step("Cleanup"):
                gw.interfaces[interface_type].vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_dfs_cac_aborted", []))
    def test_wm2_dfs_cac_aborted(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel_A = cfg.get("channel_A")
            channel_B = cfg.get("channel_B")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # GW specific arguments
            channels = gw.capabilities.get_supported_radio_channels(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            if not {channel_A, channel_B}.issubset(channels):
                pytest.skip(f"Channels {channel_A} and {channel_B} are not valid for the same radio.")

            # GW interface creation
            gw.create_interface_object(
                channel=channel_A,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel_a {channel_A}",
                f"-channel_b {channel_B}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if not pytest.test_wm2_dfs_cac_aborted_first_run:
                gw.vif_reset()
            pytest.test_wm2_dfs_cac_aborted_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_dfs_cac_aborted", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_ht_mode_and_channel_iteration", []))
    def test_wm2_ht_mode_and_channel_iteration(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_ht_mode_and_channel_iteration", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_immutable_radio_freq_band", []))
    def test_wm2_immutable_radio_freq_band(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            freq_band = cfg.get("freq_band")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                f"-freq_band {freq_band}",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if not pytest.test_wm2_immutable_radio_freq_band_first_run:
                gw.vif_reset()
            pytest.test_wm2_immutable_radio_freq_band_first_run = True
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_immutable_radio_freq_band", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_immutable_radio_hw_mode", []))
    def test_wm2_immutable_radio_hw_mode(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            custom_hw_mode = cfg.get("custom_hw_mode")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                f"-custom_hw_mode {custom_hw_mode}",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if not pytest.test_wm2_immutable_radio_hw_mode_first_run:
                gw.vif_reset()
            pytest.test_wm2_immutable_radio_hw_mode_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_immutable_radio_hw_mode", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_immutable_radio_hw_type", []))
    def test_wm2_immutable_radio_hw_type(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            hw_type = cfg.get("hw_type")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                f"-hw_type {hw_type}",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if not pytest.test_wm2_immutable_radio_hw_type_first_run:
                gw.vif_reset()
            pytest.test_wm2_immutable_radio_hw_type_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_immutable_radio_hw_type", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_leaf_ht_mode_change", []))
    def test_wm2_leaf_ht_mode_change(self, cfg: dict):
        gw, l1 = pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            custom_ht_mode = cfg.get("custom_ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            device_mode = cfg.get("device_mode", "router")

            with step("Device type checking"):
                for device_handler in [gw, l1]:
                    device_type = device_handler.capabilities.get_device_type()
                    if device_type != "extender":
                        pytest.skip(f"{device_type.name.upper()} is not an extender, skipping this test case.")

            # GW specific arguments
            gw_phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=gw_radio_band)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)

            ht_mode_args = {
                "ht_mode": custom_ht_mode,
            }

            check_ht_mode_args = gw.get_command_arguments(
                custom_ht_mode,
                l1_bhaul_sta_if_name,
                channel,
            )

        try:
            with step("VIF reset"):
                gw.vif_reset()
                l1.vif_reset()
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("Ensure WAN connectivity on GW"):
                assert gw.check_wan_connectivity()
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                )
            with step("Ensure WAN connectivity on L1"):
                assert l1.check_wan_connectivity()
            with step(f"Change HT Mode on GW from {ht_mode} to {custom_ht_mode}"):
                assert (
                    gw.ovsdb.set_value(
                        table="Wifi_Radio_Config",
                        value=ht_mode_args,
                        where=f"if_name=={gw_phy_radio_name}",
                    )[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.ovsdb.wait_for_value(
                        table="Wifi_Radio_State",
                        value=ht_mode_args,
                        where=f"if_name=={gw_phy_radio_name}",
                    )[0]
                    == ExpectedShellResult
                )
            with step("Test case"):
                assert (
                    l1.execute("tools/device/check_ht_mode_at_os_level", check_ht_mode_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_pre_cac_channel_change_validation", []))
    def test_wm2_pre_cac_channel_change_validation(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel_A = cfg.get("channel_A")
            channel_B = cfg.get("channel_B")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # GW specific arguments
            channels = gw.capabilities.get_supported_radio_channels(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            if not {channel_A, channel_B}.issubset(channels):
                pytest.skip(f"Channels {channel_A} and {channel_B} are not valid for the same radio.")

            # GW interface creation
            gw.create_interface_object(
                channel=channel_A,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel_a {channel_A}",
                f"-channel_b {channel_B}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                f"-reg_domain {gw.regulatory_domain.upper()}",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel_A, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel_A, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_pre_cac_channel_change_validation", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_pre_cac_ht_mode_change_validation", []))
    def test_wm2_pre_cac_ht_mode_change_validation(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode_a = cfg.get("ht_mode_a")
            ht_mode_b = cfg.get("ht_mode_b")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode_a,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode_a {ht_mode_a}",
                f"-ht_mode_b {ht_mode_b}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                f"-reg_domain {gw.regulatory_domain.upper()}",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_pre_cac_ht_mode_change_validation", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_bcn_int", []))
    def test_wm2_set_bcn_int(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            bcn_int = cfg.get("bcn_int")

            # Constant arguments
            interface_type = "home_ap"

            # GW specific arguments
            vif_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role=interface_type,
            )

            test_args = gw.get_command_arguments(
                phy_radio_name,
                vif_if_name,
                bcn_int,
            )

        if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
            with step("GW AP configuration"):
                assert gw.interfaces[interface_type].configure_interface() == ExpectedShellResult
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_bcn_int", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_channel", []))
    def test_wm2_set_channel(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_channel", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_channel_neg", []))
    def test_wm2_set_channel_neg(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            mismatch_channel = cfg.get("mismatch_channel")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-mismatch_channel {mismatch_channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_channel_neg", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_ht_mode", []))
    def test_wm2_set_ht_mode(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # Constant arguments
            interface_type = "home_ap"

            # GW specific arguments
            vif_if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role=interface_type,
            )

            test_args = gw.get_command_arguments(
                f"-radio_if_name {phy_radio_name}",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-vif_if_name {vif_if_name}",
            )

        with step("GW AP Configuration"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
                assert gw.interfaces[interface_type].configure_interface() == ExpectedShellResult
            else:
                allure_attach_to_report(
                    name="log_pod_gw",
                    body=f"GW AP with the channel {channel} on the {radio_band} radio band already exists.",
                )
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_ht_mode", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_ht_mode_neg", []))
    def test_wm2_set_ht_mode_neg(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            mismatch_ht_mode = cfg.get("mismatch_ht_mode")
            max_ht_mode = int(gw.capabilities.get_max_channel_width(radio_band))
            if int(mismatch_ht_mode.removeprefix("HT")) <= max_ht_mode:
                pytest.skip(f"Bandwidth {mismatch_ht_mode} should be lower than {max_ht_mode} for {radio_band}.")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-mismatch_ht_mode {mismatch_ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_ht_mode_neg", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_country", []))
    def test_wm2_set_radio_country(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            country = cfg.get("country")
            radio_band = cfg.get("radio_band")

            # GW specific arguments
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            test_args = gw.get_command_arguments(
                phy_radio_name,
                country,
            )

        with step("VIF reset"):
            if not pytest.test_wm2_set_radio_country_first_run:
                gw.vif_reset()
            pytest.test_wm2_set_radio_country_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_country", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_thermal_tx_chainmask", []))
    def test_wm2_set_radio_thermal_tx_chainmask(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            with step("Verify correct antenna settings"):
                radio_antennas = gw.capabilities.get_radio_antenna(freq_band=radio_band)
                assert radio_antennas is not None and int(radio_antennas[0])
                radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
                tx_chainmask = radio_max_chainmask
                thermal_tx_chainmask = tx_chainmask >> 1
                assert thermal_tx_chainmask != 0
                valid_chainmasks = [(1 << x) - 1 for x in range(1, 5)]
                assert all(x in valid_chainmasks for x in [thermal_tx_chainmask, tx_chainmask, radio_max_chainmask])

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-radio_band {radio_band.upper()}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                f"-tx_chainmask {tx_chainmask}",
                f"-thermal_tx_chainmask {thermal_tx_chainmask}",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

            cleanup_args = gw.get_command_arguments(
                ovsdb_ap_args["radio_if_name"],
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_set_radio_thermal_tx_chainmask", test_args)[0]
                == ExpectedShellResult
            )
        with step("Cleanup"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_set_radio_thermal_tx_chainmask_cleanup", cleanup_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_tx_chainmask", []))
    def test_wm2_set_radio_tx_chainmask(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            with step("Verify correct antenna settings"):
                radio_antennas = gw.capabilities.get_radio_antenna(freq_band=radio_band)
                assert radio_antennas is not None and int(radio_antennas[0])
                radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
                test_tx_chainmask = radio_max_chainmask >> 1
                valid_chainmasks = [(1 << x) - 1 for x in range(1, 5)]
                assert all(x in valid_chainmasks for x in [test_tx_chainmask, radio_max_chainmask])

            # GW specific arguments
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            with step("Acquire default TX chainmask and thermal TX chainmask values"):
                default_tx_chainmask = gw.ovsdb.get(
                    table="Wifi_Radio_State",
                    select="tx_chainmask",
                    where=f"if_name=={phy_radio_name}",
                )
                assert default_tx_chainmask is not None and default_tx_chainmask != ""

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                ovsdb_ap_args["radio_if_name"],
                radio_band,
                test_tx_chainmask,
                radio_max_chainmask,
                default_tx_chainmask,
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("GW AP creation"):
            assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_tx_chainmask", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_tx_power", []))
    def test_wm2_set_radio_tx_power(self, cfg: dict):
        gw = pytest.gw
        min_opensync_version = "6.4.0.0"
        opensync_version = gw.get_opensync_version()
        if compare_fw_versions(opensync_version, min_opensync_version, "<"):
            pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            tx_power = cfg.get("tx_power")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                f"-tx_power {tx_power}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_tx_power", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_tx_power_neg", []))
    def test_wm2_set_radio_tx_power_neg(self, cfg: dict):
        gw = pytest.gw
        min_opensync_version = "6.4.0.0"
        opensync_version = gw.get_opensync_version()
        if compare_fw_versions(opensync_version, min_opensync_version, "<"):
            pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            tx_power = cfg.get("tx_power")
            mismatch_tx_power = cfg.get("mismatch_tx_power")

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                f"-tx_power {tx_power}",
                f"-mismatch_tx_power {mismatch_tx_power}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_tx_power_neg", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_vif_configs", []))
    def test_wm2_set_radio_vif_configs(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            custom_channel = cfg.get("custom_channel")
            radio_band = cfg.get("radio_band")
            ht_mode = cfg.get("ht_mode")
            encryption = cfg["encryption"]

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                f"-custom_channel {custom_channel}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_vif_configs", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_ssid", []))
    def test_wm2_set_ssid(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            ssid = str(cfg.get("ssid"))
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # GW specific arguments
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Extract AP arguments and ensure they are compliant with the OVSDB format
            ssid = gw.interfaces["home_ap"].ssid_raw
            ap_args = gw.interfaces["home_ap"].combined_args
            ovsdb_ap_args = {key: gw.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

            test_args = gw.get_command_arguments(
                f"-radio_if_name {ovsdb_ap_args['radio_if_name']}",
                f"-vif_if_name {ovsdb_ap_args['vif_if_name']}",
                f"-vif_radio_idx {ovsdb_ap_args['vif_radio_idx']}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {ovsdb_ap_args['mode']}",
                "-channel_mode manual",
                "-enabled true",
                "-wpa true",
                f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
                f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
                f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                gw.vif_reset()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_ssid", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_wifi_credential_config", []))
    def test_wm2_set_wifi_credential_config(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            onboard_type = "gre"
            security = f'\'["map",[["encryption","WPA-PSK"],["key","{psk}"],["mode","2"]]]\''

            test_args = gw.get_command_arguments(
                ssid,
                security,
                onboard_type,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_set_wifi_credential_config", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_topology_change_change_parent_change_band_change_channel", []))
    def test_wm2_topology_change_change_parent_change_band_change_channel(self, cfg: dict):
        fut_configurator, gw, l1, l2 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            gw_channel = cfg.get("gw_channel")
            l2_channel = cfg.get("leaf_channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("gw_radio_band")
            l2_radio_band = cfg.get("leaf_radio_band")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # L1 specific arguments
            l1_to_gw_radio_band = l1.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
            l1_to_gw_bhaul_sta_if_name = l1.capabilities.get_bhaul_sta_ifname(l1_to_gw_radio_band)
            l1_to_l2_radio_band = l1.get_radio_band_from_remote_channel_and_band(l2_channel, l2_radio_band)
            l1_to_l2_bhaul_sta_if_name = l1.capabilities.get_bhaul_sta_ifname(l1_to_l2_radio_band)

            # L2 specific arguments
            l2_bhaul_ap_if_name = l2.capabilities.get_bhaul_ap_ifname(l2_radio_band)

            with step("6G radio band compatibility check"):
                if gw_radio_band == "6g":
                    for node in [gw, l1, l2]:
                        if "6G" not in node.supported_radio_bands:
                            pytest.skip(f"6G radio band is not supported on {node}")
                        else:
                            log.info("6G radio band is supported on all required devices")
                else:
                    log.info("6G radio band was not selected. The 6G radio band compatibility check is not necessary")

            with step("Determine encryption"):
                if gw_radio_band == "6g" or l2_radio_band == "6g":
                    encryption = "WPA3"
                else:
                    encryption = "WPA2"

            # L2 interface creation
            l2.create_interface_object(
                channel=l2_channel,
                ht_mode=ht_mode,
                radio_band=l2_radio_band,
                encryption=encryption,
                interface_role="backhaul_ap",
                ssid=ssid,
                wpa_psks=psk,
            )

        try:
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=gw_channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type=None,
                    ssid=ssid,
                    wpa_psks=psk,
                )
            with step("Determine L1 STA MAC at runtime"):
                l1_sta_vif_mac = l1.device_api.iface.get_vif_mac(l1_to_gw_bhaul_sta_if_name)[0]
                if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L1 MAC address")
                l1_sta_mac_args = gw.get_command_arguments(l1_sta_vif_mac)
            with step("Verify GW associated clients"):
                assert (
                    gw.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == ExpectedShellResult
                )
            with step("L2 AP creation"):
                assert l2.interfaces["backhaul_ap"].configure_interface() == ExpectedShellResult
            with step("Determine L2 MAC at runtime"):
                l2_ap_vif_mac = l2.device_api.iface.get_vif_mac(l2_bhaul_ap_if_name)[0]
                if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L2 MAC address")
            with step("L1 STA configuration"):
                # Channel and radio band used only as metadata in STA configuration, not pushed to the device
                l1.create_interface_object(
                    channel=l2_channel,
                    ht_mode=ht_mode,
                    radio_band=l1_to_l2_radio_band,
                    encryption=encryption,
                    interface_role="backhaul_sta",
                    ssid=ssid,
                    wpa_psks=psk,
                    parent=l2_ap_vif_mac,
                )
                assert l1.interfaces["backhaul_sta"].configure_interface(vif_reset=True) == ExpectedShellResult
            with step("Determine L1 STA MAC at runtime"):
                l1_sta_vif_mac = l1.device_api.iface.get_vif_mac(l1_to_l2_bhaul_sta_if_name)[0]
                if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L1 MAC address")
                l1_sta_mac_args = gw.get_command_arguments(l1_sta_vif_mac)
            with step("Testcase - Verify topology change"):
                assert (
                    l2.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()
                l2.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_topology_change_change_parent_same_band_change_channel", []))
    def test_wm2_topology_change_change_parent_same_band_change_channel(self, cfg: dict):
        fut_configurator, gw, l1, l2 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            gw_channel = cfg.get("channel")
            leaf_channel = cfg.get("leaf_channel")
            ht_mode = cfg.get("ht_mode")
            encryption = cfg["encryption"]
            gw_radio_band = cfg.get("radio_band")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.capabilities.get_bhaul_sta_ifname(l1_radio_band)

            # L2 specific arguments
            l2_radio_band = l2.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
            l2_bhaul_ap_if_name = l2.capabilities.get_bhaul_ap_ifname(l2_radio_band)

            with step("6G radio band compatibility check"):
                if gw_radio_band == "6g":
                    for node in [gw, l1, l2]:
                        if "6G" not in node.supported_radio_bands:
                            pytest.skip(f"6G radio band is not supported on {node}")
                        else:
                            log.info("6G radio band is supported on all required devices")
                else:
                    log.info("6G radio band was not selected. The 6G radio band compatibility check is not necessary")

            # L2 interface creation
            l2.create_interface_object(
                channel=leaf_channel,
                ht_mode=ht_mode,
                radio_band=l2_radio_band,
                encryption=encryption,
                interface_role="backhaul_ap",
                ssid=ssid,
                wpa_psks=psk,
            )

        try:
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=gw_channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type=None,
                    ssid=ssid,
                    wpa_psks=psk,
                )
            with step("Determine L1 STA MAC at runtime"):
                l1_sta_vif_mac = l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name)[0]
                if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L1 MAC address")
                l1_sta_mac_args = gw.get_command_arguments(l1_sta_vif_mac)
            with step("Verify GW associated leaf nodes"):
                assert (
                    gw.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == ExpectedShellResult
                )
            with step("L2 AP creation"):
                assert l2.interfaces["backhaul_ap"].configure_interface() == ExpectedShellResult
            with step("Determine L2 AP MAC at runtime"):
                l2_ap_vif_mac = l2.device_api.iface.get_vif_mac(l2_bhaul_ap_if_name)[0]
                if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L2 MAC address")
            with step("Testcase - Update parent"):
                bhaul_sta_update_parent_args = l1.get_command_arguments(
                    l1_bhaul_sta_if_name,
                    l2_ap_vif_mac,
                )
                assert (
                    l1.execute_with_logging("tools/device/set_parent", bhaul_sta_update_parent_args)[0]
                    == ExpectedShellResult
                )
            with step("Testcase - Verify topology change"):
                assert (
                    l2.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()
                l2.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_topology_change_change_parent_same_band_same_channel", []))
    def test_wm2_topology_change_change_parent_same_band_same_channel(self, cfg: dict):
        fut_configurator, gw, l1, l2 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.capabilities.get_bhaul_sta_ifname(l1_radio_band)

            # L2 specific arguments
            l2_radio_band = l2.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l2_bhaul_ap_if_name = l2.capabilities.get_bhaul_ap_ifname(l2_radio_band)

            with step("6G radio band compatibility check"):
                if gw_radio_band == "6g":
                    for node in [gw, l1, l2]:
                        if "6G" not in node.supported_radio_bands:
                            pytest.skip(f"6G radio band is not supported on {node}")
                        else:
                            log.info("6G radio band is supported on all required devices")
                else:
                    log.info("6G radio band was not selected. The 6G radio band compatibility check is not necessary")

            # L2 interface creation
            l2.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=l2_radio_band,
                encryption=encryption,
                interface_role="backhaul_ap",
                ssid=ssid,
                wpa_psks=psk,
            )

        try:
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type=None,
                    ssid=ssid,
                    wpa_psks=psk,
                )
            with step("Determine L1 STA MAC at runtime"):
                l1_sta_vif_mac = l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name)[0]
                if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L1 MAC address")
                l1_sta_mac_args = gw.get_command_arguments(l1_sta_vif_mac)
            with step("Verify GW associated leaf nodes"):
                assert (
                    gw.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == ExpectedShellResult
                )
            with step("L2 AP creation"):
                assert l2.interfaces["backhaul_ap"].configure_interface() == ExpectedShellResult
            with step("Determine L2 AP MAC at runtime"):
                l2_ap_vif_mac = l2.device_api.iface.get_vif_mac(l2_bhaul_ap_if_name)[0]
                if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L2 MAC address")
            with step("Testcase - Update parent"):
                bhaul_sta_update_parent_args = l1.get_command_arguments(
                    l1_bhaul_sta_if_name,
                    l2_ap_vif_mac,
                )
                assert (
                    l1.execute_with_logging("tools/device/set_parent", bhaul_sta_update_parent_args)[0]
                    == ExpectedShellResult
                )
            with step("Testcase - Verify topology change"):
                assert (
                    l2.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()
                l2.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_validate_radio_mac_address", []))
    def test_wm2_validate_radio_mac_address(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            radio_band = cfg.get("radio_band")

            # GW specific arguments
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            test_args = gw.get_command_arguments(
                phy_radio_name,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_validate_radio_mac_address", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_verify_associated_clients", []))
    def test_wm2_verify_associated_clients(self, cfg: dict):
        gw, w1 = pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            client_retry = cfg.get("client_retry", 2)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

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

        with step("GW AP creation"):
            assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
        with step("Client connection"):
            w1.device_api.connect(
                ssid=ssid,
                psk=psk,
                retry=client_retry,
            )
        with step("Test case"):
            assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_verify_leaf_channel_change", []))
    def test_wm2_verify_leaf_channel_change(self, cfg: dict):
        gw, l1 = pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            csa_channel = cfg.get("csa_channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            device_mode = cfg.get("device_mode", "router")
            encryption = cfg["encryption"]

            # GW specific arguments
            gw_phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=gw_radio_band)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_phy_radio_name = l1.capabilities.get_phy_radio_ifname(freq_band=l1_radio_band)
            l1_bhaul_iface = l1.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)

            # Constant arguments
            ping_log_file = f"/tmp/ping_{gw_radio_band}.txt"

            gw_csa_channel_args = {
                "channel": csa_channel,
            }

            l1_csa_channel_args = {
                "channel": csa_channel,
            }

        try:
            with step("VIF reset"):
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type=None,
                )
            with step("Retrieve L1 backhaul STA IP"):
                l1_bhaul_sta_ip = l1.device_api.get_ips(iface=l1_bhaul_iface).get("ipv4")
                if not l1_bhaul_sta_ip:
                    raise ValueError(f"Unable to retrieve the IP address associated with {l1_bhaul_iface}")
            with step("Ping L1 from GW"):
                # Start pinging the L1 device and save the ping statistics in a log file
                gw_ping_args = gw.get_command_arguments(
                    l1_bhaul_sta_ip,
                    ping_log_file,
                )
                assert (
                    gw.execute("tools/device/ping_check", gw_ping_args, background_execution=True)[0]
                    == ExpectedShellResult
                )
            with step("Trigger CSA on GW"):
                assert (
                    gw.ovsdb.set_value(
                        table="Wifi_Radio_Config",
                        value=gw_csa_channel_args,
                        where=f"if_name=={gw_phy_radio_name}",
                    )[0]
                    == ExpectedShellResult
                )
            with step("Wait for channel on GW"):
                assert (
                    gw.ovsdb.wait_for_value(
                        table="Wifi_Radio_State",
                        value=gw_csa_channel_args,
                        where=f"if_name=={gw_phy_radio_name}",
                    )[0]
                    == ExpectedShellResult
                )
            with step("Test case"):
                # L1: verify channel switch
                assert (
                    l1.ovsdb.wait_for_value(
                        table="Wifi_Radio_State",
                        value=l1_csa_channel_args,
                        where=f"if_name=={l1_phy_radio_name}",
                    )[0]
                    == ExpectedShellResult
                )
                # GW: stop pinging L1
                assert gw.device_api.run_raw("pkill -f ping_check.sh")[0] == ExpectedShellResult
                # GW: verify 0% packet loss
                gw.get_log_tail_file_and_attach_to_allure(log_tail_file_name=ping_log_file)
                assert gw.execute("tools/device/retrieve_ping_packet_loss", ping_log_file)[0] == ExpectedShellResult
        finally:
            with step("Cleanup"):
                # Kill ping again in case the command was not executed as part of the test case steps
                gw.device_api.run_raw("pkill -f ping_check.sh")
                gw.vif_reset()
                l1.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_verify_gre_tunnel_gw_leaf", []))
    def test_wm2_verify_gre_tunnel_gw_leaf(self, cfg: dict):
        gw, l1, w1 = pytest.gw, pytest.l1, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            ping_wan_ip = cfg.get("ping_wan_ip", "1.1.1.1")
            client_retry = cfg.get("client_retry", 2)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # L1 interface creation
            l1.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=l1_radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # Retrieve L1 AP SSID and PSK values
            ssid = l1.interfaces["home_ap"].ssid_raw
            psk = l1.interfaces["home_ap"].psk_raw

        with step("VIF reset"):
            gw.vif_reset()
            l1.vif_reset()
        with step("Put GW into router mode"):
            assert gw.configure_device_mode(device_mode="router")
        with step("Ensure WAN connectivity on GW"):
            assert gw.check_wan_connectivity()
        with step("GW AP and L1 STA creation"):
            assert gw.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
            )
        with step("L1 Home AP configuration"):
            assert l1.interfaces["home_ap"].configure_interface() == ExpectedShellResult
        with step("Client connection to LEAF"):
            w1.device_api.connect(
                ssid=ssid,
                psk=psk,
                retry=client_retry,
            )
        with step("Verify client connection to LEAF"):
            assert w1_mac in l1.device_api.get_wifi_associated_clients()
        with step("Verify client connectivity"):
            assert w1.device_api.ping_check(ipaddr=ping_wan_ip)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_verify_wifi_security_modes", []))
    def test_wm2_verify_wifi_security_modes(self, cfg: dict):
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            gw_home_ap_if_name = gw.capabilities.get_home_ap_ifname(radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid = fut_configurator.base_ssid
            psk = None if encryption.casefold() == "open" else fut_configurator.base_psk

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
                ssid=ssid,
                wpa_psks=psk,
            )

            check_ap_args = {
                "enabled": True,
            }

        with step("VIF reset"):
            gw.vif_reset()
        with step("GW AP creation"):
            assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
        with step("Test case"):
            assert (
                gw.ovsdb.wait_for_value(
                    table="Wifi_VIF_State",
                    value=check_ap_args,
                    where=f"if_name=={gw_home_ap_if_name}",
                )[0]
                == ExpectedShellResult
            )
        with step("Client connection"):
            w1.device_api.connect(
                ssid=ssid,
                psk=psk,
                retry=client_retry,
            )
        with step("Verify client connection"):
            assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_wds_backhaul_line_topology", []))
    def test_wm2_wds_backhaul_line_topology(self, cfg: dict):
        gw, l1, l2 = pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
            l1_mac = l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name)[0]

            # L2 specific arguments
            l2_radio_band = l2.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l2_bhaul_sta_if_name = l2.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l2_radio_band)
            l2_mac = l2.device_api.iface.get_vif_mac(l2_bhaul_sta_if_name)[0]

        try:
            with step("GW-LEAF1-LEAF2 WDS backhaul configuration"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type="wds",
                    second_leaf_device=l2,
                    topology="line",
                )
            with step("Verify GW-LEAF1 WDS backhaul configuration"):
                assert l1_mac in gw.device_api.get_wifi_associated_clients()
            with step("Ensure WAN connectivity on L1"):
                assert l1.check_wan_connectivity()
            with step("Verify LEAF1-LEAF2 WDS backhaul configuration"):
                assert l2_mac in l1.device_api.get_wifi_associated_clients()
            with step("Ensure WAN connectivity on L2"):
                assert l2.check_wan_connectivity()
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()
                l2.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_wds_backhaul_star_toplogy", []))
    def test_wm2_wds_backhaul_star_toplogy(self, cfg: dict):
        gw, l1, l2 = pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
            l1_mac = l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name)[0]

            # L2 specific arguments
            l2_radio_band = l2.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l2_bhaul_sta_if_name = l2.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l2_radio_band)
            l2_mac = l2.device_api.iface.get_vif_mac(l2_bhaul_sta_if_name)[0]

        try:
            with step("GW-LEAF1-LEAF2 WDS backhaul configuration"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type="wds",
                    second_leaf_device=l2,
                    topology="star",
                )
            with step("Verify GW-LEAF1 WDS backhaul configuration"):
                assert l1_mac in gw.device_api.get_wifi_associated_clients()
            with step("Ensure WAN connectivity on L1"):
                assert l1.check_wan_connectivity()
            with step("Verify GW-LEAF2 WDS backhaul configuration"):
                assert l2_mac in gw.device_api.get_wifi_associated_clients()
            with step("Ensure WAN connectivity on L2"):
                assert l2.check_wan_connectivity()
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()
                l2.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_wds_backhaul_topology_change", []))
    def test_wm2_wds_backhaul_topology_change(self, cfg: dict):
        gw, l1, l2 = pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            gw_channel = cfg.get("gw_channel")
            l2_channel = cfg.get("leaf_channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("gw_radio_band")
            l2_radio_band = cfg.get("leaf_radio_band")

            # GW-L1 specific arguments
            gw_l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
            gw_l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=gw_l1_radio_band)
            gw_l1_mac = l1.device_api.iface.get_vif_mac(gw_l1_bhaul_sta_if_name)[0]

            # L2-L1 specific arguments
            l2_l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(l2_channel, l2_radio_band)
            l2_l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l2_l1_radio_band)
            l2_l1_mac = l1.device_api.iface.get_vif_mac(l2_l1_bhaul_sta_if_name)[0]

            with step("6G radio band compatibility check"):
                if gw_radio_band == "6g":
                    for node in [gw, l1, l2]:
                        if "6G" not in node.supported_radio_bands:
                            pytest.skip(f"6G radio band is not supported on {node}")
                        else:
                            log.info("6G radio band is supported on all required devices")
                else:
                    log.info("6G radio band was not selected. The 6G radio band compatibility check is not necessary")

        with step("Determine encryption"):
            if gw_radio_band == "6g" or l2_radio_band == "6g":
                encryption = "WPA3"
            else:
                encryption = "WPA2"

        try:
            with step("GW-LEAF1 WDS backhaul configuration"):
                assert gw.create_and_configure_backhaul(
                    channel=gw_channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type="wds",
                )
            with step("Verify GW-LEAF1 WDS backhaul configuration"):
                assert gw_l1_mac in gw.device_api.get_wifi_associated_clients()
            with step("Ensure WAN connectivity on L1"):
                assert l1.check_wan_connectivity()
            with step("LEAF2-LEAF1 WDS backhaul configuration"):
                assert l2.create_and_configure_backhaul(
                    channel=l2_channel,
                    leaf_device=l1,
                    radio_band=l2_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type="wds",
                )
            with step("Verify GW-LEAF1 WDS backhaul configuration"):
                assert l2_l1_mac in l2.device_api.get_wifi_associated_clients()
            with step("Ensure WAN connectivity on L1"):
                assert l1.check_wan_connectivity()
        finally:
            with step("Cleanup"):
                gw.vif_reset()
                l1.vif_reset()
                l2.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_transmit_rate_boost", []))
    def test_wm2_transmit_rate_boost(self, cfg: dict):
        gw, w1 = pytest.gw, pytest.w1

        min_opensync_version = "6.4.0.0"
        opensync_version = gw.get_opensync_version()

        if not compare_fw_versions(opensync_version, min_opensync_version, ">"):
            pytest.skip(
                f"Insufficient OpenSync version:{opensync_version}. Higher than {min_opensync_version} required.",
            )

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")

            # GW specific arguments
            gw_phy_radio_if_name = gw.device_api.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            gw_home_ap_if_name = gw.device_api.capabilities.get_home_ap_ifname(freq_band=radio_band)
            gw_home_ap_mac = gw.device_api.iface.get_mac(gw_home_ap_if_name)

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            # W1 specific arguments
            w1_monitor_file_name = Path(f"/tmp/w1_monitor_{radio_band}")
            w1_tcpdump_log_file = f"/tmp/w1_log_tcpdump_{radio_band}.txt"
            if "5G" in radio_band.upper():
                w1_sniffer_radio_band = "5G"
            else:
                w1_sniffer_radio_band = radio_band.upper()

            # Test case arguments
            set_transmit_rate_args = gw.get_command_arguments(
                gw_phy_radio_if_name,
            )
            verify_transmit_rate_args = w1.get_command_arguments(
                "5.5",
                gw_home_ap_mac,
                w1_tcpdump_log_file,
            )

        try:
            with step("GW: increase transmit rate"):
                assert (
                    gw.execute_with_logging("tests/wm2/wm2_transmit_rate_boost", set_transmit_rate_args)[0]
                    == ExpectedShellResult
                )
            with step("W1: start traffic capture"):
                _sniff_file_name, remote_sniff_file_path = sniffing_utils.start_sniffer_on_client(
                    client_obj=w1.device_api,
                    channel=channel,
                    band=w1_sniffer_radio_band,
                    tcpdump_flags="-evln --print",
                    tcpdump_log_file=w1_tcpdump_log_file,
                )
            with step("GW: Home AP configuration"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
                # Pause test execution to ensure traffic capture
                time.sleep(5)
            with step("W1: stop traffic capture"):
                local_sniff_file_path = sniffing_utils.stop_sniffer_and_get_file(
                    client_obj=w1.device_api,
                    remote_sniff_file_path=remote_sniff_file_path,
                    tmp_path=w1_monitor_file_name,
                    check_file_size=True,
                )
            with step("W1: Analyze captured traffic"):
                # Attach the PCAP file to the Allure report
                sniffing_utils.attach_capture_file_to_allure(file_path=local_sniff_file_path)
                assert (
                    w1.execute("tests/wm2/wm2_check_transmit_rate", verify_transmit_rate_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                # W1: revert client back to STA mode in case of test case failure
                w1.device_api.wifi_station(skip_exception=True)
                gw.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_wds_backhaul_traffic_capture", []))
    def test_wm2_wds_backhaul_traffic_capture(self, cfg: dict):
        gw, l1, w1 = pytest.gw, pytest.l1, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")

            # GW specific arguments
            gw_bhaul_ap_if_name = gw.device_api.capabilities.get_bhaul_ap_ifname(freq_band=gw_radio_band)
            gw_mac = gw.device_api.iface.get_mac(gw_bhaul_ap_if_name)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
            l1_mac = l1.device_api.iface.get_mac(l1_bhaul_sta_if_name)

            # W1 specific arguments
            w1_monitor_file_name = Path(f"/tmp/w1_monitor_{gw_radio_band}")
            w1_tcpdump_log_file = f"/tmp/w1_log_tcpdump_{gw_radio_band}.txt"
            if "5G" in gw_radio_band.upper():
                w1_sniffer_radio_band = "5G"
            else:
                w1_sniffer_radio_band = gw_radio_band.upper()

            # Test case arguments
            receiver_mac = l1_mac
            destination_mac = l1_mac
            transmitter_mac = gw_mac
            source_mac = gw_mac

            traffic_args = w1.get_command_arguments(
                receiver_mac,
                destination_mac,
                transmitter_mac,
                source_mac,
                w1_tcpdump_log_file,
            )

        try:
            with step("W1: start traffic capture"):
                _sniff_file_name, remote_sniff_file_path = sniffing_utils.start_sniffer_on_client(
                    client_obj=w1.device_api,
                    channel=channel,
                    band=w1_sniffer_radio_band,
                    tcpdump_flags="-evln --print",
                    tcpdump_log_file=w1_tcpdump_log_file,
                )
            with step("GW-L1 WDS backhaul configuration"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type="wds",
                )
            with step("Verify GW-L1 WDS backhaul configuration"):
                assert l1_mac in gw.device_api.get_wifi_associated_clients()
            with step("L1: Ensure WAN connectivity"):
                assert l1.check_wan_connectivity()
            with step("W1: stop traffic capture"):
                local_sniff_file_path = sniffing_utils.stop_sniffer_and_get_file(
                    client_obj=w1.device_api,
                    remote_sniff_file_path=remote_sniff_file_path,
                    tmp_path=w1_monitor_file_name,
                    check_file_size=True,
                )
            with step("Analyze captured traffic"):
                assert (
                    w1.execute("tests/wm2/wm2_wds_backhaul_traffic_capture", traffic_args, as_sudo=True)[0]
                    == ExpectedShellResult
                )
                # Attach PCAP file to the Allure report
                sniffing_utils.attach_capture_file_to_allure(file_path=local_sniff_file_path)
        finally:
            with step("Cleanup"):
                # W1: revert client back to STA mode in case of test case failure
                w1.device_api.wifi_station(skip_exception=True)
                gw.vif_reset()
                l1.vif_reset()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.timeout(720)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_wifi_security_mix_on_multiple_aps", []))
    def test_wm2_wifi_security_mix_on_multiple_aps(self, cfg: dict):
        gw, l1, w1 = pytest.gw, pytest.l1, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            if_list = cfg.get("if_list")
            encryption_list = cfg["encryption_list"]
            client_retry = cfg.get("client_retry", None)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            encryption_cycle = cycle(encryption_list)

        with step("VIF reset"):
            gw.vif_reset()
        with step("Test case"):
            for interface in if_list:
                encryption = next(encryption_cycle)
                if interface == "backhaul_ap":
                    assert gw.create_and_configure_backhaul(
                        channel=channel,
                        leaf_device=l1,
                        radio_band=radio_band,
                        ht_mode=ht_mode,
                        encryption=encryption,
                        mesh_type=None,
                    )
                    l1_mac = "".join(l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name))
                    assert l1_mac in gw.device_api.get_wifi_associated_clients()
                else:
                    # GW interface creation
                    gw.create_interface_object(
                        channel=channel,
                        ht_mode=ht_mode,
                        radio_band=radio_band,
                        encryption=encryption,
                        interface_role=interface,
                    )
                    # Retrieve AP SSID and PSK values
                    ssid = gw.interfaces[interface].ssid_raw
                    psk = gw.interfaces[interface].psk_raw
                    # GW AP creation
                    assert gw.interfaces[interface].configure_interface() == ExpectedShellResult
                    # W1 client connection
                    w1.device_api.connect(
                        ssid=ssid,
                        psk=psk,
                        retry=client_retry,
                    )
                    assert w1_mac in gw.device_api.get_wifi_associated_clients()
