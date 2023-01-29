"""Module to configure test runs.

Refer to official pytest documentation for more details.
"""

import json
import os
import re
import sys
import time
from enum import Enum
from pathlib import Path

import allure
import pytest

import framework.tools.logger
from framework.tools.functions import FailedException, output_to_json
from .globals import SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

report_map = {
    'test_name': None,
    'group': {
        'FRM': [],
        'RECIPE': [],
    },
}

RUNTEST_REGEX = r'([0-9a-zA-Z_-]+(\[([^\]]|\[\])*\])?(\*[0-9]+)?)'

PYTEST_DEFAULT_TIMEOUT = 60
PYTEST_TIMEOUT_ADD = 30

compat_test_list = [
    "compat_client_device_version",
    "compat_client_init",
    "compat_client_ready",
    "compat_client_transfer",
    "compat_client2_device_version",
    "compat_client2_init",
    "compat_client2_ready",
    "compat_client2_transfer",
    "compat_dut_bridge_type",
    "compat_dut_device_version",
    "compat_dut_init",
    "compat_dut_ready",
    "compat_dut_tmp_mount_executable",
    "compat_dut_transfer",
    "compat_dut_verify_reg_domain",
    "compat_fut_release_version",
    "compat_is_transfer_only",
    "compat_main_init",
    "compat_ref_device_version",
    "compat_ref_init",
    "compat_ref_prevent_reboot",
    "compat_ref_ready",
    "compat_ref_tmp_mount_executable",
    "compat_ref_transfer",
    "compat_ref_verify_reg_domain",
    "compat_ref2_device_version",
    "compat_ref2_init",
    "compat_ref2_prevent_reboot",
    "compat_ref2_ready",
    "compat_ref2_tmp_mount_executable",
    "compat_ref2_transfer",
    "compat_ref2_verify_reg_domain",
    "compat_server_device_version",
    "compat_server_ready",
    "compat_unblock_dut_wan_mng_addresses",
]

setup_test_dict = {
    'brv': {
        'setup_name_dut': 'brv_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'cm2': {
        'setup_name_dut': 'cm2_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'dm': {
        'setup_name_dut': 'dm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'fsm': {
        'setup_name_dut': 'fsm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_client': 'fsm_fut_setup_client',
        'setup_item_client': None,
        'added_client': False,
    },
    'hello': {
        'setup_name_dut': 'hello_world_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'lm': {
        'setup_name_dut': 'lm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'ltem': {
        'setup_name_dut': 'ltem_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'nfm': {
        'setup_name_dut': 'nfm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_client': 'nfm_fut_setup_dut',
        'setup_item_client': None,
        'added_client': False,
    },
    'ng': {
        'setup_name_dut': None,
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_ref': None,
        'setup_item_ref': None,
        'added_ref': False,
        'setup_name_client': None,
        'setup_item_client': None,
        'added_client': False,
    },
    'nm2': {
        'setup_name_dut': 'nm2_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_client': 'nm2_fut_setup_client',
        'setup_item_client': None,
        'added_client': False,
    },
    'onbrd': {
        'setup_name_dut': 'onbrd_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_ref': 'onbrd_fut_setup_ref',
        'setup_item_ref': None,
        'added_ref': False,
        'setup_name_client': 'onbrd_fut_setup_client',
        'setup_item_client': None,
        'added_client': False,
    },
    'othr': {
        'setup_name_dut': 'othr_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_ref': 'othr_fut_setup_ref',
        'setup_item_ref': None,
        'added_ref': False,
        'setup_name_client': 'othr_fut_setup_client',
        'setup_item_client': None,
        'added_client': False,
        'setup_name_client2': 'othr_fut_setup_client2',
        'setup_item_client2': None,
        'added_client2': False,
    },
    'pm': {
        'setup_name_dut': 'pm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'qm': {
        'setup_name_dut': 'qm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'sm': {
        'setup_name_dut': 'sm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_ref': 'sm_fut_setup_ref',
        'setup_item_ref': None,
        'added_ref': False,
    },
    'um': {
        'setup_name_dut': 'um_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'unit': {
        'setup_name_dut': 'unit_test_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'vpnm': {
        'setup_name_dut': 'vpnm_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
    },
    'wm2': {
        'setup_name_dut': 'wm2_fut_setup_dut',
        'setup_item_dut': None,
        'added_dut': False,
        'setup_name_ref': 'wm2_fut_setup_ref',
        'setup_item_ref': None,
        'added_ref': False,
        'setup_name_ref2': 'wm2_fut_setup_ref2',
        'setup_item_ref2': None,
        'added_ref2': False,
        'setup_name_client': 'wm2_fut_setup_client',
        'setup_item_client': None,
        'added_client': False,
    },
}

device_markers = [
    ('dut', 'require_dut'),
    ('ref', 'require_ref'),
    ('ref2', 'require_ref2'),
    ('client', 'require_client'),
    ('client2', 'require_client2'),
]


