# Testcase um_set_invalid_firmware_pass

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server. The corresponding MD5 file is available on the RPI server.

## Testcase description

The goal of this testcase is to verify that the FW upgrade process fails if an invalid FW password is set to the
`firmware_pass` field in the OVSDB table `AWLAN_Node`.

The image is first downloaded. The download must start after the `firmware_url` field in the OVSDB table `AWLAN_Node` is
correctly set. The download must also end. Both start and end are verified by observing the `upgrade_status` field.

The upgrade is triggered by setting the field `upgrade_timer`, but must not start due to an invalid firmware password.
An error must be indicated.

## Expected outcome and pass criteria

The upgrade error is indicated by the `upgrade_status` field value `UPG_ERR_IMG_FAIL`.

## Implementation status

Implemented
