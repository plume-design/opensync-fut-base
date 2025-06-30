from random import randrange

import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def tpsm_setup(request: pytest.FixtureRequest):
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

            if gw_handler.node_service_status[manager_name]["status"] != "enabled":
                pytest.skip(f"{manager_name.upper()} not enabled on device")

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


def test_tpsm_crash_speedtest_verify_reporting(tpsm_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        test_type = parametrized_test_config.get("test_type")
        testid = randrange(100, 1000)
        other_cfg = parametrized_test_config.get("other_cfg")
        test_args = get_command_arguments(
            f"-test_type {test_type}",
            f"-testid {testid}",
            " ".join(f"-{item} {other_cfg[item]}" for item in other_cfg),
        )
    try:
        if test_type == "IPERF3_C":
            with step("Setup"):
                assert server_handler.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == 0
                assert server_handler.execute("tools/server/run_iperf3_server", as_sudo=True)[0] == 0
        with step("Test case"):
            assert (
                gw_handler.execute_with_logging("tests/tpsm/tpsm_crash_speedtest_verify_reporting", test_args)[0] == 0
            )
    finally:
        with step("Cleanup"):
            if test_type == "IPERF3_C":
                assert server_handler.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == 0


def test_tpsm_verify_iperf3_speedtest(tpsm_setup, parametrized_test_config, server_handler, gw_handler, switch_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        server_ip_addr = server_handler.MQTT_HOSTNAME
        testid = randrange(100, 1000)
        upd = parametrized_test_config.get("upd")
        direction = parametrized_test_config.get("direction")
        test_args = get_command_arguments(server_ip_addr, testid, upd, direction)

    try:
        with step("Ensure correct switch VLAN configuration"):
            vlan_name, vlan_id = switch_handler.get_connection_ip_type("gw")
            if (vlan_name, vlan_id) != ("ipv4", "200"):
                switch_handler.set_connection_ip_type("gw", "ipv4")
        with step("Start iperf3 server"):
            assert server_handler.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == 0
            assert server_handler.execute("tools/server/run_iperf3_server", as_sudo=True)[0] == 0
        with step("Test case"):
            assert gw_handler.execute_with_logging("tests/tpsm/tpsm_verify_iperf3_speedtest", test_args)[0] == 0
    finally:
        with step("Cleanup"):
            assert server_handler.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == 0


def test_tpsm_verify_ookla_speedtest(tpsm_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        testid = randrange(100, 1000)
        test_args = get_command_arguments(
            testid,
        )

    with step("Ensure WAN connectivity"):
        assert gw_handler.check_wan_connectivity()
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest", test_args)[0] == 0


def test_tpsm_verify_ookla_speedtest_bind_options(tpsm_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        testid = randrange(100, 1000)
        test_args = get_command_arguments(
            testid,
        )

    with step("Ensure WAN connectivity"):
        assert gw_handler.check_wan_connectivity()
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest_bind_options", test_args)[0] == 0


def test_tpsm_verify_ookla_speedtest_bind_reporting(tpsm_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        testid = randrange(100, 1000)
        test_args = get_command_arguments(
            testid,
        )

    with step("Ensure WAN connectivity"):
        assert gw_handler.check_wan_connectivity()
    with step("Test case"):
        assert (
            gw_handler.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest_bind_reporting", test_args)[0] == 0
        )


def test_tpsm_verify_ookla_speedtest_sdn_endpoint_config(tpsm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        speedtest_config_path = parametrized_test_config.get("speedtest_config_path")
        test_args = get_command_arguments(
            speedtest_config_path,
        )

    with step("Ensure WAN connectivity"):
        assert gw_handler.check_wan_connectivity()
    with step("Test case"):
        assert (
            gw_handler.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest_sdn_endpoint_config", test_args)[0]
            == 0
        )


def test_tpsm_verify_samknows_process(tpsm_setup, parametrized_test_config, gw_handler):
    try:
        with step("Test case"):
            assert gw_handler.execute_with_logging("tests/tpsm/tpsm_verify_samknows_process")[0] == 0
    finally:
        with step("Cleanup"):
            assert gw_handler.execute_with_logging("tests/tpsm/tpsm_samknows_process_cleanup")[0] == 0
