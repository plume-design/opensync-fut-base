import pytest

import framework.tools.logger
from framework.tools.functions import FailedException, get_command_arguments, step
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

testcase_cfg = {
    'telog_validate': {
        'config': {
            'marks': [
                'require_dut',
                'os_integration_m2',
                'extender_compatible',
            ],
            'test_script_timeout': 120,
            'steps': [
                ('Testcase', [
                    ('server', {
                        'log_folder': 'tests/ng/tools/telog/logs/telog_validate.sh/',
                        'script_path': 'tests/ng/tools/telog/run_remote.sh telog_validate.sh',
                    }),
                ]),
            ],
        },
    },
}

scenarios_cfg = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='NG')


########################################################################################################################
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="ng_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_ng_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(full=True)
    with step('NG setup'):
        assert dut_handler.run('tools/device/device_init', dut_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.mark_setup()
    server_handler.recipe.clear_full()


test_parametrization = []
test_ids = []

for i in testcase_cfg.items():
    if i[0] in scenarios_cfg.cfg:
        for idx, j in enumerate(scenarios_cfg.cfg[i[0]]):
            test_parametrization += [(i[1]['config'], j)]
            test_ids += [f"{i[0]}[config_{idx}]"]


@pytest.mark.parametrize(
    'test_config,test_scenario', test_parametrization,
    ids=test_ids,
)
def test_ng_(test_config, test_scenario):
    def _get_device_handler(dn):
        return getattr(pytest, f"{dn}_handler")

    def _get_scenario_step_args(sn, sd):
        for tsc in test_scenario:
            if tsc[0] == sn:
                for d in tsc[1]:
                    if d[0] == sd:
                        return d
        raise FailedException(f'Missing test case scenarios!\nsn: {sn}\nsd: {sd}\ntsc: {tsc}')

    for step_cfg in test_config.get('steps'):
        log.debug(f'step cfg:\n{step_cfg}')
        with step(step_cfg[0]):
            for sub_step_cfg in step_cfg[1]:
                log.debug(f'sub-step cfg:\n{sub_step_cfg}')
                handler = _get_device_handler(sub_step_cfg[0])
                scenario_cfg = _get_scenario_step_args(step_cfg[0], sub_step_cfg[0])
                log.debug(f'scenario cfg:\n{scenario_cfg}')
                setup_arguments = '' if 'arguments' not in sub_step_cfg[1] else sub_step_cfg[1]['arguments']
                test_arguments = '' if 'arguments' not in scenario_cfg[1] else scenario_cfg[1]['arguments']
                shell_env = {} if 'env' not in scenario_cfg[1] else scenario_cfg[1]['env']
                log.debug(f'setup_arguments:\n{setup_arguments}')
                log.debug(f'shell_env:\n{shell_env}')

                assert handler.run(sub_step_cfg[1]['script_path'], get_command_arguments(setup_arguments, test_arguments),
                                   ext='', suffix='', shell_env_var=shell_env) == ExpectedShellResult
                # Most NG test scripts create logs/<script_name>/ folder which contains test logs, try and attach them to report as well
                try:
                    handler.execute(f'cat $(find {handler.fut_dir}/shell/{sub_step_cfg[1]["log_folder"]} -type f)', print_out=True, step_name="NG-LOG")
                except Exception as e:
                    log.warning(f'Failed to retrieve NG test logs\n{e}')
