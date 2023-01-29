import time

import allure
import pytest

import framework.tools.logger
from framework.tools.functions import FailedException, get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

# Read entire testcase configuration
cm2_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='CM')
USE_FUT_CLOUD = cm2_config.get('cloud_config.use_fut_cloud', False)


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.os_integration_m1()
@pytest.mark.dependency(name="cm2_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_cm2_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='cm2')

    server_handler.recipe.clear_full()
    # Preparation argument from testbed config
    dut_mgmt_args = get_command_arguments(server_handler.testbed_cfg.get_or_raise('devices.dut.mgmt_ip'), 'unblock')
    dut_wan_args = get_command_arguments(server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip'), 'unblock')
    # Unblock traffic to DUT
    with step('Preparation'):
        assert server_handler.run('tools/server/cm/address_internet_man', dut_mgmt_args, as_sudo=True) == ExpectedShellResult
        assert server_handler.run('tools/server/cm/address_internet_man', dut_wan_args, as_sudo=True) == ExpectedShellResult
        assert server_handler.run('tools/server/cm/address_dns_man', dut_mgmt_args, as_sudo=True) == ExpectedShellResult
        assert server_handler.run('tools/server/cm/address_dns_man', dut_wan_args, as_sudo=True) == ExpectedShellResult

    if USE_FUT_CLOUD:
        server_handler.__setattr__('use_fut_cloud', True)
        with step('Prepare FUT Cloud'):
            # Hardcode latest TLS version 1.2 if not present in testbed configuration
            assert server_handler.fut_cloud.clear_log()
            assert server_handler.fut_cloud.change_tls_ver(server_handler.testbed_cfg.get('server.cloud.tls_version', '1.2'))
            assert server_handler.fut_cloud.restart_cloud()
    # Arguments from device capabilities
    dut_eth_wan = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
    dut_wan_bridge = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')
    setup_args = get_command_arguments(dut_eth_wan, dut_wan_bridge, "true") if USE_FUT_CLOUD else \
        get_command_arguments(dut_eth_wan, dut_wan_bridge)
    with step('CM2 setup'):
        assert dut_handler.run('tests/cm2/cm2_setup', setup_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult

    server_handler.recipe.mark_setup()


########################################################################################################################
test_cm2_ble_status_cloud_down_inputs = cm2_config.get('cm2_ble_status_cloud_down', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_ble_status_cloud_down_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_ble_status_cloud_down(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    # Test arguments from device capabilities
    dut_eth_wan = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
    dut_wan_bridge = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')

    with step('Fetch Cloud controller IP'):
        setup_args = get_command_arguments(dut_eth_wan, dut_wan_bridge, "true") if USE_FUT_CLOUD else \
            get_command_arguments(dut_eth_wan, dut_wan_bridge)
        assert dut_handler.run('tests/cm2/cm2_setup', setup_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
        controller_ip = dut_handler.run_raw('tools/device/get_connected_cloud_controller_ip', do_cloud_log=USE_FUT_CLOUD, print_out=True)
        if controller_ip[0] != ExpectedShellResult or controller_ip[1] == '' or controller_ip[1] is None:
            raise FailedException('Failed to retrieve IP address of Cloud controller')

    with step('Fetch redirector hostname'):
        redirector_hostname = dut_handler.run_raw('tools/device/get_redirector_hostname', do_cloud_log=USE_FUT_CLOUD, print_out=True)
        if redirector_hostname[0] != ExpectedShellResult or redirector_hostname[1] == '' or redirector_hostname[1] is None:
            raise FailedException('Failed to retrieve hostname of the redirector')

    cloud_recovered_args = get_command_arguments(
        "cloud_recovered",
    )
    cloud_blocked_args = get_command_arguments(
        "cloud_down",
    )

    manipulate_cloud_ip_addr = 'tools/server/cm/manipulate_cloud_ip_addresses'
    cloud_block_args = get_command_arguments(
        redirector_hostname[1],
        controller_ip[1],
        "block",
    )
    cloud_unblock_args = get_command_arguments(
        redirector_hostname[1],
        controller_ip[1],
        "unblock",
    )

    try:
        with step('Testcase'):
            assert dut_handler.run('tests/cm2/cm2_ble_status_cloud_down', cloud_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            # Disable Cloud access
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.stop_cloud()
            else:
                assert server_handler.run(manipulate_cloud_ip_addr, cloud_block_args, as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_ble_status_cloud_down', cloud_blocked_args) == ExpectedShellResult
            # Enable Cloud access
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.restart_cloud()
            else:
                assert server_handler.run(manipulate_cloud_ip_addr, cloud_unblock_args, as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_ble_status_cloud_down', cloud_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            # Enable Cloud access during cleanup
            server_handler.run(manipulate_cloud_ip_addr, cloud_unblock_args, as_sudo=True, do_cloud_log=USE_FUT_CLOUD)


########################################################################################################################
test_cm2_ble_status_interface_down_inputs = cm2_config.get('cm2_ble_status_interface_down', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_ble_status_interface_down_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_ble_status_interface_down(test_config):
    dut_handler = pytest.dut_handler
    # Test arguments from device capabilities
    test_args = get_command_arguments(dut_handler.capabilities.get('interfaces.primary_wan_interface'))
    with step('Testcase'):
        assert dut_handler.run('tests/cm2/cm2_ble_status_interface_down', test_args) == ExpectedShellResult


########################################################################################################################
test_cm2_ble_status_internet_block_inputs = cm2_config.get('cm2_ble_status_internet_block', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_ble_status_internet_block_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_ble_status_internet_block(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    # Testcase argument from testbed config
    dut_wan_inet_addr = server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip')
    # Script to manipulate internet access
    manipulate_internet = 'tools/server/cm/address_internet_man'
    # Test arguments from device capabilities
    dut_eth_wan = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
    dut_wan_bridge = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')

    internet_blocked_args = get_command_arguments("internet_blocked")
    internet_recovered_args = get_command_arguments("internet_recovered")
    setup_args = get_command_arguments(dut_eth_wan, dut_wan_bridge, "true") if USE_FUT_CLOUD else \
        get_command_arguments(dut_eth_wan, dut_wan_bridge)

    try:
        with step('CM2 setup'):
            assert dut_handler.run('tests/cm2/cm2_setup', setup_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
        with step('Testcase'):
            assert dut_handler.run('tests/cm2/cm2_ble_status_internet_block', internet_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            # Bring Cloud down to simulate internet lost since FUT Cloud is on localhost
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.stop_cloud()
            assert server_handler.run(manipulate_internet, get_command_arguments(dut_wan_inet_addr, 'block'), as_sudo=True) == ExpectedShellResult
            time.sleep(3)
            assert dut_handler.run('tests/cm2/cm2_ble_status_internet_block', internet_blocked_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            assert server_handler.run(manipulate_internet, get_command_arguments(dut_wan_inet_addr, 'unblock'), as_sudo=True) == ExpectedShellResult
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.restart_cloud()
            assert dut_handler.run('tests/cm2/cm2_ble_status_internet_block', internet_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            server_handler.fut_cloud.restart_cloud()
            server_handler.run(manipulate_internet, get_command_arguments(dut_wan_inet_addr, 'unblock'), as_sudo=True)


########################################################################################################################
test_cm2_cloud_down_inputs = cm2_config.get('cm2_cloud_down', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_cloud_down_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_cloud_down(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    # Test arguments from device capabilities
    dut_eth_wan = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
    dut_wan_bridge = dut_handler.capabilities.get_or_raise('interfaces.wan_bridge')

    with step('Fetch Cloud controller IP'):
        setup_args = get_command_arguments(dut_eth_wan, dut_wan_bridge, "true") if USE_FUT_CLOUD else \
            get_command_arguments(dut_eth_wan, dut_wan_bridge)
        assert dut_handler.run('tests/cm2/cm2_setup', setup_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
        controller_ip = dut_handler.run_raw('tools/device/get_connected_cloud_controller_ip', print_out=True, do_cloud_log=USE_FUT_CLOUD)
        if controller_ip[0] != ExpectedShellResult or controller_ip[1] == '' or controller_ip[1] is None:
            raise FailedException('Failed to retrieve IP address of Cloud controller')

    with step('Fetch redirector hostname'):
        redirector_hostname = dut_handler.run_raw('tools/device/get_redirector_hostname', do_cloud_log=USE_FUT_CLOUD, print_out=True)
        if redirector_hostname[0] != ExpectedShellResult or redirector_hostname[1] == '' or redirector_hostname[1] is None:
            raise FailedException('Failed to retrieve hostname of the redirector')

    counter = test_config.get('unreachable_cloud_counter')
    cloud_recovered_args = get_command_arguments(
        dut_eth_wan,
        "0",
        "cloud_recovered",
    )
    cloud_check_counter_args = get_command_arguments(
        dut_eth_wan,
        counter,
        "check_counter",
    )

    manipulate_cloud_ip_addr = 'tools/server/cm/manipulate_cloud_ip_addresses'
    cloud_block_args = get_command_arguments(
        redirector_hostname[1],
        controller_ip[1],
        "block",
    )
    cloud_unblock_args = get_command_arguments(
        redirector_hostname[1],
        controller_ip[1],
        "unblock",
    )

    try:
        with step('Testcase'):
            assert dut_handler.run('tests/cm2/cm2_cloud_down', cloud_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.stop_cloud()
            else:
                assert server_handler.run(manipulate_cloud_ip_addr, cloud_block_args, as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_cloud_down', cloud_check_counter_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.restart_cloud()
            else:
                assert server_handler.run(manipulate_cloud_ip_addr, cloud_unblock_args, as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_cloud_down', cloud_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            server_handler.fut_cloud.restart_cloud()
            server_handler.run(manipulate_cloud_ip_addr, cloud_unblock_args, as_sudo=True)


########################################################################################################################
test_cm2_dns_failure_inputs = cm2_config.get('cm2_dns_failure', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_dns_failure_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
@pytest.mark.skipif(USE_FUT_CLOUD, reason='Test not suitable for FUT Cloud')
def test_cm2_dns_failure(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    # Testcase argument from testbed config
    dut_wan_inet_addr = server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip')
    # Script to manipulate DNS traffic
    manipulate_dns = 'tools/server/cm/address_dns_man'

    dns_blocked_args = get_command_arguments('dns_blocked')
    dns_unblocked_args = get_command_arguments('dns_recovered')

    try:
        with step('Testcase'):
            assert dut_handler.run('tests/cm2/cm2_dns_failure', dns_unblocked_args) == ExpectedShellResult
            # Block on RPI Server, execute testcase, unblock on RPI Server
            assert server_handler.run(manipulate_dns, get_command_arguments(dut_wan_inet_addr, 'block'), as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_dns_failure', dns_blocked_args) == ExpectedShellResult
            assert server_handler.run(manipulate_dns, get_command_arguments(dut_wan_inet_addr, 'unblock'), as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_dns_failure', dns_unblocked_args) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            server_handler.run(manipulate_dns, get_command_arguments(dut_wan_inet_addr, 'unblock'), as_sudo=True)


########################################################################################################################
test_cm2_internet_lost_inputs = cm2_config.get('cm2_internet_lost', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_internet_lost_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_internet_lost(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    # Testcase argument from testbed config
    dut_wan_inet_addr = server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip')
    # Script to manipulate internet access
    manipulate_internet = 'tools/server/cm/address_internet_man'

    counter = test_config.get('unreachable_internet_counter')
    internet_blocked_args = get_command_arguments(
        dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface'),
        counter,
        "check_counter",
    )
    internet_recovered_args = get_command_arguments(
        dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface'),
        "0",
        "internet_recovered",
    )

    try:
        with step('Testcase'):
            assert dut_handler.run('tests/cm2/cm2_internet_lost', internet_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            # Bring Cloud down to simulate internet lost since FUT Cloud is on localhost
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.stop_cloud()
            assert server_handler.run(manipulate_internet, get_command_arguments(dut_wan_inet_addr, 'block'), as_sudo=True) == ExpectedShellResult
            assert dut_handler.run('tests/cm2/cm2_internet_lost', internet_blocked_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
            assert server_handler.run(manipulate_internet, get_command_arguments(dut_wan_inet_addr, 'unblock'), as_sudo=True) == ExpectedShellResult
            time.sleep(3)
            if USE_FUT_CLOUD:
                assert server_handler.fut_cloud.restart_cloud()
            assert dut_handler.run('tests/cm2/cm2_internet_lost', internet_recovered_args, do_cloud_log=USE_FUT_CLOUD) == ExpectedShellResult
    finally:
        with step('Cleanup'):
            server_handler.fut_cloud.restart_cloud()
            server_handler.run(manipulate_internet, get_command_arguments(dut_wan_inet_addr, 'unblock'), as_sudo=True)


########################################################################################################################
test_cm2_link_lost_inputs = cm2_config.get('cm2_link_lost', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_link_lost_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_link_lost(test_config):
    dut_handler = pytest.dut_handler
    # Test arguments from device capabilities
    if_name = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')
    test_args = get_command_arguments(if_name)
    with step('Testcase'):
        assert dut_handler.run('tests/cm2/cm2_link_lost', test_args) == ExpectedShellResult


########################################################################################################################
test_cm2_ssl_check_inputs = cm2_config.get('cm2_ssl_check', [])


@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_cm2_ssl_check_inputs)
@pytest.mark.dependency(depends=["cm2_fut_setup_dut"], scope='session')
def test_cm2_ssl_check(test_config):
    dut_handler = pytest.dut_handler

    with step('Testcase'):
        assert dut_handler.run('tests/cm2/cm2_ssl_check') == ExpectedShellResult
