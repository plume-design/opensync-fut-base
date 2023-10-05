# Testcase othr_verify_ethernet_backhaul

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that a wired backhaul connection between the gateway (DUT) and leaf (REF) can be
established and leaf (REF) device can access the internet.

Steps to prepare gateway and leaf for this testcase must be done independently.

Configure gateway WAN and make sure it is correctly configured by pinging some public IP from the DUT.\
Set gateway
(DUT) in Router mode.\
Configure Network Switch of the OSRT using VLAN tags. Network Switch should be configured using
the VLAN on the DUT and leaf (REF) interfaces to establish connection between them. Configure wan ethernet interface on
the leaf (REF) device and run dhcp client. Ping the same public IP from leaf (REF).

If IP is pingable, the connection is established for the leaf (REF) device and verified.

## Expected outcome and pass criteria

A public IP from the leaf device is pingable.

## Implementation status

Implemented
