from pathlib import Path

import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def fsm_setup(request: pytest.FixtureRequest):
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


def test_fsm_configure_fsm_tables(fsm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        tap_name_postfix = parametrized_test_config.get("tap_name_postfix")
        handler = parametrized_test_config.get("handler")
        plugin = parametrized_test_config.get("plugin")

        # GW specific arguments
        opensync_rootdir = gw_handler.capabilities.get_opensync_rootdir()
        lan_bridge_if_name = gw_handler.capabilities.get_lan_bridge_ifname()

        fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
        test_args = get_command_arguments(
            lan_bridge_if_name,
            tap_name_postfix,
            handler,
            fsm_plugin_path.as_posix(),
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/fsm/fsm_configure_fsm_tables", test_args)[0] == 0


def test_fsm_configure_openflow_rules(fsm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        action = parametrized_test_config.get("action")
        rule = parametrized_test_config.get("rule")
        token = parametrized_test_config.get("token")

        # GW specific arguments
        lan_bridge_if_name = gw_handler.capabilities.get_lan_bridge_ifname()

        test_args = get_command_arguments(
            lan_bridge_if_name,
            action,
            rule,
            token,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/fsm/fsm_configure_of_rules", test_args)[0] == 0
