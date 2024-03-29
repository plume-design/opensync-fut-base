import pytest

from framework.tools import fut_setup


@pytest.fixture(autouse=True, scope="session")
def setup(request):
    fut_setup.setup_fut_configurator()


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    unit_test_mark = "gen_fut_selftest"
    for item in items:
        if "self_test/" in item.nodeid:
            config.addinivalue_line(
                "markers",
                unit_test_mark,
            )
            item.add_marker(unit_test_mark)
            item.add_marker("no_process_restart_detection")
    config.option.mock_items = items
