# Testcase othr_verify_gre_iface_wifi_master_state

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Test case verifies that the `Wifi_Master_State` table is populated with DUT GRE interfaces, once they are created.

**Note:**\
NM must populate the `Wifi_Master_State` table. CM is the manager that uses information from the
`Wifi_Master_State` to establish the uplink connection.

## Expected outcome and pass criteria

Created GRE interfaces exist in the `Wifi_Inet_State` table.\
The `Wifi_Master_State` table exists.\
The
`Wifi_Master_State` table is populated with GRE interfaces.

## Implementation status

Implemented
