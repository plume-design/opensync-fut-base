from time import sleep

import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.common import compare_fw_versions
from lib_testbed.generic.util.logger import log


@pytest.fixture(scope="module")
def dm_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = module_name.lower()
            if manager_name.upper() not in gw_handler.kconfig_managers:
                pytest.skip(f"{manager_name.upper()} not present on device")

        if "l1_handler" in fixturenames:
            l1_handler = request.getfixturevalue("l1_handler")
            handlers.append(l1_handler)

        if "l2_handler" in fixturenames:
            l2_handler = request.getfixturevalue("l2_handler")
            handlers.append(l2_handler)

        reboot_pods_and_wait_available(handlers)

        if "gw_handler" in fixturenames:
            gw_handler.device_test_setup(test_suite_name=manager_name)
    yield


def test_dm_verify_awlan_node_params(dm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        awlan_field_name = parametrized_test_config.get("awlan_field_name")
        awlan_field_val = parametrized_test_config.get("awlan_field_val")
        test_args = get_command_arguments(
            awlan_field_name,
            awlan_field_val,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_awlan_node_params", test_args)[0] == 0


def test_dm_verify_count_reboot_status(dm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_count_reboot_status")[0] == 0


def test_dm_verify_counter_inc_reboot_status(dm_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        reboot_time = gw_handler.reboot_time

    try:
        with step("Reboot GW"):
            count_before_reboot = gw_handler.execute("tools/device/get_count_reboot_status")
            gw_handler.reboot()
        with step("Wait for GW after reboot"):
            # Hardcoded sleep to allow devices to actually trigger reboot. Do not optimize.
            sleep(20)
            gw_handler.wait_available(timeout=reboot_time)
            count_after_reboot = gw_handler.execute("tools/device/get_count_reboot_status")
        with step("Test case"):
            test_args = get_command_arguments(
                count_before_reboot[1],
                count_after_reboot[1],
            )
            assert gw_handler.execute_with_logging("tests/dm/dm_verify_counter_inc_reboot_status", test_args)[0] == 0
    finally:
        with step("Wait for GW after reboot"):
            gw_handler.wait_available(timeout=reboot_time)


def test_dm_verify_device_mode_awlan_node(dm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        device_mode = parametrized_test_config.get("device_mode")
        test_args = get_command_arguments(
            device_mode,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_device_mode_awlan_node", test_args)[0] == 0


def test_dm_verify_enable_node_services(dm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        service = parametrized_test_config.get("service")
        kconfig_val = parametrized_test_config.get("kconfig_val")
        wireless_manager_name = gw_handler.wireless_manager

        if service in gw_handler.supported_wireless_managers and service != wireless_manager_name:
            pytest.skip(f"Service {service} not compatible with {wireless_manager_name}, skipping test case.")

        test_args = get_command_arguments(
            service,
            kconfig_val,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_enable_node_services", test_args)[0] == 0


def test_dm_verify_node_services(dm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        service = parametrized_test_config.get("service")
        kconfig_val = parametrized_test_config.get("kconfig_val")
        wireless_manager_name = gw_handler.wireless_manager

        if service in gw_handler.supported_wireless_managers and service != wireless_manager_name:
            pytest.skip(f"Service {service} not compatible with {wireless_manager_name}, skipping test case.")

        test_args = get_command_arguments(
            service,
            kconfig_val,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_node_services", test_args)[0] == 0


def test_dm_verify_opensync_version_awlan_node(dm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_opensync_version_awlan_node")[0] == 0


def test_dm_verify_reboot_file_exists(dm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_reboot_file_exists")[0] == 0


def test_dm_verify_reboot_reason(dm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        opensync_rootdir = gw_handler.capabilities.get_opensync_rootdir()
        reboot_time = gw_handler.reboot_time

        # Arguments from test case configuration
        reboot_reason = parametrized_test_config.get("reboot_reason")

        test_args_base = [
            reboot_reason,
        ]

        if reboot_reason == "CLOUD":
            test_args_base += [
                opensync_rootdir,
            ]

        test_args = get_command_arguments(*test_args_base)

    try:
        with step("Verify GW capability to record reboot reason"):
            if not gw_handler.execute("tools/device/check_reboot_file_exists")[0] == 0:
                pytest.skip("Reboot file does not exist, skipping dm_verify_reboot_reason test case.")
        with step("Reboot GW"):
            if reboot_reason == "COLD_BOOT":
                gw_handler.rpower.cycle(timeout=15)
            else:
                assert gw_handler.execute("tools/device/reboot_dut_w_reason", test_args)[0] == 0
                # Hardcoded sleep to allow devices to actually trigger reboot. Do not optimize.
                sleep(20)
        with step(f"Wait {reboot_time}s for GW after reboot"):
            gw_handler.wait_available(timeout=reboot_time)
            # Allows the device to recover after reboot
            sleep(10)
        with step("Test case"):
            assert gw_handler.execute_with_logging("tests/dm/dm_verify_reboot_reason", test_args)[0] == 0
    finally:
        with step("Wait for GW after reboot"):
            gw_handler.wait_available(timeout=reboot_time)


def test_dm_verify_opensync_restart(dm_setup, parametrized_test_config, server_handler, gw_handler):
    min_opensync_version = "6.7.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    gw_kconfig = gw_handler.kconfig

    if "CONFIG_DM_OSYNC_CRASH_REPORTS=y" not in gw_kconfig:
        pytest.skip("CONFIG_DM_OSYNC_CRASH_REPORTS not enabled on device, skipping test case.")
    if "CONFIG_TARGET_RESTART_SCRIPT=y" not in gw_kconfig:
        pytest.skip("CONFIG_TARGET_RESTART_SCRIPT not enabled on device, skipping test case.")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        crash_name = parametrized_test_config.get("crash_name")
        crash_reason = parametrized_test_config.get("crash_reason")

        # Prepare shell script arguments
        test_args_base = [
            crash_name,
            crash_reason,
        ]

        test_args = get_command_arguments(*test_args_base)

        # Prepare arguments and helpers for inspecting MQTT messages
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"
        mqtt_topic = "Crash/Reports/dm_verify_opensync_restart"
        mqtt_topics_key = "Crash.Reports"

        dm_gw_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
            mqtt_topics_key,
        )

        def _trigger():
            assert gw_handler.execute("tools/device/fut_configure_mqtt", dm_gw_mqtt_cfg_args)[0] == 0

    with step("Trigger OpenSync restart and check if crash file was created on the device"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_opensync_restart", test_args)[0] == 0

    log.info("Waiting 60s for OpenSync to restart")
    sleep(60)

    with step("Restart MQTT broker on server"):
        assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
    with step("Wait for OpenSync restart MQTT messages to be sent"):
        assert server_handler.mqtt_trigger_and_validate_message(
            topic=mqtt_topic,
            trigger=_trigger,
            expected_data={
                "name": crash_name,
                "reason": crash_reason,
            },
            comparison_method="exact_match",
        )


def test_dm_verify_max_memory(dm_setup, parametrized_test_config, server_handler, gw_handler):
    min_opensync_version = "6.7.0.0"
    opensync_version = gw_handler.opensync
    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    gw_kconfig = gw_handler.kconfig
    if "CONFIG_DM_OSYNC_CRASH_REPORTS=y" not in gw_kconfig:
        pytest.skip("CONFIG_DM_OSYNC_CRASH_REPORTS not enabled on device, skipping test case.")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        mem_limit = parametrized_test_config.get("mem_limit")
        proc_name = parametrized_test_config.get("proc_name")

        # Prepare shell script arguments
        test_args_base = [
            mem_limit,
            proc_name,
        ]

        test_args = get_command_arguments(*test_args_base)

        # Parse max_memory value from the Kconfig
        matching_line = next(line for line in gw_kconfig if "CONFIG_MANAGER_OWM_CFG" in line)
        config_values = matching_line.partition("=")
        pairs = config_values[2].strip('"').split(";")
        mem_limit_org = next((pair.partition("=")[2] for pair in pairs if pair.startswith("max_memory=")), None)
        log.debug(f"Original mem limit from kconfig is {mem_limit_org}.")
        if not mem_limit_org:
            raise RuntimeError("Field max_memory is not defined in CONFIG_MANAGER_OWM_CFG.")

        # Prepare arguments and helpers for inspecting MQTT messages
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"
        mqtt_topic = "Crash/Reports/dm_verify_max_memory"
        mqtt_topics_key = "Crash.Reports"

        dm_gw_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
            mqtt_topics_key,
        )

        def _trigger():
            assert gw_handler.execute("tools/device/fut_configure_mqtt", dm_gw_mqtt_cfg_args)[0] == 0

    try:
        with step("Restart MQTT broker on server."):
            assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
        log.debug("Waiting 5 seconds for MQTT to become ready...")
        sleep(5)
        with step("Change the max_memory limit for the specified process and trigger a process abort."):
            assert gw_handler.execute_with_logging("tests/dm/dm_verify_max_memory", test_args)[0] == 0

        with step("Wait for max_memory MQTT messages to be sent."):
            assert server_handler.mqtt_trigger_and_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={"reason": f"Maximum memory limit exceeded ({mem_limit} kB)"},
                comparison_method="exact_match",
            )

    finally:
        test_args_restore = [
            mem_limit_org,
            proc_name,
        ]
        test_args = get_command_arguments(*test_args_restore)
        with step("Restoring max_memory limit."):
            assert gw_handler.execute_with_logging("tests/dm/dm_verify_max_memory", test_args)[0] == 0


def test_dm_verify_no_reboot(dm_setup, gw_handler):
    min_opensync_version = "6.7.0.0"
    opensync_version = gw_handler.opensync
    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    if not dict(item.split("=") for item in gw_handler.kconfig if "CONFIG_NO_REBOOT_DIR" in item):
        pytest.skip("CONFIG_NO_REBOOT_DIR kconfig value not found, skipping test case.")

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/dm/dm_verify_no_reboot")[0] == 0


def test_dm_verify_remote_triggered_reboot(dm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        delayed_reboot_script_path = parametrized_test_config.get("delayed_reboot_script_path")
        test_args = get_command_arguments(delayed_reboot_script_path)
        reboot_time = gw_handler.reboot_time

    try:
        with step("Test Case"):
            pre_uptime = gw_handler.uptime(out_format="timestamp")
            if float(pre_uptime) < float(reboot_time):
                add_sleep = float(reboot_time) - float(pre_uptime) + 20
                log.debug(f"Uptime ({pre_uptime}s) is low, wait for an additional {add_sleep}s.")
                sleep(int(add_sleep))
                pre_uptime = gw_handler.uptime(out_format="timestamp")
            # The script is expected to reboot the device in which case the return code is 255
            # Do not execute_with_logging here, as fetching the device log will fail due to the device rebooting
            assert gw_handler.execute("tests/dm/dm_verify_remote_triggered_reboot", test_args, retry=False)[0] == 255
            # It is prudent to still wait for the device to become unavailable to ensure it has rebooted
            log.info(f"Ensure enough time ({reboot_time}s) for system to reboot.")
            waitu_ret = gw_handler.lib.wait_unavailable(timeout=reboot_time)
            log.info(f"stdout:{waitu_ret[1]}, stderr:{waitu_ret[2]}")
            assert waitu_ret[0] == 0, f"wait_unavailable failed: stdout:{waitu_ret[1]}, stderr:{waitu_ret[2]}."
            log.info("Device is offline.")
            log.info(f"Ensuring device is online within {reboot_time}s")
            wait_ret = gw_handler.lib.wait_available(timeout=reboot_time)
            assert wait_ret[0] == 0, f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
            log.info("Device is online.")
            log.info("Ensuring device was rebooted.")
            post_uptime = gw_handler.uptime(out_format="timestamp")
            log.debug(f"Post uptime: {post_uptime}")
            log.debug(f"Pre uptime: {pre_uptime}")
            assert float(post_uptime) < float(pre_uptime)
            log.info("Checking Reboot_Status table.")
            where_cond = "reason==delayed-reboot -w type==CLOUD"
            uuid = gw_handler.ovsdb.get(
                table="Reboot_Status",
                select="_uuid",
                where=where_cond,
            )
            log.info(f"UUID matching condition '{where_cond}': {uuid}")
            assert uuid is not None and uuid != ""
    finally:
        gw_handler.lib.wait_available(timeout=reboot_time)
        gw_handler.check_fut_files()
