# FUT Release Notes

Welcome to OpenSync Functional Unit Testing (FUT) release notes. See what has changed with the latest release.

## Release FUT-2.4

This [version](../.version) of FUT supports the following OpenSync releases:

- 6.4.0.0
- 5.6.0.0

## New Features

Added coverage for `TPSM - OpenSync Third Party Service Manager`, to the FUT framework. A new test case
`tpsm_crash_speedtest_verify_reporting` was implemented, that verifies error reporting when speedtest services crash.
Existing test cases were updated to the latest OpenSync standard.

Added coverage for the `WDS` OpenSync feature to the FUT framework.

Added coverage for the `NAT loopback` OpenSync feature to the FUT framework.

Added coverage for `WPD - Watchdog Proxy Daemon` to the FUT framework.

Changed the method used for device bridge type retrieval. The new method defines the bridge type based on the
`ovs_version` field in the `AWLAN_Node` table.

An additional cleanup step was added to the `wm2_wds_backhaul_traffic_capture` test case. It ensures that the client
interface is set back to STA mode.

The shell `log()` function implementation was changed from using `if` statements to `switch` statements. This produces
less printout when using `set -x` for development or debugging.

The following flags in shell functions were removed:

- `log -wrn`
- `raise -nf`
- `raise -f`
- `raise -osc`
- `raise -oe`
- `raise -ow`

Some shell functions were moved from `base_lib.sh` to `unit_lib.sh` and `docstrings` were added:

- `contains_element()`
- `get_index_in_list()`
- `get_by_index_from_list()`

The unnecessary `FAIL` string was removed from all calls to the `raise()` shell function. The format was unified and
changed to include the failure type already.

Various shell script errors that were reported by the `shellcheck` static analysis tool were fixed in this release.

Checking the device WPA3 support was simplified and made faster. The code bloat in the
`tools/device/check_wpa3_compatibility.sh` script was removed and error logging in shell functions was removed in favor
of simply returning the correct exit code.

The shell function `cm_disable_fatal_state` was renamed to `disable_fatal_state` to better reflect the functionality.

Part of the function `check_ovsdb_entry()` was split into `check_ovsdb_entry_transact()` to minimize execution time and
error logs when the condition is not met.

The `wm2_set_radio_tx_power` and `wm2_set_radio_tx_power_neg` test cases were added back to the list of default test
cases. The underlying features were fixed in `OpenSync` version `6.4.0`. The minimal `OpenSync` version is checked
during the test.

Created the `test_wm2_transmit_rate_boost` test case.

Enhanced the `wm2_check_wpa3_with_wpa2_multi_psk` test case by implementing a ping check, instead of only verifying
whether the client can be associated. A bug was fixed where the VIF radio index was erroneously passed to the
`add_bridge_port.sh` script.

The `clear_port_forward_in_iptables.sh` script was renamed to `flush_iptables_chain.sh` and now allows the user to
specify which `iptables` chain should be flushed.

The `run_iperf3_server.sh` now accepts an optional port argument, which allows the user to specify the port of the
`iperf3` server on which to listen on and connect to.

The `connect_to_fut_cloud()` now appends the FUT generated `CA` file to the device `CA` file instead of overwriting it.
This ensures the original device `CA` remains accessible in case it is incorrectly restored.

The test case `wm2_set_radio_tx_power` inputs are changed to a list of values instead of a range.

Test case `nm2_ovsdb_ip_port_forward` definition file was updated after changes were made in the generators.

Removed unused shell scripts and shell functions from the FUT framework.

The test suite setup procedures were optimized to expect the device to be ready for testing instead of resetting the
device every time. This both decreases execution time and allows for more time for the device to settle into a more
stable state, thus improving stability.

The traps in FUT shell scripts have been made more robust and posix compliant by unifying indentation, making signal
specifications posix compliant, disarming them and calling exit explicitly.

The framework implemented a new method `get_wpa3_support()` for the `NodeHandler` class, that does not log errors.

The `sm_radio_type` parameter is now inferred from the `radio_band` parameter needed for the same test, and is no longer
required in the test case inputs.

The command used to detect the `noexec` flag on `tmpfs` disk partitions on devices under test was negated to eliminate
error reporting in the framework, when the expected condition is met.

A new method `_add_to_logs()` was introduced in the `NodeHandler` class. It adds logs to the report instead of the
console.

