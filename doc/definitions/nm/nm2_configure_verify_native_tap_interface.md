# Testcase nm2_configure_verify_native_tap_interface

## Environment setup and dependencies

Ensure DUT is configured to use the Native Linux Bridge instead of the OVS Bridge. Kconfig variable
`CONFIG_TARGET_USE_NATIVE_BRIDGE` is set when the Native Linux Bridge is enabled.

## Testcase description

This test case aims to ensure that interface of type `tap` can be created when the device is configured to use Linux
Native Bridge.\
Testcase verifies that the settings are applied to the device - LEVEL2.

## Expected outcome and pass criteria

Create the tap interface by configuring `Wifi_Inet_Config` table with `if_type` as `tap`.

Entry should be created for the interface in the `Wifi_Inet_State` table.\
Linux interface is created and is verified
using `ifconfig` command - LEVEL2.\
OpenSync is running and has not experienced a crash.

## Implementation status

Implemented
