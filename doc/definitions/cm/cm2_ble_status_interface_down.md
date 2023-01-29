# Testcase cm2_ble_status_interface_down

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify the `payload` field in the OVSDB
table `AW_Bluetooth_Config` during the drop/up of a link interface.\
Manipulation of the interface state is performed administratively.

The test is applicable only for devices with Bluetooth capabilities.

## Expected outcome and pass criteria

In the `AW_Bluetooth_Config` table, `payload` value (1st byte) is as expected
when the interface state is manipulated.\
When the interface is brought down the value of the 1st byte of the field
`payload` must be `0x01`, indicating the link interface is down.\
When the interface is brought up the value of the 1st byte of the field
`payload` must be `0x75`, indicating the link interface is up.

## Implementation status

Implemented
