# Testcase wpd_stop_wpd

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The testcase stops `WPD` and verifies if system watchdog will reset the system after the preset timeout.

Retrieve the system uptime and remember it.

Restart the `WPD service` on the device for a fresh state. Manually kill the `WPD process`.

Wait for the time with which the system watchdog is configured to bite after `WPD` is killed. The system should still be
alive.

Wait for the time with which the system watchdog is configured to bite after `WPD` is killed for the system to become
unresponsive, indicating that the system watchdog actually reset the system.

Wait for the time specified for the device to boot and management SSH to become available. Validate that the device was
restarted by comparing the system uptime with the stored uptime before the test took place, which should be larger.

## Expected outcome and pass criteria

The system is still running after the time with which the system watchdog is configured to bite after `WPD` is killed.

The system is restarted shortly after that, and surely within another identical time period.

The system uptime before the test is larger than the uptime after the test, verifying that the device was restarted.

## Implementation status

Implemented
