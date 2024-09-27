import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
wpd_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def wpd_setup():
    test_class_name = ["TestWpd"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for WPD: {nodes + clients}")
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "CONFIG_WPD_ENABLED=y" not in node_handler.get_kconfig():
            pytest.skip("WPD not enabled on device")
        node_handler.fut_device_setup(test_suite_name="wpd")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)
    kconfig = pytest.gw.get_kconfig()
    dconfig = dict(item.split("=", 1) for item in kconfig)
    """stop pinging watchdog if there is no ping from external applications for the last x seconds"""
    pytest.gw.wpd_ping_timeout = int(dconfig["CONFIG_WPD_PING_TIMEOUT"])  # 60
    """set the HW watchdog to bite after x seconds if there is no ping from wpd"""
    pytest.gw.wpd_watchdog_timeout = int(dconfig["CONFIG_WPD_WATCHDOG_TIMEOUT"])  # 30


class TestWpd:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wpd_config.get("wpd_check_flags", []))
    def test_wpd_check_flags(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            log_tail_command = gw._get_log_tail_command()
            sys_log_file_name = gw.capabilities.device_capabilities.get("frv_sanity").get("sys_log_file_name")
            setup_args = gw.get_command_arguments(sys_log_file_name)
            test_args = gw.get_command_arguments(log_tail_command)
            boot_time_kpi = gw.capabilities.get_boot_time_kpi()

        with step("Rotating system logs"):
            assert gw.execute("tools/device/syslog_rotate", setup_args)[0] == ExpectedShellResult

        try:
            with step("Test Case"):
                pre_uptime = gw.device_api.lib.get_stdout(gw.device_api.lib.uptime(out_format="timestamp"))
                assert gw.execute("tests/wpd/wpd_check_flags", test_args, skip_rcn=True)[0] == ExpectedShellResult
                log.info(f"Ensuring device is online within {max(boot_time_kpi, 120)}s")
                wait_ret = gw.device_api.lib.wait_available(timeout=max(boot_time_kpi, 120))
                assert (
                    wait_ret[0] == ExpectedShellResult
                ), f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
                log.info("Device is online.")
                log.info("Ensuring device was not restarted.")
                post_uptime = gw.device_api.lib.get_stdout(gw.device_api.lib.uptime(out_format="timestamp"))
                assert float(post_uptime) > float(pre_uptime)
        finally:
            gw.device_api.lib.wait_available(timeout=max(boot_time_kpi, 120))
            gw.check_fut_file_transfer()
            gw.execute("tests/wpd/wpd_cleanup")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wpd_config.get("wpd_stop_opensync", []))
    def test_wpd_stop_opensync(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            log_tail_command = gw._get_log_tail_command()
            sys_log_file_name = gw.capabilities.device_capabilities.get("frv_sanity").get("sys_log_file_name")
            setup_args = gw.get_command_arguments(sys_log_file_name)
            test_args = gw.get_command_arguments(gw.wpd_ping_timeout, log_tail_command)
            boot_time_kpi = gw.capabilities.get_boot_time_kpi()

        with step("Rotating system logs"):
            assert gw.execute("tools/device/syslog_rotate", setup_args)[0] == ExpectedShellResult

        try:
            with step("Test Case"):
                pre_uptime = gw.device_api.lib.get_stdout(gw.device_api.lib.uptime(out_format="timestamp"))
                assert gw.execute("tests/wpd/wpd_stop_opensync", test_args, skip_rcn=True)[0] == ExpectedShellResult
                log.info(f"Ensuring device is online within {max(boot_time_kpi, 120)}s")
                wait_ret = gw.device_api.lib.wait_available(timeout=max(boot_time_kpi, 120))
                assert (
                    wait_ret[0] == ExpectedShellResult
                ), f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
                log.info("Device is online.")
                log.info("Ensuring device was not restarted.")
                post_uptime = gw.device_api.lib.get_stdout(gw.device_api.lib.uptime(out_format="timestamp"))
                assert float(post_uptime) > float(pre_uptime)
        finally:
            gw.device_api.lib.wait_available(timeout=max(boot_time_kpi, 120))
            gw.check_fut_file_transfer()
            gw.execute("tests/wpd/wpd_cleanup")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", wpd_config.get("wpd_stop_wpd", []))
    def test_wpd_stop_wpd(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            test_args = gw.get_command_arguments(gw.wpd_watchdog_timeout)
            boot_time_kpi = gw.capabilities.get_boot_time_kpi()

        try:
            with step("Test Case"):
                pre_uptime = gw.device_api.lib.get_stdout(gw.device_api.lib.uptime(out_format="timestamp"))
                assert (
                    gw.execute_with_logging("tests/wpd/wpd_stop_wpd", test_args, skip_rcn=True)[0]
                    == ExpectedShellResult
                )
                log.info(f"Ensure enough time ({max(boot_time_kpi, 120)}s) for system watchdog to reset the system.")
                waitu_ret = gw.device_api.lib.wait_unavailable(timeout=max(boot_time_kpi, 120))
                log.info(f"stdout:{waitu_ret[1]}, stderr:{waitu_ret[2]}")
                assert (
                    waitu_ret[0] == ExpectedShellResult
                ), f"wait_unavailable failed: stdout:{waitu_ret[1]}, stderr:{waitu_ret[2]}."
                log.info("Device is offline.")
                log.info(f"Ensuring device is online within {max(boot_time_kpi, 120)}s")
                wait_ret = gw.device_api.lib.wait_available(timeout=max(boot_time_kpi, 120))
                assert (
                    wait_ret[0] == ExpectedShellResult
                ), f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
                log.info("Device is online.")
                log.info("Ensuring device was restarted.")
                post_uptime = gw.device_api.lib.get_stdout(gw.device_api.lib.uptime(out_format="timestamp"))
                assert float(post_uptime) < float(pre_uptime)
        finally:
            gw.device_api.lib.wait_available(timeout=max(boot_time_kpi, 120))
            gw.check_fut_file_transfer()
            gw.execute("tests/wpd/wpd_cleanup")
