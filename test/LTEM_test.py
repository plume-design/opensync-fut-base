import allure
import pytest

from framework.tools.functions import get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
ltem_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='LTEM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="ltem_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_ltem_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='ltem')
    server_handler.recipe.clear_full()
    with step('LTEM setup'):
        setup_args = get_command_arguments("wwan0", "data.icore.name", "true")
        assert dut_handler.run('tests/ltem/ltem_setup', setup_args) == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
ltem_force_lte_inputs = ltem_config.get('ltem_force_lte', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', ltem_force_lte_inputs)
@pytest.mark.dependency(depends=["ltem_fut_setup_dut"], scope='session')
def test_ltem_force_lte(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        lte_if_name = test_config.get('lte_if_name')
        test_args = get_command_arguments(
            lte_if_name,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/ltem/ltem_force_lte', test_args) == ExpectedShellResult


########################################################################################################################
ltem_validation_inputs = ltem_config.get('ltem_validation', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', ltem_validation_inputs)
@pytest.mark.dependency(depends=["ltem_fut_setup_dut"], scope='session')
def test_ltem_validation(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        access_point_name = test_config.get('access_point_name')
        has_l2 = test_config.get('has_l2')
        has_l3 = test_config.get('has_l3')
        if_type = test_config.get('if_type')
        lte_if_name = test_config.get('lte_if_name')
        metric = test_config.get('metric')
        route_tool_path = test_config.get('route_tool_path')
        # Keep the same order of arguments
        test_args = get_command_arguments(
            lte_if_name,
            if_type,
            access_point_name,
            has_l2,
            has_l3,
            metric,
            route_tool_path,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/ltem/ltem_validation', test_args) == ExpectedShellResult


########################################################################################################################
ltem_verify_table_exists_inputs = ltem_config.get('ltem_verify_table_exists', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', ltem_verify_table_exists_inputs)
@pytest.mark.dependency(depends=["ltem_fut_setup_dut"], scope='session')
def test_ltem_verify_table_exists(test_config):
    dut_handler = pytest.dut_handler
    with step('Testcase'):
        assert dut_handler.run('tests/ltem/ltem_verify_table_exists') == ExpectedShellResult
