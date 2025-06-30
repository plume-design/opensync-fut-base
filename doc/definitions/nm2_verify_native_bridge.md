# Testcase nm2_verify_native_bridge

## Environment setup and dependencies

Ensure DUT is configured to use the Native Linux Bridge instead of the OVS Bridge. Kconfig variable
`CONFIG_TARGET_USE_NATIVE_BRIDGE` is set when the Native Linux Bridge is enabled.

## Testcase description

This test case aims to ensure that Linux Native Bridge can be created and Ports can be added to the Bridge by
configuring the OVSDB `Bridge`, `Port` and `Interface` table.\
Testcase verifies that the settings are applied to the
device - LEVEL2.

## Expected outcome and pass criteria

Create the tap interface by configuring `Wifi_Inet_Config` table with `if_type` as `tap`.\
Create the bridge interface
by configuring the `Wifi_Inet_Config` table with `if_type` as `bridge`.\
Add the configured bridge interface to the
`Bridge` table.\
Enable `hairpin_mode` on the interface.

Linux Bridge is created and is verified using `brctl show` command - LEVEL2.\
The interface is added to Bridge and is
verified using `brctl show` command - LEVEL2.\
`hairpin` mode is enabled on the interface, verified using
`brctl showstp` LEVEL2.\
OpenSync is running and has not experienced a crash.

## Implementation status

Implemented
