from pathlib import Path

import allure
import pytest

import framework.tools.logger
from framework.tools.configure_ap_interface import configure_ap_interface
from framework.tools.functions import FailedException, get_command_arguments, step
from framework.tools.mqtt_trigger_validate_msg import fut_mqtt_trigger_validate_message
from framework.tools.set_device_mode import configure_device_mode
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

# Read entire testcase configuration
fsm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='FSM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="fsm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_fsm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='fsm')
    server_handler.recipe.clear_full()
    with step('FSM setup'):
        assert dut_handler.run('tests/fsm/fsm_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    with step('Put device into ROUTER mode'):
        assert configure_device_mode(device_name='dut', device_mode='router')
    server_handler.recipe.mark_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="fsm_fut_setup_client", depends=["compat_client_ready", "fsm_fut_setup_dut"], scope='session')
def test_fsm_fut_setup_client():
    server_handler, client_handler = pytest.server_handler, pytest.client_handler
    with step('Transfer'):
        assert client_handler.clear_tests_folder()
        assert client_handler.transfer(manager='fsm')
    server_handler.recipe.add_setup()
    # Add Client setup command here
    server_handler.recipe.add_setup()


########################################################################################################################
test_fsm_configure_fsm_tables_inputs = fsm_config.get('fsm_configure_fsm_tables', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_fsm_tables_inputs)
def test_fsm_configure_fsm_tables(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Arguments from device capabilities
        lan_bridge_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        # Test arguments from testcase config
        tap_name_postfix = test_config.get("tap_name_postfix")
        handler = test_config.get("handler")
        plugin = test_config.get("plugin")
        opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
        fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
        test_args = get_command_arguments(
            lan_bridge_if_name,
            tap_name_postfix,
            handler,
            fsm_plugin_path,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/fsm/fsm_configure_fsm_tables', test_args) == ExpectedShellResult


########################################################################################################################
test_fsm_configure_openflow_rules_inputs = fsm_config.get('fsm_configure_openflow_rules', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_openflow_rules_inputs)
def test_fsm_configure_openflow_rules(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Arguments from device capabilities
        lan_bridge_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        # Test arguments from testcase config
        action = test_config.get("action")
        rule = test_config.get("rule")
        token = test_config.get('token')
        test_args = get_command_arguments(
            lan_bridge_if_name,
            action,
            rule,
            token,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/fsm/fsm_configure_of_rules', test_args) == ExpectedShellResult


########################################################################################################################
test_fsm_configure_test_dns_plugin_inputs = fsm_config.get('fsm_configure_test_dns_plugin', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_dns_plugin_inputs)
def test_fsm_configure_test_dns_plugin(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        device_mode = test_config.get('device_mode')
        fsm_url_block = test_config.get('url_block')
        fsm_url_redirect = test_config.get('url_redirect')
        plugin = test_config.get("plugin")
        wc_plugin = test_config.get("plugin_web_cat")

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_dns_pl_net"
        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        configure_remove_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()

        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_topic = "fsm_configure_test_dns_plugin"
        location_id = "1000"
        node_id = "100"

        with step('Check FSM plugins existence'):
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_plugin_path)) == ExpectedShellResult
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            wc_plugin_path = Path(wc_plugin) if Path(wc_plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{wc_plugin}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(wc_plugin_path)) == ExpectedShellResult

        # Testcase specific args
        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
        ]

        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        if "client_retry" in test_config:
            client_connect_args_base += [
                f"-retry {test_config.get('client_retry')}",
            ]
        if "client_connection_timeout" in test_config:
            client_connect_args_base += [
                f"-connect_timeout {test_config.get('client_connection_timeout')}",
            ]
        client_connect_args = get_command_arguments(*client_connect_args_base)

        fsm_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
        )

        fsm_client_check_args = get_command_arguments(
            f'"{client_handler.device_config.get_or_raise("namespace_enter_cmd")}"',
            fsm_url_block,
            fsm_url_redirect,
        )
        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.tdns',
            f'{dut_if_lan_br_name}.tx',
        )

    try:
        # 1. Ensure WAN connectivity
        with step('Ensure WAN connectivity'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Create tap interfaces'):
            # 2. Create and configure tap interfaces
            assert dut_handler.run('tools/device/configure_tap_interfaces', configure_remove_tap_interface_args) == ExpectedShellResult
        with step('MQTT connection establishment and message collection'):
            assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/fut_configure_mqtt', fsm_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
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
            # 4. Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        with step('Retrieve Client MAC'):
            # Retrieve the expected Client MAC to be used at actual testcase script
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')
            fsm_pl_cfg_args = get_command_arguments(
                dut_if_lan_br_name,
                fsm_url_block,
                fsm_url_redirect,
                fsm_plugin_path,
                wc_plugin_path,
                mqtt_topic,
                client_mac_addr_res[1],
            )
        with step('Configure DNS plugin'):
            assert dut_handler.run('tools/device/configure_dns_plugin', fsm_pl_cfg_args, do_mqtt_log=True) == ExpectedShellResult
        with step('Testcase - Trigger DNS request and listen for MQTT'):
            def _trigger():
                return client_handler.run('tools/client/fsm/fsm_test_dns_plugin', fsm_client_check_args, as_sudo=True, do_mqtt_log=True)
            assert fut_mqtt_trigger_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={
                    'dnsAddress': fsm_url_block,
                    'policy': 'dev_dns_policy',
                    'action': 'allowed',
                    'ruleName': 'dev_dns_policy_rule_0',
                    'deviceMac': client_mac_addr_res[1].upper(),
                    'nodeId': node_id,
                    'locationId': location_id,
                },
            )
    finally:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode was required
            with step('Put device into ROUTER mode'):
                assert configure_device_mode(device_name='dut', device_mode='router')
        # FSM Cleanup
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_dpi_http_sni_request_inputs = fsm_config.get('fsm_configure_test_dpi_http_sni_request', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_dpi_http_sni_request_inputs)
def test_fsm_configure_test_dpi_http_sni_request(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        device_mode = test_config.get('device_mode')
        fsm_url = test_config.get('url')
        plugin_gk = test_config.get("plugin_gk")
        plugin_dpi_sni = test_config.get("plugin_dpi_sni")
        verdict = test_config.get("verdict")

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_dns_pl_net"

        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        configure_remove_dpi_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        configure_dpi_openflow_rules_args = get_command_arguments(
            dut_if_lan_br_name,
        )

        # Get client MAC address
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )
        with step('Get Client MAC address'):
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()

        # Get DUT MAC address
        gw_mac_args = get_command_arguments(
            'Wifi_Inet_State', 'hwaddr', '-w', 'if_name', dut_if_lan_br_name,
        )
        with step('Get DUT MAC address'):
            gw_mac_ec, gw_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', gw_mac_args, print_out=True)
            assert gw_mac is not None and gw_mac != '' and gw_mac_ec == ExpectedShellResult

        # Get RPI Server MAC address
        with step('Get RPI Server MAC address'):
            server_mac = server_handler.get_wan_mac()
            assert server_mac is not None and gw_mac != ''

        with step('Check FSM plugins existence'):
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            fsm_gk_plugin_path = Path(plugin_gk) if Path(plugin_gk).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin_gk}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_gk_plugin_path)) == ExpectedShellResult
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            fsm_dpi_sni_plugin_path = Path(plugin_dpi_sni) if Path(plugin_dpi_sni).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin_dpi_sni}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_dpi_sni_plugin_path)) == ExpectedShellResult

        # Testcase specific args
        client_connect_args = get_command_arguments(
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
        )

        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.devdpi',
        )

        fsm_client_check_args = get_command_arguments(
            f'"{client_handler.device_config.get_or_raise("namespace_enter_cmd")}"',
            fsm_url,
        )

        fsm_test_gatekeeper_verdict_args = get_command_arguments(
            verdict,
        )

        configure_sni_plugin_openflow_tags_args = get_command_arguments(
            gw_mac,
            client_mac_addr_res[1],
            server_mac,
        )

        fake_location_id = "100000000000000000000001"
        fake_node_id = "1000000001"
        configure_awlan_node_args = get_command_arguments(
            fake_location_id,
            fake_node_id,
        )

    try:
        # 1. Ensure WAN connectivity
        with step('Ensure WAN connectivity'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Configure AWLAN table'):
            # 2. Configure AWLAN_Node table
            assert dut_handler.run('tools/device/configure_awlan_node', configure_awlan_node_args) == ExpectedShellResult
        with step('Create tap interface'):
            # 3. Create and configure tap interface
            assert dut_handler.run('tools/device/configure_dpi_tap_interface', configure_remove_dpi_tap_interface_args) == ExpectedShellResult
        with step('Configure plugins'):
            # 4. Configure plugins (Gatekeeper and SNI)
            with step('Configure Openflow rules'):
                assert dut_handler.run('tools/device/configure_dpi_openflow_rules', configure_dpi_openflow_rules_args) == ExpectedShellResult
            with step('Configure SNI plugin Openflow tags'):
                assert dut_handler.run('tools/device/configure_sni_plugin_openflow_tags', configure_sni_plugin_openflow_tags_args) == ExpectedShellResult
            with step('Configure SNI plugin'):
                assert dut_handler.run('tools/device/configure_dpi_sni_plugin', configure_awlan_node_args) == ExpectedShellResult
            with step('Configure SNI plugin policy'):
                assert dut_handler.run('tools/device/configure_gatekeeper_policy') == ExpectedShellResult
        with step('Configure Home AP interface'):
            # 5. Create and configure home AP interface
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
            # 6. Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        with step('Testcase'):
            # 7. Make curl http request on the client
            assert client_handler.run('tools/client/fsm/make_curl_http_request', fsm_client_check_args, as_sudo=True, do_gatekeeper_log=True) == ExpectedShellResult
            # 8. Check device log for FSM message creation
            assert dut_handler.run('tests/fsm/fsm_test_gatekeeper_verdict', fsm_test_gatekeeper_verdict_args, do_gatekeeper_log=True) == ExpectedShellResult
    finally:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode was required
            with step('Put device into ROUTER mode'):
                assert configure_device_mode(device_name='dut', device_mode='router')
        # FSM Cleanup
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_dpi_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_dpi_http_url_request_inputs = fsm_config.get('fsm_configure_test_dpi_http_url_request', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_dpi_http_url_request_inputs)
def test_fsm_configure_test_dpi_http_url_request(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)
        device_mode = test_config.get('device_mode')
        fsm_url = test_config.get('url')
        plugin_gk = test_config.get("plugin_gk")
        plugin_dpi_sni = test_config.get("plugin_dpi_sni")
        verdict = test_config.get("verdict")

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_dns_pl_net"
        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        # Build test script arguments
        configure_remove_dpi_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        configure_dpi_openflow_rules_args = get_command_arguments(
            dut_if_lan_br_name,
        )

        # Get client MAC address
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )
        with step('Get Client MAC address'):
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()

        # Get DUT MAC address
        with step('Get Client MAC address'):
            gw_mac_args = get_command_arguments(
                'Wifi_Inet_State', 'hwaddr', '-w', 'if_name', dut_if_lan_br_name,
            )
            gw_mac_ec, gw_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', gw_mac_args, print_out=True)
            assert gw_mac is not None and gw_mac != '' and gw_mac_ec == ExpectedShellResult

        # Get RPI Server MAC address
        with step('Get RPI Server MAC address'):
            server_mac = server_handler.get_wan_mac()
            assert server_mac is not None and gw_mac != ''

        # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
        with step('Check FSM plugins existence'):
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            fsm_gk_plugin_path = Path(plugin_gk) if Path(plugin_gk).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin_gk}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_gk_plugin_path)) == ExpectedShellResult
            fsm_dpi_sni_plugin_path = Path(plugin_dpi_sni) if Path(plugin_dpi_sni).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin_dpi_sni}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_dpi_sni_plugin_path)) == ExpectedShellResult

        # Testcase specific args
        client_connect_args = get_command_arguments(
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
        )

        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.devdpi',
        )

        fsm_client_check_args = get_command_arguments(
            f'"{client_handler.device_config.get_or_raise("namespace_enter_cmd")}"',
            fsm_url,
        )

        fsm_test_gatekeeper_verdict_args = get_command_arguments(
            verdict,
        )

        configure_sni_plugin_openflow_tags_args = get_command_arguments(
            gw_mac,
            client_mac_addr_res[1],
            server_mac,
        )

        fake_location_id = "100000000000000000000001"
        fake_node_id = "1000000001"
        configure_awlan_node_args = get_command_arguments(
            fake_location_id,
            fake_node_id,
        )

    try:
        # 1. Ensure WAN connectivity
        with step('Ensure WAN connectivity'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Create tap interface'):
            # 3. Create and configure tap interface
            assert dut_handler.run('tools/device/configure_dpi_tap_interface', configure_remove_dpi_tap_interface_args) == ExpectedShellResult
        with step('Configure Gatekeeper'):
            assert dut_handler.run('tools/device/configure_gatekeeper_plugin', configure_dpi_openflow_rules_args) == ExpectedShellResult
        with step('Configure plugins'):
            # 4. Configure plugins (Gatekeeper and SNI)
            with step('Configure Openflow rules'):
                assert dut_handler.run('tools/device/configure_dpi_openflow_rules', configure_dpi_openflow_rules_args) == ExpectedShellResult
            with step('Configure SNI plugin Openflow tags'):
                assert dut_handler.run('tools/device/configure_sni_plugin_openflow_tags', configure_sni_plugin_openflow_tags_args) == ExpectedShellResult
            with step('Configure SNI plugin'):
                assert dut_handler.run('tools/device/configure_dpi_sni_plugin', configure_awlan_node_args) == ExpectedShellResult
            with step('Configure SNI plugin policy'):
                assert dut_handler.run('tools/device/configure_gatekeeper_policy') == ExpectedShellResult
        with step('Configure Home AP interface'):
            # 5. Create and configure home AP interface
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
            # 6. Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        with step('Testcase'):
            # 7. Make curl http request on the client
            assert client_handler.run('tools/client/fsm/make_curl_http_request', fsm_client_check_args, as_sudo=True, do_mqtt_log=True) == ExpectedShellResult
            # 8. Check device log for FSM message creation
            assert dut_handler.run('tests/fsm/fsm_test_gatekeeper_verdict', fsm_test_gatekeeper_verdict_args) == ExpectedShellResult
    finally:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode was required
            with step('Put device into ROUTER mode'):
                assert configure_device_mode(device_name='dut', device_mode='router')
        # FSM Cleanup
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_dpi_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_http_plugin_inputs = fsm_config.get('fsm_configure_test_http_plugin', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_http_plugin_inputs)
def test_fsm_configure_test_http_plugin(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        plugin = test_config.get("plugin")
        user_agent = test_config.get("user_agent")
        device_mode = test_config.get('device_mode')
        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        configure_remove_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_http_pl_net"
        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_namespace_enter_cmd = client_handler.device_config.get_or_raise("namespace_enter_cmd")
        client_wpa_type = encryption.lower()
        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_topic = "fsm_configure_test_http_plugin"
        location_id = "1000"
        node_id = "100"

        with step('Check FSM plugins existence'):
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_plugin_path)) == ExpectedShellResult

        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
        ]

        if "client_retry" in test_config:
            client_connect_args_base += [
                f"-retry {test_config.get('client_retry')}",
            ]
        if "client_connection_timeout" in test_config:
            client_connect_args_base += [
                f"-connect_timeout {test_config.get('client_connection_timeout')}",
            ]
        client_connect_args = get_command_arguments(*client_connect_args_base)

        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        fsm_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            "http",
        )

        # Testcase specific args
        fsm_client_curl_req_args = get_command_arguments(
            f'"{client_namespace_enter_cmd}"',
            user_agent,
            'www.google.com',
        )

        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.thttp',
        )

    try:
        # 1. Ensure WAN connectivity
        with step('Ensure WAN connectivity'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Create tap interfaces'):
            # 2. Create and configure tap interfaces
            assert dut_handler.run('tools/device/configure_tap_interfaces', configure_remove_tap_interface_args) == ExpectedShellResult
        with step('MQTT connection establishment and message collection'):
            assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/fut_configure_mqtt', fsm_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
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
            # 4. Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        with step('Retrieve Client MAC'):
            # Retrieve the expected Client MAC to be used at actual testcase script
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')
            fsm_pl_cfg_args = get_command_arguments(
                dut_if_lan_br_name,
                fsm_plugin_path,
                mqtt_topic,
                client_mac_addr_res[1],
            )
        with step('HTTP plugin configuration'):
            # 6. Configure HTTP FSM plugin
            assert dut_handler.run('tools/device/configure_http_plugin', fsm_pl_cfg_args) == ExpectedShellResult
        with step('Testcase - Trigger HTTP user agent request and listen for MQTT'):
            def _trigger():
                # 7. Send curl request with user agent on Client
                assert client_handler.run('tools/client/fsm/make_curl_agent_req', fsm_client_curl_req_args, as_sudo=True, do_mqtt_log=True) == ExpectedShellResult
            assert fut_mqtt_trigger_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={
                    'nodeId': node_id,
                    'locationId': location_id,
                    'deviceMac': client_mac_addr_res[1].upper(),
                    'userAgent': user_agent,
                },
            )
    finally:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode was required
            with step('Put device into ROUTER mode'):
                assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_http_url_gatekeeper_verdict_inputs = fsm_config.get('fsm_configure_test_http_url_gatekeeper_verdict', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_http_url_gatekeeper_verdict_inputs)