Framework `NodeHandler` objects now fetch information about support for individual managers in `kconfig` and their
status in the `Node_State`table at `pytest` session start. This enhances detection of missing or unsupported test
suites and skips test case execution more reliably.

Created the `VirtualInterafce` class in `node_handler.py`, which handles all configuration tasks related to virtual
interfaces on the devices. By creating a new instance for every configured interface it allows for easier VIF
manipulation and information retrieval. The parameter names used in the VIF configuration procedure have been unified
with the names of fields in OVSDB tables where possible. Redundant parameters have been removed.

Added the option of configuring a multi-leaf backhaul network, using either the star or line topology.

Added type hinting to all `NodeHandler` class methods.

The `Ovsdb` class from `lib_testbed/generic/pod/generic/pod_lib.py` was implemented into the FUT framework. An
additional `wait_for_value` method was added to the `Ovsdb` class, which can be used to wait for a field to have a
specific value in an OVSDB table.

The `Config` class in `fut_configurator.py` and all of its uses were removed from the FUT framework. The code
readability was poor and the added value did not justify the maintenance cost.

All `FutGen` keywords were removed from test case input files. This makes generating test case configurations from the
test case inputs more unified and the code more easily maintained.

The FUT framework was enhanced to enable running remote commands on the device in the background, so the function call
is not blocking.

The FUT framework no longer relies on the `192.168.200.10` DHCP reservation for the `gw` device `WAN` address. The
address is retrieved from the device every time it is needed in case it is different than expected.

Regulatory rules now correctly handle `UNII-4` support in devices. If certain `5GHz` channels are not supported by the
device, the framework infers there is no support for `UNII-4` and some channel-bandwidth combinations are not allowed as
test case inputs.

Exception handling in the FUT framework was enhanced in several ways:

- Redundant exception handling was removed if there was not a specific use case in mind.
- `RuntimeError` exceptions were replaced with more specific exceptions and more information was provided in logs.
- Generic or catch-all exceptions were replaced with more specific exceptions or removed entirely.
- Exception casting was eliminated or the same exception was thrown with additional log information.
- Exception formatting was unified and the `from` clause was added when casting exception types.

The `sanitize_arg()` framework method was simplified and unit tested. `Int` type arguments are cast into `str` before
`sanitize_arg()` is called.

The `all_encryption_types` list was added to `defaults.py` and used in tests instead of hardcoded values.

The `get_command_arguments()` method was enhanced to handle lists, tuples and sets recursively. The recursion was also
fixed, as individual arguments were unpacked incorrectly before recursively calling the method.

The unused method `get_radio_band_from_channel()` was removed.

Added type hinting to various function and class methods in the FUT framework:

- `DefaultGen.py`
- `allure_parser.py`
- `device_handler.py`
- `fut_configurator.py`
- `fut_gen_cli.py`
- `fut_lib.py`
- `fut_mqtt_tool.py`
- `fut_setup.py`
- `server_handler.py`

The FUT framework now uses only the new `osrt` CLI tools. All usage of the legacy CLI tools was removed.

Common `osrt` CLI tools now have the option to validate the location file to the provided schema. Example of use:
`./docker/dock-run osrt validate-locations -D -x config/locations/_testbed_validation_exclude.txt`.

Tracking of the `OpenSync` manager PIDs is now done by the FUT framework. The`check_manager_alive()` function in
`unit_lib.sh` is thus redundant and was removed.

Input files for the test case configuration generators are now reusing common test values, present in several tests. The
most reused are the radio band, channel and bandwidth settings for WiFi tests.

The number of test configurations per radio band was normalized. Unnecessarily duplicated `5GHz` and `6GHz` test
configurations were removed to improve overall execution time.

The monolithic implementation in `DefaultGen.py` was split into several smaller functions to improve code readability.

All custom generators were removed and the `DefaultGen.py` was enhanced to make all procedures generic, but only
executed on some test cases, where needed.

Added custom keys `do_not_sort` and `expand_permutations` to test case generators.

A method was introduced to expand permutations of test case inputs directly, without requiring an additional generator.

Methods `get_if_name_type_from_if_role()` and `replace_if_role_with_if_name_type()` were added to test case
configuration generators. This allows the user to specify test case inputs as interface roles, and the framework gets
the interface name from the device model properties. This increases reliability that the values are correct for each
device.

Some variations to the keywords `channel` and `radio_band` were added to the test case configuration generators in order
to better detect when some checks need to be performed.

