# Testcase fsm_test_new_tag_addition

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the DPI plugin client can monitor the `Openflow_Tag` table for the new tag
value that is being added.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- Configure `Flow_Service_Manager_Config` with core_dpi_dispatch plugin of type `dpi_dispatcher` and then configure
  walleye_dpi of type `dpi_plugin`.
- Configure `walleye_sni_attrs` in `Openflow_Tag` table.
- Update `walleye_sni_attrs` with a new value.
- Check the FSM log.

The message indicating that the new attribute value added to `walleye_sni_attrs` tag is being processed should be seen
in the FSM log.

## Implementation status

Not Implemented
