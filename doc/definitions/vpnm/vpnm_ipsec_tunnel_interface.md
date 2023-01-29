# Testcase vpnm_ipsec_tunnel_interface

## Environment setup and dependencies

- FW with IPSec/IKEv2 functionality (OpenSync 4.4 or newer).
- Ensure DUT is in OpenSync default state, as is after boot.
- VPNM is enabled.
- DUT is configured in router mode.
- `strongSwan` is available on the OSRT server.

## Testcase description

The goal of this testcase is to verify that a virtual tunnel interface (VTI)
can be successfully created by VPNM.

## Expected outcome and pass criteria

After the OVSDB table `Tunnel_Interface` is configured with interface name,
interface type (VTI) and enabled flag set to `true`, a tunnel interface appears
on the system.

## Implementation status

Implemented
