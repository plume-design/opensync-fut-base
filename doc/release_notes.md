# FUT Release Notes

Welcome to OpenSync Functional Unit Testing (FUT) release notes. See what has changed with the latest release.

## Release FUT-2.2

This [version](../.version) of FUT supports the following OpenSync releases:

- 5.6.0.0
- 5.4.0.0
- 5.2.0.0

### New Features

FUT test results should have `100%` pass rate for models with FW images that contain no bugs. Any bugs or issues within
the framework or test cases are either fixed or the test case is removed.

FUT now has support for devices using `MediaTek` chips.

A command line tool `result_post_processing.py` was introduced to process test results after the test run is complete.
The purpose of this tool is to take the provided reference test run (`Pytest`) results or (`Allure`) report and modify
the current test results (not report) based on the pass of fail status of the reference test run.

A command line tool `allure_parser.py` was introduced to process the (`Allure`) reports of two test runs. The purpose of
this tool is to ease the comparison of reports when there are many test cases that take a lot of time to compare
manually.

The `fsm_configure_test_dpi_redirect_action` test case was removed. The design is outdated and the test execution is no
longer reliable on newer versions of OpenSync, making it irrelevant for FUT testing.

FUT test cases are not relying on parsing logs if it is at all possible to perform test steps in another way. This makes
tests more reliable across all device models and across several OpenSync versions.

The `wm2_set_radio_tx_power` and `wm2_set_radio_tx_power_neg` test cases were removed from FUT. The underlying features
are not mandatory and the tests were often flaky on several models.

A GRE tunnel configuration test, named `wm2_verify_gre_tunnel_gw_leaf`, was added to the WM2 test suite.

The default path to the `upnp_server.py` script on client devices was changed from `/home/plume/upnp` to `/tools/upnp`.
A fallback procedure that maintains backward compatibility was implemented.

The `wm2_set_bcn_int` test case was simplified by removing the AP configuration process from the test shell script. The
AP configuration is now performed by a common method from the `NodeHandler` class and the method is only executed once
per radio band.

A new mechanism was added to the FUT framework, which tracks the PID of OpenSync managers on the `gw` device. In case of
any unexpected crashes, restarts or PID changes for any reason, the test case is either failed (non strict execution) or
the test execution is stopped (strict execution). The OpenSync restart detection is strict by default, but the flag
`--disable_strict_process_restart_detection` can be added to the test execution command to make it non strict.

The rules for acceptable model strings have been updated. There is a regular expression in effect that checks acceptable
characters, which include alphanumerical characters hyphen and underscore.

Added the ability to execute OpenSync Unit Tests with the FUT framework.

An SSH availability check was added to the FUT setup procedure in order to eliminate errors due to device issues. The
`wait_for_host_ssh.py` script now accepts devices, for which to perform an SSH check, as an argument.

Test reports now contain environment variables and testbed properties like device version and model, and release version
information.

The transfer of FUT files to target devices was simplified by making use of the `put_dir()` method from the
`lib_testbed` common library.

In order to ease debugging in the case of potential issues, default encryption values in the tests themselves and the
test case input files were removed. The generation of the encryption parameter is now the responsibility of the test
case configuration generators.

The `wpa_psks` and `wpa_oftags` field formats were adjusted to more closely follow the format pushed by cloud services.

The chain mask value retrieval on QCA platforms was enhanced and made more robust by issuing two different commands and
inferring the correct value.

A link to the `doc/release_notes.md` document was added to the `README.md` file.

### Fixed Bugs

Loading of the `example.yaml` location file is no longer mandatory when using the `pset` tool. The presence of the
`miscs` directory when executing FUT tests is also no longer necessary.

The OpenSync functionality under test of the test case `wm2_verify_sta_send_csa` has changed, requiring a complete
rework. The test case was rewritten as `wm2_verify_leaf_channel_change`. It no longer relies on log message parsing and
verifies whether the `leaf` device switched the channel after the `gw` performed a channel change. The packet loss
during this switch is analyzed. It is not acceptable to lose any packets.

The `IP_Port_Forward` table was deprecated with OpenSync 5.6. and the `Netfilter` table is now used to specify *IP
packet filter rules*. To keep backward compatibility, you are able to explicitly request which table is used by the test
case to achieve port forwarding for example. The `Netfilter` table is used by default.

The `Dockerfile.server` was updated to use **Python 3.12** to fix compatibility issues.

The `kconfig` option used for disabling **CM fatal state** was changed from `TARGET_PATH_DISABLE_FATAL_STATE` to
`CONFIG_TARGET_PATH_DISABLE_FATAL_STATE`. This change prevents `leaf` device reboots after terminating backhaul
connections.

Unnecessary test configurations for the `wm2_pre_cac_channel_change_validation` test case were removed and the
formatting of the test arguments was fixed.

Unnecessary test configurations for the `wm2_pre_cac_ht_mode_change_validation` test case were removed and the
formatting of the test arguments was fixed.

The `wm2_leaf_ht_mode_change` test case procedure now no longer requires the switching of `gw` and `leaf` device roles
with regards to the network switch.

