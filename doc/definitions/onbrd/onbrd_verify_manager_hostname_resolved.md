# Testcase onbrd_verify_manager_hostname_resolved

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The purpose of this test is to verify that `redirector_addr` can be resolved to
any target host.

For example: `ssl:ec2-54-200-0-59.us-west-2.compute.amazonaws.com:443` should
resolve to: `ssl:54.200.0.59:443`

**Note:**\
To start the resolution from beginning, all managers are restarted before
the testcase execution.

## Expected outcome and pass criteria

Field `redirector_addr` in the `AWLAN_Node` table must exist.

After the `redirector_addr` field is set to `ssl:none:443`, `target` field in
the `Manager` table must be emptied.

After `redirector_addr` field is set to predefined value, `target` field in the
`Manager` table must be resolved to any IP address.

## Implementation status

Implemented
