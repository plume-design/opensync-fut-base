import allure
import pytest
import yaml

import framework.tools.logger
from framework.lib.fut_allure import FutAllureClass
from framework.lib.fut_cloud import FutCloud
from framework.server_handler import ServerHandlerClass
from framework.tools.functions import get_command_arguments, step
from .globals import SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

fw_version_map = None
try:
    with open('config/rules/fut_version_map.yaml') as reg_rule_file:
        fw_version_map = yaml.safe_load(reg_rule_file)
except Exception:
    log.warning('Failed to load fw version map')

order_exec = 0


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_main_init", scope="session")
def test_compat_main_init():
    log.info('Initializing ServerHandler class')
    pytest.dut_handler = pytest.ref_handler = pytest.ref2_handler = pytest.client_handler = None
    pytest.server_handler = ServerHandlerClass()
    pytest.server_handler.__setattr__('fut_cloud', FutCloud(server_handler=pytest.server_handler))
    pytest.server_handler.generate_active_osrt_location_file()
    log.info('ServerHandler class initialized')


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_unblock_dut_wan_mng_addresses", scope="session", depends=["compat_main_init"])
def test_compat_unblock_dut_wan_mng_addresses():
    server_handler = pytest.server_handler
    dut_mgmt_args = get_command_arguments(server_handler.testbed_cfg.get_or_raise('devices.dut.mgmt_ip'), 'unblock')
    dut_wan_args = get_command_arguments(server_handler.testbed_cfg.get_or_raise('devices.dut.wan_ip'), 'unblock')
    with step('Address unblock'):
        assert server_handler.run('tools/server/cm/address_internet_man', dut_mgmt_args, as_sudo=True) == 0
        assert server_handler.run('tools/server/cm/address_internet_man', dut_wan_args, as_sudo=True) == 0
        assert server_handler.run('tools/server/cm/address_dns_man', dut_mgmt_args, as_sudo=True) == 0
        assert server_handler.run('tools/server/cm/address_dns_man', dut_wan_args, as_sudo=True) == 0
    log.info('DUT WAN and management IP addresses unblocked')


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_dut_init", scope="session", depends=["compat_main_init"])
def test_compat_dut_init():
    log.info('Acquiring DUT device API')
    dut_api = pytest.server_handler.get_pod_api('dut')
    dut_handler = pytest.server_handler.get_test_handler(dut_api)
    pytest.dut_handler = dut_handler
    log.info('Device DUT initialized')


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref_init", scope="session", depends=["compat_main_init"])
def test_compat_ref_init():
    log.info('Acquiring REF device API')
    ref_api = pytest.server_handler.get_pod_api('ref')
    ref_handler = pytest.server_handler.get_test_handler(ref_api)
    pytest.ref_handler = ref_handler
    log.info('Device REF initialized')


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref2_init", scope="session", depends=["compat_main_init"])
def test_compat_ref2_init():
    log.info('Acquiring REF2 device API')
    ref2_api = pytest.server_handler.get_pod_api('ref2')
    ref2_handler = pytest.server_handler.get_test_handler(ref2_api)
    pytest.ref2_handler = ref2_handler
    log.info('Device REF2 initialized')


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client_init", scope="session", depends=["compat_main_init"])
def test_compat_client_init():
    log.info('Acquiring Client device API')
    client_api = pytest.server_handler.get_pod_api('client')
    client_handler = pytest.server_handler.get_test_handler(client_api)
    pytest.client_handler = client_handler
    pytest.client_handler.execute(pytest.client_handler.device_config.get('LOGREAD_CLEAR'))
    log.info('Client initialized')


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client2_init", scope="session", depends=["compat_main_init"])
def test_compat_client2_init():
    log.info('Acquiring Client2 device API')
    client2_api = pytest.server_handler.get_pod_api('client2')
    client2_handler = pytest.server_handler.get_test_handler(client2_api)
    pytest.client2_handler = client2_handler
    pytest.client2_handler.execute(pytest.client2_handler.device_config.get('LOGREAD-CLEAR'))
    log.info('Device Client2 initialized')


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_fut_release_version", scope="session", depends=["compat_main_init"])
def test_compat_fut_release_version(pytestconfig):
    version = pytest.server_handler.get_fut_release_version()
    fut_release_version = version[0].strip()
    log.info(f'FUT release version: {fut_release_version}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_release_version(fut_release_version)
    log.info('FUT release version set')


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_server_device_version", scope="session", depends=["compat_main_init"])
def test_compat_server_device_version(pytestconfig, ignore_osrt_version):
    version = pytest.server_handler.get_server_device_version()
    if not ignore_osrt_version:
        server_handler = pytest.server_handler
        os_version = server_handler.execute_raw(f'cat {server_handler.fut_base_dir}/.version', print_out=True)[1].strip()
        ver_res = version[0].split('__')[1].split()[0]
        assert ver_res >= fw_version_map[os_version]['server']

    server_device_version = version[0].strip()
    log.info(f'Server device version: {server_device_version}')
    version_split = server_device_version.split(' ')[0]
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_server_version(version_split)


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_dut_device_version", scope="session", depends=["compat_dut_init"])
def test_compat_dut_device_version(pytestconfig, is_transfer_only):
    if is_transfer_only:
        pytest.skip('Transfer only, test not required')
    model = pytest.dut_handler.capabilities.get_or_raise('model_string')
    version = pytest.dut_handler.get_version()
    log.info(f'DUT version: {version}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_device_version('dut', model, version)


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.ref_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref_device_version", scope="session", depends=["compat_ref_init"])
def test_compat_ref_device_version(pytestconfig, is_transfer_only):
    if is_transfer_only:
        pytest.skip('Transfer only, test not required')
    model = pytest.ref_handler.capabilities.get_or_raise('model_string')
    version = pytest.ref_handler.get_version()
    log.info(f'REF device version: {version}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_device_version('ref', model, version)


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.ref2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref2_device_version", scope="session", depends=["compat_ref2_init"])
def test_compat_ref2_device_version(pytestconfig, is_transfer_only):
    if is_transfer_only:
        pytest.skip('Transfer only, test not required')
    model = pytest.ref2_handler.capabilities.get_or_raise('model_string')
    version = pytest.ref2_handler.get_version()
    log.info(f'REF2 device version: {version}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_device_version('ref2', model, version)


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.client_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client_device_version", scope="session", depends=["compat_client_init"])
def test_compat_client_device_version(pytestconfig, is_transfer_only, ignore_osrt_version):
    if is_transfer_only:
        pytest.skip('Transfer only, test not required')
    if not ignore_osrt_version:
        server_handler = pytest.server_handler
        os_version = server_handler.execute_raw(f'cat {server_handler.fut_base_dir}/.version', print_out=True)[1].strip()
        if pytest.client_handler.testbed_device_cfg.get('CFG_FOLDER') == 'rpi_client':
            ver_res = pytest.client_handler.execute_raw('cat /.version', print_out=True)[1].split('__')[1].split()[0]
        else:
            ver_res = pytest.client_handler.execute_raw('cat /.version', print_out=True)[1]
        assert ver_res >= fw_version_map[os_version][pytest.client_handler.testbed_device_cfg.get('CFG_FOLDER')]

    model = pytest.client_handler.device_config.get('model_string')
    version = pytest.client_handler.get_version()
    log.info(f'Client device version: {version}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_device_version('client', model, version)


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.client2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client2_device_version", scope="session", depends=["compat_client2_init"])
def test_compat_client2_device_version(pytestconfig, is_transfer_only, ignore_osrt_version):
    if is_transfer_only:
        pytest.skip('Transfer only, test not required')
    if not ignore_osrt_version:
        server_handler = pytest.server_handler
        os_version = server_handler.execute_raw(f'cat {server_handler.fut_base_dir}/.version', print_out=True)[1].strip()
        if pytest.client2_handler.testbed_device_cfg.get('CFG_FOLDER') == 'rpi_client':
            ver_res = pytest.client2_handler.execute_raw('cat /.version', print_out=True)[1].split('__')[1].split()[0]
        else:
            ver_res = pytest.client2_handler.execute_raw('cat /.version', print_out=True)[1]
        assert ver_res >= fw_version_map[os_version][pytest.client2_handler.testbed_device_cfg.get('CFG_FOLDER')]

    model = pytest.client2_handler.device_config.get('model_string')
    version = pytest.client2_handler.get_version()
    log.info(f'Client2 device version: {version}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_device_version('client2', model, version)


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_dut_tmp_mount_executable", scope="session", depends=["compat_dut_init"])
def test_compat_dut_tmp_mount_executable():
    log.info('Testing DUT tmpfs mount permission')
    fut_topdir = pytest.dut_handler.device_config.get_or_raise('FUT_TOPDIR')
    mount_point_cmd = f"test -e {fut_topdir} || mkdir -p {fut_topdir} && df -TP {fut_topdir} | tail -1 | awk -F' ' '{{print $NF}}'"
    with step('Get mount point'):
        mount_point_ec, mount_point_std_out, mount_point_std_err = pytest.dut_handler.execute_raw(mount_point_cmd, print_out=True)
        assert mount_point_ec == 0
    perm_check_cmd = f"mount && mount | grep -E 'on {mount_point_std_out}.*noexec'"
    check_code = 0 if pytest.server_handler.dry_run else 1
    with step('Check'):
        assert pytest.dut_handler.execute(perm_check_cmd, print_out=True, expected_ec=check_code) == check_code


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_dut_transfer", scope="session", depends=["compat_dut_init"])
def test_compat_dut_transfer(is_transfer_only):
    log.info('Testing FUT transfer to DUT')
    assert pytest.dut_handler.transfer(full=is_transfer_only)
    assert pytest.dut_handler.create_and_transfer_fut_set_env()


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref_tmp_mount_executable", scope="session", depends=["compat_ref_init"])
def test_compat_ref_tmp_mount_executable():
    log.info('Testing REF tmpfs mount permission')
    fut_topdir = pytest.ref_handler.device_config.get_or_raise('FUT_TOPDIR')
    mount_point_cmd = f"test -e {fut_topdir} || mkdir -p {fut_topdir} && df -TP {fut_topdir} | tail -1 | awk -F' ' '{{print $NF}}'"
    with step('Get mount point'):
        mount_point_ec, mount_point_std_out, mount_point_std_err = pytest.ref_handler.execute_raw(mount_point_cmd, print_out=True)
        assert mount_point_ec == 0
    perm_check_cmd = f"mount && mount | grep -E 'on {mount_point_std_out}.*noexec'"
    check_code = 0 if pytest.server_handler.dry_run else 1
    with step('Check'):
        assert pytest.ref_handler.execute(perm_check_cmd, print_out=True, expected_ec=check_code) == check_code


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref_transfer", scope="session", depends=["compat_ref_init"])
def test_compat_ref_transfer(is_transfer_only):
    log.info('Testing FUT transfer to REF')
    assert pytest.ref_handler.transfer(full=is_transfer_only)
    assert pytest.ref_handler.create_and_transfer_fut_set_env()


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref2_tmp_mount_executable", scope="session", depends=["compat_ref2_init"])
def test_compat_ref2_tmp_mount_executable():
    log.info('Testing REF2 tmpfs mount permission')
    fut_topdir = pytest.ref2_handler.device_config.get_or_raise('FUT_TOPDIR')
    mount_point_cmd = f"test -e {fut_topdir} || mkdir -p {fut_topdir} && df -TP {fut_topdir} | tail -1 | awk -F' ' '{{print $NF}}'"
    with step('Get mount point'):
        mount_point_ec, mount_point_std_out, mount_point_std_err = pytest.ref2_handler.execute_raw(mount_point_cmd, print_out=True)
        assert mount_point_ec == 0
    perm_check_cmd = f"mount && mount | grep -E 'on {mount_point_std_out}.*noexec'"
    check_code = 0 if pytest.server_handler.dry_run else 1
    with step('Check'):
        assert pytest.ref2_handler.execute(perm_check_cmd, print_out=True, expected_ec=check_code) == check_code


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref2_transfer", scope="session", depends=["compat_ref2_init"])
def test_compat_ref2_transfer(is_transfer_only):
    log.info('Testing FUT transfer to REF2')
    assert pytest.ref2_handler.transfer(full=is_transfer_only)
    assert pytest.ref2_handler.create_and_transfer_fut_set_env()


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client_transfer", scope="session", depends=["compat_client_init"])
def test_compat_client_transfer(is_transfer_only):
    log.info('Testing FUT transfer to Client')
    assert pytest.client_handler.transfer(full=is_transfer_only)
    assert pytest.client_handler.create_and_transfer_fut_set_env()


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client2_transfer", scope="session", depends=["compat_client2_init"])
def test_compat_client2_transfer(is_transfer_only):
    log.info('Testing FUT transfer to Client2')
    assert pytest.client2_handler.transfer(full=is_transfer_only)
    assert pytest.client2_handler.create_and_transfer_fut_set_env()


order_exec += 1


@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(
    name="compat_dut_verify_reg_domain", scope="session", depends=["compat_dut_init", "compat_dut_transfer"],
)
def test_compat_dut_verify_reg_domain():
    dut_handler = pytest.dut_handler
    with step('Acquire'):
        try:
            device_region = dut_handler.get_region()
        except Exception as e:
            log.warning(f'Failed to acquire device regulatory domain\n{e}')
        log.info(f'Region retrieved from DUT is {device_region}')
    with step('Validate'):
        config_region = pytest.dut_handler.capabilities.get_or_raise('regulatory_domain')
        log.info(f'Device DUT, configured region: {config_region}, actual region: {device_region}')
        assert config_region == device_region


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.ref_setup()
@pytest.mark.dependency(
    name="compat_ref_verify_reg_domain", scope="session", depends=["compat_ref_init", "compat_ref_transfer"],
)
def test_compat_ref_verify_reg_domain():
    ref_handler = pytest.ref_handler
    with step('Acquire'):
        try:
            device_region = ref_handler.get_region()
        except Exception as e:
            log.warning(f'Failed to acquire device regulatory domain\n{e}')
        log.info(f'Region retrieved from REF is {device_region}')
    with step('Validate'):
        config_region = ref_handler.capabilities.get_or_raise('regulatory_domain')
        log.info(f'Device REF, configured region: {config_region}, actual region: {device_region}')
        assert config_region == device_region


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.ref2_setup()
@pytest.mark.dependency(
    name="compat_ref2_verify_reg_domain", scope="session", depends=["compat_ref2_init", "compat_ref2_transfer"],
)
def test_compat_ref2_verify_reg_domain():
    ref2_handler = pytest.ref2_handler
    with step('Acquire'):
        try:
            device_region = ref2_handler.get_region()
        except Exception as e:
            log.warning(f'Failed to acquire device regulatory domain\n{e}')
        log.info(f'Region retrieved from REF2 is {device_region}')
    with step('Validate'):
        config_region = ref2_handler.capabilities.get_or_raise('regulatory_domain')
        log.info(f'Device REF2, configured region: {config_region}, actual region: {device_region}')
        assert config_region == device_region


order_exec += 1


@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_dut_bridge_type", scope="session", depends=["compat_dut_init"])
def test_compat_dut_bridge_type(pytestconfig, is_transfer_only):
    if is_transfer_only:
        pytest.skip('Transfer only, test not required')
    bridge_type = pytest.dut_handler.get_bridge_type()
    pytest.dut_handler.bridge_type = bridge_type
    log.info(f'DUT bridge type: {bridge_type}')
    allure_dir_option = pytestconfig.getoption('allure_report_dir')
    if allure_dir_option:
        f_allure = FutAllureClass(allure_dir_option)
        f_allure.set_device_bridge_type('dut', bridge_type)


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref_prevent_reboot", scope="session", depends=[
    "compat_ref_init", "compat_ref_transfer", "compat_ref_tmp_mount_executable",
])
def test_compat_ref_prevent_reboot():
    log.info('Initialize REF device to prevent unwanted reboot')
    with step('Setup'):
        assert pytest.ref_handler.run('tools/device/device_init') == 0


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref2_prevent_reboot", scope="session", depends=[
    "compat_ref2_init", "compat_ref2_transfer", "compat_ref2_tmp_mount_executable",
])
def test_compat_ref2_prevent_reboot():
    log.info('Initialize REF2 device to prevent unwanted reboot')
    with step('Setup'):
        assert pytest.ref2_handler.run('tools/device/device_init') == 0


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(
    name="compat_server_ready", scope="session", depends=[
        "compat_main_init", "compat_server_device_version",
    ],
)
def test_compat_server_ready():
    assert True


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
@pytest.mark.dependency(name="compat_dut_ready", scope="session", depends=[
    "compat_dut_init",
    "compat_dut_device_version",
    "compat_dut_tmp_mount_executable",
    "compat_dut_transfer",
    "compat_dut_verify_reg_domain",
    "compat_dut_bridge_type",
])
def test_compat_dut_ready():
    if pytest.logpull:
        log.info('Doing initial logpull to clear device logs')
        pytest.dut_handler.pod_api.get_logs()
    pytest.dut_handler.is_ready = True
    SERVER_HANDLER_GLOBAL.device_handlers[pytest.dut_handler.name] = pytest.dut_handler
    assert True


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref_ready", scope="session", depends=[
    "compat_ref_init",
    "compat_ref_device_version",
    "compat_ref_tmp_mount_executable",
    "compat_ref_transfer",
    "compat_ref_verify_reg_domain",
    "compat_ref_prevent_reboot",
])
def test_compat_ref_ready():
    pytest.ref_handler.is_ready = True
    SERVER_HANDLER_GLOBAL.device_handlers[pytest.ref_handler.name] = pytest.ref_handler
    assert True


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ref2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_ref2_ready", scope="session", depends=[
    "compat_ref2_init",
    "compat_ref2_device_version",
    "compat_ref2_tmp_mount_executable",
    "compat_ref2_transfer",
    "compat_ref2_verify_reg_domain",
    "compat_ref2_prevent_reboot",
])
def test_compat_ref2_ready():
    pytest.ref2_handler.is_ready = True
    SERVER_HANDLER_GLOBAL.device_handlers[pytest.ref2_handler.name] = pytest.ref2_handler
    assert True


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client_ready", scope="session",
                        depends=["compat_client_init", "compat_client_transfer", "compat_client_device_version"])
def test_compat_client_ready():
    pytest.client_handler.is_ready = True
    SERVER_HANDLER_GLOBAL.device_handlers[pytest.client_handler.name] = pytest.client_handler
    assert True


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.client2_setup()
@pytest.mark.run(order=order_exec)
@pytest.mark.dependency(name="compat_client2_ready", scope="session",
                        depends=["compat_client2_init", "compat_client2_transfer", "compat_client2_device_version"])
def test_compat_client2_ready():
    pytest.client2_handler.is_ready = True
    SERVER_HANDLER_GLOBAL.device_handlers[pytest.client2_handler.name] = pytest.client2_handler
    assert True


order_exec += 1


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.run(order=order_exec)
@pytest.mark.always_run()
def test_compat_is_transfer_only(is_transfer_only):
    if is_transfer_only:
        pytest.exit('Transfer only - quitting')
    else:
        pytest.skip('Continuing...')
