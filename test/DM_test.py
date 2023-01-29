from time import sleep

import allure
import pytest

from framework.tools.functions import FailedException, get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

# Read entire testcase configuration
dm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='DM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="dm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_dm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='dm')
    server_handler.recipe.clear_full()
    with step('DM setup'):
        assert dut_handler.run('tests/dm/dm_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
test_dm_verify_awlan_node_params_inputs = dm_config.get('dm_verify_awlan_node_params', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_awlan_node_params_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_awlan_node_params(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        awlan_field_name = test_config.get('awlan_field_name')
        awlan_field_val = test_config.get('awlan_field_val')
        test_args = get_command_arguments(
            awlan_field_name,
            awlan_field_val,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_awlan_node_params', test_args) == ExpectedShellResult


########################################################################################################################
test_dm_verify_count_reboot_status_inputs = dm_config.get('dm_verify_count_reboot_status', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_count_reboot_status_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_count_reboot_status(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_count_reboot_status') == ExpectedShellResult


########################################################################################################################
test_dm_verify_counter_inc_reboot_status_inputs = dm_config.get('dm_verify_counter_inc_reboot_status', [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_counter_inc_reboot_status_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_counter_inc_reboot_status(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        device_reboot_timeout = dut_handler.capabilities.get('kpi.boot_time')
        if not isinstance(device_reboot_timeout, int):
            raise FailedException('Device capabilities file is missing kpi.boot_time value')

    try:
        with step('Reboot DUT'):
            count_before_reboot = dut_handler.run_raw('tools/device/get_count_reboot_status')
            assert dut_handler.run('tools/device/reboot_dut_w_reason', 'USER') == ExpectedShellResult
            sleep(10)
        with step('Wait for DUT after reboot'):
            dut_handler.pod_api.lib.wait_available(timeout=device_reboot_timeout)
            # Allows device to recover after reboot
            sleep(10)
            count_after_reboot = dut_handler.run_raw('tools/device/get_count_reboot_status')
        with step('Testcase'):
            test_args = get_command_arguments(
                count_before_reboot[1],
                count_after_reboot[1],
            )
            assert dut_handler.run('tests/dm/dm_verify_counter_inc_reboot_status', test_args) == ExpectedShellResult

    finally:
        with step('Wait for DUT after reboot'):
            dut_handler.pod_api.lib.wait_available(timeout=max(device_reboot_timeout, 120))


########################################################################################################################
test_dm_verify_device_mode_awlan_node_inputs = dm_config.get('dm_verify_device_mode_awlan_node', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_device_mode_awlan_node_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_device_mode_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        device_mode = test_config.get('device_mode')
        test_args = get_command_arguments(
            device_mode,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_device_mode_awlan_node', test_args) == ExpectedShellResult


########################################################################################################################
test_dm_verify_enable_node_services_inputs = dm_config.get('dm_verify_enable_node_services', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_enable_node_services_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_enable_node_services(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        service = test_config.get('service')
        kconfig_val = test_config.get('kconfig_val')
        test_args = get_command_arguments(
            service,
            kconfig_val,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_enable_node_services', test_args) == ExpectedShellResult


########################################################################################################################
test_dm_verify_node_services_inputs = dm_config.get('dm_verify_node_services', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_node_services_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_node_services(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        service = test_config.get('service')
        kconfig_val = test_config.get('kconfig_val')
        test_args = get_command_arguments(
            service,
            kconfig_val,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_node_services', test_args) == ExpectedShellResult


########################################################################################################################
test_dm_verify_opensync_version_awlan_node_inputs = dm_config.get('dm_verify_opensync_version_awlan_node', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_opensync_version_awlan_node_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_opensync_version_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_opensync_version_awlan_node') == ExpectedShellResult


########################################################################################################################
test_dm_verify_reboot_file_exists_inputs = dm_config.get('dm_verify_reboot_file_exists', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_reboot_file_exists_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_reboot_file_exists(test_config):
    dut_handler = pytest.dut_handler
    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_reboot_file_exists') == ExpectedShellResult


########################################################################################################################
test_dm_verify_reboot_reason_inputs = dm_config.get('dm_verify_reboot_reason', [])


@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_reboot_reason_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_reboot_reason(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Argument from device capabilities, verify if correct
        opensync_rootdir = dut_handler.capabilities.get_or_raise('opensync_rootdir')
        device_reboot_timeout = dut_handler.capabilities.get('kpi.boot_time')
        if not isinstance(device_reboot_timeout, int):
            raise FailedException('Device capabilities file is missing kpi.boot_time value')

        # Test arguments from testcase config
        reason = test_config.get('reboot_reason')
        test_args_base = [
            reason,
        ]
        if reason == 'CLOUD':
            test_args_base += [
                opensync_rootdir,
            ]
        test_args = get_command_arguments(*test_args_base)

    try:
        with step('Verify device capability to record reboot reason'):
            file_exists_ec = dut_handler.run('tools/device/check_reboot_file_exists')
            if file_exists_ec != ExpectedShellResult:
                pytest.skip('Reboot file does not exist, skip dm_verify_reboot_reason test case')
        with step('Reboot DUT'):
            assert dut_handler.run('tools/device/reboot_dut_w_reason', test_args) == ExpectedShellResult
            # Hardcoded sleep to allow devices to actually trigger reboot. Do not optimize
            sleep(20)
        with step('Wait for DUT after reboot'):
            dut_handler.pod_api.lib.wait_available(timeout=device_reboot_timeout)
            # Allows device to recover after reboot
            sleep(10)
        with step('Testcase'):
            assert dut_handler.run('tests/dm/dm_verify_reboot_reason', test_args) == ExpectedShellResult
    finally:
        with step('Wait for DUT after reboot'):
            dut_handler.pod_api.lib.wait_available(timeout=max(device_reboot_timeout, 120))


########################################################################################################################
test_dm_verify_vendor_name_awlan_node_inputs = dm_config.get('dm_verify_vendor_name_awlan_node', [])


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_vendor_name_awlan_node_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup_dut"], scope='session')
def test_dm_verify_vendor_name_awlan_node(test_config):
    dut_handler = pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        vendor_name = test_config.get('vendor_name')
        test_args = get_command_arguments(
            vendor_name,
        )

    with step('Testcase'):
        assert dut_handler.run('tests/dm/dm_verify_vendor_name_awlan_node', test_args) == ExpectedShellResult
