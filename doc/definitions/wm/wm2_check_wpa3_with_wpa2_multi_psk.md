# Testcase wm2_check_wpa3_with_wpa2_multi_psk

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

A network using WPA3 encryption is configured on the DUT home interface. This network is moved to a new virtual access
point (VAP), and a new network using WPA2 with multi-PSK is configured on the existing home interface.

This testcase tests the coexistence of a WPA3 and WPA2 access point on the same radio. A client connectivity check is
performed on both virtual access points to ensure that they are operational and to verify that the multi-PSK feature
works with the WPA2 encryption as expected.

**Note:**\
The testcase is applicable only on non 6GHz radios.

**Important:**\
The transition of the primary network to a new VAP and the configuration of the WPA2 network must happen
concurrently.

## Expected outcome and pass criteria

`Wifi_VIF_State` table reports both virtual access points exist.

A successful connection between the client and the VAP configured with WPA3 is established.

A successful connection between the client and the VAP configured with WPA2 multi-PSK is established with all PSKs.

## Implementation status

Implemented
