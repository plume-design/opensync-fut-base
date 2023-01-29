# Testcase fsm_configure_test_inline_dpi

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
DUT is configured in Router Mode.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- Openflow rules are configured correctly.
- `iptables` rules are configured to send the packets to NFQUEUE.
- FSM process packets received from NFQUEUE.
- FSM sets the Conntrack mark according to the verdict received from the
  Gatekeeper.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone
  traffic/requests).
- NDP parser is created and the `IPv4_Neighbors` table is populated.
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- `iptables` rules are configured.
- FSM policy is configured in the `FSM_Policy` table.
- Conntrack mark is set according to the Gatekeeper verdict.

`wget` request is made from the client, FSM processes the packet and sets the
Conntrack mark according to the verdict.

## Implementation status

Not Implemented