def pytest_addoption(parser):
    """Handle test run options.

    Handles testcase selection and running options.

    Args:
        parser (obj): Parser option.
    """
    # Collection only
    group = parser.getgroup(name="collect")
    # pytest-native '--collect-only' option collects tests without execution
    group.addoption('--listtests', '--list-tests', action="store_true",
                    help="collected tests with configuration entry")
    group.addoption('--listconfigs', '--list-configs', action="store_true",
                    help="collected tests, parametrized with all configuration scenarios")
    group.addoption('--listconfigsdetails', '--list-configs-details', action="store_true",
                    help="collected tests, parametrized with all configuration scenarios with parameters")
    group.addoption('--listignored', '--list-ignored', action="store_true",
                    help="collected tests with ignore_collect flag")
    group.addoption('--listignoredconfig', '--list-ignored-config', action="store_true",
                    help="collected tests with ignore_collect flag parametrized with all configuration scenarios")
    group.addoption('--listignoredparams', '--list-ignored-params', action="store_true",
                    help="collected tests with ignore_collect flag parametrized with all configuration scenarios with parameters")
    group.addoption('--listmarkers', '--list-markers', action="store_true",
                    help="all tests and their markers, regardless of testcase configuration")
    group.addoption('--json', action="store", default=False,
                    help="saves listed output of list* options into json file, if not list option is defined, output test configuration")
    # Running and selection options
    group = parser.getgroup(name="general")
    group.addoption('--runtest', '--run-test', action="store", default=False,
                    help="run a subset of collected and configured tests")
    group.addoption('--transferonly', '--transfer-only', action="store_true", default=False,
                    help="transfer files to devices without test execution")
    group.addoption('--ignoreosrtversion', '--ignore-osrt-version', action="store_true", default=False,
                    help="Ignore OSRT version COMPAT check")
    parser.addoption('--dbg', action="store_true",
                     help="Increase logging level to debug and show extra info")
    group.addoption('--logpass', '--log-pass', action="store_true",
                    help="Enable LOGREAD on PASS-ed testcases")
    group.addoption('--logpull', '--log-pull', action="store_true",
                    help="Enable logpull Allure attachment for failed test cases")
    group.addoption('--skipl2', action="store_true", default=False,
                    help="Skip LEVEL2 testcase steps")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    log.debug(msg='Entered conftest.py')
    pytest.server_handler = None
    # collection markers
    # ignore_collect marker - can be added in test config files for specific models/tests
    config.addinivalue_line(
        "markers", "ignore_collect: mark tests that will not be collected",
    )
    # always_run marker
    config.addinivalue_line(
        "markers", "always_run: mark tests that will always run regardless of other markers",
    )
    # Test type markers
    config.addinivalue_line(
        "markers", "require_dut: mark test that require only DUT device",
    )
    config.addinivalue_line(
        "markers", "require_ref: mark test that require REF device",
    )
    config.addinivalue_line(
        "markers", "require_ref2: mark test that require REF2 device",
    )
    config.addinivalue_line(
        "markers", "require_client: mark test that require Client device",
    )
    config.addinivalue_line(
        "markers", "dfs: mark test that uses DFS channels",
    )
    # Device type compatibility
    config.addinivalue_line(
        "markers", "gateway_compatible: mark test that are compatible with device type GATEWAY (TARGET_CAP_GATEWAY)",
    )
    config.addinivalue_line(
        "markers", "extender_compatible: mark test that are compatible with device type EXTENDER (TARGET_CAP_EXTENDER)",
    )
    # OpenSync Integration Milestones markers
    config.addinivalue_line(
        "markers", "os_integration_m1: mark test that are part of OpenSync integration milestone M1",
    )
    config.addinivalue_line(
        "markers", "os_integration_m2: mark test that are part of OpenSync integration milestone M2",
    )
    config.addinivalue_line(
        "markers", "os_integration_m3: mark test that are part of OpenSync integration milestone M3",
    )
    config.addinivalue_line(
        "markers", "os_integration_m4: mark test that are part of OpenSync integration milestone M4",
    )
    pytest.listtests = config.option.listtests
    pytest.listconfigs = config.option.listconfigs
    pytest.listmarkers = config.option.listmarkers
    pytest.transferonly = config.option.transferonly
    pytest.runtest = config.option.runtest
    pytest.logpull = config.option.logpull

    if pytest.logpull and not pytest.runtest:
        raise Exception('--log-pull option can only be used alongside --run-test option!')

    if config.option.allure_report_dir:
        log.debug(f'config.option.allure_report_dir:{config.option.allure_report_dir}')
        if not Path(config.option.allure_report_dir).is_absolute():
            log.warning(msg='pytest.conftest.pytest_configure: Assuming path is relative to fut_base_dir')
            config.option.allure_report_dir = str(Path(SERVER_HANDLER_GLOBAL.fut_base_dir).joinpath(config.option.allure_report_dir))
    pytest.skipl2 = config.option.skipl2


@pytest.fixture(scope='session')
def is_transfer_only(pytestconfig):
    """Determine if session is 'transfer only'.

    Using this mark no testcases are executed.
    Test scripts are still transferred to the devices.

    Args:
        pytestconfig (obj): Configuration

    Returns:
        (bool): True if transfer only is set, False otherwise.
    """
    return pytestconfig.getoption("transferonly")


@pytest.fixture(scope='session')
def ignore_osrt_version(pytestconfig):
    """Get ignore OSRT version option.

    Args:
        pytestconfig (obj): Configuration

    Returns:
        (bool): True if OSRT version needs to be checked, False otherwise.
    """
    return pytestconfig.getoption("ignoreosrtversion")


