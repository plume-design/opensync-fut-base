# Testcase cpm_restart_crashed

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot. Ensure the OpenSync version is 5.6.0 or greater.

## Testcase description

The goal of this testcase is to verify that a new `tinyproxy` instance will be spawned with the same configuration in
case a running instance crashes.

To simulate a process crash, the command `kill <tinyproxy-pid>` is used. The default signal is `SIGTERM`, but others can
be used, for example `SIGSEGV`.

Insert two entries into the `Captive_Portal` table to spawn two `tinyproxy` instances listening on selected IPs and
ports. Obtain and store their `pids` by `pidof tinyproxy` and their `uuids` by parsing `/proc/<pid>/cmdline`.

Use the `kill` command to simulate a process crash in one of the instances.

Obtain the `pid` and `uuid` of the two processes again and compare the old and new values for each of the instances.

## Expected outcome and pass criteria

The running instance, that did not experience a crash has the same `pid` and `uuid`.

The instance that experienced a crash has the same `uuid`, but the `pid` is different to the initial one and matches the
instance that was started after the initial one experienced the crash.

## Implementation status

Implemented
