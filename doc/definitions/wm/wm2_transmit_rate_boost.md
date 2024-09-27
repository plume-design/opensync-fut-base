# Testcase wm2_transmit_rate_boost

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the data transmit
rate of the radio interfaces can be adjusted.\
This is done by dropping the 1 Mbps and 2 Mbps rates from the
`supported_rates` and `basic_rates` fields in the `Wifi_Radio_Config`
OVSDB table.\
The `beacon_rate`, `mgmt_rate` and `mcast_rate` fields are adjusted
as well to ensure the desired data transmit rate is used.\
A wireless client running in monitor mode is used to capture beacon
frames sent by the GW AP.\

## Expected outcome and pass criteria

Beacon frames captured on the GW AP should have the specified
data transmit rate.

## Implementation status

Implemented
