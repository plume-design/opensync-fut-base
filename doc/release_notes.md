# FUT Release Notes

Welcome to OpenSync Functional Unit Testing (FUT) release notes. See what has changed with the latest release.

## Release FUT-2.6

This [version](../.version) of FUT supports the following OpenSync releases on these reference devices:

- `PP443Z`: `6.6.0`
- `PP703X`: `6.6.0`, `7.0.0`
- `FILOGIC880-BE19000`: `6.6.0`

The `debian-server` and `debian-client` version required for FUT is `3.0.59`. The `RPI server` and `RPI client` version
required for FUT is `2.0-209`. Due to a regression in the client driver, the recommended `debian-client` version for
testbeds with non-WiFi-7 devices remains `3.0.41`.

## New Features

FUT now supports MLO fronthaul in test cases.

FUT now supports MLO backhaul in test cases.

A new mechanism was introduced for dynamic generation and loading of test configurations via pytest hooks and fixtures.
This includes the implementation of new device management handlers with cached properties and corresponding pytest
fixtures. File transfer procedures have been improved and simplified, alongside the standardization of test fixture
arguments. Automated firmware download fixtures were added for UM tests, and testbed pod initialization was simplified.
Legacy device handlers, the `test_suite_device_requirements.yaml` file, and redundant pytest fixtures have been removed.

A mechanism was introduced to load `<MODEL>_known_issues.py` files similar to `<TEST_SUITE>_inputs.py` and combine them
into test case configurations with the framework generators. The known issues files are model and version specific, and
are intended to store known FW issues. When a test session is started, the specified test cases are marked with a pytest
marker names `known_issue` to make them easy to recognize, and with the `xfail` marker, which turns test failures into
skipped tests in the Allure report, while still executing the test, in case the firmware bug is fixed, and to be able to
inspect logs without tainting results.

Changed the default encryption used throughout FUTs to `WPA3`. Unless stated otherwise, all test cases will use this
security mode.

Added the possibility to mark tests with `xfail` if the test case configuration contains this key.

Lower the `tx_power` on device radios at pytest session start. Do this only if the device supports this feature.

Removed the following deprecated test cases:

- `test_cm2_ble_status_cloud_down`
- `test_cm2_ble_status_internet_block`
- `test_wm2_check_wpa3_with_wpa2_multi_psk`
- `test_wm2_leaf_ht_mode_change`
- `test_wm2_set_wifi_credential_config`
- `test_wm2_wifi_security_mix_on_multiple_aps`

Framework logging is enhanced and simplified. `SSH` commands are no longer shown in its entirety on `DEBUG` level, only
on `TRACE` level. Instead, only the command is logged that is executed on the remote device.

Added a new test case `dm_verify_max_memory` that verifies whether `DM` terminates the `OpenSync` process that consumes
too much memory. The process crash is reported via the `MQTT`.

Added a new test case for the OpenSync restart reporting feature.

Added a new test case to verify the remotely triggered device reboot functionality.

Added a new test cases for verifying reduced disruptions caused by radar events.

Added new test cases for Latency Optimisation under Variable Load with active measurements for Fixed Wireless Access - FWA
scenarios, handled by the QOSM.

Added a new test case `sm_latency_report`, where latency stats are gathered for WAN/home-ap interfaces on the GW,
while network traffic is generated from an associated client to the testbed server. This verifies that:

- Epping (latency measuring tool) is successfully deployed on WAN and home-ap interfaces on the GW.
- Epping is able to gather data on those interfaces.
- An MQTT report is generated, which contains collected latency data samples for each interface.

Added a new test case `othr_healthcheck_service` that verifies the healthcheck service is correctly configured and
running on the device.

Added a new test suite `QOSM` with tests concerning the Quality of Service Manager.

Enhanced the test case `wpd_stop_wpd` with a generic solution to ensure HW clocks stay at the correct frequency. Some
devices tie the HW watchdog clock to the processor clock, which is throttled down at times of inactivity. By
implementing this fix, one of the CPU cores is loaded with a computationally intense repetitive task to keep it busy and
maintain the clock frequency.

Add support for `mld_addr` field in common libraries. This is used instead of the `mac` field in table
`Wifi_Associated_Clients` when the connection uses MLO.

Markdown support has been added for test case descriptions, and the documentation structure was reorganized to a flat
hierarchy. Automatic test case description generation has been integrated into Allure.

