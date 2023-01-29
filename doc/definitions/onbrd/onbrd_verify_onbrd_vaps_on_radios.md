# Testcase onbrd_verify_onbrd_vaps_on_radios

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the onboarding VAP on selected
radio exists.

**Note:**\
Determine interface names in the DUT configuration.\
Names differ from model to model. Example for PP203X (tri-band device):
`onboard-ap-24`, `onboard-ap-l50`, `onboard-ap-u50`.

Testcase implementation cleans VIFs after testcase execution.

## Expected outcome and pass criteria

Onboarding VAP on the selected radio interface exists.\
This is verified by inspecting the `Wifi_VIF_State` for each interface.

## Implementation status

Implemented
