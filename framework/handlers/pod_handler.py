import time
from functools import cached_property
from os import PathLike
from pathlib import Path
from typing import Literal

import allure

from config.defaults import all_radio_bands
from framework.lib.fut_lib import (
    _find_target_path_in_root_dir,
    allure_script_execution_post_processing,
    get_command_arguments,
    get_str_hash,
)
from lib_testbed.generic.pod.generic.pod_api import PodApi
from lib_testbed.generic.pod.pod import PodResolver
from lib_testbed.generic.rpower.rpower_tool import PowerControllerTool
from lib_testbed.generic.util.common import compare_fw_versions
from lib_testbed.generic.util.logger import log


class PodHandler(PodApi):
    def __new__(cls, **kwargs):
        # Resolve the concrete API implementation class for the device
        pod_api_class = PodResolver().resolve_pod_api_class(kwargs["dev"])

        # Create a dynamic subclass combining the API implementation with PodHandler
        class DynamicPodHandler(PodHandler, pod_api_class):
            pass

        # Create, initialize and return the instance
        instance = object.__new__(DynamicPodHandler)
        instance.__init__(**kwargs)
        return instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.FUT_BASE_DIR = Path(__file__).absolute().parents[2].as_posix()
        self.FUT_DIR = "/tmp/fut-base"
        self.TEST_SCRIPT_TIMEOUT = 180
        self.location_config = kwargs.get("config")
        self.ovsdb = self.lib.ovsdb
        self.interface: dict = {}
        self.transfer_folders = ["shell"]
        self.transfers = list(zip(self.transfer_folders, self.transfer_folders))
        # Call override_if_names() if it exists
        if hasattr(self, "override_version_specific_ifnames"):
            self.override_version_specific_ifnames()
        # Determine MLO capabilities:
        self.mlo_fh = "MLO_FH" in self.supported_features
        self.mlo_bh = "MLO_BH" in self.supported_features

    @cached_property
    def base_ssid(self) -> str:
        ssid = f"FUT_ssid_{self.location_config['user_name']}"
        base_ssid = get_str_hash(input_string=ssid, hash_length=16)
        return base_ssid

    @cached_property
    def base_psk(self) -> str:
        psk = f"FUT_psk_{self.location_config['user_name']}"
        base_psk = get_str_hash(input_string=psk, hash_length=32)
        return base_psk

    @cached_property
    def opensync(self) -> str:
        """
        Check the device AWLAN_Node table for the OPENSYNC field value.

        Returns:
            opensync_version (str): The OpenSync version on the device. Format: x.y.z.w or empty string.
        """
        opensync_version = self.opensync_version()
        log.info(f"{self.nickname.upper()} OPENSYNC version: {opensync_version}.")
        return opensync_version

    @cached_property
    def wireless_manager(self) -> str:
        """
        Determines the wireless manager name for the device and caches the result.

        Returns:
            str: The name of the wireless manager.

        Raises:
            RuntimeError: If the wireless manager cannot be determined.
        """
        wireless_manager_name = self.execute("tools/device/get_wireless_manager_name")

        if wireless_manager_name[0] == 0:
            wireless_manager_name = wireless_manager_name[1].split("\n")[-1]
            log.info(f"{self.nickname.upper()}: wireless manager -> {wireless_manager_name}.")
        else:
            raise RuntimeError(
                f"{self.nickname.upper()}: unable to determine wireless manager -> {wireless_manager_name[2]}",
            )

        return wireless_manager_name

    @cached_property
    def supported_wireless_managers(self) -> list:
        return ["wm", "owm"]

    @cached_property
    def bridge_type(self) -> str:
        """
        Determines the type of bridge the device uses based on OVSDB information.

        Returns:
            str: The type of bridge, either "native_bridge" or "ovs_bridge".
        """
        ovs_version = self.ovsdb.get(
            table="AWLAN_Node",
            select="ovs_version",
            skip_exception=True,
        )
        # The device is using Native bridge if the 'ovs_version' is not available
        bridge_type = "native_bridge" if "N/A" in ovs_version else "ovs_bridge"
        log.info(f"{self.nickname.upper()}: {bridge_type} bridge type.")
        return bridge_type

    @cached_property
    def kconfig(self) -> list[str]:
        """
        Fetches and parses the kconfig file into a list of strings representing its content.

        Returns:
            list[str]: A list of non-comment lines from the `kconfig` file, with surrounding whitespace
            removed.
        """
        kconfig_local_path = self.get_file(
            Path(self.capabilities.get_opensync_rootdir()).joinpath("etc", "kconfig"),
            self.FUT_BASE_DIR,
            create_dir=False,
        )

        with open(kconfig_local_path) as kconfig:
            kconfig_content = kconfig.readlines()

        kconfig = [line.strip() for line in kconfig_content if "#" not in line]
        return kconfig

    @cached_property
    def kconfig_managers(self) -> list:
        """
        Get the managers from the content of the kconfig file on the device. Values are cached.

        Returns:
            (list): Managers in the kconfig file on the device.
        """
        kconfig_managers = [
            line.removesuffix("=y").removeprefix("CONFIG_MANAGER_")
            for line in self.kconfig
            if line.endswith("=y") and line.startswith("CONFIG_MANAGER_")
        ]
        kconfig_managers = sorted({manager for manager in kconfig_managers if "_" not in manager})
        return kconfig_managers

    @cached_property
    def node_service_status(self):
        """
        Return Node_Services fields service and status for all services.

        Cached values are replaced if a specific service is provided.

        Returns:
            (dict): Service values are keys, and the value is a dict with status values from the device.
        """
        node_services_ovsdb = self.ovsdb.get_json_table(
            table="Node_Services",
            select=["service", "status"],
        )

        if not isinstance(node_services_ovsdb, list):
            node_services_ovsdb = [node_services_ovsdb]

        node_services = {item["service"]: {"status": item["status"]} for item in node_services_ovsdb}

        return node_services

    @property
    def dm_manager_pid(self):
        manager_pids = self.get_managers_list()
        return {"dm": manager_pids["dm"]} if "dm" in manager_pids else {}

    @cached_property
    def env_file(self) -> dict:
        """
        Prepare dictionary containing shell environment variables.

        Dictionary keys are shell variable names and dictionary values are shell variable values. Variables:

        * FUT_TOPDIR
        * MODEL_OVERRIDE_FILE
        * OPENSYNC_ROOTDIR
        * OVSH
        * PLATFORM_OVERRIDE_FILE

        Returns:
            (dict): Dictionary of shell environment variables.
        """
        ovsh = (
            f"{self.capabilities.get_opensync_rootdir()}" f"/tools/ovsh --quiet --timeout={self.TEST_SCRIPT_TIMEOUT}000"
        )
        shell_cfg = {
            "FUT_TOPDIR": self.FUT_DIR,
            "OPENSYNC_ROOTDIR": self.capabilities.get_opensync_rootdir(),
            "OVSH": ovsh,
        }

        converted_model = self.lib.device.config.get("model")  # Uses DeviceCommon.convert_model_name(model)
        model_override_file = f"{converted_model}_lib_override.sh"
        model_override_file_path = self._get_model_override_filepath(model_override_file)
        if model_override_file_path:
            shell_cfg["MODEL_OVERRIDE_FILE"] = model_override_file_path

        platform_override_file = f"{self.capabilities.get_wifi_vendor().lower()}_platform_override.sh"
        platform_override_file_path = self._get_model_override_filepath(platform_override_file)
        if platform_override_file_path:
            shell_cfg["PLATFORM_OVERRIDE_FILE"] = platform_override_file_path

        return shell_cfg

    @cached_property
    def rpower(self) -> PowerControllerTool:
        return PowerControllerTool(self.location_config, self.nickname)

    @cached_property
    def reboot_time(self) -> int:
        """
        Get the time after which the device should be online and accessible via ssh after reboot. Values are cached.

        It fetches the boot time KPI value from the model properties config file and the global minimum reboot time and returns the max value.

        Returns:
            (int): Time for the device to become available via ssh after reboot, in seconds.
        """
        from config.defaults import min_reboot_time

        boot_time_kpi = self.capabilities.get_boot_time_kpi()

        return max(boot_time_kpi, min_reboot_time)

    @cached_property
    def supported_features(self) -> list[str]:
        """
        Check which features are supported by the current firmware version.

        This method evaluates device capabilities against the current OpenSync firmware version
        to determine which features are available. Features are filtered based on minimum
        firmware requirements and EOS versions.

        Returns:
            list[str]: List of feature names that are supported by the current firmware.
        """
        supported_features = []
        current_fw_version = self.opensync

        for feature, feature_support_info in self.capabilities.device_capabilities["features"].items():
            # If feature_support_info is empty dict, treat as supported
            if not feature_support_info:
                supported_features.append(feature)
                continue

            # Skip if no minimum firmware version specified
            min_fw = feature_support_info.get("min_fw")
            if not min_fw:
                continue

            min_fw_version = min_fw

            # Check if current firmware meets minimum requirement
            if compare_fw_versions(current_fw_version, min_fw_version, condition="<"):
                continue

            # Check if feature has been deprecated
            eos_fw = feature_support_info.get("eos_fw")
            if eos_fw and compare_fw_versions(current_fw_version, eos_fw, condition=">"):
                continue

            supported_features.append(feature)

        log.info(f"{self.nickname.upper()}: Supported features -> {supported_features}")

        return supported_features

    def _get_model_override_filepath(self, override_file: str) -> str:
        """
        Return the path to the model override file.

        It will first check internal subdirectory. If the override file
        is not found it will also check the reference subdirectory.

        Args:
            override_file (str): Name of the model override file.

        Raises:
            FileNotFoundError: If model override file is not found.

        Returns:
            (str): Path to the model override file.
        """
        override_subdir = "lib/override"
        override_path = _find_target_path_in_root_dir(
            Path(override_subdir).joinpath(override_file),
            self.transfer_folders,
        )
        override_filepath = ""
        if len(override_path) == 1:
            tmp_path = override_path[0]
            # Normalize based on transfer location
            for directory, location in self.transfers:
                if Path(tmp_path).is_relative_to(directory):
                    override_filepath = (
                        Path(self.FUT_DIR).joinpath(location, Path(tmp_path).relative_to(directory)).as_posix()
                    )
                    break
        elif len(override_path) > 1:
            raise FileNotFoundError(f"Found several override files: '{override_path}', ensure only one exists.")

        return override_filepath

    def _get_log_tail_command(self) -> str:
        """
        Get the command for tailing the system log on the device. Stores this information as an object attribute.

        Logs a warning if command can not be retrieved, but does not raise an exception.

        Requires 'tail' command with '-F' option on the device: print data as file grows, but keep retrying on filename.

        Requires a valid logread command on device, specified by the model properties file:
            - 'logread'
            - 'cat /path/to/system/logfile'

        Returns:
            (str): The command for tailing the system log on the device.
        """
        if hasattr(self, "log_tail_command") and self.log_tail_command:
            return self.log_tail_command

        logread_command = self.capabilities.get_logread_command()

        if Path(logread_command).name == "logread":
            self.log_tail_command = f"{logread_command} -f"
        elif logread_command.startswith("cat"):
            self.log_tail_command = f"tail -F {logread_command.removeprefix('cat ')}"
        else:
            raise RuntimeError(f"Invalid logread command {logread_command}, could not determine 'log_tail_command'.")

        log.debug(f"{self.nickname.upper()}: log_tail_command on device is {self.log_tail_command}")

        return self.log_tail_command

    def _get_log_tail_file_name(self) -> str:
        """
        Get the file name for tailing the system log on the device. Stores this information as an object attribute.

        Returns:
            (str): The command for tailing the system log on the device.
        """
        if hasattr(self, "log_tail_file_name") and self.log_tail_file_name:
            return self.log_tail_file_name

        self.log_tail_file_name = f'{self.FUT_DIR}/{self.nickname}_{time.strftime("%Y%m%d-%H%M%S")}.log'
        log.debug(f"log_tail_file_name on device is: {self.log_tail_file_name}")

        return self.log_tail_file_name

    def _start_log_tail(self) -> None:
        """
        Start tailing system logs on the device.

        This method will create a log file and start a logging subprocess on the device in the background.
        If the log tailing processes is not executed correctly, it will only log a warning and not an exception.
        """
        log_tail_file_name = self._get_log_tail_file_name()
        log_tail_command = self._get_log_tail_command()
        # Required timeout of at least 70 seconds due to hardcoded channel set timeout of 60s
        log_tail_timeout = 70 if self.TEST_SCRIPT_TIMEOUT <= 70 else self.TEST_SCRIPT_TIMEOUT
        log_tail_start_cmd = f"timeout {log_tail_timeout} {log_tail_command} > {log_tail_file_name} &"
        log.debug(f"{self.nickname.upper()} log tail start command: '{log_tail_start_cmd}'")
        cmd_res = self.run_raw(log_tail_start_cmd, timeout=5, skip_logging=True)

        if cmd_res[0] != 0:
            log.warning(f"Encountered issue while starting log tailing process: {cmd_res[2]}")

    def _stop_log_tail(self) -> None:
        """
        Stop all log tailing processes on the device.

        If the log tailing processes are not stopped correctly, it will only log a warning.
        """
        cmd_res = self.run_raw(f"pkill {self._get_log_tail_command().split()[0]}", timeout=5, skip_logging=True)

        if cmd_res[0] != 0:
            log.warning(f"{self.nickname.upper()}: Encountered issue while stopping log tailing process {cmd_res[2]}")

    def _get_log_tail_file_and_attach_to_allure(self, log_tail_file_name: PathLike[str] | None = None) -> None:
        """
        Get the log tailing file from the device and attach it to the allure report.

        Logs a warning if the action cannot be performed.
        """
        log_tail_local_path = None

        if not log_tail_file_name:
            log_tail_file_name = self.log_tail_file_name
        try:
            # Get the file locally
            log_tail_local_path = self.get_file(log_tail_file_name, self.FUT_BASE_DIR, create_dir=False)
            allure.attach.file(log_tail_local_path, name=Path(log_tail_file_name).name)
        finally:
            # Remove file locally
            if log_tail_local_path:
                Path(log_tail_local_path).unlink(missing_ok=True)

    def _remove_log_tail_file_remotely(self) -> None:
        """
        Remove the log tailing file from the remote device.

        Logs a warning if the log tailing file cannot be removed.
        """
        log_tail_file_name = self._get_log_tail_file_name()
        log_tail_remove_cmd = f"[ -e {log_tail_file_name} ] && rm {log_tail_file_name}"

        try:
            cmd_res = self.run_raw(log_tail_remove_cmd, timeout=5)
            if cmd_res[0] != 0:
                log.warning(f"{self.nickname.upper()}: Encountered issue while removing log file remotely {cmd_res[2]}")
        finally:
            if hasattr(self, "log_tail_file_name"):
                delattr(self, "log_tail_file_name")

    def check_fut_files(self, force_transfer: bool = False) -> None:
        """
        Check if FUT files were transferred to the device.

        Args:
            force_transfer (bool): If set to True, the files will be transferred even if they are present. Defaults to False.

        If the files are not present, they are transferred.
        """
        transfers = self.transfers
        fut_file_check = self.run_raw(f"ls -la {self.FUT_DIR}/shell/lib")

        if fut_file_check[0] != 0 or force_transfer:
            log.info(f"{self.nickname.upper()}: FUT files not found on device, transferring {transfers}.")
            for directory, location in transfers:
                self.put_dir(
                    directory=f"{self.FUT_BASE_DIR}/{directory}/",
                    location=f"{self.FUT_DIR}/{location}/",
                    as_sudo=False,
                )

            log.info(f"{self.nickname.upper()}: transferring fut_set_env.sh")
            self.create_and_transfer_fut_env_file()
        else:
            log.info(f"{self.nickname.upper()}: FUT files found on device.")
            log.info(fut_file_check[1])

    def configure_device_mode(self, device_mode: str) -> None:
        """
        Configure device in either router or bridge mode.

        Besides the device mode, which is provided as an argument,
        some other parameters are fetched in the function itself
        (device capabilities) or are hardcoded, e.g.: DHCP server
        configuration.
        Args:
            device_mode (str): Mode to put the device into.
        Raises:
            RuntimeError: If invalid device mode is provided.
        Returns:
            (bool): True if device is configured.
        """
        if_lan_br_name = self.capabilities.get_lan_bridge_ifname()
        eth_wan_interface = self.capabilities.get_primary_wan_iface()

        # Fixed arguments
        internal_dhcpd = (
            '\'["map",['
            '["dhcp_option","3,192.168.40.1;6,192.168.40.1"],'
            '["force","false"],["lease_time","12h"],'
            '["start","192.168.40.2"],'
            '["stop","192.168.40.254"]'
            "]]'"
        )
        internal_inet_addr = "192.168.40.1"

        # Build configuration scripts arguments
        set_router_mode_args = get_command_arguments(
            if_lan_br_name,
            internal_dhcpd,
            internal_inet_addr,
            eth_wan_interface,
        )
        set_bridge_mode_args = get_command_arguments(
            if_lan_br_name,
            eth_wan_interface,
        )

        # Put the device into router or bridge mode.
        if device_mode == "router":
            assert self.execute("tools/device/set_router_mode", set_router_mode_args)[0] == 0
        elif device_mode == "bridge":
            assert self.execute("tools/device/set_bridge_mode", set_bridge_mode_args)[0] == 0
        else:
            raise RuntimeError(
                f"{self.nickname.upper()}: Invalid device mode provided: {device_mode}. Supported: 'router', 'bridge'.",
            )

    def create_fut_set_env(self) -> str:
        """
        Create file containing shell environment variables.

        Name of the file is hardcoded to 'fut_set_env.sh'.

        Returns:
            (str): Path to shell environment variable file.
        """
        shell_fut_env_path = f"{self.FUT_BASE_DIR}/fut_set_env.sh"
        shell_fut_env_file = open(shell_fut_env_path, "w")

        for key, value in self.env_file.items():
            ini_line = f'{key}="{value}"\n'
            shell_fut_env_file.write(ini_line)

        shell_fut_env_file.write('echo "${FUT_TOPDIR}/fut_set_env.sh sourced"\n')
        shell_fut_env_file.close()

        return shell_fut_env_path

    def device_test_setup(self, test_suite_name: str, setup_args: str = "", **kwargs) -> None:
        """
        Perform the necessary device setup for FUT test case execution.

        Args:
            test_suite_name (str): Name of the test suite to be executed.
            setup_args (str): Additional setup arguments to be passed to
                the setup script.
        Returns:
            (bool): True if setup is successful.
        """
        assert self.execute(f"tests/{test_suite_name}/{test_suite_name}_setup", setup_args, **kwargs)[0] == 0

        if self.nickname.lower() == "gw":
            self.configure_device_mode(device_mode="router")

    def get_remote_test_command(
        self,
        test_path: str,
        params: str = "",
        suffix: str = ".sh",
        folder: str = "shell",
    ) -> str:
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
        remote_command = f"{self.FUT_DIR}/{folder}/{test_path}{suffix}".replace("///", "/").replace("//", "/")
        # Append command parameters
        remote_command = f"{remote_command} {params}"

        return remote_command

    def get_log_tail_file_and_attach_to_allure(self, log_tail_file_name: PathLike[str] | None = None) -> None:
        """
        Get the log tailing file from the device and attach it to the allure report.

        Logs a warning if the action can not be performed.
        """
        if not log_tail_file_name:
            log_tail_file_name = self._get_log_tail_file_name()
        try:
            # Get file locally
            log_tail_local_path = self.get_file(log_tail_file_name, self.FUT_BASE_DIR, create_dir=False)
            allure.attach.file(log_tail_local_path, name=Path(log_tail_file_name).name)
        finally:
            # Remove file locally
            Path(log_tail_local_path).unlink(missing_ok=True)

    @allure_script_execution_post_processing
    def execute(self, path: str, args: str = "", as_sudo: bool = False, **kwargs) -> tuple[int, str, str]:
        """
        Execute the specified script with optional arguments.

        Args:
            path (str): Path to script.
            args (str): Optional script arguments. Defaults to empty string.
            as_sudo (bool): Execute script with superuser privileges.
        Keyword Args:
            suffix (str): Suffix of the script.
            folder (str): Name of the folder where the script is located.
            retry (bool): If set to False, the reconnection procedure will be skipped.
            skip_logging (bool): If set to True, the logging procedure will be skipped.
            background_execution (bool): If set to True, the script will be executed in
                the background.
        Returns:
            (tuple): Exit code (int), standard output (str) and standard error (str) of the executed command.
        """
        skip_logging = kwargs.pop("skip_logging", False)
        background_execution = kwargs.pop("background_execution", False)
        retry = kwargs.pop("retry", True)

        if isinstance(args, list):
            args = " ".join(args)

        if background_execution:
            args += " &"

        cmd = self.get_remote_test_command(test_path=path, params=args, **kwargs)

        if as_sudo:
            cmd = f"sudo {cmd}"

        timeout = self.TEST_SCRIPT_TIMEOUT * 2 if "timeout" not in kwargs else kwargs["timeout"]
        cmd_res = self.run_raw(cmd, timeout=timeout, skip_logging=skip_logging, **kwargs)

        # Error handling
        if retry and (
            cmd_res[0] in [127, 255] or "command not found" in cmd_res[2] or "No such file or directory" in cmd_res[2]
        ):
            self.wait_available(timeout=self.reboot_time)
            self.check_fut_files()
            cmd_res = self.run_raw(cmd, timeout=timeout, skip_logging=skip_logging, **kwargs)

        cmd_ec = cmd_res[0]
        cmd_std_out = "" if not cmd_res[1] else cmd_res[1]
        cmd_std_err = "" if not cmd_res[2] else cmd_res[2]

        return cmd_ec, cmd_std_out, cmd_std_err

    def execute_with_logging(self, path: str, args: str = "", as_sudo: bool = False, **kwargs) -> tuple[int, str, str]:
        """
        Wrap the execute method and create a log file section for the duration of the execution.

        Args:
            path (str): Path to script.
            args (str): Optional script arguments. Defaults to empty string.
            as_sudo (bool): Execute script with superuser privileges.

        Keyword Args:
            suffix (str): Suffix of the script.
            folder (str): Name of the folder where the script is located.
            skip_rcn (bool): If set to True, the reconnection procedure will be skipped.
            attach_on_pass (bool): If set to True, attach log file even on command success. Defaults to False.

        Returns:
            (tuple): Exit code (int), standard output (str) and standard error (str) of the executed command.
        """
        attach_on_pass = kwargs.get("attach_on_pass", False)
        try:
            self._start_log_tail()
            cmd_res = self.execute(path, args, as_sudo=as_sudo, **kwargs)
            self._stop_log_tail()
            if cmd_res[0] != 0 or attach_on_pass:
                self._get_log_tail_file_and_attach_to_allure()
            pass
        finally:
            self._remove_log_tail_file_remotely()
        return cmd_res

    def create_and_transfer_fut_env_file(self):
        env_file = self.create_fut_set_env()
        self.put_file(file_name=env_file, location=self.FUT_DIR)

    def get_radio_band_from_remote_channel_and_band(self, channel: int, remote_radio_band: str) -> str:
        """
        Return the radio_band.

        Returns the band of one device based on the provided channel and
        radio_band of another device. This is useful if we have band
        information for the gateway device, but would like to extract
        the radio band of the leaf device.

        Example: what is the band of the local device, given the channel and
            band info of the remote device?
            Remote device: channel = 157, remote_radio_band = 5gu (tri band device)
            Local device: channel = 157, radio_band = 5g (dual-band device)
        Same example with different band: we cannot infer band from channel,
            due to 6g overlapping channels
            Remote device: channel = 1, remote_radio_band = 6g
            Local device: channel = 1, radio_band = 6g

        Args:
            channel (int): Wi-Fi channel for both devices.
            remote_radio_band (str): Radio band of the "remote" device.
                Supported options: "24g", "5g", "5gl", "5gu", "6g".

        Raises:
            RuntimeError: If the radio band could not be determined.

        Returns:
            band (str): Radio band of "local" device.
        """
        orig_radio_channels = {}

        for radio_band in all_radio_bands:
            orig_radio_channels.update({radio_band: self.capabilities.get_supported_radio_channels(radio_band)})

        radio_channels = {k: v for k, v in orig_radio_channels.items() if v is not None}

        for band in radio_channels:
            channels = radio_channels[band]
            channel_in_band = str(channel) in channels or channel in channels
            matching_bands = band[:2] in remote_radio_band[:2]

            if channel_in_band and matching_bands:
                return band

        raise RuntimeError(
            f"{self.nickname.upper()}: could not determine radio band for channel={channel} and remote_radio_band={remote_radio_band}",
        )

    def vif_reset(self) -> None:
        """Reset all virtual interfaces on the device and remove all ports from home bridge.

        Raises:
            AssertionError: If the command to reset the VIFs fails.
        """
        assert self.execute("tools/device/vif_reset")[0] == 0
        lan_bridge = self.capabilities.get_lan_bridge_ifname()
        assert self.execute("tools/device/remove_all_ports_from_bridge", lan_bridge)[0] == 0

    def check_wan_connectivity(self) -> bool:
        """
        Perform a WAN connectivity check on the device.

        Returns:
            (bool): True if the WAN connectivity check was executed
                successfully, False otherwise.
        """
        return self.execute("tools/device/check_wan_connectivity")[0] == 0

    def get_if_mac(self, if_name: str, if_role: str = None, use_mld_mac: bool = True) -> str:
        """
        Get the MAC address of a physical radio or virtual interface.

        This method retrieves the MAC address based on the interface type and
        device capabilities. It handles physical radio interfaces, virtual interfaces,
        and MLDs for both fronthaul and backhaul interfaces.

        Args:
            if_name (str): The name of the interface to get the MAC address for.
                Examples:
                - Physical radio: 'wifi0', 'wifi1', 'wifi2'
                - Virtual interfaces: 'bhaul-sta-24', 'home-ap-50'
            if_role (str, optional): The role of the interface. Required for non-physical
                interfaces. Supported values include:
                - backhaul_ap
                - backhaul_sta
                - home_ap
                - onboard_ap
                - aux_1_ap
                - aux_2_ap
                - fhaul_ap
                - cportal_ap
                - haahs_ap
                Defaults to None.
            use_mld_mac (bool, optional): Whether to return the MLD MAC address for
                MLO-enabled interfaces. If False, returns the regular VIF MAC address
                instead. Only applicable for MLO-capable interfaces.
                Defaults to True.

        Returns:
            str: The MAC address of the specified interface in standard format
                (e.g., "aa:bb:cc:dd:ee:ff"). For MLO-enabled interfaces with
                use_mld_mac=True, returns the MLD address.

        Raises:
            ValueError: If if_role is None for non-physical interfaces.

        Note:
            This method requires the interface to be already configured and enabled.
        """
        # Check if this is a physical radio interface
        phy_radio_ifnames = self.capabilities.get_phy_radio_ifnames()
        if if_name in phy_radio_ifnames:
            if_mac = self.iface.get_physical_wifi_mac(if_name)
            log.info(f"Retrieved physical radio MAC address for {if_name}: {if_mac}")
            return if_mac

        if if_role is None:
            raise ValueError("Interface role is required for non-physical interfaces")

        is_mlo_backhaul = if_role in {"backhaul_sta", "backhaul_ap"} and self.mlo_bh

        # backhaul APs are configured into a MLO group even if only MLO_FH is supported
        is_mlo_fronthaul = if_role in {"backhaul_ap", "home_ap", "onboard_ap", "fhaul_ap"} and self.mlo_fh

        if (is_mlo_backhaul or is_mlo_fronthaul) and use_mld_mac:
            if_mac = self.ovsdb.get(
                table="Wifi_VIF_State",
                select="mld_addr",
                where=f"if_name=={if_name}",
            ).strip()
            log.info(f"Retrieved MLD MAC address for {if_name}: {if_mac}")
            return if_mac

        mac_list = self.iface.get_vif_mac(if_name)
        assert mac_list, f"Can not get {if_name} MAC on {self.nickname.upper()}"
        if_mac = mac_list[0]
        log.info(f"Retrieved VIF MAC address for {if_name}: {if_mac}")
        return if_mac

    def create_and_configure_backhaul(
        self,
        channel: int,
        leaf_device: "PodHandler",
        radio_band: str,
        ht_mode: str,
        encryption: str,
        mesh_type: str | None = "gre",
        second_leaf_device: "PodHandler" = None,
        topology: str | None = None,
        vif_reset: bool = False,
        **kwargs,
    ) -> Literal[True]:
        """
        Create and configure a backhaul connection.

        Args:
            channel (int): Radio channel.
            leaf_device (object): LEAF device object.
            radio_band (str): Radio band.
            ht_mode (str): HT mode.
            encryption (str): Encryption type.
            mesh_type (bool | None): Mesh type. Defaults to 'gre'.
                Supported options: 'gre', 'wds' or None
            second_leaf_device (object | None): Second leaf device object.
                Optional. Defaults to None.
            topology (str | None): Topology. Supported options: 'star', 'line'.
                Optional. Defaults to None.
            vif_reset (bool): Reset all VIF interfaces on both devices.
                Default is False.

        Returns:
            (bool): True if backhaul connection is configured correctly.

        Raises:
            ValueError: If arguments for the second leaf device are invalid.
            ValueError: The mesh_type is not either "gre" or "wds".
            ValueError: The topology is not either 'star', 'line' or None.
        """
        # Verify that either all or none args pertaining to a multi-leaf backhaul are set
        if (second_leaf_device is None) != (topology is None):
            raise ValueError(
                "When configuring a multi-leaf backhaul, both 'second_leaf_device' and 'topology' must be provided.",
            )

        # Verify mesh type
        if mesh_type not in ["gre", "wds", None]:
            raise ValueError("Invalid mesh type provided. Supported options: 'gre', 'wds' or None")

        if second_leaf_device:
            # Verify topology
            if topology not in ["star", "line"]:
                raise ValueError("Invalid topology provided. Supported options: 'star', 'line'")

            assert self._configure_dual_leaf_backhaul(
                channel=channel,
                leaf_device=leaf_device,
                second_leaf_device=second_leaf_device,
                topology=topology,
                radio_band=radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=mesh_type,
                vif_reset=vif_reset,
                **kwargs,
            )
        else:
            assert self._configure_single_leaf_backhaul(
                channel=channel,
                leaf_device=leaf_device,
                radio_band=radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=mesh_type,
                vif_reset=vif_reset,
                **kwargs,
            )

        return True

    def _configure_single_leaf_backhaul(
        self,
        channel: int,
        leaf_device: "PodHandler",
        radio_band: str,
        ht_mode: str,
        encryption: str,
        mesh_type: str | None = "gre",
        vif_reset: bool = False,
        **kwargs,
    ) -> Literal[True]:
        """
        Create and configure a backhaul connection.

        Args:
            channel (int): Radio channel.
            leaf_device (object): LEAF device object.
            radio_band (str): Radio band.
            leaf_radio_band (str): Leaf radio band.
            ht_mode (str): HT mode.
            encryption (str): Encryption type.
            mesh_type (bool | None): Mesh type. Defaults to 'gre'.
                Supported options: 'gre', 'wds' or None
            vif_reset (bool): Reset all VIF interfaces on both devices.
                Default is False.

        Returns:
            (bool): True if backhaul connection is configured correctly.
        """
        # Determine LEAF radio band
        leaf_radio_band = leaf_device.get_radio_band_from_remote_channel_and_band(
            channel=channel,
            remote_radio_band=radio_band,
        )

        # Determine backhaul STA interface name and MAC address
        backhaul_sta_if_name = leaf_device.capabilities.get_bhaul_sta_ifname(freq_band=leaf_radio_band)
        mac_list = leaf_device.iface.get_vif_mac(backhaul_sta_if_name)
        assert mac_list, f"Can not get {backhaul_sta_if_name} MAC on {leaf_device.nickname.upper()}"
        backhaul_sta_mac = mac_list[0]

        mac_list = [backhaul_sta_mac]
        network_if_name = backhaul_sta_if_name

        # Determine the appropriate MAC address for GRE configuration
        gre_config_leaf_mac = backhaul_sta_mac

        if self.mlo_bh and leaf_device.mlo_bh:
            leaf_backhaul_mld_addr = leaf_device.ovsdb.get(
                table="Wifi_VIF_State",
                select="mld_addr",
                where="mode==sta",
            )
            mac_list.append(leaf_backhaul_mld_addr.strip())
            network_if_name = leaf_device.capabilities.get_mld_iface(iface_type="backhaul_sta")
            # Use MLD address for GRE configuration when MLO is enabled
            gre_config_leaf_mac = leaf_backhaul_mld_addr.strip()
            # Disable all non-active backhaul STA interfaces on the LEAF device
            assert (
                leaf_device.execute(
                    "tools/device/ovsdb/update_ovsdb_entry",
                    f"Wifi_VIF_Config -wn if_name {backhaul_sta_if_name} -u enabled false",
                )[0]
                == 0
            )

        if vif_reset:
            # Reset VIF interfaces on GW and LEAF devices
            self.vif_reset()
            leaf_device.vif_reset()

        # AP interface object arguments
        create_gw_ap_interface_object_kwargs = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": radio_band,
            "encryption": encryption,
            "interface_role": "backhaul_ap",
            "mac_list_type": "whitelist",
            "mac_list": mac_list,
        }

        # STA interface object arguments
        create_sta_interface_object_kwargs = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": leaf_radio_band,
            "encryption": encryption,
            "interface_role": "backhaul_sta",
            "network_if_name": network_if_name,
        }

        if mesh_type == "wds":
            gw_ap_wds_kwargs = {
                "multi_ap": "backhaul_bss",
                "broadcast": "0.0.0.0",
                "dhcpd": {},
                "ip_assign_scheme": "none",
                "inet_addr": "0.0.0.0",
                "netmask": "0.0.0.0",
            }

            sta_wds_kwargs = {
                "multi_ap": "backhaul_sta",
                "wait_ip": False,
            }

            create_gw_ap_interface_object_kwargs.update(gw_ap_wds_kwargs)
            create_sta_interface_object_kwargs.update(sta_wds_kwargs)

        # Add any additional keyword arguments from **kwargs
        create_gw_ap_interface_object_kwargs.update(kwargs)
        create_sta_interface_object_kwargs.update(kwargs)

        # Create AP and STA interface objects
        self.create_interface_object(**create_gw_ap_interface_object_kwargs)
        leaf_device.create_interface_object(**create_sta_interface_object_kwargs)

        # Configure the AP and STA interfaces on the devices
        assert self.interface["backhaul_ap"].configure_interface() == 0
        assert leaf_device.interface["backhaul_sta"].configure_interface() == 0

        if mesh_type == "gre":
            gw_gre_conf_args = get_command_arguments(
                self.interface["backhaul_ap"].network_if_name,
                gre_config_leaf_mac,
                self.capabilities.get_uplink_gre_mtu(),
                self.capabilities.get_lan_bridge_ifname(),
            )
            assert self.execute("tools/device/configure_gre_tunnel_gw", gw_gre_conf_args)[0] == 0
        elif mesh_type == "wds":
            # Retrieve WDS interface name
            wds_if_name = self.ovsdb.get(
                table="Wifi_VIF_State",
                select="if_name",
                where=f"ap_vlan_sta_addr=={backhaul_sta_mac}",
            )
            log.info(f"WDS interface created on {self.nickname.upper()}: {wds_if_name}")
            # Add WDS interface to bridge
            lan_br_if_name = self.capabilities.get_lan_bridge_ifname()
            add_port_to_bridge_args = get_command_arguments(
                lan_br_if_name,
                wds_if_name,
            )
            assert self.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == 0

        return True

    def _configure_dual_leaf_backhaul(
        self,
        channel: int,
        leaf_device: "PodHandler",
        second_leaf_device: "PodHandler",
        topology: str,
        radio_band: str,
        ht_mode: str,
        encryption: str,
        mesh_type: str | None = "gre",
        vif_reset: bool = False,
        **kwargs,
    ) -> Literal[True]:
        """
        Create and configure a backhaul connection.

        Args:
            channel (int): Radio channel.
            leaf_device (object): LEAF device object.
            radio_band (str): Radio band.
            ht_mode (str): HT mode.
            encryption (str): Encryption type.
            mesh_type (bool | None): Mesh type. Defaults to 'gre'.
                Supported options: 'gre', 'wds' or None
            second_leaf_device (object | None): Second leaf device object.
            topology (str | None): Topology. Supported options: 'star', 'line'.
            vif_reset (bool): Reset all VIF interfaces on both devices.
                Default is False.

        Returns:
            (bool): True if backhaul connection is configured correctly.

        Raises:
            ValueError: The topology is not either 'star' or 'line'
        """
        # Determine LEAF radio bands
        leaf_radio_band = leaf_device.get_radio_band_from_remote_channel_and_band(
            channel=channel,
            remote_radio_band=radio_band,
        )
        second_leaf_radio_band = second_leaf_device.get_radio_band_from_remote_channel_and_band(
            channel=channel,
            remote_radio_band=radio_band,
        )

        # Determine radio interface name for the devices
        gw_bhaul_ap_if_name = self.capabilities.get_bhaul_ap_ifname(freq_band=radio_band)

        l1_bhaul_ap_if_name = leaf_device.capabilities.get_bhaul_ap_ifname(freq_band=leaf_radio_band)

        leaf_phy_radio_if_name = leaf_device.capabilities.get_phy_radio_ifname(freq_band=leaf_radio_band)
        second_leaf_phy_radio_if_name = second_leaf_device.capabilities.get_phy_radio_ifname(
            freq_band=second_leaf_radio_band,
        )

        leaf_device_physical_wifi_mac = leaf_device.iface.get_physical_wifi_mac(
            ifname=leaf_phy_radio_if_name,
        )
        second_leaf_device_physical_wifi_mac = second_leaf_device.iface.get_physical_wifi_mac(
            ifname=second_leaf_phy_radio_if_name,
        )

        if vif_reset:
            # Reset VIF interfaces on GW and LEAF devices
            self.vif_reset()
            leaf_device.vif_reset()
            second_leaf_device.vif_reset()

        if topology == "star":
            mac_list = [leaf_device_physical_wifi_mac, second_leaf_device_physical_wifi_mac]
        elif topology == "line":
            mac_list = [leaf_device_physical_wifi_mac]
        else:
            raise ValueError("Invalid topology provided. Supported options: 'star', 'line'")

        # GW AP interface object arguments
        create_gw_ap_interface_object_kwargs = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": radio_band,
            "encryption": encryption,
            "interface_role": "backhaul_ap",
            "mac_list_type": "whitelist",
            "mac_list": mac_list,
        }

        # Create GW AP interface

        if mesh_type == "wds":
            gw_ap_wds_kwargs = {
                "multi_ap": "backhaul_bss",
                "broadcast": "0.0.0.0",
                "dhcpd": {},
                "ip_assign_scheme": "none",
                "inet_addr": "0.0.0.0",
                "netmask": "0.0.0.0",
            }

            create_gw_ap_interface_object_kwargs.update(gw_ap_wds_kwargs)

        create_gw_ap_interface_object_kwargs.update(kwargs)
        self.create_interface_object(**create_gw_ap_interface_object_kwargs)
        assert self.interface["backhaul_ap"].configure_interface() == 0

        # Retrieve GW backhaul AP MAC
        mac_list = self.iface.get_vif_mac(gw_bhaul_ap_if_name)
        assert mac_list, f"Can not get {gw_bhaul_ap_if_name} MAC on {self.nickname.upper()}"
        gw_bhaul_ap_mac = mac_list[0]

        if topology == "line":

            # LEAF1 AP interface object arguments
            create_leaf1_ap_interface_object_kwargs = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "encryption": encryption,
                "interface_role": "backhaul_ap",
                "mac_list_type": "whitelist",
                "mac_list": [second_leaf_device_physical_wifi_mac],
            }

            if mesh_type == "wds":
                l1_ap_wds_kwargs = gw_ap_wds_kwargs.copy()
                create_leaf1_ap_interface_object_kwargs.update(l1_ap_wds_kwargs)

            create_leaf1_ap_interface_object_kwargs.update(kwargs)
            leaf_device.create_interface_object(**create_leaf1_ap_interface_object_kwargs)
            assert leaf_device.interface["backhaul_ap"].configure_interface() == 0

            # Retrieve LEAF1 backhaul AP MAC
            mac_list = leaf_device.iface.get_vif_mac(l1_bhaul_ap_if_name)
            assert mac_list, f"Can not get {l1_bhaul_ap_if_name} MAC on {leaf_device.nickname.upper()}"
            l1_bhaul_ap_mac = mac_list[0]

        # LEAF1 STA interface object arguments
        create_leaf1_sta_interface_object_kwargs = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": leaf_radio_band,
            "encryption": encryption,
            "interface_role": "backhaul_sta",
        }

        # LEAF2 STA interface object arguments
        create_leaf2_sta_interface_object_kwargs = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": second_leaf_radio_band,
            "encryption": encryption,
            "interface_role": "backhaul_sta",
        }

        if topology == "star":
            create_leaf1_sta_interface_object_kwargs.update(
                {
                    "parent": [gw_bhaul_ap_mac],
                },
            )
            create_leaf2_sta_interface_object_kwargs.update(
                {
                    "parent": [gw_bhaul_ap_mac],
                },
            )
        elif topology == "line":
            create_leaf1_sta_interface_object_kwargs.update(
                {
                    "parent": [gw_bhaul_ap_mac],
                },
            )
            create_leaf2_sta_interface_object_kwargs.update(
                {
                    "parent": [l1_bhaul_ap_mac],
                },
            )

        if mesh_type == "wds":
            first_sta_wds_kwargs = {
                "multi_ap": "backhaul_sta",
                "wait_ip": False,
            }

            second_sta_wds_kwargs = {
                "multi_ap": "backhaul_sta",
                "wait_ip": False,
            }

            create_leaf1_sta_interface_object_kwargs.update(first_sta_wds_kwargs)
            create_leaf2_sta_interface_object_kwargs.update(second_sta_wds_kwargs)

        # Add any additional keyword arguments from **kwargs
        create_leaf1_sta_interface_object_kwargs.update(kwargs)
        create_leaf2_sta_interface_object_kwargs.update(kwargs)

        # Create AP and STA interface objects
        leaf_device.create_interface_object(**create_leaf1_sta_interface_object_kwargs)
        second_leaf_device.create_interface_object(**create_leaf2_sta_interface_object_kwargs)

        # Configure the AP and STA interfaces on the devices
        assert leaf_device.interface["backhaul_sta"].configure_interface() == 0
        assert second_leaf_device.interface["backhaul_sta"].configure_interface() == 0

        if mesh_type == "gre":
            gw_gre_conf_args = get_command_arguments(
                self.interface["backhaul_ap"].network_if_name,
                leaf_device_physical_wifi_mac,
                self.capabilities.get_uplink_gre_mtu(),
                self.capabilities.get_lan_bridge_ifname(),
            )
            assert self.execute("tools/device/configure_gre_tunnel_gw", gw_gre_conf_args)[0] == 0

            if topology == "line":
                leaf_gre_conf_args = get_command_arguments(
                    leaf_device.interface["backhaul_ap"].network_if_name,
                    second_leaf_device_physical_wifi_mac,
                    leaf_device.capabilities.get_uplink_gre_mtu(),
                    leaf_device.capabilities.get_lan_bridge_ifname(),
                )
                assert leaf_device.execute("tools/device/configure_gre_tunnel_gw", leaf_gre_conf_args)[0] == 0
            elif topology == "star":
                gw_gre_conf_args = get_command_arguments(
                    self.interface["backhaul_ap"].network_if_name,
                    second_leaf_device_physical_wifi_mac,
                    self.capabilities.get_uplink_gre_mtu(),
                    self.capabilities.get_lan_bridge_ifname(),
                )
                assert self.execute("tools/device/configure_gre_tunnel_gw", gw_gre_conf_args)[0] == 0
        elif mesh_type == "wds":
            # Retrieve WDS interface name
            wds_if_name = self.ovsdb.get(
                table="Wifi_VIF_State",
                select="if_name",
                where=f"ap_vlan_sta_addr=={leaf_device_physical_wifi_mac}",
            )
            log.info(f"WDS interface created on {self.nickname.upper()}: {wds_if_name}")
            # Add WDS interface to bridge
            lan_br_if_name = self.capabilities.get_lan_bridge_ifname()
            add_port_to_bridge_args = get_command_arguments(
                lan_br_if_name,
                wds_if_name,
            )
            assert self.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == 0

            if topology == "line":
                wds_if_name = leaf_device.ovsdb.get(
                    table="Wifi_VIF_State",
                    select="if_name",
                    where=f"ap_vlan_sta_addr=={second_leaf_device_physical_wifi_mac}",
                )
                log.info(f"WDS interface created on {leaf_device.nickname.upper()}: {wds_if_name}")
                # Add WDS interface to bridge
                lan_br_if_name = leaf_device.capabilities.get_lan_bridge_ifname()
                add_port_to_bridge_args = get_command_arguments(
                    lan_br_if_name,
                    wds_if_name,
                )
                assert leaf_device.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == 0
            elif topology == "star":
                wds_if_name = self.ovsdb.get(
                    table="Wifi_VIF_State",
                    select="if_name",
                    where=f"ap_vlan_sta_addr=={second_leaf_device_physical_wifi_mac}",
                )
                log.info(f"WDS interface created on {self.nickname.upper()}: {wds_if_name}")
                # Add WDS interface to bridge
                lan_br_if_name = self.capabilities.get_lan_bridge_ifname()
                add_port_to_bridge_args = get_command_arguments(
                    lan_br_if_name,
                    wds_if_name,
                )
                assert self.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == 0

        return True

    def create_interface_object(
        self,
        channel: int,
        ht_mode: str,
        radio_band: str,
        encryption: str,
        interface_role: str,
        **kwargs,
    ) -> None:
        """
        Create a new interface object and assigns it to the 'interfaces' dictionary.

        Args:
            channel (int): The channel number for the interface.
            ht_mode (str): The HT mode for the interface.
            radio_band (str): The radio band for the interface.
            encryption (str): The encryption mode for the interface.
            interface_role (str): The role of the interface.
            **kwargs: Additional keyword arguments used to override defaults. Please see the 'Override arguments'
                section of the 'VirtualInterface' class docstring for further details.

        Returns:
            None: This method does not return anything.
        """
        interface = self.VirtualInterface(
            self,
            channel,
            ht_mode,
            radio_band,
            encryption,
            interface_role,
            self.location_config,
            **kwargs,
        )
        self.interface[interface_role] = interface
        log.info(f"{self.nickname.upper()}: created interface -> {interface_role}")

    class VirtualInterface:
        """
        VirtualInterface class represents a virtual interface in a network node.

        Attributes:
            node (PodHandler): The PodHandler class object.
            channel (int): The channel number on which the interface operates.
            ht_mode (str): The HT mode of the interface.
            radio_band (str): The radio band of the interface.
            encryption (str): The encryption type used for the interface.
            interface_role (str): The role of the interface.
            ssid_raw (str): The raw SSID value of the interface.
            psk_raw (str): The raw PSK (Pre-Shared Key) value of the interface.
            override_args (dict): Additional arguments to override the default configuration. Please see the
                'Override arguments' section of this docstring for further details.
            if_name (str): The name of the virtual interface.
            interface_mode (str): The mode of the interface, either "ap" or "sta".
            radio_args (dict): Configuration arguments for the radio interface.
            vif_args (dict): Configuration arguments for the virtual interface.
            network_args (dict): Configuration arguments for the network (AP interface only).
            combined_args (dict): Combined configuration arguments for the virtual interface.

        Override arguments:
            Additional arguments can be passed as **kwargs to override the default configuration. The arguments can be
            split up in three categories, as outlined below.

            AP VIF arguments:
                - ap_bridge (bool): AP isolation.
                - bridge (str | None): Bridge interface.
                - mac_list (list): A list of MAC addresses, that are either white- or blacklisted with regard to packet
                    filtering. Defaults to an empty list unless overridden.
                - mac_list_type (str): Determine whether to either whitelist/blacklist the addresses defined in mac_list
                    or skip packet filtering entirely. Supported values: 'whitelist', 'blacklist' or 'none'. Defaults to
                    none unless overridden.
                - mode (str): The virtual interface mode determined based on the interface role. Defaults to 'ap'.
                - multi_ap (str): Device type as defined by the Multi AP specification.
                - perform_cac (bool): Perform the channel availability check. Defaults to true.
                - ssid (str): SSID. Defaults to the SSID generated using the _generate_ssid() method.
                - ssid_broadcast (str): The SSID broadcast value determined based on the interface role.
                - vif_if_name (str): The virtual interface name determined based on the selected interface role and
                    radio band.
                - vif_radio_idx (int): The virtual interface radio index determined based on the selected interface
                    role.
                - wpa_psks (str | list): The PSK (Pre-Shared Key) value. Defaults to the PSK generated using the
                    _generate_psk() method.
                - wpa_key_mgmt (str): The encryption used for WPA key management.

            STA VIF arguments:
                - mac_list (list): A list of MAC addresses, that are either white- or blacklisted with regard to packet
                    filtering. Defaults to an empty list unless overridden.
                - mac_list_type (str): Determine whether to either whitelist/blacklist the addresses defined in mac_list
                    or skip packet filtering entirely. Supported values: 'whitelist', 'blacklist' or 'none'. Defaults to
                    none unless overridden.
                - mode (str): The virtual interface mode determined based on the interface role. Defaults to 'sta'.
                - multi_ap (str): Device type as defined by the Multi AP specification.
                - parent (list): MAC address of the parent interface. Default to an empty list.
                - ssid (str): SSID. Defaults to the SSID generated using the _generate_ssid() method.
                - vif_if_name (str): The virtual interface name determined based on the selected interface role and
                    radio band.
                - wpa_psks (str | list): The PSK (Pre-Shared Key) value. Defaults to the PSK generated using the
                    _generate_psk() method.
                - wpa_key_mgmt (str): The encryption used for WPA key management.
                - clear_wcc (bool): Clear the Wifi_Credentials_config OVSDB table. Default to True.
                - wait_ip (bool): Wait for the configured STA interface to receive an IP. Default to True.

            Network arguments:
                - broadcast (str): The broadcast address.
                - dhcpd (dict): DHCP options that are used to configure the DHCP server. The following options are
                    supported: dhcp_option, force, lease_time, start (IP pool start address),
                    stop (IP pool end address).
                - inet_addr (str): The IP address.
                - if_type (str): Interface type. Defaults to 'vif'.
                - inet_enabled (bool): The desired interface state. Defaults to True.
                - ip_assign_scheme (str): The IP assign scheme. Possible values: 'none', 'dhcp' and 'static'.
                - mtu (int): The desired MTU.
                - NAT (bool): NAT/Masquerading for outgoing traffic. Defaults to False.
                - network (bool): Specify whether the network configuration should be applied to the interface. Defaults
                    to True.
                - network_if_name (str): The network interface name.

            Any other provided **kwargs that are used to override any values should match the field names from the
            Wifi_VIF_Config and Wifi_Inet_Config OVSDB tables.

        Methods:
            __init__(self, node, channel, ht_mode, radio_band, encryption, interface_role, **kwargs):
                Initialize the VirtualInterface object with the provided parameters.
            _validate_parameters(self):
                Validate the parameters based on the interface role.
            _generate_ssid(self, interface_role):
                Generate hashed SSID value based on the interface role.
            _generate_psk(self, interface_role):
                Generate hashed PSK value based on the interface role.
            _determine_interface_mode(self):
                Determine interface mode based on the interface role.
            _configure_vif_args(self):
                Configure VIF arguments based on the interface mode.
            _configure_radio_args(self):
                Configure radio arguments.
            _configure_ap_vif_args(self):
                Configure virtual interface arguments for an AP.
            _configure_sta_vif_args(self):
                Configure virtual interface arguments for an STA.
        """

        def __init__(
            self,
            node: "PodHandler",
            channel: int,
            ht_mode: str,
            radio_band: str,
            encryption: str,
            interface_role: str,
            location_config: dict,
            **kwargs,
        ):
            self.node = node
            self.channel = channel
            self.ht_mode = ht_mode
            self.radio_band = radio_band
            self.encryption = encryption
            self.interface_role = interface_role
            self.location_config = location_config
            self.ssid_raw = None
            self.psk_raw = None

            # Store the override keyword arguments in a dict for easier processing
            self.override_args = kwargs

            # Retrieve virtual interface name based on the selected interface role and radio band
            self.if_name = self.node.capabilities.get_ifname(freq_band=self.radio_band, iftype=self.interface_role)

            self.interface_mode = self._determine_interface_mode()
            self.radio_args = self._configure_radio_args()
            self.vif_args = self._configure_vif_args()
            self.vif_radio_idx = self.node.capabilities.get_iftype_vif_radio_idx(iftype=self.interface_role)

            # Determine network interface name based on MLO capabilities
            is_mlo_enabled = (self.interface_role in ["backhaul_ap", "backhaul_sta"] and self.node.mlo_bh) or (
                # backhaul APs are configured into a MLO group even if only MLO_FH is supported
                self.interface_role in ["backhaul_ap", "home_ap", "onboard_ap", "fhaul_ap"]
                and self.node.mlo_fh
            )
            self.network_if_name = (
                self.node.capabilities.get_mld_iface(iface_type=self.interface_role) if is_mlo_enabled else self.if_name
            )

            # If the interface is an AP, the network arguments are also necessary
            if self.interface_role != "backhaul_sta":
                self.network_args = self._configure_network_args()

            self.combined_args = self._configure_combined_args()

        def _generate_ssid(self, interface_role: str) -> str:
            """
            Generate hashed SSID value.

            Generates a hashed SSID value based on the interface role.

            Args:
                interface_role (str): The role of the interface.

            Returns:
                str: The generated SSID.
            """
            ssid = f"{self.node.base_ssid}_{interface_role}"
            hashed_ssid = get_str_hash(input_string=ssid, hash_length=32)
            return hashed_ssid

        def _generate_psk(self, interface_role: str) -> str:
            """
            Generate hashed PSK value.

            Generates a hashed PSK (Pre-Shared Key) value based on the interface role.

            Args:
                interface_role (str): The role of the interface.

            Returns:
                str: The generated PSK.
            """
            psk = f"{self.node.base_psk}_{interface_role}"
            hashed_psk = get_str_hash(input_string=psk, hash_length=32)
            return hashed_psk

        def _determine_interface_mode(self) -> str:
            """
            Determine interface mode.

            Determines the interface mode based on the `interface_role` attribute.

            Returns:
                str: The interface mode, either "ap" or "sta".
            Raises:
                ValueError: The interface role does not end with either "ap" or "sta".
            """
            if self.interface_role.lower().endswith("ap"):
                mode = "ap"
            elif self.interface_role.lower().endswith("sta"):
                mode = "sta"
            else:
                raise ValueError(
                    f"Unable to determine interface mode from interface role {self.interface_role}, supported: 'ap', 'sta'.",
                )
            return mode

        def _configure_vif_args(self) -> dict:
            """
            Configure VIF arguments.

            The method either calls the _configure_ap_vif_args() or _configure_sta_vif_args()
            method, based on the determined interface mode.

            Returns:
                dict: Configuration arguments for the virtual interface (vif).
            """
            if self.interface_mode == "ap":
                vif_args = self._configure_ap_vif_args()
            else:
                vif_args = self._configure_sta_vif_args()
            return vif_args

        def _configure_radio_args(self):
            """
            Configure radio arguments.

            Determines the radio interface name based on the selected radio band and sets the radio arguments.

            Returns:
                radio_args (dict): A dictionary containing the radio arguments.
            """
            # Determine radio interface name based on the selected radio band
            phy_if_name = self.node.capabilities.get_phy_radio_ifname(freq_band=self.radio_band)

            radio_args = {
                "channel": self.channel,
                "channel_mode": "manual",
                "ht_mode": self.ht_mode,
                "radio_if_name": phy_if_name,
            }
            tx_power = self.override_args.pop("tx_power", 1)
            if self.node.capabilities.is_tx_power_configurable():
                radio_args["tx_power"] = tx_power
            return radio_args

        def _configure_ap_vif_args(self) -> dict:
            """
            Configure virtual interface arguments for an AP.

            Returns:
                vif_args (dict): A dictionary containing the configured AP VIF arguments.
            """
            # Determine the bridge interface and AP isolation
            if any(interface_roles in self.interface_role for interface_roles in ("backhaul_ap", "onboard_ap")):
                ap_bridge = True
                vif_args = {}
            else:
                bridge = self.node.capabilities.get_lan_bridge_ifname()
                ap_bridge = False

                vif_args = {
                    "bridge": bridge,
                }

            # Default the mac_list parameter to an empty list
            mac_list = []

            # Default the mac_list_type to 'none'
            mac_list_type = "none"

            # Retrieve virtual interface radio index based on the selected interface role
            vif_radio_idx = self.node.capabilities.get_iftype_vif_radio_idx(iftype=self.interface_role)

            # Determine SSID broadcast based on the interface role
            ssid_broadcast = "disabled" if self.interface_role == "backhaul_ap" else "enabled"

            # Default the channel availability check to true
            perform_cac = True

            common_vif_args = {
                "ap_bridge": ap_bridge,
                "enabled": True,
                "mac_list": mac_list,
                "mac_list_type": mac_list_type,
                "mode": "ap",
                "perform_cac": perform_cac,
                "ssid_broadcast": ssid_broadcast,
                "vif_if_name": self.if_name,
                "vif_radio_idx": vif_radio_idx,
            }

            vif_args.update(common_vif_args)

            # Configuration of security arguments
            security_args = self._configure_security_args()
            vif_args.update(security_args)

            # Override the configured VIF arguments with entries from the provided override dict
            vif_args.update(self.override_args)

            return vif_args

        def _configure_sta_vif_args(self) -> dict:
            """
            Configure virtual interface arguments for an STA.

            Returns:
                vif_args (dict): A dictionary containing the configured STA VIF arguments.
            """
            # Clear the Wifi_Credentials_config OVSDB table by default
            clear_wcc = True

            # Wait for the configured STA interface to receive an IP by default
            wait_ip = True

            vif_args = {
                "mode": "sta",
                "parent": [],
                "vif_if_name": self.if_name,
                "clear_wcc": clear_wcc,
                "wait_ip": wait_ip,
            }

            # The security args are by default configured to be the same as if the interface was a backhaul AP
            # Temporarily set the interface role to 'backhaul_ap' for SSID and PSK generation
            self.interface_role = "backhaul_ap"

            security_args = self._configure_security_args()
            vif_args.update(security_args)

            # Revert the interface role back to "backhaul_sta"
            self.interface_role = "backhaul_sta"

            # Override the configured VIF arguments with entries from the provided override keyword arguments
            vif_args.update(self.override_args)

            return vif_args

        def _configure_security_args(self) -> dict:
            """
            Configure virtual interface security arguments.

            Returns:
                dict: A dictionary containing the configured security arguments.

            Raises:
                KeyError: If the encryption value is invalid.
            """
            match self.encryption.upper():
                case "WPA2":
                    wpa_key_mgmt = "wpa2-psk"
                case "WPA3":
                    wpa_key_mgmt = "sae"
                case "WPA3-TRANSITION":
                    wpa_key_mgmt = ["sae", "wpa2-psk"]
                case "OPEN":
                    wpa_key_mgmt = []
                case _:
                    raise KeyError(f"Invalid encryption: {self.encryption.upper()}")

            # Check override values for SSID and PSK, otherwise generate hashed SSID and PSK values
            ssid = self.override_args.pop("ssid", self._generate_ssid(interface_role=self.interface_role))
            psk = self.override_args.pop("wpa_psks", self._generate_psk(interface_role=self.interface_role))

            # Save unformatted SSID value for use in test cases
            self.ssid_raw = ssid

            if self.encryption.upper() == "OPEN":
                wpa = False
                psk = None
                wpa_psks_dict = {}
                wpa_oftags_dict = {}
                # Save unformatted PSK value for use in test cases
                self.psk_raw = psk
            else:
                wpa = True

                # Save unformatted PSK value for use in test cases
                self.psk_raw = psk

                # Cast the psk variable into a list for further processing
                if isinstance(psk, str):
                    psk = [psk]

                # Organize the PSK(s) into a dictionary in case of Multi-PSK
                wpa_psks_dict = {f"key--{index}": key for index, key in enumerate(psk, start=1)}

                # Configure and format the wpa_oftags field value
                oftag = self.interface_role.rsplit("_", 1)[0]
                wpa_oftags_dict = {f"key--{index}": f"{oftag}--{index}" for index, key in enumerate(psk, start=1)}

            security_args = {
                "ssid": ssid,
                "wpa": wpa,
                "wpa_oftags": wpa_oftags_dict,
                "wpa_psks": wpa_psks_dict,
                "wpa_key_mgmt": wpa_key_mgmt,
            }

            return security_args

        def _configure_network_args(self) -> dict:
            """
            Configure virtual interface network arguments.

            Returns:
                dict: A dictionary containing the network configuration arguments.
            """
            # Determine IP assign scheme
            if any(interface_roles in self.interface_role for interface_roles in ("backhaul_ap", "onboard_ap")):
                ip_assign_scheme = "static"
                netmask = "255.255.255.128"
                subnet = f"169.254.{self.vif_args['vif_radio_idx']}"
                broadcast = f"{subnet}.255"
                inet_addr = f"{subnet}.129"
                dhcpd_start = f"{subnet}.130"
                dhcpd_stop = f"{subnet}.254"
                dhcpd = {
                    "dhcp_option": "26,1600",
                    "force": "false",
                    "lease_time": "12h",
                    "start": dhcpd_start,
                    "stop": dhcpd_stop,
                }

                network_args = {
                    "broadcast": broadcast,
                    "dhcpd": dhcpd,
                    "inet_addr": inet_addr,
                    "netmask": netmask,
                }
            else:
                ip_assign_scheme = "none"
                network_args = {}

            # Default NAT/Masquerading to false for all interfaces
            nat = False

            # Determine MTU
            mtu = self.node.capabilities.get_bhaul_mtu()

            common_network_args = {
                "if_type": "vif",
                "inet_enabled": True,
                "ip_assign_scheme": ip_assign_scheme,
                "mtu": mtu,
                "NAT": nat,
                "network": True,
                "network_if_name": self.network_if_name,
            }

            network_args.update(common_network_args)

            # Override the configured VIF arguments with entries from the provided override keyword arguments
            network_args.update(self.override_args)

            return network_args

        def _configure_combined_args(self):
            """
            Combine the VIF arguments.

            If the interface is an AP, the radio_args, vif_args, and network_args dictionaries are combined. If the
            interface is an STA, only the vif_args dictionary is needed.

            Returns:
                dict: A combined dictionary VIF arguments.
            """
            if self.interface_mode == "ap":
                combined_args = {**self.radio_args, **self.vif_args, **self.network_args}
            else:
                combined_args = self.vif_args

            return combined_args

        def _prepare_and_sanitize_combined_args(self) -> str:
            """
            Prepare the combined arguments for usage in shell scripts.

            This method prepares and sanitizes the combined arguments for usage in shell scripts. It combines the
            key-value pairs from the `combined_args` dictionary and converts the values to OVSDB format using the
            `python_value_to_ovsdb_value` method of the `ovsdb` object. It retrieves the command arguments by calling
            the `get_command_arguments` method of the `node` object, passing in the combined arguments list.

            Returns:
                str: Sanitized combined arguments.

            Example Usage:
                combined_args = {
                    'arg_name_1': 'arg_value_1',
                    'arg_name_2': 'arg_value_2'
                }
                sanitized_combined_args = instance._prepare_and_sanitize_combined_args()
                output:
                    str: "-arg_name_1 arg_value_1 -arg_name_2 arg_value_2"
            """
            combined_args_list = [
                f"-{k} {self.node.ovsdb.python_value_to_ovsdb_value(v)}" for k, v in self.combined_args.items()
            ]
            sanitized_combined_args = get_command_arguments(combined_args_list)

            return sanitized_combined_args

        def vif_reset(self) -> None:
            """
            Reset the virtual interface on the device and remove the port from bridge if needed.

            Raises:
                AssertionError: If the command to reset the VIF fails.
            """
            vif_reset_args = f"{self.if_name},{self.network_if_name}"  # CSV of VIF/Inet if_name
            assert self.node.execute("tools/device/vif_reset", vif_reset_args)[0] == 0

            bridge = self.combined_args.get("bridge")
            if bridge:
                remove_port_from_bridge_args = get_command_arguments(bridge, self.network_if_name)
                assert self.node.execute("tools/device/remove_port_from_bridge", remove_port_from_bridge_args)[0] == 0

        def _configure_ap_interface(self, vif_reset: bool = False, perform_network_config: bool = True) -> int:
            """
            Configure the AP VIF interface on the device.

            Args:
                vif_reset (bool): Reset all VIF interfaces on the device. Default is False.
                perform_network_config (bool): Perform network configuration. Only applicable when the VIF is an AP.
                    Default is True.

            Returns:
                res (int): Exit code.
            """
            if vif_reset:
                self.vif_reset()

            # Add the perform_network_config argument to the combined VIF arguments
            self.combined_args.update({"perform_network_config": perform_network_config})

            combined_args = self._prepare_and_sanitize_combined_args()

            res = self.node.execute_with_logging("tools/device/configure_ap_interface", combined_args)

            return res[0]

        def _configure_sta_interface(self, vif_reset: bool = False) -> int:
            """
            Configure the STA VIF interface on the device.

            This method calls the 'configure_sta_interface' shell script, which populates the necessary OVSDB tables to
            configure an STA interface. The script also waits for the STA interface to associate to an AP.

            Args:
                vif_reset (bool): Reset all VIF interfaces on the device. Default is False.

            Returns:
                res (int): Exit code.
            """
            if vif_reset:
                self.vif_reset()

            combined_args = self._prepare_and_sanitize_combined_args()

            res = self.node.execute_with_logging("tools/device/configure_sta_interface", combined_args)

            return res[0]

        def configure_interface(self, vif_reset: bool = False, perform_network_config: bool = True) -> int:
            """
            Configure the VIF interface on the device.

            Args:
                vif_reset (bool): Reset the VIF interfaces. Default is False.
                perform_network_config (bool): Perform network configuration. Only applicable when the VIF is an AP.
                    Default is True.

            Returns:
                res (int): Exit code.

            Raises:
                ValueError: The interface role does not end with either "ap" or "sta".
            """
            if self.interface_mode == "ap":
                res = self._configure_ap_interface(vif_reset, perform_network_config)
            elif self.interface_mode == "sta":
                res = self._configure_sta_interface(vif_reset)
            else:
                raise ValueError(f"Unsupported interface_mode {self.interface_mode}, supported: 'ap', 'sta'.")

            return res
