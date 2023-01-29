from datetime import datetime

import allure
import pytest

from framework.tools.functions import FailedException, get_command_arguments, step
from framework.tools.set_device_mode import configure_device_mode
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
onbrd_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='ONBRD')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="onbrd_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_onbrd_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='dm')
    server_handler.recipe.clear_full()
    with step('ONBRD setup'):
        assert dut_handler.run('tests/dm/onbrd_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    with step('Put device into ROUTER mode'):
        assert configure_device_mode(device_name='dut', device_mode='router')
    server_handler.recipe.mark_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="onbrd_fut_setup_ref", depends=["compat_ref_ready", "onbrd_fut_setup_dut"], scope='session')
def test_onbrd_fut_setup_ref():
    server_handler, ref_handler = pytest.server_handler, pytest.ref_handler
    with step('Transfer'):
        assert ref_handler.clear_tests_folder()
        assert ref_handler.transfer(manager='dm')
    server_handler.recipe.clear()
    with step('ONBRD setup'):
        assert ref_handler.run('tests/dm/onbrd_setup', ref_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.add_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="onbrd_fut_setup_client", depends=["compat_client_ready", "onbrd_fut_setup_dut"], scope='session')
def test_onbrd_fut_setup_client():
    server_handler, client_handler = pytest.server_handler, pytest.client_handler
    with step('Transfer'):
        assert client_handler.clear_tests_folder()
        assert client_handler.transfer(manager='dm')
    server_handler.recipe.clear()
    # Add Client setup command here
    server_handler.recipe.add_setup()


