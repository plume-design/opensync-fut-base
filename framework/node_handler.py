import time
from os import PathLike
from pathlib import Path
from random import randrange
from typing import Literal

import allure
from mergedeep import merge, Strategy

from config.defaults import radio_band_list
from framework.device_handler import DeviceHandler
from framework.lib.fut_lib import get_str_hash, step
from lib_testbed.generic.util.logger import log


class NodeHandler(DeviceHandler):
    def __init__(self, name):
        log.debug("Entered NodeHandler class")
        super().__init__(name)
        self.expected_shell_result = 0
        self.regulatory_domain = self._get_region()
        self.supported_radio_bands = self.capabilities.get_supported_bands()
        self.opensync_root_dir = self.capabilities.get_opensync_rootdir()
        self.ovsdb = self.device_api.lib.ovsdb
        self.interfaces: dict = {}

    def configure_device_mode(self, device_mode: str) -> Literal[True]:
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
        set_router_mode_args = self.get_command_arguments(
            if_lan_br_name,
            internal_dhcpd,
            internal_inet_addr,
            eth_wan_interface,
        )
        set_bridge_mode_args = self.get_command_arguments(
            if_lan_br_name,
            eth_wan_interface,
        )

        # Put the device into router or bridge mode.
        if device_mode == "router":
            assert self.execute("tools/device/set_router_mode", set_router_mode_args)[0] == self.expected_shell_result
        elif device_mode == "bridge":
            assert self.execute("tools/device/set_bridge_mode", set_bridge_mode_args)[0] == self.expected_shell_result
        else:
            raise RuntimeError(f"Invalid device mode provided: {device_mode}. Supported: 'router', 'bridge'.")

        return True

    def vif_reset(self) -> None:
        """Reset all virtual interfaces on the device.

        Raises:
            AssertionError: If the command to reset the VIF fails.
        """
        assert self.execute("tools/device/vif_reset")[0] == self.expected_shell_result

    def create_and_configure_backhaul(
        self,
        channel: int,
        leaf_device: "NodeHandler",
        radio_band: str,
        ht_mode: str,
        encryption: str,
        mesh_type: str | None = "gre",
        second_leaf_device: "NodeHandler" = None,
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
        leaf_device: "NodeHandler",
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

        # Determine radio interface name for the LEAF device
        leaf_phy_radio_if_name = leaf_device.capabilities.get_phy_radio_ifname(freq_band=leaf_radio_band)

        leaf_device_physical_wifi_mac = leaf_device.device_api.iface.get_physical_wifi_mac(
            ifname=leaf_phy_radio_if_name,
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
            # fmt: off
            "mac_list": [f"\"{leaf_device_physical_wifi_mac}\""],
            # fmt: on
        }

        # STA interface object arguments
        create_sta_interface_object_kwargs = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": leaf_radio_band,
            "encryption": encryption,
            "interface_role": "backhaul_sta",
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
        assert self.interfaces["backhaul_ap"].configure_interface() == self.expected_shell_result
        assert leaf_device.interfaces["backhaul_sta"].configure_interface() == self.expected_shell_result

        if mesh_type == "gre":
            gw_gre_conf_args = self.get_command_arguments(
                self.interfaces["backhaul_ap"].combined_args["vif_if_name"],
                leaf_device_physical_wifi_mac,
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
            log.info(f"WDS interface created on {self.name.upper()}: {wds_if_name}")
            # Add WDS interface to bridge
            lan_br_if_name = self.capabilities.get_lan_bridge_ifname()
            add_port_to_bridge_args = self.get_command_arguments(
                lan_br_if_name,
                wds_if_name,
            )
            assert self.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == 0

        return True

    def _configure_dual_leaf_backhaul(
        self,
        channel: int,
        leaf_device: "NodeHandler",
        second_leaf_device: "NodeHandler",
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

        leaf_device_physical_wifi_mac = leaf_device.device_api.iface.get_physical_wifi_mac(
            ifname=leaf_phy_radio_if_name,
        )
        second_leaf_device_physical_wifi_mac = second_leaf_device.device_api.iface.get_physical_wifi_mac(
            ifname=second_leaf_phy_radio_if_name,
        )

        if vif_reset:
            # Reset VIF interfaces on GW and LEAF devices
            self.vif_reset()
            leaf_device.vif_reset()
            second_leaf_device.vif_reset()

        # fmt: off
        if topology == "star":
            mac_list = [f"\"{leaf_device_physical_wifi_mac}\",\"{second_leaf_device_physical_wifi_mac}\""]
        elif topology == "line":
            mac_list = [f"\"{leaf_device_physical_wifi_mac}\""]
        else:
            raise ValueError("Invalid topology provided. Supported options: 'star', 'line'")
        # fmt: on

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
        assert self.interfaces["backhaul_ap"].configure_interface() == self.expected_shell_result

        # Retrieve GW backhaul AP MAC
        gw_bhaul_ap_mac = self.device_api.iface.get_vif_mac(gw_bhaul_ap_if_name)[0]

        if topology == "line":

            # LEAF1 AP interface object arguments
            create_leaf1_ap_interface_object_kwargs = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "encryption": encryption,
                "interface_role": "backhaul_ap",
                "mac_list_type": "whitelist",
                # fmt: off
                "mac_list": [f"\"{second_leaf_device_physical_wifi_mac}\""],
                # fmt: on
            }

            if mesh_type == "wds":
                l1_ap_wds_kwargs = gw_ap_wds_kwargs.copy()
                create_leaf1_ap_interface_object_kwargs.update(l1_ap_wds_kwargs)

            create_leaf1_ap_interface_object_kwargs.update(kwargs)
            leaf_device.create_interface_object(**create_leaf1_ap_interface_object_kwargs)
            assert leaf_device.interfaces["backhaul_ap"].configure_interface() == self.expected_shell_result

            # Retrieve LEAF1 backhaul AP MAC
            l1_bhaul_ap_mac = leaf_device.device_api.iface.get_vif_mac(l1_bhaul_ap_if_name)[0]

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
                    # fmt: off
                    "parent": [f"\"{gw_bhaul_ap_mac}\""],
                    # fmt: on
                },
            )
            create_leaf2_sta_interface_object_kwargs.update(
                {
                    # fmt: off
                    "parent": [f"\"{gw_bhaul_ap_mac}\""],
                    # fmt: on
                },
            )
        elif topology == "line":
            create_leaf1_sta_interface_object_kwargs.update(
                {
                    # fmt: off
                    "parent": [f"\"{gw_bhaul_ap_mac}\""],
                    # fmt: on
                },
            )
            create_leaf2_sta_interface_object_kwargs.update(
                {
                    # fmt: off
                    "parent": [f"\"{l1_bhaul_ap_mac}\""],
                    # fmt: on
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
        assert leaf_device.interfaces["backhaul_sta"].configure_interface() == self.expected_shell_result
        assert second_leaf_device.interfaces["backhaul_sta"].configure_interface() == self.expected_shell_result

        if mesh_type == "gre":
            gw_gre_conf_args = self.get_command_arguments(
                self.interfaces["backhaul_ap"].combined_args["vif_if_name"],
                leaf_device_physical_wifi_mac,
                self.capabilities.get_uplink_gre_mtu(),
                self.capabilities.get_lan_bridge_ifname(),
            )
            assert self.execute("tools/device/configure_gre_tunnel_gw", gw_gre_conf_args)[0] == 0

            if topology == "line":
                leaf_gre_conf_args = self.get_command_arguments(
                    leaf_device.interfaces["backhaul_ap"].combined_args["vif_if_name"],
                    second_leaf_device_physical_wifi_mac,
                    leaf_device.capabilities.get_uplink_gre_mtu(),
                    leaf_device.capabilities.get_lan_bridge_ifname(),
                )
                assert leaf_device.execute("tools/device/configure_gre_tunnel_gw", leaf_gre_conf_args)[0] == 0
            elif topology == "star":
                gw_gre_conf_args = self.get_command_arguments(
                    self.interfaces["backhaul_ap"].combined_args["vif_if_name"],
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
            log.info(f"WDS interface created on {self.name.upper()}: {wds_if_name}")
            # Add WDS interface to bridge
            lan_br_if_name = self.capabilities.get_lan_bridge_ifname()
            add_port_to_bridge_args = self.get_command_arguments(
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
                log.info(f"WDS interface created on {leaf_device.name.upper()}: {wds_if_name}")
                # Add WDS interface to bridge
                lan_br_if_name = leaf_device.capabilities.get_lan_bridge_ifname()
                add_port_to_bridge_args = leaf_device.get_command_arguments(
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
                log.info(f"WDS interface created on {self.name.upper()}: {wds_if_name}")
                # Add WDS interface to bridge
                lan_br_if_name = self.capabilities.get_lan_bridge_ifname()
                add_port_to_bridge_args = self.get_command_arguments(
                    lan_br_if_name,
                    wds_if_name,
                )
                assert self.execute("tools/device/add_port_to_bridge", add_port_to_bridge_args)[0] == 0

        return True

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
                self.get_log_tail_file_and_attach_to_allure()
            pass
        finally:
            self._remove_log_tail_file_remotely()
        return cmd_res

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
        log.debug(f"log_tail_command on device is: {self.log_tail_command}")
        return self.log_tail_command

    def get_log_tail_file_and_attach_to_allure(self, log_tail_file_name: PathLike[str] | None = None) -> None:
        """
        Get the log tailing file from the device and attach it to the allure report.

        Logs a warning if the action can not be performed.
        """
        if not log_tail_file_name:
            log_tail_file_name = self._get_log_tail_file_name()
        try:
            # Get file locally
            log_tail_local_path = self.device_api.get_file(log_tail_file_name, self.fut_base_dir, create_dir=False)
            allure.attach.file(log_tail_local_path, name=Path(log_tail_file_name).name)
        finally:
            # Remove file locally
            Path(log_tail_local_path).unlink(missing_ok=True)

    def _get_log_tail_file_name(self) -> str:
        """
        Get the file name for tailing the system log on the device. Stores this information as an object attribute.

        Returns:
            (str): The command for tailing the system log on the device.
        """
        if hasattr(self, "log_tail_file_name") and self.log_tail_file_name:
            return self.log_tail_file_name
        self.log_tail_file_name = f'{self.fut_dir}/{self.name}_{time.strftime("%Y%m%d-%H%M%S")}.log'
        log.debug(f"log_tail_file_name on device is: {self.log_tail_file_name}")
        return self.log_tail_file_name

    def _remove_log_tail_file_remotely(self) -> None:
        """
        Remove the log tailing file from the remote device.

        Logs a warning if the log tailing file cannot be removed.
        """
        log_tail_file_name = self._get_log_tail_file_name()
        log_tail_remove_cmd = f"[ -e {log_tail_file_name} ] && rm {log_tail_file_name}"
        try:
            cmd_res = self.device_api.run_raw(log_tail_remove_cmd, timeout=5)
            if cmd_res[0] != 0:
                log.warning(f"Encountered issue while removing log file remotely: {cmd_res[2]}")
        finally:
            if hasattr(self, "log_tail_file_name"):
                delattr(self, "log_tail_file_name")

    def _start_log_tail(self) -> None:
        """
        Start tailing system logs on the device.

        This method will create a log file and start a logging subprocess on the device in the background.
        If the log tailing processes is not executed correctly, it will only log a warning and not an exception.
        """
        log_tail_file_name = self._get_log_tail_file_name()
        log_tail_command = self._get_log_tail_command()
        # Required timeout of at least 70 seconds due to hardcoded channel set timeout of 60s
        log_tail_timeout = 70 if self.test_script_timeout <= 70 else self.test_script_timeout
        log_tail_start_cmd = f"timeout {log_tail_timeout} {log_tail_command} > {log_tail_file_name} &"
        log.debug(f"Log tail start command: '{log_tail_start_cmd}'")
        cmd_res = self.device_api.run_raw(log_tail_start_cmd, timeout=5)
        if cmd_res[0] != 0:
            log.warning(f"Encountered issue while starting log tailing process: {cmd_res[2]}")

    def _stop_log_tail(self) -> None:
        """
        Stop all log tailing processes on the device.

        If the log tailing processes are not stopped correctly, it will only log a warning.
        """
        cmd_res = self.device_api.run_raw(f"pkill {self._get_log_tail_command().split()[0]}", timeout=5)
        if cmd_res[0] != 0:
            log.warning(f"Encountered issue while stopping log tailing process: {cmd_res[2]}")

    def fut_device_setup(self, test_suite_name: str, setup_args: str = "") -> Literal[True]:
        """
        Perform the necessary device setup for FUT test case execution.

        Args:
            test_suite_name (str): Name of the test suite to be executed.
            setup_args (str): Additional setup arguments to be passed to
                the setup script.

        Returns:
            (bool): True if setup is successful.
        """
        with step(f"{self.name.upper()} setup"):
            with step(f"{test_suite_name.upper()} setup"):
                assert self.execute(f"tests/{test_suite_name}/{test_suite_name}_setup", setup_args)[0] == 0
            if self.name == "gw":
                with step("Put device into ROUTER mode"):
                    assert self.configure_device_mode(device_mode="router")
        return True

    def _add_to_logs(self, result: list[int, str, str], script: str, args: str | None = None):
        """Add script output to logs in the report instead of logging to console with e.g. log.info()."""
        logs_string = f"[{self.name}] --> {script}"
        if args:
            logs_string = f"{logs_string} {args}"
        self.device_api.log_catcher.add_to_logs(logs_string)
        exit_code = result[0]
        info = f"stdout:\n{result[1]}"
        error = "" if exit_code == self.expected_shell_result else f"ret:{exit_code}, stderr:\n{result[2]}"
        if isinstance(info, bytes):
            info = str(info)
        self.device_api.log_catcher.add_to_logs(f"{error}{info}")

    def get_bridge_type(self) -> str:
        """
        Check the device kconfig option for the networking bridge type.

        Returns:
            bridge_type (str): The networking bridge type retrieved from
                the device: 'native_bridge' or 'ovs_bridge'.
        """
        if hasattr(self, "bridge_type"):
            return self.bridge_type
        ovs_version = self.ovsdb.get(
            table="AWLAN_Node",
            select="ovs_version",
            skip_exception=True,
        )
        # The device is using Native bridge if the 'ovs_version' is not available
        self.bridge_type = "native_bridge" if "N/A" in ovs_version else "ovs_bridge"
        log.info(f"Bridge type on {self.name} is {self.bridge_type}.")
        return self.bridge_type

    def get_opensync_version(self) -> str:
        """
        Check the device AWLAN_Node table for the OPENSYNC field value.

        Returns:
            opensync_version (str): The OpenSync version on the device. Format: x.y.z.w or empty string.
        """
        if hasattr(self, "opensync_version") and self.opensync_version:
            return self.opensync_version
        self.opensync_version = self.device_api.opensync_version()
        log.info(f"OpenSync version on {self.name} is {self.opensync_version}.")
        return self.opensync_version

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
        for radio_band in radio_band_list:
            orig_radio_channels.update({radio_band: self.capabilities.get_supported_radio_channels(radio_band)})
        radio_channels = {k: v for k, v in orig_radio_channels.items() if v is not None}
        for band in radio_channels:
            channels = radio_channels[band]
            channel_in_band = str(channel) in channels or channel in channels
            matching_bands = band[:2] in remote_radio_band[:2]
            if channel_in_band and matching_bands:
                return band
        raise RuntimeError(
            f"Could not determine radio band for channel={channel} and remote_radio_band={remote_radio_band}",
        )

    def _get_region(self) -> str:
        """
        Query the device regulatory domain.

        Stores this information in the device handler.

        Raises:
            RuntimeError: If the region is invalid.

        Returns:
            (str): The regulatory domain retrieved from the device.
        """
        if hasattr(self, "regulatory_domain"):
            return self.regulatory_domain
        region = self.device_api.get_region()
        if str(region).upper() in ["US", "EU", "GB"]:
            self.regulatory_domain = f"{region}".upper()
            log.info(f"Device {self.name} regulatory_domain is set to {self.regulatory_domain}.")
        else:
            raise RuntimeError(f"Regulatory domain configured on device: {region} is not supported.")
        return self.regulatory_domain

    def get_wireless_manager_name(self) -> str:
        """
        Query the device for the name of the wireless manager.

        Stores this information in the device handler.

        Raises:
            RuntimeError: If the wireless manager name can not be determined.

        Returns:
            (str): The wireless manager name retrieved from the device. wm or owm.
        """
        if hasattr(self, "wireless_manager_name"):
            return self.wireless_manager_name
        wireless_manager_name = self.execute("tools/device/get_wireless_manager_name")
        if wireless_manager_name[0] == self.expected_shell_result:
            self.wireless_manager_name = wireless_manager_name[1].split("\n")[-1]
            log.info(f"Wireless manager name on {self.name} is {self.wireless_manager_name}.")
        else:
            raise RuntimeError(f"Unable to get wireless manager name on {self.name} device: {wireless_manager_name[2]}")
        return self.wireless_manager_name

    def get_wpa3_support(self) -> str:
        """
        Query the device for WPA3 support.

        Stores this information in the device handler.

        Raises:
            RuntimeError: If the device is not capable of WPA3.

        Returns:
            (bool): Device WPA3 support.
        """
        if hasattr(self, "wpa3_supported"):
            return self.wpa3_supported
        script = "tools/device/check_wpa3_compatibility"
        result = self.execute(script, skip_logging=True)
        self._add_to_logs(result, script)
        self.wpa3_supported = result[0] == self.expected_shell_result
        log.info(f"WPA3 is {'' if self.wpa3_supported else 'not'} supported on the device.")
        return self.wpa3_supported

    def get_kconfig(self) -> list:
        """
        Get content of the kconfig file on the device. Values are cached.

        Returns:
            (list): Content of the kconfig file on the device.
        """
        if hasattr(self, "kconfig"):
            return self.kconfig
        kconfig_local_path = self.device_api.get_file(
            Path(self.opensync_root_dir).joinpath("etc", "kconfig"),
            self.fut_base_dir,
            create_dir=False,
        )
        with open(kconfig_local_path) as kconfig:
            kconfig_content = kconfig.readlines()
        self.kconfig = [line.strip() for line in kconfig_content if "#" not in line]
        return self.kconfig

    def get_kconfig_managers(self) -> list:
        """
        Get the managers from the content of the kconfig file on the device. Values are cached.

        Returns:
            (list): Managers in the kconfig file on the device.
        """
        if hasattr(self, "kconfig_managers"):
            return self.kconfig_managers
        kconfig = self.get_kconfig()
        kconfig_managers = [
            line.removesuffix("=y").removeprefix("CONFIG_MANAGER_")
            for line in kconfig
            if line.endswith("=y") and line.startswith("CONFIG_MANAGER_")
        ]
        self.kconfig_managers = sorted({manager for manager in kconfig_managers if "_" not in manager})
        return self.kconfig_managers

    def _get_node_services_and_status(self, service: str = None) -> dict:
        """
        Return Node_Services fields service and status for a specific service or all services.

        Cached values are replaced if a specific service is provided.

        Returns:
            (dict): Service values are keys and the value is a dict with status values from the device.
        """
        where = None
        if service:
            assert isinstance(service, str)
            where = f"service=={service}"
        node_services_ovsdb = self.ovsdb.get_json_table(
            table="Node_Services",
            select=["service", "status"],
            where=where,
        )
        if not isinstance(node_services_ovsdb, list):
            node_services_ovsdb = [node_services_ovsdb]
        node_services = {item["service"]: {"status": item["status"]} for item in node_services_ovsdb}
        if hasattr(self, "node_services"):
            self.node_services = merge(self.node_services, node_services, strategy=Strategy.TYPESAFE_REPLACE)
        elif node_services:
            self.node_services = node_services
        return node_services

    def get_node_services_and_status(self) -> dict:
        """
        Return Node_Services fields service and status. Provide cached value from first function call.

        Returns:
            (dict): Service values are keys and the value is a dict with status values from the device.
        """
        if hasattr(self, "node_services"):
            return self.node_services
        self.node_services = self._get_node_services_and_status()
        return self.node_services

    def opensync_pid_retrieval(self, tracked_node_services: list = None) -> dict:
        """
        Retrieve PIDs of OpenSync related processes on the device.

        The function checks the Node_Services OVSDB table and retrieves
        their respective PIDs. By default, the method retrieves the PIDs
        of all the OpenSync related processes on the device. This can be
        overridden by specifying the processes you wish to track with the
        tracked_node_services argument.

        Args:
            tracked_node_services (list): list of node services you wish
                to take into account when performing the PID retrieval.

        Returns:
            os_proc_pids (dict): Dictionary containing OpenSync related
                processes and their respective PIDs

        """
        log.debug("Executing OpenSync PID retrieval")
        enabled_node_services = self.ovsdb.get(
            table="Node_Services",
            select="service",
            where="status==enabled",
        ).split()
        # Manually append DM since it is not present in the Node_Services table
        enabled_node_services.append("dm")
        if tracked_node_services:
            # Keep track of only those services that are present both in enabled_node_services_stdout and
            # tracked_node_services
            enabled_node_services = list(set(enabled_node_services) & set(tracked_node_services))
        enabled_node_services_list = [
            f"{self.opensync_root_dir}/bin/{node_service}" for node_service in enabled_node_services
        ]
        node_services_pid_args = self.get_command_arguments(*sorted(enabled_node_services_list))
        os_proc_names_and_pids = self.execute("tools/device/get_process_id", node_services_pid_args)[1].split()
        os_proc_dict = {proc.split(":")[0]: proc.split(":")[1] for proc in os_proc_names_and_pids}
        return os_proc_dict

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
        interface = self.VirtualInterface(self, channel, ht_mode, radio_band, encryption, interface_role, **kwargs)
        self.interfaces[interface_role] = interface
        log.info(f"Interface {interface_role} object successfully created.")

    class VirtualInterface:
        """
        VirtualInterface class represents a virtual interface in a network node.

        Attributes:
            node (NodeHandler): The NodeHandler class object.
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
            node: "NodeHandler",
            channel: int,
            ht_mode: str,
            radio_band: str,
            encryption: str,
            interface_role: str,
            **kwargs,
        ):
            self.node = node
            self.channel = channel
            self.ht_mode = ht_mode
            self.radio_band = radio_band
            self.encryption = encryption
            self.interface_role = interface_role
            self.ssid_raw = None
            self.psk_raw = None

            # Store the override keyword arguments in a dict for easier processing
            self.override_args = kwargs

            # Retrieve virtual interface name based on the selected interface role and radio band
            self.if_name = self.node.capabilities.get_ifname(freq_band=self.radio_band, iftype=self.interface_role)

            self.interface_mode = self._determine_interface_mode()
            self.radio_args = self._configure_radio_args()
            self.vif_args = self._configure_vif_args()

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
            ssid = f"{self.node.fut_configurator.base_ssid}_{interface_role}"
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
            psk = f"{self.node.fut_configurator.base_psk}_{interface_role}"
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
                "radio_if_name": phy_if_name,
                "ht_mode": self.ht_mode,
            }
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
                ValueError: If WPA3 is not compatible with the device.
                KeyError: If the encryption value is invalid.
            """
            # Perform WPA3 compatibility check
            if "WPA3" in self.encryption.upper() and not self.node.get_wpa3_support():
                raise ValueError(f"WPA3 is not compatible on the {self.node.name} device!")

            match self.encryption.upper():
                case "WPA2":
                    wpa_key_mgmt = "wpa2-psk"
                case "WPA3":
                    wpa_key_mgmt = "sae"
                case "WPA3-TRANSITION":
                    # fmt: off
                    wpa_key_mgmt = ["\"sae\"", "\"wpa2-psk\""]
                    # fmt: on
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
                subnet = f"169.24{self.vif_args['vif_radio_idx']}.{randrange(1, 253)}"
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
                "network_if_name": self.if_name,
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
            sanitized_combined_args = self.node.get_command_arguments(combined_args_list)

            return sanitized_combined_args

        def vif_reset(self) -> None:
            """
            Reset the virtual interface on the device.

            Raises:
                AssertionError: If the command to reset the VIF fails.
            """
            assert self.node.execute("tools/device/vif_reset", self.if_name)[0] == self.node.expected_shell_result

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
