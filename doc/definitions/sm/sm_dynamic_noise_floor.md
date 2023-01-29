# Testcase sm_dynamic_noise_floor

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the noise value is
contained in the <-120;0> range.
The testcase requires:

- MQTT broker running on RPI server
- DUT to be configured as an AP and connected to MQTT broker

The testcase retrieves the noise value by configuring the
statistics collection on the device by inserting the entries
into the `Wifi_Stats_Config` table.\
MQTT messages are parsed and checked for the following values:

- `noiseFloor`

## Expected outcome and pass criteria

The MQTT messages contain information about the noise value.
The noise value is contained in the <-120;0> range.

## Implementation status

Implemented
