# Testcase dm_verify_opensync_restart

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Check if the file `${INSTALL_PREFIX}/etc/kconfig` contains the entries `CONFIG_DM_OSYNC_CRASH_REPORTS=y` and
`CONFIG_TARGET_RESTART_SCRIPT=y`. If not, skip the test.

## Testcase description

The goal of this testcase is to verify that full OpenSync restarts are correctly reported via the Crash/Reports MQTT
topic using a predefined JSON report structure.

The testcase triggers an OpenSync restart by sending a signal segmentation violation (SIGSEGV) to DM. Because this is
the parent process tasked with controlling other managers, OpenSync is entirely restarted when it crashes.

Check if the process `dm.slave` is running. This is the process which will trigger the OpenSync restart and spawn another
instance of itself before being terminated when it receives a SIGSEGV.

Periodically check if a crash report file with fields `name` and `reason` set to specific values exists in
`/tmp/osync_crash_reports/`. Several crash report files may be located in this directory and checking for the correct
`name` and `reason` is mandatory. The file is deleted once the device reconnects to the MQTT broker and the crash
report is sent as an MQTT message to the Crash/Reports topic which is why the directory must be checked in for new files
in short intervals.

Check that the OpenSync restart is sent as an MQTT message to the Crash/Reports MQTT topic in the form of a JSON object.
Several crash reports files may be sent while the test is executing which is why checking for the correct `name` and
`reason` is mandatory.

Check that the crash report file in `/tmp/osync_crash_reports/` was deleted after the report was sent.

## Expected outcome and pass criteria

The process `dm.slave` must be running.

A file in `/tmp/osync_crash_reports/` with a line starting with `name`, followed by `OpenSync` must be found. There should
also be a line starting with `reason`, followed by `OpenSync restarted by dm_manager_kill` which is the name of the C
function which triggered the restart.

An MQTT message must be found where the content is a JSON object with keys `name` and `reason` equal to the values found
in the previous step.

The crash report file in `/tmp/osync_crash_reports/` does not exist any longer.

## Implementation status

Implemented.
