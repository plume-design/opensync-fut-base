# Testcase um_corrupt_image

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server. The corresponding MD5 file is available on the RPI server.

## Testcase description

The purpose of this test is to verify that:

- UM terminates gracefully when a corrupted image is specified for upgrade.
- UM sets the correct status value in the field `upgrade_status` of the OVSDB `AWLAN_Node` table.

This means that the MD5 sum is correct, but the FW image does not have the correct binary structure, or that the magic
numbers are not correct or in place.

The image is first downloaded. The download must start after the `firmware_url` field in the OVSDB table `AWLAN_Node` is
correctly set, and must also end. Both start and end are verified by observing the `upgrade_status` field.

The upgrade is triggered by setting the field `upgrade_timer`. The upgrade must not start due to a corrupted FW image,
and must indicate the error.

## Expected outcome and pass criteria

After the FW upgrade is triggered, an error due to corrupted FW image file is indicated by the `upgrade_status` field
value `UPG_ERR_FL_WRITE`.

## Implementation status

Implemented
