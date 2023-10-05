# Testcase wm2_wifi_security_mix_on_multiple_aps

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that multiple virtual access points (VAPs) can be created on the DUT. The VAPs
are configured one radio at a time, each with a unique SSID, PSK and radio index. This testcase uses a mix of security
modes, meaning that the configured VAPs do not share one single security mode between them. The current supported
security modes for this testcase are None, WPA2 and WPA3. A client connectivity check is performed on each configured
VAP.

## Expected outcome and pass criteria

`Wifi_VIF_State` table reports that all configured virtual access points exist. A successful connection between the
client and each VAP is established.

## Implementation status

Implemented
