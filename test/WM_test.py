from itertools import cycle

import allure
import pytest

import framework.tools.logger
from framework.tools.configure_ap_interface import configure_ap_interface
from framework.tools.create_gre_bhaul import create_and_configure_bhaul_connection_gw_leaf
from framework.tools.functions import FailedException, get_command_arguments, get_config_opts, step
from framework.tools.set_device_mode import configure_device_mode
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


wm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='WM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="wm2_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_wm2_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='wm2')
    server_handler.recipe.clear_full()
    with step('WM2 setup'):
        assert dut_handler.run('tests/wm2/wm2_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    with step('Put device into ROUTER mode'):
        assert configure_device_mode(device_name='dut', device_mode='router')
    server_handler.recipe.mark_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="wm2_fut_setup_ref", depends=["compat_ref_ready", "wm2_fut_setup_dut"], scope='session')
def test_wm2_fut_setup_ref():
    server_handler, ref_handler = pytest.server_handler, pytest.ref_handler
    with step('Transfer'):
        assert ref_handler.clear_tests_folder()
        assert ref_handler.transfer(manager='wm2')
    server_handler.recipe.clear()
    with step('WM2 setup'):
        assert ref_handler.run('tools/device/device_init') == ExpectedShellResult
    server_handler.recipe.add_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref2_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="wm2_fut_setup_ref2", depends=["compat_ref2_ready", "wm2_fut_setup_dut"], scope='session')
def test_wm2_fut_setup_ref2():
    server_handler, ref2_handler = pytest.server_handler, pytest.ref2_handler
    with step('Transfer'):
        assert ref2_handler.clear_tests_folder()
        assert ref2_handler.transfer(manager='wm2')
    server_handler.recipe.clear()
    with step('WM2 setup'):
        assert ref2_handler.run('tools/device/device_init') == ExpectedShellResult
    server_handler.recipe.add_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="wm2_fut_setup_client", depends=["compat_client_ready", "wm2_fut_setup_dut"], scope='session')
def test_wm2_fut_setup_client():
    server_handler, client_handler = pytest.server_handler, pytest.client_handler
    with step('Transfer'):
        assert client_handler.clear_tests_folder()
        assert client_handler.transfer(manager='wm2')
    server_handler.recipe.clear()
    # Add Client setup command here
    server_handler.recipe.add_setup()


########################################################################################################################
test_wm2_check_wifi_credential_config_inputs = wm_config.get("wm2_check_wifi_credential_config", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_check_wifi_credential_config_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_check_wifi_credential_config(test_config):
    dut_handler = pytest.dut_handler
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_check_wifi_credential_config') == ExpectedShellResult


########################################################################################################################
test_wm2_connect_wpa3_client_inputs = wm_config.get('wm2_connect_wpa3_client', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_wm2_connect_wpa3_client_inputs)
def test_wm2_connect_wpa3_client(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "home-wpa3-psk"
        wifi_security_type = "wpa"
        encryption = "WPA3"

        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Arguments from device capabilities
        vif_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')

        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = 'wpa3'

        client_model = client_handler.device_config.get_or_raise('model_string')
        if client_model != "linux":
            pytest.skip('A WiFi6 client is required for this testcase, skipping.')

        client_connect_args = get_command_arguments(
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
            '-dhcp false',
            '-internet_ip false',
        )
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )
    with step('Configure Home AP interface'):
        # 3. Create and configure home AP interface
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            psk=psk,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ssid,
        )
    with step('Client connection'):
        # Connect Client to AP - fails if cannot associate
        assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
    with step('Retrieve Client MAC'):
        # Retrieve the expected Client MAC to be used at actual testcase script
        client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
        if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
            pytest.skip('Failed to retrieve Client MAC address')
        check_assoc_client_args = get_command_arguments(
            vif_if_name,
            client_mac_addr_res[1],
        )

    with step('Testcase'):
        # Check associated STA on AP
        assert dut_handler.run('tests/wm2/wm2_verify_associated_clients', check_assoc_client_args) == ExpectedShellResult


