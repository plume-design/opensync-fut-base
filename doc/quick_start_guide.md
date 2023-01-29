# FUT Quick Start Guide

This guide explains the basic steps to set up, run, and debug your FUT test
suite.

## Environment

The FUT test suite is executed on the OpenSync Reference Testbed (OSRT). This
is a requirement, as it ensures a unified execution environment and minimizes
the chances for misconfiguration.

Refer to the document **EIN-020-022-501_OSRT_Setup_Guide** for more
information.

If you are using a prebuilt and preconfigured OSRT, skip the environment
chapters and proceed to the **FUT execution** chapter.

### DUT prerequisites

- Unlimited management access via VLAN 4 on LAN port.
- SSH access to the device with username and password over VLAN 4.
- The DUT user must be a super user (`root`) to execute all tests successfully.
- The `scp` command is needed to transfer the shell scripts.
- `/tmp` must be mounted with an `exec` flag or the default directory for FUT
  (`/tmp/fut-base/`) should be changed to the directory where script execution
  is enabled in the device configuration file.

### Configure the RPI server/client

The image files for your RPI server and client devices are part of the OSRT.
Refer to the **EIN-020-022-501_OSRT_Setup_Guide**, section Flashing Procedure.

### Configure the network switch

Network switch configuration file is part of the OSRT package, but the
configuration file is also stored on the RPI server:
`/home/plume/config-files/`.

1. If the switch has been reset to factory defaults, connect your computer to
   **Port 1**. This port remains unconfigured even after applying the FUT
   config file.
2. Log into the switch. IP: `192.168.0.1`; username/password: `admin/admin`.
3. Apply the FUT switch configuration:
    - Go to **System > System Tools > Restore Config**.
    - Click **Browse** to select the switch configuration file.
    - Click **Import**. This applies the configuration from the file to the
      startup configuration of the system, and reboots the switch.

### Connect the devices

Follow the wiring diagram in **EIN-020-022-501_OSRT_Setup_Guide** to connect
all devices.

### Enable device connectivity and create IP reservations

Connect your computer and OSRT uplink in the corporate network. All devices
receive their IP addresses from the DHCP server running on the RPI server. The
devices are accessible via management SSH access: VLAN 4 subnet for all devices
and clients, from the RPI server.

Before running FUT, IP reservations are required. Run the script on the RPI
server to make sure the correct devices are accessible on their default IP
addresses.

**Access the RPI server using SSH:** `ssh plume@10.1.1.99`
(*example IP address*) and execute:

```bash
user@hostname:~ $ cd /home/plume/dhcp/
user@hostname:~/dhcp $ sudo ./dhcp_reservation.py
```

**Important!** If all entries in file `/etc/dhcp/dhcpd.reservations` are not
correctly edited by the tool, apply the correct reservations manually, e.g. for
`leaf1_wan` and `leaf2_wan`.

## FUT execution

### Create the FUT shell script tar file

From the OpenSync root directory run the below command to create a tar file
which includes the FUT shell test scripts:

```bash
make fut TARGET=alltargets
```

The tar file is created in `images/` subdirectory. Copy the created tar file to
the RPI server (*example IP address*):

```bash
scp <tar_file_name>.tar.bz2 plume@10.1.1.99:/home/plume/fut-base/resource/shell/
```

Make sure only one tar file exists in the destination directory.

## Execute the FUT tests and generate the Allure report

Access the RPI server using SSH: `ssh plume@10.1.1.99` (*example IP address*).

Examine and possibly modify the testbed configuration file
`config/testbed/config.yaml` to match the device types in the OSRT.

The `init.sh` script should be used to invoke the FUT test runs. The script
includes its own help: `init.sh -h` and should be used for advanced invocation.

Example: By executing the command below all tests are executed and results are
generated in a format usable by the Allure report tool.

```bash
./init.sh -allure builds/allure-results
```

Read more about the Allure reports and how to generate them in the **FUT User
Manual**: [user_manual.md](user_manual.md),
section Allure Report Generator.

## Troubleshooting

### Debugging a failing testcase

For the testcase in question, check shell and debug logs in the Allure report.
Look for error messages. The FRM section shows framework logs. The RECIPE
section contains test steps with all input attributes needed to manually
execute the test steps and to help debug on the devices themselves. Copy and
manually execute the script with arguments on the device indicated in the
recipe. Check the logged result of each script to identify where the error
occurred.

When changing any test script, make sure you make the changes on the RPI server
and transfer these changes to the device using the `./init.sh -tr` command.
Changes made to the scripts directly on the device will be lost when you run
FUT via the framework from the RPI server, as the files are transferred from
server to devices upon each execution.

Recipe example:

```bash
# device dut, start: 07:00:26, end: 07:00:46, exit_code: 0
/tmp/fut-base/shell/tests/nm2/nm2_setup.sh wl1 wl0 wl2
...
# device dut, start: 07:16:32, end: 07:16:36, exit_code: 0
/tmp/fut-base/shell/tests/nm2/nm2_set_inet_addr.sh  wl1 vif 10.10.10.30
```

### Which scripts are executed for a single testcase? In which order?

In case there are multiple scripts executed, the framework log lists all
scripts and their execution order, as well as the device on which the scripts
are executed.

## Shell library override files

Any platform or model dependent function from the common FUT shell libraries
must be overridden for your model using the "shell library overload files".
These files implement the same function with the same name, but with a
different content, that fits that platform or model. The override files are
located in the main OpenSync repo, vendor or platform OpenSync repos, or other
repos used for building the OpenSync FW image, for example:

```bash
platform/<platform>/src/fut/shell/lib/override/<platform>_platform_override.sh
platform/<platform>/src/fut/shell/lib/override/<model>_lib_override.sh
vendor/<vendor>/src/fut/shell/lib/override/<model>_lib_override.sh
```

## Additional information

For detailed instructions, read the [**FUT User Manual**](user_manual.md).

For online FAQ visit <https://www.opensync.io/faq-fut>.
