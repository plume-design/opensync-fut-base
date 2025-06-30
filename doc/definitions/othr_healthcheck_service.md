# Testcase othr_healthcheck_service

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Check if the file `${INSTALL_PREFIX}/etc/kconfig` contains the entry `CONFIG_SERVICE_HEALTHCHECK=y`. If not, skip the
test.

## Testcase description

The goal of this testcase is to verify that the healthcheck service is compiled and running on the device.

Check if the file `${INSTALL_PREFIX}/scripts/healthcheck.service` exists. This is the service file that runs individual
healtcheck scripts, collects potential issues and executes the `healthcheck fatal` protocol, which usually reboots the
device in case a fatal condition is met.

Check if the file `/etc/init.d/healthcheck` exists. This file ensures that the service file is started when the system
boots.

Check if the `healthcheck` service is running by inspecting the `/var/run/healthcheck.pid` file for the `PID` and
ensuring the `/proc/${PID}` directory exists, indicating the process is alive.

Check if the directory `${INSTALL_PREFIX}/scripts/healthcheck.d/` exists. This directory must include but is not limited
to the following files:

``` bash
05_ntp.sh
10_bss.sh
12_dns.sh
15_ap.sh
20_tmp_df.sh
30_netdev_refcount.sh
40_conntrack_overflow.sh
98_file_handles.sh
99_zombie.sh
```

These files are the individual healtcheck scripts that ensure basic operational conditions are met for the device to
remain operational.

## Expected outcome and pass criteria

The file `${INSTALL_PREFIX}/scripts/healthcheck.service` exists.

The file `/etc/init.d/healthcheck` exists.

The `/var/run/healthcheck.pid` file contains the healthcheck `PID` and the `/proc/${PID}` directory exists.

The directory `${INSTALL_PREFIX}/scripts/healthcheck.d/` exists and contains at least the following files:

``` bash
05_ntp.sh
10_bss.sh
12_dns.sh
15_ap.sh
20_tmp_df.sh
30_netdev_refcount.sh
40_conntrack_overflow.sh
98_file_handles.sh
99_zombie.sh
```

## Implementation status

Implemented
