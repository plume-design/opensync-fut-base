from random import randrange
from time import sleep

import allure
import pytest

import framework.tools.logger
from framework.tools.configure_ap_interface import configure_ap_interface
from framework.tools.create_gre_bhaul import create_and_configure_bhaul_connection_gw_leaf
from framework.tools.functions import FailedException, get_command_arguments, step
from framework.tools.set_device_mode import configure_device_mode
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

# Read entire testcase configuration
othr_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='OTHR')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="othr_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_othr_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='dm')
    server_handler.recipe.clear_full()
    with step('OTHR setup'):
        assert dut_handler.run('tests/dm/othr_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    with step('Put device into ROUTER mode'):
        assert configure_device_mode(device_name='dut', device_mode='router')
    server_handler.recipe.mark_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="othr_fut_setup_ref", depends=["compat_ref_ready", "othr_fut_setup_dut"], scope='session')
def test_othr_fut_setup_ref():
    server_handler, ref_handler = pytest.server_handler, pytest.ref_handler
    with step('Transfer'):
        assert ref_handler.clear_tests_folder()
        assert ref_handler.transfer(manager='dm')
    server_handler.recipe.clear()
    with step('OTHR setup'):
        assert ref_handler.run('tests/dm/othr_setup', ref_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.add_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="othr_fut_setup_client", depends=["compat_client_ready", "othr_fut_setup_dut"], scope='session')
def test_othr_fut_setup_client():
    server_handler, client_handler = pytest.server_handler, pytest.client_handler
    with step('Transfer'):
        assert client_handler.clear_tests_folder()
        assert client_handler.transfer(manager='dm')
    server_handler.recipe.clear()
    # Add Client setup command here
    server_handler.recipe.add_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client2_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="othr_fut_setup_client2", depends=["compat_client2_ready", "othr_fut_setup_dut"], scope='session')
def test_othr_fut_setup_client2():
    server_handler, client2_handler = pytest.server_handler, pytest.client2_handler
    with step('Transfer'):
        assert client2_handler.clear_tests_folder()
        assert client2_handler.transfer(manager='dm')
    server_handler.recipe.clear()
    # Add Client setup command here
    server_handler.recipe.add_setup()


