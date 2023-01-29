# Testcase othr_verify_eth_lan_iface_wifi_master_state

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that the `Wifi_Master_State` table is populated with
Ethernet LAN interfaces.

**Note:**\
NM must populate the `Wifi_Master_State` table. CM is the manager that uses
information from the `Wifi_Master_State` to establish the uplink connection.

**Important:**\
Determine the Ethernet LAN interface name.\
Make sure the Ethernet LAN interface is present in the `Wifi_Inet_Config`
table. If not, the testcase is invalid, and the interface will not appear in
the `Wifi_Master_State` table. This is not a test failure.

## Expected outcome and pass criteria

The `Wifi_Master_State` table exists.\
The `Wifi_Master_State` table is populated with LAN interface.

## Implementation status

Implemented
