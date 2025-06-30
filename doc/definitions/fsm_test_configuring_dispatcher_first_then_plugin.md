# Testcase fsm_test_configuring_plugin_first_then_dispatcher

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.

## Testcase description

The goal of this testcase is to verify that DPI dispatcher can be added first and then, the DPI plugin can be added
later in FSM.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- Configure `Flow_Service_Manager_Config` with core_dpi_dispatch plugin of type `dpi_dispatcher` and then configure
  walleye_dpi of type `dpi_plugin`.
- Run `curl` command from the client for the same endpoint.

The Related FSM log from the connected client exists and contains the verdict received from the Gatekeeper service.
\
The FSM process should be running.

## Implementation status

Not Implemented
