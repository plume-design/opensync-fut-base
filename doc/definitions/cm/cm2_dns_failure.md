# Testcase cm2_dns_failure

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Make sure DNS traffic is unblocked.\
Make sure DNS traffic is unblocked.\
Add bridge interface WAN (the device is the
gateway).\
Restart all managers.\
Make sure the default gateway is configured.

Make sure the DNS cache is cleared.

## Testcase description

The goal of this testcase is to verify that the Cloud is not resolved if DNS fails. DNS failure is simulated by blocking
the DNS traffic.\
Cloud is resolved after DNS traffic is unblocked.\
Blocking is performed by manipulating the iptables
firewall rules on the OSRT's RPI server.

## Expected outcome and pass criteria

Status of the cloud is observed by inspecting the field `status` in the OVSDB table `Manager`.\
The value must include
word `BACKOFF` when DNS traffic is blocked, and must include `ACTIVE` once the DNS traffic is unblocked.

## Implementation status

Implemented
