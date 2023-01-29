import allure
import pytest

from framework.tools.functions import get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
lm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='LM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="lm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_lm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='pm')
    server_handler.recipe.clear_full()
    with step('LM setup'):
        assert dut_handler.run('tests/pm/lm_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
test_lm_verify_log_severity_inputs = lm_config.get('lm_verify_log_severity', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_lm_verify_log_severity_inputs)
@pytest.mark.dependency(depends=["lm_fut_setup_dut"], scope='session')
def test_lm_verify_log_severity(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('name'),
            test_config.get('log_severity'),
        )

    # Testcase
    with step('Testcase'):
        assert dut_handler.run('tests/pm/lm_verify_log_severity', test_args) == ExpectedShellResult


########################################################################################################################
test_lm_trigger_cloud_logpull_inputs = lm_config.get('lm_trigger_cloud_logpull', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_lm_trigger_cloud_logpull_inputs)
@pytest.mark.dependency(depends=["lm_fut_setup_dut"], scope='session')
def test_lm_trigger_cloud_logpull(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        test_args = get_command_arguments(
            test_config.get('upload_location'),
            test_config.get('upload_token'),
        )

    # Testcase
    with step('Testcase'):
        assert dut_handler.run('tests/pm/lm_trigger_cloud_logpull', test_args) == ExpectedShellResult
