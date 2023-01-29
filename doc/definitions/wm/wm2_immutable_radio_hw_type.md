# Testcase wm2_immutable_radio_hw_type

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to make sure that the immutable field `hw_type`
for the selected radio interface cannot be changed.

## Expected outcome and pass criteria

Field `hw_type` for the selected radio is changed in the `Wifi_Radio_Config` table.

Field `hw_type` for the selected radio must not change and the change must
not be reflected in the `Wifi_Radio_State` table.

## Implementation status

Implemented