Many logs in the test case generators were changed from `warning` to `debug` when loading inputs and regulatory rules.

FUT framework `unit tests` were updated after changes were made in the generators.

The `mergedeep` library was added to the test case generators. This performs efficient merging of nested dictionaries.

Test case inputs now only have the `inputs` key, the `additional_inputs` key was removed. The generator procedure was
enhanced to correctly join generic, per-platform and per-model inputs, in this order, subsequent values override
previous ones.

The `config/defaults.py` file is populated with values commonly used in test case generators, such as default `channel`,
`radio_band` and `ht_mode` values.

Some duplicate configurations on some radio bands were removed.

The `mismatch_bandwidth_list` was changed from `160MHz` to `320MHz` and a check for `max_ht_mode` was added during the
test procedure. This minimizes the possibility of the selected bandwidth being supported, which invalidates the test. If
the `max_ht_mode` of the band for the device is `320MHz`, the test is `skipped`. The test condition assumes that the
bandwidth is unsupported.

Test case `wm2_ht_mode_and_channel_iteration` now executes all combinations of test case inputs for `6GHz` band instead
of a select subset.

The exception handling of the `validate_channel_ht_mode_band()` method was improved.

The `config.py` file was removed from the framework library. This particular file was providing classes and methods to
handle the test case configuration. With this change, these configuration capabilities are no longer available within
the framework. This change was made in order to improve code readability and improve efficiency by using built-in data
structures.

## Fixed Bugs

Fixed the test case `onbrd_verify_dut_client_certificate_file_on_server` to adjust the certificate permissions in case
it is not appropriate for the test procedure.

Additional `CA` certificates were appended to the `ca_chain.pem` file. The new certificate authority files are used on
the FUT test server side to authenticate client certificates in the `onbrd_verify_client_tls_connection` test case.

Fixed the `wm2_transmit_rate_boost` test case. Piping `stdout` to `awk` and expecting it to filter the content does
*not* fail, if nothing is preset in the output. This behaves differently to the `grep` command. However piping to `grep`
after that matches the verification requirements. This change ensures the script accurately filters the packet capture
file for the specified transmit rate and source MAC address, increasing reliability in test results.

Increased the channel change timeout in the `wm2_ht_mode_and_channel_iteration` test case to prevent issues when testing
DFS channels.

Replaced capabilities dictionaries with `NodeHandler` instances in the `DefaultGen` class and refactored class methods
accordingly. Related classes and tests were refactored to accommodate this change.

The `vif_reset.sh` script now checks the interface type before performing any action. This increases robustness of the
cleanup step of `nm2_set_gateway` test case. This ensures that a VIF reset is only executed when the interface type is
`vif`, preventing potential failures for other interface types.

An `OpenSync` version check was added to the following test cases to prevent compatibility issues:

- `fsm_configure_test_dpi_http_request`
- `fsm_configure_test_dpi_http_url_request`
- `fsm_configure_test_dpi_https_sni_request`
- `nm2_set_upnp_mode`
- `wm2_transmit_rate_boost`

Increased the `pytest` test case timeout to `720` seconds in `wm2_wifi_security_mix_on_multiple_aps` and
`wm2_create_all_aps_per_radio` test cases.

Replaced `check_ovsdb_entry()` with `wait_ovsdb_entry()` when performing the `channel availability check (CAC)` to give
the access point some time to start.

Fixed the `pytest` test collection procedure. The presence of `swap files` in the `config/test_case/generic/` directory
would break the test collection procedure.

The redundant shell function `check_restore_ovsdb_server` was removed.

The following shell functions were removed:

- `add_interface_to_bridge()`
- `add_ovs_bridge()`
- `add_tap_interface()`
- `brv_setup_env()`
- `check_radar_event_on_channel()`
- `check_restore_management_access()`
- `check_sta_send_csa_message()`
- `connect_to_wpa()`
- `create_wpa_supplicant_config()`
- `disable_watchdog()`
- `enable_fatal_state_cm()`
- `force_purge_interface_raise()`
- `get_udhcpc_path()`
- `get_vif_mac_from_ovsdb()`
- `insert_wifi_stats_config()`
- `manipulate_iptables_protocol()`
- `nb_start_ovsdb_server()`
- `ovs_start_openswitch()`
- `remove_bridge_interface()`
- `restart_dhclient()`
- `start_openswitch()`
- `start_qca_hostapd()`
- `start_qca_wpa_supplicant()`
- `start_udhcpc()`
- `start_wireless_driver()`
- `stop_healthcheck()`
- `stop_openswitch()`
- `stop_wireless_driver()`
- `tap_up_cmd()`
- `um_encrypt_image()`
- `vif_clean()`
- `wait_for_empty_ovsdb_table()`

