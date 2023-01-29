# Testcase vpnm_ipsec_site_2_site

## Environment setup and dependencies

- FW with IPSec/IKEv2 functionality (OpenSync 4.4 or newer).
- Ensure DUT is in OpenSync default state, as is after boot.
- VPNM is enabled.
- DUT is configured in router mode.
- `strongSwan` is available on the OSRT server.

## Testcase description

The goal of this testcase is to verify that VPNM can succesfully establish a
site to site IPSec tunnel.

## Expected outcome and pass criteria

After OVSDB tables `VPN_Tunnel` and `IPSec_Config` are configured with a
suitable site 2 site configuraion, the IPsec tunnel is established and fields
in the `VPN_Tunnel` and `IPSec_Config` tables are set to expected values.

## Implementation status

Implemented
