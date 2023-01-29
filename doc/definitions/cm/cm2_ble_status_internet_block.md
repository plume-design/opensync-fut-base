# Testcase cm2_ble_status_internet_block

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Make sure DNS traffic is unblocked.\
Make sure DNS traffic is unblocked.\
Add bridge interface WAN (the device is the gateway).\
Restart all managers.\
Make sure the default gateway is configured.

## Testcase description

The goal of this testcase is to verify the `payload` field in the OVSDB table
`AW_Bluetooth_Config` while blocking and unblocking the internet.\
Blocking is performed by manipulating the iptables firewall rules on the
OSRT's RPI server.

The test is applicable only for devices with Bluetooth capabilities.

## Expected outcome and pass criteria

In the `AW_Bluetooth_Config` table, `payload` value (1st byte) is as expected
when the internet traffic is manipulated.\
When internet is blocked the value of the 1st byte of the field `payload`
must be `0x15`, indicating the internet is down.\
When internet is unblocked the value of the 1st byte of the field `payload`
must be `0x75`, indicating the internet is up.

## Implementation status

Implemented
