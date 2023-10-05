import os
import signal
import subprocess
import time
import zipfile
from pathlib import Path

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import (
    allure_attach_log_file,
    allure_script_execution_post_processing,
)
from lib_testbed.generic.client.client import Client
from lib_testbed.generic.pod.pod import Pod
from lib_testbed.generic.util.logger import log


class DeviceHandler:
    def __init__(self, name):
        log.debug("Entered DeviceHandler class")
        self.name = name
        self.device_type = "node" if name in ["gw", "l1", "l2"] else "client"
        self.fut_configurator = FutConfigurator()
        self.testbed_cfg = self.fut_configurator.testbed_cfg
        self.device_osrt_config = self._extract_device_osrt_config()
        self.hostname = self.device_osrt_config.get("host", {}).get("name")
        # This is the path to local directory where FUT is executed
        self.fut_base_dir = Path(__file__).absolute().parents[1].as_posix()
        # This is the path to the remote directory on the testbed device
        self.fut_dir = "/tmp/fut-base"
        self.log_tail_process = None
        self.log_tail_file = None
        self.log_tail_file_name = None
        self.device_api = self._get_device_api()
        self.rcn_active = False
        self.rcn_attempt = 0
        self.ssh_rcn_max_attempts = 4
        self.rcn_sleep_time = 30

        if not self.device_type == "client":
            self.capabilities = self.device_api.capabilities

        self.username = self.device_osrt_config["capabilities"]["username"]
        self.password = self.device_osrt_config["capabilities"]["password"]
        self.test_script_timeout = 180
        self.regulatory_shell_file = self.fut_configurator.regulatory_shell_file

        if self.device_type == "node":
            self.model = self.device_osrt_config["model"]
            self.device_config = self._extract_device_config()
        else:
            self.model = self.device_osrt_config["type"]
            self.device_config = self._extract_client_config()

        self.version = self._version()

    def _extract_device_osrt_config(self):
        """
        Extract device configuration.

        Extracts the configuration as it pertains to its role in the
        testbed.

        Raises:
            RuntimeError: If device configuration cannot be extracted.

        Returns:
            (dict): Device configuration.
        """
        device_config = {}
        device_type = self.device_type.capitalize()

        for device in self.testbed_cfg[f"{device_type}s"]:
            if self.name in device.values():
                device_config = device

        if not device_config:
            raise RuntimeError(f"Failed to extract {self.name} device configuration.")

        return device_config

    def _extract_device_config(self):
        """
        Extract device configuration.

        Loads the device configuration from the capabilities and
        prepares the required parameters as a dictionary.

        Returns:
            (dict): Device configuration as a dictionary.
        """
        test_script_timeout = 60
        wifi_vendor = self.capabilities.get_wifi_vendor()
        model = self.model.lower()
        # Assemble device configuration parameters
        model_config = {
            "pod_api_model": model,
            "py_test_timeout": test_script_timeout + 10,
            "test_script_timeout": test_script_timeout,
            "MODEL_OVERRIDE_FILE": f"{model}_lib_override.sh",
            "FUT_TOPDIR": "/tmp/fut-base",
            "PLATFORM_OVERRIDE_FILE": f"{wifi_vendor}_platform_override.sh",
        }

        return model_config

    def _extract_client_config(self):
        """
        Extract the client device configuration.

        Loads the client configuration from the capabilities and
        prepares the required parameters as a dictionary.

        Returns:
            (dict): Client configuration as a dictionary.
        """
        # Assemble client device configuration parameters
        device_config = {
            "model_string": self.model,
            "pod_api_model": self.model,
            "shell_path": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games",
            "username": self.username,
            "password": self.password,
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

    def _get_device_api(self):
        """
        Get pod or client API handler.

        The handler provides access to functions from lib_testbed for
        managing and configuring OSRT devices.

        Returns:
            (obj): Device API 'pod' or 'client' object.
        """
        if self.device_type == "client":
            device_obj = Client()
        else:
            device_obj = Pod()

        device_api = device_obj.resolve_obj(**{"config": self.testbed_cfg, "nickname": self.name})
        device_api = device_api

        return device_api

    def _clear_folder(self, folder_path):
        """Remove contents of the target folder on the remote device."""
        if not Path(folder_path).is_absolute():
            folder_path = f"{self.fut_dir}/{folder_path}/"
        cmd = f"[ -d {folder_path} ] && rm -rf {folder_path}"
        ret = self.device_api.run_raw(cmd)
        if ret[0] != 0:
            log.warning(f"Failed to empty {folder_path} on {self.name}.")
        return True

    def clear_resource_folder(self):
        return self._clear_folder(folder_path="resource")

    def clear_tests_folder(self):
        return self._clear_folder(folder_path="shell/tests")

    @staticmethod
    def sanitize_arg(arg):
        """
        Sanitize the argument of selected characters.

        Args:
            arg (str): Argument to be sanitized.

        Returns:
            (str): Sanitized argument.
        """
        try:
            # Argument is surrounded by "" or '' or starts with -
            if (arg[0] == '"' and arg[-1] == '"') or (arg[0] == "'" and arg[-1] == "'") or (arg[0] == "-"):
                arg = arg
            elif " " in arg:
                if '"' in arg:
                    arg = arg.replace('"', '"')
                arg = f'"{arg}"'
            else:
                arg = arg
        except Exception as e:
            log.warning(f"Encountered exception while sanitizing arguments: {e}")
            arg = arg

        return arg

    def get_command_arguments(self, *args):
        """
        Return command arguments.

        Returns command arguments as a string to feed the script.
        Command arguments are separated by a space and with escaped "
        or ' characters if present in arguments. Uses recursion if
        argument is a list.

        Returns:
            (str): Command arguments as a string.
        """
        command = ""

        for arg in args:
            if isinstance(arg, list):
                return self.get_command_arguments(arg)
            else:
                if isinstance(arg, str):
                    arg = arg.strip()
                command = str(command) + " " + str(self.sanitize_arg(arg))

        return command

    def get_remote_test_command(self, test_path, params="", suffix=".sh", folder="shell"):
        """
        Construct a string which represents the path to the script.

        Besides the script to be executed, provides the parameters
        that the script requires.

        Args:
            test_path (str): Path to the script to be executed.
            params (str): Script parameters. Defaults to "".
            suffix (str): Script suffix. Defaults to ".sh".
            folder (str): Script folder. Defaults to 'shell'.

        Returns:
            (str): Command to be executed with the provided parameters.
        """
        # Construct the command (script) to be executed
        remote_command = f"{self.fut_dir}/{folder}/{test_path}{suffix}".replace("///", "/").replace("//", "/")
        # Append command parameters
        remote_command = f"{remote_command} {params}"

        return remote_command

    def _start_log_tail(self):
        """
        Start log tailing process on the device.

        Method will create a log file according to current time and
        date, and start a logging subprocess on the device. If the log
        tailing processes is not executed correctly, it will only log a
        warning and not an exception.

        Returns:
            (bool): True, always.
        """
        self.log_tail_file_name = f'/tmp/{self.name}_{time.strftime("%Y%m%d-%H%M%S")}.log'
        self.log_tail_file = open(self.log_tail_file_name, "w")
        # Required timeout of at least 70 seconds due to hardcoded channel set timeout of 60s
        log_tail_start_cmd = (
            f"timeout {70 if self.test_script_timeout <= 70 else self.test_script_timeout}"
            f" sshpass -p {self.password}"
            f" ssh -A -t"
            " -o StrictHostKeyChecking=no"
            " -o UserKnownHostsFile=/dev/null"
            " -o ForwardAgent=yes"
            " -o HostKeyAlgorithms=ssh-dss,ssh-rsa,ssh-ed25519"
            f" {self.hostname} "
            f" /usr/opensync/tools/{self.capabilities.get_logread_command()} -f "
        )
        log.debug(f"Log tailing command: {log_tail_start_cmd}")

        try:
            self.log_tail_process = subprocess.Popen(
                log_tail_start_cmd.split(),
                stdout=self.log_tail_file,
                stderr=self.log_tail_file,
                shell=False,
            )
        except Exception as e:
            log.warning(f"Encountered issue while starting log tailing process: {e}")

        return True

    def _stop_log_tail(self):
        """
        Stop all log tailing processes on the device.

        If the log tailing processes are not stopped correctly, it will
        only log a warning.

        Returns:
            (bool): True, always
        """
        if self.log_tail_process:
            # Send SIGTERM to log tail pids
            try:
                os.killpg(os.getpgid(self.log_tail_process.pid), signal.SIGTERM)
                self.log_tail_process.kill()
            except Exception as e:
                log.warning(f"Failed to kill log tailing process: {e}")

            # Kill any logread_tail command running on the device as well
            try:
                self.device_api.run_raw('kill $(pgrep -f "logread -f") || true', timeout=2, skip_logging=True)
            except Exception as e:
                log.warning(f"Failed to kill log tailing process on device: {e}")

        return True

    def _remove_log_tail_file(self):
        """
        Remove the log tailing file from the device.

        Logs a warning if the log tailing file cannot be removed.

        Returns:
            (bool): True, always
        """
        try:
            os.remove(self.log_tail_file_name)
            log.debug(f"Log file {self.log_tail_file_name} was removed.")
        except Exception as e:
            log.warning(f"Failed to remove log tailing file: {e}")

        return True

    def _get_log_tail(self):
        """
        Get the log tailing file from the device.

        Logs a warning if the log tailing file cannot be retrieved.

        Returns:
            dump (str): The log tailing file.
        """
        try:
            file_size = Path(self.log_tail_file_name).stat().st_size / (1024 * 1024)

            if file_size > 5:
                zip_file_name = f"{self.log_tail_file_name}.zip"
                zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED).write(self.log_tail_file_name)
                self._remove_log_tail_file()
                return "ZIP", zip_file_name

            try:
                with open(self.log_tail_file_name, encoding="utf-8", errors="replace") as file:
                    dump = file.read()
            except Exception as e:
                log.warning(f"Failed to open/decode log tail file: {e}")

                try:
                    with open(self.log_tail_file_name, errors="replace") as file:
                        dump = file.read()
                except Exception as e:
                    log.warning(f"Failed to open/decode log tail file: {e}")

            # Remove dump file after reading it
            self._remove_log_tail_file()
            dump = f"{self.name} - {self.log_tail_file_name}\n{dump}"
        except Exception as e:
            log.warning(f"Unable to acquire log tailing file: {e}")

        return dump

    @staticmethod
    def _get_model_override_dir(override_file):
        """
        Return the path to the model override file.

        It will first check internal subdirectory. If the override file
        is not found it will also check the reference subdirectory.

        Args:
            override_file (str): Name of the model override file.

        Raises:
            RuntimeError: If model override file is not found.

        Returns:
            (str): Path to the model override file.
        """
        model_override_subdir = "shell/lib/override"
        model_override_paths = [
            Path(f"internal/{model_override_subdir}"),
            Path(f"./{model_override_subdir}"),
        ]

        for model_override_path in model_override_paths:
            if model_override_path.joinpath(override_file).is_file():
                break
        else:
            raise RuntimeError(
                f"Could not find model override file {override_file} in {model_override_subdir}."
                f"Please make sure it exists.",
            )

        return model_override_path.as_posix()

    def create_tr_tar(self, cfg):
        """
        Create tar file for transfer to the device.

        Args:
            cfg (dict): Configuration dictionary for the tar creation.

        Raises:
            RuntimeError: If the tar file for the transfer could not be
                created.
        """
        tr_path = cfg.get("tr_path")
        log.debug("Creating tar file for transfer.")
        real_path = self.fut_base_dir
        internal_shell_path = f"{self.fut_base_dir}/internal/shell"
        additional_files = [
            self.regulatory_shell_file,
        ]
        tar_cmd = cfg.get("tar_cmd", "tar -cf")

        if Path(internal_shell_path).is_dir():
            # Add internal/shell to additional_files for file transfer to device
            additional_files.append(internal_shell_path)

        additional_files = " ".join([f"{additional_path}" for additional_path in additional_files])

        if cfg.get("full", False):
            tar_cmd = f"{tar_cmd} {tr_path} {self.fut_base_dir}/shell/ {additional_files}"
        elif cfg.get("manager", False):
            tar_cmd = f'{tar_cmd} {tr_path} {self.fut_base_dir}/shell/tests/{cfg.get("manager")} {additional_files}'
        elif cfg.get("file", False) or cfg.get("folder", False):
            tmp_path_param = cfg.get("file", False) if cfg.get("file", False) else cfg.get("folder", False)
            real_path = (
                tmp_path_param if Path(tmp_path_param).is_absolute() else f"{self.fut_base_dir}/{tmp_path_param}"
            )
            tar_cmd = f"{tar_cmd} {tr_path} {real_path}/"
            if Path(real_path).name:
                temp_real_path = real_path.rstrip("/")
                real_path = os.path.dirname(temp_real_path) + "/"
        else:
            tar_cmd = (
                f"{tar_cmd} {tr_path} {real_path}/shell/lib {real_path}/shell/config {real_path}/shell/tools "
                f"{additional_files}"
            )

        tar_home_reg = str(Path(real_path).relative_to("/")).replace("/", "\\/")
        tar_to_reg = str(Path(cfg.get("to", self.fut_dir)).relative_to("/")).replace("/", "\\/")
        tar_cmd = tar_cmd + f" --transform 's/{tar_home_reg}/{tar_to_reg}/'"
        log.debug(f"Executing: {tar_cmd}")
        # Create tar file.
        tar_ec = os.system(tar_cmd)

        if tar_ec != 0:
            raise RuntimeError(
                f"Failed to create tar file for transfer - configuration: {cfg} tar_cmd: {tar_cmd} tar_ec: {tar_ec}",
            )

    def _get_shell_cfg(self):
        """
        Prepare dictionary containing shell environment variables.

        Dictionary keys are shell variables, dictionary values are
        values of variables.

        Raises:
            RuntimeError: If shell environment variables cannot be
                loaded.

        Returns:
            (dict): Dictionary of shell environment variables.
        """
        tmp_cfg = {}

        try:
            for key, value in self.device_config.items():
                if key.isupper():
                    tmp_cfg[key] = value

            tmp_cfg["FUT_TOPDIR"] = self.fut_dir
            tmp_cfg["DEFAULT_WAIT_TIME"] = self.test_script_timeout

            if "client" not in self.device_type:
                # For GW and LEAF devices
                tmp_cfg["PATH"] = self.capabilities.get_shell_path()
                if self.capabilities.get_management_iface():
                    tmp_cfg["MGMT_IFACE"] = self.capabilities.get_management_iface()
                tmp_cfg["OPENSYNC_ROOTDIR"] = self.capabilities.get_opensync_rootdir()
                tmp_cfg["OVSH"] = (
                    f"{self.capabilities.get_opensync_rootdir()}"
                    f"/tools/ovsh --quiet --timeout={self.test_script_timeout}000"
                )
                tmp_cfg["LOGREAD"] = self.capabilities.get_logread_command()
                model_override_file = self.device_config.get("MODEL_OVERRIDE_FILE")
                platform_override_file = self.device_config.get("PLATFORM_OVERRIDE_FILE")
                tmp_cfg["MODEL_OVERRIDE_FILE"] = (
                    Path(self.fut_dir)
                    .joinpath(self._get_model_override_dir(model_override_file), model_override_file)
                    .as_posix()
                )
                tmp_cfg["PLATFORM_OVERRIDE_FILE"] = (
                    Path(self.fut_dir)
                    .joinpath(self._get_model_override_dir(platform_override_file), platform_override_file)
                    .as_posix()
                )
                tmp_cfg["MGMT_IFACE_UP_TIMEOUT"] = 60
                tmp_cfg["MGMT_CONN_TIMEOUT"] = 2
                tmp_cfg["FUT_SKIP_L2"] = "true" if os.getenv("FUT_SKIP_L2") == "true" else "false"
            else:
                tmp_cfg["PATH"] = self.device_config.get("shell_path")

        except Exception as e:
            raise RuntimeError(f"Failed to load shell environment variables: {e}")

        return tmp_cfg

    def _create_fut_set_env(self):
        """
        Create file containing shell environment variables.

        Name of the file is hardcoded to 'fut_set_env.sh'.

        Returns:
            (str): Path to shell environment variable file.
        """
        shell_fut_env_path = f"{self.fut_base_dir}/fut_set_env.sh"
        shell_fut_env_file = open(shell_fut_env_path, "w")

        for key, value in self._get_shell_cfg().items():
            ini_line = f'{key}="{value}"\n'
            shell_fut_env_file.write(ini_line)

        shell_fut_env_file.write('echo "${FUT_TOPDIR}/fut_set_env.sh sourced"\n')
        shell_fut_env_file.close()

        return shell_fut_env_path

    def transfer(
        self,
        tr_name="fut_tr.tar",
        to=None,
        full=False,
        manager=False,
        file=False,
        folder=False,
        exec_perm=True,
        tr_path=None,
        **kwargs,
    ):
        """
        Transfer files to device.

        Method creates designated directory on the device, transfers
        fut tar file to the device, unpacks the contents into the
        designated directory, sets permissions, removes the file after
        unpack and updates shell paths.

        Raises:
            RuntimeError: If unpack of transferred tar file failed.
            RuntimeError: If the setting of permissions failed.
            RuntimeError: If the removal of the tar file failed.
            RuntimeError: If the update of shell paths failed.

        Returns:
            (bool): True, on success
        """
        cfg = locals().copy()
        cfg.update(kwargs)

        if not cfg.get("to"):
            cfg.update({"to": self.fut_dir})

        if not cfg.get("tr_path"):
            cfg.update({"tr_path": f"{self.fut_base_dir}/{tr_name}"})

        log.info(f"Initiated transfer to {self.name}")
        log.info(f"Transfer configuration: {cfg}")

        self.create_tr_tar(cfg)
        self.device_api.run_raw(f'mkdir -p {cfg.get("to")}')
        self.device_api.run_raw(f'chown {self.username} {cfg.get("to")}')
        log.debug(f'Transferring {cfg.get("tr_path")} to {cfg.get("to")} on {self.name}')
        self.device_api.put_file(file_name=cfg.get("tr_path"), location=cfg.get("to"))

        # Unpack tar file
        tr_name = cfg.get("tr_name")
        unpack_tar_cmd = f'tar -C / -xf {cfg.get("to")}/{tr_name}'
        log.debug(f"Unpacking {tr_name}: {unpack_tar_cmd}")
        unpack_res = self.device_api.run_raw(unpack_tar_cmd)
        unpack_ec, unpack_std, unpack_std_err = unpack_res[0], unpack_res[1], unpack_res[2]
        if unpack_ec != 0:
            raise RuntimeError(
                f"Unpack command failed!\n"
                f"cmd: {unpack_tar_cmd}\n"
                f"std_out:\n{unpack_std}\n"
                f"std_err:\n{unpack_std_err}\n"
                f"ec: {unpack_ec}",
            )

        if cfg.get("exec_perm"):
            # Make scripts executable
            set_permission_cmd = f'find {self.fut_dir} -type f -iname "*.sh" -exec chmod 755 {{}} \\;'
            log.debug(f"Setting permissions on {self.fut_dir}: {set_permission_cmd}")
            permission_ec = self.device_api.run_raw(set_permission_cmd)

            if permission_ec[0] != 0:
                raise RuntimeError(f"Permission command fail, set_permission_cmd: {set_permission_cmd}")

            # Remove tar file after unpack to free-up space
            rm_tar_cmd = f'rm {cfg.get("to")}/{tr_name}'
            log.debug(f"Removing {tr_name}: {rm_tar_cmd}")
            rm_ec = self.device_api.run_raw(rm_tar_cmd)

            if rm_ec[0] != 0:
                raise RuntimeError(f"Remove tar command fail, rm_tar_cmd: {rm_tar_cmd}")

            if self.fut_dir != "/tmp/fut-base":
                log.debug(f"Updating shell paths to match FUT_TOPDIR={self.fut_dir}")
                escaped_fut_dir = self.fut_dir.replace("/", "\\/")
                path_update_cmd = (
                    f"find {self.fut_dir} -type f -exec sed -i 's/\\/tmp\\/fut-base/{escaped_fut_dir}/g' {{}} + "
                )
                path_update_res = self.device_api.run_raw(path_update_cmd)

                if path_update_res[0] != 0:
                    raise RuntimeError(
                        f"Failed to update shell paths\n"
                        f"{path_update_cmd}\n"
                        f"{path_update_res[2]}\n"
                        f"Please use FUT_TOPDIR=/tmp/fut-base\n",
                    )

        log.debug(f"Transfer to {self.name} finished successfully.")

        return True

    def create_and_transfer_fut_set_env(self):
        """
        Create fut_set_env file and transfers it to the device.

        Returns:
            (bool): True if transfer was successful.
        """
        fut_set_env_path = self._create_fut_set_env()

        return self.transfer(file=fut_set_env_path, to=f"{self.fut_dir}/")

    def _version(self):
        """
        Return the version of the device.

        Returns:
            version (str): Device version.
        """
        version = self.device_api.version()

        if self.model == "rpi":
            version = version.split()[0].split("__")[1]

        log.debug(f"{self.name.upper} version: {version}")

        return version

    def check_fut_file_transfer(self):
        """
        Check if FUT files were transferred to the device.

        Returns:
            (bool): True if files were transferred.
        """
        fut_file_check = self.device_api.run_raw(f"ls -la {self.fut_dir}/shell/lib")

        if fut_file_check[0] != 0:
            log.info(f"{self.fut_dir} missing on {self.name.upper()}")
            self.transfer(full=True)
            self.create_and_transfer_fut_set_env()
        else:
            return True

    def _check_mgmt_ssh_connection_down(self):
        """
        Check if management SSH connection to the device is down.

        The check is executed by executing a simple 'ls' command. Each
        exit code not equal to 0 is considered as lost connection. SSH
        connection to the device is required for executing the commands
        and must be re-established if broken.

        Returns:
            (bool): True if SSH connection to the device is lost, False otherwise.
        """
        try:
            res = self.device_api.run_raw("ls /", timeout=5)[0]
            log.debug(f"Exit code of the SSH connection check: {res}")
            # Each exit_code != 0 is treated as SSH disconnection.
            return res != 0
        except Exception as e:
            log.debug(f"An exception was encountered: {e}")
            # Each exception is treated as SSH disconnection.
            return True

    def _start_rcn_procedure(self):
        """
        Start reconnection procedure to the device.

        Method tries to reconnect 'ssh_rcn_max_attempts' number of
        times. Between each unsuccessful attempt pauses and retries if
        not already tried 'ssh_rcn_max_attempts' times.

        Raises:
            ConnectionError: If device could not reconnect.

        Returns:
            (bool): True if reconnection is successful.
        """
        log.warning("Lost SSH connection")
        log.debug("Starting SSH reconnection procedure")
        self.rcn_active = True

        while self.rcn_active:
            if self.rcn_attempt > self.ssh_rcn_max_attempts:
                self.rcn_attempt = 0
                self.rcn_active = False
                raise ConnectionError("Lost connection to device.")
            log.debug(f"Waiting {self.rcn_sleep_time}s before next reconnection attempt.")
            time.sleep(self.rcn_sleep_time)
            if self._check_mgmt_ssh_connection_down():
                log.warning(f"Could not establish SSH connection - attempt {self.rcn_attempt}.")
                self.rcn_attempt += 1
            else:
                log.debug(f"SSH connection re-established - attempt {self.rcn_attempt}.")
                log.info("SSH connection re-established.")
                self.rcn_attempt = 0
                self.rcn_active = False
                break

        return True

    @allure_script_execution_post_processing
    def execute(self, path, args="", as_sudo=False, **kwargs):
        """
        Execute the specified script with optional arguments.

        Args:
            path (str): Path to script.
            args (str): Optional script arguments. Defaults to empty
                string.
            as_sudo (bool): Execute script with superuser privileges.

        Keyword Args:
            suffix (str): Suffix of the script.
            folder (str): Name of the folder where the script is
                located.
            skip_rcn (bool): If set to True, the reconnection
                procedure will be skipped.

        Returns:
            list: List comprised of the exit code, standard output and
                standard error.
        """
        skip_rcn = False if "skip_rcn" not in kwargs else kwargs["skip_rcn"]

        if isinstance(args, list):
            args = " ".join(args)

        cmd = self.get_remote_test_command(path, args)

        if as_sudo:
            cmd = f"sudo {cmd}"

        timeout = self.test_script_timeout * 2 if "timeout" not in kwargs else kwargs["timeout"]

        cmd_res = self.device_api.run_raw(cmd, timeout=timeout, combine_std=False, **kwargs)
        if cmd_res[0] == 255 and skip_rcn is False:
            if self._check_mgmt_ssh_connection_down():
                log.info(
                    "Encountered an issue related to the SSH connection. Attempting the reconnection procedure.",
                )
                self._start_rcn_procedure()
                self.check_fut_file_transfer()
                cmd_res = self.device_api.run_raw(cmd, timeout=timeout, combine_std=False, **kwargs)
        elif cmd_res[0] == 127 or "command not found" in cmd_res[2] or "No such file or directory" in cmd_res[2]:
            log.info(f"Checking FUT files: {cmd_res[2]}")
            self.check_fut_file_transfer()
            cmd_res = self.device_api.run_raw(cmd, timeout=timeout, combine_std=False, **kwargs)

        cmd_ec = cmd_res[0]
        cmd_std_out = "" if not cmd_res[1] else cmd_res[1]
        cmd_std_err = "" if not cmd_res[2] else cmd_res[2]

        return cmd_ec, cmd_std_out, cmd_std_err

    def execute_with_logging(self, path, args="", as_sudo=False, **kwargs):
        """
        Wrap the execute_script method.

        Enables the creation of a log tailing file

        Args:
            path (str): Path to script.
            args (str): Optional script arguments. Defaults to empty
                string.
            as_sudo (bool): Execute script with superuser privileges.

        Keyword Args:
            suffix (str): Suffix of the script.
            folder (str): Name of the folder where the script is located.
            skip_rcn (bool): If set to True, the reconnection procedure
                will be skipped.

        Returns:
            list: List comprised of the exit code, standard output and
                standard error if the raw argument is set to True.
        """
        self._start_log_tail()
        cmd_res = self.execute(path, args, as_sudo=as_sudo, **kwargs)
        self._stop_log_tail()

        if cmd_res[0] != 0:
            log_tail = self._get_log_tail()
            allure_attach_log_file(file=log_tail, file_name=f"logtail_{self.name}")

        return cmd_res

    def check_wan_connectivity(self):
        """
        Perform a WAN connectivity check on the device.

        Returns:
            (bool): True if the WAN connectivity check was executed
                successfully, False otherwise.
        """
        return self.execute("tools/device/check_wan_connectivity")[0] == 0
