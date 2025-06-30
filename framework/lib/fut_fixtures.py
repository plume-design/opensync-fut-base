import os
from pathlib import Path

import pytest

from framework.handlers.client_handler import ClientHandler
from framework.handlers.pod_handler import PodHandler
from framework.handlers.server_handler import ServerHandler
from lib_testbed.generic.client.client import ClientResolver
from lib_testbed.generic.pod.pod import PodResolver
from lib_testbed.generic.switch import switch
from lib_testbed.generic.switch.generic.switch_api_generic import SwitchApiGeneric
from lib_testbed.generic.util.allure_util import AllureUtil
from lib_testbed.generic.util.config import load_tb_config, TbConfig
from lib_testbed.generic.util.logger import log


def _server_handler_setup(handler: ServerHandler, request_config) -> None:
    try:
        handler.remove_dir("/tmp/fut-base", skip_exception=True)
        transfers = handler.transfers
        extra_transfer = [item for item in getattr(request_config, "extra_transfer", []) if Path(item[0]).is_dir()]
        transfers.extend(extra_transfer)
        handler.transfers = sorted(set(transfers))
        handler.transfer_folders.extend([item[0] for item in extra_transfer])
        log.info(f"{handler.nickname.upper()}: transferring {handler.transfer_folders}")
        for directory, location in handler.transfers:
            handler.put_dir(
                directory=f"{handler.FUT_BASE_DIR}/{directory}/",
                location=f"{handler.FUT_DIR}/{location}/",
                as_sudo=False,
            )

        log.info(f"{handler.nickname.upper()}: transferring fut_set_env.sh")
        handler.create_and_transfer_fut_env_file()

        assert handler.execute("server_add_response_policy_zone", suffix=".sh", folder="docker/server")[0] == 0
        assert handler.execute("dock-run", suffix=".server", folder="docker/server")[0] == 0

        handler.docker_container_id = handler.get_docker_container_id()

    except RuntimeError as e:
        raise RuntimeError(f"Unable to setup {handler.nickname.upper()} handler: {e}") from e


def _pod_handler_setup(handler: PodHandler, request_config, disable_fatal_state: bool = True) -> None:
    try:
        mount_point_ec, mount_point_std_out, mount_point_std_err = handler.run_raw(
            f"test -e {handler.FUT_DIR} || mkdir -p {handler.FUT_DIR} && df -TP {handler.FUT_DIR} | tail -1 | awk -F' ' '{{print $NF}}'",
        )

        assert mount_point_ec == 0
        assert handler.run_raw(f"mount | (! grep -E 'on {mount_point_std_out} .*noexec')")[0] == 0

        # Transfer FUT files to ensure fresh sources on every run
        transfers = handler.transfers
        extra_transfer = [item for item in getattr(request_config, "extra_transfer", []) if Path(item[0]).is_dir()]
        transfers.extend(extra_transfer)
        handler.transfers = sorted(set(transfers))
        handler.transfer_folders.extend([item[0] for item in extra_transfer])
        handler.check_fut_files(force_transfer=True)

        pod_region = handler.get_region()
        log.info(f"{handler.nickname.upper()}: retrieved region -> {pod_region}")

        reg_domain = handler.capabilities.get_regulatory_domain()
        log.info(f"{handler.nickname.upper()}: configured region -> {reg_domain}")

        assert pod_region == reg_domain

        if disable_fatal_state:
            log.info(f"{handler.nickname.upper()}: performing device initialization")
            assert handler.execute("tools/device/device_init", skip_logging=True)[0] == 0

    except RuntimeError as e:
        raise RuntimeError(f"Unable to setup {handler.nickname.upper()} handler: {e}") from e


def _client_handler_setup(handler: ClientHandler, request_config) -> None:
    try:
        transfers = handler.transfers
        extra_transfer = [item for item in getattr(request_config, "extra_transfer", []) if Path(item[0]).is_dir()]
        transfers.extend(extra_transfer)
        handler.transfers = sorted(set(transfers))
        handler.transfer_folders.extend([item[0] for item in extra_transfer])
        log.info(f"{handler.nickname.upper()}: transferring {handler.transfer_folders}")
        for directory, location in handler.transfers:
            handler.put_dir(
                directory=f"{handler.FUT_BASE_DIR}/{directory}/",
                location=f"{handler.FUT_DIR}/{location}/",
                as_sudo=True,
            )
    except RuntimeError as e:
        raise RuntimeError(f"Unable to setup {handler.nickname.upper()} handler: {e}") from e