def test_fsm_configure_test_http_url_gatekeeper_verdict(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        device_mode = test_config.get('device_mode')
        plugin_gk = test_config.get("plugin_gk")
        plugin_dpi_sni = test_config.get("plugin_dpi_sni")

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_dns_pl_net"

        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        configure_remove_dpi_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        configure_dpi_openflow_rules_args = get_command_arguments(
            dut_if_lan_br_name,
        )

        # Get client MAC address
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )
        with step('Get Client MAC address'):
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()

        # Get DUT MAC address
        gw_mac_args = get_command_arguments(
            'Wifi_Inet_State', 'hwaddr', '-w', 'if_name', dut_if_lan_br_name,
        )
        with step('Get DUT MAC address'):
            gw_mac_ec, gw_mac, std_err = dut_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', gw_mac_args, print_out=True)
            assert gw_mac is not None and gw_mac != '' and gw_mac_ec == ExpectedShellResult

        # Get RPI Server MAC address
        with step('Get RPI Server MAC address'):
            server_mac = server_handler.get_wan_mac()
            assert server_mac is not None and gw_mac != ''

        with step('Check FSM plugins existence'):
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            fsm_gk_plugin_path = Path(plugin_gk) if Path(plugin_gk).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin_gk}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_gk_plugin_path)) == ExpectedShellResult
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            fsm_dpi_sni_plugin_path = Path(plugin_dpi_sni) if Path(plugin_dpi_sni).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin_dpi_sni}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_dpi_sni_plugin_path)) == ExpectedShellResult

        # Testcase specific args
        client_connect_args = get_command_arguments(
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
        )

        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.devdpi',
        )

        configure_sni_plugin_openflow_tags_args = get_command_arguments(
            gw_mac,
            client_mac_addr_res[1],
            server_mac,
        )

        fake_location_id = "100000000000000000000001"
        fake_node_id = "1000000001"
        configure_awlan_node_args = get_command_arguments(
            fake_location_id,
            fake_node_id,
        )
        flush_gatekeeper_cache_args = [
            'FSM_Policy',
            '-i action flush_all',
            '-i name test_flush',
        ]
    try:
        # 1. Ensure WAN connectivity
        with step('Ensure WAN connectivity'):
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Configure AWLAN table'):
            # 2. Configure AWLAN_Node table
            assert dut_handler.run('tools/device/configure_awlan_node', configure_awlan_node_args) == ExpectedShellResult
        with step('Create tap interface'):
            # 3. Create and configure tap interface
            assert dut_handler.run('tools/device/configure_dpi_tap_interface', configure_remove_dpi_tap_interface_args) == ExpectedShellResult
        with step('Configure plugins'):
            # 4. Configure plugins (Gatekeeper and SNI)
            with step('Configure Openflow rules'):
                assert dut_handler.run('tools/device/configure_dpi_openflow_rules', configure_dpi_openflow_rules_args) == ExpectedShellResult
            with step('Configure SNI plugin Openflow tags'):
                assert dut_handler.run('tools/device/configure_sni_plugin_openflow_tags', configure_sni_plugin_openflow_tags_args) == ExpectedShellResult
            with step('Configure SNI plugin'):
                assert dut_handler.run('tools/device/configure_dpi_sni_plugin', configure_awlan_node_args, do_gatekeeper_log=True) == ExpectedShellResult
            with step('Configure SNI plugin policy'):
                assert dut_handler.run('tools/device/configure_gatekeeper_policy', do_gatekeeper_log=True) == ExpectedShellResult
        with step('Configure Home AP interface'):
            # 5. Create and configure home AP interface
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
            # 6. Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        results = {
            'allow': {},
            'block': {},
            'redirect': {},
        }
        with step('Testcase - verdict'):
            for verdict in ['allow', 'block', 'redirect']:
                with step(f'Testcase - verdict - {verdict}'):
                    server_handler.clear_gatekeeper_log()
                    with step('Flush FSM Gatekeeper cache'):
                        assert dut_handler.run('tools/device/ovsdb/insert_ovsdb_entry', flush_gatekeeper_cache_args, do_mgatekeeper_log=True) == ExpectedShellResult
                    fsm_client_check_args = get_command_arguments(
                        f'"{client_handler.device_config.get_or_raise("namespace_enter_cmd")}"',
                        f'http://fut.opensync.io:8000/gatekeeper/test/http_url/{verdict}',
                    )
                    fsm_test_gatekeeper_verdict_args = get_command_arguments(
                        f'http://fut.opensync.io/gatekeeper/test/http_url/{verdict}',
                        f'{verdict}ed' if verdict != 'redirect' else verdict,
                    )
                    # 7. Make curl http request on the client
                    curl_res = client_handler.run('tools/client/fsm/make_curl_http_request', fsm_client_check_args, as_sudo=True, do_gatekeeper_log=True, disable_fut_exception=True) == ExpectedShellResult
                    # 8. Check device log for FSM message creation
                    gatekeeper_res = dut_handler.run('tests/fsm/fsm_test_gatekeeper_verdict', fsm_test_gatekeeper_verdict_args, do_gatekeeper_log=True, disable_fut_exception=True) == ExpectedShellResult
                    results[verdict] = {
                        'curl_res': curl_res,
                        'gatekeeper_res': gatekeeper_res,
                    }
        with step('Testcase - validation'):
            for verdict in ['allow', 'block', 'redirect']:
                with step(f'Testcase - validation - {verdict}'):
                    if not results[verdict]['gatekeeper_res']:
                        raise FailedException(
                            f'Failed to find FSM gatekeeper verdict message in logs. '
                            f'See step "Testcase - verdict - {verdict}"')
                    # 9. Check success of Curl for request
                    if verdict == 'block':
                        if results[verdict]['curl_res']:
                            raise FailedException('In case of blocked verdict. Curl request should fail, not pass.')
                        else:
                            if not results[verdict]['curl_res']:
                                raise FailedException('Failed to do curl request.')
                            assert results[verdict]['curl_res']
    finally:
        # FSM Cleanup
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_dpi_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_ndp_plugin_inputs = fsm_config.get('fsm_configure_test_ndp_plugin', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_ndp_plugin_inputs)
def test_fsm_configure_test_ndp_plugin(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        plugin = test_config.get("plugin")
        device_mode = test_config.get('device_mode')

        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        configure_remove_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_ndp_pl_net"
        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()
        client_internet_ip = '-internet_ip false'
        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_topic = "fsm_configure_test_ndp_plugin"
        location_id = "1000"
        node_id = "100"

        with step('Check FSM plugins existence'):
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_plugin_path)) == ExpectedShellResult

        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
            client_internet_ip,
        ]
        if "client_retry" in test_config:
            client_connect_args_base += [
                f"-retry {test_config.get('client_retry')}",
            ]
        if "client_connection_timeout" in test_config:
            client_connect_args_base += [
                f"-connect_timeout {test_config.get('client_connection_timeout')}",
            ]
        client_connect_args = get_command_arguments(*client_connect_args_base)

        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        fsm_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            "ndp",
        )

        # Testcase specific args
        fsm_pl_cfg_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.tndp',
        )

    try:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Create tap interfaces'):
            # Create and configure tap interfaces
            assert dut_handler.run('tools/device/configure_tap_interfaces', configure_remove_tap_interface_args) == ExpectedShellResult
        with step('MQTT connection establishment and message collection'):
            assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/fut_configure_mqtt', fsm_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
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
            )
        with step('Client connection'):
            # Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        with step('Retrieve Client MAC'):
            # Retrieve the expected Client MAC to be used at actual testcase script
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')
            fsm_pl_cfg_args = get_command_arguments(
                dut_if_lan_br_name,
                fsm_plugin_path,
                mqtt_topic,
                client_mac_addr_res[1],
            )
        with step('Testcase - Configure and test NDP plugin'):
            assert dut_handler.run('tests/fsm/fsm_configure_test_ndp_plugin', fsm_pl_cfg_args, do_mqtt_log=True) == ExpectedShellResult
    finally:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode was required
            with step('Put device into ROUTER mode'):
                assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_upnp_plugin_inputs = fsm_config.get('fsm_configure_test_upnp_plugin', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut", "fsm_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_upnp_plugin_inputs)
