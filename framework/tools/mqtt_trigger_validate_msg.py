"""Module used to trigger and inspect MQTT message.

Its purpose is to ease the testing and inspection procedure for MQTT messages.
By calling the 'fut_mqtt_trigger_validate_message' function, which
would determine run the MQTT tool on server in background, run the 'trigger' method we pass it from test definition
in *_test.py file and inspect the gathere MQTT message if it matches expected_data we provide.
"""

import json
import time
from queue import Queue
from threading import Thread

import pytest

import framework.tools.logger
from framework.tools.functions import check_if_dicts_match, FailedException, get_command_arguments, output_to_json, \
    print_allure, step
from framework.tools.fut_mqtt_tool import extract_mqtt_data_as_dict
from test.globals import ExpectedShellResult

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


def fut_mqtt_trigger_validate_message(
        topic,
        trigger,
        expected_data,
):
    server_handler = pytest.server_handler

    # MQTT configuration
    mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
    mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
    mqtt_timeout = 60
    mqtt_max_message_count = 1

    server_mqtt_args = get_command_arguments(
        f'--hostname {mqtt_hostname}',
        f'--port {mqtt_port}',
        f'--topic {topic}',
        "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
        f'--max_message_count {mqtt_max_message_count}',
        f'--timeout {mqtt_timeout}',
        f'--collect_messages {True}',
        f'--stdout_output {True}',
        f'--json_output {True}',
    )

    main_queue = Queue()

    # 6. Verify DNS plugin on Client
    def _start_mqtt_listener():
        log.debug('Running FUT-MQTT-TOOL')
        try:
            res = server_handler.run_raw('tools/fut_mqtt_tool', server_mqtt_args, folder='framework', ext='.py', do_mqtt_log=True, device_log_for=['dut'], timeout=mqtt_timeout + 5)
        except Exception as e:
            log.debug(50 * '$')
            log.exception(e)
        log.debug('Response from FUT-MQTT-TOOL')
        log.debug(res)
        main_queue.put(res)

    thread = Thread(target=_start_mqtt_listener, args=())
    thread.start()
    time.sleep(2)
    # Run trigger method
    trigger()
    # Wait for MQTT thread
    thread.join()
    time.sleep(1)
    _mqtt_listener_thread_res = main_queue.get(timeout=5)
    if _mqtt_listener_thread_res[0] != ExpectedShellResult or _mqtt_listener_thread_res[1] == '' or _mqtt_listener_thread_res[1] is None:
        raise FailedException('Failed to collect MQTT messages')
    with step('Data extraction'):
        # Access collected MQTT messages
        with open('/tmp/mqtt_messages.json', 'r') as mqtt_file:
            mqtt_messages = json.load(mqtt_file)
        # Extract required data from MQTT messages
        extracted_data = extract_mqtt_data_as_dict(mqtt_messages, expected_data.keys(), simplify=True)
        print_allure(f'The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}')
    with step('Testcase'):
        data_comparison = check_if_dicts_match(expected_data, extracted_data)
        if data_comparison is True:
            print_allure(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \nmatches the expected data: \n{output_to_json(expected_data, convert_only=True)}')
        else:
            raise FailedException(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \n does not match the expected data \n{output_to_json(expected_data, convert_only=True)} \nfor the following keys: {data_comparison}')
    return True
