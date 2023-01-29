import allure
import pytest

from framework.tools.functions import step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
qm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='QM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="qm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_qm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='qm')
    server_handler.recipe.clear_full()
    with step('QM setup'):
        assert dut_handler.run('tests/qm/qm_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()