########################################################################################################################
test_wm2_connect_wpa3_leaf_inputs = wm_config.get('wm2_connect_wpa3_leaf', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.require_ref()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_ref"], scope='session')
@pytest.mark.parametrize('test_config', test_wm2_connect_wpa3_leaf_inputs)
def test_wm2_connect_wpa3_leaf(test_config):
    dut_handler, ref_handler = pytest.dut_handler, pytest.ref_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        gw_radio_band = test_config.get('radio_band')
        device_mode = test_config.get('device_mode', 'router')

        wifi_security_type = "wpa"
        encryption = "WPA3"
        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, gw_radio_band)
            assert ref_handler.validate_channel_ht_mode_band(channel, ht_mode, leaf_radio_band)

        # Constant arguments
        gw_interface_type = 'backhaul_ap'
        bhaul_sta_interface_type = 'backhaul_sta'
        # Arguments from device capabilities
        gw_vif_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{gw_interface_type}.{gw_radio_band}')
        bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{bhaul_sta_interface_type}.{leaf_radio_band}')

    try:
        with step('VIF clean'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
        with step(f'Put device into {device_mode.upper()} mode'):
            # Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('GW AP and LEAF STA creation'):
            # On DUT - Create and configure GW bhaul AP interface
            # On REF - Configure LEAF bhaul STA interfaces
            assert create_and_configure_bhaul_connection_gw_leaf(
                channel=channel,
                gw_radio_band=gw_radio_band,
                leaf_radio_band=leaf_radio_band,
                ht_mode=ht_mode,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                skip_gre=True,
            )
        with step('Determine LEAF1 STA MAC at runtime'):
            bhaul_sta_vif_mac_args = get_command_arguments(f'if_name=={bhaul_sta_if_name}')
            bhaul_sta_vif_mac_ec, bhaul_sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', bhaul_sta_vif_mac_args, print_out=True)
            assert bhaul_sta_vif_mac is not None and bhaul_sta_vif_mac != '' and bhaul_sta_vif_mac_ec == ExpectedShellResult
        with step('Testcase'):
            check_assoc_leaf_args = get_command_arguments(
                gw_vif_if_name,
                bhaul_sta_vif_mac,
            )
            # On DUT - Wait for AP to report associated STA
            assert dut_handler.run('tests/wm2/wm2_verify_associated_leaf', check_assoc_leaf_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult


########################################################################################################################
test_wm2_create_all_aps_per_radio_inputs = wm_config.get("wm2_create_all_aps_per_radio", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dfs()
@pytest.mark.parametrize('test_config', test_wm2_create_all_aps_per_radio_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_client"], scope='session')
def test_wm2_create_all_aps_per_radio(test_config):
    server_handler, dut_handler, ref_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        vif_config = test_config.get('vif_config')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        mode = 'ap'
        bhaul_sta_interface_type = 'backhaul_sta'
        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, radio_band)
        bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{bhaul_sta_interface_type}.{leaf_radio_band}')

        # Derived arguments
        client_wpa_type = encryption.lower()
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')

    with step('VIF reset'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult

    with step('Testcase'):
        for interface in vif_config:
            vif_name, vif_radio_idx = vif_config[interface]
            ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}_{vif_radio_idx}"
            psk = f"FUT_psk_{vif_name}_{vif_radio_idx}"

            configure_ap_interface(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                psk=psk,
                device_name='dut',
                interface_type=interface,
                mode=mode,
                ssid=ssid,
                vif_name=vif_name,
                vif_radio_idx=vif_radio_idx,
                reset_vif=False,
            )

            if interface == 'backhaul_ap':
                gw_vif_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface}.{radio_band}')
                leaf_onboard_type = 'gre'

                leaf_bhaul_sta_radio_vif_args_base = [
                    f"-if_name {bhaul_sta_if_name}",
                    f"-ssid {ssid}",
                    f"-onboard_type {leaf_onboard_type}",
                    f"-channel {channel}",
                    f"-wifi_security_type {wifi_security_type}",
                    '-clear_wcc',
                    '-wait_ip',
                ]
                leaf_bhaul_sta_radio_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, psk)
                leaf_bhaul_sta_radio_vif_args = get_command_arguments(*leaf_bhaul_sta_radio_vif_args_base)
                assert ref_handler.run('tools/device/configure_sta_interface', leaf_bhaul_sta_radio_vif_args) == ExpectedShellResult

                bhaul_sta_vif_mac_args = get_command_arguments(f'if_name=={bhaul_sta_if_name}')
                bhaul_sta_vif_mac_ec, bhaul_sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', bhaul_sta_vif_mac_args, print_out=True)
                check_assoc_leaf_args = get_command_arguments(
                    gw_vif_if_name,
                    bhaul_sta_vif_mac,
                )
                # On DUT - Wait for AP to report associated STA
                assert dut_handler.run('tests/wm2/wm2_verify_associated_leaf', check_assoc_leaf_args) == ExpectedShellResult
            else:
                client_connect_args = get_command_arguments(
                    client_wpa_type,
                    client_network_namespace,
                    client_wlan_if_name,
                    client_wpa_supp_cfg_path,
                    ssid,
                    f'-psk {psk}',
                    '-dhcp false',
                    '-internet_ip false',
                )
                assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult


########################################################################################################################
test_wm2_create_wpa3_ap_inputs = wm_config.get('wm2_create_wpa3_ap', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.parametrize('test_config', test_wm2_create_wpa3_ap_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
def test_wm2_create_wpa3_ap(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        interface_type = test_config.get('interface_type')
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        wpa_psk = "home-wpa3-psk"
        wifi_security_type = "wpa"
        encryption = "WPA3"
        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

    with step('Testcase'):
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            psk=wpa_psk,
            interface_type=interface_type,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ssid,
            skip_inet=True,
        )


########################################################################################################################
test_wm2_dfs_cac_aborted_first_run = False
test_wm2_dfs_cac_aborted_inputs = wm_config.get("wm2_dfs_cac_aborted", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dfs()
@pytest.mark.parametrize('test_config', test_wm2_dfs_cac_aborted_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_dfs_cac_aborted(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel_A = test_config.get('channel_A')
        channel_B = test_config.get('channel_B')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel_A, ht_mode, radio_band)
            assert dut_handler.validate_channel_ht_mode_band(channel_B, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')
        channels = dut_handler.capabilities.get_or_raise('interfaces.radio_channels')
        if not {channel_A, channel_B}.issubset(channels[radio_band]):
            pytest.skip(f'Channels {channel_A} and {channel_B} are not valid for the same radio {phy_radio_name}!')

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel_a {channel_A}",
            f"-channel_b {channel_B}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    # Test preparation
    with step('VIF reset'):
        global test_wm2_dfs_cac_aborted_first_run
        if not test_wm2_dfs_cac_aborted_first_run:
            assert dut_handler.run('tools/device/vif_reset', if_name) == ExpectedShellResult
            test_wm2_dfs_cac_aborted_first_run = True
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_dfs_cac_aborted', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_ht_mode_and_channel_iteration_inputs = wm_config.get("wm2_ht_mode_and_channel_iteration", [])
# Create individual scenarios from grouped lists of parameters
test_wm2_ht_mode_and_channel_iteration_scenarios = [
    {
        "channel": a,
        "ht_mode": b,
        "radio_band": g["radio_band"],
        "encryption": "WPA2" if "encryption" not in g else g["encryption"],
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        **get_config_opts(g),
    }
    for g in test_wm2_ht_mode_and_channel_iteration_inputs for a in g["channels"] for b in g["ht_modes"]
]


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_ht_mode_and_channel_iteration_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_ht_mode_and_channel_iteration(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_ht_mode_and_channel_iteration', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_immutable_radio_freq_band_first_run = False
test_wm2_immutable_radio_freq_band_first_run_inputs = wm_config.get("wm2_immutable_radio_freq_band", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_immutable_radio_freq_band_first_run_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_immutable_radio_freq_band(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global test_wm2_immutable_radio_freq_band_first_run

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        freq_band = test_config.get('freq_band')

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            f"-freq_band {freq_band}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('VIF reset'):
        if not test_wm2_immutable_radio_freq_band_first_run:
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            test_wm2_immutable_radio_freq_band_first_run = True
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_immutable_radio_freq_band', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_immutable_radio_hw_mode_first_run = False
test_wm2_immutable_radio_hw_mode_first_run_inputs = wm_config.get("wm2_immutable_radio_hw_mode", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_immutable_radio_hw_mode_first_run_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_immutable_radio_hw_mode(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global test_wm2_immutable_radio_hw_mode_first_run

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        custom_hw_mode = test_config.get('custom_hw_mode')

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            f"-custom_hw_mode {custom_hw_mode}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('VIF reset'):
        if not test_wm2_immutable_radio_hw_mode_first_run:
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            test_wm2_immutable_radio_hw_mode_first_run = True
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_immutable_radio_hw_mode', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_immutable_radio_hw_type_first_run = False
test_wm2_immutable_radio_hw_type_first_run_inputs = wm_config.get("wm2_immutable_radio_hw_type", [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_immutable_radio_hw_type_first_run_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_immutable_radio_hw_type(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global test_wm2_immutable_radio_hw_type_first_run

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        hw_type = test_config.get('hw_type')

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            f"-hw_type {hw_type}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    # Test preparation
    with step('VIF reset'):
        if not test_wm2_immutable_radio_hw_type_first_run:
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            test_wm2_immutable_radio_hw_type_first_run = True
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_immutable_radio_hw_type', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_leaf_ht_mode_change_inputs = wm_config.get('wm2_leaf_ht_mode_change', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_ref"], scope='session')
@pytest.mark.parametrize('test_config', test_wm2_leaf_ht_mode_change_inputs)
def test_wm2_leaf_ht_mode_change(test_config):
    server_handler, dut_handler, ref_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        custom_ht_mode = test_config.get("custom_ht_mode")
        gw_radio_band = test_config.get("radio_band")
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")
        leaf_radio_band = dut_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, gw_radio_band)
            assert ref_handler.validate_channel_ht_mode_band(channel, ht_mode, leaf_radio_band)

        dut_primary_wan_interface = dut_handler.capabilities.get('interfaces.primary_wan_interface')
        ref_primary_wan_interface = ref_handler.capabilities.get('interfaces.primary_wan_interface')
        gw_phy_radio_if_name = dut_handler.capabilities.get('interfaces.phy_radio_name').get(gw_radio_band)
        update_ht_mode_args = get_command_arguments(
            'Wifi_Radio_Config',
            '-w', 'if_name', gw_phy_radio_if_name,
            '-u', 'ht_mode', custom_ht_mode,
        )
        wait_ht_mode_args = get_command_arguments(
            'Wifi_Radio_State',
            '-w', 'if_name', gw_phy_radio_if_name,
            '-is', 'ht_mode', custom_ht_mode,
        )

    try:
        with step('Changing roles in network switch: DUT to act as LEAF and LEAF to act as GW'):
            log.info('Reconfigure network switch for DUT to act as LEAF')
            cmd = f'switch dut_{dut_primary_wan_interface} vlan-delete 200'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
            cmd = f'switch ref_{ref_primary_wan_interface} vlan-set 200 untagged'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)

        with step(f'Put device into {device_mode.upper()} mode - REF/GW'):
            assert configure_device_mode(device_name='ref', device_mode=device_mode)
        with step('Device setup - DUT/LEAF'):
            assert dut_handler.run('tools/device/device_init') == ExpectedShellResult

        with step('Ensure WAN connectivity on REF/GW'):
            assert ref_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        with step('REF/GW AP and DUT/LEAF STA creation, configuration and GW/REF GRE configuration'):
            assert create_and_configure_bhaul_connection_gw_leaf(
                channel,
                gw_radio_band,
                leaf_radio_band,
                ht_mode,
                wifi_security_type,
                encryption,
                gw_device="ref",
                leaf_device="dut",
            )
        with step('Ensure WAN connectivity on DUT/LEAF'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        with step(f'Change HT Mode on REF/GW from {ht_mode} to {custom_ht_mode}'):
            assert ref_handler.run('tools/device/ovsdb/update_ovsdb_entry', update_ht_mode_args) == ExpectedShellResult
            assert ref_handler.run('tools/device/ovsdb/wait_ovsdb_entry', wait_ht_mode_args) == ExpectedShellResult
        with step('Testcase: Ensure WAN connectivity on DUT/LEAF after HT Mode change'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
    finally:
        with step('Cleanup - reverting roles in network switch: LEAF <-> GW'):
            log.info('Revert network switch for DUT to act as GW')
            cmd = f'switch ref_{ref_primary_wan_interface} vlan-delete 200'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
            cmd = f'switch dut_{dut_primary_wan_interface} vlan-set 200 untagged'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
        with step('Cleanup - Run setup procedures for DUT / REF'):
            configure_device_mode(device_name='dut', device_mode='router')
            ref_handler.run('tools/device/device_init')


########################################################################################################################
last_radio_band_used = None
test_wm2_pre_cac_channel_change_validation_inputs = wm_config.get("wm2_pre_cac_channel_change_validation", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dfs()
@pytest.mark.parametrize('test_config', test_wm2_pre_cac_channel_change_validation_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_pre_cac_channel_change_validation(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel_A = test_config.get('channel_A')
        channel_B = test_config.get('channel_B')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel_A, ht_mode, radio_band)
            assert dut_handler.validate_channel_ht_mode_band(channel_B, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')
        channels = dut_handler.capabilities.get_or_raise('interfaces.radio_channels')
        if not {channel_A, channel_B}.issubset(channels[radio_band]):
            pytest.skip(f'Channels {channel_A} and {channel_B} are not valid for the same radio {phy_radio_name}!')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel_a {channel_A}",
            f"-channel_b {channel_B}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            "-channel_mode manual",
            "-enabled true",
            f"-reg_domain {dut_handler.regulatory_domain.upper()}",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_pre_cac_channel_change_validation', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_pre_cac_ht_mode_change_validation_inputs = wm_config.get("wm2_pre_cac_ht_mode_change_validation", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dfs()
@pytest.mark.parametrize('test_config', test_wm2_pre_cac_ht_mode_change_validation_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_pre_cac_ht_mode_change_validation(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode_a = test_config.get('ht_mode_a')
        ht_mode_b = test_config.get('ht_mode_b')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode_a, radio_band)
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode_b, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        mode = "ap"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode_a {ht_mode_a}",
            f"-ht_mode_b {ht_mode_b}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            "-channel_mode manual",
            "-enabled true",
            f"-reg_domain {dut_handler.regulatory_domain.upper()}",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_pre_cac_ht_mode_change_validation', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_bcn_int_inputs = wm_config.get("wm2_set_bcn_int", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_bcn_int_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_bcn_int(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        bcn_int = test_config.get('bcn_int')

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            f"-bcn_int {bcn_int}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_bcn_int', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_channel_inputs = wm_config.get("wm2_set_channel", [])
test_wm2_set_channel_scenarios = [
    {
        "channel": a,
        "ht_mode": g["ht_mode"],
        "radio_band": g["radio_band"],
        "encryption": "WPA2" if "encryption" not in g else g["encryption"],
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        **get_config_opts(g),
    }
    for g in test_wm2_set_channel_inputs for a in g["channels"]
]


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_channel_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_channel(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_channel', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_set_channel_neg_inputs = wm_config.get("wm2_set_channel_neg", [])
test_wm2_set_channel_neg_scenarios = [
    {
        "channel": g["channel"],
        "ht_mode": g["ht_mode"],
        "mismatch_channel": a,
        "radio_band": g["radio_band"],
        "encryption": "WPA2" if "encryption" not in g else g["encryption"],
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        **get_config_opts(g),
    }
    for g in test_wm2_set_channel_neg_inputs for a in g["mismatch_channels"]
]


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_channel_neg_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_channel_neg(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        ht_mode = test_config.get('ht_mode')
        channel = test_config.get('channel')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        mismatch_channel = test_config.get('mismatch_channel')

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
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
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_channel_neg', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_ht_mode_inputs = wm_config.get("wm2_set_ht_mode", [])

test_wm2_set_ht_mode_scenarios = [
    {
        "channel": a,
        "ht_mode": b,
        "radio_band": g["radio_band"],
        "encryption": "WPA2" if "encryption" not in g else g["encryption"],
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        "channel_change_timeout": '' if "channel_change_timeout" not in g else g["channel_change_timeout"],
        **get_config_opts(g),
    }
    for g in test_wm2_set_ht_mode_inputs for a in g["channels"] for b in g["ht_modes"]
]


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_ht_mode_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_ht_mode(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        # Optional configuration parameter, load if present, keep empty string if not
        channel_change_timeout = '' if 'channel_change_timeout' not in test_config else test_config.get('channel_change_timeout')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
            channel_change_timeout,
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_ht_mode', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_set_ht_mode_neg_inputs = wm_config.get("wm2_set_ht_mode_neg", [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_ht_mode_neg_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_ht_mode_neg(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        mismatch_ht_mode = test_config.get('mismatch_ht_mode')

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
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
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_ht_mode_neg', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_set_radio_country_first_run = False
test_wm2_set_radio_country_first_run_inputs = wm_config.get("wm2_set_radio_country", [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_radio_country_first_run_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_radio_country(test_config):
    dut_handler = pytest.dut_handler
    global test_wm2_set_radio_country_first_run

    with step('Preparation'):
        # Test arguments from testcase config
        country = test_config.get('country')
        radio_band = test_config.get('radio_band')

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        test_args = get_command_arguments(
            phy_radio_name,
            country,
        )

    with step('VIF reset'):
        if not test_wm2_set_radio_country_first_run:
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            test_wm2_set_radio_country_first_run = True
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_radio_country', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_radio_thermal_tx_chainmask_inputs = wm_config.get("wm2_set_radio_thermal_tx_chainmask", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_radio_thermal_tx_chainmask_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_radio_thermal_tx_chainmask(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        with step('Verify correct antennas settings'):
            radio_antennas = dut_handler.capabilities.get_or_raise(f'interfaces.radio_antennas.{radio_band}')
            assert radio_antennas is not None and int(radio_antennas[0])
            radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
            tx_chainmask = radio_max_chainmask
            thermal_tx_chainmask = tx_chainmask >> 1
            assert thermal_tx_chainmask != 0
            valid_chainmasks = [(1 << x) - 1 for x in range(1, 5)]
            assert all([x in valid_chainmasks for x in [thermal_tx_chainmask, tx_chainmask, radio_max_chainmask]])

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
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
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_radio_thermal_tx_chainmask', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_radio_tx_chainmask_inputs = wm_config.get("wm2_set_radio_tx_chainmask", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_radio_tx_chainmask_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_radio_tx_chainmask(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        with step('Verify correct antennas settings'):
            radio_antennas = dut_handler.capabilities.get_or_raise(f'interfaces.radio_antennas.{radio_band}')
            assert radio_antennas is not None and int(radio_antennas[0])
            radio_max_chainmask = (1 << int(radio_antennas[0])) - 1
            tx_chainmask = (radio_max_chainmask >> 1)
            valid_chainmasks = [(1 << x) - 1 for x in range(1, 5)]
            assert all([x in valid_chainmasks for x in [tx_chainmask, radio_max_chainmask]])

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-tx_chainmask {tx_chainmask}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_radio_tx_chainmask', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_radio_tx_power_inputs = wm_config.get("wm2_set_radio_tx_power", [])
test_wm2_set_radio_tx_power_scenarios = [
    {
        "channel": g["channel"],
        "ht_mode": g["ht_mode"],
        "radio_band": g["radio_band"],
        "tx_power": a,
        "encryption": "WPA2" if "encryption" not in g else g["encryption"],
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        **get_config_opts(g),
    }
    for g in test_wm2_set_radio_tx_power_inputs for a in g["tx_powers"]
]


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_radio_tx_power_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_radio_tx_power(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        tx_power = test_config.get('tx_power')

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            f"-tx_power {tx_power}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_radio_tx_power', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_set_radio_tx_power_neg_inputs = wm_config.get("wm2_set_radio_tx_power_neg", [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_radio_tx_power_neg_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_radio_tx_power_neg(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        tx_power = test_config.get('tx_power')
        mismatch_tx_power = test_config.get('mismatch_tx_power')

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            f"-tx_power {tx_power}",
            f"-mismatch_tx_power {mismatch_tx_power}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_radio_tx_power_neg', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_set_radio_vif_configs_first_run_inputs = wm_config.get("wm2_set_radio_vif_configs", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_radio_vif_configs_first_run_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_radio_vif_configs(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        custom_channel = test_config.get('custom_channel')
        radio_band = test_config.get('radio_band')
        ht_mode = test_config.get('ht_mode')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
            assert dut_handler.validate_channel_ht_mode_band(custom_channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
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
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_radio_vif_configs', test_args) == ExpectedShellResult


########################################################################################################################
last_radio_band_used = None
test_wm2_set_ssid_inputs = wm_config.get("wm2_set_ssid", [])
test_wm2_set_ssid_scenarios = [
    {
        "channel": g["channel"],
        "ht_mode": g["ht_mode"],
        "radio_band": g["radio_band"],
        "ssid": a,
        "encryption": "WPA2" if "encryption" not in g else g["encryption"],
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        **get_config_opts(g),
    }
    for g in test_wm2_set_ssid_inputs for a in g["ssids"]
]


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_ssid_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_ssid(test_config):
    dut_handler = pytest.dut_handler
    global last_radio_band_used

    with step('Preparation'):
        # Test arguments from testcase config
        ssid = test_config.get('ssid')
        ssid = f"\'{ssid}\'"
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        mode = "ap"
        psk = "FutTestPSK"

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Arguments from device capabilities
        if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')
        hw_mode = dut_handler.capabilities.get_or_raise(f'interfaces.radio_hw_mode.{radio_band}')

        if last_radio_band_used != radio_band:
            with step('VIF reset'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        last_radio_band_used = radio_band

        test_args_base = [
            f"-vif_radio_idx {vif_radio_idx}",
            f"-if_name {phy_radio_name}",
            f"-ssid {ssid}",
            f"-channel {channel}",
            f"-ht_mode {ht_mode}",
            f"-hw_mode {hw_mode}",
            f"-mode {mode}",
            f"-vif_if_name {if_name}",
            "-channel_mode manual",
            "-enabled true",
            f"-wifi_security_type {wifi_security_type}",
        ]
        test_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        test_args = get_command_arguments(*test_args_base)

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_ssid', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_set_wifi_credential_config_inputs = wm_config.get("wm2_set_wifi_credential_config", [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_set_wifi_credential_config_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_set_wifi_credential_config(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Constant arguments
        psk = "FutTestPSK"
        onboard_type = "gre"
        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        security = f'\'["map",[["encryption","WPA-PSK"],["key","{psk}"],["mode","2"]]]\''
        test_args = get_command_arguments(
            ssid,
            security,
            onboard_type,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_set_wifi_credential_config', test_args) == ExpectedShellResult


########################################################################################################################
wm2_topology_change_change_parent_change_band_change_channel_inputs = wm_config.get('wm2_topology_change_change_parent_change_band_change_channel', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.require_ref()
@pytest.mark.require_ref2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_ref", "wm2_fut_setup_ref2"], scope='session')
@pytest.mark.parametrize('test_config', wm2_topology_change_change_parent_change_band_change_channel_inputs)
def test_wm2_topology_change_change_parent_change_band_change_channel(test_config):
    server_handler, dut_handler, ref_handler, ref2_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler, pytest.ref2_handler

    with step('Preparation'):
        # Test arguments from testcase config
        gw_channel = test_config.get("gw_channel")
        leaf2_channel = test_config.get("leaf_channel")
        ht_mode = test_config.get("ht_mode")
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        gw_radio_band = test_config.get("gw_radio_band")
        leaf2_radio_band = test_config.get("leaf_radio_band")

        with step('6G radio band compatibility check'):
            if gw_radio_band == '6g' or leaf2_radio_band == '6g':
                gw_radio_band_check = dut_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                leaf_radio_band_check = ref_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                leaf2_radio_band_check = ref2_handler.capabilities.get(f'interfaces.radio_channels.{leaf2_radio_band}')
                if '' in [gw_radio_band_check, leaf_radio_band_check, leaf2_radio_band_check]:
                    pytest.skip('6G radio band is not supported on all required devices')
                else:
                    log.info('6G radio band is supported on all required devices')
            else:
                log.info('6G radio band was not selected. The 6G radio band compatibility check is not necessary')

        # Reacquire LEAF2 radio band, due to possible issues caused by differences between dual band and triband devices
        leaf2_radio_band = ref2_handler.get_radio_band_from_channel_and_band(leaf2_channel, leaf2_radio_band)

        # Common GW and LEAF AP VIF arguments
        bhaul_interface_type = 'backhaul_ap'
        psk = 'FutTestPSK'
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Specific GW and LEAF2 AP VIF arguments
        gw_bhaul_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{bhaul_interface_type}.{gw_radio_band}')
        leaf2_bhaul_ap_if_name = ref2_handler.capabilities.get_or_raise(f'interfaces.{bhaul_interface_type}.{leaf2_radio_band}')

        # Specific LEAF1 STA arguments
        leaf_bhaul_interface_type = 'backhaul_sta'

        # Reacquire LEAF radio band, due to possible issues caused by differences between dual band and triband devices
        gw_band_leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(gw_channel, gw_radio_band)
        gw_band_leaf_bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{leaf_bhaul_interface_type}.{gw_band_leaf_radio_band}')

        # Reacquire LEAF radio band, due to possible issues caused by differences between dual band and triband devices
        leaf2_band_leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(leaf2_channel, leaf2_radio_band)
        leaf_band_leaf_bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{leaf_bhaul_interface_type}.{leaf2_band_leaf_radio_band}')

    with step('Assemble testcase parameters'):
        leaf1_to_gw_bhaul_sta_vif_args_base = [
            f"-if_name {gw_band_leaf_bhaul_sta_if_name}",
            f"-ssid {ssid}",
            f'-wifi_security_type {wifi_security_type}',
            '-clear_wcc',
        ]

        leaf1_to_leaf2_bhaul_sta_vif_args_base = [
            f"-if_name {leaf_band_leaf_bhaul_sta_if_name}",
            f"-ssid {ssid}",
            f'-wifi_security_type {wifi_security_type}',
            '-clear_wcc',
        ]

        leaf1_to_gw_bhaul_sta_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        leaf1_to_leaf2_bhaul_sta_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, psk)

    try:
        with step('GW AP creation'):
            # On DUT - Create AP VIF interface
            assert configure_ap_interface(
                channel=gw_channel,
                ht_mode=ht_mode,
                radio_band=gw_radio_band,
                psk=psk,
                interface_type=bhaul_interface_type,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
            )
        with step('Determine DUT GW MAC at runtime'):
            gw_ap_vif_mac_args = get_command_arguments(f'if_name=={gw_bhaul_ap_if_name}')
            gw_ap_vif_mac_ec, gw_ap_vif_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', gw_ap_vif_mac_args, print_out=True)
            assert gw_ap_vif_mac is not None and gw_ap_vif_mac != '' and gw_ap_vif_mac_ec == ExpectedShellResult
        with step('LEAF1 STA configuration to connect to DUT GW'):
            # On REF1 - Create LEAF1 STA VIF interface
            leaf1_to_gw_bhaul_sta_vif_args_base += [
                f"-parent {gw_ap_vif_mac}",
            ]
            leaf1_to_gw_bhaul_sta_vif_args = get_command_arguments(*leaf1_to_gw_bhaul_sta_vif_args_base)
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/configure_sta_interface', leaf1_to_gw_bhaul_sta_vif_args) == ExpectedShellResult
        with step('Determine LEAF1 STA MAC at runtime'):
            leaf_sta_vif_mac_args = get_command_arguments(f'if_name=={gw_band_leaf_bhaul_sta_if_name}')
            leaf_sta_vif_mac_ec, leaf_sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', leaf_sta_vif_mac_args, print_out=True)
            assert leaf_sta_vif_mac is not None and leaf_sta_vif_mac != '' and leaf_sta_vif_mac_ec == ExpectedShellResult
        with step('Verify GW associated clients'):
            check_associated_leaf_args = get_command_arguments(
                gw_bhaul_ap_if_name,
                leaf_sta_vif_mac,
            )
            assert dut_handler.run('tests/wm2/wm2_verify_associated_leaf', check_associated_leaf_args) == ExpectedShellResult
        with step('LEAF2 AP creation'):
            # On REF2 - Create AP VIF interface using same credentials as on DUT except a different channel and radio band
            assert configure_ap_interface(
                device_name='ref2',
                channel=leaf2_channel,
                ht_mode=ht_mode,
                radio_band=leaf2_radio_band,
                psk=psk,
                interface_type=bhaul_interface_type,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
                bridge=False,
            )
        with step('Determine LEAF2 AP MAC at runtime'):
            leaf_ap_vif_mac_args = get_command_arguments(f'if_name=={leaf2_bhaul_ap_if_name}')
            leaf_ap_vif_mac_ec, leaf_ap_vif_mac, std_err = ref2_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', leaf_ap_vif_mac_args, print_out=True)
            assert leaf_ap_vif_mac is not None and leaf_ap_vif_mac != '' and leaf_ap_vif_mac_ec == ExpectedShellResult
        with step('Testcase - Reset LEAF1 STA configuration'):
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
        with step('Testcase - LEAF1 STA configuration to connect to LEAF2 AP'):
            leaf1_to_leaf2_bhaul_sta_vif_args_base += [
                f"-parent {leaf_ap_vif_mac}",
            ]
            leaf1_to_leaf2_bhaul_sta_vif_args = get_command_arguments(*leaf1_to_leaf2_bhaul_sta_vif_args_base)
            assert ref_handler.run('tools/device/configure_sta_interface', leaf1_to_leaf2_bhaul_sta_vif_args) == ExpectedShellResult
        with step('Determine LEAF1 STA MAC at runtime'):
            leaf_sta_vif_mac_args = get_command_arguments(f'if_name=={leaf_band_leaf_bhaul_sta_if_name}')
            leaf_sta_vif_mac_ec, leaf_sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', leaf_sta_vif_mac_args, print_out=True)
            assert leaf_sta_vif_mac is not None and leaf_sta_vif_mac != '' and leaf_sta_vif_mac_ec == ExpectedShellResult
        with step('Testcase - Verify topology change'):
            check_associated_leaf_args = get_command_arguments(
                leaf2_bhaul_ap_if_name,
                leaf_sta_vif_mac,
            )
            assert ref2_handler.run('tests/wm2/wm2_verify_associated_leaf', check_associated_leaf_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref2_handler.run('tools/device/vif_reset') == ExpectedShellResult


########################################################################################################################
wm2_topology_change_change_parent_same_band_change_channel_inputs = wm_config.get('wm2_topology_change_change_parent_same_band_change_channel', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.require_ref()
@pytest.mark.require_ref2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_ref", "wm2_fut_setup_ref2"], scope='session')
@pytest.mark.parametrize('test_config', wm2_topology_change_change_parent_same_band_change_channel_inputs)
def test_wm2_topology_change_change_parent_same_band_change_channel(test_config):
    server_handler, dut_handler, ref_handler, ref2_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler, pytest.ref2_handler

    with step('Preparation'):
        # Test arguments from testcase config
        gw_channel = test_config.get("gw_channel")
        leaf_channel = test_config.get("leaf_channel")
        ht_mode = test_config.get("ht_mode")
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        gw_radio_band = test_config.get("radio_band")

        with step('6G radio band compatibility check'):
            if gw_radio_band == '6g':
                gw_radio_band_check = dut_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                leaf_radio_band_check = ref_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                leaf2_radio_band_check = ref2_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                if '' in [gw_radio_band_check, leaf_radio_band_check, leaf2_radio_band_check]:
                    pytest.skip('6G radio band is not supported on all required devices')
                else:
                    log.info('6G radio band is supported on all required devices')
            else:
                log.info('6G radio band was not selected. The 6G radio band compatibility check is not necessary')

        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(gw_channel, gw_radio_band)
        leaf2_radio_band = ref2_handler.get_radio_band_from_channel_and_band(gw_channel, gw_radio_band)

        # GW and LEAF2 AP VIF arguments
        bhaul_interface_type = 'backhaul_ap'
        psk = 'FutTestPSK'
        # Arguments from device capabilities
        gw_bhaul_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{bhaul_interface_type}.{gw_radio_band}')
        leaf2_bhaul_ap_if_name = ref2_handler.capabilities.get_or_raise(f'interfaces.{bhaul_interface_type}.{leaf2_radio_band}')
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # LEAF1 STA arguments
        leaf_bhaul_interface_type = 'backhaul_sta'
        leaf_bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{leaf_bhaul_interface_type}.{leaf_radio_band}')

    with step('Assemble testcase parameters'):
        leaf_bhaul_sta_vif_args_base = [
            f"-if_name {leaf_bhaul_sta_if_name}",
            f"-ssid {ssid}",
            f'-wifi_security_type {wifi_security_type}',
            '-clear_wcc',
        ]

        leaf_bhaul_sta_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, psk)

    try:
        with step('GW AP creation'):
            # On DUT - Create AP VIF interface
            assert configure_ap_interface(
                channel=gw_channel,
                ht_mode=ht_mode,
                radio_band=gw_radio_band,
                psk=psk,
                interface_type=bhaul_interface_type,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
            )
        with step('Determine DUT GW MAC at runtime'):
            gw_vif_mac_args = get_command_arguments(f'if_name=={gw_bhaul_ap_if_name}')
            gw_vif_mac_ec, gw_vif_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', gw_vif_mac_args, print_out=True)
            assert gw_vif_mac is not None and gw_vif_mac != '' and gw_vif_mac_ec == ExpectedShellResult
        with step('LEAF1 STA configuration'):
            # On REF1 - Create LEAF1 STA VIF interface
            leaf_bhaul_sta_vif_args_base += [
                f"-parent {gw_vif_mac}",
            ]
            leaf_bhaul_sta_vif_args = get_command_arguments(*leaf_bhaul_sta_vif_args_base)
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/configure_sta_interface', leaf_bhaul_sta_vif_args) == ExpectedShellResult
        with step('Determine LEAF1 STA MAC at runtime'):
            leaf_sta_vif_mac_args = get_command_arguments(f'if_name=={leaf_bhaul_sta_if_name}')
            leaf_sta_vif_mac_ec, leaf_sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', leaf_sta_vif_mac_args, print_out=True)
            assert leaf_sta_vif_mac is not None and leaf_sta_vif_mac != '' and leaf_sta_vif_mac_ec == ExpectedShellResult
        with step('Verify GW associated clients'):
            check_associated_leaf_args = get_command_arguments(
                gw_bhaul_ap_if_name,
                leaf_sta_vif_mac,
            )
            assert dut_handler.run('tests/wm2/wm2_verify_associated_leaf', check_associated_leaf_args) == ExpectedShellResult
        with step('LEAF2 AP creation'):
            # On REF2 - Create LEAF2 AP VIF interface using same credentials as on DUT except a different channel
            assert configure_ap_interface(
                device_name='ref2',
                channel=leaf_channel,
                ht_mode=ht_mode,
                radio_band=leaf2_radio_band,
                psk=psk,
                interface_type=bhaul_interface_type,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
                bridge=False,
            )
        with step('Determine LEAF2 AP MAC at runtime'):
            leaf_ap_vif_mac_args = get_command_arguments(f'if_name=={leaf2_bhaul_ap_if_name}')
            leaf_ap_vif_mac_ec, leaf_ap_vif_mac, std_err = ref2_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', leaf_ap_vif_mac_args, print_out=True)
            assert leaf_ap_vif_mac is not None and leaf_ap_vif_mac != '' and leaf_ap_vif_mac_ec == ExpectedShellResult
        with step('Testcase - Update parent'):
            leaf_bhaul_sta_update_parent_args = get_command_arguments(
                leaf_bhaul_sta_if_name,
                leaf_ap_vif_mac,
            )
            assert ref_handler.run('tools/device/set_parent', leaf_bhaul_sta_update_parent_args) == ExpectedShellResult
        with step('Testcase - Verify topology change'):
            check_associated_leaf_args = get_command_arguments(
                leaf2_bhaul_ap_if_name,
                leaf_sta_vif_mac,
            )
            assert ref2_handler.run('tests/wm2/wm2_verify_associated_leaf', check_associated_leaf_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref2_handler.run('tools/device/vif_reset') == ExpectedShellResult


########################################################################################################################
test_wm2_topology_change_change_parent_same_band_same_channel_inputs = wm_config.get('wm2_topology_change_change_parent_same_band_same_channel', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.require_ref()
@pytest.mark.require_ref2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_ref", "wm2_fut_setup_ref2"], scope='session')
@pytest.mark.parametrize('test_config', test_wm2_topology_change_change_parent_same_band_same_channel_inputs)
def test_wm2_topology_change_change_parent_same_band_same_channel(test_config):
    server_handler, dut_handler, ref_handler, ref2_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler, pytest.ref2_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        gw_radio_band = test_config.get("radio_band")
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('6G radio band compatibility check'):
            if gw_radio_band == '6g':
                gw_radio_band_check = dut_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                leaf_radio_band_check = ref_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                leaf2_radio_band_check = ref2_handler.capabilities.get(f'interfaces.radio_channels.{gw_radio_band}')
                if '' in [gw_radio_band_check, leaf_radio_band_check, leaf2_radio_band_check]:
                    pytest.skip('6G radio band is not supported on all required devices')
                else:
                    log.info('6G radio band is supported on all required devices')
            else:
                log.info('6G radio band was not selected. The 6G radio band compatibility check is not necessary')

        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)
        leaf2_radio_band = ref2_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)

        bhaul_ap_interface_type = 'backhaul_ap'
        psk = 'FutTestPSK'
        # Arguments from device capabilities
        gw_bhaul_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{bhaul_ap_interface_type}.{gw_radio_band}')
        leaf2_bhaul_ap_if_name = ref2_handler.capabilities.get_or_raise(f'interfaces.{bhaul_ap_interface_type}.{leaf2_radio_band}')
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # LEAF1 STA arguments
        bhaul_sta_interface_type = 'backhaul_sta'
        bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{bhaul_sta_interface_type}.{leaf_radio_band}')

    with step('Assemble testcase parameters'):

        bhaul_sta_vif_args_base = [
            f"-if_name {bhaul_sta_if_name}",
            f"-ssid {ssid}",
            f'-wifi_security_type {wifi_security_type}',
            '-clear_wcc',
        ]

        bhaul_sta_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, psk)

    try:
        with step('GW AP creation'):
            # On DUT - Create GW AP VIF interface
            assert configure_ap_interface(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=gw_radio_band,
                psk=psk,
                interface_type=bhaul_ap_interface_type,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
            )
        with step('Determine DUT GW MAC at runtime'):
            gw_vif_mac_args = get_command_arguments(f'if_name=={gw_bhaul_ap_if_name}')
            gw_vif_mac_ec, gw_vif_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', gw_vif_mac_args, print_out=True)
            assert gw_vif_mac is not None and gw_vif_mac != '' and gw_vif_mac_ec == ExpectedShellResult
        with step('LEAF1 STA configuration'):
            # On REF1 - Create LEAF1 STA VIF interface
            bhaul_sta_vif_args_base += [
                f"-parent {gw_vif_mac}",
            ]
            bhaul_sta_vif_args = get_command_arguments(*bhaul_sta_vif_args_base)
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/configure_sta_interface', bhaul_sta_vif_args) == ExpectedShellResult
        with step('Determine LEAF1 STA MAC at runtime'):
            sta_vif_mac_args = get_command_arguments(f'if_name=={bhaul_sta_if_name}')
            sta_vif_mac_ec, sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', sta_vif_mac_args, print_out=True)
            assert sta_vif_mac is not None and sta_vif_mac != '' and sta_vif_mac_ec == ExpectedShellResult
        with step('Verify GW associated clients'):
            check_associated_leaf_args = get_command_arguments(
                gw_bhaul_ap_if_name,
                sta_vif_mac,
            )
            assert dut_handler.run('tests/wm2/wm2_verify_associated_leaf', check_associated_leaf_args) == ExpectedShellResult
        with step('LEAF2 AP creation'):
            # On REF2 - Create LEAF2 AP VIF interface using same credentials as on DUT
            assert configure_ap_interface(
                device_name='ref2',
                channel=channel,
                ht_mode=ht_mode,
                radio_band=leaf2_radio_band,
                psk=psk,
                interface_type=bhaul_ap_interface_type,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
                bridge=False,
            )
        with step('Determine LEAF2 AP MAC at runtime'):
            ap_vif_mac_args = get_command_arguments(f'if_name=={leaf2_bhaul_ap_if_name}')
            ap_vif_mac_ec, ap_vif_mac, std_err = ref2_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', ap_vif_mac_args, print_out=True)
            assert ap_vif_mac is not None and ap_vif_mac != '' and ap_vif_mac_ec == ExpectedShellResult
        with step('Testcase - Update parent'):
            bhaul_sta_update_parent_args = get_command_arguments(
                bhaul_sta_if_name,
                ap_vif_mac,
            )
            assert ref_handler.run('tools/device/set_parent', bhaul_sta_update_parent_args) == ExpectedShellResult
        with step('Testcase - Verify topology change'):
            # On REF2 - Verify that LEAF1 STA is associated to LEAF2 AP
            check_associated_leaf_args = get_command_arguments(
                leaf2_bhaul_ap_if_name,
                sta_vif_mac,
            )
            assert ref2_handler.run('tests/wm2/wm2_verify_associated_leaf', check_associated_leaf_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref2_handler.run('tools/device/vif_reset') == ExpectedShellResult


########################################################################################################################
test_wm2_validate_radio_mac_address_inputs = wm_config.get("wm2_validate_radio_mac_address", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_validate_radio_mac_address_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_validate_radio_mac_address(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        radio_band = test_config.get('radio_band')

    with step('Determine physical radio name'):
        phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
        assert phy_radio_name is not None

    test_args = get_command_arguments(
        phy_radio_name,
    )

    with step('Testcase'):
        assert dut_handler.run('tests/wm2/wm2_validate_radio_mac_address', test_args) == ExpectedShellResult


########################################################################################################################
test_wm2_verify_associated_clients_inputs = wm_config.get("wm2_verify_associated_clients", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_verify_associated_clients_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_client"], scope='session')
def test_wm2_verify_associated_clients(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    client_handler = pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        psk = 'FutTestPSK'
        interface_type = 'home_ap'
        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Arguments from device capabilities
        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')

        # Get physical radio name
        phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
        if phy_radio_name is None:
            raise FailedException(f'Could not determine phy_radio_name for radio_band:{radio_band}')

        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()

        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        check_chan_args = get_command_arguments(
            channel,
            phy_radio_name,
        )

        client_connect_args = get_command_arguments(
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
            '-dhcp false',
            '-internet_ip false',
        )

    with step('Retrieve Client MAC'):
        # Retrieve the expected Client MAC to be used at actual testcase script
        client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
        if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
            pytest.skip('Failed to retrieve Client MAC address')
        check_assoc_client_args = get_command_arguments(
            vif_name,
            client_mac_addr_res[1],
        )

    with step('Configure Home AP interface'):
        # 1. Create and configure home AP interface
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            psk=psk,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ssid,
        )
    with step('Check channel readiness'):
        # 2. On DUT - Check if channel is ready for use
        assert dut_handler.run('tools/device/check_channel_is_ready', check_chan_args) == ExpectedShellResult
    with step('Client connection'):
        # 3. On Client - Connect to DUT
        assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
    with step('Testcase'):
        # 4. On DUT - Check contents of tested table
        assert dut_handler.run('tests/wm2/wm2_verify_associated_clients', check_assoc_client_args) == ExpectedShellResult


########################################################################################################################
test_wm2_verify_sta_send_csa_inputs = wm_config.get("wm2_verify_sta_send_csa", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_verify_sta_send_csa_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_ref"], scope='session')
def test_wm2_verify_sta_send_csa(test_config):
    dut_handler, ref_handler = pytest.dut_handler, pytest.ref_handler

    with step('Preparation'):
        # Test configuration values
        channel = test_config.get("channel")
        csa_channel = test_config.get("csa_channel")
        ht_mode = test_config.get("ht_mode")
        gw_radio_band = test_config.get("radio_band")
        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")
        encryption = test_config.get("encryption", "WPA2")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, gw_radio_band)
            assert dut_handler.validate_channel_ht_mode_band(csa_channel, ht_mode, gw_radio_band)
            assert ref_handler.validate_channel_ht_mode_band(channel, ht_mode, leaf_radio_band)
            assert ref_handler.validate_channel_ht_mode_band(csa_channel, ht_mode, leaf_radio_band)

        # GW bhaul Radio/VIF constant arguments
        gw_bhaul_interface_type = 'backhaul_ap'
        # GW device capabilities
        gw_phy_radio_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.phy_radio_name.{gw_radio_band}')
        gw_bhaul_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{gw_bhaul_interface_type}.{gw_radio_band}')

    with step('Assemble testcase parameters'):
        gw_get_vif_mac_args = get_command_arguments(
            'Wifi_VIF_State', 'mac',
            '-w', 'if_name', gw_bhaul_ap_if_name,
        )
        gw_update_csa_channel_args = get_command_arguments(
            'Wifi_Radio_Config',
            '-w', 'if_name', gw_phy_radio_if_name,
            '-u', 'channel', csa_channel,
        )
        gw_wait_csa_channel_args = get_command_arguments(
            'Wifi_Radio_Config',
            '-w', 'if_name', gw_phy_radio_if_name,
            '-is', 'channel', csa_channel,
        )

    try:
        with step('VIF clean'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset') == ExpectedShellResult
        with step(f'Put device into {device_mode.upper()} mode'):
            # Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('GW AP and LEAF STA creation, configuration and GW GRE configuration'):
            # On DUT - Create and configure GW bhaul AP interface
            # On REF - Create and configure LEAF bhaul STA interfaces
            # On DUT - Configure GRE tunnel
            assert create_and_configure_bhaul_connection_gw_leaf(channel, gw_radio_band, leaf_radio_band, ht_mode, wifi_security_type, encryption)
        with step('Determine DUT/GW MAC'):
            gw_mac_res = dut_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', gw_get_vif_mac_args, print_out=True)
            assert gw_mac_res[1] is not None and gw_mac_res[1] != '' and gw_mac_res[0] == ExpectedShellResult
        with step('GW trigger CSA'):
            # On DUT - Update GW channel to csa_channel only by Wifi_Radio_Config
            assert dut_handler.run('tools/device/ovsdb/update_ovsdb_entry', gw_update_csa_channel_args) == ExpectedShellResult
        with step('GW wait for channel'):
            # On DUT - Waitfor GW channel to being set in State stable, reason for it is CSA will be complete
            # if LEAF VIF is still connected on previous channel
            assert dut_handler.run('tools/device/ovsdb/wait_ovsdb_entry', gw_wait_csa_channel_args) == ExpectedShellResult
        with step('Testcase'):
            leaf_verify_csa_msg_args = get_command_arguments(
                gw_mac_res[1],
                csa_channel,
                ht_mode,
            )
            # On REF - Check for ieee80211_mgmt_sta_send_csa_rx_nl_msg message on REF
            assert ref_handler.run('tests/wm2/wm2_verify_sta_send_csa_msg', leaf_verify_csa_msg_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            dut_handler.run('tools/device/vif_reset', disable_fut_exception=True)
            ref_handler.run('tools/device/vif_reset', disable_fut_exception=True)


########################################################################################################################
test_wm2_verify_wifi_security_modes_inputs = wm_config.get("wm2_verify_wifi_security_modes", [])
test_wm2_verify_wifi_security_modes_scenarios = [
    {
        "channel": g["channel"],
        "ht_mode": g["ht_mode"],
        "radio_band": g["radio_band"],
        "encryption": a,
        "wifi_security_type": "wpa" if "wifi_security_type" not in g else g["wifi_security_type"],
        **get_config_opts(g),
    }
    for g in test_wm2_verify_wifi_security_modes_inputs for a in g["encryption_list"]
]


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_wm2_verify_wifi_security_modes_scenarios)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_wm2_verify_wifi_security_modes(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    client_handler = pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get('encryption', "WPA2")
        wifi_security_type = test_config.get('wifi_security_type')
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "FutTestPSK"
        client_model = client_handler.device_config.get_or_raise('model_string')
        client_wpa_type = encryption.lower()

        if encryption == "WPA3":
            if client_model != "linux":
                pytest.skip('A WiFi6 client is required for this testcase, skipping.')
        elif encryption == "WPA3-transition":
            client_wpa_type = "wpa2" if client_model != "linux" else "wpa3"

        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

    with step('Assemble testcase parameters'):
        # Testcase arguments
        gw_bhaul_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        check_ap_args = get_command_arguments(
            'Wifi_VIF_State',
            '-w', 'if_name', gw_bhaul_ap_if_name,
            '-is', 'enabled', "true",
        )

        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')

        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            '-dhcp false',
            '-internet_ip false',
        ]

        if client_wpa_type != "open":
            client_connect_args_base.append(f"-psk {psk}")

        client_connect_args = get_command_arguments(*client_connect_args_base)

    with step('VIF reset'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult

    with step('Configure Home AP interface'):
        # Create and configure home AP interface
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            psk=psk,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ssid,
            reset_vif=False,
        )

    with step('Testcase'):
        assert dut_handler.run('tools/device/ovsdb/wait_ovsdb_entry', check_ap_args) == ExpectedShellResult
    with step('Client connection'):
        # Connect Client to AP - fails if cannot associate
        assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult


########################################################################################################################
test_wm2_wifi_security_mix_on_multiple_aps_inputs = wm_config.get("wm2_wifi_security_mix_on_multiple_aps", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dfs()
@pytest.mark.parametrize('test_config', test_wm2_wifi_security_mix_on_multiple_aps_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut", "wm2_fut_setup_client"], scope='session')
def test_wm2_wifi_security_mix_on_multiple_aps(test_config):
    server_handler, dut_handler, ref_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        vif_config = test_config.get('vif_config')
        encryption_list = test_config.get("encryption_list", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        mode = 'ap'

        # Derived arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_model = client_handler.device_config.get_or_raise('model_string')
        # Cycle through provided list of security modes
        encryption_cycle = cycle(encryption_list)

    with step('VIF reset'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult

    with step('Testcase'):
        for interface in vif_config:
            # Prepare AP configurations
            vif_name, vif_radio_idx = vif_config[interface]
            ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}_{vif_radio_idx}"
            psk = f"FUT_psk_{vif_name}_{vif_radio_idx}"
            encryption = next(encryption_cycle)

            if encryption == "WPA3":
                if client_model != "linux":
                    log.info('A WiFi6 client is required for WPA3 security mode, defaulting to WPA2.')
                    encryption = "WPA2"

            client_wpa_type = encryption.lower()

            configure_ap_interface(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                psk=psk,
                device_name='dut',
                interface_type=interface,
                mode=mode,
                ssid=ssid,
                vif_name=vif_name,
                vif_radio_idx=vif_radio_idx,
                reset_vif=False,
            )

            if interface == 'backhaul_ap':
                bhaul_sta_interface_type = 'backhaul_sta'
                gw_vif_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface}.{radio_band}')
                leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, radio_band)
                bhaul_sta_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{bhaul_sta_interface_type}.{leaf_radio_band}')
                leaf_onboard_type = 'gre'

                leaf_bhaul_sta_radio_vif_args_base = [
                    f"-if_name {bhaul_sta_if_name}",
                    f"-ssid {ssid}",
                    f"-onboard_type {leaf_onboard_type}",
                    f"-channel {channel}",
                    f"-wifi_security_type {wifi_security_type}",
                    '-clear_wcc',
                    '-wait_ip',
                ]
                leaf_bhaul_sta_radio_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, psk)
                leaf_bhaul_sta_radio_vif_args = get_command_arguments(*leaf_bhaul_sta_radio_vif_args_base)
                assert ref_handler.run('tools/device/configure_sta_interface', leaf_bhaul_sta_radio_vif_args) == ExpectedShellResult

                bhaul_sta_vif_mac_args = get_command_arguments(f'if_name=={bhaul_sta_if_name}')
                bhaul_sta_vif_mac_ec, bhaul_sta_vif_mac, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', bhaul_sta_vif_mac_args, print_out=True)
                check_assoc_leaf_args = get_command_arguments(
                    gw_vif_if_name,
                    bhaul_sta_vif_mac,
                )
                # On DUT - Wait for AP to report associated STA
                assert dut_handler.run('tests/wm2/wm2_verify_associated_leaf', check_assoc_leaf_args) == ExpectedShellResult
            else:
                client_connect_args_base = [
                    client_wpa_type,
                    client_network_namespace,
                    client_wlan_if_name,
                    client_wpa_supp_cfg_path,
                    ssid,
                    '-dhcp false',
                    '-internet_ip false',
                ]

                if client_wpa_type != "open":
                    client_connect_args_base.append(f"-psk {psk}")

                client_connect_args = get_command_arguments(*client_connect_args_base)

                assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
