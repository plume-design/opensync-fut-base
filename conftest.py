from enum import Enum
from pathlib import Path

import pytest

from config.defaults import unit_test_exec_name, unit_test_resource_dir, unit_test_subdir
from framework.lib.fut_lib import determine_required_devices, find_filename_in_dir, output_to_json, print_allure
from framework.tools import fut_setup
from lib_testbed.generic.util.logger import log


pytest.expected_shell_result = 0
# Global variable that defines the managers which are tracked as part of the OpenSync process restart feature
pytest.tracked_managers = ["dm"]
pytest_plugins = [
    "framework.lib.fut_allure",
]
if Path("internal/pytest_plugins").is_dir():
    pytest_plugins.extend(
        [
            plugin.as_posix().replace("/", ".").removesuffix(".py")
            for plugin in Path("internal/pytest_plugins").glob("*.py")
            if plugin.name != "__init__.py"
        ],
    )


def pytest_addoption(parser):
    parser.addoption(
        "--run_test",
        type=str,
        action="store",
        default=False,
        help="Specify which test to run. To run multiple, separate them with a comma without any additional spaces.",
    )
    parser.addoption(
        "--disable_strict_process_restart_detection",
        action="store_true",
        default=False,
        help="Strict OpenSync restart detection? False (default): strict - exit session. True: not strict - fail test.",
    )


def pytest_sessionstart():
    unit_test_file_list = find_filename_in_dir(
        directory=Path(unit_test_resource_dir).joinpath(unit_test_subdir).as_posix(),
        pattern=unit_test_exec_name,
    )
    unit_test_files = [{"unit_test_file": file} for file in unit_test_file_list]
    if unit_test_files:
        pytest.unit_test_files = unit_test_files


def pytest_collection_modifyitems(config, items):
    def _get_item_config(item):
        try:
            tcc = item._request.node.callspec.params
        except AttributeError:
            return {}
        if isinstance(tcc, Enum):
            return {}
        if "cfg" not in tcc:
            return tcc
        if isinstance(tcc["cfg"], Enum):
            return {}
        return tcc["cfg"]

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
        log.debug("Entered FUT setup fixture.")
        test_suites = request.config.test_suites
        required_nodes, required_clients = determine_required_devices(test_suites)
        fut_setup.pre_test_device_setup(node_devices=required_nodes, client_devices=required_clients)
    except RuntimeError as exception:
        raise RuntimeError(f"Failed to perform FUT setup: {exception}")


@pytest.fixture(scope="function")
def update_baseline_os_pids():
    """
    Update the baseline OpenSync PIDs used for reboot detection.

    The fixture is used in test cases where a reboot is part of the
    test procedure, and the PIDs used in the reboot detection
    process need to be updated.

    Returns:
        None
    """
    yield
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


@pytest.fixture(autouse=True, scope="function")
def process_restart_detection(request):
    """
    Check if OpenSync related PIDs have changed.

    The function checks if the PIDs of OpenSync related processes on
    the device have changed, which would indicate that a reboot has
    happened.

    Returns with no action if requesting function uses marker "no_process_restart_detection"

    Returns:
        None

    """
    yield

    if "no_process_restart_detection" in request.keywords:
        return

    log.debug("Executing process restart detection fixture")
    current_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)

    session_baseline_os_pids = pytest.session_baseline_os_pids.copy()
    baseline_os_proc = sorted(session_baseline_os_pids.keys())
    current_os_proc = sorted(current_os_pids.keys())
    missing_os_pids = {key: session_baseline_os_pids[key] for key in baseline_os_proc if key not in current_os_proc}
    mismatching_os_pids = {
        key: current_os_pids[key]
        for key in current_os_proc
        if key in baseline_os_proc and current_os_pids[key] != session_baseline_os_pids[key]
    }

    # This modifies pytest.session_baseline_os_pids and must be done last, but before failing or exiting pytest
    new_os_pids = {key: current_os_pids[key] for key in current_os_proc if key not in baseline_os_proc}
    if new_os_pids:
        pytest.session_baseline_os_pids.update(new_os_pids)
        print_allure(f"Adding new OpenSync process PIDs to baseline: {new_os_pids}")

    if missing_os_pids or mismatching_os_pids:
        print_allure(
            "\n".join(
                [
                    "Current OpenSync process PIDs:",
                    f"{output_to_json(current_os_pids, convert_only=True)}",
                    "mismatch the baseline OpenSync process PIDs:",
                    f"{output_to_json(session_baseline_os_pids, convert_only=True)}",
                    "Current OpenSync processes with different PID in baseline:",
                    f"{output_to_json(mismatching_os_pids, convert_only=True)}",
                    "Baseline OpenSync processes that are currently missing:",
                    f"{output_to_json(missing_os_pids, convert_only=True)}",
                ],
            ),
        )
        os_restart_msg = "Unexpected OpenSync restart detected."

        if request.config.getoption("disable_strict_process_restart_detection"):
            pytest.session_baseline_os_pids.update(mismatching_os_pids)
            print_allure(f"Updating baseline OpenSync process PIDs: {mismatching_os_pids}")
            pytest.fail(reason=os_restart_msg)
        else:
            pytest.exit(reason=os_restart_msg, returncode=1)


def pytest_sessionfinish():
    try:
        server = pytest.server
        log.info("Performing docker container cleanup on the server device")
        assert server.execute("server_docker_cleanup", suffix=".py", folder="docker/server")[0] == 0
    except AttributeError as exception:
        log.debug(f"Unable to perform docker container cleanup on the server device: {exception}")
    except Exception as exception:
        log.warning(f"Unable to perform docker container cleanup on the server device: {exception}")
