import pytest

from framework.lib.fut_lib import reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def cpm_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = module_name.lower()
            if "CAPTIVEPORTAL" not in gw_handler.kconfig_managers:
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


def test_cpm_default_listen_ip_port(cpm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cpm/cpm_default_listen_ip_port")[0] == 0


def test_cpm_delete_while_restarting(cpm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cpm/cpm_delete_while_restarting")[0] == 0


def test_cpm_restart_crashed(cpm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cpm/cpm_restart_crashed")[0] == 0


def test_cpm_same_ip_port(cpm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cpm/cpm_same_ip_port")[0] == 0


def test_cpm_spawn_three_update_one(cpm_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cpm/cpm_spawn_three_update_one")[0] == 0
