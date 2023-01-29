# Testcase wm2_create_all_aps_per_radio

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that multiple virtual access points
(VAPs) can be created on the DUT. The VAPs are configured one radio at a time,
each with a unique SSID, PSK and radio index. This testcase uses the WPA2
security mode. A client connectivity check is performed on each configured VAP.

## Expected outcome and pass criteria

`Wifi_VIF_State` table reports that all configured virtual access points exist.
A successful connection between the client and each VAP is established.

## Implementation status

Implemented
