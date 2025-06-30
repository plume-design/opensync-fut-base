import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step


@pytest.fixture(scope="module")
def brv_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = "dm"
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


def test_brv_busybox_builtins(brv_setup, test_config, gw_handler):
    results: dict = {}

    for cfg in test_config:
        with step(f"Test case, cfg={cfg}"):
            busybox_builtin = cfg.get("busybox_builtin")
            test_args = get_command_arguments(busybox_builtin)
            result = gw_handler.execute("tests/dm/brv_busybox_builtins", test_args)
            results[busybox_builtin] = result

    with step("Assertion"):
        exit_code_set = {exit_code for exit_code, stdout, stderr in results.values()}
        assert exit_code_set == {
            0,
        }, f"Failing steps: {[config for config, result in results.items() if result[0] != 0]}\n"


def test_brv_is_bcm_license_on_system_fut(brv_setup, test_config, gw_handler):
    results: dict = {}

    if gw_handler.capabilities.get_wifi_vendor() != "bcm":
        pytest.skip(
            f"Test of BCM is not applicable when device Wi-Fi vendor is {gw_handler.capabilities.get_wifi_vendor()}, skipping the test.",
        )

    for cfg in test_config:
        license_cmd = cfg.get("license_cmd")
        if license_cmd:
            license_name = "/tmp/bcm_licence_by_fut_license_cmd"
            with step(f"Using license_cmd={license_cmd} to create license_file={license_name}"):
                result = gw_handler.run_raw(f"{license_cmd} > {license_name}")
                results[license_cmd] = result
        else:
            license_name = cfg.get("license")
        with step(f"Test case, cfg={cfg}"):
            service_name = cfg.get("service")
            test_args = get_command_arguments(
                f"{license_name}",
                f"'{service_name}'",
            )
            result = gw_handler.execute("tests/dm/brv_is_bcm_license_on_system", test_args)
            results[service_name] = result

    with step("Assertion"):
        exit_code_set = {exit_code for exit_code, stdout, stderr in results.values()}
        assert exit_code_set == {
            0,
        }, f"Failing steps: {[config for config, result in results.items() if result[0] != 0]}\n"


def test_brv_is_script_on_system_fut(brv_setup, test_config, gw_handler):
    results: dict = {}

    for cfg in test_config:
        with step(f"Test case, cfg={cfg}"):
            system_script = cfg.get("system_script")
            test_args = get_command_arguments(system_script)
            result = gw_handler.execute("tests/dm/brv_is_script_on_system", test_args)
            results[system_script] = result

    with step("Assertion"):
        exit_code_set = {exit_code for exit_code, stdout, stderr in results.values()}
        assert exit_code_set == {
            0,
        }, f"Failing steps: {[config for config, result in results.items() if result[0] != 0]}\n"


def test_brv_is_tool_on_system(brv_setup, full_test_config, gw_handler):
    results: dict = {}
    common_config: list = []
    common_config_keys = ["brv_is_tool_on_system_fut", "brv_is_tool_on_system_opensync"]

    if gw_handler.bridge_type == "ovs_bridge":
        merge_keys = common_config_keys + ["brv_is_tool_on_system_ovs_bridge"]
    elif gw_handler.bridge_type == "native_bridge":
        merge_keys = common_config_keys + ["brv_is_tool_on_system_native_bridge"]
    else:
        merge_keys = common_config_keys

    for key in merge_keys:
        common_config.extend(full_test_config.get(key, []))

    for cfg in common_config:
        with step(f"Test case, cfg={cfg}"):
            system_tool = cfg.get("system_tool")
            test_args = get_command_arguments(system_tool)
            result = gw_handler.execute("tests/dm/brv_is_tool_on_system", test_args)
            results[system_tool] = result

    with step("Assertion"):
        exit_code_set = {exit_code for exit_code, stdout, stderr in results.values()}
        assert exit_code_set == {
            0,
        }, f"Failing steps: {[config for config, result in results.items() if result[0] != 0]}\n"


def test_brv_ovs_check_version(brv_setup, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "ovs_bridge":
            pytest.skip(
                "Test is not applicable when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Test Case"):
        assert gw_handler.execute("tests/dm/brv_ovs_check_version")[0] == 0
