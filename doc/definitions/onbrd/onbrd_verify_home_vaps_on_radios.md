# Testcase onbrd_verify_home_vaps_on_radios

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the home VAP on the selected radio
interface exists.

**Note:**\
Determine interface names in DUT's configuration.\
Names differ from model to model. Example for PP203X (tri-band device):
`home-ap-24`, `home-ap-l50`, `home-ap-u50`.

## Expected outcome and pass criteria

Home VAP on selected radio interface exists.\
This is verified by inspecting the `Wifi_VIF_State` for each interface.

## Implementation status

Implemented