def pytest_generate_tests(metafunc):
    """Generate clones of the testcase."""
    def _get_test_multiply(tn):
        """Determine testcase multiplicator.

        Args:
            tn (str): Testcase name

        Raises:
            Exception: Failed to parse '--runtest' option value.

        Returns:
            (int): Testcase multiplicator
        """
        run_only_test = metafunc.config.getoption("runtest")
        test_multiply = 1
        try:
            run_only_test_cfg = [x[0] for x in re.findall(RUNTEST_REGEX, run_only_test)]
        except Exception as e:
            raise Exception(f'Failed to parse --runtest value ({run_only_test})\n{e}')

        for test in run_only_test_cfg:
            # Acquire test name base
            test_name = test.split('*')[0] if '[' not in test else test.split('[')[0]
            if test_name != tn:
                continue
            # Check if there are [ ] configuration for specific test
            if '[' in test and ']' in test:
                # Acquire test list between [] value
                test_opts = test.split('[')[1].split(']')
                try:
                    test_multiply = int(test_opts[1].replace('*', ''))
                except Exception:
                    continue
            else:
                try:
                    test_multiply = int(test.split('[')[0].split('*')[1])
                except Exception:
                    test_multiply = 1
        return test_multiply

    try:
        if 'repeat' not in metafunc.fixturenames:
            name = metafunc.function.__name__.replace('test_', '', 1)
            multiply = _get_test_multiply(name)
            if multiply != 1:
                metafunc.fixturenames.append('repeat')
                metafunc.parametrize('repeat', range(0, multiply))
    except Exception:
        pass


