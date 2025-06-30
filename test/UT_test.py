from pathlib import Path

import pytest

from config.defaults import unit_test_resource_dir, unit_test_subdir
from framework.lib.fut_lib import reboot_pods_and_wait_available, step
from lib_testbed.generic.util.logger import log


@pytest.fixture(scope="module")
def ut_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"OpenSync firmware {module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = "nm"
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
            transfer_dir = Path(unit_test_resource_dir).joinpath(unit_test_subdir)
            if not transfer_dir.is_dir():
                raise FileNotFoundError(
                    f"Can not transfer {transfer_dir} to {gw_handler.nickname}, directory does not exist.",
                )
            log.debug(f"Transfer {transfer_dir} to {gw_handler.nickname}.")
            gw_handler.file_transfer(folders=[transfer_dir], as_sudo=False, skip_env_file=True)
            gw_handler.device_test_setup(test_suite_name=module_name.lower())
    yield


def test_device_unit_test(ut_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        unit_test_file = parametrized_test_config.get("unit_test_file")
    with step("Test case"):
        assert gw_handler.execute(Path(unit_test_file).name, suffix="", folder=Path(unit_test_file).parent)[0] == 0
