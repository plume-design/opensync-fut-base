import allure
import pytest

from framework.tools.functions import step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
vpnm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='VPNM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="vpnm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_vpnm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='vpnm')
    server_handler.recipe.clear_full()
    with step('VPNM setup'):
        assert dut_handler.run('tests/vpnm/vpnm_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
test_vpnm_healthcheck_inputs = vpnm_config.get('vpnm_healthcheck', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_vpnm_healthcheck_inputs)
@pytest.mark.dependency(depends=["vpnm_fut_setup_dut"], scope='session')
def test_vpnm_healthcheck(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/vpnm/vpnm_healthcheck') == ExpectedShellResult


########################################################################################################################
test_vpnm_p2s_inputs = vpnm_config.get('vpnm_p2s', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_vpnm_p2s_inputs)
@pytest.mark.dependency(depends=["vpnm_fut_setup_dut"], scope='session')
def test_vpnm_p2s(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/vpnm/vpnm_p2s') == ExpectedShellResult


########################################################################################################################
test_vpnm_s2s_inputs = vpnm_config.get('vpnm_s2s', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_vpnm_s2s_inputs)
@pytest.mark.dependency(depends=["vpnm_fut_setup_dut"], scope='session')
def test_vpnm_s2s(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/vpnm/vpnm_s2s') == ExpectedShellResult


########################################################################################################################
test_vpnm_tunnel_interface_inputs = vpnm_config.get('vpnm_tunnel_interface', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_vpnm_tunnel_interface_inputs)
@pytest.mark.dependency(depends=["vpnm_fut_setup_dut"], scope='session')
def test_vpnm_tunnel_interface(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/vpnm/vpnm_tunnel_interface') == ExpectedShellResult
