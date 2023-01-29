# Testcase um_verify_firmware_url_length

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `firmware_url` field in the
OVSDB table `AWLAN_Node` supports the maximum number of characters specified in
the testcase config.

## Expected outcome and pass criteria

The value in field `firmware_url` of the `AWLAN_Node` table is populated with
an URL of the set length.
