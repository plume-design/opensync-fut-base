"""Module used to configure the FUT device (DUT, REF, REF2) device into either router or bridge mode.

Its purpose is to ease the device mode configuration by providing a
one-step configuration by calling the 'configure_device_mode' function, which
would determine all the required arguments from the e.g. device capabilities
file for device, and call the 'set_router_mode' or 'set_bridge_mode' script
to put the device into the selected mode.
"""

import pytest

import framework.tools.logger
from framework.tools.functions import get_command_arguments
from test.globals import ExpectedShellResult


global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


def configure_device_mode(device_name, device_mode):
    """Configure device in either router or bridge mode.

    As an argument function takes device mode, other arguments are fetched in
    the function itself (device capabilities) or hardcoded, e.g.: DHCP server
    configuration.

    Args:
        device_name (str): Device name to configure (DUT, REF, REF2)
        device_mode (str): Mode to put device into

    Raises:
        Exception: If invalid device mode is provided.

    Returns:
        (bool): True if device is configured.
    """
    try:
        device_handler = getattr(pytest, f'{device_name.lower()}_handler')
        if not device_handler:
            raise Exception(f'Invalid device_name {device_name} provided')
    except Exception as e:
        raise Exception(f'Invalid device_name {device_name} provided\n{e}')

    # Test arguments from device capabilities
    if_lan_br_name = device_handler.capabilities.get_or_raise('interfaces.lan_bridge')
    eth_wan_interface = device_handler.capabilities.get_or_raise("interfaces.primary_wan_interface")

    # Fixed arguments
    internal_dhcpd = '\'[\"map\",[' \
                     '[\"dhcp_option\",\"3,192.168.40.1;6,192.168.40.1\"],' \
                     '[\"force\",\"false\"],[\"lease_time\",\"12h\"],' \
                     '[\"start\",\"192.168.40.2\"],' \
                     '[\"stop\",\"192.168.40.254\"]' \
                     ']]\''
    internal_inet_addr = '192.168.40.1'

    # Build configuration scripts arguments
    set_router_mode_args = get_command_arguments(
        if_lan_br_name,
        internal_dhcpd,
        internal_inet_addr,
        eth_wan_interface,
    )
    set_bridge_mode_args = get_command_arguments(
        if_lan_br_name,
        eth_wan_interface,
    )

    # Put device into router or bridge mode.
    # Raise exception if invalid mode given.
    if device_mode == 'router':
        assert device_handler.run('tools/device/set_router_mode', set_router_mode_args) == ExpectedShellResult
    elif device_mode == 'bridge':
        assert device_handler.run('tools/device/set_bridge_mode', set_bridge_mode_args) == ExpectedShellResult
    else:
        raise Exception('Invalid device mode')
    return True
