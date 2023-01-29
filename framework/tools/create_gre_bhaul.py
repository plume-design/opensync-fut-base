"""Module used to configure GRE backhauld connection between the DUT and REF.

DUT device has a role of gateway and REF device has a role of leaf device.
Its purpose is to ease the backhaul configuration by providing a
one-step configuration by calling the 'create_and_configure_bhaul_connection_gw_leaf'
function, which would determine all the required arguments from the e.g. device
capabilities file for DUT and as well for REF device, and call required scripts
to establish the connection.
"""
from random import randrange

import pytest

import framework.tools.logger
from framework.tools.functions import FailedException, get_command_arguments
from test.globals import ExpectedShellResult

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


def create_and_configure_bhaul_connection_gw_leaf(
        channel,
        gw_radio_band,
        leaf_radio_band,
        ht_mode,
        wifi_security_type,
        encryption,
        gw_device='dut',
        leaf_device='ref',
        skip_gre=False,
):
    """Create and configure backhaul connection between the DUT and REF.

    Args:
        channel (int): Radio channel
        gw_radio_band (str): Gateway radio band
        leaf_radio_band (str): Leaf radio band
        ht_mode (str): HT mode
        encryption (str): Encryption type
        wifi_security_type (str): Type of security - (legacy, wpa)
        gw_device (str): Name of GW device (dut, ref, ref2)
        leaf_device (str): Name of LEAF device (dut, ref, ref2)
        skip_gre (bool) : Skips configuration of GRE interface on GW device for LEAF connection
    Raises:
        FailedException: REF MAC cannot be retrieved.
        Exception: Incorrect encryption parameter.

    Returns:
        (bool): True if connection is configured.
    """
    server_handler = pytest.server_handler
    try:
        dut_handler = getattr(pytest, f'{gw_device.lower()}_handler')
        if not dut_handler:
            raise Exception(f'Invalid gw_device {gw_device} provided')
    except Exception as e:
        raise Exception(f'Invalid gw_device {gw_device} provided\n{e}')
    try:
        ref_handler = getattr(pytest, f'{leaf_device.lower()}_handler')
        if not ref_handler:
            raise Exception(f'Invalid leaf_device {leaf_device} provided')
    except Exception as e:
        raise Exception(f'Invalid leaf_device {leaf_device} provided\n{e}')

    # GW bhaul Radio/VIF constants
    gw_bhaul_interface_type = 'backhaul_ap'
    gw_bhaul_enabled = 'true'
    gw_bhaul_mode = 'ap'
    gw_bhaul_psk = "FutTestPSK"
    gw_bhaul_ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
    gw_bhaul_ssid_broadcast = 'disabled'
    gw_bhaul_mac_list_type = 'whitelist'
    # GW bhaul Inet constants
    gw_bhaul_broadcast_n = "255"
    gw_bhaul_inet_addr_n = "129"
    gw_bhaul_subnet = f"169.254.{randrange(1, 253)}"
    gw_bhaul_netmask = "255.255.255.128"
    gw_bhaul_if_type = "vif"
    gw_bhaul_ip_assign_scheme = "static"
    gw_bhaul_nat = "false"
    gw_bhaul_network = "true"
    # GW device capabilities
    gw_phy_radio_if_name = dut_handler.capabilities.get('interfaces.phy_radio_name').get(gw_radio_band)
    gw_hw_mode = dut_handler.capabilities.get('interfaces.radio_hw_mode').get(gw_radio_band)
    gw_vif_radio_idx = dut_handler.capabilities.get('interfaces.vif_radio_idx').get(gw_bhaul_interface_type)
    gw_bhaul_mtu = dut_handler.capabilities.get('mtu.backhaul')
    gw_bhaul_ap_if_name = dut_handler.capabilities.get('interfaces').get(gw_bhaul_interface_type).get(gw_radio_band)
    gw_uplink_gre_mtu = dut_handler.capabilities.get('mtu.uplink_gre')
    gw_lan_br_if_name = dut_handler.capabilities.get('interfaces.lan_bridge')

    # LEAF bhaul Radio/VIF constants
    leaf_bhaul_interface_type = 'backhaul_sta'
    leaf_onboard_type = 'gre'
    # LEAF device_capabilities
    leaf_phy_radio_if_name = ref_handler.capabilities.get(f'interfaces.phy_radio_name.{leaf_radio_band}')
    leaf_bhaul_ap_if_name = ref_handler.capabilities.get(f'interfaces.{leaf_bhaul_interface_type}.{leaf_radio_band}')

    leaf_mac_arg = get_command_arguments(f'if_name=={leaf_phy_radio_if_name}')
    leaf_mac_ec, leaf_radio_mac_raw, std_err = ref_handler.run_raw('tools/device/ovsdb/get_radio_mac_from_ovsdb', leaf_mac_arg)
    if leaf_radio_mac_raw is None or leaf_radio_mac_raw == '' or leaf_mac_ec != ExpectedShellResult:
        raise FailedException(f'Failed to retrieve MAC for REF {leaf_phy_radio_if_name}')

    gw_bhaul_mac_list = f'\'["set",["{leaf_radio_mac_raw}"]]\''
    gw_bhaul_ap_vif_radio_args_base = [
        f"-if_name {gw_phy_radio_if_name}",
        f"-vif_if_name {gw_bhaul_ap_if_name}",
        f"-vif_radio_idx {gw_vif_radio_idx}",
        f"-channel {channel}",
        f"-ht_mode {ht_mode}",
        f"-hw_mode {gw_hw_mode}",
        f"-enabled {gw_bhaul_enabled}",
        f"-mac_list {gw_bhaul_mac_list}",
        f"-mac_list_type {gw_bhaul_mac_list_type}",
        f"-mode {gw_bhaul_mode}",
        f"-ssid {gw_bhaul_ssid}",
        f"-ssid_broadcast {gw_bhaul_ssid_broadcast}",
        f"-wifi_security_type {wifi_security_type}",
    ]
    gw_bhaul_ap_inet_args = get_command_arguments(
        f"-if_name {gw_bhaul_ap_if_name}",
        f"-if_type {gw_bhaul_if_type}",
        f"-broadcast_n {gw_bhaul_broadcast_n}",
        f"-inet_addr_n {gw_bhaul_inet_addr_n}",
        f"-subnet {gw_bhaul_subnet}",
        f"-netmask {gw_bhaul_netmask}",
        f"-ip_assign_scheme {gw_bhaul_ip_assign_scheme}",
        f"-mtu {gw_bhaul_mtu}",
        f"-NAT {gw_bhaul_nat}",
        f"-enabled {gw_bhaul_enabled}",
        f"-network {gw_bhaul_network}",
    )
    leaf_bhaul_sta_radio_vif_args_base = [
        f"-if_name {leaf_bhaul_ap_if_name}",
        f"-ssid {gw_bhaul_ssid}",
        f"-onboard_type {leaf_onboard_type}",
        f"-channel {channel}",
        f"-wifi_security_type {wifi_security_type}",
        '-clear_wcc',
        '-wait_ip',
    ]

    gw_bhaul_ap_vif_radio_args_base += dut_handler.configure_wifi_security(wifi_security_type, encryption, gw_bhaul_psk)
    leaf_bhaul_sta_radio_vif_args_base += ref_handler.configure_wifi_security(wifi_security_type, encryption, gw_bhaul_psk)
    gw_gre_conf_args = get_command_arguments(
        gw_bhaul_ap_if_name,
        leaf_radio_mac_raw,
        gw_uplink_gre_mtu,
        gw_lan_br_if_name,
    )

    create_bhaul_ap_radio_vif_args = get_command_arguments(*gw_bhaul_ap_vif_radio_args_base)
    leaf_bhaul_sta_radio_vif_args = get_command_arguments(*leaf_bhaul_sta_radio_vif_args_base)

    # On DUT - Create and configure GW bhaul AP interface
    assert dut_handler.run('tools/device/create_radio_vif_interface',
                           create_bhaul_ap_radio_vif_args) == ExpectedShellResult
    assert dut_handler.run('tools/device/create_inet_interface',
                           gw_bhaul_ap_inet_args) == ExpectedShellResult
    # On REF - Create and configure LEAF bhaul STA interfaces
    assert ref_handler.run('tools/device/configure_sta_interface',
                           leaf_bhaul_sta_radio_vif_args) == ExpectedShellResult
    if not skip_gre:
        # On DUT - Configure GRE tunnel
        assert dut_handler.run('tools/device/configure_gre_tunnel_gw', gw_gre_conf_args) == ExpectedShellResult

    return True
