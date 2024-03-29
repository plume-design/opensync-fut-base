# Testcase qm_telog_validate

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to ensure that the time event logging works on the device.

Issue a time event log using the command line tool `telog`.

## Expected outcome and pass criteria

The device system logs contain time event log messages from the command line tool `telog`.

## Implementation status

Implemented
