import json
import time
from queue import Queue
from threading import Thread
from typing import Callable, Literal

from framework.handlers.client_handler import ClientHandler
from framework.lib.fut_lib import (
    allure_attach_to_report,
    check_if_dicts_match,
    get_command_arguments,
    output_to_json,
    print_allure,
    step,
)
from framework.tools.fut_mqtt_tool import extract_mqtt_data_as_dict
from lib_testbed.generic.util.logger import log


class ServerHandler(ClientHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.MQTT_HOSTNAME = "fut.opensync.io"
        self.MQTT_PORT = 65002
        self.MQTT_MESSAGES_FILE = "mqtt_messages.json"
        self.CLOUD_SCRIPT = "start_cloud_simulation.sh"
        self.cloud_script_path = f"{self.FUT_DIR}/shell/tools/server/{self.CLOUD_SCRIPT}"
        self.docker_container_id = None
        self.transfer_folders = ["docker", "framework", "resource", "lib_testbed", "shell", "config"]
        self.transfers = list(zip(self.transfer_folders, self.transfer_folders))

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
            f"{self.FUT_DIR}/framework/tools/fut_mqtt_tool.py",
            args=mqtt_args,
            timeout=mqtt_timeout,
        )
        log.info(f"Response from FUT MQTT tool: {res}")
        queue.put(res)

    def execute_in_docker(self, command, args="", as_sudo=False, bash=False, **kwargs):
        if isinstance(args, list):
            args = " ".join(args)

        if bash:
            bash = "bash -c"
        else:
            bash = ""

        cmd = f"docker exec {self.docker_container_id} {bash} {command} {args}"

        if as_sudo:
            cmd = f"sudo {cmd}"

        log.info(f"Executing: {cmd}")
        cmd_ec, cmd_std_out, cmd_std_err = self.run_raw(cmd, as_sudo=as_sudo, **kwargs)

        allure_attach_to_report(name="log_client_host", body=cmd_std_out)

        return cmd_ec, cmd_std_out, cmd_std_err

    def get_docker_container_id(self):
        active_containers_cmd = 'docker container list --filter=ancestor=fut-server --format "{{.ID}}"'
        container = self.run_raw(active_containers_cmd)[1]
        return container

    def restart_cloud(self):
        """
        Restart FUT cloud simulation.

        Cloud simulation is restarted by executing the cloud script.
        The script is selected at the instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is restarted,
                False otherwise.
        """
        log.debug(f"{self.nickname.upper()}: restarting FUT Cloud simulation.")

        if self.run_raw(f"{self.cloud_script_path} -r")[0] != 0:
            log.warning("Could not restart FUT cloud simulation.")
            return False

        log.debug(f"{self.nickname.upper()}: FUT Cloud simulation restarted.")

        return True

    def mqtt_trigger_and_validate_message(
        self,
        topic: str,
        trigger: Callable,
        expected_data: dict,
        unique_data: bool = False,
        comparison_method: str = "exact_match",
        inorder: bool = True,
        max_message_count: int = 1,
        node_filter: str = "",
        **kwargs,
    ) -> Literal[True]:
        """
        Start the FUT MQTT tool.

        Starts the tool, configures the MQTT connection and subscribes to
        a topic. This method also starts a trigger function once the
        MQTT connection has been configured and validates the received
        data against a dictionary containing the expected data using the
        specified comparison method.

        Args:
            topic (str): MQTT topic.
            trigger (function): The trigger function.
            expected_data (dict): Dictionary containing the expected data.
            unique_data(bool): Normalize iterator values in response to unique values.
            comparison_method (str): Comparison method. Supported options:
                exact_match or in_range.
            inorder (bool): Comparison parameter for exact iterables.
                Validates elements in order or in unordered way.
            max_message_count (int): Number of messages to collect before
                terminating connection
            node_filter (str): Filter received messages based on node ID

        Raises:
            RuntimeError: If no MQTT messages were collected.
            RuntimeError: If an issue was encountered during the data
                comparison.

        Returns:
            (bool): True if the MQTT connection, message gathering and data
                comparison were performed correctly.
        """
        main_queue: Queue = Queue()
        messages_remote_path = f"{self.FUT_DIR}/{self.MQTT_MESSAGES_FILE}"
        messages_local_path = f"{self.FUT_BASE_DIR}/{self.MQTT_MESSAGES_FILE}"
        server_mqtt_args_base = [
            f"--hostname {self.MQTT_HOSTNAME}",
            f"--port {self.MQTT_PORT}",
            f"--topic {topic}",
            "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
            f"--max_message_count {max_message_count}",
            "--collect_messages",
            "--stdout_output",
            f"--json_output {messages_remote_path}",
        ]

        mqtt_timeout = kwargs.pop("mqtt_timeout", None)
        if mqtt_timeout:
            server_mqtt_args_base += [
                f"--timeout {mqtt_timeout}",
            ]
        if node_filter:
            server_mqtt_args_base += [
                f"--node_filter {node_filter}",
            ]

        server_mqtt_args = get_command_arguments(*server_mqtt_args_base)

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
            self.get_file(messages_remote_path, self.FUT_BASE_DIR, create_dir=False)
            with open(messages_local_path, "r") as mqtt_file:
                mqtt_messages = json.load(mqtt_file)
            # Extract required data from MQTT messages
            extracted_data = extract_mqtt_data_as_dict(
                mqtt_messages,
                expected_data.keys(),
                simplify=True,
                unique=unique_data,
            )
            print_allure(f"The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}")
        with step("Testcase"):
            if comparison_method == "exact_match":
                data_comparison = check_if_dicts_match(expected_data, extracted_data, inorder)
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
