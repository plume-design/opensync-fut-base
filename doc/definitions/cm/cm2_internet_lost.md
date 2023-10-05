# Testcase cm2_internet_lost

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Make sure DNS traffic is unblocked.\
Make sure DNS traffic is unblocked.\
Add bridge interface WAN (the device is the
gateway).\
Restart all managers.\
Make sure the default gateway is configured.

## Testcase description

The goal of the testcase is to check CM increments the field `unreachable_internet_counter` in the OVSDB table
`Connection_Manager_Uplink`.\
The unreachable_internet_counter value must reach the required value when the internet is
blocked, and it must be reset to zero, when the internet is again unblocked.\
Blocking is performed by manipulating the
iptables firewall rules on the OSRT's RPI server.

## Expected outcome and pass criteria

The `unreachable_internet_counter` field is incremented to the desired value if the internet traffic is blocked.\
The
`unreachable_internet_counter` field is reset to zero after the internet traffic is unblocked.

## Implementation status

Implemented