########################################################################################################################
test_othr_add_client_freeze_inputs = othr_config.get("othr_add_client_freeze", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_othr_add_client_freeze_inputs)
def test_othr_add_client_freeze(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler
    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")

        assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        psk = 'FutTestPSK'
        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Device capabilities arguments
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()

        # Testcase specific arguments
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

        client_internet_block_args = get_command_arguments(
            client_network_namespace,
            "block",
        )
        client_internet_unblock_args = get_command_arguments(
            client_network_namespace,
            "unblock",
        )
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        # Retrieve the expected Client MAC to be used at actual testcase script
        client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
        if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
            pytest.skip('Failed to retrieve Client MAC address')
        dut_client_freeze_args = get_command_arguments(
            client_mac_addr_res[1],
            dut_if_lan_br_name,
        )
        dut_client_assoc_args = get_command_arguments(
            client_mac_addr_res[1],
        )

    try:
        with step('Ensure WAN connectivity'):
            # 1. Ensure WAN connectivity
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        with step(f'Put device into {device_mode.upper()} mode'):
            # 2. Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Bring up Home AP interface'):
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
            # 5. Verify Client MAC is added to Wifi_Associated_Clients table
            assert dut_handler.run('tools/device/check_wifi_client_associated', dut_client_assoc_args) == ExpectedShellResult
        with step('Testcase'):
            # 6. Add Client freeze rules into Openflow tables
            assert dut_handler.run('tests/dm/othr_connect_wifi_client_to_ap_freeze', dut_client_freeze_args) == ExpectedShellResult
            # 7. Verify if internet is blocked for the Client after adding rules into Openflow tables
            assert client_handler.run('tools/client/check_internet_traffic', client_internet_block_args, as_sudo=True) == ExpectedShellResult
            # 8. Remove Client freeze rules from Openflow tables
            assert dut_handler.run('tests/dm/othr_connect_wifi_client_to_ap_unfreeze') == ExpectedShellResult
            log.info('Sleeping for 10 seconds')
            sleep(10)
            # 9. Verify if internet is blocked for the Client after removing rules from Openflow tables
            assert client_handler.run('tools/client/check_internet_traffic', client_internet_unblock_args, as_sudo=True) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            dut_handler.run('tests/dm/othr_connect_wifi_client_to_ap_unfreeze')
            client_handler.run('tools/client/reboot_client', as_sudo=True)
            dut_handler.run('tests/dm/othr_setup', dut_handler.get_if_names(True))
            configure_device_mode(device_name='dut', device_mode='router')


########################################################################################################################
test_othr_connect_wifi_client_multi_psk_inputs = othr_config.get('othr_connect_wifi_client_multi_psk', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_othr_connect_wifi_client_multi_psk_inputs)
def test_othr_connect_wifi_client_multi_psk(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")
        encryption = test_config.get("encryption", "WPA2")
        assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk_a = test_config.get("psk_a")
        psk_b = test_config.get("psk_b")
        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Device params
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()
        client_internet_ip = '-internet_ip false'

        # Testcase specific args
        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
        ]
        client_connect_args_a = get_command_arguments(
            *client_connect_args_base,
            f'-psk {psk_a}',
            client_internet_ip,
        )
        client_connect_args_b = get_command_arguments(
            *client_connect_args_base,
            f'-psk {psk_b}',
            client_internet_ip,
        )
        # Cleanup args
        othr_cleanup_args = get_command_arguments(
            dut_if_lan_br_name,
            vif_name,
        )
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        # Retrieve the expected Client MAC to be used at actual testcase script
        client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
        if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
            pytest.skip('Failed to retrieve Client MAC address')
        dut_client_assoc_args = get_command_arguments(
            client_mac_addr_res[1],
        )

    try:
        with step(f'Put device into {device_mode.upper()} mode'):
            # Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Bring up Home AP interface'):
            # Create and configure home AP interface
            assert configure_ap_interface(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                psk=[psk_a, psk_b],
                wifi_security_type=wifi_security_type,
                encryption=encryption,
                ssid=ssid,
            )
        with step('Testcase'):
            with step('Client connection #1 PSK'):
                # Configure Client to connect to DUT home AP, use 1st PSK
                assert client_handler.run('tools/client/connect_to_wpa', client_connect_args_a, as_sudo=True) == ExpectedShellResult
                # Verify DUT has associated Client
                assert dut_handler.run('tools/device/check_wifi_client_associated', dut_client_assoc_args) == ExpectedShellResult
            with step('Client connection #2 PSK'):
                # Configure Client to connect to DUT home AP, use 2nd PSK
                assert client_handler.run('tools/client/connect_to_wpa', client_connect_args_b, as_sudo=True) == ExpectedShellResult
                # Verify DUT has associated Client
                assert dut_handler.run('tools/device/check_wifi_client_associated', dut_client_assoc_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            dut_handler.run('tests/dm/othr_cleanup', othr_cleanup_args, disable_fut_exception=True)
            if device_mode != 'router':
                configure_device_mode(device_name='dut', device_mode='router')


########################################################################################################################
test_othr_connect_wifi_client_to_ap_inputs = othr_config.get('othr_connect_wifi_client_to_ap', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_othr_connect_wifi_client_to_ap_inputs)
def test_othr_connect_wifi_client_to_ap(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")

        assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_connect_to_ap"
        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Device params
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Client arguments
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()
        client_internet_ip = '-internet_ip false'

        # Testcase specific args
        client_connect_args = get_command_arguments(
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
            client_internet_ip,
        )
        # Cleanup args
        othr_cleanup_args = get_command_arguments(
            dut_if_lan_br_name,
            vif_name,
        )
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        # Retrieve the expected Client MAC to be used at actual testcase script
        client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
        if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
            pytest.skip('Failed to retrieve Client MAC address')
        dut_client_assoc_args = get_command_arguments(
            client_mac_addr_res[1],
        )

    try:
        with step(f'Put device into {device_mode.upper()} mode'):
            # Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Bring up Home AP interface'):
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
        with step('Testcase'):
            # Verify DUT has associated Client
            assert dut_handler.run('tools/device/check_wifi_client_associated', dut_client_assoc_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            dut_handler.run('tests/dm/othr_cleanup', othr_cleanup_args)
            if device_mode != 'router':
                configure_device_mode(device_name='dut', device_mode='router')


######################################################################################################################
test_othr_eth_client_connect_inputs = othr_config.get('othr_eth_client_connect', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client2()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_client2"], scope='session')
@pytest.mark.parametrize('test_config', test_othr_eth_client_connect_inputs)
def test_othr_eth_client_connect(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from device capabilities
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        eth_lan_interface = dut_handler.capabilities.get_or_raise("interfaces.primary_lan_interface")
        add_eth_port_to_bridge_args = get_command_arguments(
            dut_if_lan_br_name,
            eth_lan_interface,
        )
    try:
        with step('Client eth-connect'):
            cmd = 'client eclient2 eth-connect dut'
            # This step will fail since lan port is not added into br-home bridge
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
        with step('Add bridge port'):
            assert dut_handler.run('tools/device/add_bridge_port', add_eth_port_to_bridge_args) == ExpectedShellResult
        with step('Client start-dhclient'):
            # Re-run dhclient on client
            cmd = 'client eclient2 start-dhclient'
            assert server_handler.execute(cmd, print_out=True) == ExpectedShellResult
        with step('Retrieve Client MAC address'):
            # Retrieve the expected Client MAC to be used at actual testcase script
            get_client_mac_cmd = "client -j eclient2 get-mac | awk '{ print $5 }' | cut -d'\"' -f 2"
            client_mac_addr_res = server_handler.execute_raw(get_client_mac_cmd, print_out=True)
            if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
                pytest.skip('Failed to retrieve Client MAC address')
        verify_eth_client_connection_args = get_command_arguments(
            eth_lan_interface,
            client_mac_addr_res[1],
        )
        with step('Testcase - Validate client association to DUT'):
            # 5. Verify Client MAC is added to Wifi_Associated_Clients table
            assert dut_handler.run('tests/dm/othr_verify_eth_client_connection', verify_eth_client_connection_args) == ExpectedShellResult
        with step('Testcase - Validate client internet connection'):
            get_client_mac_cmd = "client eclient2 ping-check 8.8.8.8"
            assert server_handler.execute(get_client_mac_cmd, print_out=True) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            with step('Client eth-disconnect'):
                cmd = 'client eclient2 eth-disconnect dut'
                server_handler.execute(cmd, print_out=True, ignore_assertion=True)


########################################################################################################################
test_othr_verify_eth_lan_iface_wifi_master_state_inputs = othr_config.get('othr_verify_eth_lan_iface_wifi_master_state', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_eth_lan_iface_wifi_master_state_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_eth_lan_iface_wifi_master_state(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Argument from device capabilities
        eth_lan_interface = dut_handler.capabilities.get_or_raise("interfaces.primary_lan_interface")
        if not eth_lan_interface:
            pytest.skip('No ethernet LAN interface at this device')
        test_args = get_command_arguments(
            eth_lan_interface,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_eth_lan_iface_wifi_master_state', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_eth_wan_iface_wifi_master_state_inputs = othr_config.get('othr_verify_eth_wan_iface_wifi_master_state', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_eth_wan_iface_wifi_master_state_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_eth_wan_iface_wifi_master_state(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Argument from device capabilities
        eth_wan_interface = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
        if not eth_wan_interface:
            pytest.skip('No ethernet WAN interface at this device')
        test_args = get_command_arguments(
            eth_wan_interface,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_eth_wan_iface_wifi_master_state', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_ethernet_backhaul_inputs = othr_config.get('othr_verify_ethernet_backhaul', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_ethernet_backhaul_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_ref"], scope='session')
def test_othr_verify_ethernet_backhaul(test_config):
    dut_handler = pytest.dut_handler
    ref_handler = pytest.ref_handler
    server_handler = pytest.server_handler
    with step('Preparation'):
        # GW device capabilities
        gw_eth_lan_if_name = dut_handler.capabilities.get('interfaces.primary_lan_interface')
        gw_lan_br_if_name = dut_handler.capabilities.get('interfaces.lan_bridge')

        # LEAF WAN interface
        leaf_eth_wan_if_name = ref_handler.capabilities.get('interfaces.primary_wan_interface')
        add_eth_port_to_bridge_args = get_command_arguments(
            gw_lan_br_if_name,
            gw_eth_lan_if_name,
        )
        leaf_wan_iface = 'ref_' + leaf_eth_wan_if_name

    try:
        with step('VIF clean'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        with step('Ensure WAN connectivity'):
            # On DUT - Ensure WAN connectivity, ping Internet from the GW device.
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        with step('Put device into Router mode'):
            # Configure device into router mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Add LAN ethernet port into LAN bridge'):
            assert dut_handler.run('tools/device/add_bridge_port', add_eth_port_to_bridge_args) == ExpectedShellResult
        with step('Network Switch configuration'):
            # On Network Switch - Configure Network Switch for LEAF to use VLAN309 of GW device.
            log.info('Reconfigure network switch to connect REF WAN ethernet interface to DUT LAN ethernet interface')
            cmd = f'switch {leaf_wan_iface} vlan-set 309 untagged'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
            # On Network Switch - Disable port isolation.
            log.info('Disable port isolation')
            cmd = 'switch disable-isolation'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
            log.info('Checking if vlans are tagged')
            cmd = f'switch {leaf_wan_iface} info'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
        with step('Testcase: Backhaul verification'):
            # Check ping to internet from the LEAF device.
            assert ref_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
    finally:
        with step('Cleanup - reverting VLAN back to original'):
            cmd = 'switch enable-isolation'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
            # Configure Network Switch for LEAF to use original VLAN304.
            log.info('Reconfigure network switch for REF to original VLAN config')
            cmd = f'switch {leaf_wan_iface} vlan-set 304 untagged'
            server_handler.execute(cmd, print_out=True, ignore_assertion=True)
            configure_device_mode(device_name='dut', device_mode='router')


########################################################################################################################
test_othr_verify_gre_iface_wifi_master_state_inputs = othr_config.get('othr_verify_gre_iface_wifi_master_state', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_gre_iface_wifi_master_state_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_gre_iface_wifi_master_state(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # DUT is synonymous to GW
        # GW bhaul Radio/VIF constants
        gw_bhaul_interface_type = 'backhaul_ap'

        gw_bhaul_psk = "FutTestPSK"
        gw_bhaul_ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # GW device capabilities
        gw_eth_wan_if_name = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
        gw_wan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')
        gw_lan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        gw_patch_h2w = dut_handler.capabilities.get_or_raise('interfaces.patch_port_lan_to_wan')
        gw_patch_w2h = dut_handler.capabilities.get_or_raise('interfaces.patch_port_wan_to_lan')
        gw_uplink_gre_mtu = dut_handler.capabilities.get_or_raise('mtu.uplink_gre')
        gw_bhaul_ap_if_name = dut_handler.capabilities.get_or_raise(f'interfaces.{gw_bhaul_interface_type}.{radio_band}')
        gw_gre_if_name = f"gre-ifname-{randrange(100, 1000)}"

    # DEVICE SETUP
    # 0. Determine all shell input parameters
    with step("Determine GW network mode and WANO"):
        dut_in_bridge_mode_args = get_command_arguments(
            gw_eth_wan_if_name,
            gw_lan_br_if_name,
            gw_wan_br_if_name,
            gw_patch_h2w,
            gw_patch_w2h,
        )
        dut_in_bridge_mode = dut_handler.run('tools/device/check_device_in_bridge_mode', dut_in_bridge_mode_args) == ExpectedShellResult
        has_wano_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
        has_wano = dut_handler.run('tools/device/check_kconfig_option', has_wano_args) == ExpectedShellResult

    # Keep the same order of parameters!
    with step('Assemble testcase parameters'):
        gw_lan_br_inet_args_base = [
            f"-if_name {gw_lan_br_if_name}",
            "-if_type bridge",
            "-enabled true",
            "-network true",
            "-NAT false",
        ]
        if dut_in_bridge_mode:
            ip_assign_scheme = "none" if has_wano else "dhcp"
            gw_lan_br_inet_args_base.append(f"-ip_assign_scheme {ip_assign_scheme}")
        else:
            gw_lan_br_inet_args_base += [
                "-ip_assign_scheme static",
                "-inet_addr 192.168.0.1",
                "-netmask 255.255.255.0",
                "-dhcpd '[\"map\",[[\"start\",\"192.168.0.10\"],[\"stop\",\"192.168.0.200\"]]]'",
            ]
        gw_lan_br_inet_args = get_command_arguments(*gw_lan_br_inet_args_base)

        gw_gre_conf_verify_args = get_command_arguments(
            gw_bhaul_ap_if_name,
            gw_gre_if_name,
            gw_uplink_gre_mtu,
        )

    with step('LAN configuration'):
        assert dut_handler.run('tools/device/create_inet_interface', gw_lan_br_inet_args) == ExpectedShellResult
    with step('GW bhaul AP creation'):
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            psk=gw_bhaul_psk,
            interface_type=gw_bhaul_interface_type,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=gw_bhaul_ssid,
            bridge=False,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_gre_iface_wifi_master_state', gw_gre_conf_verify_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_gre_tunnel_dut_gw_inputs_dut = othr_config.get('othr_verify_gre_tunnel_dut_gw', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_gre_tunnel_dut_gw_inputs_dut)
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_ref"], scope='session')
def test_othr_verify_gre_tunnel_dut_gw(test_config):
    dut_handler, ref_handler = pytest.dut_handler, pytest.ref_handler

    with step('Preparation'):
        # DUT is synonymous to GW
        # REF is synonymous to LEAF
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        gw_radio_band = test_config.get("radio_band")
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")
        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)
        assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, gw_radio_band)
        assert ref_handler.validate_channel_ht_mode_band(channel, ht_mode, leaf_radio_band)

        # GW device capabilities
        gw_lan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')

        # LEAF device_capabilities
        leaf_phy_radio_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.phy_radio_name.{leaf_radio_band}')

    with step("Determine LEAF radio MAC remotely at runtime, to whitelist on GW"):
        leaf_mac_arg = get_command_arguments(f'if_name=={leaf_phy_radio_if_name}')
        leaf_mac_ec, leaf_radio_mac_raw, std_err = ref_handler.run_raw('tools/device/ovsdb/get_radio_mac_from_ovsdb', leaf_mac_arg)
        if leaf_radio_mac_raw is None or leaf_radio_mac_raw == '' or leaf_mac_ec != ExpectedShellResult:
            raise FailedException(f'Failed to retrieve MAC for REF {leaf_phy_radio_if_name}')

    with step('Assemble testcase parameters'):
        gw_gre_verify_args = get_command_arguments(
            leaf_radio_mac_raw,
        )
        gw_gre_clean_up_args = get_command_arguments(
            gw_lan_br_if_name,
        )

    try:
        with step('VIF clean'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        with step('Ensure WAN connectivity'):
            # On DUT - Ensure WAN connectivity
            assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
        with step(f'Put device into {device_mode.upper()} mode'):
            # 2. Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('GW AP and LEAF STA creation, configuration and GW GRE configuration'):
            # On DUT - Create and configure GW bhaul AP interface
            # On REF - Create and configure LEAF bhaul STA interfaces
            # On DUT - Configure GRE tunnel
            assert create_and_configure_bhaul_connection_gw_leaf(channel, gw_radio_band, leaf_radio_band, ht_mode, wifi_security_type, encryption)
        with step('Testcase: GW bhaul AP verification'):
            # On DUT - Verify GW bhaul GRE tunnel
            assert dut_handler.run('tests/dm/othr_verify_gre_tunnel_gw', gw_gre_verify_args) == ExpectedShellResult
        with step('Testcase: LEAF GRE tunnel verification'):
            # On REF - Verify LEAF GRE tunnel
            assert ref_handler.run('tests/dm/othr_verify_gre_tunnel_leaf') == ExpectedShellResult
    finally:
        with step('Cleanup'):
            dut_handler.run('tests/dm/othr_verify_gre_tunnel_gw_cleanup', gw_gre_clean_up_args, disable_fut_exception=True)
            dut_handler.run('tools/device/vif_reset', disable_fut_exception=True)
            ref_handler.run('tools/device/vif_reset', disable_fut_exception=True)
            if device_mode != 'router':
                configure_device_mode(device_name='dut', device_mode='router')


########################################################################################################################
test_othr_verify_iperf3_speedtest_inputs = othr_config.get('othr_verify_iperf3_speedtest', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_iperf3_speedtest_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_iperf3_speedtest(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        traffic_type = test_config.get('traffic_type')
        server_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        iperf_forward_traffic_args = get_command_arguments(
            server_hostname,
            traffic_type,
        )

    with step('Testcase'):
        assert server_handler.run('tools/server/run_iperf3_server', as_sudo=True) == ExpectedShellResult
        assert dut_handler.run('tests/dm/othr_verify_iperf3_speedtest', iperf_forward_traffic_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_lan_bridge_iface_wifi_master_state_inputs = othr_config.get('othr_verify_lan_bridge_iface_wifi_master_state', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_lan_bridge_iface_wifi_master_state_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_lan_bridge_iface_wifi_master_state(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Argument from device capabilities
        lan_bridge_interface = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        test_args = get_command_arguments(
            lan_bridge_interface,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_lan_bridge_iface_wifi_master_state', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_ookla_speedtest_inputs = othr_config.get('othr_verify_ookla_speedtest', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_ookla_speedtest_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_ookla_speedtest(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        testid = randrange(100, 1000)
        test_args = get_command_arguments(
            testid,
        )
    with step('Ensure WAN Connectivity'):
        assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_ookla_speedtest', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_ookla_speedtest_bind_options_inputs = othr_config.get('othr_verify_ookla_speedtest_bind_options', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_ookla_speedtest_bind_options_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_ookla_speedtest_bind_options(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        testid = randrange(100, 1000)
        test_args = get_command_arguments(
            testid,
        )
    with step('Ensure WAN Connectivity'):
        assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_ookla_speedtest_bind_options', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_ookla_speedtest_bind_reporting_inputs = othr_config.get('othr_verify_ookla_speedtest_bind_reporting', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_ookla_speedtest_bind_reporting_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_ookla_speedtest_bind_reporting(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        testid = randrange(100, 1000)
        test_args = get_command_arguments(
            testid,
        )
    with step('Ensure WAN Connectivity'):
        assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_ookla_speedtest_bind_reporting', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_ookla_speedtest_sdn_endpoint_config_inputs = othr_config.get('othr_verify_ookla_speedtest_sdn_endpoint_config', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_ookla_speedtest_sdn_endpoint_config_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_ookla_speedtest_sdn_endpoint_config(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        speedtest_config_path = test_config.get('speedtest_config_path')

        test_args = get_command_arguments(
            speedtest_config_path,
        )
    with step('Ensure WAN Connectivity'):
        assert dut_handler.run('tools/device/check_wan_connectivity') == ExpectedShellResult
    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_ookla_speedtest_sdn_endpoint_config', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_verify_samknows_process_inputs = othr_config.get('othr_verify_samknows_process', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m3()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_samknows_process_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_samknows_process(test_config):
    dut_handler = pytest.dut_handler

    try:
        with step('Testcase'):
            assert dut_handler.run('tests/dm/othr_verify_samknows_process') == ExpectedShellResult
    finally:
        with step('Cleanup'):
            dut_handler.run('tests/dm/othr_samknows_process_cleanup', disable_fut_exception=True)


########################################################################################################################
test_othr_verify_vif_iface_wifi_master_state_inputs = othr_config.get('othr_verify_vif_iface_wifi_master_state', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_vif_iface_wifi_master_state_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_vif_iface_wifi_master_state(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        interface_type = 'backhaul_sta'
        # Determine radio bands for the device
        radio_channels = dut_handler.capabilities.get_or_raise('interfaces.radio_channels')
        radio_bands = [band for band in radio_channels if dut_handler.capabilities.get(f'interfaces.{interface_type}.{band}', fallback=None) is not None]
        if radio_bands is None or not radio_bands:
            raise FailedException(f'Could not determine radio_bands for interface type:{interface_type}')

    with step('Testcase'):
        for band in radio_bands:
            assert dut_handler.run('tests/dm/othr_verify_vif_iface_wifi_master_state', dut_handler.capabilities.get(f'interfaces.{interface_type}.{band}')) == ExpectedShellResult


########################################################################################################################
test_othr_verify_wan_bridge_iface_wifi_master_state_inputs = othr_config.get('othr_verify_wan_bridge_iface_wifi_master_state', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_othr_verify_wan_bridge_iface_wifi_master_state_inputs)
@pytest.mark.dependency(depends=["othr_fut_setup_dut"], scope='session')
def test_othr_verify_wan_bridge_iface_wifi_master_state(test_config):
    dut_handler = pytest.dut_handler

    with step('Check device if WANO enabled'):
        # Check if WANO is enabled, if yes, interface_name_wan_bridge does not exist, test should be skipped
        has_wano_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
        check_kconfig_wano_ec = dut_handler.run('tools/device/check_kconfig_option', has_wano_args)
        if check_kconfig_wano_ec == 0:
            pytest.skip('If WANO is enabled, there should be no WAN bridge')

    with step('Preparation'):
        wan_bridge_interface = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')
        test_args = get_command_arguments(
            wan_bridge_interface,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/othr_verify_wan_bridge_iface_wifi_master_state', test_args) == ExpectedShellResult


########################################################################################################################
test_othr_wifi_disabled_after_removing_ap_inputs = othr_config.get('othr_wifi_disabled_after_removing_ap', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["othr_fut_setup_dut", "othr_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_othr_wifi_disabled_after_removing_ap_inputs)
def test_othr_wifi_disabled_after_removing_ap(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        ht_mode = test_config.get("ht_mode")
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")

        assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        # Constant arguments
        interface_type = 'home_ap'
        psk = "fut_connect_to_ap"
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Device params
        dut_if_lan_br_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        # Get physical radio name
        phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
        if phy_radio_name is None:
            raise FailedException(f'Could not determine phy_radio_name for radio_band:{radio_band}')

        vif_name = dut_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}')
        # Device params - Client
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_wpa_type = encryption.lower()
        client_internet_ip = '-internet_ip false'

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

        othr_cleanup_args = get_command_arguments(
            dut_if_lan_br_name,
            vif_name,
        )
        remove_home_ap_vif_radio_args = get_command_arguments(
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {vif_name}",
        )
        client_get_mac_args = get_command_arguments(
            client_network_namespace,
            client_wlan_if_name,
        )

        # Retrieve the expected Client MAC to be used at actual testcase script
        client_mac_addr_res = client_handler.run_raw('tools/client/get_client_mac', client_get_mac_args, as_sudo=True, print_out=True)
        if client_mac_addr_res[0] != ExpectedShellResult or not client_mac_addr_res[1] or client_mac_addr_res[1] == '':
            pytest.skip('Failed to retrieve Client MAC address')
        dut_client_assoc_args = get_command_arguments(
            client_mac_addr_res[1],
        )

    try:
        with step(f'Put device into {device_mode.upper()} mode'):
            # Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('Bring up Home AP interface'):
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
        with step('Control connection'):
            # Verify DUT has associated Client
            assert dut_handler.run('tools/device/check_wifi_client_associated', dut_client_assoc_args) == ExpectedShellResult
        with step('Home AP destruction'):
            # Remove home AP interface
            assert dut_handler.run('tools/device/remove_vif_interface', remove_home_ap_vif_radio_args) == ExpectedShellResult
        with step('Client connection'):
            # Configure Client to connect to DUT home AP
            assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) != ExpectedShellResult
        with step('Testcase'):
            # Verify DUT has no associated clients
            assert dut_handler.run('tests/dm/othr_verify_wifi_client_not_associated') == ExpectedShellResult
    finally:
        with step('Cleanup'):
            client_handler.run('tools/client/reboot_client', as_sudo=True)
            dut_handler.run('tests/dm/othr_cleanup', othr_cleanup_args)
            if device_mode != 'router':
                configure_device_mode(device_name='dut', device_mode='router')
