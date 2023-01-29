"""Module provides class and its methods for execution of the testcases."""

import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path
from threading import Thread

import allure
import pytest
import yaml

import framework.tools.logger
from config.model.generic.fut_gen import FutTestConfigGenClass
from lib_testbed.generic.pod.pod_ext import PodExt
from lib_testbed.generic.util.config import get_model_capabilities
from .lib.config import Config
from .lib.fut_exception import FutException
from .lib.recipe import Recipe
from .lib.test_handler import FutTestHandler
from .tools.functions import (get_info_dump, get_section_line, load_reg_rule,
                              map_dict_key_path)

EXPECTED_EC = 0
global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

LOG_PASS = '--log-pass' in sys.argv
FUT_MQTT_LOG_DUMP_CMD = "cat /tmp/fut.mosquitto.log"
FUT_GATEKEEPER_LOG_FILE_PATH = '/tmp/fut_gatekeeper.log'
FUT_GATEKEEPER_LOG_DUMP_CMD = f'cat {FUT_GATEKEEPER_LOG_FILE_PATH}'


class ServerHandlerClass:
    """ServerHandlerClass class."""

    def __init__(self):
        log.debug(msg='Entered ServerHandlerClass')
        # fut_base_dir: top of fut source code directory tree on server
        self.fut_base_dir = Path(__file__).absolute().parents[1].as_posix()
        self.fut_dir = self.fut_base_dir
        self.testbed_cfg = Config(self.handle_testbed_config())
        self.testbed_cfg.set("fut_base_dir", str(self.fut_base_dir))
        self.recipe = Recipe()
        self.devices_cfg = []
        self.device_handlers = {}
        self.additional_files = []
        self.fut_exception = FutException()
        self.name = 'server'
        self.server_pass = self.testbed_cfg.get('server.password')
        self.use_docker = True if os.getenv('USE_DOCKER') == 'true' else False
        self.dry_run = os.getenv("FUT_DRY_RUN", 'False').lower() in ('true', '1', 't')
        self.gen_type = os.getenv("FUT_GEN_TYPE", 'optimized')
        self.use_generator = os.getenv("FUT_USE_GENERATOR", 'False').lower() in ('true', '1', 't')
        self.regulatory_rule = load_reg_rule()
        self.fut_config_from_json = False if os.getenv('FUT_CONFIG_FROM_JSON', 'False').lower() in (False, None, 'false', 'none', '') else os.getenv('FUT_CONFIG_FROM_JSON')
        self.mqtt_dump_cmd = FUT_MQTT_LOG_DUMP_CMD
        self.gatekeeper_dump_cmd = FUT_GATEKEEPER_LOG_DUMP_CMD
        self.fut_cloud = None
        self.use_fut_cloud = None
        self.ssid_postfix = ""
        if self.use_generator:
            self.fut_test_config_gen_cls = FutTestConfigGenClass(
                self.testbed_cfg.get("devices.dut.CFG_FOLDER"),
                self.testbed_cfg.get("devices.refs")[0]["CFG_FOLDER"],
                gen_type=self.gen_type,
            )
        else:
            self.fut_test_config_gen_cls = None
        # LOAD DEVICES CONFIGURATIONS #
        for device_role, device_configs in self.testbed_cfg.get('devices').items():
            if device_role == 'dut':
                device_configs = [device_configs]

            for testbed_device_cfg in device_configs:
                device_folder = testbed_device_cfg.get('CFG_FOLDER')
                device_name = testbed_device_cfg.get('name')
                if not device_folder:
                    log.warning(msg=f'No {device_name} config folder for {device_folder}, skipping')
                    continue

                if not device_name:
                    raise Exception(f'{device_folder} missing "name" config.')
                if 'dut' in device_role or 'ref' in device_role:
                    device_config = self.handle_device_config(device_folder)
                elif 'client' in device_role:
                    device_config = self.handle_client_config(device_folder)
                # Use FUT device configuration file if it exists
                path = Path(f'{self.get_model_config_dir(device_folder)}/device/config.yaml')
                if path.is_file():
                    with open(path) as device_conf_file:
                        device_config = yaml.safe_load(device_conf_file)
                try:
                    self.__setattr__(f'{device_name}_cfg_folder', device_folder)
                    self.__setattr__(
                        device_name, {
                            # Load test config only for DUT
                            "test_cfg": False if device_name != 'dut' else self.get_test_config(),
                            "device_config": Config(deepcopy(device_config)),
                            "testbed_device_cfg": Config(deepcopy(testbed_device_cfg)),
                            "name": device_name,
                        },
                    )
                    self.devices_cfg.append(device_name)
                    log.debug(f'{device_name} loaded')
                except Exception as exception:
                    raise type(exception)(f"Error importing {device_name} config\n{exception}")
        # Set server password
        self.server_pass = self.testbed_cfg.get('server.password')
        # Always create regulatory.txt file, regardless if it exists
        try:
            self.additional_files.append(self.create_regulatory_shell_file())
        except Exception as exception:
            log.exception(f'Failed to create regulatory.txt file\n{exception}')

        internal_shell_path = f'{self.fut_base_dir}/internal/shell'
        if Path(internal_shell_path).is_dir():
            # Add internal/shell to self.additional_files for file transfer to device
            self.additional_files.append(internal_shell_path)

    def _get_cmd_process(self, cmd, as_sudo=False, shell_env_var=None, **kwargs):
        """Start subprocess.

        Executes child program in a new process.

        Args:
            cmd (str): Command to be executed.
            as_sudo (bool, optional): Execute the command as 'sudo'. Defaults to False.
            shell_env_var (str, optional): Shell environment variables. Defaults to None.

        Returns:
            (command): Subprocess command parameters
        """
        shell = True if 'shell' not in kwargs else kwargs['shell']
        stdin = None
        stdout = subprocess.PIPE
        stderr = subprocess.STDOUT
        os_env = os.environ.copy()
        os_env['FUT_TOPDIR'] = self.fut_base_dir
        if shell_env_var:
            os_env.update(shell_env_var)
        if as_sudo:
            cmd_pass = subprocess.Popen(
                ['echo', self.server_pass],
                stdout=stdout,
                stderr=stderr,
                universal_newlines=True,
                env=os_env,
                shell=shell,
            )
            stdin = cmd_pass.stdout
            cmd = f'sudo -n -S {cmd}'
        cmd_process = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            universal_newlines=True,
            env=os_env,
            shell=shell,
        )
        return cmd_process

    def _get_run_command(self, path, args, **kwargs):
        """Return string representing the command to be executed.

        If extension as keyword argument is provided, use it, else default to '.sh'.
        If folder as keyword argument is provided, use it, else default to 'shell'.

        Args:
            path (string): Path to the script
            args (string): Script arguments

        Returns:
            (int): Exit code
        """
        ext = ".sh" if 'ext' not in kwargs else kwargs['ext']
        folder = 'shell' if 'folder' not in kwargs else kwargs['folder']
        return f"{self.fut_base_dir}/{folder}/{path}{ext} {args}"

    def create_regulatory_shell_file(self):
        """Create regulatory file in directory 'shell/config/'.

        Method names the file as 'regulatory.txt'.

        Returns:
            (str): Path to regulatory shell file.
        """
        reg_map_shell_path = f'{self.fut_base_dir}/shell/config/regulatory.txt'
        reg_map_shell_file = open(reg_map_shell_path, "w")
        for reg_key_value in map_dict_key_path(self.regulatory_rule):
            # Remove ',' from list, for easier shell retrieval
            ini_line = f"{reg_key_value[0].upper()}= {' '.join(str(x) for x in reg_key_value[1])}\n"
            reg_map_shell_file.write(ini_line)
        reg_map_shell_file.close()
        return reg_map_shell_path

    def clear_gatekeeper_log(self):
        log.info(f'Clearing {FUT_GATEKEEPER_LOG_FILE_PATH} log file.')
        os.system(f'echo "" > {FUT_GATEKEEPER_LOG_FILE_PATH}')
        return True

    def execute(self, *args, **kwargs):
        """Execute the 'execute_raw' command.

        Wrapper to execute the command.

        Returns:
            (int): Exit code
        """
        return self.execute_raw(*args, **kwargs)[0]

    def execute_raw(self, cmd, print_out=False, as_sudo=False, timeout=340, shell_env_var=None, **kwargs):
        """Execute command on the server.

        Supports DRY-RUN mode which would not actually execute the command, but
        would still generate, e.g. recipe.

        Args:
            cmd (str): Command to be executed
            print_out (bool, optional): Generate execution print-outs. Defaults to False.
            as_sudo (bool, optional): Execute the command as 'sudo'. Defaults to False.
            timeout (int, optional): Command execution timeout. Defaults to 340.
            shell_env_var (str, optional): Shell environment variables. Defaults to None.

        Raises:
            TimeoutError: Command took more that timeout seconds to execute.
            subprocess_exception: Subprocess generated an exception.

        Returns:
            (int, str, str): Return code, std_out, std_err
        """
        expected_ec = EXPECTED_EC if 'expected_ec' not in kwargs else kwargs['expected_ec']
        step_name = False if 'step_name' not in kwargs else kwargs['step_name']
        ignore_assertion = False if 'ignore_assertion' not in kwargs else kwargs['ignore_assertion']
        do_mqtt_log = False if 'do_mqtt_log' not in kwargs else kwargs['do_mqtt_log']
        device_log_for = [] if 'device_log_for' not in kwargs else kwargs['device_log_for']
        do_cloud_log = False if 'do_cloud_log' not in kwargs else kwargs['do_cloud_log']
        do_gatekeeper_log = False if 'do_gatekeeper_log' not in kwargs else kwargs['do_gatekeeper_log']

        # Function within a method
        def _print_output_section(std_o, std_t, cmd_t, cmd_ec):
            info_dump = False
            if std_o:
                std_o, info_dump = get_info_dump(std_o)
            if isinstance(cmd, list):
                cmd_t = ' '.join(cmd_t)
            try:
                script_name = re.search(r'([\w\d\-.]+\.sh|[\w\d\-.]+\.py)', cmd_t).group()
            except Exception:
                script_name = cmd_t
            if std_o != '':
                std_o_p = f'{get_section_line(self.name, cmd_t, std_t, "start")}\n' \
                          f'{std_o}\n' \
                          f'{get_section_line(self.name, cmd_t, std_t, "stop")}\n'
            else:
                std_o_p = f'{get_section_line(self.name, cmd_t, f"No {std_t}")}\n'
            print(std_o_p)
            try:
                with allure.step(f'{self.name} - {script_name if not step_name else step_name}'):
                    allure.attach(
                        name=std_t.upper().replace('_', '-'),
                        body=std_o_p,
                    )
                    if info_dump:
                        allure.attach(
                            name='INFO-DUMP',
                            body=info_dump,
                        )
                    if not ignore_assertion:
                        assert cmd_ec == expected_ec
            except Exception as exception:
                log.warning(f'Failed to create Allure attachments\n{exception}')

        cmd_start = time.strftime('%H:%M:%S')
        if self.dry_run:
            # Dry run does not execute the command.
            log.info(msg=f'DRY-RUN: ({self.name}) {cmd} on Server')
            custom_object = type('CustomObject', (object,), {})
            cmd_process = custom_object()
            cmd_process.returncode = 0
            std_out = f'<!!! REPLACE THIS FROM {self.name} `{cmd}` OUTPUT !!!>'
            std_err = False
        else:
            try:
                if device_log_for:
                    for device_log_device in device_log_for:
                        if device_log_device in self.device_handlers:
                            self.device_handlers[device_log_device].start_log_tail()
                log.info(msg=f'Executing ({self.name}) {cmd} on Server')
                cmd_process = self._get_cmd_process(cmd, as_sudo=as_sudo, shell_env_var=shell_env_var, **kwargs)
                last = time.time()
                drop_time = last + timeout
                while cmd_process.poll() is None:
                    time.sleep(.5)
                    last = time.time()
                    if last > drop_time:
                        raise TimeoutError(f'Command execution took longer than {timeout}s')
                try:
                    readout_time = 3
                    std_out, std_err = cmd_process.communicate(timeout=readout_time)
                except Exception as subprocess_exception:
                    cmd_process.kill()
                    std_out, std_err = cmd_process.communicate()
                    _print_output_section(std_out, 'output', cmd, cmd_process.returncode)
                    _print_output_section(std_err, 'std_err', cmd, cmd_process.returncode)
                    raise subprocess_exception
            finally:
                if device_log_for:
                    for device_log_device in device_log_for:
                        if device_log_device in self.device_handlers:
                            self.device_handlers[device_log_device].stop_log_tail()

            if cmd_process.stdout:
                cmd_process.stdout.close()
            if cmd_process.stderr:
                cmd_process.stderr.close()
        cmd_end = time.strftime('%H:%M:%S')

        std_err_log = f"\nstd_err={std_err}" if cmd_process.returncode != 0 else ''

        log.debug(f"device={self.name}, cmd={cmd}, ec={cmd_process.returncode}{std_err_log}")
        self.recipe.add(device='server', cmd=cmd if isinstance(cmd, str) else ' '.join(cmd), start_t=cmd_start, end_t=cmd_end, ec=cmd_process.returncode)
        if (cmd_process.returncode != expected_ec and device_log_for) or (LOG_PASS and device_log_for):
            if device_log_for:
                for device_log_device in device_log_for:
                    if device_log_device in self.device_handlers:
                        self.device_handlers[device_log_device].attach_log_file()
        if (cmd_process.returncode != expected_ec and do_cloud_log) or (LOG_PASS and do_cloud_log):
            try:
                dump = self.fut_cloud.dump_log()
            except Exception as exception:
                dump = f'Failed to generate FUT Cloud logread section\n{exception}'
            try:
                allure.attach(
                    name='LOGREAD-CLOUD',
                    body=dump,
                )
            except Exception as exception:
                log.warning(f'Failed to Attach Allure report\n{exception}')
        if (cmd_process.returncode != expected_ec and do_mqtt_log) or (LOG_PASS and do_mqtt_log):
            try:
                dump = self.execute_raw(self.mqtt_dump_cmd)[1]
            except Exception as exception:
                dump = f'Failed to generate FUT MQTT logread section\n{exception}'
            try:
                allure.attach(
                    name='LOGREAD-MQTT',
                    body=dump,
                )
            except Exception as exception:
                log.warning(f'Failed to Attach Allure report\n{exception}')

        if (cmd_process.returncode != expected_ec and do_gatekeeper_log) or (LOG_PASS and do_gatekeeper_log):
            try:
                dump = self.execute_raw(self.gatekeeper_dump_cmd)[1]
            except Exception as exception:
                dump = f'Failed to generate FUT Gatekeeper logread section\n{exception}'
            try:
                allure.attach(
                    name='LOGREAD-GATEKEEPER',
                    body=dump,
                )
            except Exception as exception:
                log.warning(f'Failed to Attach Allure report\n{exception}')

        if print_out or cmd_process.returncode != 0:
            if std_out:
                _print_output_section(std_out, 'output', cmd, cmd_process.returncode)
            if std_err:
                _print_output_section(std_err, 'std_err', cmd, cmd_process.returncode)
        return cmd_process.returncode, std_out, std_err

    def generate_active_osrt_location_file(self):
        """Generate active OSRT location file used by OSRT tools.

        Returns:
            (bool): True, always.
        """
        log.info('Generating active OSRT location file which will be used for OSRT tools')
        with open('config/locations/osrt.copy.yaml') as osrt_copy_file:
            loaded_osrt_copy_file = yaml.safe_load(osrt_copy_file)
            tmp_updated_file = deepcopy(loaded_osrt_copy_file)
        try:
            for node_index, node_config in enumerate(loaded_osrt_copy_file['Nodes']):
                device_cfg = self.__getattribute__(node_config['name'])
                node_model = device_cfg['device_config'].get('pod_api_model', self.testbed_cfg.get(f'{node_config["name"].upper()}_CFG_FOLDER'))
                device_capabilities = Config(get_model_capabilities(node_model))
                primary_wan_interface = device_capabilities.get('interfaces.primary_wan_interface')
                primary_lan_interface = device_capabilities.get('interfaces.primary_lan_interface')
                # Update Node device model based on FUT testbed_cfg (testbed_cfg already loads environment variables)
                tmp_updated_file['Nodes'][node_index]['model'] = node_model.upper()
                # Update Node device switch interface names
                for switch_if_config in node_config['switch'].values():
                    if node_config['name'] == 'dut':
                        if 'uplink' in switch_if_config:
                            tmp_updated_file['Nodes'][node_index]['switch'][f"{node_config['name']}_{primary_wan_interface}"] = switch_if_config
                        elif 'lan' in switch_if_config:
                            tmp_updated_file['Nodes'][node_index]['switch'][f"{node_config['name']}_{primary_lan_interface}"] = switch_if_config
                    else:
                        if 'lan' in switch_if_config and 'mn' in switch_if_config:
                            tmp_updated_file['Nodes'][node_index]['switch'][f"{node_config['name']}_{primary_wan_interface}"] = switch_if_config
                        elif 'lan' in switch_if_config:
                            tmp_updated_file['Nodes'][node_index]['switch'][f"{node_config['name']}_{primary_lan_interface}"] = switch_if_config

                # We need to edit Switch configuration as well to match device capabilities and primary interfaces
                for switch_alias_index, switch_alias_config in enumerate(loaded_osrt_copy_file['Switch'][0]['alias']):
                    if node_config['name'] == 'dut' and switch_alias_config['name'] == 'dut_eth0':
                        tmp_updated_file['Switch'][0]['alias'][switch_alias_index]['name'] = f'dut_{primary_wan_interface}'
                    elif node_config['name'] == 'dut' and switch_alias_config['name'] == 'dut_eth1':
                        tmp_updated_file['Switch'][0]['alias'][switch_alias_index]['name'] = f'dut_{primary_lan_interface}'
                    elif node_config['name'] == 'ref' and switch_alias_config['name'] == 'ref_eth0':
                        tmp_updated_file['Switch'][0]['alias'][switch_alias_index]['name'] = f'ref_{primary_wan_interface}'
                    elif node_config['name'] == 'ref' and switch_alias_config['name'] == 'ref_eth1':
                        tmp_updated_file['Switch'][0]['alias'][switch_alias_index]['name'] = f'ref_{primary_lan_interface}'
                    elif node_config['name'] == 'ref2' and switch_alias_config['name'] == 'ref2_eth0':
                        tmp_updated_file['Switch'][0]['alias'][switch_alias_index]['name'] = f'ref2_{primary_wan_interface}'
                    elif node_config['name'] == 'ref2' and switch_alias_config['name'] == 'ref2_eth1':
                        tmp_updated_file['Switch'][0]['alias'][switch_alias_index]['name'] = f'ref2_{primary_lan_interface}'
            # For clients, we only need to update client model
            for client_index, client_config in enumerate(loaded_osrt_copy_file['Clients']):
                client_name = client_config['name'][1:]
                if client_name == 'client3':
                    client_name = 'client2'
                client_cfg = self.__getattribute__(client_name)
                tmp_updated_file['Clients'][client_index]['type'] = client_cfg['device_config'].get('pod_api_model')

        except Exception as exception:
            log.warning(f'Failed to edit osrt location file\n{exception}')
        with open('config/locations/osrt.yaml', 'w') as file:
            yaml.dump(tmp_updated_file, file, default_flow_style=False, sort_keys=False)
        log.info('Active OSRT location yaml file contents:')
        with open('config/locations/osrt.yaml', 'r') as file:
            log.info(f'\n{file.read()}')
        return True

    def get_fut_release_version(self):
        """Return FUT release version.

        If version is not defined reads version string from version
        file and returns the version string.

        Returns:
            (str): FUT release version
        """
        if not os.getenv('FUT_RELEASE_VERSION'):
            with open(f'{self.fut_base_dir}/.version', 'r') as infile:
                fut_version = infile.readlines()
        else:
            fut_version = os.getenv('FUT_RELEASE_VERSION')
        return fut_version

    def get_model_config_dir(self, device_folder):
        """Return the path to the model config directory in POSIX format.

        Method considers internal subdirectory as a config file location candidate!

        Args:
            device_folder (str): Name of the model testcase directory

        Raises:
            Exception: Model directory cannot be found.

        Returns:
            (str): Path to the model config directory in POSIX format.
        """
        model_config_subdir = 'config/model'
        model_config_paths = [
            Path(f"internal/{model_config_subdir}/{device_folder}"),
            Path(f"./{model_config_subdir}/{device_folder}"),
        ]
        for model_config_path in model_config_paths:
            if model_config_path.is_dir():
                break
        else:
            log.error(f"Can not find model config directory for {device_folder}. Please make sure it exists.")
            return None
        return model_config_path.as_posix()

    def get_pod_api(self, pod_name):
        """Get pod API handler.

        Handler provides access to functions from lib_testbed for managing and
        configuring OSRT devices.

        Args:
            pod_name (str): Device name

        Returns:
            (obj): PodApi 'pod' object
        """
        log.debug(msg='Entered get_pod_api')
        model_cfg = getattr(self, pod_name)
        if 'client' not in pod_name:
            capabilities = get_model_capabilities(model_cfg['device_config'].get('pod_api_model', self.testbed_cfg.get(f'{pod_name.upper()}_CFG_FOLDER')))
        else:
            # PodExt required wifi_vendor key for utilization of Pod Class, only for clients
            capabilities = {
                'wifi_vendor': 'qca',
                'username': model_cfg['device_config'].get('username'),
                'password': model_cfg['device_config'].get('password'),
            }
        ssh_gateway = {
            "user": self.testbed_cfg.get("server.username"),
            "hostname": self.testbed_cfg.get("server.host"),
        }

        pod = PodExt(
            ssh_gateway=ssh_gateway,
            gw_id='',
            model=model_cfg['device_config'].get('pod_api_model', self.testbed_cfg.get(f'{pod_name.upper()}_CFG_FOLDER')),
            host={
                "user": capabilities.get('username'),
                "name": model_cfg['testbed_device_cfg'].get('mgmt_ip'),
                "pass": capabilities.get('password'),
                "port": model_cfg['device_config'].get('ssh_port', 22),
            },
            host_recover={
                "screen_app": "platform_3f980000_usb_usb_0_1_3_1_0",
                "screen_acc": "platform_3f980000_usb_usb_0_1_1_2_1_0",
            },
            name=pod_name,
            capabilities=capabilities,
        )
        pod_api = pod.get_pod_api()
        pod_api.__setattr__('name', pod_name)
        return pod_api

    @staticmethod
    def get_server_device_version():
        """Return server version read from .version file.

        Returns:
            (str): Server version as string
        """
        with open('/.version', 'r') as infile:
            server_version = infile.readlines()
        return server_version

    def get_ssid_unique_postfix(self):
        """Get unique SSID.

        Creates a unique postfix for the server AP SSID based on uniqueness
        of the server. Server MAC is used for this purpose. MAC in this case is
        a string with deleted colons in between the MAC octets.

        Raises:
            Exception: Failed to get server MAC address.

        Returns:
            (str): Server MAC address stripped of colons
        """
        if not self.ssid_postfix:
            self.ssid_postfix = self.get_wan_mac().replace(':', '')
            if not self.ssid_postfix:
                raise Exception('Failed to get server MAC')
        return self.ssid_postfix

    def get_test_config(self, cfg_file_prefix=None):
        """Import test configuration for DUT.

        Method looks for any filename "*_config.py" and loads it.
        If "cfg_file_prefix" is specified, imports from single file, else
        finds all files that match the expression.

        If FUT_CONFIG_FROM_JSON env variable is set, function will load JSON file from
        FUT_CONFIG_FROM_JSON path as configuration

        Args:
            cfg_file_prefix (str, optional): Prefix of the testcase configuration file
                                             Defaults to None.

        Returns:
            Config: Testcase configuration Config class.
        """
        log.info(msg=f'Entered get_test_config, {cfg_file_prefix}')

        if self.fut_config_from_json:
            log.debug(msg=f'Using JSON configuration file: {self.fut_config_from_json}')
            try:
                if os.path.isabs(self.fut_config_from_json):
                    json_load_path = self.fut_config_from_json
                else:
                    json_load_path = f'{self.fut_base_dir}/{self.fut_config_from_json}'
                with open(json_load_path) as jf:
                    json_dict = json.load(jf)
                return Config(json_dict['data'])
            except Exception as e:
                log.exception(e)
                sys.exit(1)
        elif self.use_generator:
            log.info(msg='Using FUT test generic configuration generator')
            return Config(self.fut_test_config_gen_cls.get_test_configs())
        else:
            log.info(msg='Using FUT testcase configuration files')
            test_cfg = {}
            testcase_dir = f'{self.get_model_config_dir(self.dut_cfg_folder)}/testcase'
            testcase_mod = testcase_dir.replace('/', '.')
            if cfg_file_prefix is not None:
                # If prefix is specified, import from single file
                config_files = [f'{cfg_file_prefix}_config']
            else:
                # No prefix specified, import all correctly named files from folder
                tc_dir = Path(f'{self.fut_base_dir}/{testcase_dir}')
                config_files = [f.stem for f in tc_dir.iterdir() if '_config.py' in f.name]
            for cfg_file in config_files:
                spec = importlib.util.find_spec(f'{testcase_mod}.{cfg_file}')
                if spec is not None:
                    log.debug(msg=f'Importing {spec.name}')
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # Shallow-merge new module over existing dictionary
                    test_cfg = {**test_cfg, **module.test_cfg}
            # Create Config class instance from dictionary and return
            return Config(test_cfg)

    def get_test_handler(self, pod_api):
        """Instantiate the FutTestHandler and return its handler.

        Initializes the class in the process.

        Args:
            pod_api (PodApi class): PodApi class

        Returns:
            FutTestHandler: handler of instance of FutTestHandler
        """
        log.debug(msg='Entered get_test_handler')
        model_config = getattr(self, pod_api.name)
        test_handler = FutTestHandler(
            pod_api=pod_api,
            fut_base_dir=self.fut_base_dir,
            testbed_device_cfg=model_config['testbed_device_cfg'],
            device_config=model_config['device_config'],
            recipe=self.recipe,
            server_handler=self,
        )
        self.device_handlers[pod_api.name] = test_handler
        return test_handler

    def get_wan_mac(self):
        """Return WAN MAC address.

        Returns:
            (str): WAN interface MAC
        """
        with open('/sys/class/net/eth0/address', 'r') as infile:
            wan_mac = infile.readlines()
        return wan_mac[0].rstrip()

    @staticmethod
    def handle_client_config(device):
        """Handle the client device configuration.

        Loads the device configuration from the capabilities and
        prepares the required parameters as a dictionary.

        Args:
            device (str): Client device type

        Returns:
            (dict): Client configuration as a dictionary
        """
        model_string = device = device.replace('_client', '')
        device_capabilities = Config(get_model_capabilities(device, device_type='client'))
        pod_api_model = device_capabilities.get('device_type')
        username = device_capabilities.get('username')
        password = device_capabilities.get('password')
        device_config = {
            "model_string": model_string,
            "pod_api_model": pod_api_model,
            "shell_path": '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games',
            "username": username,
            "password": password,
            "kpi": {
                "boot_time": 160,
            },
            "namespace_enter_cmd": "ip netns exec nswifi1 bash",
            "network_namespace": "nswifi1",
            "wlan_if_name": "wlan0",
            "wpa_supp_cfg_path": "/etc/netns/nswifi1/wpa_supplicant/wpa_supplicant.conf",
            "device_version_cmd": "sed 's/ .*//' /.version",
            "logread": "sudo tail -n 1000 /tmp/wpa_supplicant_wlan0.log*",
            "logread_tail": "sudo tail -f /tmp/wpa_supplicant_wlan0.log*",
            "FUT_TOPDIR": "/tmp/fut-base",
            "SHELL": "/bin/bash",
        }
        return device_config

    @staticmethod
    def handle_device_config(device):
        """Handle the device configuration.

        Loads the device configuration from the capabilities and
        prepares the required parameters as a dictionary.

        Args:
            device (str): Device type

        Returns:
            (dict): Device configuration as a dictionary
        """
        test_script_timeout = 60
        device_capabilities = Config(get_model_capabilities(device))
        wifi_vendor = device_capabilities.get('wifi_vendor')
        model = device.replace('-', '_').lower()
        # Assemble device configuration parameters
        device_config = {
            "pod_api_model": model,
            "py_test_timeout": test_script_timeout + 10,
            "test_script_timeout": test_script_timeout,
            "MODEL_OVERRIDE_FILE": device_capabilities.get("MODEL_OVERRIDE_FILE", f"{model}_lib_override.sh"),
            "FUT_TOPDIR": "/tmp/fut-base",
            "PLATFORM_OVERRIDE_FILE": device_capabilities.get("PLATFORM_OVERRIDE_FILE", f"{wifi_vendor}_platform_override.sh"),
        }
        return device_config

    @staticmethod
    def handle_testbed_config():
        """Handle the testbed configuration file.

        Loads the testbed configuration file.
        Sets the device configuration folder from the file if necessary.
        Quits testcase execution if any device configuration folder cannot be set.

        Returns:
            (dict): Testcase configuration as a dictionary
        """
        log.debug(msg='Entered handle_testbed_config')
        try:
            with open('config/testbed/config.yaml') as testbed_cfg_file:
                testbed_cfg = yaml.safe_load(testbed_cfg_file)
        except Exception:
            pytest.exit('Failed to load testbed configuration')

        fut_dut_test_cfg_name = os.getenv("DUT_CFG_FOLDER")
        if not fut_dut_test_cfg_name:
            fut_dut_test_cfg_name = testbed_cfg["devices"]["dut"]["CFG_FOLDER"]
        if not fut_dut_test_cfg_name:
            pytest.exit("DUT_CFG_FOLDER is not defined, quitting.")
        testbed_cfg["devices"]["dut"]["CFG_FOLDER"] = fut_dut_test_cfg_name

        for d_type in ['REF', 'CLIENT']:
            for _cfg, idx in enumerate(range(len(testbed_cfg['devices'][f"{d_type.lower()}s"]))):
                str_idx = '' if idx == 0 else idx + 1
                fut_test_cfg_name = os.getenv(f"{d_type}{str_idx}_CFG_FOLDER")
                if not fut_test_cfg_name:
                    fut_test_cfg_name = testbed_cfg["devices"][f'{d_type.lower()}s'][idx]["CFG_FOLDER"]
                if not fut_test_cfg_name:
                    pytest.exit(f"{d_type}{str_idx}_CFG_FOLDER is not defined, quitting.")
                testbed_cfg["devices"][f"{d_type.lower()}s"][idx]["CFG_FOLDER"] = fut_test_cfg_name
        return testbed_cfg

    def run(self, path, args='', **kwargs):
        """Execute the command on the provided path.

        Args:
            path (str): Path to the command
            args (str, optional): Command arguments. Defaults to ''.

        Returns:
            (int): Exit code
        """
        if isinstance(args, list):
            args = ' '.join(args)
        remote_command = self._get_run_command(path, args, **kwargs)
        return self.execute(remote_command, print_out=True, **kwargs)

    def run_raw(self, path, args='', **kwargs):
        """Execute the 'execute_raw' command on device of the OSRT testbed.

        Used to execute the command on the provided path and with provided
        arguments.

        Args:
            path (str): Path to the command
            args (str, optional): Command arguments. Defaults to ''.

        Returns:
            (int): Exit code
        """
        remote_command = self._get_run_command(path, args, **kwargs)
        return self.execute_raw(remote_command, print_out=True, **kwargs)

    @staticmethod
    def set_current_time(ssh):
        """Execute the 'date' command.

        Args:
            ssh (str): SSH connection IP
        """
        time_now = time.gmtime()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        current_time_shell = time.strftime("%Y%m%d%H%M.%S", time_now)
        log.info(msg=f"Setting time {current_time} on {ssh.name}")
        ssh.execute(f'date -s {current_time_shell}')

    def sync_time(self, ssh_connections):
        """Synchronize time on all ssh connections.

        Synchonizes the time by executing the 'date' command.
        Uses multithreading.

        Args:
            ssh_connections (str): SSH connections
        """
        threads = []
        if not isinstance(ssh_connections, tuple):
            ssh_connections = [ssh_connections]

        log.info(msg="Synchronizing time on ssh connections")
        for ssh_connection in ssh_connections:
            thread = Thread(target=self.set_current_time, args=[ssh_connection])
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
