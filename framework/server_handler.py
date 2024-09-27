import json
import os
import subprocess
import time
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Callable, Literal

import pytest

from framework.device_handler import DeviceHandler
from framework.lib.fut_lib import (
    allure_attach_to_report,
    allure_script_execution_post_processing,
    check_if_dicts_match,
    output_to_json,
    print_allure,
    step,
)
from framework.tools.fut_mqtt_tool import extract_mqtt_data_as_dict
from lib_testbed.generic.switch.generic.switch_tool_generic import SwitchToolGeneric
from lib_testbed.generic.util.logger import log


class ServerHandler(DeviceHandler):
    def __init__(self, name):
        log.debug("Entered ServerHandler class")
        super().__init__(name)
        self.mgmt_ip_dict = self._get_mgmt_ip_dict()
        self.mqtt_hostname = "fut.opensync.io"
        self.mqtt_messages_file = "mqtt_messages.json"
        self.mqtt_port = 65002
        self.opensync_root = os.getenv("OPENSYNC_ROOT", "/home/plume/fut-base")
        self.docker_root = f"{self.opensync_root}/docker"
        self.docker_run_cmd = f"{self.docker_root}/dock-run"
        self.switch = self._switch_tool()
        self.fut_cloud = None
        self.hap_path = f"{self.fut_dir}/shell/tools/server/files/haproxy.cfg"
        self.cloud_script = "start_cloud_simulation.sh"
        self.cloud_script_path = f"{self.fut_dir}/shell/tools/server/{self.cloud_script}"

    def get_docker_container_id(self):
        active_containers_cmd = 'docker container list --filter=ancestor=fut-server --format "{{.ID}}"'
        container = self.device_api.run_raw(active_containers_cmd)[1]
        return container

    def _switch_tool(self):
        """
        Create a SwitchToolGeneric object.

        Returns:
            (object): SwitchToolGeneric object.
        """
        return SwitchToolGeneric(config=self.testbed_cfg)

    def _get_mgmt_ip_dict(self):
        """
        Retrieve the management IPs for all nodes.

        Returns:
            mgmt_ip_dict (dict): Dictionary of node management IPs.

        """
        mgmt_ip_dict = {}

        for device in ["gw", "l1", "l2"]:
            if device in ["l1", "l2"]:
                hostname = device[:1] + "eaf" + device[1:]
            else:
                hostname = device
            mgmt_ip_cmd = f"getent hosts {hostname} | cut -d' ' -f1"
            mgmt_ip = self.device_api.run_raw(mgmt_ip_cmd)[1]
            mgmt_ip_dict.update({device: mgmt_ip})

        return mgmt_ip_dict

    def restart_cloud(self):
        """
        Restart FUT cloud simulation.

        Cloud simulation is restarted by executing the cloud script.
        The script is selected at the instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is restarted,
                False otherwise.
        """
        log.debug("Restarting FUT Cloud simulation.")

        if self.device_api.run_raw(f"{self.cloud_script_path} -r")[0] != 0:
            log.warning("Could not restart FUT cloud simulation.")
            return False

        log.debug("FUT Cloud simulation restarted.")

        return True

    def start_cloud(self):
        """
        Start FUT cloud simulation.

        Simulation is started by executing the cloud script. The script
        is selected at the instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is started,
                False otherwise.
        """
        log.debug("Starting FUT Cloud simulation")

        if self.device_api.run_raw(self.cloud_script_path)[0] != 0:
            log.warning("Could not start FUT cloud simulation.")
            return False

        log.debug("FUT Cloud simulation started.")

        return True

    def stop_cloud(self):
        """
        Stop FUT cloud simulation.

        Cloud simulation is stopped by stopping the cloud script. The
        script is selected at the instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is stopped,
                False otherwise.
        """
        log.debug("Stopping FUT Cloud simulation")

        if self.device_api.run_raw(f"{self.cloud_script_path} -s")[0] != 0:
            log.warning("Could not stop FUT cloud simulation.")
            return False

        log.debug("FUT Cloud simulation stopped.")

        return True

    @staticmethod
    def get_wan_mac():
        """
        Return WAN MAC address.

        Returns:
            (str): WAN interface MAC.
        """
        with open("/sys/class/net/eth0/address", "r") as infile:
            wan_mac = infile.readlines()

        return wan_mac[0].rstrip()

    def _get_cmd_process(self, cmd, as_sudo=False, shell_env_var=None, **kwargs):
        """
        Start subprocess and executes child program in a new process.

        Args:
            cmd (str): Command to be executed.
            as_sudo (bool, optional): Execute the command as 'sudo'.
                Defaults to False.
            shell_env_var (str, optional): Shell environment variables.
                Defaults to None.
        Returns:
            cmd_process (command): Subprocess command parameters.
        """
        shell = True if "shell" not in kwargs else kwargs["shell"]
        stdin = None
        stdout = subprocess.PIPE
        stderr = subprocess.STDOUT
        os_env = os.environ.copy()
        os_env["FUT_TOPDIR"] = self.fut_dir
        if shell_env_var:
            os_env.update(shell_env_var)
        if as_sudo:
            cmd_pass = subprocess.Popen(
                ["echo", self.password],
                stdout=stdout,
                stderr=stderr,
                universal_newlines=True,
                env=os_env,
                shell=shell,
            )
            stdin = cmd_pass.stdout
            cmd = f"sudo -n -S {cmd}"
        cmd_process = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            universal_newlines=True,
            env=os_env,
            shell=shell,
        )
        return cmd_process

    def execute_in_docker(self, command, args="", as_sudo=False, bash=False, **kwargs):
        if isinstance(args, list):
            args = " ".join(args)

        if bash:
            bash = "bash -c"
        else:
            bash = ""

        cmd = f"docker exec {pytest.server_docker} {bash} {command} {args}"

        if as_sudo:
            cmd = f"sudo {cmd}"

        log.info(f"Executing: {cmd}")
        cmd_ec, cmd_std_out, cmd_std_err = self.device_api.run_raw(cmd, as_sudo=as_sudo, **kwargs)

        allure_attach_to_report(name="log_client_host", body=cmd_std_out)

        return cmd_ec, cmd_std_out, cmd_std_err

    def _run_raw(self, path, args="", as_sudo=False, **kwargs):
        ext = ".sh" if "suffix" not in kwargs else kwargs["suffix"]
        folder = "shell" if "folder" not in kwargs else kwargs["folder"]

        if isinstance(args, list):
            args = " ".join(args)

        cmd = f"{self.fut_dir}/{folder}/{path}{ext} {args}"

        if ext == ".py":
            cmd = f"python3 -u {cmd}"

        if as_sudo:
            cmd = f"sudo {cmd}"

        timeout = self.test_script_timeout * 2 if "timeout" not in kwargs else kwargs["timeout"]

        log.debug(f"Executing: {cmd}")

        cmd_res = self.device_api.run_raw(cmd, timeout=timeout)

        cmd_ec = cmd_res[0]
        cmd_std_out = "" if not cmd_res[1] else cmd_res[1]
        cmd_std_err = "" if not cmd_res[2] else cmd_res[2]

        return cmd_ec, cmd_std_out, cmd_std_err

    @allure_script_execution_post_processing
    def execute(self, path: str, args: str = "", as_sudo: bool = False, **kwargs) -> tuple[int, str, str]:
        """
        Execute the specified script with optional arguments.

        Args:
            path (str): Path to script.
            args (str): Optional script arguments. Defaults to empty
                string.
            as_sudo (bool): Execute script with superuser privileges.
        Keyword Args:
            suffix (str): Suffix of the script
            folder (str): Name of the folder where the script is located
        Returns:
            (list): List comprised of the exit code, standard output and standard error
        """
        cmd_ec, cmd_std_out, cmd_std_err = self._run_raw(path, args, as_sudo, **kwargs)
        return cmd_ec, cmd_std_out, cmd_std_err

    def _mqtt_start_listener(self, queue: Queue, mqtt_args: str, mqtt_timeout: int) -> None:
        """
        Start the FUT MQTT tool with the provided arguments.

        Args:
            queue (object): Queue object.
            mqtt_args (str): String containing MQTT configuration arguments.
            mqtt_timeout (int): MQTT timeout.
        """
        log.info("Running FUT MQTT tool.")
        res = self.execute_in_docker(
            f"{self.fut_dir}/framework/tools/fut_mqtt_tool.py",
            args=mqtt_args,
            timeout=mqtt_timeout,
        )
        log.info(f"Response from FUT MQTT tool: {res}")
        queue.put(res)

    def mqtt_trigger_and_validate_message(
        self,
        topic: str,
        trigger: Callable,
        expected_data: dict,
        comparison_method: str = "exact_match",
        max_message_count: int = 1,
        node_filter: str = "",
    ) -> Literal[True]:
        """
        Start the FUT MQTT tool.

        Starts the tool configures the MQTT connection and subscribes to
        a topic. This method also starts a trigger function once the
        MQTT connection has been configured and validates the received
        data against a dictionary containing the expected data using the
        specified comparison method.

        Args:
            topic (str): MQTT topic.
            trigger (function): The trigger function.
            expected_data (dict): Dictionary containing the expected data.
            comparison_method (str): Comparison method. Supported options:
                exact_match or in_range.
            max_message_count (int): Number of messages to collect before
                terminating connection
            node_filter (str) : Filter received messages based on node ID

        Raises:
            RuntimeError: If no MQTT messages were collected.
            RuntimeError: If an issue was encountered during the data
                comparison.

        Returns:
            (bool): True if the MQTT connection, message gathering and data
                comparison were performed correctly.
        """
        main_queue: Queue = Queue()
        mqtt_timeout = 300
        messages_remote_path = f"{self.fut_dir}/{self.mqtt_messages_file}"
        messages_local_path = f"{self.fut_base_dir}/{self.mqtt_messages_file}"
        server_mqtt_args_base = [
            f"--hostname {self.mqtt_hostname}",
            f"--port {self.mqtt_port}",
            f"--topic {topic}",
            "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
            f"--max_message_count {max_message_count}",
            f"--timeout {mqtt_timeout}",
            "--collect_messages",
            "--stdout_output",
            f"--json_output {messages_remote_path}",
        ]

        if node_filter:
            server_mqtt_args_base += [
                f"--node_filter {node_filter}",
            ]

        server_mqtt_args = self.get_command_arguments(*server_mqtt_args_base)

        thread = Thread(
            target=self._mqtt_start_listener,
            args=(main_queue, server_mqtt_args, mqtt_timeout),
        )
        thread.start()
        time.sleep(2)
        # Run trigger method
        trigger()
        # Wait for MQTT thread
        thread.join()
        time.sleep(1)
        _mqtt_listener_thread_res = main_queue.get(timeout=5)

        if (
            _mqtt_listener_thread_res[0] != 0
            or _mqtt_listener_thread_res[1] == ""
            or _mqtt_listener_thread_res[1] is None
        ):
            raise RuntimeError("Failed to collect MQTT messages.")

        with step("Data extraction"):
            # Access collected MQTT messages
            self.device_api.get_file(messages_remote_path, self.fut_base_dir, create_dir=False)
            with open(messages_local_path, "r") as mqtt_file:
                mqtt_messages = json.load(mqtt_file)
            # Extract required data from MQTT messages
            extracted_data = extract_mqtt_data_as_dict(mqtt_messages, expected_data.keys(), simplify=True)
            print_allure(f"The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}")
        with step("Testcase"):
            if comparison_method == "exact_match":
                data_comparison = check_if_dicts_match(expected_data, extracted_data)
            elif comparison_method == "in_range":
                if len(extracted_data) != 1 or len(expected_data) != 1:
                    raise RuntimeError(
                        'The "in_range" comparison method requires both dictionaries with the extracted and expected data to have only one key.',
                    )
                (range_limits,) = expected_data.values()
                if not isinstance(range_limits, tuple):
                    raise RuntimeError("The range limits should be passed as a tuple.")
                lower_range, upper_range = range_limits
                (reference_value,) = extracted_data.values()
                if lower_range <= reference_value <= upper_range:
                    print_allure(
                        f"The gathered data: {output_to_json(extracted_data, convert_only=True)} is within the specified range: {range_limits}",
                    )
                    return True
                else:
                    raise RuntimeError(
                        f"The gathered data: {output_to_json(extracted_data, convert_only=True)} is not within the specified range: {range_limits}",
                    )
            if data_comparison is True:
                print_allure(
                    f"The gathered data: {output_to_json(extracted_data, convert_only=True)} matches the expected data: {output_to_json(expected_data, convert_only=True)}",
                )
            else:
                raise RuntimeError(
                    f"The gathered data: {output_to_json(extracted_data, convert_only=True)} does not match the expected data {output_to_json(expected_data, convert_only=True)} for the following keys: {data_comparison}",
                )

        return True

    def clear_folder(self, folder_path: str) -> Literal[True]:
        """Remove contents of the target folder on the remote device."""
        if not Path(folder_path).is_absolute():
            folder_path = f"{self.fut_dir}/{folder_path}/"
        cmd = f"[ -d {folder_path} ] && sudo rm -rf {folder_path}"
        ret = self.device_api.run_raw(cmd)
        if ret[0] != 0:
            log.warning(f"Failed to empty {folder_path} on {self.name}.")
        return True
