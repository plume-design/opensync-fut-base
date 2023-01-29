# Testcase cm2_cloud_down

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Unblock DNS traffic.\
Unblock SSL traffic.\
Add bridge interface WAN (the device is the gateway).\
Restart all managers.\
Make sure the default gateway is configured.

## Testcase description

The goal of the testcase is to check CM increments the field
`unreachable_cloud_counter` in the OVSDB table `Connection_Manager_Uplink`.\
The `unreachable_cloud_counter` value must reach the required value when the
Cloud is blocked and it must be reset to zero, when the Cloud is again
unblocked.\
Blocking is performed by manipulating the iptables firewall rules on the
OSRT's RPI server.

## Expected outcome and pass criteria

`unreachable_cloud_counter` field is incremented to the desired value if the
Cloud connection addresses are blocked.\
`unreachable_cloud_counter` field is reset to zero after the Cloud
connection addresses are unblocked.

## Implementation status

Implemented