The AP network configuration parameters were adjusted to take the AP interface type into account. If the interface is a
*home AP*, a static IP is not assigned to it.

The `nm2_set_upnp_mode.sh` script was reworked to only check if the correct parameters have been applied and avoid any
additional manipulation of the parameters.

The redundant `nm2_verify_router_mode.sh` script was removed.

The `wm2_set_ht_mode` test case has been simplified. The `gw` AP is now only configured once per radio band and the
`wm2_set_ht_mode.sh` script only updates the value of the *HT mode* in the `Wifi_Radio_Config` table instead of also
handling the configuration of the `gw` AP. Usage of class variables in the `WM2` test suite was also fixed.

Fixed the test case `wm2_set_ht_mode_neg` by correctly determining which wireless manager is present on the device.
There were issues when the `check_kconfig_option()` function was called by other functions due to its `grep` output. The
`grep` output would get appended to the actual values that the function was supposed to return. This was resolved by
suppressing the output of `grep` in the function. The retrieval of the wireless manager has been moved to a function in
`unit_lib.sh`.

Fixed the test case `wm2_set_channel_neg` by correctly determining which wireless manager is present on the device.

The `gw` AP configuration procedure in the `wm2_set_radio_tx_chainmask` test case was moved to a different step. A
cleanup procedure was added to the shell script that reverts the TX chainmask values back to their default pre-test
values.

The test case `wm2_set_ssid` now correctly loads all `SSID` parameters from `Python` into `shell`. The issue with
escaping special characters and whitespace was fixed.

The broken `wm2_leaf_ht_mode_change` test case, which caused failures in subsequent test cases, was removed. All
topology change test cases were enhanced by allowing the nodes some time to report associated clients instead of
checking immediately after changing the STA parent.

Adjusted the backhaul network configuration procedure. The `gw` device now waits for the `Wifi_Associated_Clients` table
to become populated with the `leaf` node MAC address, instead of checking once and failing if empty. This allows for
some time before association.

The `SSID` creation procedure in the `wm2_wifi_security_mix_on_multiple_aps` test case was changed to ensure that the
result does not exceed the 32 byte limit.

The client connectivity check in the test case `othr_wifi_disabled_after_removing_ap` was adjusted and an unnecessary
client reboot in the test case cleanup was removed.

The FUT framework now supports the execution of FUT shell scripts **locally**. The
`onbrd_verify_dut_client_certificate_file_on_server` test case was reworked to execute locally instead of the testbed
server.

The test case `othr_verify_eth_client_connection` procedure was fixed so that adding the interface port into the bridge
is executed at the correct time.

The retrieval of the STA interface names in the `othr_verify_vif_iface_wifi_master_state` test case was corrected.

Test case `pm_trigger_cloud_logpull` procedure is now fixed. An additional test parameter was added to make the
procedure more robust on all device models.

Fixed the failing test cases `dm_verify_enable_node_services` and `dm_verify_node_services`.

The order of merging values when unpacking dictionaries in `DefaultGen.py` was corrected in order to prevent default
values from being overwritten. This fixes test cases `wm2_connect_wpa3_client` and `wm2_connect_wpa3_leaf`.

The OpenSync restart procedure in the `LTEM` test suite setup was unnecessary and was removed.

The switch tool no longer fails when using the `all` port specifier with the `info` and `status` commands. The command
were successful, but the `switch` tool misinterpreted the results and reported an error. This is now fixed and the
correct exit code `0` is returned if individual commands for all ports succeed.

Testing the `UM` suite on reference boards was disabled since the firmware upgrade procedure is highly vendor specific.

Fixed two errors in the `user_manual.md` regarding file paths in the `Adding support for your own device model` section.

`Allure` reports now include device system logs as attachments to failed test steps, where requested by the framework.
This increases the ability to debug failures from inspecting the report alone.

A cleanup procedure was added to the `onbrd_verify_client_tls_connection.sh` script. The cleanup procedure restores the
original `ca.pem` file on the device after the test is finished.

Backhaul AP interfaces are now used as inputs in the `nm2_enable_disable_iface_network` test case.

The `um_set_invalid_firmware_pass` test case was adjusted to work on models that do not distinguish between image check
and flash write errors.

The `MTU` value used for `nm2_set_mtu` test case is now set to **1500**.

The client reboot in the `othr_add_client_freeze` test cleanup procedure was removed in order to avoid erasing the
`/tmp` directory on the device.

Incorrect combinations of *channel* and *channel width* were removed from the `wm2_ht_mode_and_channel_iteration` test
case inputs.

The order of test steps in the `nm2_set_upnp_mode` was changed. This was done in order to ensure that the `gw` is in
router mode before attempting to retrieve the LAN IP address. The fix for the `nm2_set_upnp_mode` test also required the
insertion of additional `Netfilter` OVSDB table entries, which reference the `MINIUPNPD` chain in *IP packet filter
rules*.

The OVSDB table used for channel switch validation in the `wm2_verify_leaf_channel_change` test case was changed from
`Wifi_Radio_Config` to `Wifi_Radio_State`.

