# Testcase ltem_validation

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

LTE functionality must be present on the device.\
LTE signal must be available to the device.

## Testcase description

The goal of this testcase is to validate LTE is running on LTE interface by
checking the correct entries are present in the OVSDB tables `Lte_State`,
`Connection_Manager_Uplink` and `Wifi_Inet_State`.\
The correct entries indicate that the LTE interface is used as WAN interface
when there is an internet outage on the previously used WAN interface.\
The testcase also verifies LTE interface is added to the route table and is
used as the default route in case of internet outage.\
This testcase uses test mode, which is setting the `force_use_lte` field in
the `Lte_Config` table to `true`.

## Expected outcome and pass criteria

The fields in the tables `Lte_State`, `Connection_Manager_Uplink` and
`Wifi_Inet_State` have expected values from the testcase configuration,
indicating the device uses the LTE interface.\
LTE interface is selected as the default route for the device.

## Implementation status

Implemented