def pytest_collection_modifyitems(session, config, items):
    """Collect testcases and modify testcases after collection has beed performed.

    Support for options:
    Can only list available testcases, does not execute.
    Can only list available testcase configuration, does not execute.
    Can only list ignored testcases, does not execute.
    Can only list ignored testcase configuration, does not execute.
    Can only list testcase markers, does not execute.
    Can handle the option to only transport test scripts to devices, does not execute.

    Args:
        session (pytest.Session): Pytest session object
        config (pytest.Config): The pytest config object
        items (List[pytest.Item]): List of item objects
    """
    def _get_item_config(item):
        try:
            tcc = item._request.node.callspec.params
            if isinstance(tcc, Enum):
                return {}
            if 'test_config' in tcc:
                if isinstance(tcc['test_config'], Enum):
                    return {}
                return tcc['test_config']
            return tcc
        except Exception:
            return {}

    def _get_setup_item(ip):
        _si = []
        for _dn in SERVER_HANDLER_GLOBAL.devices_cfg:
            try:
                if setup_test_dict[ip][f'setup_item_{_dn}'] and not \
                        setup_test_dict[ip][f'added_{_dn}']:
                    setup_test_dict[ip][f'added_{_dn}'] = True
                    _si.append(setup_test_dict[ip][f'setup_item_{_dn}'])
            except Exception:
                pass
        if _si:
            log.debug(f'Adding setup items {[f"{i.name}," for i in _si]}')
        return _si

    def _check_cfg_option(_ic, _opt):
        return False if _opt not in _ic else _ic[_opt]

    log.debug(msg='Entered pytest_collection_modifyitems')
    tr = config.pluginmanager.get_plugin('terminalreporter')
    fut_pytest_path = os.getenv('FUT_PYTEST_PATH')

    # Ensure the `always_run` marker is always selected if any marker is given
    markexpr = config.getoption("markexpr", 'False')
    config.option.markexpr = f"(always_run and not ignore_collect) or ({markexpr})" if markexpr else ''
    config.option.markexpr = config.option.markexpr.replace('"', '')

    run_only_test = config.getoption("runtest")
    output_test_names = []
    if run_only_test:
        try:
            output_test_names = [x[0] for x in re.findall(RUNTEST_REGEX, run_only_test)]
        except Exception as e:
            raise Exception(f'Failed to parse --runtest value ({run_only_test})\n{e}')

    # Ensure milestone integration markers order is respected
    if 'os_integration_m2' in config.option.markexpr:
        config.option.markexpr = f"(os_integration_m1 or ({config.option.markexpr}))"
    elif 'os_integration_m3' in config.option.markexpr:
        config.option.markexpr = f"(os_integration_m1 or os_integration_m2 or ({config.option.markexpr}))"
    elif 'os_integration_m4' in config.option.markexpr:
        config.option.markexpr = f"(os_integration_m1 or os_integration_m2 or os_integration_m3 or ({config.option.markexpr}))"

    to_json_file = config.getoption('json')

    if config.getoption('listtests'):
        _org_names = []
        log.debug(msg='Listing collected testcases for selected configuration')
        tr.write_line('\nAvailable test cases:', bold=True)
        for tc in items:
            if 'setup' in tc.name or not _check_cfg_option(_get_item_config(tc), 'ignore_collect'):
                if tc.originalname not in _org_names:
                    _t = tc.originalname.replace('test_', '', 1)
                    if run_only_test and _t not in output_test_names:
                        continue
                    _org_names.append(_t)
        _org_names = list(dict.fromkeys(_org_names))
        for _on in _org_names:
            tr.write_line(f"\t{_on}")
        if to_json_file:
            output_to_json(_org_names, to_json_file)
        pytest.exit("Listed available test cases.")

    if config.getoption('listconfigs') or config.getoption('listconfigsdetails'):
        _configs_data = {}
        log.debug(msg='List available configurations for selected model')
        tr.write_line('\nAvailable test configurations:', bold=True)
        for tc in items:
            if 'setup' in tc.name or not _check_cfg_option(_get_item_config(tc), 'ignore_collect'):
                _tc_cfg = _get_item_config(tc)
                tr.write_line(f'{40 * "-"}\n{tc.name}')
                if run_only_test and tc.name not in output_test_names:
                    continue
                _configs_data[tc.name] = _tc_cfg
                if config.getoption('listconfigsdetails'):
                    tr.write_line(f'Params:\n{json.dumps(_get_item_config(tc), sort_keys=True, indent=4)}\n{40 * "-"}\n')
        if to_json_file and not config.getoption('listconfigsdetails'):
            output_to_json(list(_configs_data.keys()), json_file=to_json_file)
        elif to_json_file and config.getoption('listconfigsdetails'):
            output_to_json(_configs_data, json_file=to_json_file)
        pytest.exit("Listed available test configurations.")

    if config.getoption('listignored'):
        _org_names = []
        log.debug(msg='Listing ignored testcases for selected configuration')
        tr.write_line('\nIgnored test cases:', bold=True)
        for tc in items:
            if _check_cfg_option(_get_item_config(tc), 'ignore_collect'):
                if tc.originalname not in _org_names:
                    _t = tc.originalname.replace('test_', '', 1)
                    if run_only_test and _t not in output_test_names:
                        continue
                    _org_names.append(_t)
        _org_names = list(dict.fromkeys(_org_names))
        for _on in _org_names:
            tr.write_line(f"\t{_on}")
        if to_json_file:
            output_to_json(_org_names, json_file=to_json_file)
        pytest.exit("Listed ignored test cases.")

    if config.getoption('listignoredconfig') or config.getoption('listignoredparams'):
        _configs_data = {}
        log.debug(msg='Listing ignored testcases for selected configuration with configuration/params')
        tr.write_line('\nIgnored test cases:', bold=True)
        for tc in items:
            if _check_cfg_option(_get_item_config(tc), 'ignore_collect'):
                _tc_cfg = _get_item_config(tc)
                tr.write_line(f'{40 * "-"}\n{tc.name}')
                if run_only_test and tc.name not in output_test_names:
                    continue
                _configs_data[tc.name] = _tc_cfg
                if config.getoption('listignoredparams'):
                    tr.write_line(f'Params:\n{json.dumps(_tc_cfg, sort_keys=True, indent=4)}\n{40 * "-"}\n')
        if to_json_file and not config.getoption('listignoredparams'):
            output_to_json(list(_configs_data.keys()), json_file=to_json_file)
        elif to_json_file and config.getoption('listignoredparams'):
            output_to_json(_configs_data, json_file=to_json_file)
        pytest.exit("Listed ignored test cases with configuration/params.")

    if config.getoption('listmarkers'):
        log.debug(msg='List all testcases and their markers, regardless of testcase configuration')
        tr.write_line('All test cases with markers:', bold=True)
        # The names are split to squash all configs for the same testcase, markers are the same
        names_and_markers = {item.name.split("[")[0]: [i.name for i in item.iter_markers()] for item in items}
        for name, markers in names_and_markers.items():
            tr.write_line(f'\t{name}: {markers}')
        pytest.exit("Listed all testcases and their markers, regardless of testcase configuration.")

    # If only --json is passed, we output FUT test configuration
    if to_json_file:
        if run_only_test:
            data = {}
            for name, config in SERVER_HANDLER_GLOBAL.dut['test_cfg'].cfg.items():
                if name not in output_test_names:
                    continue
                data[name] = config
            output_to_json(data, json_file=to_json_file)
        else:
            output_to_json(SERVER_HANDLER_GLOBAL.dut['test_cfg'].cfg, json_file=to_json_file)
        pytest.exit(f"Saved FUT test configuration to JSON file {to_json_file}")

    log.debug(msg='Retrieving test configurations')
    is_transfer_only_bool = config.getoption("transferonly")
    tmp_items = items.copy()
    item_names = []
    # Looking for pytest items for test setup files
    for item in tmp_items:
        item_names.append(item.name)
        item_prefix = item.name.split('_')[0]
        for device_name in SERVER_HANDLER_GLOBAL.devices_cfg:
            for key in setup_test_dict:
                try:
                    if not setup_test_dict[key][f'setup_item_{device_name}'] and key == item_prefix:
                        for item_s in tmp_items:
                            if setup_test_dict[key][f'setup_name_{device_name}'] and item_s.name == setup_test_dict[key][f'setup_name_{device_name}']:
                                setup_test_dict[key][f'setup_item_{device_name}'] = item_s
                except Exception:
                    pass

    items.clear()

    def _get_multiply_test_list(rl, ml, tn):
        """Multiply testcase list to allow multiple execution.

        Starts with empty list and appends testcase names to the list.

        Args:
            rl (list):
            ml (int): Multiplier
            tn (str): Testcase name

        Returns:
            (list): List of testcase names to execute.
        """
        names = []
        for idx in rl:
            if ml != 1:
                for i in range(ml):
                    names.append(f'{tn}[{idx}-{i}]')
            else:
                names.append(f'{tn}[{idx}]')
        return names

    def _get_run_only_test_list():
        """Return list of testcases to run.

        UT and NG testcases are handled separately. They will not be added to full runs.

        Raises:
            Exception: Failed to parse runtest option.
            Exception: Invalid run configuration.
        """
        run_only_test = config.getoption("runtest")

        if run_only_test is False:
            return False
        _run_only_test_list = []
        try:
            run_only_test_cfg = [x[0] for x in re.findall(RUNTEST_REGEX, run_only_test)]
        except Exception as e:
            raise Exception(f'Failed to parse --runtest value ({run_only_test})\n{e}')

        def _is_negative(s):
            """Determine if negative.

            Args:
                s (str): String to check

            Returns:
                (bool): True if string starts with '-', False otherwise.
            """
            return s.startswith('-')

        for test in run_only_test_cfg:
            # Check if there are [ ] configuration for specific test
            # Acquire test name base
            test_name = test.split('*')[0] if '[' not in test else test.split('[')[0]
            # Acquire test list between [] value
            try:
                if '[' in test and ']' in test:
                    test_opts = test.split('[')[1].split(']')
                else:
                    test_opts = test.split('*')
                test_configs = test_opts[0]
            except Exception:
                test_opts = None
                test_configs = None

            try:
                test_multiply = int(test_opts[1].replace('*', ''))
            except Exception:
                test_multiply = 1

            # Check if test list is list - [1, 3, 5, 6] etc.
            try:
                is_list = eval(f'[{test_configs}]')
            except Exception:
                is_list = False

            log.debug(f'test_name: {test_name} | test_configs: {test_configs} | test_multiply: {test_multiply}')

            if '[' in test and ']' in test:
                # Check if : is in the test list config which represent range of tests
                if ':' in test_configs:
                    # Check if test list range is from some number to all of the rest available:
                    # [4:] -> from test config 4 to the all rest
                    if (
                            not _is_negative(test_configs.split(':')[0]) and test_configs.split(':')[0].isdigit()
                    ) and (
                            not _is_negative(test_configs.split(':')[1]) and not test_configs.split(':')[1].isdigit()
                    ):
                        cfg_range = range(int(test_configs.split(':')[0]), int(sum(f'{test_name}[' in s for s in item_names)))
                    # Check if test list range is from first to until given number:
                    # - [:5] -> from test config 0 to the test config 5 (including 5)
                    elif (
                            not _is_negative(test_configs.split(':')[0]) and not test_configs.split(':')[0].isdigit()
                    ) and (
                            not _is_negative(test_configs.split(':')[1]) and test_configs.split(':')[1].isdigit()
                    ):
                        cfg_range = range(0, int(test_configs.split(':')[1]) + 1)
                    # Check if test list range is from number to number:
                    # - [2:5] -> from test config 2 (including 2) to the test config 5 (including 5)
                    elif (
                            not _is_negative(test_configs.split(':')[0]) and test_configs.split(':')[0].isdigit()
                    ) and (
                            not _is_negative(test_configs.split(':')[1]) and test_configs.split(':')[1].isdigit()
                    ):
                        cfg_range = range(int(test_configs.split(':')[0]), int(test_configs.split(':')[1]) + 1)
                    # Raise exception for any non supported list configuration
                    else:
                        raise Exception(f'Invalid {test} run configuration given! Given: {test_configs}')

                    for ns in _get_multiply_test_list(cfg_range, test_multiply, test_name):
                        if ns not in item_names:
                            log.warning(f'Test {ns} was not found in test collection. Will not add')
                            continue
                        if ns not in _run_only_test_list:
                            log.debug(f'Appending test: {ns}')
                            _run_only_test_list.append(ns)
                # Check if test list value is ALL ([ALL] / [all])
                elif test_configs.upper() == 'ALL':
                    if test_name == test_configs or test_configs in ['all', 'ALL']:
                        pass
                    elif f'{test}[0]' not in item_names:
                        log.warning(f'Test {test} was not found in test collection. Will not add')
                        continue
                    test_name = test.split('[')[0].split('*')[0]
                    _run_only_test_list.append(f'{test_name}[ALL]')
                # Check if test list is python list
                # [3,5,10] -> Run configuration 3, 5 and 10
                # [3,5,-15] -> Run configuration 3, 5. Configuration -15 will be logged as warning message since it does not exist
                elif is_list:
                    for ns in _get_multiply_test_list(is_list, test_multiply, test_name):
                        if ns not in item_names:
                            log.warning(f'Test {ns} was not found in test collection. Will not add')
                            continue
                        if ns not in _run_only_test_list:
                            log.debug(f'Appending test: {ns}')
                            _run_only_test_list.append(ns)
                else:
                    raise Exception(f'Invalid {test_name} run configuration given! Given: {test}')
            # Check if test list is not closed or opened
            elif '[' in test or ']' in test:
                raise Exception(f'Invalid {test} run configuration given! Given: {test}')
            # If there is no [ ] in string, it means to run all configurations
            else:
                if test_name == test_configs or test_configs in ['all', 'ALL']:
                    pass
                elif f'{test}[0]' not in item_names:
                    log.warning(f'Test {test} was not found in test collection. Will not add')
                    continue
                test_name = test.split('[')[0].split('*')[0]
                _run_only_test_list.append(f'{test_name}[ALL]')
        # Check if _run_only_test_list is not empty
        if not _run_only_test_list:
            raise Exception(f'No tests found matching --runtest option {run_only_test}')
        return _run_only_test_list

    run_only_test_count = 0
    run_only_test_list = _get_run_only_test_list()

    for item in tmp_items:
        if not is_transfer_only_bool and item.name == 'compat_is_transfer_only':
            continue

        test_case_configuration = _get_item_config(item)
        item_prefix = item.name.split('_')[0]
        if test_case_configuration or test_case_configuration == {}:
            # Set test markers through testcase configuration
            if 'marks' in test_case_configuration:
                for mark_name in test_case_configuration['marks']:
                    item.add_marker(mark_name)
            if run_only_test_list:  # Do not optimize this line
                if item.name in compat_test_list:
                    items.append(item)
                    continue
                # Check it test name is present in run_only_test_list or test_name[ALL] which means to run all configurations
                if item.name in run_only_test_list or re.sub(r"\[.*]", '[ALL]', item.name) in run_only_test_list:
                    items += _get_setup_item(item_prefix)
                    log.debug(msg=f'Appending {item.name} to list of tests for execution')
                    items.append(item)
                    run_only_test_count += 1
            # Run ALL UT tests only if explicitly defined by -path test/UT_test.py - Only DUT setup
            elif item_prefix == 'unit' and 'test/UT_test.py' in fut_pytest_path:
                if item.name in compat_test_list:
                    items.append(item)
                # Edit collected UT test name to match the naming
                try:
                    # Acquire UT test name from config value
                    ut_test_name = f"{item.name.split('[')[1]}".replace(']', '')
                    # UT test do not support multiple configurations, so 0 is hardcoded
                    item.name = f'unit_test_{ut_test_name}[0]'
                except Exception as e:
                    log.warning(f'Failed to rename test {item.name}\n{e}')
                items.append(item)
            # Run ALL NG tests only if explicitly defined by -path test/NG_test.py - Only DUT setup
            elif item_prefix == 'ng' and 'test/NG_test.py' in fut_pytest_path:
                if item.name in compat_test_list:
                    items.append(item)
                items.append(item)
            # Do not add UT and NG tests into full runs, they are only explicitly run if appropriate --path is passed!
            elif item_prefix in ['unit', 'ng']:
                continue
            else:
                # Manage test case execution with 'skip' key in test configuration. Test case is skipped.
                if _check_cfg_option(test_case_configuration, 'skip'):
                    # Add skip message from test configuration.
                    skip_reason = 'Missing skip reason' if 'skip_msg' not in test_case_configuration else test_case_configuration['skip_msg']
                    skip_marker = pytest.mark.skip(reason=skip_reason)
                    log.warning(msg=f'{item.name} is marked with skip, will skip')
                    item.add_marker(skip_marker)
                # Manage test case execution with 'ignore_collect' key. Test case is not collected.
                if _check_cfg_option(test_case_configuration, 'ignore_collect'):
                    log.warning(msg=f'{item.name} is marked with ignore_collect, will not collect')
                else:
                    if item.name in compat_test_list or item.originalname.replace('test_', '', 1) in SERVER_HANDLER_GLOBAL.dut['test_cfg'].cfg:
                        log.debug(msg=f'appending {item.name} to list of tests for execution')
                        items += _get_setup_item(item_prefix)
                        items.append(item)
                    else:
                        # Do not log missing entries for setup since they will almost never have entry in configuration
                        if 'setup' not in item.name:
                            log.debug(msg=f'{item.name} does not contain entry in DUT test configuration, will not collect')
    used_devices = []
    org_expr = config.option.markexpr

    for item in items:
        for dm in device_markers:
            if item.get_closest_marker(dm[1]) and dm[0] not in used_devices:
                if dm not in used_devices:
                    used_devices.append((dm[0], dm[1]))
                    if org_expr:
                        config.option.markexpr = f"(({dm[1]} or {dm[0]}_setup) and ({org_expr})) or {config.option.markexpr}"
                    else:
                        config.option.markexpr = 'or always_run' if config.option.markexpr == '' else f"or ({config.option.markexpr})"
                        config.option.markexpr = f"({dm[1]} or {dm[0]}_setup) {config.option.markexpr}"
    if pytest.logpull and run_only_test_count > 10:
        raise Exception("Usage of --log-pull option is only allowed up to 10 test cases. Please reduece number of tests to run for use with --log-pull")


