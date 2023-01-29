from random import randrange

import allure
import pytest

from framework.tools.configure_ap_interface import configure_ap_interface
from framework.tools.functions import FailedException, get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
nm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='NM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="nm2_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_nm2_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='nm2')
    server_handler.recipe.clear_full()
    with step('NM2 setup'):
        assert dut_handler.run('tests/nm2/nm2_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.mark_setup()


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="nm2_fut_setup_client", depends=["compat_client_ready", "nm2_fut_setup_dut"], scope='session')
def test_nm2_fut_setup_client():
    server_handler, client_handler = pytest.server_handler, pytest.client_handler
    with step('Transfer'):
        assert client_handler.clear_tests_folder()
        assert client_handler.transfer(manager='nm2')
    server_handler.recipe.add_setup()
    # Add Client setup command here
    server_handler.recipe.add_setup()


########################################################################################################################
test_nm2_configure_nonexistent_iface_inputs = nm_config.get('nm2_configure_nonexistent_iface', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_configure_nonexistent_iface_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_configure_nonexistent_iface(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('inet_addr'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_configure_nonexistent_iface', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_configure_verify_native_tap_interface_inputs = nm_config.get('nm2_configure_verify_native_tap_interface', [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_configure_verify_native_tap_interface_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_configure_verify_native_tap_interface(test_config):
    dut_handler = pytest.dut_handler

    with step('Check bridge type'):
        if not dut_handler.bridge_type == 'native_bridge':
            pytest.skip('This test is applicable only when the device is configured with Native Linux Bridge, skipping the test')

    test_args = get_command_arguments(
        test_config['interface'],
        test_config['if_type'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_configure_verify_native_tap_interface', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_enable_disable_iface_network_inputs = nm_config.get('nm2_enable_disable_iface_network', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_enable_disable_iface_network_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_enable_disable_iface_network(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_enable_disable_iface_network', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_ovsdb_configure_interface_dhcpd_inputs = nm_config.get('nm2_ovsdb_configure_interface_dhcpd', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_ovsdb_configure_interface_dhcpd_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_ovsdb_configure_interface_dhcpd(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        if_name = test_config.get('if_name')
        if_type = test_config.get('if_type')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        test_args = get_command_arguments(
            if_name,
            if_type,
            test_config.get('start_pool'),
            test_config.get('end_pool'),
        )

    if if_type == 'vif':
        # Additional test arguments for if_type == vif and validation
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        interface_type = 'home_ap'
        vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')

        with step('Determine physical radio name'):
            phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
            assert phy_radio_name is not None

        # Constant arguments
        enabled = "true"
        mode = "ap"
        psk = "FutTestPSK"
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Keep the same order of parameters
        create_radio_vif_args_base = [
            f"-if_name {phy_radio_name}",
            f"-channel {channel}",
            f"-enabled {enabled}",
            f"-ht_mode {ht_mode}",
            f"-mode {mode}",
            f"-ssid {ssid}",
            f"-vif_if_name {if_name}",
            f"-vif_radio_idx {vif_radio_idx}",
            f"-wifi_security_type {wifi_security_type}",
        ]

        create_radio_vif_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
        create_radio_vif_args = get_command_arguments(*create_radio_vif_args_base)
        # Test preparation for if_type == vif, interface is created at runtime
        with step('Radio VIF creation'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
            assert dut_handler.run('tools/device/create_radio_vif_interface', create_radio_vif_args) == ExpectedShellResult

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_ovsdb_configure_interface_dhcpd', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_ovsdb_ip_port_forward_inputs = nm_config.get('nm2_ovsdb_ip_port_forward', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_ovsdb_ip_port_forward_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_ovsdb_ip_port_forward(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        src_ifname = test_config.get('src_ifname')

        # Check if src_ifname is equal to interface_name_wan_bridge
        if src_ifname == dut_handler.capabilities.get_or_raise('interfaces.wan_bridge'):
            with step('Check device if WANO enabled'):
                # Check if WANO is enabled, if yes, interface_name_wan_bridge does not exist, test should be skipped
                check_kconfig_wano_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
                check_kconfig_wano_ec = dut_handler.run('tools/device/check_kconfig_option', check_kconfig_wano_args)
                if check_kconfig_wano_ec == 0:
                    pytest.skip(f'If WANO is enabled, there should be no WAN bridge {src_ifname}')

        test_args = get_command_arguments(
            src_ifname,
            test_config.get('src_port'),
            test_config.get('dst_ipaddr'),
            test_config.get('dst_port'),
            test_config.get('protocol'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_ovsdb_ip_port_forward', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_ovsdb_remove_reinsert_iface_inputs = nm_config.get('nm2_ovsdb_remove_reinsert_iface', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_ovsdb_remove_reinsert_iface_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_ovsdb_remove_reinsert_iface(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_ovsdb_remove_reinsert_iface', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_broadcast_inputs = nm_config.get('nm2_set_broadcast', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_broadcast_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_broadcast(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('broadcast'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_broadcast', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_dns_inputs = nm_config.get('nm2_set_dns', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_dns_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_dns(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('primary_dns'),
            test_config.get('secondary_dns'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_dns', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_gateway_inputs = nm_config.get('nm2_set_gateway', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_gateway_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_gateway(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        if_name = test_config.get('if_name')
        if_type = test_config.get('if_type')
        gateway = test_config.get('gateway')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")

        test_args = get_command_arguments(
            if_name,
            if_type,
            gateway,
        )

        if if_type == 'vif':
            # Additional test arguments for if_type == vif and validation
            channel = test_config.get('channel')
            ht_mode = test_config.get('ht_mode')
            radio_band = test_config.get('radio_band')
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

            interface_type = 'home_ap'
            vif_radio_idx = dut_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}')

            with step('Determine physical radio name'):
                phy_radio_name = dut_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
                assert phy_radio_name is not None

            # Constant arguments
            enabled = "true"
            mode = "ap"
            psk = "FutTestPSK"
            ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
            # Keep the same order of parameters
            create_radio_vif_args_base = [
                f"-if_name {phy_radio_name}",
                f"-channel {channel}",
                f"-enabled {enabled}",
                f"-ht_mode {ht_mode}",
                f"-mode {mode}",
                f"-ssid {ssid}",
                f"-vif_if_name {if_name}",
                f"-vif_radio_idx {vif_radio_idx}",
                f"-wifi_security_type {wifi_security_type}",
            ]
            create_radio_vif_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, psk)
            create_radio_vif_args = get_command_arguments(*create_radio_vif_args_base)
            # Test preparation for if_type == vif, interface is created at runtime
            with step('Radio VIF creation'):
                assert dut_handler.run('tools/device/create_radio_vif_interface', create_radio_vif_args) == ExpectedShellResult

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_gateway', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_inet_addr_inputs = nm_config.get('nm2_set_inet_addr', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_inet_addr_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_inet_addr(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('inet_addr'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_inet_addr', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_ip_assign_scheme_inputs = nm_config.get('nm2_set_ip_assign_scheme', [])


# Create individual scenarios from grouped lists of parameters when channels are defined
# Provide channels and ht_modes as list of parameters, even if there is only one
# channel or ht_mode in configuration.
test_nm2_set_ip_assign_scheme_scenarios_channels = [
    {
        "channel": a,
        "ht_mode": b,
        "radio_band": g["radio_band"],
        "if_name": g["if_name"],
        "if_type": g["if_type"],
        "ip_assign_scheme": g["ip_assign_scheme"],
    }
    for g in list(filter(lambda channels: "channels" in channels, test_nm2_set_ip_assign_scheme_inputs))
    for a in g["channels"]
    for b in g["ht_modes"]
]

# Create testcase scenarios when no channels are defined
test_nm2_set_ip_assign_scheme_scenarios_no_channel = list(filter(lambda channels: "channels" not in channels, test_nm2_set_ip_assign_scheme_inputs))

# Combine the two lists of different testcase scenarios
test_nm2_set_ip_assign_scheme_scenarios = [
    *test_nm2_set_ip_assign_scheme_scenarios_channels,
    *test_nm2_set_ip_assign_scheme_scenarios_no_channel,
]


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_ip_assign_scheme_scenarios)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_ip_assign_scheme(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # DUT is synonymous to GW
        # Test arguments from testcase config
        gw_radio_band = test_config.get('radio_band')
        gw_channel = test_config.get('channel')
        gw_ht_mode = test_config.get('ht_mode')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        if gw_radio_band is not None and gw_channel is not None and gw_ht_mode is not None:
            assert dut_handler.validate_channel_ht_mode_band(gw_channel, gw_ht_mode, gw_radio_band)

        # Pre-defined GW bhaul Radio/VIF values
        gw_bhaul_interface_type = 'backhaul_ap'

        # GW device arguments from device capabilities
        gw_lan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
        gw_eth_wan_name = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
        gw_wan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')
        patch_h2w = dut_handler.capabilities.get_or_raise('interfaces.patch_port_lan_to_wan')
        patch_w2h = dut_handler.capabilities.get_or_raise('interfaces.patch_port_wan_to_lan')

        gw_vif_radio_idxs = dut_handler.capabilities.get_or_raise("interfaces.vif_radio_idx")
        gw_uplink_gre_mtu = dut_handler.capabilities.get_or_raise('mtu.uplink_gre')

        if gw_bhaul_interface_type not in gw_vif_radio_idxs:
            raise FailedException(f'Invalid DUT device configuration - {gw_bhaul_interface_type} does not have vif_radio_idx')
        gw_bhaul_ap_if_name = dut_handler.capabilities.get(f'interfaces.{gw_bhaul_interface_type}.{gw_radio_band}')

        psk = "FutTestPSK"
        gw_ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # DEVICE SETUP
        # 0. Determine all shell input parameters
        dut_in_bridge_mode = dut_handler.run('tools/device/check_device_in_bridge_mode',
                                             get_command_arguments(gw_eth_wan_name,
                                                                   gw_lan_br_if_name,
                                                                   gw_wan_br_if_name,
                                                                   patch_w2h,
                                                                   patch_h2w,
                                                                   )) == ExpectedShellResult

        wan_handling_args = get_command_arguments("CONFIG_MANAGER_WANO", "y")
        # Script returns 0 if wan_handling_args match the kconfig!
        has_wano = dut_handler.run('tools/device/check_kconfig_option', wan_handling_args) == ExpectedShellResult

    with step('Assemble testcase parameters'):
        gw_lan_br_inet_args_base = [
            f"-if_name {gw_lan_br_if_name}",
            "-if_type bridge",
            "-enabled true",
            "-network true",
            "-NAT false",
        ]

        if not dut_in_bridge_mode:
            gw_lan_br_inet_args_base += [
                "-ip_assign_scheme static",
                "-inet_addr 192.168.0.1",
                "-netmask 255.255.255.0",
                "-dhcpd '[\"map\",[[\"start\",\"192.168.0.10\"],[\"stop\",\"192.168.0.200\"]]]'",
            ]
        elif dut_in_bridge_mode:
            ip_assign_scheme = "none" if has_wano else "dhcp"
            gw_lan_br_inet_args_base.append(f"-ip_assign_scheme {ip_assign_scheme}")
        else:
            raise FailedException('Invalid device state. Check output.')

        gw_lan_br_inet_args = get_command_arguments(*gw_lan_br_inet_args_base)

        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('ip_assign_scheme'),
            gw_eth_wan_name,
            gw_lan_br_if_name,
            gw_bhaul_ap_if_name,
            gw_uplink_gre_mtu,
            gw_uplink_gre_mtu,
        )

    try:
        if_type = test_config.get('if_type')

        if if_type == 'bridge' or if_type == 'gre':
            # 1. On DUT - Ensure LAN is configured
            with step('LAN configuration'):
                assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
                assert dut_handler.run('tools/device/create_inet_interface', gw_lan_br_inet_args) == ExpectedShellResult

        if if_type == 'gre':
            with step('GW bhaul AP configuration'):
                # 2. On DUT - Create and configure GW bhaul AP interface
                assert configure_ap_interface(
                    channel=gw_channel,
                    ht_mode=gw_ht_mode,
                    radio_band=gw_radio_band,
                    psk=psk,
                    interface_type=gw_bhaul_interface_type,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    ssid=gw_ssid,
                    bridge=False,
                )
        with step('Testcase'):
            assert dut_handler.run('tests/nm2/nm2_set_ip_assign_scheme', test_args) == ExpectedShellResult
    finally:
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult


########################################################################################################################
test_nm2_set_mtu_inputs = nm_config.get('nm2_set_mtu', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_mtu_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_mtu(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('mtu'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_mtu', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_nat_inputs = nm_config.get('nm2_set_nat', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_nat_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_nat(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('NAT'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_nat', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_netmask_inputs = nm_config.get('nm2_set_netmask', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_set_netmask_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_set_netmask(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('if_name'),
            test_config.get('if_type'),
            test_config.get('netmask'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_set_netmask', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_set_upnp_mode_inputs = nm_config.get('nm2_set_upnp_mode', [])


@pytest.mark.require_dut()
@pytest.mark.require_client()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["nm2_fut_setup_dut", "nm2_fut_setup_client"], scope='session')
@pytest.mark.parametrize('test_config', test_nm2_set_upnp_mode_inputs)
def test_nm2_set_upnp_mode(test_config):
    server_handler, dut_handler, client_handler = pytest.server_handler, pytest.dut_handler, pytest.client_handler

    with step('Preparation'):
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

        psk = "FutTestPSK"
        tcp_port = 5201
        # Derived arguments
        ssid = f"fut_nm2_{randrange(1000, 10000)}"
        dut_lan_ip_addr = "10.10.10.30"
        eth_wan_ip_addr = server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip')
        client_network_namespace = client_handler.device_config.get_or_raise('network_namespace')
        client_wlan_if_name = client_handler.device_config.get_or_raise('wlan_if_name')
        client_wpa_supp_cfg_path = client_handler.device_config.get_or_raise('wpa_supp_cfg_path')
        client_ip_addr = "10.10.10.40"
        client_wpa_type = encryption.lower()

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

        client_connect_args_base = [
            client_wpa_type,
            client_network_namespace,
            client_wlan_if_name,
            client_wpa_supp_cfg_path,
            ssid,
            f'-psk {psk}',
            '-dhcp false',
            '-internet_ip false',
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

        check_chan_args = get_command_arguments(
            channel,
            phy_radio_name,
        )
        client_upnp_args = get_command_arguments(
            client_wlan_if_name,
            client_network_namespace,
            client_ip_addr,
            dut_lan_ip_addr,
            tcp_port,
        )
        router_mode_args = get_command_arguments(
            dut_wan_if_name,
            dut_if_lan_br_name,
        )
        upnp_mode_args = get_command_arguments(
            dut_wan_if_name,
            dut_if_lan_br_name,
            dut_lan_ip_addr,
        )
        check_traffic_args = get_command_arguments(
            eth_wan_ip_addr,
            tcp_port,
        )
        check_iptable_args = get_command_arguments(
            client_ip_addr,
            tcp_port,
        )
        client_cleanup_args = get_command_arguments(
            client_network_namespace,
            tcp_port,
        )

    with step('Verify router mode on DUT'):
        # 1. On DUT - Set router mode on DUT
        assert dut_handler.run('tests/nm2/nm2_verify_router_mode', router_mode_args) == ExpectedShellResult
    with step('Set UPnP mode on DUT'):
        # 2. On DUT - Turn ON UPnP mode on DUT
        assert dut_handler.run('tests/nm2/nm2_set_upnp_mode', upnp_mode_args) == ExpectedShellResult
    with step('Home AP creation'):
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
    with step('Check channel readiness'):
        # 4. On DUT - Check if channel is ready for use
        assert dut_handler.run('tools/device/check_channel_is_ready', check_chan_args) == ExpectedShellResult
    with step('Client connection'):
        # 5. Configure Client to connect to DUT home AP
        assert client_handler.run('tools/client/connect_to_wpa', client_connect_args, as_sudo=True) == ExpectedShellResult
    with step('Testcase'):
        # 6. Run miniupnp client on Client device
        assert client_handler.run('tools/client/run_upnp_client', client_upnp_args, as_sudo=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/validate_port_forward_entry_in_iptables', check_iptable_args) == ExpectedShellResult
        # 7. Checks the traffic to the client to validate if the port is forwarded
        assert server_handler.run('tools/server/check_traffic_to_client', check_traffic_args, as_sudo=True) == ExpectedShellResult
    with step('Cleanup'):
        # 8. Stop UPnP client running on the client host
        client_handler.run('tools/client/stop_upnp_client', client_cleanup_args, as_sudo=True)
        # 9. Clean the iptable rules on DUT.
        dut_handler.run('tools/device/clear_port_forward_in_iptables')


########################################################################################################################
test_nm2_verify_linux_traffic_control_rules_inputs = nm_config.get('nm2_verify_linux_traffic_control_rules', [])


@pytest.mark.parametrize('test_config', test_nm2_verify_linux_traffic_control_rules_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_verify_linux_traffic_control_rules(test_config):
    dut_handler = pytest.dut_handler

    with step('Check bridge type'):
        if not pytest.dut_handler.bridge_type == 'native_bridge':
            pytest.skip('Test is applicable only when device is configured with Linux Native Bridge, skipping the test.')

    lan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
    ingress_action_args = f"{test_config['ingress_action']} dev {lan_br_if_name}"
    egress_action_args = f"{test_config['egress_action']} dev {lan_br_if_name}"

    test_args = get_command_arguments(
        test_config['if_name'],
        test_config['ingress_match'],
        ingress_action_args,
        test_config['ingress_expected_str'],
        test_config['egress_match'],
        egress_action_args,
        test_config['egress_expected_str'],
        test_config['priority'],
        test_config['ingress_updated_match'],
        test_config['ingress_expected_str_after_update'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_verify_linux_traffic_control_rules', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_verify_linux_traffic_control_template_rules = nm_config.get('nm2_verify_linux_traffic_control_template_rules', [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_verify_linux_traffic_control_template_rules)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_verify_linux_traffic_control_template_rules(test_config):
    dut_handler = pytest.dut_handler

    with step('Check bridge type'):
        if not pytest.dut_handler.bridge_type == 'native_bridge':
            pytest.skip('Test is applicable only when device is configured with Linux Native Bridge, skipping the test.')

    lan_br_if_name = dut_handler.capabilities.get_or_raise('interfaces.lan_bridge')
    ingress_action_args = f"{test_config['ingress_action']} dev {lan_br_if_name}"
    egress_action_args = f"{test_config['egress_action']} dev {lan_br_if_name}"

    test_args = get_command_arguments(
        test_config['if_name'],
        test_config['ingress_match'],
        ingress_action_args,
        test_config['ingress_tag_name'],
        test_config['egress_match'],
        egress_action_args,
        test_config['egress_match_with_tag'],
        test_config['egress_expected_str'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_verify_linux_traffic_control_template_rules', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_verify_native_bridge_inputs = nm_config.get('nm2_verify_native_bridge', [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_verify_native_bridge_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_verify_native_bridge(test_config):
    dut_handler = pytest.dut_handler

    with step('Check bridge type'):
        if not dut_handler.bridge_type == 'native_bridge':
            pytest.skip('This test is applicable only when the device is configured with Native Linux Bridge, skipping the test')

    test_args = get_command_arguments(
        test_config['bridge'],
        test_config['interface'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_verify_native_bridge', test_args) == ExpectedShellResult


########################################################################################################################
test_nm2_vlan_interface_inputs = nm_config.get('nm2_vlan_interface', [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nm2_vlan_interface_inputs)
@pytest.mark.dependency(depends=["nm2_fut_setup_dut"], scope='session')
def test_nm2_vlan_interface(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('parent_ifname'),
            test_config.get('vlan_id'),
        )

    with step('Testcase'):
        assert dut_handler.run('tests/nm2/nm2_vlan_interface', test_args) == ExpectedShellResult
