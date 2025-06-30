# Testcase wm2_verify_wpa2_wpa3_enterprise_security

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify the WPA2/WPA3 enterprise authentication process of the client to the AP of the
DUT using a range of possible security options (AKM suites).\\

Firstly, FreeRADIUS server installed on RPI server must be configured on the DUT AP side. On DUT, server credentials are
added to the OVS table `Radius` by populating it with the standard IP addresses and secret passcode of both primary and
secondary FreeRadius servers. Now, `Wifi_VIF_Config` table is configured with one or combinations of the below
`wpa_key_mgmt` on DUT AP side:

- wpa-psk
- wpa-eap
- sae
- ft-sae
- ft-eap
- wpa-eap-sha256

Along with `wpa_key_mgmt`, `pmf`(Protected Management Frame) is configured on the DUT based on the bits MFPC (Management
Frame Protection Capable) and MFPR (Management Frame Protection Required) enabled. The field `pmf` can be set as below:

- disabled(0) → MFPC=0 and MFPR=0
- optional(1) → MFPC=1 and MFPR=0
- required(2) → MFPC=1 and MFPR=1

The client needs to match this on its side by setting 'ieee80211w' parameter (ieee80211w = 0/1/2) accordingly.

Finally, add the `uuid` of the configured primary and secondary servers into `primary_radius` and `secondary_radius`
fields of the `Wifi_VIF_Config` table.

On client side, it is configured with one of the `wpa_key_mgmt` used at the AP side along with `pmf` selected.

**Note:**\
Configure the CA certificate on the client side if TTLS EAP method is used. However, CA certificate is not
mandatory for PEAP method, but validated if supplied.

## Expected outcome and pass criteria

Client should be able to connect to DUT AP when both are configured with the matching `wpa_keymgmts` and `pmf` values.

## Implementation status

Not Implemented
