# Testcase cm2_dns_failure

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Make sure DNS traffic is unblocked on the server.

Make sure the DNS cache is cleared!

## Testcase description

The goal of this testcase is to verify that the cloud controller (redirector) address is not resolved if DNS fails. DNS
failure is simulated by blocking DNS traffic on the testbed server. The cloud controller (redirector) address is
resolved after DNS traffic is unblocked on the testbed server.

Blocking is performed by manipulating the iptables firewall rules on the tesbed server.

## Expected outcome and pass criteria

Status of the cloud is observed by inspecting the field `status` in the OVSDB table `Manager`.

The value must include the word `BACKOFF` when DNS traffic is blocked, and must include `ACTIVE` once the DNS traffic is
unblocked.

## Implementation status

Implemented
