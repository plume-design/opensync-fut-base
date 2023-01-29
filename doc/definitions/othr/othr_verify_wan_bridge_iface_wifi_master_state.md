# Testcase othr_verify_wan_bridge_iface_wifi_master_state

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that the `Wifi_Master_State` table is populated with DUT
WAN bridge interface.

**Note:**\
NM must populate the `Wifi_Master_State` table. CM is the manager that uses
information from the `Wifi_Master_State` to establish the up-link connection.

## Expected outcome and pass criteria

The `Wifi_Master_State` table exists.
The `Wifi_Master_State` table is populated with WAN bridge interface.

## Implementation status

Implemented
