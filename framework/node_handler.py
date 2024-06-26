import time
from pathlib import Path
from random import randrange

import allure

from framework.device_handler import DeviceHandler
from framework.fut_configurator import Config
from framework.lib.fut_lib import step
from lib_testbed.generic.util.logger import log


class NodeHandler(DeviceHandler):
    def __init__(self, name):
        log.debug("Entered NodeHandler class")
        super().__init__(name)
        self.expected_shell_result = 0
        self.regulatory_domain = self._get_region()
        self.supported_radio_bands = self.capabilities.get_supported_bands()
        self.opensync_root_dir = self.capabilities.get_opensync_rootdir()
        self._ap_args = None
        self._sta_args = None

    @property
    def ap_args(self):
        """The access point (AP) arguments property."""
        return self._ap_args

    @ap_args.setter
    def ap_args(self, args: dict):
        """
        AP arguments.

        Args (passed as a dictionary):
            channel (int): Radio channel. Defaults to 1.
            ht_mode (str): Radio channel bandwidth. Defaults to HT20,
                representing 20MHz.
            radio_band (str): Radio band. Defaults to 24g, representing
                the 2.4GHz radio band.
            ap_ip_assign_scheme (str): IP assign scheme.
            ap_mtu (int): Maximum transmission unit.
            ap_nat (str): Enable or disable NAT.
            ap_netmask (str): Netmask
            ap_subnet (str): Subnet
            bridge (bool): Add bridge name to AP configuration.
            channel_mode (str): Channel mode.
            enabled (str): Enable or disable AP.
            encryption (str): Encryption method used.
            interface_type (str): VIF type.
            wpa_psk (None) (str) or (list): PSK or list of keys for
                multi_psk.
            reset_vif (bool): Reset all virtual interfaces.
            ssid (str): SSID.
            ssid_broadcast (str): Enable or disable SSID broadcast.
            vif_name (str): Virtual interface name.
            vif_radio_idx (str): Radio index of the virtual interface.
            wifi_security_type (str): WiFi security type - 'legacy' or
                'wpa'.

        Returns:
            (dict): VAP arguments.
        """
        ap_arguments = {
            "channel": 1,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "ap_broadcast_n": None,
            "ap_inet_addr_n": None,
            "ap_ip_assign_scheme": None,
            "ap_mtu": None,
            "ap_nat": "false",
            "ap_netmask": None,
            "ap_subnet": None,
            "bridge": None,
            "channel_mode": "manual",
            "enabled": "true",
            "mac_list_type": None,
            "mac_list": None,
            "encryption": "WPA2",
            "interface_type": "home_ap",
            "wpa_psk": self.fut_configurator.base_psk,
            "reset_vif": False,
            "ssid": self.fut_configurator.base_ssid,
            "ssid_broadcast": "enabled",
            "vif_name": None,
            "vif_radio_idx": None,
            "wifi_security_type": "wpa",
        }

        for key in args:
            if key not in ap_arguments:
                raise RuntimeWarning("The provided arguments contain invalid key-value pairs.")

        ap_arguments.update(args)

        ap_arguments.update(
            {
                "vif_name": (
                    self.capabilities.get_ifname(
                        freq_band=ap_arguments["radio_band"],
                        iftype=ap_arguments.get("interface_type"),
                    )
                    if not ap_arguments.get("vif_name")
                    else ap_arguments.get("vif_name")
                ),
            },
        )
        ap_arguments.update(
            {
                "vif_radio_idx": (
                    self.capabilities.get_iftype_vif_radio_idx(iftype=ap_arguments.get("interface_type"))
                    if not ap_arguments.get("vif_radio_idx")
                    else ap_arguments.get("vif_radio_idx")
                ),
            },
        )
        ap_arguments.update(
            {
                "ap_ip_assign_scheme": "none" if ap_arguments.get("interface_type") == "home_ap" else "static",
            },
        )
        ap_arguments.update(
            {
                "bridge": True if ap_arguments.get("interface_type") == "home_ap" else False,
            },
        )

        ap_arguments = Config(**ap_arguments)

        self._ap_args = ap_arguments

    @ap_args.deleter
    def ap_args(self):
        del self._ap_args

    @property
    def sta_args(self):
        """The station (STA) interface arguments property."""
        return self._sta_args

    @sta_args.setter
    def sta_args(self, args: dict):
        """
        STA arguments.

        Args (passed as a dictionary):
            vif_name (str): Interface name.
            parent (str): Parent BSSID to which the STA needs to be
                connected. If empty, any BSSID is allowed to match.
            wpa_oftags (str): WPA passwords' oftags.
            wpa_key_mgmt (str): Configure the Wi-Fi security mode.
            wpa (bool): Enables support for WPA.
            wpa_psk (None) (str) or (list): List of passwords used by
                WPA.
            ssid (str): Interface SSID.
            onboard_type (str): Onboard type: GRE, no-GRE.
            clear_wcc (bool): Remove ALL entries in the
                Wifi_Credentials_Config OVSDB table.
            wait_ip (bool): Wait for inet_addr field in the
                Wifi_Inet_State OVSDB table based on the
                interface name to be populated.
            wifi_security_type (str): Wi-Fi security type: "legacy" or
                "wpa".
            encryption (str): Encryption type.
            reset_vif (bool): Reset all virtual interfaces.

        Returns:
            (dict): STA arguments
        """
        sta_arguments = {
            "vif_name": None,
            "parent": None,
            "radio_band": "24g",
            "wpa_psk": self.fut_configurator.base_psk,
            "ssid": self.fut_configurator.base_ssid,
            "onboard_type": "gre",
            "clear_wcc": False,
            "wait_ip": False,
            "wifi_security_type": "wpa",
            "encryption": "WPA2",
            "interface_type": "backhaul_sta",
            "reset_vif": False,
        }

        for key in args:
            if key not in sta_arguments:
                raise RuntimeWarning("The provided arguments contain invalid key-value pairs.")

        sta_arguments.update(args)

        sta_arguments.update(
            {
                "vif_name": (
                    self.capabilities.get_ifname(
                        freq_band=sta_arguments["radio_band"],
                        iftype=sta_arguments.get("interface_type"),
                    )
                    if not sta_arguments.get("vif_name")
                    else sta_arguments.get("vif_name")
                ),
            },
        )

        sta_arguments = Config(**sta_arguments)

        self._sta_args = sta_arguments

    @sta_args.deleter
    def sta_args(self):
        del self._sta_args

    def configure_device_mode(self, device_mode):
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
            raise RuntimeError(f"Invalid device mode provided: {device_mode}.")

        return True

    def configure_network_parameters(self, return_as_dict=False):
        """
        Configure network parameters.

        Args:
            return_as_dict (bool): Determine whether to return the
                configured parameters as a Python dictionary.

        Returns:
            (list/dict): List or dict of network configuration parameters.
        """
        ap_mtu = self.capabilities.get_bhaul_mtu() if not self.ap_args.ap_mtu else self.ap_args.ap_mtu

        network_parameters = [
            "-inet_enabled true",
            f"-inet_if_name {self.ap_args.vif_name}",
            f"-ip_assign_scheme {self.ap_args.ap_ip_assign_scheme}",
            f"-NAT {self.ap_args.ap_nat}",
            f"-mtu {ap_mtu}",
            "-if_type vif",
            "-network true",
        ]

        if self.ap_args.interface_type != "home_ap":
            ap_broadcast_n = "255" if not self.ap_args.ap_broadcast_n else self.ap_args.ap_broadcast_n
            ap_inet_addr_n = "129" if not self.ap_args.ap_inet_addr_n else self.ap_args.ap_inet_addr_n
            ap_subnet = (
                f"169.24{self.ap_args.vif_radio_idx}.{randrange(1, 253)}"
                if not self.ap_args.ap_subnet
                else self.ap_args.ap_subnet
            )
            ap_netmask = "255.255.255.128" if not self.ap_args.ap_netmask else self.ap_args.ap_netmask

            network_parameters += [
                f"-broadcast_n {ap_broadcast_n}",
                f"-inet_addr_n {ap_inet_addr_n}",
                f"-subnet {ap_subnet}",
                f"-netmask {ap_netmask}",
            ]

        if return_as_dict:
            network_parameters = {
                "inet_if_name": self.ap_args.vif_name,
                "broadcast_n": ap_broadcast_n,
                "inet_addr_n": ap_inet_addr_n,
                "subnet": ap_subnet,
                "netmask": self.ap_args.vif_name,
                "ip_assign_scheme": self.ap_args.ap_ip_assign_scheme,
                "NAT": self.ap_args.ap_nat,
                "mtu": ap_mtu,
                "if_type": "vif",
                "network": "true",
            }

        return network_parameters

    def configure_radio_vif_and_network(self):
        """
        Configure AP virtual interface on the device.

        This also includes the network configuration.

        Returns:
            (bool): True if both the AP virtual interface and the
                network are configured, False otherwise.
        """
        ap_radio_vif_args_base = self.configure_radio_vif_interface(return_as_dict=False)
        ap_radio_vif_args_base += self.configure_network_parameters(return_as_dict=False)
        ap_radio_vif_args = self.get_command_arguments(*ap_radio_vif_args_base)

        if self.ap_args.reset_vif:
            assert self.execute("tools/device/vif_reset")[0] == self.expected_shell_result

        assert (
            self.execute_with_logging("tools/device/configure_ap_interface", ap_radio_vif_args)[0]
            == self.expected_shell_result
        )

        return True

    def configure_radio_vif_interface(self, return_as_dict=False):
        """
        Configure AP interface on the device.

        Args:
            return_as_dict (bool): Determine whether to return the
                configured parameters as a Python dictionary.

        Returns:
            (list/dict): List or dict of AP configuration parameters.
        """
        # Set interface mode
        mode = "ap"

        # Get physical radio name
        phy_radio_name = self.capabilities.get_phy_radio_ifname(freq_band=self.ap_args.radio_band)

        ssid = self.ap_args.ssid

        if self.ap_args.interface_type == "backhaul_ap":
            ssid_broadcast = "disabled"
        else:
            ssid_broadcast = self.ap_args.ssid_broadcast

        ap_radio_vif_args = [
            f"-if_name {phy_radio_name}",
            f"-vif_if_name {self.ap_args.vif_name}",
            f"-vif_radio_idx {self.ap_args.vif_radio_idx}",
            f"-channel {self.ap_args.channel}",
            f"-channel_mode {self.ap_args.channel_mode}",
            f"-ht_mode {self.ap_args.ht_mode}",
            f"-enabled {self.ap_args.enabled}",
            f"-mode {mode}",
            f"-ssid '{ssid}'",
            f"-ssid_broadcast {ssid_broadcast}",
            f"-wifi_security_type {self.ap_args.wifi_security_type}",
        ]

        if self.ap_args.mac_list_type is not None:
            ap_radio_vif_args.append(
                f"-mac_list_type {self.ap_args.mac_list_type}",
            )
            mac_list = f'\'["set",["{self.ap_args.mac_list}"]]\''
            ap_radio_vif_args.append(
                f"-mac_list {mac_list}",
            )

        dut_if_lan_br_name = self.capabilities.get_lan_bridge_ifname()
        if self.ap_args.bridge and self.ap_args.bridge is True:
            bridge = dut_if_lan_br_name
            ap_radio_vif_args.append(
                f"-bridge {bridge}",
            )
        elif isinstance(self.ap_args.bridge, str):
            bridge = self.ap_args.bridge
            ap_radio_vif_args.append(
                f"-bridge {bridge}",
            )
        else:
            bridge = ""

        ap_radio_vif_args += self.configure_wifi_security(device_mode=mode, return_as_dict=return_as_dict)

        if return_as_dict:
            ap_radio_vif_args = {
                "if_name": phy_radio_name,
                "vif_if_name": self.ap_args.vif_name,
                "vif_radio_idx": self.ap_args.vif_radio_idx,
                "channel": self.ap_args.channel,
                "channel_mode": self.ap_args.channel_mode,
                "ht_mode": self.ap_args.ht_mode,
                "enabled": self.ap_args.enabled,
                "mode": mode,
                "ssid": ssid,
                "ssid_broadcast": ssid_broadcast,
                "wifi_security_type": self.ap_args.wifi_security_type,
                "bridge": bridge,
            }

            ap_radio_vif_args = {
                **ap_radio_vif_args,
                **self.configure_wifi_security(device_mode=mode, return_as_dict=return_as_dict),
            }

        return ap_radio_vif_args

    def configure_sta_interface(self):
        """
        Configure STA interface on the device.

        Returns:
            (bool): True if the STA interface is configured.
        """
        sta_args_base = [
            f"-if_name {self.sta_args.vif_name}",
            f"-ssid '{self.sta_args.ssid}'",
            f"-onboard_type {self.sta_args.onboard_type}",
            f"-wifi_security_type {self.sta_args.wifi_security_type}",
        ]

        if self.sta_args.parent is not None:
            sta_args_base += [
                f"-parent {self.sta_args.parent}",
            ]

        if self.sta_args.clear_wcc:
            sta_args_base += [
                "-clear_wcc",
            ]

        if self.sta_args.wait_ip:
            sta_args_base += [
                "-wait_ip",
            ]

        sta_args_base += self.configure_wifi_security(device_mode="sta")
        sta_args = self.get_command_arguments(*sta_args_base)

        if self.sta_args.reset_vif:
            assert self.execute("tools/device/vif_reset")[0] == self.expected_shell_result

        assert (
            self.execute_with_logging("tools/device/configure_sta_interface", sta_args)[0] == self.expected_shell_result
        )

        return True

    def configure_wifi_security(self, device_mode="ap", return_as_dict=False):
        """
        Configure Wi-Fi security arguments.

        Configures arguments with 'security' field if wifi_security_type
        is 'legacy' or with 'wpa' fields if wifi_security_type is 'wpa'.

        Args:
            device_mode (str): Device mode. Supported options: "ap" or
                "sta".
            return_as_dict (bool): Determine whether to return the
                configured parameters as a Python dictionary.

        Raises:
            RuntimeError: If the provided security arguments (or their
                combination) are not valid.

        Returns:
            (list/dict): List or dict of Wi-Fi security configuration
                parameters.
        """
        if device_mode == "ap":
            security_args = self.ap_args
        else:
            security_args = self.sta_args

        try:
            if security_args.encryption.upper() == "WPA2":
                wpa_key = "wpa2-psk"
                wpa_key_mgmt = "WPA-PSK"
            elif security_args.encryption.upper() == "WPA3":
                wpa_key = "sae"
                wpa_key_mgmt = "SAE"
            elif security_args.encryption.upper() == "WPA3-TRANSITION":
                wpa_key = '\'["set",["sae","wpa2-psk"]]\''
                wpa_key_mgmt = ["WPA-PSK", "SAE"]
            elif security_args.encryption.upper() == "OPEN":
                wpa_key_mgmt = "NONE"
        except Exception:
            raise RuntimeError(
                f"Invalid encryption type {security_args.encryption} provided. Supported [open, WPA2, WPA3-personal, WPA3-transition]",
            )

        if security_args.wpa_psk:
            if isinstance(security_args.wpa_psk, str):
                psk_list = [security_args.wpa_psk]
            elif isinstance(security_args.wpa_psk, list):
                psk_list = security_args.wpa_psk
            else:
                raise RuntimeError(
                    f"Invalid psk value provided: {security_args.wpa_psk} provided. Supported types are str or list",
                )

        if security_args.encryption.upper() == "WPA3":
            wpa3_supported = self.execute("tools/device/check_wpa3_compatibility")
            if wpa3_supported[0] != 0:
                raise RuntimeError("WPA3 is not compatible on device!")

        if security_args.wifi_security_type == "legacy":
            psk_list_str = ",".join([f'["key","{key}"]' for key in psk_list])
            security = (
                "'[\"map\",[]]'"
                if security_args.encryption.upper() == "OPEN"
                else f'\'["map",[["encryption","{wpa_key.upper()}"],{psk_list_str}]]\''
            )
            wifi_security_args = [
                f"-security {security}",
            ]
            if return_as_dict:
                wifi_security_args = {
                    "security": security,
                }
        elif security_args.wifi_security_type == "wpa":
            wpa_supported = self.execute(
                "tools/device/ovsdb/check_ovsdb_table_field_exists",
                self.get_command_arguments("Wifi_VIF_Config", "wpa"),
            )
            if wpa_supported[0] != 0:
                raise RuntimeError(f"'wpa' fields are not supported on the '{self.name}' device!")

            if security_args.encryption.upper() == "OPEN":
                wifi_security_args = [
                    '-wpa "false"',
                ]
                if return_as_dict:
                    wifi_security_args = {
                        "wpa": "false",
                        "key_mgmt_mapping": wpa_key_mgmt,
                    }
            else:
                wpa_psk_list_str = ",".join(
                    [f'["key--{index}","{key}"]' for index, key in enumerate(psk_list, start=1)],
                )
                oftag = security_args.interface_type.rsplit("_", 1)[0]
                wpa_oftag_list_str = ",".join(
                    [f'["key--{index}","{oftag}--{index}"]' for index, key in enumerate(psk_list, start=1)],
                )
                wpa_psks = f"'[\"map\",[{wpa_psk_list_str}]]'"
                wpa_oftags = f"'[\"map\",[{wpa_oftag_list_str}]]'"
                wifi_security_args = [
                    '-wpa "true"',
                    f"-wpa_psks {wpa_psks}",
                    f"-wpa_oftags {wpa_oftags}",
                    f"-wpa_key_mgmt {wpa_key}",
                ]
                if return_as_dict:
                    wifi_security_args = {
                        "wpa": "true",
                        "wpa_psks": wpa_psks,
                        "wpa_oftags": wpa_oftags,
                        "wpa_key_mgmt": wpa_key,
                        "key_mgmt_mapping": wpa_key_mgmt,
                    }
        else:
            raise RuntimeError("Incorrect 'wifi_security_type' option passed, supported: 'legacy', 'wpa'")

        return wifi_security_args

    def create_and_configure_bhaul_connection_gw_leaf(
        self,
        channel,
        leaf_device: "NodeHandler",
        gw_radio_band,
        leaf_radio_band,
        ht_mode,
        wifi_security_type,
        encryption,
        skip_gre=False,
    ):
        """
        Create and configure a backhaul connection.

        Args:
            channel (int): Radio channel.
            leaf_device (object): LEAF device object.
            gw_radio_band (str): Gateway radio band.
            leaf_radio_band (str): Leaf radio band.
            ht_mode (str): HT mode.
            wifi_security_type (str): Type of security. Supported options:
                'legacy' or 'wpa'.
            encryption (str): Encryption type.
            skip_gre (bool) : Skips configuration of GRE interface on the GW
                device for LEAF connection.

        Returns:
            (bool): True if backhaul connection is configured correctly.
        """
        leaf_phy_radio_if_name = leaf_device.capabilities.get_phy_radio_ifname(freq_band=leaf_radio_band)

        leaf_device_physical_wifi_mac = leaf_device.device_api.iface.get_physical_wifi_mac(
            ifname=leaf_phy_radio_if_name,
        )

        gw_ap_vif_args = {
            "channel": channel,
            "ht_mode": ht_mode,
            "radio_band": gw_radio_band,
            "interface_type": "backhaul_ap",
            "wifi_security_type": wifi_security_type,
            "encryption": encryption,
            "mac_list_type": "whitelist",
            "mac_list": leaf_device_physical_wifi_mac,
            "reset_vif": True,
        }

        self.ap_args = gw_ap_vif_args

        leaf_sta_vif_args = {
            "radio_band": leaf_radio_band,
            "interface_type": "backhaul_sta",
            "wifi_security_type": wifi_security_type,
            "encryption": encryption,
            "clear_wcc": True,
            "wait_ip": True,
            "reset_vif": True,
        }

        leaf_device.sta_args = leaf_sta_vif_args

        self.configure_radio_vif_and_network()
        leaf_device.configure_sta_interface()

        gw_gre_conf_args = self.get_command_arguments(
            self.ap_args.vif_name,
            leaf_device_physical_wifi_mac,
            self.capabilities.get_uplink_gre_mtu(),
            self.capabilities.get_lan_bridge_ifname(),
        )

        if not skip_gre:
            assert self.execute("tools/device/configure_gre_tunnel_gw", gw_gre_conf_args)[0] == 0

        return True

    def execute_with_logging(self, path, args="", as_sudo=False, **kwargs):
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

    def _get_log_tail_command(self):
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
            log.warning(f"Invalid logread command {logread_command}, could not determine log_tail_command.")
        log.debug(f"log_tail_command on device is: {self.log_tail_command}")
        return self.log_tail_command

    def get_log_tail_file_and_attach_to_allure(self, log_tail_file_name=None):
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
        except Exception as e:
            log.warning(f"Failed to attach log tailing file to the Allure report: {e}")
        finally:
            # Remove file locally
            Path(log_tail_local_path).unlink(missing_ok=True)

    def _get_log_tail_file_name(self):
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

    def _remove_log_tail_file_remotely(self):
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

    def _start_log_tail(self):
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

    def _stop_log_tail(self):
        """
        Stop all log tailing processes on the device.

        If the log tailing processes are not stopped correctly, it will only log a warning.
        """
        cmd_res = self.device_api.run_raw(f"pkill {self._get_log_tail_command().split()[0]}", timeout=5)
        if cmd_res[0] != 0:
            log.warning(f"Encountered issue while stopping log tailing process: {cmd_res[2]}")

    def fut_device_setup(self, test_suite_name: str, setup_args=""):
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

    def get_bridge_type(self):
        """
        Check the device kconfig option for the networking bridge type.

        Returns:
            bridge_type (str): The networking bridge type retrieved from
                the device: 'native_bridge' or 'ovs_bridge'.
        """
        if hasattr(self, "bridge_type"):
            return self.bridge_type

        bridge_type = "ovs_bridge"

        try:
            check_kconfig_native_bridge_args = self.get_command_arguments("CONFIG_TARGET_USE_NATIVE_BRIDGE", "y")
            if (
                self.execute("tools/device/check_kconfig_option", check_kconfig_native_bridge_args)[0]
                == self.expected_shell_result
            ):
                bridge_type = "native_bridge"
        except Exception as e:
            log.warning(f"Failed to retrieve bridge type: {e}")
        self.bridge_type = bridge_type

        return bridge_type

    def get_radio_band_from_channel(self, channel):
        """
        Return the radio band of the device.

        The radio band is based on the provided channel and radio
        channels lists for interfaces read from the device capabilities.

        Args:
            channel (int): Wi-Fi channel.

        Raises:
            RuntimeError: If the radio band could not be determined.

        Returns:
            (str): Radio band of the device.
        """
        radio_channels = self.capabilities.get_all_supported_channels()

        for band in radio_channels:
            channels = radio_channels[band]
            if channels is not None and (str(channel) in channels or channel in channels):
                return band
            else:
                raise RuntimeError(
                    f"Could not determine radio_band_from channel. Channel {channel} is not in the model capabilities file.",
                )

    def get_radio_band_from_remote_channel_and_band(self, channel, remote_radio_band):
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

        for radio_band in ["24g", "5g", "5gl", "5gu", "6g"]:
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

    def _get_region(self):
        """
        Query the device regulatory domain.

        Stores this information in the device handler.

        Raises:
            RuntimeError: If the region is invalid.

        Returns:
            (str): The regulatory domain retrieved from the device.
        """
        try:
            reg = self.device_api.get_region()
            if str(reg).upper() in ["US", "EU", "GB"]:
                self.regulatory_domain = f"{reg}".upper()
                log.info(f"Device {self.name} regulatory_domain is set to {self.regulatory_domain}")
            else:
                raise RuntimeError(f"Invalid region on device: {reg}")
        except Exception as e:
            log.warning(f"Failed to retrieve device region: {e}")

        return self.regulatory_domain

    def get_wireless_manager_name(self):
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
        enabled_node_services_args = self.get_command_arguments("Node_Services", "service", "-w", "status", "enabled")
        enabled_node_services = self.execute(
            "tools/device/ovsdb/get_ovsdb_entry_value",
            enabled_node_services_args,
        )[1].split()
        # Manually append DM since it is not present in the Node_Services table
        enabled_node_services.append("dm")
        if tracked_node_services:
            # Keep track of only those services that are present both in enabled_node_services_stdout and tracked_node_services
            enabled_node_services = list(set(enabled_node_services) & set(tracked_node_services))
        enabled_node_services_list = [
            f"{self.opensync_root_dir}/bin/{node_service}" for node_service in enabled_node_services
        ]
        node_services_pid_args = self.get_command_arguments(*sorted(enabled_node_services_list))
        os_proc_names_and_pids = self.execute("tools/device/get_process_id", node_services_pid_args)[1].split()
        os_proc_dict = {proc.split(":")[0]: proc.split(":")[1] for proc in os_proc_names_and_pids}
        return os_proc_dict
