# Testcase cpm_spawn_three_update_one

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot. Ensure the OpenSync version is 5.6.0 or greater.

## Testcase description

Insert three entries into the `Captive_Portal` table to spawn three `tinyproxy` processes. After updating one of the
entries, the statuses in the `Captive_Portal` table must match `tinyproxy` processes on the system.

## Expected outcome and pass criteria

The status of the updated `tinyproxy` processes must match the changed entry in the `Captive_Portal` table. The statuses
of the other `tinyproxy` processes must match the unchanged entries in the `Captive_Portal` table.

## Implementation status

Implemented
