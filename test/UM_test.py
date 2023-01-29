import os
import random
import string
from pathlib import Path

import allure
import pytest

import framework.tools.logger
from framework.tools.functions import generate_image_key, get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

# Read entire testcase configuration
um_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='UM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="um_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_um_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    if not server_handler.use_docker:
        pytest.skip('non-docker execution. Test UM only in docker environment')

    um_fw_name = um_config.get('um_config.fw_name', '')
    um_fw_path = f'{server_handler.fut_base_dir}/resource/um/{um_fw_name}'
    um_fw_md5_path = f'{server_handler.fut_base_dir}/resource/um/{um_fw_name}.md5'

    with step('Preparation'):
        if not Path(um_fw_path).is_file():
            pytest.skip(f'UM test FW image is missing in {um_fw_path}!\nSkipping UM test cases')

        if not Path(um_fw_md5_path).is_file():
            assert server_handler.run('tools/server/um/create_md5_file', get_um_fw_path()) == ExpectedShellResult
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='um')

    interface_name_eth_wan = dut_handler.capabilities.get_or_raise('interfaces.primary_wan_interface')

    server_handler.recipe.clear_full()
    with step('UM setup'):
        assert dut_handler.run(
            'tests/um/um_setup', get_command_arguments(
                dut_handler.capabilities.get('fw_download_path', '/tmp/pfirmware/'),
                interface_name_eth_wan,
            ),
        ) == ExpectedShellResult
    server_handler.recipe.mark_setup()


def get_um_fw_url(prefix=''):
    """Return URL to FW image file with optionally pre-pended prefix.

    Args:
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Returns:
        str: URL to FW image file.
    """
    um_fw_name = um_config.get('um_config.fw_name', '')
    curl_host = SERVER_HANDLER_GLOBAL.testbed_cfg.get('server.curl.host', 'http://fut.opensync.io:8000/')
    um_fw_url = f'{curl_host}/fut-base/resource/um/{prefix}{um_fw_name}'
    return um_fw_url


def get_um_fw_path(prefix=''):
    """Return path to FW image file with optionally pre-pended prefix.

    Args:
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Returns:
        str: Path to FW image file.
    """
    um_fw_name = um_config.get('um_config.fw_name', '')
    um_fw_path = f'{SERVER_HANDLER_GLOBAL.fut_base_dir}/resource/um/{prefix}{um_fw_name}'
    return um_fw_path


def duplicate_image(prefix=''):
    """Create duplicated FW image file with optionally pre-pended prefix.

    Args:
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Raises:
        Exception: _description_

    Returns:
        bool: Returns True if FW image file is created, False otherwise.
    """
    um_fw_name = um_config.get('um_config.fw_name', '')
    # Set file names for original iamge and for duplicated image
    um_fw_path = f'{SERVER_HANDLER_GLOBAL.fut_base_dir}/resource/um/{um_fw_name}'
    um_fw_prefix_path = f'{SERVER_HANDLER_GLOBAL.fut_base_dir}/resource/um/{prefix}{um_fw_name}'
    try:
        # Copy
        res = os.system(f'cp {um_fw_path} {um_fw_prefix_path}')
        if res != 0:
            raise Exception('Error creating duplicated image')
    except Exception as e:
        log.info(msg=e)
        return False

    return True


def remove_duplicate_image(prefix=''):
    """Remove duplicated FW image file with optionally pre-pended prefix.

    Args:
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Returns:
        bool: Returns True if FW image file is removed, False otherwise.
    """
    um_fw_name = um_config.get('um_config.fw_name', '')
    um_fw_prefix_path = f'{SERVER_HANDLER_GLOBAL.fut_base_dir}/resource/um/{prefix}{um_fw_name}'
    res = os.system(f'rm {um_fw_prefix_path}')
    if res != 0:
        log.warning(msg='Unable to remove duplicated image')

    return True


