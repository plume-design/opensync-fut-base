from framework.tools.functions import get_command_arguments
from framework.tools.functions import step
from .globals import ExpectedShellResult
from .globals import SERVER_HANDLER_GLOBAL
import pytest


hello_world_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='hello_world')


@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="hello_world_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_hello_world_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='hello_world')
    server_handler.recipe.clear_full()
    with step('Hello World setup'):
        assert dut_handler.run('tests/hello_world/hello_world_setup') == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
test_hello_world_insert_demo_fail_to_update_inputs = hello_world_config.get(
    'hello_world_insert_demo_fail_to_update', [])


@pytest.mark.parametrize('test_config', test_hello_world_insert_demo_fail_to_update_inputs)
@pytest.mark.require_dut()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["hello_world_fut_setup_dut"], scope='session')
def test_hello_world_insert_demo_fail_to_update(test_config):
    dut_handler = pytest.dut_handler
    test_args = get_command_arguments(
        test_config['kv_key'],
        test_config['kv_value'],
    )
    with step('Testcase'):
        if "expect_to_pass" in test_config:
            expect_to_pass = test_config['expect_to_pass']
        else:
            expect_to_pass = True

        assert dut_handler.run('tests/hello_world/hello_world_insert_demo_fail_to_update', test_args) == ExpectedShellResult


########################################################################################################################
test_hello_world_insert_demo_fail_to_write_inputs = hello_world_config.get('hello_world_insert_demo_fail_to_write', [])


@pytest.mark.parametrize('test_config', test_hello_world_insert_demo_fail_to_write_inputs)
@pytest.mark.require_dut()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(depends=["hello_world_fut_setup_dut"], scope='session')
def test_hello_world_insert_demo_fail_to_write(test_config):
    dut_handler = pytest.dut_handler
    test_args = get_command_arguments(
        test_config['kv_key'],
        test_config['kv_value'],
    )
    with step('Testcase'):
        if "expect_to_pass" in test_config:
            expect_to_pass = test_config['expect_to_pass']
        else:
            expect_to_pass = True
        assert dut_handler.run('tests/hello_world/hello_world_insert_demo_fail_to_write', test_args) == ExpectedShellResult


########################################################################################################################
test_hello_world_insert_foreign_module_inputs = hello_world_config.get('hello_world_insert_foreign_module', [])


@pytest.mark.parametrize('test_config', test_hello_world_insert_foreign_module_inputs)
@pytest.mark.dependency(depends=["hello_world_fut_setup_dut"], scope='session')
@pytest.mark.require_dut()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
def test_hello_world_insert_foreign_module(test_config, dut_handler):
    dut_handler = pytest.dut_handler
    test_args = get_command_arguments(
        test_config['kv_key'],
        test_config['kv_value'],
        test_config['module_name'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/hello_world/hello_world_insert_foreign_module', test_args) == ExpectedShellResult


########################################################################################################################
test_hello_world_insert_module_key_value_inputs = hello_world_config.get('hello_world_insert_module_key_value', [])


@pytest.mark.parametrize('test_config', test_hello_world_insert_module_key_value_inputs)
@pytest.mark.dependency(depends=["hello_world_fut_setup_dut"], scope='session')
@pytest.mark.require_dut()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
def test_hello_world_insert_module_key_value(test_config):
    dut_handler = pytest.dut_handler
    test_args = get_command_arguments(
        test_config['kv_key'],
        test_config['kv_value'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/hello_world/hello_world_insert_module_key_value', test_args) == ExpectedShellResult


########################################################################################################################
test_hello_world_update_module_key_value_inputs = hello_world_config.get('hello_world_update_module_key_value', [])


@pytest.mark.parametrize('test_config', test_hello_world_update_module_key_value_inputs)
@pytest.mark.dependency(depends=["hello_world_fut_setup_dut"], scope='session')
@pytest.mark.require_dut()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
def test_hello_world_update_module_key_value(test_config):
    dut_handler = pytest.dut_handler
    test_args = get_command_arguments(
        test_config['kv_key'],
        test_config['kv_value'],
        test_config['kv_changed_value'],
    )
    with step('Testcase'):
        assert dut_handler.run('tests/hello_world/hello_world_update_module_key_value', test_args) == ExpectedShellResult
