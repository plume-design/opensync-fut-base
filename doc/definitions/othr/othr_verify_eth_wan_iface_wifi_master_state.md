# Testcase othr_verify_eth_wan_iface_wifi_master_state

## Environment setup and dependencies

Testcase verifies that the `Wifi_Master_State` table is populated with
DUT ethernet WAN interfaces.

**Note:**\
NM must populate the `Wifi_Master_State` table, CM is the manager that uses
information from the `Wifi_Master_State` to establish the uplink connection.

**Important:**\
Determine the Ethernet WAN interface name.\
Make sure the Ethernet WAN interface is present in the `Wifi_Inet_Config`
table. If not, the testcase is invalid, and the interface will not appear in
the `Wifi_Master_State` table. This is not a test failure.

## Expected outcome and pass criteria

The `Wifi_Master_State` table exists.\
The `Wifi_Master_State` table is populated with WAN interface.

## Implementation status

Implemented
