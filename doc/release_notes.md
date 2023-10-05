# FUT Release Notes

Welcome to OpenSync Functional Unit Testing (FUT) release notes. See what has changed with the latest release.

## Release FUT-2.0

This [version](../.version) of FUT supports the following OpenSync releases:

- 5.4.0.0
- 5.2.0.0

### New Features

The 6GHz radio band requires the `WPA3` WiFi security mode. This is now the default value for all test cases.

With the change in execution from remote to local, the local and remote docker images are now also separate. A testbed
server docker image cleanup script was introduced, which is called at the end of every test session and stops the docker
container on the server, since it is no longer needed.

Redundant files were removed from the FUT framework:

- `framework/lib/test_handler.py`
- `framework/lib/fut_exception.py`
- `framework/lib/recipe.py`
- `framework/tools/cfg_sort.py`
- `framework/tools/get_file_from_device.py`
- `framework/tools/network_switch.py`
- `framework/tools/validate_off_chan_survey.py`
- `config/testbed/config.yaml`
- `docker/fut_interactive.py`

The `DRY-RUN` feature was removed from the framework. The purpose of this feature was to display the entire test
procedure in the test report, for development and debugging, even if the test did not finish executing. This is now less
relevant, since the local execution allows you to add breakpoints into the python code right on your workspace and run
the code live from your command line or IDE.

A `YAML` configuration file was introduced to assemble device requirements of all test suites. This allows the device
setup procedure to perform the device setup only for the devices required by the selected test suite or suites.

Missing test case definition `Markdown` files were added where test cases were already implemented.

The `run_raw` device method now has the option to strip the standard output of any newline characters. This allows the
FUT framework to be executed on devices with newer Linux kernels.

The `FSM` test suite now more closely follows the test case definitions. The FUT MQTT message parsing tool now allows
you to filter messages based on device `node ID`.

You are no longer required to execute the FUT framework remotely on the testbed server. Execution is now local. This
makes the `init.sh` script obsolete, and instead `pytest` is invoked directly. The test suite setup is now a fixture to
ensure automatic execution.

Some test cases from the ONBRD test suite became redundant with the implementation of the test case
`wm2_create_all_aps_per_radio`. This test verifies the setup of all wireless access points per radio required by
OpenSync, in order to provide all features. It is no longer necessary to separately test individual interfaces:

- `onbrd_verify_home_vaps_on_home_bridge`
- `onbrd_verify_home_vaps_on_radios`
- `onbrd_verify_onbrd_vaps_on_radios`

The shell function `disable_fatal_state_cm` was enhanced with reading the `Kconfig` option
`TARGET_PATH_DISABLE_FATAL_STATE`. This retrieves the actual path to the file which prevents the `CM fatal state` and
subsequent reboot of the device, instead of relying on a hardcoded path.

The test case `test_dm_verify_reboot_reason` is enhanced with the option to test for a `COLD_BOOT` reboot.

The `ignore_collect` configuration option is removed from the framework. The previous logic used the test case
generators to expand the inputs into explicit configurations, and adding the `ignore_collect` option to tests that
should not be collected by pytest. Now, the `ignore` option in the test case configuration generator inputs simply
prevents the configuration from being expanded, so pytest has nothing to collect or ignore. This saves one step in the
complexity of the framework, while preserving the ability to ignore certain default test case configuration input
values.

Support checking for different WiFi managers in FUT test cases. This allows you to test different configurations of
OpenSync with the same FUT framework.

The FUT framework in this version was completely restructured along with the way FUT tests are structured and executed.
All FUT test suites are now structured as classes, and the setup procedure has been reduced to a single step. The device
initialization procedure now waits for conditions instead of checking once, eliminating race conditions in some models.
A global test case timeout of 480 seconds was added to the pytest configuration file to ensure test cases that do not
terminate correctly are killed by the framework.

The usage of classes and methods from the common testbed library, like the device API, is now preferred over the unique
implementation in this framework.

The FUT python code is made to conform to the Black Python code formatter style guide. A GitHub action is added that
checks each pull request for compliance with the Black style guide.

The execution of FUT is now done locally instead of requiring the user to remote onto the testbed server and execute FUT
there. All setup of source code is local, and starting the docker container is now local. The FUT framework ensures that
SSH proxy commands are used to access the required testbed and the devices within.

FUT now uses location files where the user configures the physical testbed properties.