Backhaul connectivity issues on the 6 GHz radio band in the test case `wm2_verify_leaf_channel_change` were fixed by
lowering TX power on `leaf` devices.

An AP configuration issue was corrected in the test case `wm2_verify_leaf_channel_change`. The existing VIF configs in
the `Wifi_Radio_Config` table were overridden unnecessarily.

The handling of keyword arguments in the `execute()` method of the `NodeHandler` class was adjusted to avoid issues that
stem from passing incorrect keyword arguments to the `get_remote_test_command()` method.

The operation in the `ovsdb-client` `transaction()` command was changed from `update()` to `mutate()` in order to avoid
overriding the existing values in the `vif_configs` field of the `Wifi_Radio_Config` OVSDB table.

The test case `pm_trigger_cloud_logpull` procedure was enhanced to eliminate excessive wait times when the `logpull`
procedure was not triggered or when system logs did not log this event.

### Common Test Bed Library

Recover a broken SSH connection to a testbed device before retrying a failing command.

Fixed an issue with non-zero exit code of the switch tool for commands with several interfaces.

Fixed the shebang of several testbed tools, a system may have bash in a different location than `/bin/bash`.

Device credentials from the capabilities configuration file are used for remote hosts if unspecified.

Striped the `stdout` string from the device of trailing newlines and spaces.

Improve typing, type hinging and type checking in `Python` code.

The framework cache directory is mounted to `$HOME/.pyenv` to prevent picking up the Python version from the local
`pyenv` environment instead of the `Docker` interpreter.

Move interface name overrides to separate method. This change enables the usage of the
`override_version_specific_ifnames` method. The default behavior remains unchanged.

Create parents of the temporary directory in the artifactory reader tool if they do not exist.

Enhanced `Python` error checking by introducing a list of possible radio bands.

Use the directory `.framework_cache` as a temporary directory to simplify cleanup procedures.

Gracefully exit the `rpower` tool when the PDU device is not accessible.

Update the command used to get the process id from the device reliably. Some models do not support flags for the `ps`
tool.

Update port-forwarding rules between WAN ports.

Use a `CACHE_DIR` for the client tool for storing client firmware images for upgrade purposes.

Force legacy SCP protocol instead of new SFTP when executing `get_file()` and `put_file()` in `parallelssh`.

Record and display `exit code`, `stdout` and `stderr` from all devices, if an action is performed on several at once.

Made the `pset` tool more modular by removing the loading of `example.yaml` file.

Made code resistant to a missing `miscs` directory.

Enhanced `reservelib` to prepend `username` to the owner string. This is beneficial on multi-user systems, where users
not relying on `Docker` would end up being visible as hostname-only owners, making it impossible to see who owns a
setup.

Added wildcard matching to the name parameter of the `pod` and `client` testbed tools and added error-handling to
improve the user experience for these two CLI tools.

Enhanced `device_log_catcher` to log both `stdout` and `stderr` when the remote command fails. This enables better
debugging ability as before part of the information may have been hidden, depending on the remote command being
executed.

Added `put_dir()` method to `device_api`.

Added `get_rssi()` method to `pod_api` for `bcm` and `qca` platforms.

Update the `Docker` image and all packages to support and use `Python 3.12`

Added per model version specific interface name overrides. This method will return different interface names than the
ones retrieved from the configuration files, based on the device version.

Enabled custom destination dir in `download_proper_version()` in the artifactory reader tool.

Enhanced the version string requirement in the artifactory reader tool. The major and minor versions are required, the
revision and patch versions (3rd and 4th respectively) are optional, so is the build number. The `LATEST` version string
is also permitted, since this is an `Artifactory` builtin.

Extended common utilities with a function to compare FW versions. This enables you to determine which version is newer.

Enhanced the firmware version comparison function to compare 3-digit version strings and allow `greater than`, `lesser
than`, and `equal to` checks.

Added the parsing of fractional frequencies output from the `iw` tool. Previous versions of the `iw` tool did not
contain fractional frequencies, but the tool version on the current version of testbed devices does.

Added method to check `SingleDPI` status of the device from the `Flow_Service_Manager_Config` table.

Enhanced the `switch` tool to accept comma separated lists of parameters.

The firmware upgrade fixture is forced before storing pod versions in the `Allure` environment.

Firmware version reporting is moved to the `allure_environment` plugin, now extracting version information from devices directly.

Deprecated obsolete models `IPQ807X-AP-HK09` and `MR8300-EXT`.

### Limitations

There is a limitation in the current implementation of the regulatory rules `config/rules/regulatory.yaml` in the FUT
framework. By reading supported channel information from the device capabilities `YAML` files in
`config/model_properties/*` it is impossible to determine the supported bandwidth for each channel without additional
logic. This is why the default configuration currently excludes channels
available for devices that support `UNII-4`. Without `UNII-4` support, the following 7 combinations are not supported by
the device: channel 165 + HT40/HT80/HT160 and channel 149/153/157/161 + HT160. This limitation is due for improvement in
the following releases.