The NGINX rate limiting on the testbed server, used for UM tests, was changed from `1024k` to `10240k` to speed up image
download. This decreases the setup steps of most UM test cases.

Test case config files were removed for models that are no longer supported.

Test case configuration generators were enhanced with the option to override inputs completely. This is useful if
skipping or ignoring certain inputs would be too complex.

Add `log.info` to server and client setup functions in `fut_fixtures.py`.

Unified OpenSync version checks across all test suites to ensure consistency.

Enhanced file transfer by introducing separate local and remote paths. The `self.transfers` attribute now stores a list
of `(local path, remote path)` tuples intended for file transfer. All pytest plugins must use the same structure when
appending directories via the `extra_transfer` attribute. This enhancement required updating supplementary functions
such as `_get_model_override_dir()`, which was renamed to `_get_model_override_filepath()` and now returns the correct
remote file path regardless of the local path. Using `Path.is_file()` was inappropriate since the return value reflects
the remote location. Because local and remote paths may differ due to the enhanced transfer logic, the value is now
normalized before being returned.

Retrieved only the DM manager PID in `fut_fixtures.py` instead of getting all and filtering later. This reduced
execution time and avoided unnecessary device function calls.

Implemented fixes for `FILOGIC880-BE19000` MLO compatibility, which includes correcting the model properties file and
adding additional checks to FUT test cases, which verify the validity of interfaces. This makes it possible to run FUT
test cases on this WiFi-7 device, that uses AP interfaces instead of MLD interfaces.

Replaced capabilities dictionaries with `NodeHandler` instances in the `DefaultGen` class and refactored class methods
accordingly. Related classes and tests were refactored to accommodate this change.

The `vif_reset.sh` script now checks the interface type before performing any action. This increases robustness of the
cleanup step of `nm2_set_gateway` test case. This ensures that a VIF reset is only executed when the interface type is
vif, preventing potential failures for other interface types.

An OpenSync version check was added to the following test cases to prevent compatibility issues:

- `nm2_set_upnp_mode`
- `fsm_configure_test_dpi_http_request`
- `fsm_configure_test_dpi_https_sni_request`
- `fsm_configure_test_dpi_http_url_request`
- `wm2_transmit_rate_boost`

The test case `wm2_verify_associated_clients` was removed. It is the same as `wm2_connect_wpa3_client` since we started
defaulting to WPA3 encryption.

The test case `wm2_connect_wpa3_client` was renamed to `wm2_connect_client`.

Introduced new functions to manage pod reboots and dynamically check for device availability within tests.

Added a shell function to disable all GRE interfaces during test cleanup procedures.

The test framework's reliability has been improved by handling pod reboots during module setup, ensuring devices are
properly initialized.

Device initialization is now more robust by verifying that all device radios are active before proceeding with tests.

System configuration is now better protected against modification during runtime by converting certain default values to
read-only tuples.

Optimized the process for retrieving PIDs by fetching the specific manager PID directly, reducing system calls and
execution time.

Replaced fixed-time delays with more reliable wait functions in shell scripts to improve test stability.

Standardized the use of `ovs-vsctl` for interacting with network bridges to ensure consistent behavior across different
device types.

Test framework setup now defaults to performing a full device initialization for all required devices, increasing test
robustness.

Unified OpenSync version checks across all test suites for consistency.

Enhanced Multi-Link Operation (MLO) detection logic to use feature flags for determining backhaul and fronthaul support.

Various variable and internal key names were updated for better clarity and consistency throughout the framework.

Test client connection methods were refactored for improved stability.

Updated the Python version from `3.12` to `3.13` and downgraded the protobuf library to resolve compatibility issues.

Removed a duplicate test case for verifying associated clients, as its functionality was covered by the WPA3 connection
test.

Numerous refactoring and code cleanup tasks were completed, including removing redundant code and unifying function
calls.

Test reporting was enhanced to include more dynamic information, such as ticket numbers and failure reasons for known
issues.

Renamed test case `wm2_create_wpa3_ap` to `wm2_create_ap`.

Renamed test case `wm2_connect_wpa3_leaf` to `wm2_connect_leaf`.

Test case `wm2_set_radio_tx_power_neg` was removed to simplify testing procedure and reduce the need for empirically
determined test case inputs.

