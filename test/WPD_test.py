import time

import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.logger import log

wpd_ping_timeout: int = 0
wpd_watchdog_timeout: int = 0


@pytest.fixture(scope="module")
def wpd_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = module_name.lower()
            kconfig = gw_handler.kconfig
            if "CONFIG_WPD_ENABLED=y" not in kconfig:
                pytest.skip(f"{manager_name.upper()} not present on device")

            dconfig = dict(item.split("=", 1) for item in kconfig)
            global wpd_ping_timeout, wpd_watchdog_timeout
            """stop pinging watchdog if there is no ping from external applications for the last x seconds"""
            wpd_ping_timeout = int(dconfig["CONFIG_WPD_PING_TIMEOUT"])
            """set the HW watchdog to bite after x seconds if there is no ping from wpd"""
            wpd_watchdog_timeout = int(dconfig["CONFIG_WPD_WATCHDOG_TIMEOUT"])

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


def test_wpd_check_flags(wpd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        log_tail_command = gw_handler._get_log_tail_command()
        sys_log_file_name = gw_handler.capabilities.device_capabilities.get("frv_sanity").get("sys_log_file_name")
        setup_args = get_command_arguments(sys_log_file_name)
        test_args = get_command_arguments(log_tail_command)
        reboot_time = gw_handler.reboot_time

    with step("Rotating system logs"):
        assert gw_handler.execute("tools/device/syslog_rotate", setup_args)[0] == 0

    try:
        with step("Test Case"):
            pre_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            if float(pre_uptime) < float(reboot_time):
                add_sleep = float(reboot_time) - float(pre_uptime)
                log.debug(f"Uptime ({pre_uptime}s) is low, wait for an additional {add_sleep}s.")
                time.sleep(int(add_sleep))
                pre_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            assert gw_handler.execute("tests/wpd/wpd_check_flags", test_args, retry=False)[0] == 0
            log.info(f"Ensuring device is online within {reboot_time}s")
            wait_ret = gw_handler.lib.wait_available(timeout=reboot_time)
            assert wait_ret[0] == 0, f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
            log.info("Device is online.")
            log.info("Ensuring device was not restarted.")
            post_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            assert float(post_uptime) > float(pre_uptime)
    finally:
        gw_handler.lib.wait_available(timeout=reboot_time)
        gw_handler.check_fut_files()
        gw_handler.execute("tests/wpd/wpd_cleanup")


def test_wpd_stop_opensync(wpd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        log_tail_command = gw_handler._get_log_tail_command()
        sys_log_file_name = gw_handler.capabilities.device_capabilities.get("frv_sanity").get("sys_log_file_name")
        setup_args = get_command_arguments(sys_log_file_name)
        test_args = get_command_arguments(wpd_ping_timeout, log_tail_command)
        reboot_time = gw_handler.reboot_time

    with step("Rotating system logs"):
        assert gw_handler.execute("tools/device/syslog_rotate", setup_args)[0] == 0

    try:
        with step("Test Case"):
            pre_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            if float(pre_uptime) < float(reboot_time):
                add_sleep = float(reboot_time) - float(pre_uptime)
                log.debug(f"Uptime ({pre_uptime}s) is low, wait for an additional {add_sleep}s.")
                time.sleep(int(add_sleep))
                pre_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            assert gw_handler.execute("tests/wpd/wpd_stop_opensync", test_args, retry=False)[0] == 0
            log.info(f"Ensuring device is online within {reboot_time}s")
            wait_ret = gw_handler.lib.wait_available(timeout=reboot_time)
            assert wait_ret[0] == 0, f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
            log.info("Device is online.")
            log.info("Ensuring device was not restarted.")
            post_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            assert float(post_uptime) > float(pre_uptime)
    finally:
        gw_handler.lib.wait_available(timeout=reboot_time)
        gw_handler.check_fut_files()
        gw_handler.execute("tests/wpd/wpd_cleanup")


def test_wpd_stop_wpd(wpd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        test_args = get_command_arguments(wpd_watchdog_timeout)
        reboot_time = gw_handler.reboot_time

    try:
        with step("Test Case"):
            pre_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            if float(pre_uptime) < float(reboot_time):
                add_sleep = float(reboot_time) - float(pre_uptime)
                log.debug(f"Uptime ({pre_uptime}s) is low, wait for an additional {add_sleep}s.")
                time.sleep(int(add_sleep))
                pre_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            assert gw_handler.execute_with_logging("tests/wpd/wpd_stop_wpd", test_args, retry=False)[0] == 0
            log.info(f"Ensure enough time ({reboot_time}s) for system watchdog to reset the system.")
            waitu_ret = gw_handler.lib.wait_unavailable(timeout=reboot_time)
            log.info(f"stdout:{waitu_ret[1]}, stderr:{waitu_ret[2]}")
            assert waitu_ret[0] == 0, f"wait_unavailable failed: stdout:{waitu_ret[1]}, stderr:{waitu_ret[2]}."
            log.info("Device is offline.")
            log.info(f"Ensuring device is online within {reboot_time}s")
            wait_ret = gw_handler.lib.wait_available(timeout=reboot_time)
            assert wait_ret[0] == 0, f"wait_available failed: stdout:{wait_ret[1]}, stderr:{wait_ret[2]}."
            log.info("Device is online.")
            log.info("Ensuring device was restarted.")
            post_uptime = gw_handler.lib.get_stdout(gw_handler.lib.uptime(out_format="timestamp"))
            assert float(post_uptime) < float(pre_uptime)
    finally:
        gw_handler.lib.wait_available(timeout=reboot_time)
        gw_handler.check_fut_files()
        gw_handler.execute("tests/wpd/wpd_cleanup")
