# Testcase dm_verify_opensync_version_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the OVSDB `AWLAN_Node` table field
`version_matrix` holds the information about the installed OpenSync version.

## Expected outcome and pass criteria

The field `version_matrix` has been correctly set by the DM. The field holds
the information about the installed OpenSync version.\
Information about the OpenSync is found after the 'OPENSYNC' string.

## Implementation status

Implemented
