# Testcase onbrd_verify_dut_system_time_accuracy

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
DUT must have internet connectivity, since most devices synchronize their time
with a remote server which must be accessible.

## Testcase description

The goal of this testcase is to verify that DUT date and time are within +/-
time threshold boundaries of the global real-time.

**Note:**\
Get RPI server system time and use this time as an input to the testcase script.

**Important:**\
System time on DUT must not have been manually modified. If so, a reboot of
DUT is required.\
Timestamps must be compared to the same time zone.

## Expected outcome and pass criteria

Compare OSRT RPI server system time with DUT system time.\
Time difference must be within threshold.

## Implementation status

Implemented