@pytest.fixture(autouse=True)
def function_fixture(request):
    """Get device handlers and configure testcase according to request.

    Get server handler. Clear recipe list in the process.
    Get DUT handler.
    Handle testcase compatibility.
    Handle configuration special flags ('skip', 'xfail').
    Set testcase timeout if defined in the testcase config, else set default.

    Args:
        request (_pytest.fixtures.FixtureRequest): Fixture request

    Raises:
        FailedException: Device capability file is missing.
    """
    log.debug(msg='Entered function_fixture')
    try:
        server_handler = pytest.server_handler
        server_handler.recipe.clear()
    except Exception:
        pass

    # Always run COMPAT testcases.
    if request.node.name in compat_test_list:
        return True

    dut_handler = pytest.dut_handler

    # Determine if compatibility check is required.
    do_compatibility_check = False
    for marker in request.node.iter_markers():
        if marker.name == 'gateway_compatible' or marker.name == 'extender_compatible':
            do_compatibility_check = True
            break

    # Determine compatibility for testcase against device type.
    if do_compatibility_check:
        compatible_test = False
        incompatible_with = ''
        dut_device_type = dut_handler.capabilities.get('device_type', None)
        if dut_device_type not in ['extender', 'residential_gateway']:
            raise FailedException('Device capabilities file is missing value for device_type parameter.')
        for marker in request.node.iter_markers():
            if marker.name == 'gateway_compatible' and dut_device_type == 'residential_gateway':
                compatible_test = True
            else:
                incompatible_with = 'GATEWAY'
            if marker.name == 'extender_compatible' and dut_device_type == 'extender':
                compatible_test = True
            else:
                incompatible_with = 'EXTENDER'

        # If testcase does not have defined compatibility markers, run it either way.
        if not compatible_test:
            pytest.skip(f'Testcase not applicable for device capabilities. ({incompatible_with} only)')

    if hasattr(request.node, 'callspec'):
        if request.node.callspec.params is not None:
            if 'test_config' in request.node.callspec.params:
                test_configuration = request.node.callspec.params['test_config']

                # Check testcase configuration for supported keys.
                # Currently supported keys: 'skip', 'xfail'
                if "skip" in test_configuration and test_configuration['skip'] is True:
                    skip_msg = 'Test skipped.'
                    if 'skip_msg' in test_configuration:
                        skip_msg = test_configuration['skip_msg']
                    pytest.skip(msg=skip_msg)
                if "xfail" in test_configuration and test_configuration['xfail'] is True:
                    request.node.add_marker(
                        pytest.mark.xfail(
                            reason='Known FW bug, expected to fail' if 'xfail_msg' not in test_configuration else
                            test_configuration['xfail_msg']))

                if "device_mode" in test_configuration:
                    if test_configuration['device_mode'] == 'bridge':
                        request.node.add_marker(pytest.mark.BRIDGE_MODE())
                    elif test_configuration['device_mode'] == 'router':
                        request.node.add_marker(pytest.mark.ROUTER_MODE())

                # Get testcase timeout from testcase config if exists.
                timeout = False
                try:
                    timeout = int(test_configuration['test_script_timeout'])
                except KeyError:
                    pass
                except Exception as e:
                    log.exception(msg=e)

                # Set framework timeout. If not set, set default.
                py_test_timeout = server_handler.dut['device_config'].get("py_test_timeout", PYTEST_DEFAULT_TIMEOUT)
                request.node.add_marker(pytest.mark.timeout(py_test_timeout if not timeout else timeout + PYTEST_TIMEOUT_ADD))

                # Set pytest timeout.
                for _test_handler_name, test_handler in server_handler.device_handlers.items():
                    try:
                        if request.node.get_closest_marker('dependency'):
                            dependencies = request.node.get_closest_marker('dependency').kwargs['depends']
                            if any(test_handler.name in ds for ds in dependencies):
                                test_handler.update_shell_timeout(timeout)
                    except Exception as e:
                        log.warning(f'Failed to update shell timeout: {e}')
            else:
                log.warning('Function lacks "test_config" input parameter!')


