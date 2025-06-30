import json
import os
from pathlib import Path

import allure
import pytest

from framework.generators.fut_gen import FutTestConfigGenClass
from framework.handlers.pod_handler import PodHandler
from framework.lib.fut_fixtures import resolve_pod_obj
from framework.lib.fut_lib import get_testbed_name, read_md_description
from lib_testbed.generic.util.config import load_tb_config

# Global variable that defines the managers which are tracked as part of the OpenSync process restart feature
pytest.tracked_managers = ["dm"]
pytest_plugins = [
    "framework.lib.fut_allure",
    "framework.lib.fut_fixtures",
    "lib_testbed.generic.pytest_plugins.logger_configurator",
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


def _generate_test_configs():
    try:
        testbed_name = os.getenv("OPENSYNC_TESTBED", get_testbed_name())
        testbed_cfg = load_tb_config(location_file=f"{testbed_name}.yaml", skip_deployment=True)
        gw_obj = resolve_pod_obj(name="gw", index=0, config=testbed_cfg, multi_obj=False)
        leaf_obj = resolve_pod_obj(name="l1", index=1, config=testbed_cfg, multi_obj=False)

        gw_handler = PodHandler(**gw_obj)
        leaf_handler = PodHandler(**leaf_obj)

        fut_test_config_generator = FutTestConfigGenClass(
            gw=gw_handler,
            leaf=leaf_handler,
        )

        test_configs = fut_test_config_generator.get_test_configs()

        with open("config/test_case/full_test_config.json", "w") as config_file:
            json.dump(test_configs, config_file, sort_keys=True, indent=4)

        return test_configs
    except RuntimeError as runtime_error:
        raise RuntimeError(f"Failed to generate test configurations: {runtime_error}")


def pytest_collection_modifyitems(config, items):
    """Filter tests based on CLI options."""
    if config.getoption("--run_test"):
        run_test_list = config.getoption("--run_test").split(",")
        filtered_items = []
        for item in items:
            tc_name, _sep, _tc_tail = item.name.partition("[")
            if tc_name in run_test_list:
                filtered_items.append(item)
        items[:] = filtered_items


def pytest_configure(config):
    """Configure pytest options."""
    config.GLOBAL_TEST_CONFIGS = _generate_test_configs()


@pytest.fixture(scope="session")
def full_test_config(pytestconfig):
    return pytestconfig.GLOBAL_TEST_CONFIGS


@pytest.fixture(scope="function")
def test_config(request, pytestconfig):
    test_name = request.node.name.removeprefix("test_")
    return pytestconfig.GLOBAL_TEST_CONFIGS.get(test_name, [])


def _marks_for(cfg: dict) -> list:
    """Create pytest markers for the test configuration."""
    marks = []
    if cfg.get("xfail"):
        marks.append(pytest.mark.xfail(reason=cfg["xfail_msg"]))
    if cfg.get("known_issues"):
        marks.append(pytest.mark.known_issues)
        marks.append(pytest.mark.xfail(reason=cfg["known_issues_msg"]))
    return marks


def pytest_generate_tests(metafunc):
    """Dynamically parametrize tests with generated configurations."""
    if "parametrized_test_config" in metafunc.fixturenames:
        test_name = metafunc.function.__name__.removeprefix("test_")
        test_config = metafunc.config.GLOBAL_TEST_CONFIGS.get(test_name, [])
        parameters = [pytest.param(cfg, marks=_marks_for(cfg)) for cfg in test_config]
        metafunc.parametrize("parametrized_test_config", parameters)


def pytest_runtest_setup(item):
    test_name = getattr(item, "originalname", item.name.partition("[")[0])
    test_name = test_name.removeprefix("test_")
    test_config = item.config.GLOBAL_TEST_CONFIGS.get(test_name, [])
    # For parametrized tests, match the config to the current parameter set
    if hasattr(item, "callspec"):
        config = item.callspec.params.get("parametrized_test_config")
        if not isinstance(config, dict):
            raise TypeError(f"Expected dict for 'parametrized_test_config', got {type(config).__name__}")
    else:
        # Non-parametrized: use the first config, flags are the same for all list items
        config = test_config[0] if len(test_config) > 0 else {}

    # For non-parametrized tests, pytest markers are added to the function object after collection
    for mark in _marks_for(config):
        if mark.name in [mark.name for mark in item.iter_markers()]:
            continue
        # Items need to be added individually to avoid duplicates
        item.add_marker(mark)

    # Apply allure decorators dynamically based on the test configuration
    if ticket := config.get("ticket"):
        allure.dynamic.issue(ticket)
    allure.dynamic.severity(config.get("severity", "normal"))


def pytest_runtest_call(item):
    test_name = getattr(item, "originalname", item.name.partition("[")[0])
    test_name = test_name.removeprefix("test_")
    # Apply allure decorators dynamically based on the test configuration
    # Description must be applied at execution time to ensure it reflects the current test configuration
    allure.dynamic.description(read_md_description(test_name))


def pytest_sessionfinish(session):
    """Save testing environment information into Allure's environment.properties file after test run."""
    if not session.config.getoption("--alluredir"):
        return

    from lib_testbed.generic.util.allure_util import AllureUtil

    AllureUtil(session.config).save_cached_environment_info()
