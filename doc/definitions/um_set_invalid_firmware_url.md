# Testcase um_set_invalid_firmware_url

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the UM sets the correct value of the field `upgrade_status` in the OVSDB
table `AWLAN_Node` if an invalid FW URL is set.

## Expected outcome and pass criteria

Download error is indicated by the `upgrade_status` field value `UPG_ERR_DL_FW`.

## Implementation status

Implemented