########################################################################################################################
test_onbrd_set_and_verify_bridge_mode_inputs = onbrd_config.get('onbrd_set_and_verify_bridge_mode', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_set_and_verify_bridge_mode_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_set_and_verify_bridge_mode(test_config):
    dut_handler = pytest.dut_handler

    try:
        with step('Testcase'):
            assert configure_device_mode(device_name='dut', device_mode='bridge')
    finally:
        with step('Restore connection'):
            # Restore connection - run onbrd_setup.sh
            dut_handler.run('tests/dm/onbrd_setup')


########################################################################################################################
test_onbrd_verify_client_certificate_files_inputs = onbrd_config.get('onbrd_verify_client_certificate_files', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_client_certificate_files_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_client_certificate_files(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('cert_file'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_client_certificate_files', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_client_tls_connection_inputs = onbrd_config.get('onbrd_verify_client_tls_connection', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_client_tls_connection_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_client_tls_connection(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        tls_ver = test_config.get('tls_ver')

    with step('Cloud preparation'):
        assert server_handler.fut_cloud.change_tls_ver(tls_ver)
        assert server_handler.fut_cloud.restart_cloud()

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_client_tls_connection', do_cloud_log=True) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_dhcp_dry_run_success_inputs = onbrd_config.get('onbrd_verify_dhcp_dry_run_success', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_dhcp_dry_run_success_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_dhcp_dry_run_success(test_config):
    dut_handler = pytest.dut_handler

    with step('Check device if WANO enabled'):
        # Check if WANO is enabled, if yes, interface_name_wan_bridge does not exist, test should be skipped
        check_kconfig_wano_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
        check_kconfig_wano_ec = dut_handler.run('tools/device/check_kconfig_option', check_kconfig_wano_args)
        if check_kconfig_wano_ec == 0:
            pytest.skip('Testcase not applicable to WANO enabled devices')

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_dhcp_dry_run_success', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_dut_client_certificate_file_on_server_inputs = onbrd_config.get('onbrd_verify_dut_client_certificate_file_on_server', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_dut_client_certificate_file_on_server_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_dut_client_certificate_file_on_server(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Get Certificate details'):
        eth_wan_name = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
        cert_file_path_args = get_command_arguments("cert_file", "full_path")
        ca_file_path_args = get_command_arguments("ca_file", "full_path")
        cert_file_args = get_command_arguments("cert_file", "file_name")
        ca_file_args = get_command_arguments("ca_file", "file_name")

        cert_full_path = dut_handler.run_raw('tools/device/get_client_certificate', cert_file_path_args, print_out=True)
        if cert_full_path[0] != ExpectedShellResult or cert_full_path[1] == '' or cert_full_path[1] is None:
            raise FailedException('Failed to retrieve Client certificate path from device')

        ca_full_path = dut_handler.run_raw('tools/device/get_client_certificate', ca_file_path_args, print_out=True)
        if ca_full_path[0] != ExpectedShellResult or ca_full_path[1] == '' or ca_full_path[1] is None:
            raise FailedException('Failed to retrieve CA certificate path from device')

        cert_file = dut_handler.run_raw('tools/device/get_client_certificate', cert_file_args, print_out=True)
        if cert_file[0] != ExpectedShellResult or cert_file[1] == '' or cert_file[1] is None:
            raise FailedException('Failed to retrieve Client certificate from device')

        ca_file = dut_handler.run_raw('tools/device/get_client_certificate', ca_file_args, print_out=True)
        if ca_file[0] != ExpectedShellResult or ca_file[1] == '' or ca_file[1] is None:
            raise FailedException('Failed to retrieve CA certificate from device')

    # Copy Client and CA certificates from DUT onto RPI Server
    with step('Copy certificates to server'):
        cert_location = 'tools/server/files'
        get_cert_args = get_command_arguments("-D dut", f'-f {cert_full_path[1]}', f'-d {cert_location}')
        get_ca_args = get_command_arguments("-D dut", f'-f {ca_full_path[1]}', f'-d {cert_location}')
        assert server_handler.run('tools/get_file_from_device', get_cert_args, folder='framework', ext='.py') == ExpectedShellResult
        assert server_handler.run('tools/get_file_from_device', get_ca_args, folder='framework', ext='.py') == ExpectedShellResult

        # pod_api specifics: files are transferred into subfolder "device_name"
        cert_verify_args = get_command_arguments(
            f'{cert_location}/{dut_handler.name}/{cert_file[1]}',
            f'{cert_location}/{dut_handler.name}/{ca_file[1]}',
        )

    # Get common name of the Client certificate for validation
    with step('Get common name from certificate'):
        common_name = server_handler.run_raw(
            'tools/server/get_common_name_from_certificate',
            get_command_arguments(f'{cert_location}/{dut_handler.name}/{cert_file[1]}'),
            as_sudo=True)
        if common_name[0] != ExpectedShellResult or common_name[1] == '' or common_name[1] is None:
            raise FailedException('Failed to retrieve Common Name of certificate')

        cert_cn_verify_args = get_command_arguments(common_name[1], eth_wan_name)

    with step('Testcase'):
        # Validate Client certificate against CA on RPI Server
        assert server_handler.run('tools/server/verify_dut_client_certificate_file_on_server', cert_verify_args,
                                  as_sudo=True) == ExpectedShellResult

    try:
        # Validate common name of Client certificate on DUT (optional, pass either way)
        with step('Testcase - optional'):
            dut_handler.run('tools/device/verify_dut_client_certificate_common_name', cert_cn_verify_args)
    finally:
        pass


########################################################################################################################
test_onbrd_verify_dut_system_time_accuracy_inputs = onbrd_config.get('onbrd_verify_dut_system_time_accuracy', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_dut_system_time_accuracy_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_dut_system_time_accuracy(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        time_sec_since_epoch = int(datetime.utcnow().strftime('%s'))
        test_args = get_command_arguments(
            time_sec_since_epoch,
            test_config.get('time_accuracy'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_dut_system_time_accuracy', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_fw_version_awlan_node_inputs = onbrd_config.get('onbrd_verify_fw_version_awlan_node', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_fw_version_awlan_node_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_fw_version_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('search_rule'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_fw_version_awlan_node', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_home_vaps_on_home_bridge_inputs = onbrd_config.get('onbrd_verify_home_vaps_on_home_bridge', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_home_vaps_on_home_bridge_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_home_vaps_on_home_bridge(test_config):
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

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        interface_type = 'home_ap'
        home_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx_all = dut_handler.capabilities.get_or_raise("interfaces.vif_radio_idx")
        assert interface_type in vif_radio_idx_all
        vif_radio_idx = vif_radio_idx_all[interface_type]

        # Constant arguments
        enabled = "true"
        mode = "ap"
        preshared_key = "FutTestPSK"
        ssid_broadcast = "enabled"
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        test_args = get_command_arguments(
            home_ap_if_name,
            dut_handler.capabilities.get_or_raise('interfaces.lan_bridge'),
        )
        # Keep the same order of parameters
        create_radio_vif_args_base = [
            f"-if_name {phy_radio_name}",
            f"-channel {channel}",
            f"-enabled {enabled}",
            f"-ht_mode {ht_mode}",
            f"-mode {mode}",
            f"-ssid {ssid}",
            f"-ssid_broadcast {ssid_broadcast}",
            f"-vif_if_name {home_ap_if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-wifi_security_type {wifi_security_type}",
        ]

        create_radio_vif_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, preshared_key)
        create_radio_vif_args = get_command_arguments(*create_radio_vif_args_base)

    with step('Radio VIF creation'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        assert dut_handler.run('tools/device/create_radio_vif_interface', create_radio_vif_args) == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_home_vaps_on_home_bridge', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_home_vaps_on_radios_inputs = onbrd_config.get('onbrd_verify_home_vaps_on_radios', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_home_vaps_on_radios_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_home_vaps_on_radios(test_config):
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

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        interface_type = 'home_ap'
        home_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx_all = dut_handler.capabilities.get_or_raise("interfaces.vif_radio_idx")
        assert interface_type in vif_radio_idx_all
        vif_radio_idx = vif_radio_idx_all[interface_type]

        # Constant arguments
        enabled = "true"
        mode = "ap"
        preshared_key = "FutTestPSK"
        ssid_broadcast = "enabled"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        test_args = get_command_arguments(
            home_ap_if_name,
        )
        # Keep the same order of parameters
        create_radio_vif_args_base = [
            f"-if_name {phy_radio_name}",
            f"-channel {channel}",
            f"-enabled {enabled}",
            f"-ht_mode {ht_mode}",
            f"-mode {mode}",
            f"-ssid {ssid}",
            f"-ssid_broadcast {ssid_broadcast}",
            f"-vif_if_name {home_ap_if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-wifi_security_type {wifi_security_type}",
        ]
        create_radio_vif_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, preshared_key)
        create_radio_vif_args = get_command_arguments(*create_radio_vif_args_base)

    with step('Radio VIF creation'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        assert dut_handler.run('tools/device/create_radio_vif_interface', create_radio_vif_args) == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_home_vaps_on_radios', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_id_awlan_node_inputs = onbrd_config.get('onbrd_verify_id_awlan_node', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_id_awlan_node_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_id_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        # Get DUT MAC address
        dut_mac_args = get_command_arguments(
            'Wifi_Inet_State', 'hwaddr', '-w', 'if_name', dut_if_lan_br_name,
        )
        dut_mac_ec, dut_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', dut_mac_args, print_out=True)
        assert dut_mac is not None and dut_mac != '' and dut_mac_ec == ExpectedShellResult

        test_args = get_command_arguments(
            dut_mac,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_id_awlan_node', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_manager_hostname_resolved_inputs = onbrd_config.get('onbrd_verify_manager_hostname_resolved', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_manager_hostname_resolved_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_manager_hostname_resolved(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Set device type: "extender" or "residential_gateway"
        dut_device_type = dut_handler.capabilities.get_or_raise('device_type')
        is_extender = "true" if dut_device_type == "extender" else "false"

        test_args = get_command_arguments(
            is_extender,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_manager_hostname_resolved', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_model_awlan_node_inputs = onbrd_config.get('onbrd_verify_model_awlan_node', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_model_awlan_node_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_model_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Argument from device capabilities
        test_args = get_command_arguments(
            dut_handler.capabilities.get_or_raise('model_string'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_model_awlan_node', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_number_of_radios_inputs = onbrd_config.get('onbrd_verify_number_of_radios', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_number_of_radios_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_number_of_radios(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Argument from device capabilities
        radio_channels = dut_handler.capabilities.get_or_raise('interfaces.radio_channels')
        # Calculate the expected number of radios on device
        radio_bands = [band for band in radio_channels if radio_channels[band] is not None]
        test_args = get_command_arguments(
            len(radio_bands),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_number_of_radios', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_onbrd_vaps_on_radios_inputs = onbrd_config.get('onbrd_verify_onbrd_vaps_on_radios', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_onbrd_vaps_on_radios_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_onbrd_vaps_on_radios(test_config):
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

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        interface_type = 'onboard_ap'
        onboard_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        vif_radio_idx_all = dut_handler.capabilities.get_or_raise("interfaces.vif_radio_idx")
        assert interface_type in vif_radio_idx_all
        vif_radio_idx = vif_radio_idx_all[interface_type]
        # Constant arguments
        enabled = "true"
        mode = "ap"
        preshared_key = "FutTestPSK"
        ssid_broadcast = "disabled"
        # Derived variables
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        test_args = get_command_arguments(
            onboard_ap_if_name,
        )
        # Keep the same order of parameters
        create_radio_vif_args_base = [
            f"-if_name {phy_radio_name}",
            f"-channel {channel}",
            f"-enabled {enabled}",
            f"-ht_mode {ht_mode}",
            f"-mode {mode}",
            f"-ssid {ssid}",
            f"-ssid_broadcast {ssid_broadcast}",
            f"-vif_if_name {onboard_ap_if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-wifi_security_type {wifi_security_type}",
        ]
        create_radio_vif_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, preshared_key)
        create_radio_vif_args = get_command_arguments(*create_radio_vif_args_base)

    with step('Radio VIF creation'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        assert dut_handler.run('tools/device/create_radio_vif_interface', create_radio_vif_args) == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_onbrd_vaps_on_radios', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_redirector_address_awlan_node_inputs = onbrd_config.get('onbrd_verify_redirector_address_awlan_node', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_redirector_address_awlan_node_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_redirector_address_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_redirector_address_awlan_node') == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_router_mode_inputs = onbrd_config.get('onbrd_verify_router_mode', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_router_mode_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_router_mode(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Determine wired uplink interface name: WAN bridge or ETH WAN
        wan_handling_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
        # Script returns 0 if wan_handling_args match the kconfig!
        has_wano = dut_handler.run('tools/device/check_kconfig_option', wan_handling_args) == ExpectedShellResult
        dut_device_type = dut_handler.capabilities.get_or_raise('device_type')
        if has_wano or dut_device_type == "residential_gateway":
            wan_if_type = 'primary_wan_interface'
        else:
            wan_if_type = 'wan_bridge'
        dut_wan_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{wan_if_type}')
        if not dut_wan_if_name:
            raise FailedException(f'Could not determine {wan_if_type} from device configuration')
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        if not dut_if_lan_br_name:
            raise FailedException('Could not determine interface_name_lan_bridge from device configuration')

        # Test arguments from testcase config
        dut_dhcp_start_pool = test_config.get('dhcp_start_pool')
        dut_dhcp_end_pool = test_config.get('dhcp_end_pool')
        internal_inet_addr = test_config.get('gateway_inet_addr')

        test_args = get_command_arguments(
            dut_wan_if_name,
            dut_if_lan_br_name,
            dut_dhcp_start_pool,
            dut_dhcp_end_pool,
            internal_inet_addr,
        )

    try:
        with step('Testcase'):
            assert dut_handler.run('tests/dm/onbrd_verify_router_mode', test_args) == ExpectedShellResult
    finally:
        # Restore connection after modifying uplink, then assert test results
        with step('Restore connection'):
            dut_handler.run('tests/dm/onbrd_setup')


########################################################################################################################
test_onbrd_verify_wan_iface_mac_addr_inputs = onbrd_config.get('onbrd_verify_wan_iface_mac_addr', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_wan_iface_mac_addr_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_wan_iface_mac_addr(test_config):
    dut_handler = pytest.dut_handler

    with step('Check device if WANO enabled'):
        wan_handling_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
        # Script returns 0 if wan_handling_args match the kconfig!
        has_wano = dut_handler.run('tools/device/check_kconfig_option', wan_handling_args) == ExpectedShellResult

    with step('Testcase'):
        if has_wano:
            assert dut_handler.run('tests/dm/onbrd_verify_wan_iface_mac_addr') == ExpectedShellResult
        else:
            test_args = get_command_arguments(
                dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface'),
            )
            assert dut_handler.run('tests/dm/onbrd_verify_wan_iface_mac_addr', test_args) == ExpectedShellResult


########################################################################################################################
test_onbrd_verify_wan_ip_address_inputs = onbrd_config.get('onbrd_verify_wan_ip_address', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_onbrd_verify_wan_ip_address_inputs)
@pytest.mark.dependency(depends=["onbrd_fut_setup_dut"], scope='session')
def test_onbrd_verify_wan_ip_address(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        if "if_name" in test_config:
            if_name = test_config.get("if_name")
        else:
            wan_handling_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
            # Script returns 0 if wan_handling_args match the kconfig!
            has_wano = dut_handler.run('tools/device/check_kconfig_option', wan_handling_args) == ExpectedShellResult
            dut_device_type = dut_handler.capabilities.get_or_raise('device_type')
            if has_wano or dut_device_type == "residential_gateway":
                if_name = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
            else:
                if_name = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')

        test_args = get_command_arguments(
            if_name,
            server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/onbrd_verify_wan_ip_address', test_args) == ExpectedShellResult
