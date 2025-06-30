import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def pm_setup(request: pytest.FixtureRequest):
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


def test_pm_verify_log_severity(pm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        test_args = get_command_arguments(
            parametrized_test_config.get("name"),
            parametrized_test_config.get("log_severity"),
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/pm/pm_verify_log_severity", test_args)[0] == 0


def test_pm_trigger_cloud_logpull(pm_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        logread_command = gw_handler.capabilities.get_logread_command()
        assert (
            logread_command != "" and logread_command is not None
        ), "Logread command is empty, check model properties file"
        # Arguments from test case configuration
        test_args = get_command_arguments(
            parametrized_test_config.get("upload_location"),
            parametrized_test_config.get("upload_token"),
            parametrized_test_config.get("name"),
            logread_command,
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/pm/pm_trigger_cloud_logpull", test_args)[0] == 0