Running the `dhclient` on the testbed client device is now more robust. Detecting an existing process and stopping it is
now successful even if the `PID` stored in the pid file is incorrect or the process is stopped already.

### Removed shell overrides

Model and platform shell library override files were removed and adjustments made to test cases to make them generic.
The files can still be used for other models, if required, each user is responsible for their own overrides.

UM test cases now use `UPG_ERR_IMG_FAIL` and `UPG_ERR_FL_WRITE` interchangeably. This affects `um_corrupt_image.sh`,
`um_set_invalid_firmware_url.sh`, `um_set_upgrade_timer.sh`.

The `wm2_set_radio_tx_power` test case now allows test case input overrides to be more generic and accomodate more
devices.

The function `get_actual_chainmask()` in `wm2_set_radio_thermal_tx_chainmask` and `wm2_set_radio_tx_chainmask` was
replaced with overridable test case inputs and the function was removed from `unit_lib.sh`.

The test case `validate_radio_mac_address` was removed.

The function `get_syslog_rotate_cmd()` was changed from a stub to generic implementation and the function
`device_syslog_rotate()` was added.

The function `clear_dns_cache()` was changed from a stub to generic implementation and the `cm2_dns_failure` test case
definition.

Changed the default value of the `disable_fatal_state` parameter in `_pod_handler_setup()` to `True` in
`fut_fixtures.py`. This ensured that all required devices perform `device_init`, including OpenSync restart, at session
start, where previously only L1 and L2 devices did. This increased test robustness at the cost of ~18 seconds of
execution time.

Replaced the combination of sleep and check with a wait function in `unit_lib.sh` for `nb_add_port_to_bridge()`.

Used `ovs-vsctl` instead of `brctl` in `unit_lib.sh`, regardless of bridge type. This is the correct method for
obtaining system information, even on devices that implement Linux native bridges.

Printed Inet tables in the script trap in `wm2_setup.sh`.

Ensured `MODEL_OVERRIDE_FILE` and `PLATFORM_OVERRIDE_FILE` were only added in `pod_handler.py` if configured. Paired
with the default `/dev/null` value in `default_shell.sh`, these files are populated only when the correct pytest plugin
is loaded. The overrides were removed and are now loaded explicitly rather than implicitly, if you decide to provide
them for models that require them.

Changed the default value of `MODEL_OVERRIDE_FILE` and `PLATFORM_OVERRIDE_FILE` in `default_shell.sh` to `/dev/null`.

Enhanced `_get_model_override_dir()` in `pod_handler.py` to search only in `self.file_transfer_folders`.

Updated `_find_target_path_in_root_dir()` in `fut_lib.py` to search through a list of `root_dirs` instead of a single
one.

Added an `extra_transfer` list of directories from `request.config` to `self.transfer_folders` during device handler
setup in `fut_fixtures.py`.

Added the `transfer_folders` attribute to all handler classes.

Introduced `_find_target_path_in_root_dir()` as a general function to locate a target path within a root directory. Used
this function in `_get_test_case_inputs_dirs()` in `fut_gen.py`.

Removed the `wpa3_support` cached property from the `PodHandler` class and eliminated compatibility checks in
`_configure_security_args()`. Assume all devices support WPA3. Removed the `check_wpa3_compatibility()` function from
`unit_lib.sh`. Also removed calls to `get_wpa3_support()` from `WM2_test.py` and deleted the
`check_wpa3_compatibility.sh` script.

Removed `get_tx_power_from_os()` and updated the `wm2_set_radio_tx_power_neg` test case and its definition accordingly.

Removed `check_tx_power_at_os_level()` and updated the `wm2_set_radio_tx_power` test and definition.

Removed the `simulate_radar()` function from `unit_lib.sh`.

Removed `check_ht_mode_at_os_level()` and updated the `wm2_set_ht_mode` test and its definition.

Removed the `leaf_ht_mode_change` test case, its definition, inputs, and `check_ht_mode_at_os_level` shell file.

Removed `check_channel_at_os_level()` and updated the `wm2_set_channel` test and definition.

Removed `get_ht_mode_from_os()` and updated the `wm2_set_ht_mode_neg` test and definition.

Removed `get_channel_from_os()` and updated the `wm2_set_channel_neg` test and definition.

