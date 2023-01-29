"""Module used to configure device AP interface.

Its purpose is to ease the configuration of AP interface by providing a
one-step configuration by calling the 'configure_ap_interface' function, which
would determine all the required arguments for proper AP interface configuration
on device.
"""
from random import randrange

import pytest

import framework.tools.logger
from framework.tools.functions import FailedException, get_command_arguments
from test.globals import ExpectedShellResult

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


def configure_ap_interface(
        channel,
        ht_mode,
        radio_band,
        wifi_security_type="wpa",
        encryption="WPA2",
        psk="fut_ap_psk",
        device_name='dut',
        enabled="true",
        interface_type='home_ap',
        channel_mode="manual",
        mode="ap",
        ssid_broadcast="enabled",
        wpa_oftag="fut-ap--1",
        ap_broadcast_n=None,
        ap_inet_addr_n=None,
        ap_subnet=None,
        ap_netmask=None,
        ap_ip_assign_scheme="static",
        ap_nat="false",
        ap_mtu=None,
        ssid=None,
        reset_vif=True,
        bridge=True,
        skip_inet=False,
        vif_name=None,
        vif_radio_idx=None,
):
    """Configure AP interface on device.

    As an argument function takes device mode, other arguments are fetched in

    Raises:
        Exception: If invalid device mode is provided.

    Returns:
        (bool): True if AP is configured.
    """
    try:
        device_handler = getattr(pytest, f'{device_name.lower()}_handler')
        if not device_handler:
            raise Exception(f'Invalid device_name {device_name} provided')
    except Exception as e:
        raise Exception(f'Invalid device_name {device_name} provided\n{e}')

    try:
        server_handler = pytest.server_handler
    except Exception as e:
        raise Exception(f'Could not acquire server_handler from pytest\n{e}')

    # Get physical radio name
    phy_radio_name = device_handler.capabilities.get(f'interfaces.phy_radio_name.{radio_band}', None)
    if phy_radio_name is None:
        raise FailedException(f'Could not determine phy_radio_name for radio_band:{radio_band}')

    vif_name = device_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{radio_band}') if not vif_name else vif_name
    vif_radio_idx = device_handler.capabilities.get_or_raise(f'interfaces.vif_radio_idx.{interface_type}') if not vif_radio_idx else vif_radio_idx
    ap_mtu = device_handler.capabilities.get_or_raise('mtu.backhaul') if not ap_mtu else ap_mtu
    ap_broadcast_n = "255" if not ap_broadcast_n else ap_broadcast_n
    ap_inet_addr_n = "129" if not ap_inet_addr_n else ap_inet_addr_n
    ap_subnet = f"169.24{vif_radio_idx}.{randrange(1, 253)}" if not ap_subnet else ap_subnet
    ap_netmask = "255.255.255.128" if not ap_netmask else ap_netmask
    ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}" if not ssid else ssid

    dut_if_lan_br_name = device_handler.capabilities.get_or_raise('interfaces.lan_bridge')
    if bridge and bridge is True:
        bridge = f'-bridge {dut_if_lan_br_name}'
    elif type(bridge) == str:
        bridge = f'-bridge {bridge}'
    else:
        bridge = ''

    if interface_type == 'backhaul_ap':
        ssid_broadcast = "disabled"

    home_ap_radio_vif_inet_args_base = [
        f"-if_name {phy_radio_name}",
        f"-vif_if_name {vif_name}",
        f"-vif_radio_idx {vif_radio_idx}",
        f"-channel {channel}",
        f"-channel_mode {channel_mode}",
        f"-ht_mode {ht_mode}",
        f"-enabled {enabled}",
        f"-mode {mode}",
        f"-ssid {ssid}",
        f"-ssid_broadcast {ssid_broadcast}",
        "-if_type vif",
        "-network true",
        f"-wifi_security_type {wifi_security_type}",
        bridge,
    ]
    if not skip_inet:
        home_ap_radio_vif_inet_args_base += [
            "-inet_enabled true",
            f"-inet_if_name {vif_name}",
            f"-broadcast_n {ap_broadcast_n}",
            f"-inet_addr_n {ap_inet_addr_n}",
            f"-subnet {ap_subnet}",
            f"-netmask {ap_netmask}",
            f"-ip_assign_scheme {ap_ip_assign_scheme}",
            f"-NAT {ap_nat}",
            f"-mtu {ap_mtu}",
        ]

    home_ap_radio_vif_inet_args_base += device_handler.configure_wifi_security(wifi_security_type, encryption, psk)
    home_ap_radio_vif_inet_args = get_command_arguments(*home_ap_radio_vif_inet_args_base)

    if reset_vif:
        assert device_handler.run('tools/device/vif_reset') == ExpectedShellResult
    assert device_handler.run('tools/device/configure_ap_interface', home_ap_radio_vif_inet_args) == ExpectedShellResult

    return True
