import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "fut_selftest" in item.nodeid:
            item.add_marker("gen_fut_selftest")
    config.option.mock_items = items
