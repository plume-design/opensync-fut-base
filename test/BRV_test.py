import allure
import pytest

from framework.tools.functions import get_command_arguments, get_config_opts, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
brv_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='BRV')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.os_integration_m1()
@pytest.mark.dependency(name="brv_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_brv_fut_setup_dut():
    dut_handler, server_handler = pytest.dut_handler, pytest.server_handler
    with step('Transfer'):
        assert dut_handler.transfer(manager='dm')
    server_handler.recipe.clear_full()
    with step('BRV setup'):
        assert dut_handler.run('tests/dm/brv_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
brv_busybox_builtins_args = brv_config.get('brv_busybox_builtins', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', brv_busybox_builtins_args)
@pytest.mark.dependency(depends=["brv_fut_setup_dut"], scope='session')
def test_brv_busybox_builtins(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        tool = test_config['busybox_builtin']
        test_args = get_command_arguments(tool)

    with step('Testcase'):
        assert dut_handler.run('tests/dm/brv_busybox_builtins', test_args) == ExpectedShellResult


########################################################################################################################
brv_is_bcm_license_on_system_fut_inputs = brv_config.get('brv_is_bcm_license_on_system_fut', [])
brv_is_bcm_license_on_system_fut_scenarios = [
    {
        "license": g["license"],
        "service": a,
        **get_config_opts(g),
    }
    for g in brv_is_bcm_license_on_system_fut_inputs for a in g["services"]
]


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', brv_is_bcm_license_on_system_fut_scenarios)
@pytest.mark.dependency(depends=["brv_fut_setup_dut"], scope='session')
def test_brv_is_bcm_license_on_system_fut(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        script = test_config['license']
        service = test_config['service']
        test_args = get_command_arguments(
            f"{script}",
            f"'{service}'",
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/brv_is_bcm_license_on_system', test_args) == ExpectedShellResult


########################################################################################################################
brv_is_script_on_system_fut_args = brv_config.get('brv_is_script_on_system_fut', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', brv_is_script_on_system_fut_args)
@pytest.mark.dependency(depends=["brv_fut_setup_dut"], scope='session')
def test_brv_is_script_on_system_fut(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        script = test_config['system_script']
        test_args = get_command_arguments(script)

    with step('Testcase'):
        assert dut_handler.run('tests/dm/brv_is_script_on_system', test_args) == ExpectedShellResult


########################################################################################################################
brv_is_tool_on_system_fut_args = brv_config.get('brv_is_tool_on_system_fut', [])
brv_is_tool_on_system_native_bridge_args = brv_config.get('brv_is_tool_on_system_native_bridge', [])
brv_is_tool_on_system_ovs_bridge_args = brv_config.get('brv_is_tool_on_system_ovs_bridge', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', brv_is_tool_on_system_fut_args + brv_is_tool_on_system_native_bridge_args + brv_is_tool_on_system_ovs_bridge_args)
@pytest.mark.dependency(depends=["brv_fut_setup_dut"], scope='session')
def test_brv_is_tool_on_system_fut(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        tool = test_config['system_tool']
        test_args = get_command_arguments(tool)

    with step('Check bridge type'):
        bridge_type = pytest.dut_handler.bridge_type
        only_ovs_supported_list = [item['system_tool'] for item in brv_is_tool_on_system_ovs_bridge_args]
        only_native_supported_list = [item['system_tool'] for item in brv_is_tool_on_system_native_bridge_args]
        if (bridge_type == 'native_bridge' and tool in only_ovs_supported_list) or (bridge_type == 'ovs_bridge' and tool in only_native_supported_list):
            pytest.skip(f'Tool {tool} not supported with {bridge_type} bridge type, skipping the test.')

    with step('Testcase'):
        assert dut_handler.run('tests/dm/brv_is_tool_on_system', test_args) == ExpectedShellResult


########################################################################################################################
brv_is_tool_on_system_opensync_args = brv_config.get('brv_is_tool_on_system_opensync', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', brv_is_tool_on_system_opensync_args)
@pytest.mark.dependency(depends=["brv_fut_setup_dut"], scope='session')
def test_brv_is_tool_on_system_opensync(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        tool = test_config['system_tool']
        test_args = get_command_arguments(tool)

    with step('Testcase'):
        assert dut_handler.run('tests/dm/brv_is_tool_on_system', test_args) == ExpectedShellResult


########################################################################################################################
brv_ovs_check_version_args = brv_config.get('brv_ovs_check_version', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', brv_ovs_check_version_args)
@pytest.mark.dependency(depends=["brv_fut_setup_dut"], scope='session')
def test_brv_ovs_check_version(test_config):
    dut_handler = pytest.dut_handler
    # Testcase
    with step('Testcase'):
        if not pytest.dut_handler.bridge_type == 'ovs_bridge':
            pytest.skip('Test is not applicable when device is configured with Linux Native Bridge, skipping the test.')
        assert dut_handler.run('tests/dm/brv_ovs_check_version') == ExpectedShellResult