def pytest_itemcollected(item):
    """Collect pytest item.

    Item is a testcase.
    Upon test function collection, remove 'test_' string from name.

    Args:
        item (str): Testcase name
    """
    item.name = item.name.replace('test_', '', 1)
    item.name = item.name.replace('[test_config', '[', 1)
    item.name = item.name.replace('-test_config', ',')

    try:
        test_basename = item.name.split('[')[0]
        if '[' in item.name:
            test_configs = item.name.split('[')[1].split(']')[0]
        else:
            test_configs = item.name
        test_configs_list = eval(f'[{test_configs}]')
        test_configs_list.reverse()
        item.name = f'{test_basename}{str(test_configs_list).replace(", ", "-")}'
    except NameError:
        pass
    except IndexError as e:
        log.warning(f'{item.name}: {e}')
    except Exception as e:
        log.warning(f'{item.name}: {e}')
        pass
    log.debug(msg=f'{item.name}')


def pytest_report_collectionfinish(config, startdir, items):
    """Return a string or list of strings to be displayed after collection has finished successfully.

    These strings will be displayed after the standard “collected X items” message.

    Args:
        config (pytest.Config): The pytest config object startdir
        (LEGACY_PATH): The starting dir (deprecated).
        items (Sequence[Item]): List of pytest items that are going to be executed.
                                This list should not be modified.
    """
    log.debug(msg=f'{len(items)} items')
    tr = config.pluginmanager.get_plugin('terminalreporter')
    tr.write_line(f"Pytest collection finished {len(items)} items", bold=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Call to create a TestReport for each of the setup, call and teardown runtest phases of a test item.

    Args:
        item (Item): Testcase
        call (CallInfo[None]): The CallInfo for the phase.
    """
    log.debug(msg=f'{item.name} {call}')
    global report_map
    # yield to other hooks, to obtain _pytest.runner.TestReport object
    report = (yield).get_result()
    log.debug(msg=f'{item.name} report available')
    # There are three reporting phases: "setup", "call", "teardown"
    if report.when != 'call':
        return  # only postprocess on "call"

    if report_map['test_name'] != item.name:
        log.debug(msg=f'Initializing report map for test {item.name}')
        report_map = {
            'test_name': item.name,
            'group': {
                'FRM': [],
                'RECIPE': [],
            },
        }

    frm_lines = report.capstderr.split('\n')

    log.debug(msg='Categorizing report logs by group')
    # 1) Remove empty strings from all sources
    frm_lines = list(filter(lambda x: x != '', frm_lines))

    # 2) Create DEBUG and FRM section lines
    report_map['group']['FRM'] = frm_lines

    try:
        rec = pytest.server_handler.recipe.get_for_allure()
        if pytest.server_handler.dry_run and '--dbg' in sys.argv:
            # rec is a list, only print RECIPE if not empty.
            if rec:
                print('\n\nRECIPE:\n')
                print('\n'.join(rec))
        report_map['group']['RECIPE'] = rec
    except Exception as t_e:
        report_map['group']['RECIPE'] = [f'Could not generate test recipe\n{t_e}']
        log.warning(msg=t_e)

    log.debug(msg='Attaching reports to allure')
    for group in report_map['group'].keys():
        try:
            body = "\n".join(report_map['group'][group])
            allure.attach(
                name=group,
                body=body,
            )
        except Exception as e:
            log.warning(msg=f'Exception attaching {item.name} log {group} to allure')
            log.warning(msg=e)
    if report.failed and pytest.logpull:
        try:
            log_pull_res = pytest.dut_handler.pod_api.get_logs(directory='/tmp/')
            if log_pull_res[0] == 1:
                log.error(f'Failed to create logpull.\n{log_pull_res}')
            allure.attach.file(log_pull_res, name='LOGPULL', extension="tgz")
        except Exception as e:
            log.exception(f'Failed to create logpull.\n{e}')


def pytest_assertrepr_compare(op, left, right):
    """Compare assertions and raise exception accordingly.

    Args:
        op (str): Not used.
        left (int): Error type.
        right (int): Error type.

    Raises:
        PermissionError: Testcase not executable on the device.
        ConnectionError: Lost connection to device error.
    """
    if (isinstance(left, int) and isinstance(right, int) and left == 3) or (isinstance(left, str) and left == 'skip'):
        pytest.skip('Shell propagation skip, check test output')
    elif isinstance(left, int) and isinstance(right, int) and left == 126:
        raise PermissionError('Permission to execute denied or non-executable')
    elif isinstance(left, int) and isinstance(right, int) and left == 255:
        raise ConnectionError('Lost connection to device')


def _print_versions_for_jenkins_job_descriptions(session):
    """Print and format version (and other data) for Jenkins job descriptions.

    Args:
        session (pytest.Session): Pytest session object
    """
    dut_handler = pytest.dut_handler
    log.info(msg='Generating Jenkins HTML job descriptor')
    tr = session.config.pluginmanager.get_plugin('terminalreporter')
    duration = time.strftime('%H:%M:%S', time.gmtime(time.time() - tr._sessionstarttime))
    passed = xfailed = 0
    skipped = 0
    if 'xfailed' in tr.stats:
        xfailed = len(tr.stats['xfailed'])
    if 'passed' in tr.stats:
        passed = len(tr.stats['passed']) + xfailed
    if 'skipped' in tr.stats:
        skipped = len(tr.stats['skipped'])
    failed = session.testsfailed
    collected = session.testscollected

    # This string acts as token for setting build description - match with Jenkins config!
    jenkins_descriptor = os.getenv('FUT_JENKINS_DESCRIPTOR')
    if jenkins_descriptor is None:
        jenkins_descriptor = '[FutJenkinsBuildDescription]'

    dut_fw_version = None
    if dut_handler:
        try:
            dut_fw_version = dut_handler.get_version().split('-g')[0]
        except Exception:
            log.warning('Failed to retrieve device FW version')
            dut_fw_version = 'None'

    dut_cfg_folder = os.getenv('DUT_CFG_FOLDER')

    git_branch = os.getenv('GIT_BRANCH')
    if git_branch is None or 'detached' in git_branch:
        git_branch = os.getenv('GIT_COMMIT')
        if git_branch is not None:
            git_branch = git_branch[:7]
    if isinstance(git_branch, str):
        if git_branch.startswith('origin/'):
            git_branch = git_branch[len('origin/'):]
    if not git_branch:
        git_branch = ''

    fut_testcase_list = os.getenv('FUT_TESTCASE_LIST')
    if fut_testcase_list:
        fut_testcase_list = f'{fut_testcase_list[:8]}<br>'
    else:
        fut_testcase_list = ''

    fut_pytest_list = os.getenv('FUT_PYTEST_LIST')
    if fut_pytest_list:
        fut_pytest_list = f'{fut_pytest_list[:8]}<br>'
    else:
        fut_pytest_list = ''

    html_fail = f'<font color="red">fail:{failed}</font>'
    html_pass = f'<font color="green">pass:{passed}</font>'
    html_all = f'<font color="black">all:{collected}</font>'
    html_fw_ver = f'{dut_fw_version}'
    html_dut_cfg_folder = f'{dut_cfg_folder}'
    html_git_id = f'<font color="magenta">F:{git_branch[:8]}</font>'
    html_time = f'{duration}'

    html_jenkins_description = f'{jenkins_descriptor}' \
                               f'{html_fail} {html_pass} {html_all}<br>' \
                               f'{html_fw_ver} | {html_dut_cfg_folder}<br>' \
                               f'{html_git_id}<br>' \
                               f'{fut_testcase_list}' \
                               f'{fut_pytest_list}' \
                               f'{html_time}<br>' \
                               f'{jenkins_descriptor}'
    tr.write_sep(sep="#")
    print('FUT results in spreadsheet-friendly format:')
    print('fail\tpass\tall\tskip\tduration')
    print(f'{failed}\t{passed}\t{collected}\t{skipped}\t{duration}')
    tr.write_sep(sep="#")

    # Contain description string to one line, use print for clean string output
    print(html_jenkins_description.replace('\n', ''))  # Do not use log here


def pytest_sessionfinish(session):
    """Finish pytest session."""
    if hasattr(pytest, 'dut_handler') and not any([pytest.listtests, pytest.listconfigs, pytest.transferonly]):
        _print_versions_for_jenkins_job_descriptions(session)
