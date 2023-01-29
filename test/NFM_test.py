import allure
import pytest

from framework.tools.functions import get_command_arguments, step
from .globals import ExpectedShellResult
from .globals import SERVER_HANDLER_GLOBAL


# Read entire testcase configuration
nfm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='NFM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.os_integration_m1()
@pytest.mark.dependency(name="nfm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_nfm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='nfm')
    server_handler.recipe.clear_full()
    with step('NFM setup'):
        assert dut_handler.run('tests/nfm/nfm_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
test_nfm_native_ebtable_check_inputs = nfm_config.get('nfm_native_ebtable_check', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nfm_native_ebtable_check_inputs)
@pytest.mark.dependency(depends=["nfm_fut_setup_dut"], scope='session')
def test_nfm_native_ebtable_check(test_config):
    dut_handler = pytest.dut_handler
    with step('Check bridge type'):
        if not dut_handler.bridge_type == 'native_bridge':
            pytest.skip('Test is applicable only when device is configured with Linux Native Bridge, skipping the test.')
    with step('Preparation'):
        # Test arguments from testcase config
        name = test_config.get('name')
        chain_name = test_config.get('chain_name')
        table_name = test_config.get('table_name')
        rule = test_config.get('rule')
        target = test_config.get('target')
        priority = test_config.get('priority')
        update_target = test_config.get('update_target')
        test_args = get_command_arguments(
            name,
            chain_name,
            table_name,
            rule,
            target,
            priority,
            update_target,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/nfm/nfm_native_ebtable_check', test_args) == ExpectedShellResult


########################################################################################################################
test_nfm_native_ebtable_template_check_inputs = nfm_config.get('nfm_native_ebtable_template_check', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_nfm_native_ebtable_template_check_inputs)
@pytest.mark.dependency(depends=["nfm_fut_setup_dut"], scope='session')
def test_nfm_native_ebtable_template_check(test_config):
    dut_handler = pytest.dut_handler

    with step('Check bridge type'):
        if not dut_handler.bridge_type == 'native_bridge':
            pytest.skip('Test is applicable only when device is configured with Linux Native Bridge, skipping the test.')
    with step('Preparation'):
        # Test arguments from testcase config
        name = test_config.get('name')
        chain_name = test_config.get('chain_name')
        table_name = test_config.get('table_name')
        target = test_config.get('target')
        priority = test_config.get('priority')
        update_target = test_config.get('update_target')
        test_args = get_command_arguments(
            name,
            chain_name,
            table_name,
            target,
            priority,
            update_target,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/nfm/nfm_native_ebtable_template_check', test_args) == ExpectedShellResult