The test case configuration generator and input directory structure has been refactored to fit within the FUT
architecture. Generators fit under the framework portion, the inputs fit under configurations, the instructions fit
under documentation. Tiered structure including generic, model specific and platform-specific configuration files was
also established to mimic other configuration types and framework or shell features.

The order of test configuration iteration in the `wm2_ht_mode_and_channel_iteration` test case configuration generator
is changed in order to improve readability of test outputs.

All channels and HT mode test case configuration options are unified for all models.

The FUT documentation is updated to fit the changes in the new version. Redundant documents were removed and merged into
the main `doc/user_manual.md` file. The content of the user manual was updated to agree with recent improvements and
changes to FUT. The `README.md` file was made simpler to provide only the needed information at first glance of the
repository.

The model `MR8300-EXT` changed the `wifi_vendor` configuration in the `model_properties` file from `qca` to `cfg80211`
to correctly reflect the wireless driver used for the device.

The test case `dm_verify_vendor_name_awlan_node` was removed. The vendor name is now checked as part of the test case
`dm_verify_awlan_node_params`.

Renamed everything related to the `LM` test cases to `PM`. This change does affect the test case procedures.

The `COMPAT` test suite was replaced with a module that includes the necessary steps for the setup of FUT. These were
mischaracterized as test cases in the past, they are indeed setup and verification steps for the devices in the testbed.

Replaced the FUT-specific logger with the one developed and maintained in the common testbed library.

Fixed a `FutConfigurator` class issue which prevented it from being instantiated as a singleton.

The FUT GUI was removed. Since the FUT execution is now local, there is no need for this feature.

The `functions.py` file was renamed to `fut_lib.py` and its content minimized.

The `conftest.py` is minimized and now only includes what is necessary to modify the default pytest behavior and does
not implement device or testbed specific behavior.

The FUT framework server handler class is split up into smaller logical chunks and reworked. A new device handler base
class was created and dedicated node, client and server handler classes that inherit from it. Any non-device related
functionality from the former server handler class was moved into other classes or modules.

Default beacon interval configuration values are set at 100, 200 and 400ms.

An `OVSDBConfigurator` class was introduced into the FUT framework to take the roll of loading and storing all
configuration data related to the physical devices involved, test case parameters, test run related information,
general rules, etc.

The interface names and their respective VIF radio indices are now directly loaded from the model properties files.

Shell files used in FUT were removed from the vendor OpenSync repositories and put into the repository containing the
FUT framework.

Shell files used in FUT were removed from the platform OpenSync repositories and put into the repository containing the
FUT framework.

Shell files used in FUT were removed from the core OpenSync repository and put into the repository containing the FUT
framework.

Testbed location files had only a subset of all interface types recognized by OpenSync configured until now:
`backhaul_ap`, `backhaul_sta`, `home_ap`, `onboard_ap`, `uplink_gre`. The following were added to enable more tests to
be executed: `aux_1_ap`, `aux_2_ap`, `cportal_ap`, `fhaul_ap`.

A new test case `wm2_check_wpa3_with_wpa2_multi_psk` was added that tests the coexistence of a WPA3 and WPA2 access
point on the same radio.

The testbed server standard output is now added as an attachment to the Allure report.

Transitioned from explicit FUT test case `config.py` files to a generator class that takes much more succinct
`inputs.py` files and expands them for each model. This enables users much greater clarity in what is executed and
eases the creation of test case configuration for new models.

Updated `IPQ807X-AP-HK09` test case configurations for stability and reproducibility.

#### Common Test Bed Library

The device upgrade procedure in the common library was stabilized by introducing additional delays to allow the device
to respond.

The pset tool to determine the testbed in use by docker in the common library now works on case-insensitive file
systems.

Enhancements were made to regulatory domain (region) logic in the common library. This determines the regulatory
constraints of the device more reliably and ensures correct test behavior.

An error is logged in the `execute_command` in `util/ssh/parallelssh` in the common library in case the `sshpass` tool
is missing on your system.

A python decorator called `threaded` was added to `common/util` in the common library. This enables developers to run
some functions in parallel.

The use of a host name was replaced by the use of an IP address for IPv6 ping-check in the common library. This makes
IPv6 test cases more reliable.

The common library now has an option to connect windows clients to a wireless access point.

Support for MAP-T and MAP-E VLANs was added to the common library. Together with changes in the testing environment,
this enables execution of new test cases.

Support for devices using LinuxSDN (Linux Native Bridge) was added to the common library. There is a capability to
detect the bridge type: is the device using Linux Native Bridge or OVS Bridge.

