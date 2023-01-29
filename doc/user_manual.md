# Functional Unit Testing User Manual

## Change log

| Date              | Notes                                                                              |
|-------------------|------------------------------------------------------------------------------------|
| August 9, 2022    | Changes related to model configuration file                                        |
| April 12, 2022    | Content cleanup                                                                    |
| March 31, 2022    | Transferred document from PDF file to Markdown                                     |
| January 7, 2021   | Added sections **Testcase Debugging** and **Executing the Testcases Manually**     |
| December 7, 2021  | Reorganized structure, corrected use of terms `device` and `model`                 |
| November 24, 2021 | Added section **Adding a new device model to the FUT framework**                   |
| November 8, 2021  | Update for release `r_2021_11`                                                     |
| July 28, 2021     | Update for release `dev_2021_07`                                                   |
| May 26, 2021      | Content cleanup                                                                    |
| April 22, 2021    | Move content regarding `OSRT` to separate document. Update for release `r_2021_05` |
| March 25, 2021    | Move section **Quick Setup Guide** into separate document                          |
| March 18, 2021    | Removed **Default USTB Testbed** in favor of **OSRT**                              |

## References

[1] EIN-020-022-501 OSRT Setup Guide\
[2] quick_start_guide.md\
[3] unit_test_guide.md

## OpenSync version info

