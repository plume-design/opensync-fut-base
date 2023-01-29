# Testcase wm2_validate_ft_keys_in_hostapd

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to validate Fast BSS transition keys are properly
propagated from `Wifi_VIF_Neighbors` table to hostapd `r0kh`/`r1kh` files.

The testcase first configures the RADIUS server on the DUT by populating the
`RADIUS` table with the standard IP addresses, port numbers and secret passcode
of both primary and secondary FreeRadius servers. Now on DUT, testcase adds the
dummy Neighbor into the `Wifi_VIF_Neighbors` table that is configured with
`wpa_key_mgmt` and `pmf`. `wpa_key_mgmt` list in the table `Wifi_VIF_Neighbors`
must be configured with at least one FT method (`ft-eap` or `ft-sae`).
For example: `wpa_key_mgmt:=["set",["wpa-eap","wpa-eap-sha256","ft-eap"]]`

The testcase verifies the `hostapd-{interface}X.Y.rxkh` file if it contains the
list of `BSSID`, `r0kh:nas_identifier/r1kh:BSSID` and `Encryption` key per AP
interface. Testcase also verifies if

* `nas_identifier` for `r0kh` matches
    * `nas_identifier` in the `Wifi_VIF_Config` table on local interface(self).
    * `nas_identifier` in the `Wifi_VIF_Neighbors` table on external interface.
    * `nas_identifier` defaults to BSSID if `as_identifier` is not set.
* `encryption` key matches
    * `ft_encr_key` in the `Wifi_VIF_Config` table on local interface(self).
    * `ft_encr_key` in the `Wifi_VIF_Neighbors` table on external interface.
    * `ft_encr_key` defaults to OpenSync default value if not set.

## Expected outcome and pass criteria

Testcase passes if `nas_identifier` and `ft_encr_key` keys in the table
`Wifi_VIF_Neighbors` matches the entries of `r0kh`/`r1kh` and `encryption` in
the `hostapd-{interface}X.Y.rxkh` files respectively.

## Implementation status

Not Implemented
