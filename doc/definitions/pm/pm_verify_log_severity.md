# Testcase pm_verify_log_severity

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `log_severity` field in the OVSDB `AW_Debug` table can be set to
selected severities for selected OpenSync managers present on the device and that the log file exists and has the
correct contents.

The test is applicable for all devices.

## Expected outcome and pass criteria

After selected log severity is set for selected manager, log file must exist and must contain a string indicating the
manager tested and the selected log severity.

## Implementation status

Implemented
