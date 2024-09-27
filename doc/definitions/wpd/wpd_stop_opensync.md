# Testcase wpd_stop_opensync

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

To ensure that system logs capture the relevant information pertaining to the test procedure and to minimize the chance
of rotation during the test procedure, the system logs should be rotated immediately prior to starting the test
procedure.

To ensure that system logs can be captured reliably, the `log tailing command` needs to be provided, for example:

* `logread -f`
* `tail -F /var/log/messages`

## Testcase description

The testcase stops `OpenSync` and verifies that `WPD` will attempt to reboot the device after a set time.

Retrieve the system uptime and remember it.

Start capturing system logs into a separate file on the `tmpfs`. The goal is to filter and capture only relevant log
messages for the `WPD` process. **Note** that filtering with external tools and redirecting into a separate log file may
delay the messages as some tools have large buffers and do not flush incoming inputs immediately.

Restart the `WPD service` on the device for a fresh state.

Wait for the time period with which `wpd` pings the system watchdog to ensure one ping is issued to overcome any initial
setup conditions.

Stop `OpenSync` and wait for the time period configured for `WPD` to trigger the system watchdog after it receives no
pings from external applications.

Quickly restart the `WPD service` to ensure the system watchdog gets a ping and does not reset the system.

Ensure `OpenSync` is started to return the system into the default state.

Kill all system log capturing processes put in the background.

Inspect the captured logs for the string `Failed to get ping from managers. Watchdog will soon bite`.

Inspect the captured logs for the string `Setting WD timeout to 3 seconds`.

Validate that the device was not restarted by comparing the system uptime with the stored uptime before the test took
place, which should be smaller.

## Expected outcome and pass criteria

Captured logs contain the string `Failed to get ping from managers. Watchdog will soon bite`.

Captured logs contain the string `Setting WD timeout to 3 seconds`.

The system is still running after the test case procedure finishes. This indicates that expected timings are respected.

The system uptime before the test is smaller than after the test, verifying that the device was not restarted.

## Implementation status

Implemented
