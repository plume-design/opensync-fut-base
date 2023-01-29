# Testcase vpnm_ipsec_vpn_healthcheck

## Environment setup and dependencies

- FW with IPSec/IKEv2 functionality (OpenSync 4.4 or newer).
- Ensure DUT is in OpenSync default state, as is after boot.
- VPNM is enabled.
- DUT is configured in router mode.
- `strongSwan` is available on the OSRT server.

## Testcase description

The goal of this testcase is to verify if VPN healthcheck is functional.

## Expected outcome and pass criteria

After VPN healthcheck is configured with a dummy configuration with healthcheck
IP pointing to an IP that is assumed to be always available (not over any VPN
tunnel), field `healthcheck_status` in the `VPN_Tunnel` table should transition
to `ok`.

## Implementation status

Implemented