The following shell functions were renamed:

- `add_bridge_port()` to `add_port_to_bridge()`
- `nb_add_bridge_port()` to `nb_add_port_to_bridge()`
- `ovs_add_bridge_port()` to `ovs_add_port_to_bridge()`
- `ovs_create_bridge()` to `ovsdb_create_bridge()`
- `ovs_delete_bridge()` to `ovsdb_delete_bridge()`
- `ovs_gen_bridge_config()` to `ovsdb_gen_bridge_config()`
- `ovs_remove_bridge_port()` to `ovs_remove_port_from_bridge()`
- `remove_bridge_port()` to `remove_port_from_bridge()`
- `set_ovs_vsctl_interface_option()` to `ovs_set_interface_option()`

Test `onbrd_verify_client_tls_connection` procedure was enhanced and simplified to handle previously running services
gracefully.

A shell syntax error was fixed in the test case `onbrd_verify_client_tls_connection`, fixing test failures on devices
where the `CA` certificate file needs to be adjusted before the test procedure.

The test case `nm2_set_upnp_mode` is now more robust. The client connectivity is maintained until the `UPnP` `WAN` lease
is removed from the `gw` device. The test script waits for the `iptables` rule for some time to allow time to be applied
to the system, instead of testing immediately. The `regex` was made more generic to comply with several different
`OpenSync` versions.

Fixed the `othr_add_client_freeze` test case to support execution on devices using Linux native bridge.

The code for testing the presence of the `CONFIG_CPM_TINYPROXY_PATH` kconfig option has been updated. It not only checks
for the existence of the `tinyproxy` binary at the kconfig specified path but also validates if it is executable.

FSM test cases no longer use hard-coded commands. Only parametrized functions from common shell libraries are used. The
bridge type is now taken into account.

The VPNM test suite was previously executed on all devices with the necessary test case inputs, as there was no reliable
way to determine support on the device. A Kconfig value check was added, that should determine if the device supports
executing tests these tests.

## Common Test Bed Library

### Features

Added `osrt validate-locations [OPTIONS] [LOCATIONS]` tool to validate location configuration files against
`locations_schema.json` using the `JSON` schema data format. There is an option to exclude specified configuration files
from schema validation.

Added support for continuous `ping` on the client devices. The interval can be specified, `sudo` privilege is used for
very small intervals. The interface can be specified. IPv6 is supported.

Client WiFi sniffing: Added optional tcpdump flags and configurable log file. Fixed enabling and disabling sniffing.
Extend capture file download time.

Added the `wait_unavailable()` method for devices. This is useful when a reboot is expected.

Added support for `DFS puncturing`.

Increased unit test coverage.

Docker: Fixed caching and checksumming all direct `Dockerfile` downloads. The `apt install` command can use stale
package data when reusing old images so `apt update` is always run beforehand. All `apt` commands use cache mount. Use
`eatmydata` with all `apt` commands to avoid unnecessary `fsync` and decrease the `docker` image build time. Create
unique docker volumes per user to ensure optimal performance. Support `docker` building from the `home` directory.

Bump versions of the following packages:

- cryptography
- jmeter
- mitmproxy
- protobuf
- pytest
- requests
- ubuntu

Added the following packages:

- aiofiles
- checksumdir
- columnify
- databricks
- dotenv
- jsonschema
- mergedeep
- retry
- sortedcontainers
- sphinxcontrib-programoutput

Removed the following packages:

- chrome
- cmdrunner

Added a method into `pod_api.py` to set the device ethernet interface speed.

Added support for setting 6HGz channel topology.

Added support for setting `ip-type` for multiple nodes.

Added the `wait_for_value()` method to the `Ovsdb` class in `pod_api.py`. The method can be used to wait for a field to
have a specific value.

Added `pytest` fixtures for the `bt1` client.

Added a new ovsdb method `update_value()` to update `OVSDB` values on the device without requiring a `where` statement.

The `WiFi7` client connection procedure is more robust.