Removed `check_vlan_iface()` and updated the `nm2_vlan_interface` test and definition.

Removed `check_tx_chainmask_at_os_level()` and updated the `wm2_set_radio_thermal_tx_chainmask` and
`wm2_set_radio_tx_chainmask` tests and definitions.

Removed `check_beacon_interval_at_os_level()` and updated the `wm2_set_bcn_int` test and definition.

Updated the `nm2_set_upnp_mode` test case definition.

Fixed a typo in the `test_nm2_set_upnp_mode` log in `NM2_test.py`.

Passed `request.config` to all device handler fixtures and added `extra_transfer` to `put_dir` calls in setup
procedures. This replaced the hardcoded transfer of the shell/internal directory. if it existed and had files. With the
recent improvements in selective pytest collection, this change prevents tainting the device shell environment with
overrides. These overrides are now opt-in, rather than assumed to always be present.

Added kwargs support to the `device_test_setup()` method in `pod_handler.py` and propagated the argument to the
`execute()` call. This allowed for overriding the path to the executed function, making internal shell scripts
reachable.

### Fixed shellcheck errors

Fixed `shellcheck SC2068: Double quote array expansions to avoid re-splitting elements`.

Fixed `shellcheck SC2181: Check exit code directly with e.g. if mycmd;, not indirectly with 130`.

Fixed `shellcheck SC2046: Quote this to prevent word splitting`.

Fixed `shellcheck SC2016: Expressions don't expand in single quotes, use double quotes for that`.

Fixed `shellcheck SC1073: Couldn't parse this (thing), fix to allow more checks`.

Fixed `shellcheck SC2060: Quote parameters to tr to prevent glob expansion`.

Fixed `shellcheck SC2034: foo appears unused. Verify it or export it`.

Fixed `shellcheck SC2002: Useless cat. Consider cmd < file | .. or cmd file | .. instead`.

Fixed `shellcheck SC2091: Remove surrounding $() to avoid executing output (or use eval if intentional)`.

Fixed `shellcheck SC3046: In POSIX sh, source in place of . is undefined`.

Unified sourcing of shell libs and redirecting `stdout` and `stderr` to `/dev/null`. For shell scripts in
`shell/tools/device` it is necessary to only echo to `stdout` or `stderr` whatever is needed by the calling script. If
sourcing the library scripts is not silenced, this may end up unexpectedly in the calling scripts expected output.

Replaced variable `tc_name` with hardcoded string in `nm2_configure_verify_native_tap_interface.sh`.

Enhanced `unit_lib.sh::killall_process_by_name()` by sleeping between `kill` commands with different signals. This gives
the process time to die gracefully, before continuing with the next, more aggresive signal. To save time, only sleep
`10000` microseconds if `usleep` is available on the device, otherwise sleep `1` second.

Enhanced `unit_lib.sh::contains_element()` to handle several input arguments or a single space separated string.

Removed unnecessary code comments `FUT environment loading`, `SECTION START` and `SECTION STOP` in shell scripts.

Unified shell scripts used on the testbed client:

- Prefer using `fut_topdir` variable when only `base_lib.sh` is needed.
- Unified script sourcing and paths.
- Eliminated sourcing `fut_set_env.sh` as this is not generated or transferred for the client device.
- Eliminated sourcing of `default_shell.sh` as it requires device-specific variables to be set.

Removed `set -x` from `tpsm_crash_speedtest_verify_reporting.sh` that was unintentionally left in the code.

Shell scripts used on the testbed server were unified:

- Script sourcing and paths were unified both in logs and function calls.
- Prefer using `fut_topdir` variable when only `rpi_lib.sh` is needed, and only export `FUT_TOPDIR` when `unit_lib.sh`
- import is needed.
- Added checks if the file exists for UM shell scripts.
- Hardened shell UM scripts to handle cases where the script path given is relative, and there is no dir change needed.
- Eliminated sourcing `fut_set_env.sh` as this is not generated or transferred for the server device.
- Eliminated sourcing of `default_shell.sh` as it requires device-specific variables to be set.
- Unified naming and invocation of help/usage function in scripts.

Reversed import order of `fut_set_env.sh` and `default_shell.sh`. The `default_shell.sh` now has import guards
preventing execution if key environment variables are not set, so it must be sourced after `fut_set_env.sh`.

