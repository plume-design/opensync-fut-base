# Testcase sm_latency_report

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the latency report was executed.

The testcase requires:

- MQTT broker running on RPI server
- DUT to be configured as an AP and connected to MQTT broker
- Client connected to the AP

The testcase configures the stats collected on the device by inserting the entries into the `Wifi_Stats_Config`
table.\
MQTT messages are parsed and checked for matching values:

- `ifName`

which represents the list of all interfaces where we expect data-streams/packets to appear.

## Expected outcome and pass criteria

The MQTT messages informing that latency samples has been gathered on listed interfaces.

## Implementation status

Implemented
