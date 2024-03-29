#!/usr/bin/env python3

"""CLI tool to perform the device setup necessary for FUT execution."""


import argparse
import signal
import subprocess
import sys
import threading
import traceback
from pathlib import Path

import pytest

from framework.device_handler import DeviceHandler
from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import (
    flatten_list,
    step,
)
from framework.node_handler import NodeHandler
from framework.server_handler import ServerHandler
from lib_testbed.generic.util.logger import log

lock = threading.Lock()


ALL_CLIENTS_TUPLE = ("w1", "w2", "e1", "e2")
ALL_NODES_TUPLE = ("gw", "l1", "l2")


def parse_arguments():
    """Standalone method to parse script input arguments."""
    parser = argparse.ArgumentParser(
        description="Initiate FUT device setup",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--nodes",
        "-n",
        nargs="+",
        required=True,
        choices=ALL_NODES_TUPLE,
        help="List of nodes",
    )
    parser.add_argument(
        "--clients",
        "-c",
        nargs="*",
        required=False,
        choices=ALL_CLIENTS_TUPLE,
        default=[],
        help="List of clients",
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


def setup_fut_configurator():
    log.info("Setting up FUT configurator")
    try:
        with step("FUT configurator initialization"):
            pytest.fut_configurator = FutConfigurator()
    except Exception:
        raise RuntimeError(traceback.format_exc())


def setup_server_handler():
    log.info("Setting up server handler")
    try:
        with step("Server handler initialization"):
            pytest.server = ServerHandler(name="host")
    except Exception:
        raise RuntimeError(traceback.format_exc())


def setup_node_handlers(nodes=ALL_NODES_TUPLE):
    log.info("Setting up node handlers")
    try:
        for node in nodes:
            log.debug(f"Setting up {node} handler")
            if hasattr(pytest, node):
                log.info(f"Found existing {node} handler")
                continue
            with step(f"{node.upper()} handler initialization"):
                setattr(pytest, node, NodeHandler(name=node))
    except Exception:
        raise RuntimeError(traceback.format_exc())


def setup_client_handlers(clients=ALL_CLIENTS_TUPLE):
    log.info("Setting up client handlers")
    try:
        for client in clients:
            log.debug(f"Setting up {client} handler")
            with step(f"{client.upper()} handler initialization"):
                setattr(pytest, client, DeviceHandler(name=client))
    except Exception:
        raise RuntimeError(traceback.format_exc())


def setup_server_device():
    log.info("Performing server device setup")
    server = pytest.server
    server.clear_folder(server.fut_dir)
    try:
        with step("Server device setup"):
            server.file_transfer(folders=["docker", "framework", "resource", "lib_testbed", "shell"], as_sudo=False)
            assert server.execute("server_add_response_policy_zone", suffix=".sh", folder="docker/server")[0] == 0
            # Start FUT services in dedicated docker container
            assert server.execute("dock-run", suffix=".server", folder="docker/server")[0] == 0
            # Add docker container ID as an attribute for later use
            pytest.server_docker = server.get_docker_container_id()
    except Exception:
        raise RuntimeError(traceback.format_exc())


def setup_node_device(node, *args):
    assert node in ALL_NODES_TUPLE
    try:
        with step(f"{node.upper()} device setup"):
            node_handler = getattr(pytest, node)

            # TMP mount executable
            fut_dir = node_handler.fut_dir
            mount_point_ec, mount_point_std_out, mount_point_std_err = node_handler.device_api.run_raw(
                f"test -e {fut_dir} || mkdir -p {fut_dir} && df -TP {fut_dir} | tail -1 | awk -F' ' '{{print $NF}}'",
            )
            assert mount_point_ec == 0
            assert (
                node_handler.device_api.run_raw(f"mount && mount | grep -E 'on {mount_point_std_out} .*noexec'")[0] == 1
            )

            # Transfer FUT files
            node_handler.file_transfer(folders=["shell"])

            if Path("internal/shell").is_dir():
                node_handler.file_transfer(folders=["internal/shell"], skip_env_file=True)

            # Verify GW regulatory domain
            device_region = node_handler.regulatory_domain
            log.info(f"Region retrieved from node_handler is {device_region}")
            config_region = node_handler.capabilities.get_regulatory_domain()
            log.info(f"Device node_handler, configured region: {config_region}, actual region: {device_region}")
            assert config_region == device_region

            if node != "gw":
                # Prevent node from rebooting
                assert node_handler.execute("tools/device/device_init", skip_logging=True)[0] == 0
    except Exception:
        raise RuntimeError(traceback.format_exc())


def setup_client_device(client, *args):
    assert client in ALL_CLIENTS_TUPLE
    try:
        with step(f"{client.upper()} device setup"):
            client_handler = getattr(pytest, client)
            client_handler.file_transfer(folders=["shell"])
    except Exception:
        raise RuntimeError(traceback.format_exc())


def pre_test_device_setup(node_devices=ALL_NODES_TUPLE, client_devices=ALL_CLIENTS_TUPLE):
    try:
        threads = []
        setup_device_map = []
        log.info(f"Performing setup for the following devices: {node_devices + client_devices}")

        setup_fut_configurator()
        setup_server_handler()
        setup_server_device()

        log.info(f"Performing SSH availability check for the following devices: {node_devices}")

        server = pytest.server

        with step("SSH availability check"):
            ssh_check_nodes = ",".join(node_devices)
            stream = subprocess.Popen(
                [f"{server.fut_base_dir}/framework/tools/wait_for_host_ssh.py", ssh_check_nodes],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = stream.communicate()
            stdout = stdout.decode("utf-8").strip()
            exit_code = stream.returncode
            log.info(stdout)
            assert exit_code == 0

        if node_devices:
            setup_node_handlers(node_devices)
            setup_device_map.extend(zip([setup_node_device] * len(node_devices), node_devices))

        if client_devices:
            setup_client_handlers(client_devices)
            setup_device_map.extend(
                zip([setup_client_device] * (len(client_devices)), set(client_devices) - {"e1", "e2"}),
            )

        log.info("Setting up node devices")
        for target, target_args in setup_device_map:
            log.debug(f"Setting up {target_args} device")
            flattened_args = flatten_list([target_args])
            thread = threading.Thread(target=target, args=flattened_args)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    except Exception:
        raise RuntimeError(traceback.format_exc())


if __name__ == "__main__":
    # Accept Ctrl+C as a signal interrupt
    signal.signal(signal.SIGINT, signal_handler)

    # Parse input arguments
    input_args = parse_arguments()
    nodes = input_args.nodes
    clients = input_args.clients

    pre_test_device_setup(node_devices=nodes, client_devices=clients)