def _device_allure_environment(request_config, device_handler):
    if not request_config.getoption("--alluredir"):
        return
    allure_util = AllureUtil(request_config)
    _attach_device_version(allure_util=allure_util, device_handler=device_handler)


def _attach_device_version(allure_util, device_handler):
    allure_util.cache_environment_value(f"{device_handler.nickname}_version", device_handler.version())


def _pod_allure_environment(request_config, device_handler):
    if not request_config.getoption("--alluredir"):
        return
    log.info("Creating Allure environment for %s.", device_handler.nickname)
    allure_util = AllureUtil(request_config)
    _attach_device_version(allure_util=allure_util, device_handler=device_handler)
    allure_util.cache_environment_value(f"{device_handler.nickname}_fut_base_dir", device_handler.FUT_BASE_DIR)
    allure_util.cache_environment_value(f"{device_handler.nickname}_bridge_type", device_handler.bridge_type)
    allure_util.cache_environment_value(f"{device_handler.nickname}_opensync", device_handler.opensync)
    allure_util.cache_environment_value(f"{device_handler.nickname}_model", device_handler.model)
    allure_util.cache_environment_value(f"{device_handler.nickname}_wireless_manager", device_handler.wireless_manager)
    allure_util.cache_environment_value(f"{device_handler.nickname}_reboot_time", str(device_handler.reboot_time))


def _server_allure_environment(request_config, device_handler):
    if not request_config.getoption("--alluredir"):
        return
    log.info("Creating Allure environment for %s.", device_handler.nickname)
    allure_util = AllureUtil(request_config)

    # Docker env.list file
    envlist_filepath = Path(__file__).absolute().parents[2].joinpath("docker/env.list")
    if not envlist_filepath.is_file():
        envlist_filepath = envlist_filepath.parent.joinpath("env.list.base")
    with open(envlist_filepath, "r") as envlist_file:
        env_vars = [line.rstrip("\n").split("=")[0] for line in envlist_file.readlines()]
    for env_var in env_vars:
        env_value = os.getenv(env_var)
        allure_util.cache_environment_value(env_var, env_value)

    from framework.lib.fut_lib import fut_release_version, get_testbed_name

    allure_util.cache_environment_value("testbed_name", get_testbed_name())
    allure_util.cache_environment_value("fut_release_version", fut_release_version())

    _attach_device_version(allure_util=allure_util, device_handler=device_handler)

    from lib_testbed.generic.pytest_plugins.allure_environment import get_osrt_snapshot

    snapshot = get_osrt_snapshot(device_handler)
    if snapshot:
        allure_util.cache_environment_value("osrt_snapshot", snapshot)


@pytest.fixture(scope="session")
def server_handler(request, fut_tb_config, pytestconfig) -> ServerHandler | None:
    log.info("SERVER: initializing handler")
    server_handler_args = resolve_client_obj(name="host", config=fut_tb_config, nickname="host")
    server_handler = ServerHandler(**server_handler_args)
    _server_handler_setup(server_handler, request.config)
    _server_allure_environment(request_config=request.config, device_handler=server_handler)
    yield server_handler
    try:
        log.info("Performing docker container cleanup on the server device")
        assert server_handler.execute("server_docker_cleanup", suffix=".py", folder="docker/server")[0] == 0
    except AttributeError as exception:
        log.debug(f"Unable to perform docker container cleanup on the server device: {exception}")
    except Exception as exception:
        log.warning(f"Unable to perform docker container cleanup on the server device: {exception}")


@pytest.fixture(scope="session")
def switch_handler(fut_tb_config) -> SwitchApiGeneric | None:
    log.info("SWITCH: initializing handler")
    switch_handler = switch.Switch().create_obj(module_name="switch", request=None, config=fut_tb_config)
    yield switch_handler


@pytest.fixture(scope="session")
def gw_handler(request, fut_tb_config, pytestconfig) -> PodHandler | None:
    log.info("GW: initializing handler")
    pod_handler_args = resolve_pod_obj(name="gw", index=0, config=fut_tb_config, multi_obj=False)
    pod_handler = PodHandler(**pod_handler_args)
    _pod_handler_setup(pod_handler, request.config)
    pytestconfig.gw_manager_pids = pod_handler.get_managers_list("dm")
    _pod_allure_environment(request_config=request.config, device_handler=pod_handler)
    yield pod_handler


