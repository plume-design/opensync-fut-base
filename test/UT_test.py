import os
from copy import deepcopy
from pathlib import Path

import pytest

import framework.tools.logger
from framework.tools.functions import step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

skip_ut_test = False
ut_test_skip_reason = ''
ut_folder_name = ''
global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

# Read entire testcase configuration
ut_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='UT')


ut_name = ut_config.get('ut.ut_name', '')
ut_res_path = f'{SERVER_HANDLER_GLOBAL.fut_base_dir}/resource/ut/'

try:
    if ut_name:
        ut_tar_path = f'{ut_res_path}{ut_name}.tar'
        ut_tar_bz2_path = f'{ut_res_path}{ut_name}.tar.bz2'
        ut_folder_path = f'{ut_res_path}{ut_name}'
        if Path(ut_folder_path).is_dir():
            log.info(msg=f'{ut_folder_path} found, using it for UT collection')
            ut_folder_name = ut_name
        elif Path(ut_tar_path).is_dir():
            log.info(msg=f'{ut_tar_path} found, extracting it and using it for UT collection')
            SERVER_HANDLER_GLOBAL.execute(f'mkdir -p {ut_folder_path}')
            SERVER_HANDLER_GLOBAL.execute(f'tar -xf {ut_tar_path.replace(".bz2", "")} -C {ut_folder_path}')
            ut_folder_name = ut_name
        elif Path(ut_tar_bz2_path).is_file():
            log.info(msg=f'{ut_tar_bz2_path} found, extracting it and using it for UT collection')
            SERVER_HANDLER_GLOBAL.execute(f'mkdir -p {ut_folder_path}')
            SERVER_HANDLER_GLOBAL.execute(f'bzip2 -d {ut_tar_bz2_path}')
            SERVER_HANDLER_GLOBAL.execute(f'tar -xf {ut_tar_bz2_path.replace(".bz2", "")} -C {ut_folder_path}')
            ut_folder_name = ut_name
        else:
            skip_ut_test = True
            ut_test_skip_reason = f'No folder {ut_folder_path} or {ut_tar_bz2_path} found, skipping!'
    else:
        log.info(msg='UT_config ut_name not provided, will use first .tar.bz2 found, if none, will skip UT_test!')
        ut_found = False
        for item in os.listdir(ut_res_path):
            if item.endswith('.tar.bz2'):
                ut_folder_name = item.replace('.tar.bz2', '')
                ut_folder_path = f'{ut_res_path}{ut_folder_name}'

                if Path(ut_folder_path).is_dir():
                    SERVER_HANDLER_GLOBAL.execute(f'rm -rf {ut_folder_path}')

                item_path = Path(ut_res_path, item)
                item_posixpath = item_path.as_posix()

                SERVER_HANDLER_GLOBAL.execute(f'mkdir -p {ut_folder_path}')
                SERVER_HANDLER_GLOBAL.execute(f'bzip2 -kfd {item_posixpath}')
                SERVER_HANDLER_GLOBAL.execute(f'tar -xf {item_posixpath.replace(".bz2", "")} -C {ut_folder_path}')

                ut_found = True
                break
        if not ut_found:
            skip_ut_test = True
            ut_test_skip_reason = f'No *.tar.bz2 found in {ut_res_path}, skipping!'
except Exception as e:
    skip_ut_test = True
    ut_test_skip_reason = f'Exception caught while collecting UT_test\n{e}'


def get_unit_test_config(folder=''):
    fut_base_dir = SERVER_HANDLER_GLOBAL.fut_base_dir
    _ut_config = []
    unit_test_path = f"{fut_base_dir}/resource/ut/{folder}"
    for path, _sub_dirs, files in os.walk(unit_test_path):
        if files and len(files) == 1 and files[0] == "unit":
            test_path = f'{str(path).replace(str(fut_base_dir), "").replace("shell/", "")}/unit'
            ut_cfg_def = {
                "path": test_path,
                "name": test_path.split('/')[-2],
            }
            ut_cfg_add = SERVER_HANDLER_GLOBAL.dut["test_cfg"].get(ut_cfg_def["name"], {})
            ut_cfg = {**ut_cfg_def, **ut_cfg_add}
            _ut_config.append(deepcopy(ut_cfg))
    return _ut_config


ut_config = get_unit_test_config(folder=ut_folder_name)

if not ut_config:
    ut_config.append({
        "name": "No_UT_tests",
    })
    skip_ut_test = True
    ut_test_skip_reason = ut_test_skip_reason if ut_test_skip_reason else 'No UT tests collected'


@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="unit_test_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_unit_test_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    if skip_ut_test:
        pytest.skip(ut_test_skip_reason)
    assert dut_handler.clear_tests_folder()
    with step('Transfer'):
        assert dut_handler.transfer(manager='ut')
        assert dut_handler.clear_resource_folder()
        assert dut_handler.transfer(folder=ut_res_path, to=dut_handler.fut_dir + '/resource/')
    server_handler.recipe.clear_full()
    with step('UT setup'):
        assert dut_handler.run('tests/ut/ut_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()


@pytest.mark.skipif(condition=skip_ut_test, reason=ut_test_skip_reason)
@pytest.mark.require_dut()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize(
    'test_config', ut_config,
    ids=[i['name'] for i in ut_config],
)
@pytest.mark.dependency(depends=["unit_test_fut_setup_dut"], scope='session')
def test_unit_test_(test_config):
    dut_handler = pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_resource_folder()
        assert dut_handler.transfer(folder=ut_res_path, to=dut_handler.fut_dir + '/resource/')
    with step('Testcase'):
        log.info(msg=f'Executing unit test {test_config["name"]}')
        assert dut_handler.run(test_config['path'], suffix="", folder='') == ExpectedShellResult
