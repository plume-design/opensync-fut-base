#!/usr/bin/env python3

"""Module to transfer selected file from the device (source) to the destination location."""


import argparse
import signal
import sys
from pathlib import Path

topdir_path = str(Path(Path(__file__).absolute()).parents[2])
sys.path.append(topdir_path)
from framework.server_handler import ServerHandlerClass  # noqa: E402

ServerHandler = ServerHandlerClass()


def parse_arguments():
    """Standalone method to parse script input arguments."""
    parser = argparse.ArgumentParser(
        description='Transfer file from source to destination',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '--device', '-D',
        type=str,
        required=True,
        choices=ServerHandler.devices_cfg,
        help='FUT Device type',
    )
    parser.add_argument(
        '--remote_file', '-f',
        type=str,
        required=True,
        help='Path to remote file',
    )
    parser.add_argument(
        '--destination', '-d',
        type=str,
        required=True,
        help='Location to transfer the remote file',
    )
    input_args = parser.parse_args()
    return input_args


def signal_handler(sig, frame):
    """Handle the signal.

    Args:
        sig (_type_): Not used
        frame (_type_): Not used
    """
    sys.exit(0)


if __name__ == '__main__':
    # Accept Ctrl+C interrupt signal
    signal.signal(signal.SIGINT, signal_handler)

    # Parse input arguments
    input_args = parse_arguments()
    name = input_args.device
    remote_file = input_args.remote_file
    file_name = Path(remote_file).name
    destination = input_args.destination

    # pod_api.get_file() transfers into destination subfolder "name"
    dest_filepath = Path(f'{destination}/{name}/{file_name}').absolute()
    # Clear destination
    dest_filepath.unlink(missing_ok=True)
    # Transfer file
    device_api = ServerHandler.get_pod_api(name)
    device_api.get_file(remote_file, destination)
    # Verify file location
    assert dest_filepath.is_file()
