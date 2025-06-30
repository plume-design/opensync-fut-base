# Testcase vpnm_ipsec_point_2_site

## Environment setup and dependencies

- FW with IPSec/IKEv2 functionality (OpenSync 4.4 or newer).
- Ensure DUT is in OpenSync default state, as is after boot.
- VPNM is enabled.
- DUT is configured in router mode.
- `strongSwan` is available on the OSRT server.

## Testcase description

The goal of this testcase is to verify that VPNM can establish a point to site IPsec tunnel with dynamically assigned
virtual IP and to verify that the tunnel status is correctly updated in the `VPN_Tunnel` OVSDB table and that the
`IPSec_State` fields are correctly updated.

## Expected outcome and pass criteria

After configuring the `VPN_Tunnel` OVSDB table and a corresponding `IPSec_Config` row with a point-2-site configuration,
requesting a virtual IP from the remote, a tunnel is successfully established and entries in `VPN_Tunnel` and
`IPSec_State` tables are correctly populated.

## Implementation status

Implemented