Environment variables are used to build and run the docker container in the common library. Variables can be overridden
from a calling script enabling several test frameworks to use the same common testbed library.

An extra Dockerfile can now be passed to dock-run in the common library. This enables several frameworks using the same
common testbed library to add additional features to the standard docker image.

The docker in the common library now generates and mounts `passwd` and `group` files. This extends the possibilities for
successful execution from your local system to remote test environments with different credentials as well.

BuildKit is now used for building docker images and adding package caching in the common library. BuildKit allows you to
mount docker managed temporary volumes during image builds and use them for package manager caches. The volumes persist
between builds, so the downloaded packages can be reused in the next build, even when a step in Dockerfile changes.

Python pip now always builds wheels for source packages when building a docker container in the common library. This
makes rebuilds faster, even when the recipe for the docker image changes.

The python interpreter version can now be specified in the common library docker with pyenv.

The following packages were added to the common library docker Pipfile: `Pillow`, `arrow`, `black`, `cassandra-driver`,
`dateparser`, `jellyfish`, `nslookup`, `packaging`, `qase-pytest`, `simple-salesforce`, `slack-sdk`, `validators`.

The common library API is enhanced with several new methods:

- `pod_lib`: `get_beacon_interval`, `get_client_snr method`, `opensync_version`, `eth_connect`, `eth_disconnect`,
  `get_parsed_conntrack_entries`, `get_pid_by_cmd`, `get_name`, `get_bhal_24_mac`
- `base_lib`: `get_wan_port`
- `client_lib`: `_wait_for_dhcp_lease`
- `switch_api_generic`: `get_default_port_vlan`
- `util/common`: `get_module_parameterization_id`
- `pod/generic/capabilities`: `Capabilities.get_all_supported_radio_channels`
- `device_api`: `DevicesApiIface`

Packet sniffing utility code for client traffic is now available in the common library.

Client IPs are now retrievable in the common library from point-to-point interfaces.

The `ClientApi.eth_disconnect` in the common library now disables the pod port if it is unused. The old behavior is
still available with the `disable_unused_ports=False` parameter.

Recover gracefully instead of failing and exiting where configuration options required by the common library are
missing.

Both `stdout` and `stderr` are now redirected when putting a command in the background in the common library. The
process put into the background can otherwise remain attached to the SSH session in some versions of the
`openssh server`.

The `os.path.realpath` was replaced with `pathlib.Path.absolute` in the common library. This respects symlinks and keeps
the directory structure correct when resolving the symlinks would provide the incorrect path to the files. This makes
using the common testbed library more robust when implemented in different test frameworks.

The `mqtt/mqtt_client.py` tool in the common library now supports MQTT report pre-processing and decoding of the
`resDesc` value from the `mDNS` topic.

The MQTT `protobuf` schema in the common library was extended to support additional functionality. This keeps up with
newer OpenSync versions.

Custom object instantiation in the common library is now done with pytest fixtures.

Pod fixtures in the common library were updated:

- `pods` fixtures now request `gw,l1,l2` simultaneously to provide speed enhancements.
- The mechanisms to resolve and discover devices are now based on the device index instead of the device name, improving
  reliability.
- Class hinting is now simplified, which improves code quality.

The `iperf` and `iperf3` fixtures are now available in `osrt_fixtures` in the common library. This enables new test
cases.

The Python Black formatting tool was added to ensure unified python code formatting across the entire common testbed
library. A black configuration file enforces code styling rules.

### Fixed Bugs

The `UM` test suite now executes reliably.

The command for getting the pid of a process in `pod_lib` in the common library is now fixed.

The input arguments of the `rpower` tool in the common library are now fixed. You are now required to provide a list of
devices to perform the action on for some commands of this tool.

A possible infinite recursion in the `Logger` class in the common library is now fixed. The problem would sometimes
exhibit when using testbed tools with the `-D` debug flag.

A delay between bringing up an interface and starting the DHCP client in the `ClientLib.eth_connect` in the common
library was introduced. This ensures that the interface is fully operational before the client requests a DHCP lease.

Disabling of the client wireless access points is now executed outside the network namespace in the common library.
Network namespaces are used to simulate individual wired and wireless clients on a single physical device. Disabling the
access points only works outside the network namespace.

System services on the device, controlled by the common library, are now started and stopped in the foreground, in order
to collect the command output.

Fixed the faulty WPA3 compatibility check for PP203X in the FUT override shell script.
