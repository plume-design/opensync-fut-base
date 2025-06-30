# Testcase fsm_test_new_tag_deletion

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the DPI plugin client can monitor `Openflow_Tag` table for the tag value
being removed.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- Configure `Flow_Service_Manager_Config` with core_dpi_dispatch plugin of type `dpi_dispatcher` and then configure
  walleye_dpi of type `dpi_plugin`
- Configure `walleye_sni_attrs` in `Openflow_Tag` table.
- Update `walleye_sni_attrs` to remove one of the existing attribute values.
- Check the FSM log.

Attribute removed from `walleye_sni_attrs` should not be processed by the FSM.\
FSM log should indicate that the
attribute is not being processed.

## Implementation status

Not Implemented