def test_fsm_configure_test_upnp_plugin(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        configure_remove_tap_interface_args = get_command_arguments(
            dut_if_lan_br_name,
        )
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        device_mode = test_config.get('device_mode')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        plugin = test_config.get("plugin")

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_fsm_upnp_pl_net"
        # Derived parameters
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()
        client_internet_ip = '-internet_ip false'
        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_topic = "fsm_configure_test_upnp_plugin"
        location_id = "1000"
        node_id = "100"

        with step('Check FSM plugins existence'):
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_plugin_path)) == ExpectedShellResult

        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
            client_internet_ip,
        ]
        if "client_retry" in test_config:
            client_connect_args_base += [
                f"-retry {test_config.get('client_retry')}",
            ]
        if "client_connection_timeout" in test_config:
            client_connect_args_base += [
                f"-connect_timeout {test_config.get('client_connection_timeout')}",
            ]
        client_connect_args = get_command_arguments(*client_connect_args_base)

        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        fsm_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            "upnp",
        )

        fsm_upnp_cfg_args = get_command_arguments(
            f"--deviceType='{test_config.get('upnp_device_type')}'",
            f"--friendlyName='{test_config.get('upnp_friendly_name')}'",
            f"--manufacturer='{test_config.get('upnp_manufacturer')}'",
            f"--manufacturerURL='{test_config.get('upnp_manufacturer_URL')}'",
            f"--modelDescription='{test_config.get('upnp_model_description')}'",
            f"--modelName='{test_config.get('upnp_model_name')}'",
            f"--modelNumber='{test_config.get('upnp_model_number')}'",
        )

        # Testcase specific args
        upnp_stop_server_cmd = f'sudo {client_handler.device_config.get("namespace_enter_cmd")} -c "kill $(netstat -nlp | grep 5000 | awk \'{{ print $7 }}\' | cut -d/ -f1)"'
        upnp_start_server_cmd = f'sudo {client_handler.device_config.get("namespace_enter_cmd")} -c "sleep 2 && timeout 20 /home/plume/upnp/upnp_server.py {fsm_upnp_cfg_args}" &>/dev/null &'
        # Cleanup args
        fsm_cleanup_args = get_command_arguments(
            f'{vif_name}',
            f'{dut_if_lan_br_name}',
            f'{dut_if_lan_br_name}.tupnp',
        )

    try:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode is required
            with step(f'Put device into {str(device_mode).upper()} mode'):
                assert configure_device_mode(device_name='dut', device_mode='bridge')
        with step('Create tap interfaces'):
            # Create and configure tap interfaces
            assert dut_handler.run('tools/device/configure_tap_interfaces', configure_remove_tap_interface_args) == ExpectedShellResult
        with step('MQTT configuration'):
            # Configure MQTT on RPI Server and connect DUT
            assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/fut_configure_mqtt', fsm_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
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
            )
        with step('Client connection'):
            # Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
        with step('Retrieve Client MAC'):
            # Retrieve the expected Client MAC to be used at actual testcase script
            client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')
            fsm_pl_cfg_args = get_command_arguments(
                dut_if_lan_br_name,
                fsm_plugin_path,
                mqtt_topic,
                client_mac_addr_res[1],
            )
        with step('UPnP plugin configuration'):
            # Configure UPnP FSM plugin
            assert dut_handler.run('tools/device/configure_upnp_plugin', fsm_pl_cfg_args, do_mqtt_log=True) == ExpectedShellResult
        with step('Testcase -Trigger UPnP on client and listen for MQTT'):
            def _trigger():
                # Stop any existing UPnP server which may be running on the Client wlan namespace
                log.info('Stopping any existing UPnP Server on port 5000 on client wlan namespace')
                log.info(upnp_stop_server_cmd)
                client_handler.execute(upnp_stop_server_cmd, print_out=True)
                # Bring up UPnP Server on Client
                log.info('Bringing up UPnP Server on Client')
                log.info(upnp_start_server_cmd)
                assert client_handler.execute(upnp_start_server_cmd, print_out=True) == ExpectedShellResult
            assert fut_mqtt_trigger_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={
                    'nodeId': node_id,
                    'locationId': location_id,
                    'deviceMac': client_mac_addr_res[1].upper(),
                    'deviceType': test_config.get('upnp_device_type'),
                    'friendlyName': test_config.get('upnp_friendly_name'),
                    'manufacturer': test_config.get('upnp_manufacturer'),
                    'manufacturerURL': test_config.get('upnp_manufacturer_URL'),
                    'modelDescription': test_config.get('upnp_model_description'),
                    'modelName': test_config.get('upnp_model_name'),
                    'modelNumber': test_config.get('upnp_model_number'),
                },
            )
    finally:
        if device_mode == 'bridge':
            # Execute this step only if BRIDGE mode was required
            with step('Put device into ROUTER mode'):
                assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Cleanup'):
            dut_handler.run('tools/device/remove_tap_interfaces', configure_remove_tap_interface_args)
            dut_handler.run('tests/fsm/fsm_cleanup', fsm_cleanup_args)


