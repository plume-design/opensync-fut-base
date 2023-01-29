# Testcase fsm_test_if_plugin_can_monitor_group_tag

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that the DPI plugin client can monitor
the `Openflow_Tag_Group` table.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- Configure `Flow_Service_Manager_Config` with core_dpi_dispatch plugin of
  type `dpi_dispatcher` and then configure walleye_dpi of type `dpi_plugin`.
- Configure `walleye_sni_attrs` in `Openflow_Tag_Group` table.
- Run `curl` command from the client for the same endpoint.

The message indicating that the attribute specified in the walleye_sni_attrs
tag is being processed and should be seen in the FSM log.

## Implementation status

Not Implemented
