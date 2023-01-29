# Testcase sm_survey_report

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the survey report scan was
executed.

The testcase requires:

- MQTT broker running on RPI server
- DUT to be configured as an AP and connected to MQTT broker

The testcase performs on-channel and off-channel testing:

- On-channel testing: the channel of the created interface equals the channel
on which survey reporting is configured.
- Off-channel testing: the channel of the created interface does not equal
the channel on which survey reporting is configured.

The testcase configures the stats collected on the device by inserting the
entries into the `Wifi_Stats_Config` table.\
MQTT messages are parsed and checked for matching values:

- `channel`

## Expected outcome and pass criteria

The MQTT messages informing that the neighbor report was executed are found.

## Implementation status

Implemented