########################################################################################################################
test_fsm_configure_test_walleye_plugin_inputs = fsm_config.get('fsm_configure_test_walleye_plugin', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_configure_test_walleye_plugin_inputs)
def test_fsm_configure_test_walleye_plugin(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        plugin = test_config.get("plugin")
        # Constant arguments
        location_id = "1000"
        node_id = "100"
        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        # RPI Server arguments
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port')

        with step('Check FSM plugins existence'):
            # Check if FSM Plugin lib is implemented, if not exit code 3 (test will be skipped)
            opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
            fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
            assert dut_handler.run('tools/device/check_lib_plugin_exists', get_command_arguments(fsm_plugin_path)) == ExpectedShellResult

        fsm_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            "dpi_walleye",
        )
        # Testcase specific args
        fsm_pl_cfg_args = get_command_arguments(
            dut_if_lan_br_name,
            fsm_plugin_path,
        )

        with step('MQTT configuration'):
            # 1. Configure MQTT on RPI Server and connect DUT
            assert server_handler.run('tools/server/start_mqtt', '--start', do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/fut_configure_mqtt', fsm_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
        with step('Testcase'):
            # 2. Configure and test Walleye FSM plugin
            assert dut_handler.run('tests/fsm/fsm_configure_test_walleye_plugin', fsm_pl_cfg_args, do_mqtt_log=True) == ExpectedShellResult


########################################################################################################################
test_fsm_create_tap_interface_inputs = fsm_config.get('fsm_create_tap_interface', [])


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["fsm_fut_setup_dut"], scope='session')
@pytest.mark.parametrize('test_config', test_fsm_create_tap_interface_inputs)
def test_fsm_create_tap_interface(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Arguments from device capabilities
        lan_bridge_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        # Test arguments from testcase config
        tap_name_postfix = test_config.get("tap_name_postfix")
        of_port = test_config.get('of_port')
        test_args = get_command_arguments(
            lan_bridge_if_name,
            tap_name_postfix,
            of_port,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/fsm/fsm_create_tap_interface', test_args) == ExpectedShellResult