Removed comment regarding `remove_sta_interfaces_exclude` from `unit_lib.sh` since the function was previously removed.

Replaced calling the `test` tool with native parameter evaluation in `default_shell.sh`.

Removed shell variable `DEFAULT_WAIT_TIME` and hardcoded the value or passed as parameter from calling function.

Do not modify the shell variable `PATH`, since the framework does this already when executing ssh commands. Removed
`PATH` from the device handler `_get_shell_cfg()` function.

Removed shell variable `LOGREAD` and replaced it with a config parameter provided by the framework.

Removed unused variables fom `default_shell.sh` and `device_handler.py`.

Removed unused import guard variables from `default_shell.sh` for shell libs that no longer exist.

Removed unused variables from shell:

- `CAC_TIMEOUT`
- `MGMT_IFACE`
- `MGMT_IFACE_UP_TIMEOUT`
- `MGMT_CONN_TIMEOUT`

Added the import guard variable to `base_lib.sh`.

Fixed terminal logging for `fut_setup.py` tool and added the debug level option.

Removed unused file `shell/lib/client_lib.sh`.

## Fixed Bugs

Fixed the retrieval of the incorrect MAC address when connecting the client device to the pod.

Created new shell function `wan_link_selection_enabled()`. This function checks the new Kconfig value
`CONFIG_TARGET_ENABLE_WAN_LINK_SELECTION` to see if OpenSync or a third party service controls the WAN link selection on
the device. The legacy `CONFIG_TARGET_CAP_EXTENDER` value is also evaluated for backward compatibility.

Fixed the `get_wifi_associated_clients()` method in `pod_lib.py` to no longer treat `00:00:00:00:00:00` as a valid MAC addresses.

Fixed the kconfig dependency for the bridge type check in shell. The check is now performed by inspecting the
`ovs_version` filed of the `AWLAN_Node` OVSDB table. This fix was previously done in the framework, and now the two are
identical.

Moved test cases `test_nm2_verify_linux_traffic_control_rules` and
`test_nm2_verify_linux_traffic_control_template_rules` in the NM suite to `test_qosm_verify_linux_traffic_control_rules`
and `test_qosm_verify_linux_traffic_control_template_rules` in the QOSM suite.

Fixed `test_dm_verify_reboot_reason` failures due to a Python error: `UnboundLocalError: cannot access local variable
'log_tail_local_path' where it is not associated with a value.`

Added missing `arping_cmd` value to `unit_lib.sh`.

Fixed the test case `tpsm_verify_ookla_speedtest_bind_reporting` to wait for the process PID for some time instead of
only checking once without delay.

Fixed test case `test_onbrd_verify_model_awlan_node` by using `model_org` instead of `model` attribute in the testbed
configuration. The difference between these attributes is the change done by `DeviceCommon.convert_model_name()`. Each
value should be used for its own purpose.

Added a check of the wireless manager to the FUT framework. The `wm2_set_wifi_credential_config` test case is executed
only on devices using the WM2 wireless manager.

Fixed the `AW_Debug` entry parameters used to enable TRACE logs for OWM.

Fixed the test case `test_onbrd_verify_client_tls_connection` that occasionally failed during the setup procedure if a
`cloud_listener` process was not already running.

Fixed the `wm2_transmit_rate_boost` test case. Piping stdout to awk and expecting it to filter the content does not
fail, if nothing is preset in the output. This behaves differently to the grep command. However piping to grep after
that matches the verification requirements. This change ensures the script accurately filters the packet capture file
for the specified transmit rate and source MAC address, increasing reliability in test results.

Increased the channel change timeout in the `wm2_ht_mode_and_channel_iteration` test case to prevent issues when testing
DFS channels.

Increased the pytest test case timeout to `720` seconds in `wm2_wifi_security_mix_on_multiple_aps` and
`wm2_create_all_aps_per_radio` test cases.

The test case `nm2_set_gateway` configuration is simplified to only execute on the uplink WAN ethernet port.

Corrected an issue where checks for associated Wi-Fi clients would only evaluate the first client in the list,
potentially missing others.

Resolved a bug that could cause an error when retrieving MAC addresses from an empty list.

Fixed an issue where a service would enter an endless restart loop if it crashed.

Addressed a test timeout in the `dm_verify_max_memory` test by adjusting the memory check parameters for a faster
response.

