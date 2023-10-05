# Testcase dm_verify_reboot_file_exists

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the reboot file exists, is not empty and that the reboot file holds the
string "REBOOT".

During this testcase, the device will not reboot. The testcase assumes that the device has been reset at least once in
the past.

## Expected outcome and pass criteria

Reboot file exists, is not empty, and holds the string "REBOOT".

## Implementation status

Implemented
