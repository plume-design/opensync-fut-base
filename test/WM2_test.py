import time
from pathlib import Path

import pytest

from framework.lib.fut_lib import (
    allure_attach_to_report,
    get_command_arguments,
    multi_device_script_execution,
    reboot_pods_and_wait_available,
    step,
)
from lib_testbed.generic.util import sniffing_utils
from lib_testbed.generic.util.common import compare_fw_versions
from lib_testbed.generic.util.logger import log


test_wm2_dfs_cac_aborted_first_run = False
test_wm2_immutable_radio_hw_mode_first_run = False
test_wm2_immutable_radio_freq_band_first_run = False
test_wm2_immutable_radio_hw_type_first_run = False
test_wm2_set_radio_country_first_run = False
wm2_last_channel_and_radio_band_used = None


@pytest.fixture(scope="module")
def wm2_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = gw_handler.wireless_manager
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
            gw_handler.device_test_setup(test_suite_name=module_name.lower(), setup_args=manager_name)

        if "l1_handler" in fixturenames and "6G" in l1_handler.capabilities.get_supported_bands():
            l1_handler.create_interface_object(
                channel=5,
                ht_mode="HT40",
                radio_band="6g",
                encryption="WPA3",
                interface_role="home_ap",
            )
            assert l1_handler.interface["home_ap"].configure_interface() == 0
    yield


def test_wm2_check_wifi_credential_config(wm2_setup, gw_handler):
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_check_wifi_credential_config")[0] == 0


def test_wm2_connect_client(wm2_setup, parametrized_test_config, gw_handler, w1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        client_retry = parametrized_test_config.get("client_retry", 2)
        encryption = parametrized_test_config["encryption"]

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

    try:
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Client connection"):
            w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=gw_handler)
        with step("Test case"):
            assert w1_mac in gw_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()