FUT is part of OpenSync releases, and is tested on reference devices running
OpenSync of that version. The releases follow a monthly schedule. For more
information, see the OpenSync website:
[https://www.opensync.io/documentation](https://www.opensync.io/documentation)

## Glossary

| Term or abbreviation | Meaning                                                                          |
|----------------------|----------------------------------------------------------------------------------|
| CI                   | Continuous Integration                                                           |
| DUT                  | Device under test                                                                |
| FRV                  | Firmware Release Verification - system end-to-end test suite, different from FUT |
| FUT                  | Functional Unit Test or Functional Unit Testing                                  |
| FW                   | Firmware                                                                         |
| GW                   | Gateway device                                                                   |
| OSRT                 | OpenSync Reference Testbed                                                       |
| PDU                  | Power Distribution Unit - remotely managed power switch                          |
| REF                  | Reference - leaf node                                                            |
| RPI                  | Raspberry Pi                                                                     |
| TB                   | Testbed - testing environment comprised of several devices                       |
| USTB                 | Unified Standard Testbed                                                         |
| VLAN                 | Virtual Local Area Network                                                       |

## Notes on terminology

**What is the difference between USTB and OSRT?**

The term **Unified Standard Testbed (USTB)** denotes standard devices, software
images, wiring scheme, and the process for setting up and running a globally
relevant testbed for OpenSync devices. **OpenSync Reference Testbed (OSRT)** is
a commercial product, available to Plume partners, consisting of a fully
assembled USTB with three OpenSync reference nodes. This allows you to use
testing tools for OpenSync devices.

## Introduction

**Functional Unit Testing (FUT)** is a framework developed for OpenSync
integration testing and functional verification. This user manual guides you
through the FUT setup procedure, and explains how to use the framework.

In terms of testcase complexity, FUT stands between the source code unit tests,
which are on the level of C functions, and the end-to-end system testing, which
involves all software components, even the controller. FUT focuses on
individual functional parts of OpenSync at the inter-process communication
level, OVSDB. FUT relies on the premise that testing the individual component
parts gives a good indication of the quality of the entire OpenSync integration
on the system, while there is no need to be comprehensive.

**Why is FUT important?**\
OpenSync uses controller services to provide a large part of advanced
functionality. To enable one or more controller services to communicate with
several device models successfully, an interface must be well defined and
thoroughly tested. FUT focuses on verifying if the device FW works properly
when OpenSync is integrated.

**Does FUT require connection to the Plume Cloud?**\
No. In fact any connection to the cloud controller is forbidden. OVSDB, the
OpenSync Northbound API, is tested independently, without controller services.
To ensure reliability of FUT results, devices under test must not be claimed at
any customer location. Still, the DUT inside the OSRT requires internet access
for various tests.

**What about my testbed?**\
FUT uses the standard commercially available **OpenSync Reference Testbed**
(OSRT). The OSRT is commercially available as a ready-made testbed. To start
working with the OSRT, refer to the document
**EIN-020-022-501_OSRT_Setup_Guide** [1]. The essential steps to start using
the FUT are available in document
[quick_start_guide.md](quick_start_guide.md) [2].

## OpenSync Reference Testbed (OSRT)

A detailed description for the OSRT is provided in a dedicated document
**EIN-020-022-501_OSRT_Setup_Guide** [1].

## FUT framework

The FUT framework runs on the server within the OSRT. By providing the official
OSRT server image, all dependencies are satisfied and the environment can be
unified. No modifications are required to run the FUT framework, except for
special circumstances, detailed in the **EIN-020-022-501_OSRT_Setup_Guide**
[1].

### FUT code structure

This is the FUT directory structure with inline explanations for each
directory:

```plaintext
fut-base/        Top directory of the FUT directory tree
    config       Configuration files for testbed, testcases
    doc          Documentation: release notes, manuals, testcase descriptions
    docker       FUT docker files
    framework    Framework Python files, modules and utilities
    lib_testbed  Testbed and device API library
    resource     Resources needed for execution: FW image
    self_test    Code coverage and unit tests for the FUT framework
    test         Pytest helper scripts for testcase collection
```

### Configuration Files

The FUT framework allows you to configure the testcase execution without the
need to change any test scripts. This is achieved by providing the
configuration files with input parameter values, which are then loaded by the
framework. The included values are used for setup, initialization, and test
execution on the connected devices.

There are three categories of configuration files:

- Testbed configuration
- Model configuration
- Testcase configuration

Model and testcase configurations are device-dependent. The configuration files
are located in the `config/` directory and its subdirectories.

The model-dependent configuration files are located in the directory
`config/model_properties/reference/`.

To help you insert the content into your own configuration files, several
reference configuration directories are available. For demonstration purposes,
let us consider the example of the model `PP203X` with configuration files in
`config/model/PP203X/`.

Configuration files are either Python files containing dictionaries or YAML
files. These configuration files are directly imported into the runtime
environment during testcase execution. It is important to maintain the correct
syntax and structure of the configuration files, while the values of the
parameters in these the configuration files should be adapted to your model.

```bash
config/
├── model
│   ├── ...
│   └── PP203X
│       └── testcase
│           ├── BRV_config.py
│           ├── CM_config.py
│           ├── DM_config.py
│           ├── FSM_config.py
│           ├── LM_config.py
│           ├── NM_config.py
│           ├── ONBRD_config.py
│           ├── OTHR_config.py
│           ├── QM_config.py
│           ├── SM_config.py
│           ├── UM_config.py
│           ├── UT_config.py
│           └── WM_config.py
├── model_properties
│   ├── ...
│   └── reference
│       ├── ...
│       └──pp203x.yaml
├── rules
│   ├── fut_version_map.yaml
│   └── regulatory.yaml
└── testbed
    └── config.py
```

### Testbed configuration

The FUT framework can not be generalized to work with any DUT in advance,
without providing the information specific to the device model. The testbed
configuration file `config/testbed/config.yaml` contains parameters specific to
the individual testbed. This allows the user to specify where the
model-specific configuration directory is located.

The below shown modification example specifies which model directory contains
the DUT device configuration:

```yaml
server:
  host: "192.168.4.1"                           # RPI server IP on management subnet
  username: "plume"
  password: "plume"
  rsa:
    key_path: "/home/plume/.ssh/id_rsa"
    key_pass: "plume"
  curl:                                         # Configuration for web hosted file transfer
    host: "http://192.168.4.1:8000/"
  mqtt_settings:
    hostname: "192.168.200.1"
    port: "65002"
  cloud:
    tls_version: '1.2'
  mgmt_vlan: 1                                  # VLAN 1 is the system VLAN for the FUT testbed
  tb_role: "server"                             # RPI server role in the FUT testbed

devices:
  dut:                                          # Device under test (these entries are modified for each specific device model)
    mgmt_ip: "192.168.4.10"                     # DUT management IP
    mgmt_vlan: 4                                # VLAN of DUT management IP
    wan_ip: "192.168.200.10"                    # DUT WAN IP
    CFG_FOLDER: "PP203X"                        # DUT configuration directory name (the name depends on each specific device model)
    name: "dut"                                 # DUT role in the FUT testbed
  refs:                                         # Reference devices (typically, model "PP203X" is used)
  - mgmt_ip: "192.168.4.11"                     # REF management IP
    mgmt_vlan: 4                                # VLAN of REF management IP
    wan_ip: "192.168.200.11"                    # REF WAN IP
    CFG_FOLDER: "PP203X"                        # REF configuration directory name
    name: "ref"                                 # REF role in the FUT testbed
  - mgmt_ip: "192.168.4.12"
    mgmt_vlan: 4
    wan_ip: "192.168.200.12"
    CFG_FOLDER: "PP203X"
    name: "ref2"
  clients:                                      # Client device
  - mgmt_ip: "192.168.4.13"                     # Client management IP
    mgmt_vlan: 4                                # VLAN of client management IP
    CFG_FOLDER: "rpi_client"                    # Client configuration directory name
    name: "client"                              # Client role in the FUT testbed

network_switch:                                 # Network switch configuration
  Switch:
  - name: "stb-switch"
    type: "tplink"
    hostname: "switch"
    user: "admin"
    pass: "12testtest"
    ipaddr: "192.168.5.254"
    port: "23"
```

#### Model configuration and properties

As mentioned in the section **Testbed configuration**, the FUT framework also
provides model-specific configurations. To provide configurations for your
models, select the existing configuration directories for the FUT framework, or
create such configurations for the new models.

It is mandatory to provide a YAML file for the newly supported models.
For example, the configuration file for our reference model is
`config/model_properties/reference/pp203x.yaml`. The values in this file are
used across several testing frameworks. These files also serve as the initial
input for the controller and optimizer configuration files in later stages of
OpenSync integration.

To support a new device use any file in directory
`config/model_properties/reference/`, make a copy of it and rename it to fit
the name of the new model. Then modify the contents of the file to fit the new
model.

The device configuration file
`config/model_properties/reference/<my_model>.yaml` specifies interface names,
supported channels per radio, model string, OpenSync root directory, device
type (extender or residential gateway), MTU settings, Wi-Fi vendor, etc.

#### Testcase configuration

The directory `config/model/<my_model>/testcase/` contains several Python
configuration files `<suite>_config.py`, each specific for one suite of tests,
defined in the corresponding `pytest` script `test/<suite>_test.py`. For
example, here are the configuration files and `pytest` scripts, all
corresponding to the `BRV` suite - `Basic Requirements Verification`:

```bash
./config/model/<my_model>/testcase/BRV_config.py
./test/BRV_test.py
```

The testcase configuration files are responsible for providing the input
parameters and values to the `pytest` files for testcase collection and
execution. If the testcase directory is empty (has no configuration files), the
files contain an empty configuration dictionary, or if the corresponding
testcase name from the `pytest` file is not present in the testcase
configuration file, the testcase(s) are not collected by `pytest`. This means
that even if the testcase is defined in the `pytest` files, it is not executed
due to lack of configuration files.

The use of configuration files is useful because certain models may not support
specific test suites (OpenSync features). If a device lacks support for some
OpenSync features, test execution is not needed, and configuration file should
reflect the intended coverage.

Here is an example of the possible content for one of the testcase suites:

```python
test_cfg = {
    "brv_busybox_builtins": [
        {
            "tool": "[",
        },
        {
            "tool": "[[",
        },
    ],
    "brv_ovs_check_version": [
        {},
    ],
}
```

#### Special configuration keys

In addition to the testcase input parameters, the testcase configuration may
contain special keys that are not considered as input parameters, but control
the execution of the testcase.

**`skip`**\
Skips the execution of the testcase, while the testcase will still be collected
and will eventually be shown in the report. Usually this key would be used only
for debugging purposes, as testcases that are relevant for the device under
test are executed and either pass or fail, or they should be ignored, provided
there is a good reason to do so. The value is boolean, either `False` or
`True`, the latter skipping the testcase execution. This is a default `pytest`
feature.

**`skip_msg`**\
Used with the `skip` key and provides the information why the testcase is
skipped. The value of the `skip_msg` key is a string.

**`xfail`**\
Marks the testcases, that are expected to fail, but special behavior is
required. If the testcase marked with `xfail` fails, the report will show this
testcase as `skipped`, but will also provide all the logs and execution
details. If the testcase passes, it will be shown as `passed`. This is a
default `pytest` feature.

**`xfail_msg`**\
Used with the `xfail` key and provides the information why the testcase is
expected to fail. The value of the `xfail_msg` key is a string.

**`ignore_collect`**\
Similar to `skip`, but in contrast to being collected and skipped, the testcase
is not even collected. The effect is the same, as completely removing an entry
of this testcase from the testcase configuration file. As a consequence, it is
not counted in the report. The benefit is that the testcase configuration file
can have a unified format among all models, while providing a written
commentary why a particular testcase should be ignored for a particular model.
One example would be that a testcase is not supported on that model, e.g.
establishing an uplink GRE tunnel for a GW only device. The value of the
`ignore_collect` key is boolean, either `False` or `True`, the latter skipping
the testcase execution. It is encouraged to use the `ignore_collect` key
instead of the `skip` key.\
**Note:** Using the `ignore_collect` key has no effect when executing a test
run with a single testcase (or a list of testcases) executed explicitly.

**`ignore_collect_msg`**\
Used with the `ignore_collect` key and provides information on why the testcase
is ignored. This key will not be used in testcase execution, since the testcase
is completely ignored, but is still required in the configuration file for
visual reference. The value of the `ignore_collect_msg` key is a string.

**`test_script_timeout`**\
Provides the user the control over testcase execution timing. This setting
overrides the default value of `test_script_timeout` in the file
`config/model/<my_model>/device/config.yaml`. The time allowed for the testcase
to pass can be extended, for example in longer running tests, or decreased, for
example to limit the timeout it takes for a test to fail, or to enforce timing
KPIs. The value of the `test_script_timeout` is the integer number of seconds.

## Using the FUT framework

For easier use of the FUT framework, the `init.sh` script exposes the common
FUT use cases. The script includes an extensive help message that explains how
to work with the FUT. To display help, go to the top directory of the framework
and execute:

```bash
./init.sh -h
```

The most common execution examples with and without the helper script are:

Collect and execute all tests configured for this model, keep the `pytest`
capture:

```bash
./init.sh
```

Collect and execute all tests configured for this model, print logs to console,
generate the Allure results:

```bash
./init.sh -p -allure allure-results
```

### Execution example

For demonstration purposes, let us imagine the following scenario: a new model
`my_opensync_model` integrated the OpenSync `advanced networking` features. The
user would like to perform tests to verify this.

First, create the correct model configuration directory, and populate this
directory with the testcase configuration file. In this case, we help ourselves
with the NM suite file from the template:

```bash
cd /home/plume/fut-base
mkdir -p config/model/my_opensync_model/testcase
touch config/model/my_opensync_model/testcase/NM_config.py
```

The correct content of each file is essential. In the model configuration file
`device/config.yaml`, make changes compared to the reference file, to match the
new model.

Finally, you must update the model properties file
`config/model_properties/reference/<my_opensync_model>.yaml`. The model is
specified by the value of the `pod_api_model` variable in the device config
file:

```yaml
# Exact model name (case sensitive!)
model_string: my_opensync_model
# DUT type. Available options: extender, residential_gateway
device_type: extender
# Username for device management SSH access (null if not supported)
username: osync
# Password for device management SSH access (null if not supported)
password: osync123
# Is Dynamic Frequency Selection (DFS) supported
dfs: true
# Is controller fully managing Home VAPs
home_ap_managed: true
# Default regulatory domain
regulatory_domain: US
# Location of SSL certificates
cert_dir_path: /var/certs/
# Location for firmware upgrade images
fw_download_path: /tmp/pfirmware
# OpenSync home directory
opensync_rootdir: /usr/opensync
# Append the following locations to the default system PATH
shell_path: /bin:/sbin:/usr/bin:/usr/sbin:/opt/bin:/opt/sbin:/usr/opensync/tools:/usr/opensync/bin:/usr/plume/tools:/usr/plume/bin
# Command for reading system logs (including any parameters, e.g. "cat /var/log/messages")
logread: logread
# 'logread method' for FRV. Available options: logread_v1, logread_v2 (json), logread_v3 (cat <file_name>)
frv_logread: logread_v2
# WiFi chip vendor (a.k.a. device family). Supported options: qca, bcm, mtk, rdk
wifi_vendor: qca
# Does device have a fan for active cooling
active_cooling: true
# Is device able to change the regulatory domain
regulatory_domain_managed: true

# Interface names and radio information (in case of a single 5 GHz radio, use only the '5g' key)
interfaces:
  radio_hw_mode:
    24g: 11n
    5g: null
    5gl: 11ac
    5gu: 11ac
    6g: null

  max_channel_width:
    24g: 40
    5g: null
    5gl: 80
    5gu: 80
    6g: null

  backhaul_sta:
    24g: bhaul-sta-24
    5g: null
    5gl: bhaul-sta-l50
    5gu: bhaul-sta-u50
    6g: null

  backhaul_ap:
    24g: bhaul-ap-24
    5g: null
    5gl: bhaul-ap-l50
    5gu: bhaul-ap-u50
    6g: null

  home_ap:
    24g: home-ap-24
    5g: null
    5gl: home-ap-l50
    5gu: home-ap-u50
    6g: null

  onboard_ap:
    24g: onboard-ap-24
    5g: null
    5gl: onboard-ap-l50
    5gu: onboard-ap-u50
    6g: null

  uplink_gre:
    24g: g-bhaul-sta-24
    5g: null
    5gl: g-bhaul-sta-l50
    5gu: g-bhaul-sta-u50
    6g: null

  phy_radio_name:
    24g: wifi0
    5g: null
    5gl: wifi1
    5gu: wifi2
    6g: null

  radio_antennas:
    24g: 2x2
    5g: null
    5gl: 2x2
    5gu: 4x4
    6g: null

  vif_radio_idx:
    backhaul_ap: 1
    backhaul_sta: 0
    home_ap: 2
    onboard_ap: 3

  radio_channels:
    24g: [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ]
    5g: null
    5gl: [ 36, 40, 44, 48, 52, 56, 60, 64 ]
    5gu: [ 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153, 157, 161, 165 ]
    6g: null

  lan_bridge: br-home
  wan_bridge: br-wan
  management_interface: eth0.4
  primary_wan_interface: eth0
  wan_interfaces: [eth0, eth1, eth0.835, eth1.835]
  primary_lan_interface: eth1
  lan_interfaces: [eth0, eth1]
  ppp_wan_iterface: ppp-wan
  patch_port_lan_to_wan: patch-h2w
  patch_port_wan_to_lan: patch-w2h

# Maximum Transmission Unit (MTU) per link
mtu:
  backhaul: 1600
  uplink_gre: 1562
  wan: 1500

# Key Performance Indicators (in seconds)
kpi:
  # time needed to get shell response after power on
  boot_time: 70
  # time from power on until Bluetooth starts beaconing (if supported)
  bt_on_time: 30
  # power on till gateway connected to the cloud controller (a.k.a. onboarding time)
  cloud_gw_onboard_time: 120
  # power on till leaf pods connected to the cloud controller
  cloud_leaf_onboard_time: 180
  # total onboarding time for a location (gateway with two leaf pods)
  cloud_location_onboard_time: 300
  # time needed to get the first optimization after the location is onboarded
  cloud_first_optimization: 180
  # time needed to change the topology of a location (extended for CAC in case of DFS channels)
  topology_change_time: 120
  # time needed to update network credentials on Home VAPs
  network_credential_update: 10
  # Statistics Manager restart
  sm_restart: 10

# DUT sanity checks to be performed during testing
frv_sanity:
  # file name where syslog is stored
  sys_log_file_name: messages
  # OVSDB tables to be analyzed
  tables: [['AWLAN_Node table'],
          ['Manager table'],
          ['Bridge table'],
          ['DHCP_leased_IP table'],
          ['Interface table'],
          ['Wifi_Master_State table'],
          ['Wifi_Inet_Config table', 'Wifi_Inet_State table'],
          ['Wifi_Radio_Config table', 'Wifi_Radio_State table'],
          ['Wifi_VIF_Config table', 'Wifi_VIF_State table'],
          ['Wifi_Associated_Clients table'],
          ['Radios country code check'],
          ['Syslog sanity check']]
```

**Note:** The capabilities file is shared between several testing frameworks.
These frameworks are generally independent. Not all content of the capabilities
file is used by FUT, but should still be populated, as this will ensure a
smoother transition between stages of OpenSync integration.

The next step is to populate the NM configuration file `testcase/NM_config.py`.
The content determines which tests are available to `pytest` to be collected
along with the available parameters.

**Note:** This is just an example for `NM`, `Network Manager`. Configuration
entries for this and other test suites will differ from this example.

```python
test_cfg = {
    # Creates (updates if exists) interfaces with parameters: if_name, if_type
    "nm2_enable_disable_iface_network": [
        {
            "if_name": "eth0",
            "if_type": "eth"
        },
        {
            "if_name": "wifi0",
            "if_type": "vif"
        },
        {
            "if_name": "wifi1",
            "if_type": "vif"
        },
    ],
    # Creates (updates if exists) interfaces with parameters: if_name, if_type, mtu
    "nm2_set_mtu": [
        {
            "if_name": "eth1",
            "if_type": "eth",
            "mtu": 2000,
            "ignore_collect": True,
            "ignore_collect_msg": "eth1 not present on device",
        },
        {
            "if_name": "eth0",
            "if_type": "eth",
            "mtu": 1400
        },
        {
            "if_name": "wifi0",
            "if_type": "vif",
            "mtu": 1600
        },
    ],
}
```

This kind of configuration allows the `pytest` library to detect 6 testcases: 3
tests from each of the 2 test scripts, but collect only 5, since one is
ignored:

```bash
shell/tests/nm2/nm2_enable_disable_iface_network.sh
shell/tests/nm2/nm2_set_mtu.sh
```

### FUT testcase results

After the tests are executed, they yield test results. There are a few possible
test outcomes, based on default `pytest` library features:

- PASS
- FAIL
- BROKEN
- SKIP
- UNKNOWN (not used in FUT)

The testcases marked as **PASSED** are the ones that experience no assertions
or no Python exceptions are raised. This means that all pass criteria was met
in shell test scripts and propagated into the framework.

The testcases marked as **FAILED** are a bit more tricky to determine fully.
There are several reasons why a testcase might fail: usually an assertion was
not met inside the `pytest` testcase function, or a shell error occurred
(non-zero exit code) that got propagated back into the framework. These are
some examples of reasons for the testcase being marked as failed:

- FutShellException (any failure which is caused by the FUT Shell scripts)
- Any misconfiguration of the channel against ht_mode/regulatory rule
- Any failure of the retrieving data from your device to FUT which is required
  for a specific testcase (VIF states, etc.).

A testcase is marked as **BROKEN** if some error occurred in the Python
framework, but outside the `pytest` test function testcases. These are some
examples of reasons for the testcase being marked as broken:

- Any failure within the FUT framework methods.
- Failures which are caused by the FUT framework during testcase executions,
file transfers, etc.
- Any misconfiguration of testcase configuration, such as missing testcases
argument from test_config, incorrect argument type (string instead of int,
etc.).

A testcase is marked as **SKIPPED**, only if explicitly marked with `"skip":
True` in the testcase configuration file, or a condition within the shell test
script is not met, that is deemed a requirement, for example a required Kconfig
flag.

## FUT framework reporting with Allure

FUT framework uses the `pytest-allure` plugin during testcase execution to
produce results in a format compatible with the **`Allure`** reporting tool.
Viewing the results with Allure is more user friendly than just looking at the
results in the command line, and it is also easier to share.

There are two ways to use the framework reporting possibilities: using the FUT
docker image (see section `FUT web GUI docker container`, or using `allure`
command line tools on your local machine.

To generate and view reports on your local machine:

1. Install the Allure tool.
2. Execute tests on the testbed with the option to generate an Allure report.
3. Transfer the report from the testbed to the local machine.
4. Execute a command to view Allure reports.

The following command which executes all available tests also shows how to
specify the directory into which the Allure results should be placed:

```bash
# Generate allure results using helper script
./init.sh -allure allure-results
```

**Note:** The option to produce results must be provided at test execution
time, not after tests are run, if an Allure report is required.

The generated results are placed in the `allure-results` directory on the
RPI server, where the FUT is executed. The directory stores several json and
plaintext files. The Allure tool uses these files to generate a **report**.
This is an interactive web page, which the user navigates with a web browser on
the local machine.

**Note:** There are no **Allure** tool packages available on the RPI server
image. Generating the Allure reports from Allure results is not possible on
your RPI server natively. It is possible to generate and view the reports on
your local machine, or using a CI tool like Jenkins, which provides its own
**allure-jenkins plugin** for this case. Alternatively, it is possible to use
the FUT docker GUI to create and view reports on the OSRT.

### Installing Allure on your local machine

To view the results in a web browser on a Linux-based system, install Allure on
your machine first. First, download the Allure tool to a directory on your
local machine and unzip:

```bash
wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.13.9/allure-commandline-2.13.9.zip
sudo unzip allure-commandline-2.13.9.zip -d /opt/
sudo ln -s /opt/allure-2.13.9//bin/allure /usr/bin/allure
```

Check if Allure is installed by checking its version:

```bash
allure --version
```

The expected output should look like this:

```bash
user@hostname:~/fut-base$ allure --version
2.13.9
```

### Creating an Allure report

The test results are created by the `pytest` library in the format readable
by the Allure tool during testcase execution by issuing the correct `--allure`
parameter to the `init.sh` start script. After the test execution is complete,
copy the results from the OSRT server to the local machine to create a test
report.

On your local machine, first create the Allure report from the testcase
results:

```bash
allure generate allure-results/ -o allure-report
```

The created report is an interactive web page, that can be served and inspected
with the same Allure tool:

```bash
allure open allure-report
```

### FUT Docker

FUT contains a standalone Docker image for execution of tests in a fixed
environment.

The FUT Docker container is used for testcase execution. It is possible to
execute tests without Docker, by adding the `-nodocker` flag to the `init.sh`
script, but this is reserved for debugging purposes.

The FUT Docker environment also provides a Web GUI with a built-in terminal and
Allure report server, to enable the user to interact with the FUT environment
more easily. Before you can access the Docker web GUI, execute the script
`./dock-run`. This script brings up the Docker container running the web
GUI in the background:

```bash
cd docker/
./dock-run run
```

After the command brings up the Docker container in the background, the web
terminal is accessible via the web browser on your machine. To access the Web
GUI, use the IP address of your OSRT server, and port `8000`, for example:

```plaintext
http://10.1.1.99:8000
```

You will be prompted with a password. Enter `plume` to access the terminal
environment inside the Web GUI. Once you enter the FUT Docker Web GUI, the
landing page displays two tabs:

- Web GUI terminal
- Allure report generator

### FUT web GUI

The use of the Web GUI terminal is equivalent to accessing the OSRT server via
SSH. The user can perform any task in either of the two environments. For
example, you can execute test runs and generate test results within this tab:

```bash
./init.sh -allure builds/example_build_in_web_gui/ -r nm2_set_gateway[config_0]
```

#### Allure report generator

The FUT docker container also provides an Allure report generator. Click on the
**`Allure`** tab in the Web GUI. Following the example test run from above,
where the Allure results are placed into directory
`builds/example_build_in_web_gui` the Allure report can be generated from
Allure results in the Web GUI. Click **`Allure`** tab, then **`Builds`**, then
**`example_build_in_web_gui`**. The report is automatically generated and
displayed. Be advised that due to large file sizes, the report generation may
take some time.

**Note:** It is recommended to use the `-allure` path relative to the top
directory of the FUT framework. For example if the top directory is
`fut-base/`, use `-allure builds/<build-name>` path for test results.

```bash
# Recommended: use relative path on OSRT server
cd /home/plume/fut-base/
./init.sh -allure builds/fut_full_run_1
```

## Additional FUT information

### Ports used in the FUT framework and FUT testcases

The below table is to be used by the user as a reference. The ports in the
table are not supposed to be changed, even when part of the testcase
configuration.

```plaintext
80      Destination port in NM testcases, also used in FSM testcases
1900    UPnP UDP port, used in FSM testcases
5000    UPnP TCP port, used in FSM testcases
5000    Custom FUT nginx instance port with rate limiting for upgrade tests
8000    FUT Docker container GUI, web terminal, and Allure report generator
8080    Port forwarding to network switch GUI
9000    Port forwarding to PDU GUI
65000   Connection to simulated "FUT Cloud" port
```

## Adding a new model to the FUT framework

The goal of the below section is to describe how to add a new model to the FUT
framework, and to enable running the FUT testcases on the new model.

To add a new model for testing, a few steps are required. The steps include
modifying configuration files and adding model specific steps. Modifications
and additions are done in the top framework directory, but some files may be
added to other repositories.

The process can be split into four steps:

1. Adding the new model device configuration files to the framework
2. Configuring the testbed itself
3. Configuring the testcases that will be executed on the new model
4. Providing shell override file(s) with platform and model specific functions

Required files in the framework:

```plaintext
config/model_properties/reference/<my_model>.yaml
config/testbed/config.yaml
config/model/<my_model>/testcase/<suite>_config.py
```

Required files within OpenSync sources, optionally located in `platform` or
`vendor` directories:

```plaintext
platform/<my_platform>/src/fut/shell/lib/override/
vendor/<my_vendor>/src/fut/shell/lib/override/
```

### Adding new model device configuration files

There are a few configuration files that need to be added to the framework. The
file `config/model_properties/reference/<my_model>.yaml` provides device
specific information, that is shared across testing frameworks, and is the base
for controller and optimizer service configuration files as well.

The `model_properties/reference` directory contains other files for reference
models, while the same content within `model_properties/internal` is also
allowed, however not supported or shared with the public.

Any of the existing reference model configuration files can be copied, renamed
and modified to fit the new model.

### Configuring the testbed

The testbed configuration file `config/testbed/config.yaml` refers to
parameters, that are specific to each individual OSRT. The FUT framework must
be aware of the devices inside the OSRT to be able to select the correct
configuration files. Most notably, the entry `"CFG_FOLDER":` selects which
device config files are chosen for `DUT`, `REF` and `client`devices.

### Adding new model testcase configuration files

To provide information which testcases are executed on the new model, the
directory `config/model/<my_model>/testcase/` needs to be populated with
`<suite>_config.py` files, each containing the entire testcase configuration
dictionary for all intended FUT test suites. Any of the existing reference
model configuration files can be copied, renamed and modified to fit the new
model. Special care must be taken to keep the format of the configuration file,
while only the values of the testcase input parameters should be changed.
Adding or removing several configuration entries within a list of test
configurations for a single testcase is allowed, but not modifying the
structure.

### Adding new model shell library overrides

The FUT testcases are implemented as shell test scripts, and the Python
framework serves the purpose of configuration, orchestration and reporting.
Shell test scripts rely on generic implementations of library functions, but
can not all be guaranteed complete portability between device platforms and
models. Specifically, the use of system tools are SDK- and driver-dependent.

It is essential to add the shell library override files for each platform and
model. These contain the platform or model-specific functions, that are
modified to work with the new model. Some library functions in the main
libraries are intentionally left as `stubs` to force the user to reimplement.
Some are assumed portable, but any function can be overridden. All functions
are well documented and should provide enough information to the user to
implement for their own model.

The first level are _platform dependent_ overrides:
`platform/<my_platform>/src/fut/shell/lib/override/<my_platform>_platform_override.sh`.\
There is currently support for three platforms: **Broadcom**, **Qualcomm** and
**cfg80211** open source driver. The support will be extended in the future.

The second level are _model dependent_ overrides:
`platform/<my_platform>/src/fut/shell/lib/override/<my_model>_lib_override.sh`.\
There is currently support for several reference models, and more will be added
in the future.

Any contributions to OpenSync from the open source community are encouraged.

The framework itself determines which platform and model-specific shell
override files are used for the model.

## Testcase debugging

After a testcase failure, it is suggested to learn why the failure occurred,
for example due to a bug in the OpenSync integration on the device. The steps
in the root cause analysis are:

- Examining the logs and test report
- Attempting to recreate the issue
- Manual testcase execution to pinpoint the cause of the issue

If using the top-down approach, the debugging starting point is the Allure
report. Open the list of all executed testcases and navigate to the desired
failing testcase. By clicking the failed testcase, a detailed report opens on
the right hand side of the Allure report.

The text with red background is the actual error that occurred during the test
run and provides the first point of interest. The text would usually give the
initial information about what went wrong and at which point in the framework
the issue occurred. If the failure happened inside an `assert` statement in the
framework, this means that the actual failure happened in the shell test
script. The debugging needs to be done on the level of shell scripts, executed
on the OpenSync devices in the OSRT.

For this reason the FUT framework provides the individual test steps executed
as part of the testcase. Each step has separate logs for easier segmentation of
the entire procedure and to determine the cause more quickly. All steps that
were executed successfully are colored in green, that is, they are marked as
`pass`. The first step that has failed is colored in red and no further
testcase steps will be performed, with the exception of the testcase cleanup,
if implemented.

The logs for every test step can be expanded, which reveals the logs generated
during the execution by both the framework and shell scripts.

### Log segments

While expanding the testcase steps, the generated logs have multiple segments
which are described in the sections below.

**OUTPUT**\
The content of device logs are concatenated into this segment. It is generated
within the shell scripts and libraries and contains the following information:

- Timestamp
- Log level
- The device on which the step is executed (`dut`, `ref`, `client`)
- The command executed on the device

Look out for any [ERROR] logs, indicating possible points of failure.

**INFO-DUMP**\
Additional info about the state of the device. For example content of the OVSDB
tables on the OpenSync devices, or wpa_supplicant logs on the client device.
The content is generated when the shell script exits. The content is defined
within the trap section of the shell.

**LOGREAD** or **LOGREAD-\<device\>**\
This segment is available only if the testcase fails, as this greatly reduces
the amount of data that the test report collects. This section contains system
logs, a part of which are OpenSync logs, and the aim is to provide additional
information about the system at the exact time when a testcase fails.

**FRM**\
Logs generated only by the FUT framework. This is a section used as an overview
of the testcase procedure.

**RECIPE**\
This is a special segment that contains a list of all commands and their input
parameters that were executed during the testcase execution, along with the
device on which they were executed. This is essential for the manual execution,
if the failure needs to be reproduced. From the OSRT server, establish an SSH
connection to the required device(s) involved in the testcase and execute the
command(s) from the recipe steps one by one in the same order as they
are listed.

### Executing the tests manually

FUT allows you to execute the testcases manually, without requiring the
framework. This method is intended for debugging or testcase development, as
many of the steps usually done by the framework must be done by hand. For
example transferring the files to the devices, determining the input
parameters, etc.

The manual testcase execution procedure is similar to executing the test using
the `init.sh` script. In this case, the init script can be used to transfer the
shell scripts to the devices:

```bash
./init.sh -tr
```

Establish a connection to the intended device and navigate to the `FUT-TOPDIR`
directory. This is `/tmp/fut-base/` by default. The steps from the `RECIPE` can
now be executed individually. These may be setup scripts, tools, or test
scripts. A shell script will require the correct input parameters for the
device and model in question. These can be acquired from the `RECIPE` section,
or provided by the user for debugging or development purposes.

Most scripts document the usage as code commentary well enough to allow
user-independent usage and even development of further shell scripts.

During the actual test execution, logs are displayed as if the test is executed
using an `init.sh` script using the `-o` option.

## OpenSync Unit Test execution

FUT framework is able to execute the OpenSync Unit Tests (UT) as an alternative
to manual UT execution. A separate document exists to cover the topics on
executing the UT with the framework with detailed instructions.

[unit_test_guide.md](unit_test_guide.md) [3].
