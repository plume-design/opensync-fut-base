#!/usr/bin/env python3

"""Module to control SSH connection to the OSRT devices."""

import argparse
import signal
import subprocess
import sys
from pathlib import Path
from time import time

topdir_path = str(Path(Path(__file__).absolute()).parents[2])
sys.path.append(topdir_path)
from framework.server_handler import ServerHandlerClass  # noqa: E402
from lib_testbed.generic.util.config import get_model_capabilities

PING_TIMEOUT_MAX = 600
ServerHandler = ServerHandlerClass()


def parse_arguments():
    """Standalone method to parse script input arguments."""
    parser = argparse.ArgumentParser(
        description='Wait for OpenSync device management ssh',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '--devices', '-D',
        type=str,
        required=True,
        choices=ServerHandler.devices_cfg,
        nargs='+',
        help='FUT Device type',
    )
    parser.add_argument(
        '--ping_cmd', '-P',
        type=str,
        required=False,
        default="ping -q -c1 -W1 -w1",
        help='Define the command to use for pinging the device',
    )
    parser.add_argument(
        '--wait_for_ssh', '-s',
        action='store_true',
        help='Wait for ssh as well as ping',
    )
    input_args = parser.parse_args()
    return input_args


def check_host_ping(host, ping_cmd):
    """Ping the host.

    Args:
        host (str): IP of the host
        ping_cmd (str): ping command

    Returns:
        (bool): True if pinging the host succeeded, False otherwise.
    """
    cmd = f'{ping_cmd} {host}'
    try:
        if subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True) == 0:
            return True
    except OSError as exception:
        print("Execution failed:", exception, file=sys.stderr)
    return False


def check_host_ssh(host, device_api):
    """Check if SSH connection to the host is established.

    Executes 'ls' command.

    Args:
        host (str): IP of the host
        device_api (_type_): _description_

    Returns:
        (bool): True if SSH connection is extablished, False otherwise.
    """
    res = device_api.run_raw("ls /", timeout=5)
    if res[0] == 0:
        return True
    return False


def signal_handler(sig, frame):
    """Handle the signal.

    Args:
        sig (_type_): Not used.
        frame (_type_): Not used.
    """
    sys.exit(0)


def wait_for_hosts(devices, ping_cmd):
    """Wait for all hosts to respond to ping.

    Args:
        devices (str): Devices to wait for
        ping_cmd (str): Ping command

    Raises:
        TimeoutError: Devices did not respond withing given timeout.
    """
    # Take the largest timeout of all devices, loop until time runs out
    timeout_max = max([devices[device]['reboot_timeout'] for device in devices])
    start_time = time()
    while (time() - start_time) < timeout_max:
        # Check each device sequentially every iteration, but treat them as a group overall
        for device in devices.copy():
            # Ping only devices that did not yet respond to ping.
            if not devices[device]['pingable']:
                if check_host_ping(devices[device]['mgmt_ip'], ping_cmd):
                    print(f"Connection to {devices[device]['mgmt_ip']} established")
                    devices[device]['pingable'] = True
                else:
                    print(f"Waiting for {devices[device]['mgmt_ip']} to respond to ping...")
            elif devices[device]['device_api'] is not None:
                if check_host_ssh(devices[device]['mgmt_ip'], devices[device]['device_api']):
                    print(f"SSH to {devices[device]['mgmt_ip']} available")
                    # Remove device from loop.
                    devices.pop(device)
                else:
                    print(f"Waiting for SSH to {devices[device]['mgmt_ip']}...")
            else:
                devices.pop(device)
        # Check if there are any devices left to be pinged.
        if not devices:
            print(f"Connection to devices established within {time() - start_time} seconds.")
            return
    raise TimeoutError(f"ERROR: Connection to {list(devices)} could not be established within {timeout_max} seconds")


if __name__ == '__main__':
    # Accept ctrl+C interrupt signal
    signal.signal(signal.SIGINT, signal_handler)

    # Parse input arguments
    input_args = parse_arguments()

    # Determine device parameters for each specified device
    devices = {}
    mng_ip = None
    for name in input_args.devices:
        device = {}
        for _device_n, device_c in ServerHandler.testbed_cfg.get('devices').items():
            if isinstance(device_c, dict) and device_c['name'] == name:
                mng_ip = device_c['mgmt_ip']
            elif isinstance(device_c, list):
                for dc in device_c:
                    if dc['name'] == name:
                        mng_ip = dc['mgmt_ip']
        if not mng_ip:
            print(f'Failed to acquire mng_ip for {name}')
            sys.exit(1)

        device["mgmt_ip"] = mng_ip
        if 'client' in name:
            device["reboot_timeout"] = getattr(ServerHandler, name).get('device_config').get('kpi.boot_time', 160)
        else:
            model_name = getattr(ServerHandler, name).get('device_config').get('pod_api_model')
            device["reboot_timeout"] = get_model_capabilities(model_name).get('kpi')['boot_time']
        if device["reboot_timeout"] > PING_TIMEOUT_MAX:
            print(f"ERROR: Ensure timeout={device['reboot_timeout']}s for {name} is less than {PING_TIMEOUT_MAX}s")
        device["device_api"] = ServerHandler.get_pod_api(name) if input_args.wait_for_ssh else None
        # Start with assumption that device is not accessible
        device["pingable"] = False
        devices[name] = device

    # Wait for PING and optionally SSH for all hosts simultaneously
    wait_for_hosts(devices, input_args.ping_cmd)