def test_wm2_connect_leaf(wm2_setup, parametrized_test_config, gw_handler, l1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        device_mode = parametrized_test_config.get("device_mode", "router")
        encryption = parametrized_test_config["encryption"]

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
        l1_mac = l1_handler.get_if_mac(if_name=l1_bhaul_sta_if_name, if_role="backhaul_sta")

    try:
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("GW AP and L1 STA creation"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=None,
            )
        with step("Test case"):
            assert l1_mac in gw_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            gw_handler.interface["backhaul_ap"].vif_reset()
            l1_handler.interface["backhaul_sta"].vif_reset()


@pytest.mark.timeout(720)
def test_wm2_create_all_aps_per_radio(wm2_setup, parametrized_test_config, gw_handler, l1_handler, w1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        if_list = parametrized_test_config.get("if_list")
        encryption = parametrized_test_config["encryption"]
        client_retry = parametrized_test_config.get("client_retry", None)

        # W1 specific arguments
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

    try:
        with step("Test case"):
            for interface in if_list:
                if gw_handler.capabilities.get_ifname(iftype=interface, freq_band=radio_band) is None:
                    log.info(f"Interface {interface} is not supported on {gw_handler.model}.")
                    continue
                if interface == "backhaul_ap":
                    assert gw_handler.create_and_configure_backhaul(
                        channel=channel,
                        leaf_device=l1_handler,
                        radio_band=radio_band,
                        ht_mode=ht_mode,
                        encryption=encryption,
                        mesh_type=None,
                    )
                else:
                    ssid, psk = f"FUT_ssid_{interface}", f"FUT_psk_{interface}"
                    gw_handler.create_interface_object(
                        channel=channel,
                        ht_mode=ht_mode,
                        radio_band=radio_band,
                        encryption=encryption,
                        interface_role=interface,
                        ssid=ssid,
                        wpa_psks=psk,
                    )
                    with step(f"GW AP creation - {interface}"):
                        assert gw_handler.interface[interface].configure_interface() == 0
                    with step("Client connection"):
                        w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=gw_handler)
                    with step("Verify client connection"):
                        assert w1_mac in gw_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            gw_handler.vif_reset()


def test_wm2_create_ap(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        interface_type = parametrized_test_config.get("interface_type")
        encryption = parametrized_test_config["encryption"]

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role=interface_type,
        )

    try:
        with step("Test case"):
            assert gw_handler.interface[interface_type].configure_interface() == 0
    finally:
        with step("Cleanup"):
            gw_handler.interface[interface_type].vif_reset()


def test_wm2_dfs_cac_aborted(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel_A = parametrized_test_config.get("channel_A")
        channel_B = parametrized_test_config.get("channel_B")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        channels = gw_handler.capabilities.get_supported_radio_channels(freq_band=radio_band)
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        if not {channel_A, channel_B}.issubset(channels):
            pytest.skip(f"Channels {channel_A} and {channel_B} are not valid for the same radio.")

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel_A,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global test_wm2_dfs_cac_aborted_first_run
        if not test_wm2_dfs_cac_aborted_first_run:
            gw_handler.vif_reset()
        test_wm2_dfs_cac_aborted_first_run = True
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_dfs_cac_aborted", test_args)[0] == 0


def test_wm2_ht_mode_and_channel_iteration(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_ht_mode_and_channel_iteration", test_args)[0] == 0


def test_wm2_immutable_radio_freq_band(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        freq_band = parametrized_test_config.get("freq_band")

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global test_wm2_immutable_radio_freq_band_first_run
        if not test_wm2_immutable_radio_freq_band_first_run:
            gw_handler.vif_reset()
        test_wm2_immutable_radio_freq_band_first_run = True
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_immutable_radio_freq_band", test_args)[0] == 0


def test_wm2_immutable_radio_hw_mode(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        custom_hw_mode = parametrized_test_config.get("custom_hw_mode")

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global test_wm2_immutable_radio_hw_mode_first_run
        if not test_wm2_immutable_radio_hw_mode_first_run:
            gw_handler.vif_reset()
        test_wm2_immutable_radio_hw_mode_first_run = True
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_immutable_radio_hw_mode", test_args)[0] == 0


def test_wm2_immutable_radio_hw_type(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        hw_type = parametrized_test_config.get("hw_type")

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global test_wm2_immutable_radio_hw_type_first_run
        if not test_wm2_immutable_radio_hw_type_first_run:
            gw_handler.vif_reset()
        test_wm2_immutable_radio_hw_type_first_run = True
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_immutable_radio_hw_type", test_args)[0] == 0


def test_wm2_pre_cac_channel_change_validation(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel_A = parametrized_test_config.get("channel_A")
        channel_B = parametrized_test_config.get("channel_B")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        channels = gw_handler.capabilities.get_supported_radio_channels(freq_band=radio_band)
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        if not {channel_A, channel_B}.issubset(channels):
            pytest.skip(f"Channels {channel_A} and {channel_B} are not valid for the same radio.")

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel_A,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
            f"-reg_domain {gw_handler.capabilities.get_regulatory_domain().upper()}",
            "-wpa true",
            f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
            f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
            f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
        )

    with step("VIF reset"):
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel_A, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel_A, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_pre_cac_channel_change_validation", test_args)[0] == 0


def test_wm2_pre_cac_ht_mode_change_validation(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode_a = parametrized_test_config.get("ht_mode_a")
        ht_mode_b = parametrized_test_config.get("ht_mode_b")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode_a,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
            f"-reg_domain {gw_handler.capabilities.get_regulatory_domain().upper()}",
            "-wpa true",
            f"-wpa_psks {ovsdb_ap_args['wpa_psks']}",
            f"-wpa_oftags {ovsdb_ap_args['wpa_oftags']}",
            f"-wpa_key_mgmt {ovsdb_ap_args['wpa_key_mgmt']}",
        )

    with step("VIF reset"):
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_pre_cac_ht_mode_change_validation", test_args)[0] == 0


def test_wm2_set_bcn_int(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        bcn_int = parametrized_test_config.get("bcn_int")

        # Constant arguments
        interface_type = "home_ap"

        # GW specific arguments
        vif_if_name = gw_handler.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
        phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role=interface_type,
        )

        test_args = get_command_arguments(
            phy_radio_name,
            vif_if_name,
            bcn_int,
        )

    global wm2_last_channel_and_radio_band_used
    if wm2_last_channel_and_radio_band_used != (channel, radio_band):
        with step("GW AP configuration"):
            assert gw_handler.interface[interface_type].configure_interface() == 0
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_bcn_int", test_args)[0] == 0


def test_wm2_set_channel(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_channel", test_args)[0] == 0


def test_wm2_set_channel_neg(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        mismatch_channel = parametrized_test_config.get("mismatch_channel")

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_channel_neg", test_args)[0] == 0


def test_wm2_set_ht_mode(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # Constant arguments
        interface_type = "home_ap"

        # GW specific arguments
        vif_if_name = gw_handler.capabilities.get_ifname(freq_band=radio_band, iftype=interface_type)
        phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role=interface_type,
        )

        test_args = get_command_arguments(
            f"-radio_if_name {phy_radio_name}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-vif_if_name {vif_if_name}",
        )

    with step("GW AP Configuration"):
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            assert gw_handler.execute("tools/device/vif_reset")[0] == 0
            assert gw_handler.interface[interface_type].configure_interface() == 0
        else:
            allure_attach_to_report(
                name="log_pod_gw",
                body=f"GW AP with the channel {channel} on the {radio_band} radio band already exists.",
            )
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_ht_mode", test_args)[0] == 0


def test_wm2_set_ht_mode_neg(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        mismatch_ht_mode = parametrized_test_config.get("mismatch_ht_mode")
        max_ht_mode = int(gw_handler.capabilities.get_max_channel_width(radio_band))
        if int(mismatch_ht_mode.removeprefix("HT")) <= max_ht_mode:
            pytest.skip(f"Bandwidth {mismatch_ht_mode} should be lower than {max_ht_mode} for {radio_band}.")

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_ht_mode_neg", test_args)[0] == 0


def test_wm2_set_radio_country(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        country = parametrized_test_config.get("country")
        radio_band = parametrized_test_config.get("radio_band")

        # GW specific arguments
        phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)

        test_args = get_command_arguments(
            phy_radio_name,
            country,
        )

    with step("VIF reset"):
        global test_wm2_set_radio_country_first_run
        if not test_wm2_set_radio_country_first_run:
            gw_handler.vif_reset()
        test_wm2_set_radio_country_first_run = True
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_radio_country", test_args)[0] == 0


def test_wm2_set_radio_thermal_tx_chainmask(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        with step("Verify correct antenna settings"):
            radio_antennas = gw_handler.capabilities.get_radio_antenna(freq_band=radio_band)
            assert radio_antennas is not None and int(radio_antennas[0])
            radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
            # Override autogenerated radio_max_chainmask from inputs, if needed
            tx_chainmask = parametrized_test_config.get("tx_chainmask", radio_max_chainmask)
            thermal_tx_chainmask = tx_chainmask >> 1
            assert thermal_tx_chainmask != 0

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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

        cleanup_args = get_command_arguments(
            ovsdb_ap_args["radio_if_name"],
        )

    with step("VIF reset"):
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_radio_thermal_tx_chainmask", test_args)[0] == 0
    with step("Cleanup"):
        assert (
            gw_handler.execute_with_logging("tests/wm2/wm2_set_radio_thermal_tx_chainmask_cleanup", cleanup_args)[0]
            == 0
        )


def test_wm2_set_radio_tx_chainmask(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        with step("Verify correct antenna settings"):
            radio_antennas = gw_handler.capabilities.get_radio_antenna(freq_band=radio_band)
            assert radio_antennas is not None and int(radio_antennas[0])
            radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
            # Override autogenerated radio_max_chainmask from inputs, if needed
            tx_chainmask = parametrized_test_config.get("tx_chainmask", radio_max_chainmask)
            test_tx_chainmask = tx_chainmask >> 1

        # GW specific arguments
        phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)

        with step("Acquire default TX chainmask and thermal TX chainmask values"):
            default_tx_chainmask = gw_handler.ovsdb.get(
                table="Wifi_Radio_State",
                select="tx_chainmask",
                where=f"if_name=={phy_radio_name}",
            )
            assert default_tx_chainmask is not None and default_tx_chainmask != ""

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
            ovsdb_ap_args["radio_if_name"],
            radio_band,
            test_tx_chainmask,
            tx_chainmask,
            default_tx_chainmask,
        )

    with step("VIF reset"):
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("GW AP creation"):
        assert gw_handler.interface["home_ap"].configure_interface() == 0
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_radio_tx_chainmask", test_args)[0] == 0


def test_wm2_set_radio_tx_power(wm2_setup, parametrized_test_config, gw_handler):
    min_opensync_version = "6.4.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        tx_power = parametrized_test_config.get("tx_power")

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_radio_tx_power", test_args)[0] == 0


def test_wm2_set_radio_vif_configs(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        custom_channel = parametrized_test_config.get("custom_channel")
        radio_band = parametrized_test_config.get("radio_band")
        ht_mode = parametrized_test_config.get("ht_mode")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_radio_vif_configs", test_args)[0] == 0


def test_wm2_set_ssid(wm2_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        hw_mode = gw_handler.capabilities.get_radio_hw_mode(freq_band=radio_band)

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Extract AP arguments and ensure they are compliant with the OVSDB format
        ssid = gw_handler.interface["home_ap"].ssid_raw
        ap_args = gw_handler.interface["home_ap"].combined_args
        ovsdb_ap_args = {key: gw_handler.ovsdb.python_value_to_ovsdb_value(value) for key, value in ap_args.items()}

        test_args = get_command_arguments(
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
        global wm2_last_channel_and_radio_band_used
        if wm2_last_channel_and_radio_band_used != (channel, radio_band):
            gw_handler.vif_reset()
        wm2_last_channel_and_radio_band_used = (channel, radio_band)
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/wm2/wm2_set_ssid", test_args)[0] == 0


def test_wm2_topology_change_change_parent_change_band_change_channel(
    wm2_setup,
    parametrized_test_config,
    gw_handler,
    l1_handler,
    l2_handler,
):
    if gw_handler.mlo_bh:
        pytest.skip("Not applicable for MLO backhaul capable devices.")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        gw_channel = parametrized_test_config.get("gw_channel")
        l2_channel = parametrized_test_config.get("leaf_channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("gw_radio_band")
        l2_radio_band = parametrized_test_config.get("leaf_radio_band")

        # Constant arguments
        ssid, psk = gw_handler.base_ssid, gw_handler.base_psk

        # L1 specific arguments
        l1_to_gw_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
        l1_to_gw_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(l1_to_gw_radio_band)
        l1_to_l2_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(l2_channel, l2_radio_band)
        l1_to_l2_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(l1_to_l2_radio_band)

        # L2 specific arguments
        l2_bhaul_ap_if_name = l2_handler.capabilities.get_bhaul_ap_ifname(l2_radio_band)

        with step("6G radio band compatibility check"):
            if gw_radio_band == "6g":
                for node in [gw_handler, l1_handler, l2_handler]:
                    if "6G" not in node.capabilities.get_supported_bands():
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
        l2_handler.create_interface_object(
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
            assert gw_handler.create_and_configure_backhaul(
                channel=gw_channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=None,
                ssid=ssid,
                wpa_psks=psk,
            )
        with step("Determine L1 STA MAC at runtime"):
            mac_list = l1_handler.iface.get_vif_mac(l1_to_gw_bhaul_sta_if_name)
            assert mac_list, f"Can not get {l1_to_gw_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
            l1_sta_vif_mac = mac_list[0]
            if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                raise RuntimeError("Failed to retrieve L1 MAC address")
            l1_sta_mac_args = get_command_arguments(l1_sta_vif_mac)
        with step("Verify GW associated clients"):
            assert gw_handler.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == 0
        with step("L2 AP creation"):
            assert l2_handler.interface["backhaul_ap"].configure_interface() == 0
        with step("Determine L2 MAC at runtime"):
            mac_list = l2_handler.iface.get_vif_mac(l2_bhaul_ap_if_name)
            assert mac_list, f"Can not get {l2_bhaul_ap_if_name} MAC on {l2_handler.nickname.upper()}"
            l2_ap_vif_mac = mac_list[0]
            if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                raise RuntimeError("Failed to retrieve L2 MAC address")
        with step("L1 STA configuration"):
            # Channel and radio band used only as metadata in STA configuration, not pushed to the device
            l1_handler.create_interface_object(
                channel=l2_channel,
                ht_mode=ht_mode,
                radio_band=l1_to_l2_radio_band,
                encryption=encryption,
                interface_role="backhaul_sta",
                ssid=ssid,
                wpa_psks=psk,
                parent=l2_ap_vif_mac,
            )
            assert l1_handler.interface["backhaul_sta"].configure_interface(vif_reset=True) == 0
        with step("Determine L1 STA MAC at runtime"):
            mac_list = l1_handler.iface.get_vif_mac(l1_to_l2_bhaul_sta_if_name)
            assert mac_list, f"Can not get {l1_to_l2_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
            l1_sta_vif_mac = mac_list[0]
            if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                raise RuntimeError("Failed to retrieve L1 MAC address")
            l1_sta_mac_args = get_command_arguments(l1_sta_vif_mac)
        with step("Testcase - Verify topology change"):
            assert l2_handler.execute("tools/device/check_wifi_client_associated", l1_sta_mac_args)[0] == 0
    finally:
        with step("Cleanup"):
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            l2_handler.vif_reset()


def test_wm2_topology_change_change_parent_same_band_change_channel(
    wm2_setup,
    parametrized_test_config,
    gw_handler,
    l1_handler,
    l2_handler,
):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        gw_channel = parametrized_test_config.get("channel")
        leaf_channel = parametrized_test_config.get("leaf_channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        encryption = parametrized_test_config["encryption"]
        gw_radio_band = parametrized_test_config.get("radio_band")

        # Constant arguments
        ssid, psk = gw_handler.base_ssid, gw_handler.base_psk

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(l1_radio_band)

        # L2 specific arguments
        l2_radio_band = l2_handler.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
        l2_bhaul_ap_if_name = l2_handler.capabilities.get_bhaul_ap_ifname(l2_radio_band)

        with step("6G radio band compatibility check"):
            if gw_radio_band == "6g":
                for node in [gw_handler, l1_handler, l2_handler]:
                    if "6G" not in node.capabilities.get_supported_bands():
                        pytest.skip(f"6G radio band is not supported on {node}")
                    else:
                        log.info("6G radio band is supported on all required devices")
            else:
                log.info("6G radio band was not selected. The 6G radio band compatibility check is not necessary")

        # L2 interface creation
        l2_handler.create_interface_object(
            channel=leaf_channel,
            ht_mode=ht_mode,
            radio_band=l2_radio_band,
            encryption=encryption,
            interface_role="backhaul_ap",
            ssid=ssid,
            wpa_psks=psk,
        )

        def _full_vif_reset():
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            l2_handler.vif_reset()

    try:
        with step("VIF reset"):
            _full_vif_reset()
        with step("GW AP and L1 STA creation"):
            assert gw_handler.create_and_configure_backhaul(
                channel=gw_channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=None,
                ssid=ssid,
                wpa_psks=psk,
            )
        with step("Determine L1 STA MAC at runtime"):
            l1_sta_vif_mac = l1_handler.get_if_mac(if_name=l1_bhaul_sta_if_name, if_role="backhaul_sta")
            if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                raise RuntimeError("Failed to retrieve L1 MAC address")
        with step("Verify GW associated leaf nodes"):
            assert l1_sta_vif_mac in gw_handler.get_wifi_associated_clients()
        with step("L2 AP creation"):
            assert l2_handler.interface["backhaul_ap"].configure_interface() == 0
        with step("Determine L2 AP MAC at runtime"):
            l2_ap_vif_mac = l2_handler.get_if_mac(if_name=l2_bhaul_ap_if_name, if_role="backhaul_ap", use_mld_mac=False)
            if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                raise RuntimeError("Failed to retrieve L2 MAC address")
        with step("Testcase - Update parent"):
            bhaul_sta_update_parent_args = get_command_arguments(
                l1_bhaul_sta_if_name,
                l2_ap_vif_mac,
            )
            assert l1_handler.execute_with_logging("tools/device/set_parent", bhaul_sta_update_parent_args)[0] == 0
        with step("Testcase - Verify topology change"):
            assert l1_sta_vif_mac in l2_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            _full_vif_reset()


def test_wm2_topology_change_change_parent_same_band_same_channel(
    wm2_setup,
    parametrized_test_config,
    gw_handler,
    l1_handler,
    l2_handler,
):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]

        # Constant arguments
        ssid, psk = gw_handler.base_ssid, gw_handler.base_psk

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(l1_radio_band)

        # L2 specific arguments
        l2_radio_band = l2_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l2_bhaul_ap_if_name = l2_handler.capabilities.get_bhaul_ap_ifname(l2_radio_band)

        with step("6G radio band compatibility check"):
            if gw_radio_band == "6g":
                for node in [gw_handler, l1_handler, l2_handler]:
                    if "6G" not in node.capabilities.get_supported_bands():
                        pytest.skip(f"6G radio band is not supported on {node}")
                    else:
                        log.info("6G radio band is supported on all required devices")
            else:
                log.info("6G radio band was not selected. The 6G radio band compatibility check is not necessary")

        # L2 interface creation
        l2_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=l2_radio_band,
            encryption=encryption,
            interface_role="backhaul_ap",
            ssid=ssid,
            wpa_psks=psk,
        )

        def _full_vif_reset():
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            l2_handler.vif_reset()

    try:
        with step("VIF reset"):
            _full_vif_reset()
        with step("GW AP and L1 STA creation"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=None,
                ssid=ssid,
                wpa_psks=psk,
            )
        with step("Determine L1 STA MAC at runtime"):
            l1_sta_vif_mac = l1_handler.get_if_mac(if_name=l1_bhaul_sta_if_name, if_role="backhaul_sta")
            if not l1_sta_vif_mac or l1_sta_vif_mac == "":
                raise RuntimeError("Failed to retrieve L1 MAC address")
        with step("Verify GW associated leaf nodes"):
            assert l1_sta_vif_mac in gw_handler.get_wifi_associated_clients()
        with step("L2 AP creation"):
            assert l2_handler.interface["backhaul_ap"].configure_interface() == 0
        with step("Determine L2 AP MAC at runtime"):
            l2_ap_vif_mac = l2_handler.get_if_mac(if_name=l2_bhaul_ap_if_name, if_role="backhaul_ap", use_mld_mac=False)
            if not l2_ap_vif_mac or l2_ap_vif_mac == "":
                raise RuntimeError("Failed to retrieve L2 MAC address")
        with step("Testcase - Update parent"):
            bhaul_sta_update_parent_args = get_command_arguments(
                l1_bhaul_sta_if_name,
                l2_ap_vif_mac,
            )
            assert l1_handler.execute_with_logging("tools/device/set_parent", bhaul_sta_update_parent_args)[0] == 0
        with step("Testcase - Verify topology change"):
            assert l1_sta_vif_mac in l2_handler.get_wifi_associated_clients()
    finally:
        with step("Cleanup"):
            _full_vif_reset()


def test_wm2_verify_leaf_channel_change(wm2_setup, parametrized_test_config, gw_handler, l1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        csa_channel = parametrized_test_config.get("csa_channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        device_mode = parametrized_test_config.get("device_mode", "router")
        encryption = parametrized_test_config["encryption"]

        # GW specific arguments
        gw_phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=gw_radio_band)

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_phy_radio_name = l1_handler.capabilities.get_phy_radio_ifname(freq_band=l1_radio_band)

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
            multi_device_script_execution(devices=[gw_handler, l1_handler], script="tools/device/vif_reset")
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("GW AP and L1 STA creation"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=None,
            )
        with step("Retrieve L1 backhaul STA IP"):
            l1_bhaul_iface = l1_handler.interface["backhaul_sta"].network_if_name
            l1_bhaul_sta_ip = l1_handler.get_ips(iface=l1_bhaul_iface).get("ipv4")
            if not l1_bhaul_sta_ip:
                raise ValueError(f"Unable to retrieve the IP address associated with {l1_bhaul_iface}")
        with step("Ping L1 from GW"):
            # Start pinging the L1 device and save the ping statistics in a log file
            gw_ping_args = get_command_arguments(
                l1_bhaul_sta_ip,
                ping_log_file,
            )
            assert gw_handler.execute("tools/device/ping_check", gw_ping_args, background_execution=True)[0] == 0
        with step("Trigger CSA on GW"):
            assert (
                gw_handler.ovsdb.set_value(
                    table="Wifi_Radio_Config",
                    value=gw_csa_channel_args,
                    where=f"if_name=={gw_phy_radio_name}",
                )[0]
                == 0
            )
        with step("Wait for channel on GW"):
            assert (
                gw_handler.ovsdb.wait_for_value(
                    table="Wifi_Radio_State",
                    value=gw_csa_channel_args,
                    where=f"if_name=={gw_phy_radio_name}",
                )[0]
                == 0
            )
        with step("Test case"):
            # L1: verify channel switch
            assert (
                l1_handler.ovsdb.wait_for_value(
                    table="Wifi_Radio_State",
                    value=l1_csa_channel_args,
                    where=f"if_name=={l1_phy_radio_name}",
                )[0]
                == 0
            )
            # GW: stop pinging L1
            assert gw_handler.run_raw("pkill -f ping_check.sh")[0] == 0
            # GW: verify 0% packet loss
            gw_handler.get_log_tail_file_and_attach_to_allure(log_tail_file_name=ping_log_file)
            assert gw_handler.execute("tools/device/retrieve_ping_packet_loss", ping_log_file)[0] == 0
    finally:
        with step("Cleanup"):
            # Kill ping again in case the command was not executed as part of the test case steps
            gw_handler.run_raw("pkill -f ping_check.sh")
            gw_handler.vif_reset()
            l1_handler.vif_reset()


def test_wm2_verify_gre_tunnel_gw_leaf(wm2_setup, parametrized_test_config, gw_handler, l1_handler, w1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        ping_wan_ip = parametrized_test_config.get("ping_wan_ip", "1.1.1.1")
        client_retry = parametrized_test_config.get("client_retry", 2)

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)

        # W1 specific arguments
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

        # L1 interface creation
        l1_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=l1_radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        # Retrieve L1 AP SSID and PSK values
        ssid = l1_handler.interface["home_ap"].ssid_raw
        psk = l1_handler.interface["home_ap"].psk_raw

    with step("VIF reset"):
        gw_handler.vif_reset()
        l1_handler.vif_reset()
    with step("Put GW into router mode"):
        gw_handler.configure_device_mode(device_mode="router")
    with step("Ensure WAN connectivity on GW"):
        assert gw_handler.check_wan_connectivity()
    with step("GW AP and L1 STA creation"):
        assert gw_handler.create_and_configure_backhaul(
            channel=channel,
            leaf_device=l1_handler,
            radio_band=gw_radio_band,
            ht_mode=ht_mode,
            encryption=encryption,
        )
    with step("L1 Home AP configuration"):
        assert l1_handler.interface["home_ap"].configure_interface() == 0
    with step("Client connection to LEAF"):
        w1_handler.connect(ssid=ssid, psk=psk, retry=client_retry, node=l1_handler)
    with step("Verify client connection to LEAF"):
        assert w1_mac in l1_handler.get_wifi_associated_clients()
    with step("Verify client connectivity"):
        assert w1_handler.ping_check(ipaddr=ping_wan_ip)


def test_wm2_verify_wifi_security_modes(wm2_setup, parametrized_test_config, gw_handler, w1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        client_retry = parametrized_test_config.get("client_retry", 2)

        # GW specific arguments
        gw_home_ap_if_name = gw_handler.capabilities.get_home_ap_ifname(radio_band)

        # W1 specific arguments
        wlan_if_name = w1_handler.wlan_ifname
        w1_mac = w1_handler.get_mac(if_name=wlan_if_name)

        # Constant arguments
        ssid = gw_handler.base_ssid
        psk = None if encryption.casefold() == "open" else gw_handler.base_psk

        # Client connection arguments
        client_kwargs = {"ssid": ssid, "psk": psk, "retry": client_retry, "node": gw_handler}
        if encryption.casefold() == "open":
            client_kwargs["key_mgmt"] = ["NONE"]

        # GW interface creation
        gw_handler.create_interface_object(
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
        gw_handler.vif_reset()
    with step("GW AP creation"):
        assert gw_handler.interface["home_ap"].configure_interface() == 0
    with step("Test case"):
        assert (
            gw_handler.ovsdb.wait_for_value(
                table="Wifi_VIF_State",
                value=check_ap_args,
                where=f"if_name=={gw_home_ap_if_name}",
            )[0]
            == 0
        )
    with step("Client connection"):
        w1_handler.connect(**client_kwargs)
    with step("Verify client connection"):
        assert w1_mac in gw_handler.get_wifi_associated_clients()


@pytest.mark.skip(reason="Flaky test")
def test_wm2_wds_backhaul_line_topology(wm2_setup, parametrized_test_config, gw_handler, l1_handler, l2_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config.get("encryption", "WPA2")

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
        mac_list = l1_handler.iface.get_vif_mac(l1_bhaul_sta_if_name)
        assert mac_list, f"Can not get {l1_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
        l1_mac = mac_list[0]

        # L2 specific arguments
        l2_radio_band = l2_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l2_bhaul_sta_if_name = l2_handler.capabilities.get_bhaul_sta_ifname(freq_band=l2_radio_band)
        mac_list = l2_handler.iface.get_vif_mac(l2_bhaul_sta_if_name)
        assert mac_list, f"Can not get {l2_bhaul_sta_if_name} MAC on {l2_handler.nickname.upper()}"
        l2_mac = mac_list[0]

    try:
        with step("GW-LEAF1-LEAF2 WDS backhaul configuration"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type="wds",
                second_leaf_device=l2_handler,
                topology="line",
            )
        with step("Verify GW-LEAF1 WDS backhaul configuration"):
            assert l1_mac in gw_handler.get_wifi_associated_clients()
        with step("Ensure WAN connectivity on L1"):
            assert l1_handler.check_wan_connectivity()
        with step("Verify LEAF1-LEAF2 WDS backhaul configuration"):
            assert l2_mac in l1_handler.get_wifi_associated_clients()
        with step("Ensure WAN connectivity on L2"):
            assert l2_handler.check_wan_connectivity()
    finally:
        with step("Cleanup"):
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            l2_handler.vif_reset()


@pytest.mark.skip(reason="Flaky test")
def test_wm2_wds_backhaul_star_topology(wm2_setup, parametrized_test_config, gw_handler, l1_handler, l2_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config.get("encryption", "WPA2")

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
        mac_list = l1_handler.iface.get_vif_mac(l1_bhaul_sta_if_name)
        assert mac_list, f"Can not get {l1_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
        l1_mac = mac_list[0]

        # L2 specific arguments
        l2_radio_band = l2_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l2_bhaul_sta_if_name = l2_handler.capabilities.get_bhaul_sta_ifname(freq_band=l2_radio_band)
        mac_list = l2_handler.iface.get_vif_mac(l2_bhaul_sta_if_name)
        assert mac_list, f"Can not get {l2_bhaul_sta_if_name} MAC on {l2_handler.nickname.upper()}"
        l2_mac = mac_list[0]

    try:
        with step("GW-LEAF1-LEAF2 WDS backhaul configuration"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type="wds",
                second_leaf_device=l2_handler,
                topology="star",
            )
        with step("Verify GW-LEAF1 WDS backhaul configuration"):
            assert l1_mac in gw_handler.get_wifi_associated_clients()
        with step("Ensure WAN connectivity on L1"):
            assert l1_handler.check_wan_connectivity()
        with step("Verify GW-LEAF2 WDS backhaul configuration"):
            assert l2_mac in gw_handler.get_wifi_associated_clients()
        with step("Ensure WAN connectivity on L2"):
            assert l2_handler.check_wan_connectivity()
    finally:
        with step("Cleanup"):
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            l2_handler.vif_reset()


@pytest.mark.skip(reason="Flaky test")
def test_wm2_wds_backhaul_topology_change(wm2_setup, parametrized_test_config, gw_handler, l1_handler, l2_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        gw_channel = parametrized_test_config.get("gw_channel")
        l2_channel = parametrized_test_config.get("leaf_channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("gw_radio_band")
        l2_radio_band = parametrized_test_config.get("leaf_radio_band")

        # GW-L1 specific arguments
        gw_l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(gw_channel, gw_radio_band)
        gw_l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=gw_l1_radio_band)
        mac_list = l1_handler.iface.get_vif_mac(gw_l1_bhaul_sta_if_name)
        assert mac_list, f"Can not get {gw_l1_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
        gw_l1_mac = mac_list[0]

        # L2-L1 specific arguments
        l2_l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(l2_channel, l2_radio_band)
        l2_l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=l2_l1_radio_band)
        mac_list = l1_handler.iface.get_vif_mac(l2_l1_bhaul_sta_if_name)
        assert mac_list, f"Can not get {l2_l1_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
        l2_l1_mac = mac_list[0]

        with step("6G radio band compatibility check"):
            if gw_radio_band == "6g":
                for node in [gw_handler, l1_handler, l2_handler]:
                    if "6G" not in node.capabilities.get_supported_bands():
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
            assert gw_handler.create_and_configure_backhaul(
                channel=gw_channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type="wds",
            )
        with step("Verify GW-LEAF1 WDS backhaul configuration"):
            assert gw_l1_mac in gw_handler.get_wifi_associated_clients()
        with step("Ensure WAN connectivity on L1"):
            assert l1_handler.check_wan_connectivity()
        with step("LEAF2-LEAF1 WDS backhaul configuration"):
            assert l2_handler.create_and_configure_backhaul(
                channel=l2_channel,
                leaf_device=l1_handler,
                radio_band=l2_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type="wds",
            )
        with step("Verify GW-LEAF1 WDS backhaul configuration"):
            assert l2_l1_mac in l2_handler.get_wifi_associated_clients()
        with step("Ensure WAN connectivity on L1"):
            assert l1_handler.check_wan_connectivity()
    finally:
        with step("Cleanup"):
            gw_handler.vif_reset()
            l1_handler.vif_reset()
            l2_handler.vif_reset()


def test_wm2_transmit_rate_boost(wm2_setup, parametrized_test_config, gw_handler, w1_handler):
    min_opensync_version = "6.4.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config.get("encryption", "WPA2")

        # GW specific arguments
        gw_phy_radio_if_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)
        gw_home_ap_if_name = gw_handler.capabilities.get_home_ap_ifname(freq_band=radio_band)
        gw_home_ap_mac = gw_handler.iface.get_mac(gw_home_ap_if_name)

        # GW interface creation
        gw_handler.create_interface_object(
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
        set_transmit_rate_args = get_command_arguments(
            gw_phy_radio_if_name,
        )
        verify_transmit_rate_args = get_command_arguments(
            "5.5",
            gw_home_ap_mac,
            w1_tcpdump_log_file,
        )

    try:
        with step("GW: increase transmit rate"):
            assert gw_handler.execute_with_logging("tests/wm2/wm2_transmit_rate_boost", set_transmit_rate_args)[0] == 0
        with step("W1: start traffic capture"):
            _sniff_file_name, remote_sniff_file_path = sniffing_utils.start_sniffer_on_client(
                client_obj=w1_handler,
                channel=channel,
                band=w1_sniffer_radio_band,
                tcpdump_flags="-evln --print",
                tcpdump_log_file=w1_tcpdump_log_file,
            )
        with step("GW: Home AP configuration"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
            # Pause test execution to ensure traffic capture
            time.sleep(5)
        with step("W1: stop traffic capture"):
            local_sniff_file_path = sniffing_utils.stop_sniffer_and_get_file(
                client_obj=w1_handler,
                remote_sniff_file_path=remote_sniff_file_path,
                tmp_path=w1_monitor_file_name,
                check_file_size=True,
            )
        with step("W1: Analyze captured traffic"):
            # Attach the PCAP file to the Allure report
            sniffing_utils.attach_capture_file_to_allure(file_path=local_sniff_file_path)
            assert (
                w1_handler.execute("tests/wm2/wm2_check_transmit_rate", verify_transmit_rate_args, as_sudo=True)[0] == 0
            )
    finally:
        with step("Cleanup"):
            # W1: revert client back to STA mode in case of test case failure
            w1_handler.wifi_station(skip_exception=True)
            gw_handler.vif_reset()


@pytest.mark.skip(reason="Flaky test")
def test_wm2_wds_backhaul_traffic_capture(wm2_setup, parametrized_test_config, gw_handler, l1_handler, w1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config.get("encryption", "WPA2")

        # GW specific arguments
        gw_bhaul_ap_if_name = gw_handler.capabilities.get_bhaul_ap_ifname(freq_band=gw_radio_band)
        gw_mac = gw_handler.iface.get_mac(gw_bhaul_ap_if_name)

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
        l1_mac = l1_handler.iface.get_mac(l1_bhaul_sta_if_name)

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

        traffic_args = get_command_arguments(
            receiver_mac,
            destination_mac,
            transmitter_mac,
            source_mac,
            w1_tcpdump_log_file,
        )

    try:
        with step("W1: start traffic capture"):
            _sniff_file_name, remote_sniff_file_path = sniffing_utils.start_sniffer_on_client(
                client_obj=w1_handler,
                channel=channel,
                band=w1_sniffer_radio_band,
                tcpdump_flags="-evln --print",
                tcpdump_log_file=w1_tcpdump_log_file,
            )
        with step("GW-L1 WDS backhaul configuration"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type="wds",
            )
        with step("Verify GW-L1 WDS backhaul configuration"):
            assert l1_mac in gw_handler.get_wifi_associated_clients()
        with step("L1: Ensure WAN connectivity"):
            assert l1_handler.check_wan_connectivity()
        with step("W1: stop traffic capture"):
            local_sniff_file_path = sniffing_utils.stop_sniffer_and_get_file(
                client_obj=w1_handler,
                remote_sniff_file_path=remote_sniff_file_path,
                tmp_path=w1_monitor_file_name,
                check_file_size=True,
            )
        with step("Analyze captured traffic"):
            assert w1_handler.execute("tests/wm2/wm2_wds_backhaul_traffic_capture", traffic_args, as_sudo=True)[0] == 0
            # Attach PCAP file to the Allure report
            sniffing_utils.attach_capture_file_to_allure(file_path=local_sniff_file_path)
    finally:
        with step("Cleanup"):
            # W1: revert client back to STA mode in case of test case failure
            w1_handler.wifi_station(skip_exception=True)
            gw_handler.vif_reset()
            l1_handler.vif_reset()
