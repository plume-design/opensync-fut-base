# Testcase cm2_link_lost

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the CM sets a correct value for
the physical link state for an interface when it is brought up or down.\
The state is indicated by the field `has_l2` in the OVSDB table
`Connection_Manager_Uplink`.\
Manipulation of the interface state is performed administratively.

## Expected outcome and pass criteria

When the interface is brought down the value of the `has_l2` in the OVSDB table
`Connection_Manager_Uplink` must become `false`, indicating the link interface
is down.\
When the interface is brought up the value of the `has_l2` in the OVSDB table
`Connection_Manager_Uplink` must become `true`, indicating the link interface
is up.

## Implementation status

Implemented