Corrected the interface name being passed to a test script for GRE tunnel verification.

Fixed a bug in a GRE tunnel test caused by an incorrect MAC address being used.

Fixed an issue where a test cleanup procedure failed to disable all GRE interfaces.

Corrected the setup step for a speedtest crash verification test.

Resolved a potential error by ensuring the pod reboot function can handle an empty list of inputs.

Removed the 6GHz radio band configuration from a multi-PSK Wi-Fi client connection test to prevent failures.

Added a SIGKILL stop signal to the server's Docker container to ensure it exits immediately when stopped.

Temporarily disabled several known flaky test cases and suites (CM2, NM2, WM2) to improve overall test run stability.

Removed the erroneous second input parameter `port_name` in `get_all_ports_in_bridge()` calls to
`nb_get_all_ports_in_bridge()` and `ovs_get_all_ports_in_bridge()` and improve error handling in the
`remove_all_ports_from_bridge()` function in `unit_lib.sh`, by examining the exit code of the sub-shell used to get the
value of ports instead of using the sub-shell directly in the for loop.

Test case `wm2_dfs_cac_aborted` procedure was simplified to only wait for the correct state of the
`Wifi_Radio_State::channels` field, not the `Wifi_Radio_State::channel` field. Waiting for the channel to change in
`Wifi_Radio_State` after setting it in `Wifi_Radio_Config` may hide the fact that enough time has passed for CAC to
elapse. This is no longer the case, and `30s` is chosen for this effect to be seen.

## Common Testbed Library

New model features were incorporated into the capabilities list.

`POWER_METER` was added to the capabilities enum array in `locations_schema.json`.

A method `is_tx_power_configurable()` was added to the `Capabilities` class.

A method `is_mld_iface()` was added to the `Capabilities` class.

A method `is_mlo_bh()` was added to the `Capabilities` class.

A method `is_mlo_fh()` was added to the `Capabilities` class.

The `client_api: disable_mlo` flag was added to allow disabling Multi-Link Operation (MLO) when requested, not only when
the BSSID was set.

The `iw` tool is now used to look for active MLO link BSSID in `client_lib.py`.

MLO was disabled for client connect `--bssid=` on Wi-Fi 7 clients.

The `client.connect()` method now includes a `node` parameter that works with MLO.

The `bssid_accept=` `wpa_supplicant` option now works with MLO.

The logic for finding the active BSSID was updated to no longer rely on `wpa_cli mlo_status` and instead uses `iw link`
and `iw info` for Wi-Fi 7 clients with MLO support.

The `client_lib` no longer uses fixed BSSID in `wpa_supplicant` config for MLO, and instead uses `wpa_cli roam` to move
to the desired node.

The associated clients check was enhanced to ignore `00:00:00:00:00:00` as a valid MAC address for MLO-capable clients.

MLD address support was added to `Wifi_Associated_Clients`.

LAN Latency Measurements were introduced, including the addition of `collect_lan_latency_stats` to `MqttClient` and
`get_lan_latency_topic` to `MqttResolver`.

The `mqtt_client` now handles all exceptions when establishing an MQTT connection to improve robustness.

The `sta` interface type was unified to `backhaul_sta`.

A fix was implemented for the `osrt tree` command to handle non-group commands that do not have the `.list_commands()`
attribute.

The multiplex command in `parallelssh.py` was updated to remove unnecessary concatenation of strings.

A `wait` command was added to the client tool, allowing waiting for a client to become available.

The `cfg80211` based `tx_power` methods were moved to the generic `pod_lib`.

The `iw` tool's `set txpower` syntax was fixed by adding the `fixed` keyword.

The `tx-power` setting now allows resetting to default by using "auto" or "fixed 0" when the input `tx_power` is less
than or equal to 0.

Generic `PodLib.*tx_power*()` methods now stop on the first `iw` error.

The `iw` tool is now used for getting and setting `tx_power` on `QSDK >= 11` and Mediatek by default.

Tx power limit setting was reworked, including renaming `limit-tx-power` to `limit-tx-power-set` and adding
`limit-tx-power-get` commands. Options were also reworked into arguments, and `True/False` into `enabled/disabled`.

A `network namespace` property was added to `client_api`.

The `put_dir()` methods for `ssh_execute` and `client_lib` were unified and logging was enhanced.

