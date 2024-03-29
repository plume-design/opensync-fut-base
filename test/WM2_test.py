from itertools import cycle

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import (
    allure_attach_to_report,
    determine_required_devices,
    get_str_hash,
    multi_device_script_execution,
    step,
)
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
wm2_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def wm2_setup():
    test_class_name = ["TestWm2"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for WM2: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            wireless_manager_name = device_handler.get_wireless_manager_name()
            device_handler.fut_device_setup(test_suite_name="wm2", setup_args=wireless_manager_name)
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    # L1: configure an AP with the purpose of lowering the default TX power level for the 6GHz radio (if applicable)
    if "6G" in pytest.l1.capabilities.get_supported_bands():
        l1_ap_vif_args = {
            "channel": 5,
            "ht_mode": "HT40",
            "radio_band": "6g",
        }
        pytest.l1.ap_args = l1_ap_vif_args
        pytest.l1.configure_radio_vif_and_network()
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

            with step("Testcase compatibility check"):
                if radio_band == "6g":
                    pytest.skip("This testcase is not applicable for the 6GHz radio band.")

            if w1.model not in ["linux", "debian"]:
                pytest.skip("A WiFi6 client is required for this testcase, skipping.")

            # Common VAP arguments
            common_vap_configuration_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wifi_security_type": "wpa",
            }

            # Primary VAP arguments
            primary_vap_configuration_args = common_vap_configuration_args | {
                "encryption": "WPA3",
                "interface_type": "home_ap",
                "wpa_psk": "FUT_primary_PSK",
                "ssid": "FUT_primary_SSID",
                "reset_vif": True,
            }

            # Secondary VAP arguments
            secondary_vap_configuration_args = common_vap_configuration_args | {
                "encryption": "WPA2",
                "interface_type": "fhaul_ap",
                "wpa_psk": ["FUT_secondary_PSK0", "FUT_secondary_PSK1"],
                "ssid": "FUT_secondary_SSID",
            }

            # Constant arguments
            client_retry = 3

            # VAP and security arguments
            gw.ap_args = primary_vap_configuration_args
            primary_vap_args = gw.configure_radio_vif_interface(return_as_dict=True)
            gw.ap_args = secondary_vap_configuration_args
            secondary_vap_args = gw.configure_radio_vif_interface(return_as_dict=True)

            # Network arguments
            secondary_vap_network_args = gw.configure_network_parameters()

            test_args = gw.get_command_arguments(
                f"-if_name {primary_vap_args['if_name']}",
                f"-bridge {primary_vap_args['bridge']}",
                f"-enabled {primary_vap_args['enabled']}",
                f"-primary_vif_if_name {primary_vap_args['vif_if_name']}",
                f"-secondary_vif_if_name {secondary_vap_args['vif_if_name']}",
                f"-mode {primary_vap_args['mode']}",
                f"-primary_ssid {primary_vap_args['ssid']}",
                f"-secondary_ssid {secondary_vap_args['ssid']}",
                f"-ssid_broadcast {primary_vap_args['ssid_broadcast']}",
                f"-primary_vif_radio_idx {primary_vap_args['vif_radio_idx']}",
                f"-secondary_vif_radio_idx {secondary_vap_args['vif_radio_idx']}",
                f"-wpa {primary_vap_args['wpa']}",
                f"-primary_wpa_key_mgmt {primary_vap_args['wpa_key_mgmt']}",
                f"-secondary_wpa_key_mgmt {secondary_vap_args['wpa_key_mgmt']}",
                f"-primary_wpa_psks {primary_vap_args['wpa_psks']}",
                f"-secondary_wpa_psks {secondary_vap_args['wpa_psks']}",
                f"-primary_wpa_oftags {primary_vap_args['wpa_oftags']}",
                f"-secondary_wpa_oftags {secondary_vap_args['wpa_oftags']}",
            )

        try:
            with step("Configure primary VAP"):
                gw.ap_args = primary_vap_configuration_args
                assert gw.configure_radio_vif_and_network()
            with step("Testcase"):
                assert (
                    gw.execute_with_logging("tests/wm2/wm2_check_wpa3_with_wpa2_multi_psk", test_args)[0]
                    == ExpectedShellResult
                )
            with step("Configure secondary VAP network"):
                secondary_vap_network_args = gw.get_command_arguments(*secondary_vap_network_args)
                assert (
                    gw.execute("tools/device/create_inet_interface", secondary_vap_network_args)[0]
                    == ExpectedShellResult
                )
                add_port_to_bridge_args = gw.get_command_arguments(
                    primary_vap_args["bridge"],
                    secondary_vap_args["vif_radio_idx"],
                )
                assert gw.execute("tools/device/add_bridge_port", add_port_to_bridge_args)[0] == ExpectedShellResult
            with step("Client connectivity check - WPA2 encryption with multi-PSK"):
                gw.ap_args = secondary_vap_configuration_args
                security_args = gw.configure_wifi_security(return_as_dict=True)
                for psk in secondary_vap_configuration_args["wpa_psk"]:
                    w1.device_api.connect(
                        ssid=secondary_vap_configuration_args["ssid"],
                        psk=psk,
                        key_mgmt=security_args["key_mgmt_mapping"],
                        retry=client_retry,
                    )
            with step("Client connectivity check - WPA3 encryption"):
                gw.ap_args = primary_vap_configuration_args
                security_args = gw.configure_wifi_security(return_as_dict=True)
                w1.device_api.connect(
                    ssid=primary_vap_configuration_args["ssid"],
                    psk=primary_vap_configuration_args["wpa_psk"],
                    key_mgmt=security_args["key_mgmt_mapping"],
                    retry=client_retry,
                )
        finally:
            with step("Cleanup"):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_check_wifi_credential_config", []))
    def test_wm2_check_wifi_credential_config(self, cfg: dict):
        gw = pytest.gw

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_check_wifi_credential_config")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_connect_wpa3_client", []))
    def test_wm2_connect_wpa3_client(self, cfg: dict):
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            client_retry = cfg.get("client_retry", 2)
            encryption = cfg["encryption"]

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            wifi_security_type = "wpa"

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

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

            if w1.model not in ["linux", "debian"]:
                pytest.skip("A WiFi6 client is required for this testcase, skipping.")

        with step("GW AP creation"):
            assert gw.configure_radio_vif_and_network()
        with step("Client connection"):
            security_args = gw.configure_wifi_security(return_as_dict=True)
            w1.device_api.connect(
                ssid=ssid,
                psk=psk,
                key_mgmt=security_args["key_mgmt_mapping"],
                retry=client_retry,
            )
        with step("Test case"):
            assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_connect_wpa3_leaf", []))
    def test_wm2_connect_wpa3_leaf(self, cfg: dict):
        gw, l1 = pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            device_mode = cfg.get("device_mode", "router")
            encryption = cfg["encryption"]

            # Constant arguments
            wifi_security_type = "wpa"

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
            l1_mac = l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name)[0]

        try:
            with step("VIF reset"):
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=l1_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=True,
                )
            with step("Test case"):
                assert l1_mac in gw.device_api.get_wifi_associated_clients()[0]
        finally:
            with step("Cleanup"):
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.timeout(540)
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
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", None)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

        with step("VIF reset"):
            assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
        with step("Test case"):
            for interface in if_list:
                if interface == "backhaul_ap":
                    assert gw.create_and_configure_bhaul_connection_gw_leaf(
                        channel=channel,
                        leaf_device=l1,
                        gw_radio_band=radio_band,
                        leaf_radio_band=l1_radio_band,
                        ht_mode=ht_mode,
                        wifi_security_type=wifi_security_type,
                        encryption=encryption,
                        skip_gre=True,
                    )
                else:
                    ssid, psk = f"FUT_ssid_{interface}", f"FUT_psk_{interface}"
                    gw_ap_vif_args = {
                        "channel": channel,
                        "ht_mode": ht_mode,
                        "radio_band": radio_band,
                        "wpa_psk": psk,
                        "wifi_security_type": wifi_security_type,
                        "encryption": encryption,
                        "ssid": ssid,
                        "interface_type": interface,
                    }
                    gw.ap_args = gw_ap_vif_args
                    with step(f"GW AP creation - {interface}"):
                        assert gw.configure_radio_vif_and_network()
                    with step("Client connection"):
                        security_args = gw.configure_wifi_security(return_as_dict=True)
                        w1.device_api.connect(
                            ssid=ssid,
                            psk=psk,
                            key_mgmt=security_args["key_mgmt_mapping"],
                            retry=client_retry,
                        )
                    with step("Verify client connection"):
                        assert (
                            gw.execute(
                                "tools/device/ovsdb/wait_ovsdb_entry",
                                f"Wifi_Associated_Clients -w mac {w1_mac}",
                            )[0]
                            == ExpectedShellResult
                        )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_create_wpa3_ap", []))
    def test_wm2_create_wpa3_ap(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            interface_type = cfg.get("interface_type")
            encryption = cfg["encryption"]

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "ssid": ssid,
                "interface_type": interface_type,
            }
            gw.ap_args = gw_ap_vif_args

        with step("Test case"):
            assert gw.configure_radio_vif_and_network()

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_dfs_cac_aborted", []))
    def test_wm2_dfs_cac_aborted(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel_A = cfg.get("channel_A")
            channel_B = cfg.get("channel_B")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            channels = gw.capabilities.get_supported_radio_channels(freq_band=radio_band)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            if not {channel_A, channel_B}.issubset(channels):
                pytest.skip(f"Channels {channel_A} and {channel_B} are not valid for the same radio.")

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel_A,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel_a {channel_A}",
                f"-channel_b {channel_B}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if not pytest.test_wm2_dfs_cac_aborted_first_run:
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.test_wm2_dfs_cac_aborted_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_dfs_cac_aborted", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_ht_mode_and_channel_iteration", []))
    def test_wm2_ht_mode_and_channel_iteration(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_ht_mode_and_channel_iteration", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_immutable_radio_freq_band", []))
    def test_wm2_immutable_radio_freq_band(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            freq_band = cfg.get("freq_band")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
                f"-freq_band {freq_band}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if not pytest.test_wm2_immutable_radio_freq_band_first_run:
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.test_wm2_immutable_radio_freq_band_first_run = True
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_immutable_radio_freq_band", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_immutable_radio_hw_mode", []))
    def test_wm2_immutable_radio_hw_mode(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            custom_hw_mode = cfg.get("custom_hw_mode")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
                f"-custom_hw_mode {custom_hw_mode}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if not pytest.test_wm2_immutable_radio_hw_mode_first_run:
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.test_wm2_immutable_radio_hw_mode_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_immutable_radio_hw_mode", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_immutable_radio_hw_type", []))
    def test_wm2_immutable_radio_hw_type(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            hw_type = cfg.get("hw_type")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
                f"-hw_type {hw_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if not pytest.test_wm2_immutable_radio_hw_type_first_run:
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
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
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            device_mode = cfg.get("device_mode", "router")

            with step("Device type checking"):
                for device_handler in [gw, l1]:
                    device_type = device_handler.capabilities.get_device_type()
                    if device_type != "extender":
                        pytest.skip(f"{device_type.name.upper()} is not an extender, skipping this test case.")

            # GW specific arguments
            gw_phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=gw_radio_band)
            gw_bhaul_sta_if_name = gw.capabilities.get_bhaul_sta_ifname(freq_band=gw_radio_band)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)

            update_ht_mode_args = gw.get_command_arguments(
                "Wifi_Radio_Config",
                "-w",
                "if_name",
                gw_phy_radio_name,
                "-u",
                "ht_mode",
                custom_ht_mode,
            )
            wait_ht_mode_args = gw.get_command_arguments(
                "Wifi_Radio_State",
                "-w",
                "if_name",
                gw_phy_radio_name,
                "-is",
                "ht_mode",
                custom_ht_mode,
            )
            check_ht_mode_args = gw.get_command_arguments(
                custom_ht_mode,
                gw_bhaul_sta_if_name,
                channel,
            )

        try:
            with step("VIF reset"):
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("Ensure WAN connectivity on GW"):
                assert gw.check_wan_connectivity()
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=l1_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=False,
                )
            with step("Ensure WAN connectivity on L1"):
                assert l1.check_wan_connectivity()
            with step(f"Change HT Mode on GW from {ht_mode} to {custom_ht_mode}"):
                assert (
                    gw.execute("tools/device/ovsdb/update_ovsdb_entry", update_ht_mode_args)[0] == ExpectedShellResult
                )
                assert gw.execute("tools/device/ovsdb/wait_ovsdb_entry", wait_ht_mode_args)[0] == ExpectedShellResult
            with step("Test case"):
                assert (
                    l1.execute("tools/device/check_ht_mode_at_os_level", check_ht_mode_args)[0] == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_pre_cac_channel_change_validation", []))
    def test_wm2_pre_cac_channel_change_validation(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel_A = cfg.get("channel_A")
            channel_B = cfg.get("channel_B")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            channels = gw.capabilities.get_supported_radio_channels(freq_band=radio_band)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            if not {channel_A, channel_B}.issubset(channels):
                pytest.skip(f"Channels {channel_A} and {channel_B} are not valid for the same radio.")

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel_A,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel_a {channel_A}",
                f"-channel_b {channel_B}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-reg_domain {gw.regulatory_domain.upper()}",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel_A, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.wm2_last_channel_and_radio_band_used = (channel_A, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_pre_cac_channel_change_validation", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_pre_cac_ht_mode_change_validation", []))
    def test_wm2_pre_cac_ht_mode_change_validation(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode_a = cfg.get("ht_mode_a")
            ht_mode_b = cfg.get("ht_mode_b")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode_a,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode_a {ht_mode_a}",
                f"-ht_mode_b {ht_mode_b}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-reg_domain {gw.regulatory_domain.upper()}",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/wm2/wm2_pre_cac_ht_mode_change_validation", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_bcn_int", []))
    def test_wm2_set_bcn_int(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            bcn_int = cfg.get("bcn_int")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args
            test_args = gw.get_command_arguments(
                phy_radio_name,
                if_name,
                bcn_int,
            )

        if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
            with step("GW AP configuration"):
                assert gw.configure_radio_vif_and_network()
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_bcn_int", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_channel", []))
    def test_wm2_set_channel(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                f"-vif_if_name {if_name}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_channel", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_channel_neg", []))
    def test_wm2_set_channel_neg(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            mismatch_channel = cfg.get("mismatch_channel")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                f"-vif_if_name {if_name}",
                f"-mismatch_channel {mismatch_channel}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_channel_neg", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_ht_mode", []))
    def test_wm2_set_ht_mode(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-vif_if_name {if_name}",
            ]
            test_args = gw.get_command_arguments(*test_args_base)

        with step("GW AP Configuration"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
                assert gw.configure_radio_vif_and_network()
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
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            mismatch_ht_mode = cfg.get("mismatch_ht_mode")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                f"-vif_if_name {if_name}",
                f"-mismatch_ht_mode {mismatch_ht_mode}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

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
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.test_wm2_set_radio_country_first_run = True
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_country", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_thermal_tx_chainmask", []))
    def test_wm2_set_radio_thermal_tx_chainmask(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            with step("Verify correct antenna settings"):
                radio_antennas = gw.capabilities.get_radio_antenna(freq_band=radio_band)
                assert radio_antennas is not None and int(radio_antennas[0])
                radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
                tx_chainmask = radio_max_chainmask
                thermal_tx_chainmask = tx_chainmask >> 1
                assert thermal_tx_chainmask != 0
                valid_chainmasks = [(1 << x) - 1 for x in range(1, 5)]
                assert all(x in valid_chainmasks for x in [thermal_tx_chainmask, tx_chainmask, radio_max_chainmask])

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-if_name {phy_radio_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                f"-vif_if_name {if_name}",
                f"-tx_chainmask {tx_chainmask}",
                f"-thermal_tx_chainmask {thermal_tx_chainmask}",
                f"-radio_band {radio_band.upper()}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

            cleanup_args = gw.get_command_arguments(
                phy_radio_name,
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
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
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            with step("Verify correct antenna settings"):
                radio_antennas = gw.capabilities.get_radio_antenna(freq_band=radio_band)
                assert radio_antennas is not None and int(radio_antennas[0])
                radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
                test_tx_chainmask = radio_max_chainmask >> 1
                valid_chainmasks = [(1 << x) - 1 for x in range(1, 5)]
                assert all(x in valid_chainmasks for x in [test_tx_chainmask, radio_max_chainmask])

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"

            # GW specific arguments
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)

            default_tx_chainmask_args = gw.get_command_arguments(
                "Wifi_Radio_State",
                "tx_chainmask",
                "-w",
                "if_name",
                phy_radio_name,
            )

            with step("Acquire default TX chainmask and thermal TX chainmask values"):
                default_tx_chainmask_ec, default_tx_chainmask, tx_std_err = gw.execute(
                    "tools/device/ovsdb/get_ovsdb_entry_value",
                    default_tx_chainmask_args,
                )
                assert (
                    default_tx_chainmask is not None
                    and default_tx_chainmask != ""
                    and default_tx_chainmask_ec == ExpectedShellResult
                )

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args = gw.get_command_arguments(
                phy_radio_name,
                radio_band,
                test_tx_chainmask,
                radio_max_chainmask,
                default_tx_chainmask,
            )

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            pytest.wm2_last_channel_and_radio_band_used = (channel, radio_band)
        with step("GW AP creation"):
            assert gw.configure_radio_vif_and_network()
        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_tx_chainmask", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_radio_vif_configs", []))
    def test_wm2_set_radio_vif_configs(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            custom_channel = cfg.get("custom_channel")
            radio_band = cfg.get("radio_band")
            ht_mode = cfg.get("ht_mode")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-vif_radio_idx {vif_radio_idx}",
                f"-if_name {phy_radio_name}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                f"-vif_if_name {if_name}",
                f"-custom_channel {custom_channel}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("Test case"):
            assert gw.execute_with_logging("tests/wm2/wm2_set_radio_vif_configs", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_set_ssid", []))
    def test_wm2_set_ssid(self, cfg: dict):
        fut_configurator, gw = pytest.fut_configurator, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            ssid = str(cfg.get("ssid"))
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

            # Constant arguments
            psk = fut_configurator.base_psk
            interface_type = "home_ap"
            mode = "ap"

            # GW specific arguments
            if_name = gw.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
            vif_radio_idx = gw.capabilities.get_iftype_vif_radio_idx(iftype=interface_type)
            phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            hw_mode = gw.capabilities.get_radio_hw_mode(freq_band=radio_band)

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "interface_type": interface_type,
            }

            gw.ap_args = gw_ap_vif_args

            test_args_base = [
                f"-vif_radio_idx {vif_radio_idx}",
                f"-if_name {phy_radio_name}",
                f"-ssid '{ssid}'",
                f"-channel {channel}",
                f"-ht_mode {ht_mode}",
                f"-hw_mode {hw_mode}",
                f"-mode {mode}",
                f"-vif_if_name {if_name}",
                "-channel_mode manual",
                "-enabled true",
                f"-wifi_security_type {wifi_security_type}",
            ]
            test_args_base += gw.configure_wifi_security()
            test_args = gw.get_command_arguments(*test_args_base)

        with step("VIF reset"):
            if pytest.wm2_last_channel_and_radio_band_used != (channel, radio_band):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
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
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
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

            # L1 STA arguments
            l1_to_l2_sta_args = {
                "vif_name": l1_to_l2_bhaul_sta_if_name,
                "wpa_psk": psk,
                "ssid": ssid,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "reset_vif": True,
            }

            # L2 AP arguments
            l2_ap_args = {
                "channel": l2_channel,
                "ht_mode": ht_mode,
                "radio_band": l2_radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "interface_type": "backhaul_ap",
                "bridge": False,
                "reset_vif": True,
            }

            l2.ap_args = l2_ap_args

        try:
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=gw_channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=True,
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
                assert l2.configure_radio_vif_and_network()
            with step("Determine L2 MAC at runtime"):
                l2_ap_vif_mac = l2.device_api.iface.get_vif_mac(l2_bhaul_ap_if_name)[0]
                if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                    raise RuntimeError("Failed to retrieve L2 MAC address")
            with step("L1 STA configuration"):
                l1_to_l2_sta_args.update({"parent": l2_ap_vif_mac})
                l1.sta_args = l1_to_l2_sta_args
                assert l1.configure_sta_interface()
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
                multi_device_script_execution(devices=[gw, l1, l2], script="tools/device/vif_reset")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_topology_change_change_parent_same_band_change_channel", []))
    def test_wm2_topology_change_change_parent_same_band_change_channel(self, cfg: dict):
        fut_configurator, gw, l1, l2 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.l2

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            gw_channel = cfg.get("gw_channel")
            leaf_channel = cfg.get("leaf_channel")
            ht_mode = cfg.get("ht_mode")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
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

            # L2 AP arguments
            l2_ap_args = {
                "channel": leaf_channel,
                "ht_mode": ht_mode,
                "radio_band": l2_radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "interface_type": "backhaul_ap",
                "bridge": False,
                "reset_vif": True,
            }

            l2.ap_args = l2_ap_args

        try:
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=gw_channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=l1_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=True,
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
                assert l2.configure_radio_vif_and_network()
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
                multi_device_script_execution(devices=[gw, l1, l2], script="tools/device/vif_reset")

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
            wifi_security_type = cfg.get("wifi_security_type", "wpa")

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

            # L2 AP arguments
            l2_ap_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": l2_radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "interface_type": "backhaul_ap",
                "bridge": False,
                "reset_vif": True,
            }

            l2.ap_args = l2_ap_args

        try:
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=l1_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=True,
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
                assert l2.configure_radio_vif_and_network()
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
                multi_device_script_execution(devices=[gw, l1, l2], script="tools/device/vif_reset")

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
        fut_configurator, gw, w1 = pytest.fut_configurator, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 2)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

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

        with step("GW AP creation"):
            assert gw.configure_radio_vif_and_network()
        with step("Client connection"):
            security_args = gw.configure_wifi_security(return_as_dict=True)
            w1.device_api.connect(
                ssid=ssid,
                psk=psk,
                key_mgmt=security_args["key_mgmt_mapping"],
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
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
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

            gw_update_csa_channel_args = gw.get_command_arguments(
                "Wifi_Radio_Config",
                "-w",
                "if_name",
                gw_phy_radio_name,
                "-u",
                "channel",
                csa_channel,
            )
            gw_wait_csa_channel_args = gw.get_command_arguments(
                "Wifi_Radio_State",
                "-w",
                "if_name",
                gw_phy_radio_name,
                "-is",
                "channel",
                csa_channel,
            )
            l1_wait_csa_channel_args = gw.get_command_arguments(
                "Wifi_Radio_State",
                "-w",
                "if_name",
                l1_phy_radio_name,
                "-is",
                "channel",
                csa_channel,
            )

        try:
            with step("VIF reset"):
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=l1_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=False,
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
                    gw.execute("tools/device/ovsdb/update_ovsdb_entry", gw_update_csa_channel_args)[0]
                    == ExpectedShellResult
                )
            with step("Wait for channel on GW"):
                assert (
                    gw.execute("tools/device/ovsdb/wait_ovsdb_entry", gw_wait_csa_channel_args)[0]
                    == ExpectedShellResult
                )
            with step("Test case"):
                # L1: verify channel switch
                assert (
                    l1.execute("tools/device/ovsdb/wait_ovsdb_entry", l1_wait_csa_channel_args)[0]
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
                multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_verify_gre_tunnel_gw_leaf", []))
    def test_wm2_verify_gre_tunnel_gw_leaf(self, cfg: dict):
        fut_configurator, gw, l1, w1 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            ping_wan_ip = cfg.get("ping_wan_ip", "1.1.1.1")
            client_retry = cfg.get("client_retry", 2)

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            l1_home_ap_ssid, l1_home_ap_psk = f"{ssid}_home", f"{psk}_home"

        with step("VIF reset"):
            multi_device_script_execution(devices=[gw, l1], script="tools/device/vif_reset")
        with step("Put GW into router mode"):
            assert gw.configure_device_mode(device_mode="router")
        with step("Ensure WAN connectivity on GW"):
            assert gw.check_wan_connectivity()
        with step("GW AP and L1 STA creation"):
            assert gw.create_and_configure_bhaul_connection_gw_leaf(
                channel=channel,
                leaf_device=l1,
                gw_radio_band=gw_radio_band,
                leaf_radio_band=l1_radio_band,
                ht_mode=ht_mode,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                skip_gre=False,
            )
        with step("L1 Home AP configuration"):
            # L1 AP arguments
            l1_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": l1_radio_band,
                "wpa_psk": l1_home_ap_psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": l1_home_ap_ssid,
                "reset_vif": False,
            }

            l1.ap_args = l1_ap_vif_args
            assert l1.configure_radio_vif_and_network()
        with step("Client connection to LEAF"):
            security_args = l1.configure_wifi_security(return_as_dict=True)
            w1.device_api.connect(
                ssid=l1_home_ap_ssid,
                psk=l1_home_ap_psk,
                key_mgmt=security_args["key_mgmt_mapping"],
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
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 2)

            # GW specific arguments
            gw_home_ap_if_name = gw.capabilities.get_home_ap_ifname(radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            # Constant arguments
            ssid = fut_configurator.base_ssid
            psk = None if encryption.casefold() == "open" else fut_configurator.base_psk

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "encryption": encryption,
                "wifi_security_type": wifi_security_type,
                "ssid": ssid,
                "reset_vif": False,
            }

            gw.ap_args = gw_ap_vif_args

            check_ap_args = gw.get_command_arguments(
                "Wifi_VIF_State",
                "-w",
                "if_name",
                gw_home_ap_if_name,
                "-is",
                "enabled",
                "true",
            )

        with step("VIF reset"):
            assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
        with step("GW AP creation"):
            assert gw.configure_radio_vif_and_network()
        with step("Test case"):
            assert gw.execute("tools/device/ovsdb/wait_ovsdb_entry", check_ap_args)[0] == ExpectedShellResult
        with step("Client connection"):
            security_args = gw.configure_wifi_security(return_as_dict=True)
            w1.device_api.connect(
                ssid=ssid,
                psk=psk,
                key_mgmt=security_args["key_mgmt_mapping"],
                retry=client_retry,
            )
        with step("Verify client connection"):
            assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.timeout(540)
    @pytest.mark.parametrize("cfg", wm2_config.get("wm2_wifi_security_mix_on_multiple_aps", []))
    def test_wm2_wifi_security_mix_on_multiple_aps(self, cfg: dict):
        fut_configurator, gw, l1, w1 = pytest.fut_configurator, pytest.gw, pytest.l1, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            if_list = cfg.get("if_list")
            encryption_list = cfg["encryption_list"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", None)

            # Constant arguments
            base_ssid, base_psk = fut_configurator.base_ssid, fut_configurator.base_psk

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)

            # W1 specific arguments
            wlan_if_name = w1.device_config.get("wlan_if_name")
            w1_mac = w1.device_api.get_mac(if_name=wlan_if_name)

            encryption_cycle = cycle(encryption_list)

        with step("VIF reset"):
            assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
        with step("Test case"):
            for interface in if_list:
                ssid, psk = get_str_hash(f"{base_ssid}_{interface}"), f"{base_psk}_{interface}"
                encryption = next(encryption_cycle)

                if interface == "backhaul_ap":
                    assert gw.create_and_configure_bhaul_connection_gw_leaf(
                        channel=channel,
                        leaf_device=l1,
                        gw_radio_band=radio_band,
                        leaf_radio_band=radio_band,
                        ht_mode=ht_mode,
                        wifi_security_type=wifi_security_type,
                        encryption=encryption,
                        skip_gre=True,
                    )
                    l1_mac = "".join(l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name))
                    assert l1_mac in gw.device_api.get_wifi_associated_clients()
                else:
                    gw_ap_vif_args = {
                        "channel": channel,
                        "ht_mode": ht_mode,
                        "radio_band": radio_band,
                        "wpa_psk": psk,
                        "wifi_security_type": wifi_security_type,
                        "encryption": encryption,
                        "ssid": ssid,
                        "interface_type": interface,
                    }
                    gw.ap_args = gw_ap_vif_args
                    assert gw.configure_radio_vif_and_network()

                    security_args = gw.configure_wifi_security(return_as_dict=True)
                    w1.device_api.connect(
                        ssid=ssid,
                        psk=psk,
                        key_mgmt=security_args["key_mgmt_mapping"],
                        retry=client_retry,
                    )
                    assert w1_mac in gw.device_api.get_wifi_associated_clients()