########################################################################################################################
test_um_corrupt_image_inputs = um_config.get('um_corrupt_image', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_corrupt_image_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_corrupt_image(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Create corrupted image and MD5 files'):
        log.info(msg='Creating corrupted unencrypted image')
        assert server_handler.run('tools/server/um/create_corrupt_image_file', get_um_fw_path()) == ExpectedShellResult
        assert server_handler.run('tools/server/um/create_md5_file', get_um_fw_path(prefix='corrupt_')) == ExpectedShellResult
    with step('Preparation'):
        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(prefix='corrupt_'),
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_corrupt_image', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_corrupt_md5_sum_inputs = um_config.get('um_corrupt_md5_sum', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_corrupt_md5_sum_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_corrupt_md5_sum(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Create corrupted MD5sum file and FW image file'):
        md5_fw_prefix = 'corrupt_md5_sum_'
        log.info(msg=f'Duplicating image with prefix {md5_fw_prefix}')
        assert duplicate_image(prefix=md5_fw_prefix)
        log.info(msg='Creating corrupted md5 sum')
        assert server_handler.run('tools/server/um/create_corrupt_md5_file', get_um_fw_path(prefix=md5_fw_prefix)) == ExpectedShellResult
    with step('Preparation'):
        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(prefix=md5_fw_prefix),
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_corrupt_md5_sum', test_cmd) == ExpectedShellResult
    with step('Cleanup'):
        assert remove_duplicate_image(prefix=md5_fw_prefix)


########################################################################################################################
test_um_download_image_while_downloading_inputs = um_config.get('um_download_image_while_downloading', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_download_image_while_downloading_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_download_image_while_downloading(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Preparation'):
        um_fw_name = um_config.get('um_config.fw_name', '')
        um_fw_path = f'{server_handler.fut_base_dir}/resource/um/{um_fw_name}'

        # Check for 1st image file and create 2nd FW image file.
        if not Path(um_fw_path).is_file():
            pytest.skip(f'UM test FW image is missing in {um_fw_path}!\nSkipping UM test cases')
        else:
            log.info(msg=f'UM test found original FW image: {um_fw_path}')
            # Make 2nd image with prefix.
            duplicate_image(prefix='copied_')

        um_fw_name_2 = um_config.get('um_config.fw_name', None)
        assert um_fw_name_2 is not None
        um_fw_name_2 = f"copied_{um_fw_name_2}"
        um_fw_path_2 = f'{server_handler.fut_base_dir}/resource/um/{um_fw_name_2}'
        um_fw_md5_path_2 = f'{server_handler.fut_base_dir}/resource/um/{um_fw_name_2}.md5'

        # Check for 2nd firmware image and md5 file needed for testcase.
        if not Path(um_fw_path_2).is_file():
            pytest.skip(f"UM test 2nd FW image is missing in {um_fw_path_2}!\nSkipping 'um_download_image_while_downloading' test case")
        else:
            log.info(msg=f"UM test found 2nd FW image: {um_fw_path_2}")

        # Create md5 file for 2nd image.
        if not Path(um_fw_md5_path_2).is_file():
            assert server_handler.run('tools/server/um/create_md5_file', get_um_fw_path('copied_')) == ExpectedShellResult

        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config['fw_path'],
            get_um_fw_url(),
            get_um_fw_url(prefix='copied_'),
            test_config['fw_dl_timer'],
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_download_image_while_downloading', test_cmd) == ExpectedShellResult
    with step('Cleanup'):
        assert remove_duplicate_image(prefix='copied_')


########################################################################################################################
test_um_missing_md5_sum_inputs = um_config.get('um_missing_md5_sum', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_missing_md5_sum_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_missing_md5_sum(test_config):
    dut_handler = pytest.dut_handler
    with step('Preparation'):
        md5_fw_prefix = 'missing_md5_sum_'
        log.info(msg=f'Duplicating image with prefix {md5_fw_prefix}')
        assert duplicate_image(prefix=md5_fw_prefix)
        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(prefix=md5_fw_prefix),
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_missing_md5_sum', test_cmd) == ExpectedShellResult
    with step('Cleanup'):
        assert remove_duplicate_image(prefix=md5_fw_prefix)


########################################################################################################################
test_um_set_firmware_url_inputs = um_config.get('um_set_firmware_url', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_set_firmware_url_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_set_firmware_url(test_config):
    dut_handler = pytest.dut_handler
    with step('Get UM firmware URL'):
        um_fw_url = get_um_fw_url()
    with step('Preparation'):
        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            um_fw_url,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_set_firmware_url', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_set_invalid_firmware_pass_inputs = um_config.get('um_set_invalid_firmware_pass', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_set_invalid_firmware_pass_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_set_invalid_firmware_pass(test_config):
    dut_handler = pytest.dut_handler
    with step('Generate invalid FW password'):
        # Generate FW password if not in testcase config
        fw_pass = generate_image_key() if 'fw_pass' not in test_config else test_config['fw_pass']
    with step('Preparation'):
        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(),
            fw_pass,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_set_invalid_firmware_pass', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_set_invalid_firmware_url_inputs = um_config.get('um_set_invalid_firmware_url', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_set_invalid_firmware_url_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_set_invalid_firmware_url(test_config):
    dut_handler = pytest.dut_handler
    with step('Preparation'):
        # Test arguments from device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        # Prepare not existing FW URL
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(prefix='non_existing_fw_url_'),
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_set_invalid_firmware_url', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_set_upgrade_dl_timer_abort_inputs = um_config.get('um_set_upgrade_dl_timer_abort', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_set_upgrade_dl_timer_abort_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_set_upgrade_dl_timer_abort(test_config):
    dut_handler = pytest.dut_handler
    with step('Preparation'):
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config['fw_path'],
            get_um_fw_url(),
            test_config['fw_dl_timer'],
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_set_upgrade_dl_timer_abort', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_set_upgrade_dl_timer_end_inputs = um_config.get('um_set_upgrade_dl_timer_end', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_set_upgrade_dl_timer_end_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_set_upgrade_dl_timer_end(test_config):
    dut_handler = pytest.dut_handler
    with step('Preparation'):
        # Test arguments from testcase config and device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(),
            test_config['fw_dl_timer'],
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_set_upgrade_dl_timer_end', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_set_upgrade_timer_inputs = um_config.get('um_set_upgrade_timer', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_set_upgrade_timer_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_set_upgrade_timer(test_config):
    dut_handler = pytest.dut_handler
    with step('Preparation'):
        # Test arguments from testcase config and device capabilities
        # Get FW download path from device capabilities if not found in testcase config
        test_cmd = get_command_arguments(
            dut_handler.capabilities.get('fw_download_path') if 'fw_path' not in test_config else test_config.get('fw_path'),
            get_um_fw_url(),
            test_config['fw_up_timer'],
            um_config.get('um_config.fw_name', ''),
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_set_upgrade_timer', test_cmd) == ExpectedShellResult


########################################################################################################################
test_um_verify_firmware_url_length_inputs = um_config.get('um_verify_firmware_url_length', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m4()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_um_verify_firmware_url_length_inputs)
@pytest.mark.dependency(depends=["um_fut_setup_dut"], scope='session')
def test_um_verify_firmware_url_length(test_config):
    dut_handler = pytest.dut_handler
    with step('Preparation'):
        # Test arguments from testcase config
        url_max_length = test_config.get('url_max_length')

        firmware_url_base = "http://fut.opensync.io:8000/fut-base/resource/um/"
        firmware_url_suffix = ".img"
        url_mid_length = url_max_length - len(firmware_url_base) - len(firmware_url_suffix)
        # Make sure there is space for middle part of URL
        assert url_mid_length > 0

        # Create middle part of the URL from random characters and insert it in FW URL
        firmware_url_mid = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=url_mid_length))
        firmware_url = f'{firmware_url_base}{firmware_url_mid}{firmware_url_suffix}'
        # Make sure total length of firmware URL is exactly max length
        assert len(firmware_url) == url_max_length

        # Get FW download path from device capabilities if not found in testcase config
        fw_download_path = dut_handler.capabilities.get('fw_download_path') if 'fw_download_path' not in test_config else test_config.get('fw_download_path')
        assert fw_download_path is not None and fw_download_path != ''

        test_cmd = get_command_arguments(
            fw_download_path,
            firmware_url,
        )
    with step('Testcase'):
        assert dut_handler.run('tests/um/um_verify_firmware_url_length', test_cmd) == ExpectedShellResult
