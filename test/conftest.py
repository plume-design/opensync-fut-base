from enum import Enum

import pytest

from framework.lib.fut_lib import determine_required_devices
from framework.tools import fut_setup
from lib_testbed.generic.util.logger import log


pytest.expected_shell_result = 0


def pytest_addoption(parser):
    parser.addoption(
        "--run_test",
        type=str,
        action="store",
        default=False,
        help="Specify which test to run. To run multiple, separate them with a comma without any additional spaces.",
    )


def pytest_collection_modifyitems(session, config, items):
    def _get_item_config(item):
        try:
            tcc = item._request.node.callspec.params
            if isinstance(tcc, Enum):
                return {}
            if "cfg" in tcc:
                if isinstance(tcc["cfg"], Enum):
                    return {}
                return tcc["cfg"]
            return tcc
        except Exception:
            return {}

    tests_to_run, class_mapping = [], []

    if config.getoption("--run_test"):
        specified_tc_list = config.getoption("--run_test").split(",")
        for item in items:
            tc_name, sep, tc_tail = item.name.partition("[")
            if tc_name in specified_tc_list:
                tests_to_run.append(item)
    else:
        tests_to_run = items

    for item in tests_to_run:
        # Get a list of all parent nodes - used for determining device requirements
        class_mapping.append(item.cls.__name__)
        test_case_configuration = _get_item_config(item)
        if test_case_configuration.get("xfail"):
            item.add_marker(pytest.mark.xfail(reason=test_case_configuration.get("xfail_msg")))

    # Remove duplicated values in the class_mapping list
    config.test_suites = list(set(class_mapping))

    items[:] = tests_to_run


@pytest.fixture(autouse=True, scope="session")
def setup(request):
    try:
        log.info("Entered FUT setup fixture.")
        test_suites = request.config.test_suites
        required_nodes, required_clients = determine_required_devices(test_suites)
        fut_setup.pre_test_device_setup(node_devices=required_nodes, client_devices=required_clients)
    except Exception as exception:
        raise RuntimeError(f"Failed to perform FUT setup: {exception}")


def pytest_sessionfinish(session, exitstatus):
    log.info("Performing docker container cleanup on the server device")
    server = pytest.server
    try:
        assert server.execute("server_docker_cleanup", suffix=".py", folder="docker/server")[0] == 0
    except Exception as exception:
        log.warning(f"Unable to perform docker container cleanup on the server device: {exception}")
