# Testcase nm2_ovsdb_remove_reinsert_iface

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to ensure that the interface can be disabled or
enabled through the setting of field `enable` in the `Wifi_Inet_Config` table
and that the setting is applied to the device - LEVEL2.

## Expected outcome and pass criteria

Interface can be disabled and enabled through the field `enable` in the
`Wifi_Inet_Config` table and the setting is applied to the device - LEVEL2.

The interface is configured in the `Wifi_Inet_State` table.\
The interface is not created on the device when disabled - LEVEL2.\
The interface is created on the device when enabled - LEVEL2.

## Implementation status

Implemented
