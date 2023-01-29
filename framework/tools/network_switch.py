#!/usr/bin/env python3

"""Module used to configure the VLAN interfaces of the network switch.

Module provides the means for configuring the network switch interfaces.
It is intended to switch the roles of interfaces that are used by gateway and
leaf device in the OSRT testbed.
"""

import argparse
import sys
from pathlib import Path

topdir_path = str(Path(Path(__file__).absolute()).parents[2])
sys.path.append(topdir_path)
from framework.server_handler import ServerHandlerClass
from lib_testbed.generic.switch.switchlib import switchlib

ServerHandler = ServerHandlerClass()


def parse_arguments():
    """Standalone method to parse script input arguments."""
    parser = argparse.ArgumentParser(
        description='Network switch manipulation tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--alias', '-a',
        type=str,
        required=True,
        help='Network switch port alias',
    )
    parser.add_argument(
        '--role', '-r',
        type=str,
        required=True,
        choices=['gw', 'leaf'],
        help='Role of port to set to',
    )
    input_args = parser.parse_args()
    return input_args


if __name__ == '__main__':
    # Parse input arguments
    input_args = parse_arguments()
    network_switch = switchlib
    network_switch.switch_init_config(ServerHandler.testbed_cfg.get('network_switch'))

    if input_args.role == 'gw':
        print(f'{input_args.alias} -> Add VLAN200::untagged')
        network_switch.vlan_set([input_args.alias], '200', 'untagged')
    elif input_args.role == 'leaf':
        print(f'{input_args.alias} -> Remove VLAN200')
        network_switch.vlan_remove([input_args.alias], '200')
    else:
        print('Invalid port role selected')
        sys.exit(1)
    sys.exit(0)
