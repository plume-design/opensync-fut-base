# Testcase cm2_ble_status_cloud_down

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Make sure DNS traffic is unblocked.\
Make sure DNS traffic is unblocked.\
Add bridge interface WAN (the device is the
gateway).\
Restart all managers.\
Make sure the default gateway is configured.

## Testcase description

The goal of this testcase is to verify the `payload` field in the OVSDB table `AW_Bluetooth_Config` during Cloud
blocking and unblocking.\
Blocking is performed by manipulating the iptables firewall rules on the OSRT's RPI server.

Test is applicable only for devices with Bluetooth capabilities.

## Expected outcome and pass criteria

In the `AW_Bluetooth_Config` table, `payload` value (1st byte) is as expected when the Cloud connection is
manipulated.\
When the Cloud connection is blocked the value of the 1st byte of the field `payload` must be `0x35`,
indicating the connection to the Cloud is not established.\
When the Cloud connection is unblocked the value of the 1st
byte of the field `payload` must be `0x75`, indicating the connection to the Cloud is established.

## Implementation status

Implemented
