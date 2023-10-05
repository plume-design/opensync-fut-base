# Testcase sm_leaf_report

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the SM is reporting the leaf device.

The testcase requires:

- MQTT broker running on RPI server
- DUT to be configured as an AP and connected to MQTT broker
- Leaf to be configured as an STA and connected to DUT

The testcase configures the stats collected on the device by inserting entries into the `Wifi_Stats_Config` table.\
MQTT
messages are parsed and checked for matching values:

- `channel`
- `connection status`
- `mac address`

## Expected outcome and pass criteria

The MQTT messages informing that the leaf report was executed are found.

## Implementation status

Implemented
