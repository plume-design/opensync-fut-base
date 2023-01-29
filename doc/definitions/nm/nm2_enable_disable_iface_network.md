# Testcase nm2_enable_disable_iface_network

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to ensure that the interface can be disabled or
enabled using a setting in the field `network` in the `Wifi_Inet_Config` table
and that the setting is applied to the device - LEVEL2.

## Expected outcome and pass criteria

Interface can be disabled and enabled through the `network` field in the
`Wifi_Inet_Config` table and that the setting is applied to the device - LEVEL2.

The interface is configured in the `Wifi_Inet_State` table.\
The interface is not created on the device when disabled - LEVEL2.\
The interface is created on the device when enabled - LEVEL2.

## Implementation status

Implemented
