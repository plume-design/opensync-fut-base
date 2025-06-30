# Testcase othr_verify_eth_client_connection

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that a wired connection between the gateway and client can be established and the
client device can be pinged from the gateway.

Establish a wired ethernet connection between the client and gateway. Ensure that the LAN ethernet port on the gateway
is present in the home bridge. The device can operate in either bridge or router mode. Only the client LAN connectivity
is verified. Send a DHCP discover packet from the client to obtain a local IP address.

Check if the `has_L2` field is set to `true` and the `has_L3` field is set to `false` in the `Connection_Manager_Uplink`
table on the gateway for the LAN ethernet interface.

Check if the client MAC address is present in the `DHCP_leased_IP` table on the gateway.

Check connectivity from the gateway device to the client on the obtained IP address with the `ping` command.

## Expected outcome and pass criteria

The `Connection_Manager_Uplink` table on the gateway device is populated correctly for the LAN ethernet interface. The
`DHCP_leased_IP` table contains the MAC address of the client device. The gateway device can ping the client device IP.

## Implementation status

Implemented