Logging was enhanced for `wait_available()`, `wait_unavailable()`, and `put_file()` in `ssh_execute.py`.

The logging level in `set_log_level()` was changed from `debug` to `trace`.

Logging clutter at the `DEBUG` level was reduced in `parallelssh.py` and `ssh_execute.py` by changing some debug logs to
trace logs.

The ability to log at `TRACE = 5` level, lower than `DEBUG = 10`, was added.

`client_lib` now checks for SSH availability before attempting to get `dmesg` logs to prevent timeouts.

The `get_client_ips` method in `client_lib` was updated to try parsing IP output even if the return code is 255.

The `fqdn_check` method in `client_lib` now uses the `EXECUTE_CMD_TIMEOUT` for its default timeout.

Client connection now retries if the wrong BSSID is selected.

The `bssid_accept` option is no longer used on RPi clients due to lack of support.

The `client.set_accepted_bssid()` API was added to change which BSSID `wpa_supplicant` will associate with.

Wireless clients are now always disconnected, even if they are not shown as connected, to prevent `wpa_supplicant` from
remaining running after failed connection attempts.

The "roam to bssid" feature in `connect()` is now used only for Wi-Fi 7 clients.

Upgrade using `ospkg` images is now possible.

The `upgrade` procedure for `BCM947622DVT` was fixed by correcting the overloaded method.

Unencrypted upgrade now allows different image types beyond `.img`, including `.bin` and `.pkgtb`.

A fix was implemented to ensure `args` are not altered to `None` in `upgrade_from_local_file()` when `fw_key` does not
exist, preventing exceptions during unencrypted image upgrades.

The `md5sum` check in Artifactory download was fixed to correctly handle cases where the md5sum is not available.

The `fn-prefix` in `artifactory_lib.py` was adjusted to remove trailing hyphens.

The `artifactory_reader` was adjusted to enhance the API request for getting a list of images by increasing the search
depth.

Prefix checking in `artifactory_reader` now supports regex.

BSSID parsing was updated to handle lowercase BSSIDs returned by some clients.

The `get_channel_states()` function was implemented to return `channel_states` / `cs` objects.

The `pod_api` now uses the config model if SSH fails when retrieving the model.

The `pod_lib` was updated to override `DE` as `EU` for country code handling.

The `pod_lib` now skips exceptions when getting the OVS version.

The `pod_lib` was fixed to correctly get client MAC addresses, even if the MAC is `00:00:00:00:00:00`.

The `get_bssids` method in `pod_lib` now properly handles both single and multiple UUID cases when a radio band has only
one UUID associated with it.

The `eval()` function was removed from `python_list_to_ovsdb_set()` in `pod_lib.py` and replaced with a more robust type
checking and string formatting approach.

A 1-second timeout was added after stopping `tcpdump` and switching the Wi-Fi client to station mode, and before
downloading the pcap file, to improve stability.

The `pod api get_wifi_associated_clients()` method was updated to always return a list of MAC addresses, empty if no
clients are found.

Installation of editable packages was reverted to be done in separate steps in `dock-run`.

Implementation was added for setting and getting bandwidth limits on switch ports, including new `set_bw_limit()` and
`get_bw_limit()` methods.

A client reboot is now triggered when `wlan0` is missing after stopping the network namespace service.

Cached client data is now stored in `cached_properties` for improved performance.

Clients are now rebooted in case of a driver crash while starting the sniffer.

A missing `--band` option was added to the `client wmonitor` command, and `wifi_station` was fixed.

The `scp_timeout` in sniffing utilities was increased and exposed as an argument to `sniff_packets_on_client` to allow
downloading larger files.

The Docker image now attempts to query systemd for the timezone.

Blindly bind-mounting `/etc/localtime` in Docker was avoided.

The `fastavro` version was bumped to `1.10.0` to add support for Python 3.13.

Deprecated `mix_stderr` parameter was removed from `CliRunner` in `conftest.py` due to its removal in `Click 8.2.0`.

The Python interpreter was bumped to version `3.13.2`.

Code formatting errors were fixed in `sanity_lib.py` and `rpowerlib.py`.

Support for DSS (DSA) host SSH keys was dropped.

PID retrieval from commands for clients was fixed.

MD5 sum hash calculation was replaced with a dedicated `get_md5sum()` method using `hashlib.md5`.