@pytest.fixture(scope="session")
def l1_handler(request, fut_tb_config, pytestconfig) -> PodHandler | None:
    log.info("L1: initializing handler")
    pod_handler_args = resolve_pod_obj(name="l1", index=1, config=fut_tb_config, multi_obj=False)
    pod_handler = PodHandler(**pod_handler_args)
    _pod_handler_setup(pod_handler, request.config)
    pytestconfig.gw_manager_pids = pod_handler.get_managers_list("dm")
    _pod_allure_environment(request_config=request.config, device_handler=pod_handler)
    yield pod_handler


@pytest.fixture(scope="session")
def l2_handler(request, fut_tb_config, pytestconfig) -> PodHandler | None:
    log.info("L2: initializing handler")
    pod_handler_args = resolve_pod_obj(name="l2", index=2, config=fut_tb_config, multi_obj=False)
    pod_handler = PodHandler(**pod_handler_args)
    _pod_handler_setup(pod_handler, request.config)
    pytestconfig.gw_manager_pids = pod_handler.get_managers_list("dm")
    _pod_allure_environment(request_config=request.config, device_handler=pod_handler)
    yield pod_handler


@pytest.fixture(scope="session")
def w1_handler(request, fut_tb_config) -> ClientHandler | None:
    log.info("W1: initializing handler")
    client_handler_args = resolve_client_obj(name="w1", config=fut_tb_config, wifi=True, multi_obj=False)
    client_handler = ClientHandler(**client_handler_args)
    _client_handler_setup(client_handler, request.config)
    log.info("Creating Allure environment for %s.", client_handler.nickname)
    _device_allure_environment(request_config=request.config, device_handler=client_handler)
    yield client_handler


@pytest.fixture(scope="session")
def w2_handler(request, fut_tb_config) -> ClientHandler | None:
    log.info("W2: initializing handler")
    client_handler_args = resolve_client_obj(name="w2", config=fut_tb_config, wifi=True, multi_obj=False)
    client_handler = ClientHandler(**client_handler_args)
    _client_handler_setup(client_handler, request.config)
    log.info("Creating Allure environment for %s.", client_handler.nickname)
    _device_allure_environment(request_config=request.config, device_handler=client_handler)
    yield client_handler


@pytest.fixture(scope="session")
def e1_handler(request, fut_tb_config) -> ClientHandler | None:
    log.info("E1: initializing handler")
    client_handler_args = resolve_client_obj(name="e1", config=fut_tb_config, eth=True, multi_obj=False)
    client_handler = ClientHandler(**client_handler_args)
    _client_handler_setup(client_handler, request.config)
    log.info("Creating Allure environment for %s.", client_handler.nickname)
    _device_allure_environment(request_config=request.config, device_handler=client_handler)
    yield client_handler


@pytest.fixture(scope="session")
def e2_handler(request, fut_tb_config) -> ClientHandler | None:
    log.info("E2: initializing handler")
    client_handler_args = resolve_client_obj(name="e2", config=fut_tb_config, eth=True, multi_obj=False)
    client_handler = ClientHandler(**client_handler_args)
    _client_handler_setup(client_handler, request.config)
    log.info("Creating Allure environment for %s.", client_handler.nickname)
    _device_allure_environment(request_config=request.config, device_handler=client_handler)
    yield client_handler


@pytest.fixture(scope="session")
def fut_tb_config() -> TbConfig:
    testbed_name = os.getenv("OPENSYNC_TESTBED")

    if not testbed_name:
        raise ValueError("OPENSYNC_TESTBED environment variable is not set")
    tb_config = load_tb_config(location_file=f"{testbed_name}.yaml", skip_deployment=True)
    return tb_config


def resolve_pod_obj(request=None, **kwargs) -> dict:
    kwargs["device_type"] = "Nodes"
    dev_discovered = PodResolver().get_device(request=request, **kwargs)
    kwargs["dev"] = dev_discovered
    return kwargs


def resolve_client_obj(request=None, **kwargs) -> dict:
    kwargs["device_type"] = "Clients"
    dev_discovered = ClientResolver().get_device(request=request, **kwargs)
    kwargs["dev"] = dev_discovered
    return kwargs
