"""Module provides FutTestHandler class and its methods for testcase execution."""

import os
import re
import signal
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import allure

import framework.tools.logger
from framework.tools.functions import (FailedException, get_command_arguments,
                                       get_info_dump, get_section_line,
                                       validate_channel_ht_mode_band)
from lib_testbed.generic.util.config import get_model_capabilities
from lib_testbed.generic.util.ssh.sshexception import SshException
from .config import Config
from .fut_exception import FutException
from .recipe import Recipe

EXPECTED_EC = 0
TEST_SCRIPT_TIMEOUT = 180

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

LOG_PASS = '--log-pass' in sys.argv


class FutTestHandler:
    """FutTestHandler class."""

    def __init__(
            self,
            pod_api=None,
            fut_base_dir=None,
            testbed_device_cfg=None,
            device_config=None,
            fut_exception=None,
            recipe=None,
            name=None,
            server_handler=None,
    ):
        self.is_ready = False
        self.log_tail_process = None
        self.log_tail_file = None
        self.log_tail_file_name = None
        self.recipe = recipe
        self.server_handler = server_handler
        if not self.recipe:
            self.recipe = Recipe()

        self.fut_exception = fut_exception
        if not self.fut_exception:
            self.fut_exception = FutException()

        self.pod_api = pod_api
        self.testbed_device_cfg = testbed_device_cfg
        self.device_config = device_config
        try:
            self.name = self.pod_api.name
        except AttributeError:
            self.name = name
        self.fut_base_dir = f'{fut_base_dir}/'

        self.rcn_attempt = 0
        self.ssh_rcn_max_attempts = 4
        self.rcn_sleep_t = 30
        self.rcn_active = False

        self.fut_dir = self.device_config.get('FUT_TOPDIR', '/tmp/fut-base')
        self.shell_timeout_org = self.device_config.get('test_script_timeout', TEST_SCRIPT_TIMEOUT)
        self.test_script_timeout = self.device_config.get('test_script_timeout', TEST_SCRIPT_TIMEOUT)

        if 'client' not in self.name:
            self.capabilities = Config(get_model_capabilities(self.device_config.get('pod_api_model', self.server_handler.testbed_cfg.get(f'{self.name.upper()}_CFG_FOLDER'))))
        else:
            self.capabilities = self.device_config

        self.regulatory_domain = self.capabilities.get('regulatory_domain', 'US')

        if not self.capabilities.get("logread_tail"):
            self.log_tail_cmd = f'PATH={self.capabilities.get("shell_path")} logread -f'
        else:
            self.log_tail_cmd = self.capabilities.get("logread_tail")

    def attach_log_file(self):
        """Attaches logread file to Allure report.

        Returns:
            (bool): True if Allure attachment was successfully attached.
        """
        try:
            dump = self.get_log_tail()
            if isinstance(dump, tuple) and dump[0] == 'ZIP':
                allure.attach.file(dump[1], name=f'logread_{self.name.upper()}', extension='zip')
                # Remove ZIP file after attaching it to Allure
                try:
                    os.remove(dump[1])
                except Exception as e:
                    log.warning(f'Failed to remove {dump[1]} file\n{e}')
            else:
                allure.attach(
                    name=f'LOGREAD-{self.name.upper()}',
                    body=dump,
                )
        except Exception as e:
            log.warning(f'Failed to Attach Allure report\n{e}')
        return True

    def _check_ssh_connection_down(self):
        """Check if SSH connection to the device is down.

        Check is executed by executing a simple 'ls' command.
        Each exit code not equal to 0 is considered as lost connection.
        SSH connection to the device is required for executing the commands and
        must be re-established if broken.

        Returns:
            (bool): True if SSH connection to the device is lost, False otherwise.
        """
        try:
            res = self.pod_api.run_raw('ls /', timeout=5)[0]
            log.debug(f'Check SSH connection exit_code={res}')
            # Each exit_code != 0 is treated as SSH disconnection.
            return res != 0
        except Exception:
            # Each exception is treated as SSH disconnection.
            return True

    def _check_transfer_fut(self):
        """Check if FUT files were transferred to the device.

        It also creates and prepares environment variables on the device.

        Returns:
            (bool): True if files were transferred and environment was set-up, False otherwise.
        """
        # Check for /shell/lib folder, since manager transfer will create fut-base/shell/
        fut_ls_check = self.pod_api.run_raw(f'ls -la {self.fut_dir}/shell/lib')[0]
        if fut_ls_check != 0:
            log.info(f'{self.fut_dir} missing on device')
            self.transfer(full=True)
            self.create_and_transfer_fut_set_env()
            return True
        else:
            return False

    def _pod_api_run_raw_wrapper(self, cmd, timeout):
        """Execute the 'run_raw' method on 'pod_api' wrapper.

        Args:
            cmd (str): Command to execute
            timeout (int): Allowed execution timeout

        Returns:
            (int): Exit code
        """
        return self.pod_api.run_raw(cmd, timeout=timeout, combine_std=True)

    def _start_rcn_procedure(self):
        """Start reconnection procedure to the device.

        Method tries to reconnect 'ssh_rcn_max_attempts' number of times.
        Between each unsuccessful attempt pauses and retries if not already
        tried 'ssh_rcn_max_attempts' times.

        Raises:
            ConnectionError: Device could not reconnect.

        Returns:
            (bool): True if reconnection is successful.
        """
        log.warning('Lost SSH connection')
        log.info('Starting SSH reconnection procedure')
        self.rcn_active = True
        while self.rcn_active:
            if self.rcn_attempt > self.ssh_rcn_max_attempts:
                self.rcn_attempt = 0
                self.rcn_active = False
                raise ConnectionError(f'Lost connection to device - {self.name}')
            log.debug(f'Waiting {self.rcn_sleep_t}s before next reconnection attempt')
            time.sleep(self.rcn_sleep_t)
            if self._check_ssh_connection_down():
                log.warning(f'Could not establish SSH connection - attempt {self.rcn_attempt}')
                self.rcn_attempt += 1
            else:
                log.debug(f'SSH connection re-established - attempt {self.rcn_attempt}')
                log.info('SSH connection re-established')
                self.rcn_attempt = 0
                self.rcn_active = False
                break
        return True

    def configure_wifi_security(self, wifi_security_type='wpa', encryption='WPA2', psk='FutTestPSK'):
        """Configure wifi security arguments.

        Configures wifi security arguments with 'security' field if wifi_security_type
        is 'legacy' or with 'wpa' fields if wifi_security_type is 'wpa'.

        Args:
            wifi_security_type (str): wifi security type - 'legacy' or 'wpa'
            psk (str) or (list): psk key or list of keys for multi_psk
            encryption (str): Encryption method used.

        Raises:
            Exception: Device does not support wpa fields if wifi_security_type==wpa.
            Exception: Incorrect wifi_security_type parameter.

        Returns:
            (list): list of wifi security configuration parameters.
        """
        try:
            if encryption.upper() == 'WPA2':
                wpa_key = "wpa2-psk"
            elif encryption.upper() == 'WPA3':
                wpa_key = "sae"
            elif encryption.upper() == 'WPA3-TRANSITION':
                wpa_key = '\'["set",["sae","wpa2-psk"]]\''
            elif encryption.upper() != 'OPEN':
                raise
        except Exception:
            raise FailedException(f'Invalid encryption type {encryption} provided. Supported [open, WPA2, WPA3-personal, WPA3-transition]')

        if type(psk) == str:
            psk_list = [psk]
        elif type(psk) == list:
            psk_list = psk
        else:
            raise FailedException(f'Invalid psk value provided: {psk} provided. Supported types are str or list')

        if encryption.upper() == 'WPA3':
            wpa3_supported = self.run('tools/device/check_wpa3_compatibility')
            if wpa3_supported != 0:
                raise Exception('WPA3 is not compatible on device!')

        if wifi_security_type == 'legacy':
            psk_list_str = ','.join([f'["key","{key}"]' for key in psk_list])
            security = '\'["map",[]]\'' if encryption.upper() == 'OPEN' else f'\'["map",[["encryption","{wpa_key.upper()}"],{psk_list_str}]]\''
            wifi_security_args = [
                f'-security {security}',
            ]
        elif wifi_security_type == 'wpa':
            wpa_supported = self.run('tools/device/ovsdb/check_ovsdb_table_field_exists', get_command_arguments('Wifi_VIF_Config', 'wpa'))
            if wpa_supported != 0:
                raise Exception(f"'wpa' fields are not supported on the '{self.name}' device!")

            if encryption.upper() == 'OPEN':
                wifi_security_args = [
                    '-wpa "false"',
                ]
            else:
                wpa_psk_list_str = ','.join([f'["key-{index}","{key}"]' for index, key in enumerate(psk_list)])
                wpa_oftag_list_str = ','.join([f'["key-{index}","key-tag--{index}"]' for index, key in enumerate(psk_list)])
                wpa_psks = f'\'["map",[{wpa_psk_list_str}]]\''
                wpa_oftags = f'\'["map",[{wpa_oftag_list_str}]]\''
                wifi_security_args = [
                    '-wpa "true"',
                    f'-wpa_psks {wpa_psks}',
                    f'-wpa_oftags {wpa_oftags}',
                    f'-wpa_key_mgmt {wpa_key}',
                ]

        else:
            raise Exception("Incorrect 'wifi_security_type' option passed, supported: 'legacy', 'wpa'")

        return wifi_security_args

    def execute(self, *args, **kwargs):
        """Call 'execute_raw' method and return its exit code.

        Returns:
            (int): Exit code
        """
        return self.execute_raw(*args, **kwargs)[0]

    def execute_raw(self, cmd, as_sudo=False, print_out=False, **kwargs):
        """Execute the command provided as 'cmd' parameter on the device.

        Command can be optionally executed as sudo (Super User), and can optionally
        print-out the execution progress.

        Args:
            cmd (str): Command to execute
            as_sudo (bool, optional): Run command as 'super user'. Defaults to False.
            print_out (bool, optional): Enable print-outs. Defaults to False.

        Raises:
            e: Any raised exception during the command execution

        Returns:
            (int, str, str):  Exit code, std_out, std_err
        """
        # Prepend sudo if command is to be executed with super user privileges.
        if as_sudo:
            cmd = f'sudo {cmd}'

        # Load kwargs or set defaults
        timeout = self.test_script_timeout * 10 if 'timeout' not in kwargs else kwargs['timeout']
        disable_fut_exception = False if 'disable_fut_exception' not in kwargs else kwargs['disable_fut_exception']
        do_cloud_log = False if 'do_cloud_log' not in kwargs else kwargs['do_cloud_log']
        do_mqtt_log = False if 'do_mqtt_log' not in kwargs else kwargs['do_mqtt_log']
        do_gatekeeper_log = False if 'do_gatekeeper_log' not in kwargs else kwargs['do_gatekeeper_log']
        step_name = False if 'step_name' not in kwargs else kwargs['step_name']
        expected_ec = EXPECTED_EC if 'expected_ec' not in kwargs else kwargs['expected_ec']
        # If script is executed on other device than 'dut', always
        # attach DUT logread as well.
        logread_devices = ['dut'] if self.name == 'dut' else ['dut', self.name]

        # Start execution
        cmd_start = time.strftime("%H:%M:%S")
        if self.server_handler.dry_run:
            log.info(f'DRY-RUN: ({self.name}): {cmd}')
            cmd_res = (0, f'<!!! REPLACE THIS FROM {self.name} `{cmd}` OUTPUT !!!>', False)
        else:
            log.info(f'Executing ({self.name}): {cmd}')
            try:
                # Start log tail on selected devices
                try:
                    for logread_device in logread_devices:
                        if logread_device in self.server_handler.device_handlers:
                            self.server_handler.device_handlers[logread_device].start_log_tail()
                    cmd_res = self._pod_api_run_raw_wrapper(cmd, timeout)
                except SshException:
                    cmd_res = [255]
                # SSH down detection
                # Workaround for SSH down detection cause limitation of parallelssh.execute_commands - Popen().communicate()
                # On SSH down, exit_code 255 is returned
                # some processes may return exit_code 255 as well, re-checking exit_code 255 with 'ls /' command
                if cmd_res[0] == 255 and self._check_ssh_connection_down():
                    # Start reconnection procedure, raises ConnectionError on fail
                    self._start_rcn_procedure()
                    # Check and transfer fut-base if needed
                    self._check_transfer_fut()
                    # Re-run command again
                    cmd_res = self._pod_api_run_raw_wrapper(cmd, timeout)
                elif cmd_res[0] == 127 or \
                        (as_sudo and cmd_res[0] == 1 and 'command not found' in cmd_res[1]) or \
                        (cmd_res[0] == 2 and 'No such file or directory' in cmd_res[1]):
                    did_transfer = self._check_transfer_fut()
                    if did_transfer:
                        cmd_res = self._pod_api_run_raw_wrapper(cmd, timeout)
            except Exception as e:
                print(get_section_line(self.name, cmd, 'exception', 'start'))
                print(str(e))
                print(get_section_line(self.name, cmd, 'exception', 'stop'))
                raise e
            finally:
                for logread_device in logread_devices:
                    if logread_device in self.server_handler.device_handlers:
                        self.server_handler.device_handlers[logread_device].stop_log_tail()
        cmd_end = time.strftime("%H:%M:%S")

        # Log result
        cmd_ec = cmd_res[0]
        cmd_std_out = '' if not cmd_res[1] else cmd_res[1]
        cmd_std_err = '' if not cmd_res[2] else cmd_res[2]
        std_err_log = f"\nstd_err={cmd_std_err}" if cmd_ec != 0 else ''

        # Add command to recipe
        log.debug(f"device={self.name}, cmd={cmd}, ec={cmd_ec}{std_err_log}")
        self.recipe.add(device=self.name, cmd=cmd, start_t=cmd_start, end_t=cmd_end, ec=cmd_ec)

        cmd_std_out, info_dump = get_info_dump(cmd_std_out)
        # Print result if needed
        if print_out or cmd_ec != 0:
            try:
                script_name = re.search(r'([\w\d\-.]+\.sh|[\w\d\-.]+\.py)', cmd).group()
            except Exception:
                script_name = cmd

            if cmd_std_out != '':
                cmd_std_out_p = f'{get_section_line(self.name, cmd, "output", "start")}\n' \
                    f'{cmd_std_out}\n' \
                    f'{get_section_line(self.name, cmd, "output", "stop")}'
            else:
                cmd_std_out_p = get_section_line(self.name, cmd, 'No output')
            print(cmd_std_out_p)

            try:
                with allure.step(f'{self.name} - {script_name if not step_name else step_name}'):
                    # Attach command output
                    allure.attach(
                        name='OUTPUT',
                        body=cmd_std_out_p,
                    )
                    # Attach command info-dump if exists
                    if info_dump:
                        allure.attach(
                            name='INFO-DUMP',
                            body=info_dump,
                        )
                    # STD-ERR is most likely to always be empty, but just in case to cover it
                    if cmd_std_err != '':
                        cmd_std_err_p = f'{get_section_line(self.name, cmd, "std_err", "start")}\n' \
                                        f'{cmd_std_err}\n' \
                                        f'{get_section_line(self.name, cmd, "std_err", "stop")}'
                        allure.attach(
                            name=f'STD-ERR - {script_name if not step_name else step_name}',
                            body=cmd_std_err_p,
                        )
                        print(cmd_std_err_p)

                    # On any failure, do logread dump to specific failing step
                    if cmd_ec != expected_ec or LOG_PASS:
                        for logread_device in logread_devices:
                            self.server_handler.device_handlers[logread_device].attach_log_file()
                        if do_cloud_log:
                            try:
                                dump = self.server_handler.fut_cloud.dump_log()
                            except Exception as e:
                                dump = f'Failed to generate FUT Cloud logread section\n{e}'
                            try:
                                allure.attach(
                                    name='LOGREAD-CLOUD',
                                    body=dump,
                                )
                            except Exception as e:
                                log.warning(f'Failed to Attach Allure report\n{e}')
                        if do_mqtt_log:
                            try:
                                dump = self.server_handler.execute_raw(self.server_handler.mqtt_dump_cmd)[1]
                            except Exception as e:
                                dump = f'Failed to generate FUT MQTT logread section\n{e}'
                            try:
                                allure.attach(
                                    name='LOGREAD-MQTT',
                                    body=dump,
                                )
                            except Exception as e:
                                log.warning(f'Failed to Attach Allure report\n{e}')
                        if do_gatekeeper_log:
                            try:
                                dump = self.server_handler.execute_raw(self.server_handler.gatekeeper_dump_cmd)[1]
                            except Exception as exception:
                                dump = f'Failed to generate FUT Gatekeeper logread section\n{exception}'
                            try:
                                allure.attach(
                                    name='LOGREAD-GATEKEEPER',
                                    body=dump,
                                )
                            except Exception as exception:
                                log.warning(f'Failed to Attach Allure report\n{exception}')
                    assert cmd_ec == expected_ec
            except AssertionError:
                pass
            except Exception as e:
                log.warning(f'Exception caught during Allure attachment creation\n{e}')

        # Propagate FUT Shell exception if needed
        if not disable_fut_exception:
            self.fut_exception.fut_raise(cmd_res)

        # Return exit_code, std_out, std_err
        return cmd_ec, cmd_std_out, cmd_std_err

    def get_if_names(self, join=False):
        """Return device radio interface names from the device capabilities file.

        Args:
            join (bool, optional): Returned interface names are joined with spaces in between.
                                   Defaults to False.

        Returns:
            (str): Interface names as string.
        """
        if_names = [value for key, value in self.capabilities.get('interfaces.phy_radio_name').items() if value is not None]
        return ' '.join(if_names) if join else if_names

    def get_log_read(self):
        """Determine the 'logread' command for the device.

        Takes info from device capabilities.

        Returns:
            (list): String as list
        """
        if not self.capabilities.get('logread', False):
            return ["LOGREAD not available on this device"]
        return self._pod_api_run_raw_wrapper(f'{self.capabilities.get("logread")}', timeout=20)[1]

    def get_log_tail(self):
        """_summary_.

        Returns:
            _type_: _description_
        """
        if self.log_tail_file_name:
            # Get file size in MB
            file_size = Path(self.log_tail_file_name).stat().st_size / (1024 * 1024)
            # If size is greater than 5MB, zip the file
            if file_size > 5:
                zip_file_name = f'{self.log_tail_file_name}.zip'
                zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED).write(self.log_tail_file_name)
                # remove log file after zipping it
                self.remove_log_tail_file()
                return 'ZIP', zip_file_name

            try:
                with open(self.log_tail_file_name, encoding='utf-8', errors='replace') as file:
                    dump = file.read()
            except Exception as e:
                log.warning(f'Failed to open/decode log tail file #1\n{e}')
                try:
                    with open(self.log_tail_file_name, errors='replace') as file:
                        dump = file.read()
                except Exception as e:
                    log.warning(f'Failed to open/decode log tail file #2\n{e}')
                    # Fallback to old way LOGREAD fetch
                    dump = self.get_log_read()
            # Remove dump file after reading it
            self.remove_log_tail_file()
            dump = f'{self.name} - {self.log_tail_file_name}\n{dump}'
        else:
            # Fallback to old way LOGREAD fetch
            dump = self.get_log_read()
        return dump

    def get_remote_test_command(self, test_path, params="", suffix=".sh", folder='shell'):
        """Return string which represents the path to the script.

        Besides the script to be executed, provides the parameters that the
        script requires.

        Args:
            test_path (str, required): Path to the script to be executed
            params (str, optional): Script parameters. Defaults to "". suffix,
            (str, optional): Script suffix. Defaults to ".sh".
            folder (str, optional): Script folder. Defaults to 'shell'.

        Returns:
            (str): Command to be executed with the provided parameters
        """
        # Contruct the command (script) to be executed
        remote_command = f"{self.fut_dir}/{folder}/{test_path}{suffix}".replace('///', '/').replace('//', '/')
        # Append command parameters to the command
        remote_command = f"{remote_command} {params}"
        return remote_command

    def remove_log_tail_file(self):
        """Remove log_tail file from the device.

        If not being able to remove, logs warning.

        Returns:
            (bool): True, always
        """
        try:
            os.remove(self.log_tail_file_name)
            log.debug(f'Log file {self.log_tail_file_name} was removed')
        except Exception as e:
            log.warning(f'Failed to remove log file\n{e}')
        return True

    def run(self, path, args='', **kwargs):
        """Execute the 'run_raw' method.

        Prepares the arguments for the script to be executed if arguments are
        provided.

        Args:
            path (str): Path to the script
            args (str, optional): Script arguments. Defaults to ''.

        Returns:
            (int): Exit code
        """
        if isinstance(args, list):
            args = ' '.join(args)
        return self.run_raw(path, args, print_out=True, **kwargs)[0]

    def run_raw(self, path, args='', **kwargs):
        """Execute the 'execute_raw' method.

        Args:
            path (str): Path to the script
            args (str, optional): Script arguments. Defaults to ''.

        Returns:
            (int): Exit code
        """
        suffix = ".sh" if 'suffix' not in kwargs else kwargs['suffix']
        folder = 'shell' if 'folder' not in kwargs else kwargs['folder']
        remote_command = self.get_remote_test_command(path, args, suffix, folder)
        return self.execute_raw(remote_command, **kwargs)

    def start_log_tail(self):
        """Start 'log_tail' process on the device.

        Method will create log file according to current time and date, and
        start a logging subprocess on the device.
        If not being able to start 'log_tail' processes, it will only log
        warning, not an exception.

        Returns:
            (bool): True, always
        """
        self.log_tail_file_name = f'/tmp/{self.name}_{time.strftime("%Y%m%d-%H%M%S")}.log'
        self.log_tail_file = open(self.log_tail_file_name, 'w')
        # Required timeout of at least 70 seconds due to hardcoded channel set timeout of 60s
        log_tail_start_cmd = f'timeout {70 if self.test_script_timeout <= 70 else self.test_script_timeout}' \
                             f' sshpass -p {self.capabilities.get("password")}' \
                             f' ssh -A -t' \
                             ' -o StrictHostKeyChecking=no' \
                             ' -o UserKnownHostsFile=/dev/null' \
                             ' -o ForwardAgent=yes' \
                             ' -o HostKeyAlgorithms=ssh-dss,ssh-rsa,ssh-ed25519' \
                             f' {self.capabilities.get("username")}@{self.testbed_device_cfg.get("mgmt_ip")} ' \
                             f' {self.log_tail_cmd}'
        log.debug(f'Log tailing command\n{log_tail_start_cmd}')
        try:
            self.log_tail_process = subprocess.Popen(log_tail_start_cmd.split(), stdout=self.log_tail_file,
                                                     stderr=self.log_tail_file, shell=False)
        except Exception as e:
            log.warning(f'Issue while starting log tailing process\n{e}')
        return True

    def stop_log_tail(self):
        """Stop all 'log_tail' processes on the device.

        If not being able to stop 'log_tail' processes, it will only log
        warning, not an exception.

        Returns:
            (bool): True, always
        """
        if self.log_tail_process:
            # Send SIGTERM to log tail pids
            try:
                os.killpg(os.getpgid(self.log_tail_process.pid), signal.SIGTERM)
                self.log_tail_process.kill()
            except Exception as e:
                log.warning(f'Failed to kill log tailing process\n{e}')
            # Kill any logread_tail command running on the device as well
            try:
                self.pod_api.run_raw('kill $(pgrep -f "logread -f") || true', timeout=2)
            except Exception as e:
                log.warning(f'Failed to kill log tailing process on device\n{e}')
        return True

    # TRANSFER START #
    def clear_resource_folder(self):
        """Remove contents of the resource/ folder on an OpenSync device.

        Returns:
            (bool): True, always
        """
        resource_path = f'{self.fut_dir}/resource/'
        cmd = f"[ -d {resource_path} ] && rm -rf {resource_path}"
        exit_code = self.execute(cmd)
        if exit_code != 0:
            log.warning(f'Failed to empty {resource_path} on {self.name}')
        return True

    def clear_tests_folder(self):
        """Clear 'tests' folder on the device.

        Upon not being able to remove, logs warning.

        Returns:
            (bool): True, always
        """
        tests_path = f'{self.fut_dir}/shell/tests/*'
        cmd = f"[ -d {tests_path} ] && rm -rf {tests_path}"
        exit_code = self.execute(cmd)
        if exit_code != 0:
            log.warning(f'Failed to empty {tests_path} on {self.name}')
        return True

    def create_tr_tar(self, cfg):
        """Create tar file for transfer to the device.

        Args:
            cfg (dict): Configuration dictionary

        Raises:
            Exception: tar file for the transfer could not be created.
        """
        tr_path = cfg.get('tr_path')
        log.debug('Creating tar file for transfer')
        real_path = self.fut_base_dir
        additional_files = ' ' .join([f'{additional_path}' for additional_path in self.server_handler.additional_files])
        if cfg.get('full', False):
            tar_cmd = f'tar -cf {tr_path} {self.fut_base_dir}shell/ {additional_files}'
        elif cfg.get('manager', False):
            tar_cmd = f'tar -cf {tr_path} {self.fut_base_dir}shell/tests/{cfg.get("manager")} {additional_files}'
        elif cfg.get('file', False) or cfg.get('folder', False):
            tmp_path_param = cfg.get('file', False) if cfg.get('file', False) else cfg.get('folder', False)
            real_path = tmp_path_param if Path(tmp_path_param).is_absolute() else f'{self.fut_base_dir}/{tmp_path_param}'
            tar_cmd = f'tar -cf {tr_path} {real_path}'
            if Path(real_path).name:
                temp_real_path = real_path.rstrip('/')
                real_path = os.path.dirname(temp_real_path) + '/'
        else:
            tar_cmd = f'tar -cf {tr_path} {real_path}shell/lib {real_path}shell/config {real_path}shell/tools ' \
                      f'{additional_files}'

        tar_home_reg = str(Path(real_path).relative_to('/')).replace('/', '\\/')
        tar_to_reg = str(Path(cfg.get('to', self.fut_dir)).relative_to('/')).replace('/', '\\/')
        tar_cmd = tar_cmd + f" --transform 's/{tar_home_reg}/{tar_to_reg}/'"
        log.debug(f'Executing (server): {tar_cmd}')
        # Create tar file.
        tar_ec = os.system(tar_cmd)
        if tar_ec != 0:
            raise Exception(f'Failed to create tar file for transfer\ncfg: {cfg}\ntar_cmd: {tar_cmd}\ntar_ec: {tar_ec}')

    def transfer(self, *args, **kwargs):
        """Create tar file.

        Method creates designated directory on the device, transfers fut tar file
        to the device, unpacks the contents into the designated directory, sets
        permissions, removes the file after unpack and updates shell paths.

        Raises:
            Exception: Unpack of transferred tar file failed.
            Exception: Setting permissions failed.
            Exception: Removing the tar file failed.
            Exception: Updating shell paths failed.

        Returns:
            (bool): True, on success
        """
        cfg = Config({
            'tr_name': kwargs.get('tr_name') if kwargs.get('tr_name') else 'fut_tr.tar',
            'direction': kwargs.get('direction') if kwargs.get('direction') else 'push',
            'to': kwargs.get('to') if kwargs.get('to') else self.fut_dir,
            'full': kwargs.get('full') if kwargs.get('full') else False,
            'manager': kwargs.get('manager') if kwargs.get('manager') else False,
            'file': kwargs.get('file') if kwargs.get('file') else False,
            'folder': kwargs.get('folder') if kwargs.get('folder') else False,
            'exec_perm': True if 'exec_perm' not in kwargs else kwargs['exec_perm'],
        })
        cfg.set('tr_path', kwargs.get('tr_path') if kwargs.get('tr_path') else f'{self.fut_base_dir}/{cfg.get("tr_name")}')

        log.info(f'Initiated transfer to {self.name}')
        log.debug(f'Transfer cfg: {cfg.cfg}')

        self.create_tr_tar(cfg)
        self.execute(f'mkdir -p {cfg.get("to")}')
        log.debug(f'Transfering {cfg.get("tr_path")} from RPI server to {cfg.get("to")} on {self.name}')
        self.pod_api.put_file(file_name=cfg.get("tr_path"), location=cfg.get("to"))

        if True:
            # Unpack tar file
            tr_name = cfg.get('tr_name')
            unpack_tar_cmd = f'cd {cfg.get("to")} && tar -C / -xf {tr_name}'
            log.debug(f'Unpacking {tr_name}: {unpack_tar_cmd}')
            unpack_res = self.execute_raw(unpack_tar_cmd)
            unpack_ec, unpack_std, unpack_std_err = unpack_res[0], unpack_res[1], unpack_res[2]
            if unpack_ec != 0:
                raise Exception(
                    f'Unpack command fail!\n'
                    f'cmd: {unpack_tar_cmd}\n'
                    f'std_out:\n{unpack_std}\n'
                    f'std_err:\n{unpack_std_err}\n'
                    f'ec: {unpack_ec}',
                )

            if cfg.get('exec_perm'):
                # Make scripts executable
                set_permission_cmd = f'find {self.fut_dir} -type f -iname "*.sh" -exec chmod 755 {{}} \\;'
                log.debug(f'Setting permissions on {self.fut_dir}: {set_permission_cmd}')
                permission_ec = self.execute(set_permission_cmd)
                if permission_ec != 0:
                    raise Exception(f'Permission command fail, set_permission_cmd: {set_permission_cmd}')

            # Remove tar file after unpack to free-up space
            rm_tar_cmd = f'rm {cfg.get("to")}/{tr_name}'
            log.debug(f'Removing {tr_name}: {rm_tar_cmd}')
            rm_ec = self.execute(rm_tar_cmd)
            if rm_ec != 0:
                raise Exception(f'Remove tar command fail, rm_tar_cmd: {rm_tar_cmd}')

            if self.fut_dir != '/tmp/fut-base':
                log.debug(f'Updating shell paths to match FUT_TOPDIR={self.fut_dir}')
                escaped_fut_dir = self.fut_dir.replace('/', '\\/')
                path_update_cmd = f"find {self.fut_dir} -type f -exec sed -i 's/\\/tmp\\/fut-base/{escaped_fut_dir}/g' {{}} + "
                path_update_res = self.execute_raw(path_update_cmd)
                if path_update_res[0] != 0:
                    raise Exception(
                        f'Failed to update shell paths\n'
                        f'{path_update_cmd}\n'
                        f'{path_update_res[2]}\n'
                        f'Please use FUT_TOPDIR=/tmp/fut-base\n',
                    )
        log.info(f'Transfer finished to {self.name}')
        return True
    # TRANSFER END #

    # SHELL ENV START #
    def create_and_transfer_fut_set_env(self):
        """Create fut_set_env file and transfer it to the device.

        Returns:
            (int): Exit code
        """
        fut_set_env_path = self.create_fut_set_env()
        return self.transfer(file=fut_set_env_path, to=f'{self.fut_dir}/')

    def create_fut_set_env(self):
        """Create file containing shell environment variables.

        Name of the file is hardcoded 'fut_set_env.sh'

        Returns:
            (str): Path to shell environment variable
        """
        shell_fut_env_path = f'{self.fut_base_dir}/fut_set_env.sh'
        shell_fut_env_file = open(shell_fut_env_path, "w")
        for key, value in self.get_shell_cfg().items():
            ini_line = f"{key}=\"{value}\"\n"
            shell_fut_env_file.write(ini_line)
        # Inform creation is a success.
        shell_fut_env_file.write('echo "${FUT_TOPDIR}/fut_set_env.sh sourced"\n')
        shell_fut_env_file.close()
        return shell_fut_env_path

    def get_model_override_dir(self, override_file):
        """Return path to the model override file.

        It will first check internal subdirectory and regular later.

        Args:
            override_file (str): Name of the model override file

        Raises:
            Exception: If file is not found.

        Returns:
            (str): Path to the model override file
        """
        model_override_subdir = 'shell/lib/override'
        model_override_paths = [
            Path(f"internal/{model_override_subdir}"),
            Path(f"./{model_override_subdir}"),
        ]
        for model_override_path in model_override_paths:
            if model_override_path.joinpath(override_file).is_file():
                break
        else:
            raise Exception(f"Can not find model override file {override_file} in {model_override_subdir}. Please make sure it exists.")
        return model_override_path.as_posix()

    def get_shell_cfg(self):
        """Prepare dictionary containing shell environment variables.

        Dictionary keys are shell variables, dictionary values are values of variables.

        Raises:
            FailedException: Shell variable was not loaded.

        Returns:
            (dict): Dictionary of shell environment variables
        """
        tmp_cfg = {}
        try:
            for key, value in self.device_config.cfg.items():
                if key.isupper():
                    tmp_cfg[key] = value
            tmp_cfg["FUT_TOPDIR"] = self.fut_dir
            tmp_cfg["DEFAULT_WAIT_TIME"] = self.test_script_timeout
            if 'client' not in self.name:
                # For DUT and REF devices
                tmp_cfg["PATH"] = self.capabilities.get('shell_path')
                if self.capabilities.get('interfaces').get('management_interface'):
                    tmp_cfg["MGMT_IFACE"] = self.capabilities.get('interfaces').get('management_interface')
                tmp_cfg["OPENSYNC_ROOTDIR"] = self.capabilities.get('opensync_rootdir')
                tmp_cfg["OVSH"] = f"{self.capabilities.get('opensync_rootdir')}" \
                                  f"/tools/ovsh --quiet --timeout={self.test_script_timeout}000"
                tmp_cfg["LOGREAD"] = self.capabilities.get('logread')
                model_override_file = self.capabilities.get('MODEL_OVERRIDE_FILE', self.device_config.get('MODEL_OVERRIDE_FILE'))
                platform_override_file = self.capabilities.get('PLATFORM_OVERRIDE_FILE', self.device_config.get('PLATFORM_OVERRIDE_FILE'))
                tmp_cfg["MODEL_OVERRIDE_FILE"] = Path(self.fut_dir).joinpath(self.get_model_override_dir(model_override_file), model_override_file).as_posix()
                tmp_cfg["PLATFORM_OVERRIDE_FILE"] = Path(self.fut_dir).joinpath(self.get_model_override_dir(platform_override_file), platform_override_file).as_posix()
                tmp_cfg["MGMT_IFACE_UP_TIMEOUT"] = 60
                tmp_cfg["MGMT_CONN_TIMEOUT"] = 2
                tmp_cfg["FUT_SKIP_L2"] = 'true' if os.getenv('FUT_SKIP_L2') == 'true' else 'false'
            else:
                tmp_cfg["PATH"] = self.device_config.get('shell_path')
        except Exception as e:
            raise FailedException(f'Failed to load shell environment variables\n\t{e}')
        return tmp_cfg

    @staticmethod
    def string_is_int(string_to_check):
        """Check if string is numeric.

        Args:
            string_to_check (str): String to be checked.

        Returns:
            (bool): True if string is numeric, False otherwise.
        """
        try:
            int(string_to_check)
            return True
        except ValueError:
            return False

    def update_shell_timeout(self, new_timeout):
        """Update the shell timeout used to limit the shell execution time.

        If new_timeout does not differ from original timeout, timeout is not
        changed.

        Args:
            new_timeout (int): New shell timeout

        Returns:
            (bool): True if timeout is not set, Exit code otherwise.
        """
        if not new_timeout and self.test_script_timeout == self.shell_timeout_org:
            return True

        if new_timeout:
            if new_timeout == self.test_script_timeout:
                return True
        else:
            if self.test_script_timeout == self.shell_timeout_org:
                return True
            new_timeout = self.shell_timeout_org

        log.info(f'Changing shell timeout from {self.test_script_timeout} to {new_timeout}')
        self.__setattr__('test_script_timeout', new_timeout)
        self.create_and_transfer_fut_set_env()
        self.recipe.clear()
    # SHELL ENV END #

    # UTILITY START #
    def get_version(self):
        """Return the version of any device that is a part of the testbed.

        Support of the client device differs to others, the function handles
        fetching the client version by executing the command
        defined in client capabilities.

        Raises:
            FailedException: Client version command is not defined.
            FailedException: Client version could not be acquired.
            FailedException: Device version could not be acquired.

        Returns:
            (str): Version of the device.
        """
        if 'client' in self.name:
            device_version_cmd = self.capabilities.get('device_version_cmd', None)
            if not device_version_cmd:
                raise FailedException('Could not acquire device version for client. Version command not defined')
            dev_ver_res = self.execute_raw(device_version_cmd)
            if dev_ver_res[0] != 0:
                raise FailedException(f'Could not acquire device version!\n'
                                      f'cmd: {device_version_cmd}\n'
                                      f'ec: {dev_ver_res[0]}\n'
                                      f'std_err: {dev_ver_res[2]}')
            return dev_ver_res[1].rstrip()
        else:
            device_version = self.pod_api.version()
            if not device_version:
                raise FailedException('Could not acquire device version for device')
            return device_version
    # UTILITY END #

    # CAPABILITIES START #
    def get_bridge_type(self):
        """Query the device kconfig option for the networking bridge type.

        Returns:
            string: The networking bridge type retrieved from the device: 'native_bridge', 'ovs_bridge'.
        """
        bridge_type = 'ovs_bridge'
        try:
            check_kconfig_native_bridge_args = get_command_arguments('CONFIG_TARGET_USE_NATIVE_BRIDGE', 'y')
            if self.run('tools/device/check_kconfig_option', check_kconfig_native_bridge_args) == 0:
                bridge_type = 'native_bridge'
        except Exception as e:
            log.warning(f'Failed to retrieve bridge type\n{e}')
        return bridge_type

    def get_radio_band_from_channel(self, channel):
        """Return radio band of the device.

        Radio band based on the provided channel and radio channels lists for
        interfaces read from device capabilities.

        Args:
            (int): WiFi channel

        Returns:
            (str): Radio band of the device
        """
        radio_channels = self.capabilities.get('interfaces.radio_channels')
        for band in radio_channels:
            channels = radio_channels[band]
            if channels is not None and (str(channel) in channels or channel in channels):
                return band
        raise FailedException(f'Could not determine radio_band_from channel. Channel {channel} '
                              f'is not in capabilities::interfaces.radio_channels')

    def get_radio_band_from_channel_and_band(self, channel, remote_radio_band):
        """Return the radio_band of one device.

        Return value is based on the provided channel and radio_band of another
        device. This is useful if we have band information for gateway device,
        but would like to extract the radio_band of the leaf.

        Example: what is the band of the local device, given the channel and
            band info of remote device?
            Remote device: channel = 157, remote_radio_band = 5gu (tri band device)
            Local device: channel = 157, radio_band = 5g (dual band device)
        Same example with different band: we can not infer band from channel,
            due to 6g overlapping channels
            Remote device: channel = 1, remote_radio_band = 6g
            Local device: channel = 1, radio_band = 6g

        Args:
            channel (int): WiFi channel - both devices
            remote_radio_band (str): Radio band of "remote" device. Supported "24g", "5g", "5gl", "5gu", "6g".

        Returns:
            (str): Radio band of "local" device.
                   Supported "24g", "5g", "5gl", "5gu", "6g".
        """
        orig_radio_channels = self.capabilities.get('interfaces.radio_channels')
        radio_channels = {k: v for k, v in orig_radio_channels.items() if v is not None}
        for band in radio_channels:
            channels = radio_channels[band]
            channel_in_band = (str(channel) in channels or channel in channels)
            matching_bands = band[:2] in remote_radio_band[:2]
            if channel_in_band and matching_bands:
                return band
        raise Exception(f'Could not determine radio_band for channel={channel} and remote_radio_band={remote_radio_band}')

    def get_region(self):
        """Query the device regulatory domain.

        Method stores this information into the device handler.

        Returns:
            (str): The regulatory domain retrieved from the device
        """
        try:
            reg = self.pod_api.get_region()
            if str(reg).upper() in ['US', 'EU', 'GB']:
                self.regulatory_domain = f'{reg}'.upper()
                log.debug(f'Device {self.name} regulatory_domain is set to {self.regulatory_domain}')
            else:
                raise FailedException(f'Invalid region on device\n{reg}')
        except Exception as e:
            log.warning(f'Failed to retrieve device region\n{e}')
        return self.regulatory_domain

    def validate_channel_ht_mode_band(self, channel, ht_mode, radio_band):
        return validate_channel_ht_mode_band(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            reg_domain=self.regulatory_domain,
            raise_broken=True,
            regulatory_rule=self.server_handler.regulatory_rule,
        )
    # CAPABILITIES END #
