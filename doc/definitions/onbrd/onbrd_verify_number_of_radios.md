# Testcase onbrd_verify_number_of_radios

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the number of configured radio interfaces for the DUT matches the number of
actual radios of the DUT.

## Expected outcome and pass criteria

The number of configured radio interfaces in `Wifi_Radio_State` must match the number of radios for the DUT. The number
is obtained from the DUT capabilities file.

## Implementation status

Implemented
