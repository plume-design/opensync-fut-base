import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def ltem_setup(request: pytest.FixtureRequest):
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
            setup_args = get_command_arguments("wwan0", "data.icore.name", "true")
            gw_handler.device_test_setup(test_suite_name=manager_name, setup_args=setup_args)
    yield


def test_ltem_force_lte(ltem_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        lte_if_name = parametrized_test_config.get("lte_if_name")
        test_args = get_command_arguments(
            lte_if_name,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/ltem/ltem_force_lte", test_args)[0] == 0


def test_ltem_validation(ltem_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        access_point_name = parametrized_test_config.get("access_point_name")
        has_l2 = parametrized_test_config.get("has_l2")
        has_l3 = parametrized_test_config.get("has_l3")
        if_type = parametrized_test_config.get("if_type")
        lte_if_name = parametrized_test_config.get("lte_if_name")
        metric = parametrized_test_config.get("metric")
        route_tool_path = parametrized_test_config.get("route_tool_path")

        # Keep the same order of arguments if making any adjustments
        test_args = get_command_arguments(
            lte_if_name,
            if_type,
            access_point_name,
            has_l2,
            has_l3,
            metric,
            route_tool_path,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/ltem/ltem_validation", test_args)[0] == 0


def test_ltem_verify_table_exists(ltem_setup, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/ltem/ltem_verify_table_exists")[0] == 0
