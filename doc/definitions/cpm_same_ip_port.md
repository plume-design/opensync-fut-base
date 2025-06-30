# Testcase cpm_same_ip_port

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot. Ensure the OpenSync version is 5.6.0 or greater.

## Testcase description

The goal of this testcase is to check that two instances of `tinyproxy` with the same ip and port configurations are not
started.

Insert an entry into the `Captive_Portal` table to spawn a `tinyproxy` instance listening on a selected IP and port.

Insert a second identical entry into the `Captive_Portal` table, listening on the same IP and port. This is a
misconfiguration. `CPM` will attempt to start another `tinyproxy` instance. `CPM` has auto-restart enabled by default,
with a maximum of 10 retries, one each second.

The second `tinyproxy` instance exits immediately after each attempt to start with settings identical to an existing
instance. The exit status is `71`, which means `Could not create listening sockets`.

After 10 failed attempts to start another `tinyproxy` instance, `CPM` will stop further attempts.

Only one `tinyproxy` instance remains running. There is only one `tinyproxy` configuration file remaining on the system,
corresponding to the running instance. The second entry in the `Captive_Portal` table is updated with an error status.

## Expected outcome and pass criteria

One `tinyproxy` instance is running with correct configuration file content, matching the first `Captive_Portal` entry.

The second `tinyproxy` instance is not running, and there is no corresponding configuration file content on the system.

After 10 retries to start the second `tinyproxy` instance, the second `Captive_Portal` table entry is updated with an
error status.

## Implementation status

Implemented
