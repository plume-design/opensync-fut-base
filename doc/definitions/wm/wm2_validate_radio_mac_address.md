# Testcase wm2_validate_radio_mac_address

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the MAC address of the provided radio interface in OVSDB matches the MAC
address retrieved from the system - LEVEL2.

The MAC address is retrieved from the field `mac` in the table `Wifi_Radio_State` for the selected radio interface. The
MAC address is retrieved from the system. This is platform and model dependent and may require shell overrides. The two
MAC addresses are compared.

## Expected outcome and pass criteria

The two MAC addresses are identical.

## Implementation status

Implemented
