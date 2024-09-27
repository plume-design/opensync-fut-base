from random import randrange

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
tpsm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def tpsm_setup():
    test_class_name = ["TestTpsm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for TPSM: {nodes + clients}")
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "TPSM" not in node_handler.get_kconfig_managers():
            # Do not pytest.skip(), rather log.debug(). Tests are backward-compatible as standalone or managed by TPSM
            log.debug("TPSM not present on device")
        phy_radio_ifnames = node_handler.capabilities.get_phy_radio_ifnames(return_type=list)
        setup_args = node_handler.get_command_arguments(*phy_radio_ifnames)
        node_handler.fut_device_setup(test_suite_name="tpsm", setup_args=setup_args)
        service_status = node_handler.get_node_services_and_status()
        if "TPSM" not in node_handler.get_kconfig_managers():
            pass
        elif service_status["tpsm"]["status"] != "enabled":
            pytest.skip("TPSM not enabled on device")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestTpsm:
    def iperf3_server(self, action):
        if "setup" in action.lower():
            assert pytest.server.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == ExpectedShellResult
            assert pytest.server.execute("tools/server/run_iperf3_server", as_sudo=True)[0] == ExpectedShellResult
        elif "cleanup" in action.lower():
            assert pytest.server.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == ExpectedShellResult
        else:
            raise RuntimeError(f"Unsupported action {action}.")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_crash_speedtest_verify_reporting", []))
    def test_tpsm_crash_speedtest_verify_reporting(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            test_type = cfg.get("test_type")
            testid = randrange(100, 1000)
            other_cfg = cfg.get("other_cfg")
            extra_step = cfg.get("extra_step")
            test_args = gw.get_command_arguments(
                f"-test_type {test_type}",
                f"-testid {testid}",
                " ".join(f"-{item} {other_cfg[item]}" for item in other_cfg),
            )
        try:
            if extra_step is not None:
                setup_fnc = getattr(self, extra_step)
                with step("Setup"):
                    setup_fnc("Setup")
            with step("Test case"):
                assert (
                    gw.execute_with_logging("tests/tpsm/tpsm_crash_speedtest_verify_reporting", test_args)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                if extra_step is not None:
                    setup_fnc("Cleanup")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_verify_iperf3_speedtest", []))
    def test_tpsm_verify_iperf3_speedtest(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            server_ip_addr = server.mqtt_hostname
            testid = randrange(100, 1000)
            upd = cfg.get("upd")
            direction = cfg.get("direction")
            test_args = gw.get_command_arguments(server_ip_addr, testid, upd, direction)

        try:
            with step("Start iperf3 server"):
                assert server.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == ExpectedShellResult
                assert server.execute("tools/server/run_iperf3_server", as_sudo=True)[0] == ExpectedShellResult
            with step("Test case"):
                assert (
                    gw.execute_with_logging("tests/tpsm/tpsm_verify_iperf3_speedtest", test_args)[0]
                    == ExpectedShellResult
                )
        finally:
            with step("Cleanup"):
                assert server.execute("tools/server/stop_iperf3_server", as_sudo=True)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_verify_ookla_speedtest", []))
    def test_tpsm_verify_ookla_speedtest(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            testid = randrange(100, 1000)
            test_args = gw.get_command_arguments(
                testid,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_verify_ookla_speedtest_bind_options", []))
    def test_tpsm_verify_ookla_speedtest_bind_options(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            testid = randrange(100, 1000)
            test_args = gw.get_command_arguments(
                testid,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest_bind_options", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_verify_ookla_speedtest_bind_reporting", []))
    def test_tpsm_verify_ookla_speedtest_bind_reporting(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            testid = randrange(100, 1000)
            test_args = gw.get_command_arguments(
                testid,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest_bind_reporting", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_verify_ookla_speedtest_sdn_endpoint_config", []))
    def test_tpsm_verify_ookla_speedtest_sdn_endpoint_config(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            speedtest_config_path = cfg.get("speedtest_config_path")
            test_args = gw.get_command_arguments(
                speedtest_config_path,
            )

        with step("Ensure WAN connectivity"):
            assert gw.check_wan_connectivity()
        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/tpsm/tpsm_verify_ookla_speedtest_sdn_endpoint_config", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", tpsm_config.get("tpsm_verify_samknows_process", []))
    def test_tpsm_verify_samknows_process(self, cfg: dict):
        gw = pytest.gw

        try:
            with step("Test case"):
                assert gw.execute_with_logging("tests/tpsm/tpsm_verify_samknows_process")[0] == ExpectedShellResult
        finally:
            with step("Cleanup"):
                assert gw.execute_with_logging("tests/tpsm/tpsm_samknows_process_cleanup")[0] == ExpectedShellResult