Added a `protobuf` file for 5G cellular network `MQTT` information. Added post-processing of the `mac_address` field for
the `LatencyReport` in `MQTT` messages. MQTT messages are now generated using `fake-mqtts` based on messages from all
pods from the location instead of relying only only on messages from the gw node. A new reference of object for
`proto-decoder` is created and separated from the publisher (`fake-mqtt`) and receiver.

Added support for modern `HostKeyAlgorithms` for secure SSH connections to devices.

Added debug level logs to every `SSH` call.

Prefer `SLAAC` over `link-local` `IPv6` addresses when calling `client.get_client_ips()`.

Added a `timeout` parameter to the `run_command()` method in `pod_lib.py`

Test execution is paused in case the testbed is `force-reserved`. The testbed reservation status is gathered in 10
minute intervals, so the effect is not immediate. In case the testbed reservation can not be established again in the
following 6 hours, pytest exits with an error.

Add country code support for Morocco.

Enhance support for `mtk` and `cfg80211` platforms.

### New `osrt` tools

Added new `osrt` tools that replace the legacy CLI testbed tools. See the [user manual](user_manual.md) for more info.

Moved `pipenv` and `venv` outside of docker. Replace `pipenv` with `python` `uv`, a `Rust` based replacement. A new
unique virtual environment is created for every `dock-run` invocation under `/tmp/` due to performance issues. Move UV
cache to named volume, to work around FS slowness on Mac. An `ascii art` warning shows the user when a testbed is
reserved by another user, preventing conflicts in simultaneous access. The new tools are using `processpoolexecutor`
instead of `threadpoolexecutor` to allow for true simultaneous execution of commands on multiple devices. The `osrt`
tools have extensive `help` messages for all commands, sub-commands and options, and feature `tab auto-completion` for
`bash` and `zsh` shells. Piping the output of the `osrt` tools or processing with other tools changes the output from
`pretty` to `json` or `raw`. The `osrt reserve` tool now stores the testbed reservation expiration timestamp and
displays a countdown in the `PROMPT_COMMAND`.

Examples of available commands (not limited to):

``` bash
osrt client connect --bssid=86:9f:07:00:d1:45 --ip-v4=False --ipv6=stateful w2
osrt client upgrade --download-locally
osrt pod boot-partition-switch
osrt pod upgrade-multi 6.4.0,5.8.0 gw,l1
osrt reserve get mytb* --only-free
osrt server ssh-login-logs
osrt server upgrade --version=stable
osrt switch daisy-chain-set gw l1
osrt testbed upgrade --mirror-url=<URL>
```

#### Testbed features

All the tools from the testbed server `home` directory are moved into the `/tools` directory. The network switch
configuration files are moved to the `/srv/tftp/switch-configs` directory.

Added support for setting port isolation on `2.5G` network switches.

Fix an `AssertionError` when the telnet session is not closed in case of failed login attempt to the network switch.

Added support for `Shelly Pro 4PM smart relay` as a type of `PDU`.

Added the ability to limit client device tx power.

Added the ability monitor the `RSSI` of a connected client device.

Collate device temperature reports.

Added support for multiple network switches per testbed in the `osrt switch` tool.

#### Fixes

Fixed client `SNR` retrieval for `QCA`.

Windows clients now trigger a WiFi scan before connecting an access point. Encoding is force changed to UTF-8 for
increased interoperability.

Fixed SSH multiplexing (muxing) to testbed devices. Fixed names are used for establishing SSH connections to devices.
SSH muxing was broken due to a random thread name on the testbed server, which caused the device name and SSH mux file
to be different each time. Connection speed is increased.

## Limitations

- VPNM tests may be executed while VPNM is not supported by the device, if the device has a misconfigured Kconfig file.
- WDS tests may be executed while VPNM is not supported by the device, since there is no Kconfig value to check and the
  feature is not only dependent on the OpenSync version.
- The `test_dm_verify_reboot_reason` test case sometimes causes the framework to disconnect and the test to fail.
- The `test_nfm_nat_loopback_check` test case fails due to a known firmware bug.
- The `test_tpsm_verify_iperf3_speedtest` test case fails due to a known firmware bug.
- The `test_um_corrupt_image` test case fails due to a known firmware bug.
- The rapid changing of channel or bandwidth settings on wireless interfaces sometimes causes the device to take longer
  to respond to the configured values. The tests do not implement dynamic timeouts and sometimes fail as a result.
- The test cases requiring clients to sniff WiFi packets are sometimes unreliable and the packet capture files generated
  by the client in monitor mode are empty.
