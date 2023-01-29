# Testcase onbrd_verify_home_vaps_on_home_bridge

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the home VAP on the selected radio
interface exists and is added to the home bridge.

**Note:**\
Determine the home bridge interface name. Example for PP203X: `br-home`\
Determine interface names in the DUT configuration.\
Names differ from model to model. Example for PP203X (tri-band device):
`home-ap-24`, `home-ap-l50`, `home-ap-u50`.

## Expected outcome and pass criteria

Home VAP is added to the home bridge.\
This is verified by inspecting the `Wifi_VIF_State` for each interface.

## Implementation status

Implemented
