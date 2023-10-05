# Testcase um_set_firmware_url

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available at RPI server. The corresponding md5 file is available at RPI server.

## Testcase description

The goal of this testcase is to verify that the FW image download process completes if a valid FW path is set to the
`firmware_url` field in the OVSDB table `AWLAN_Node`.

The image is first downloaded. Download must start after the `firmware_url` field in the OVSDB table `AWLAN_Node` is
correctly set and must also end, both start and end are verified by observing the `upgrade_status` field.

Both the actual FW image and corresponding `md5.sum` files are downloaded to the device.

## Expected outcome and pass criteria

FW image and corresponding `md5.sum` files are present on the device.

## Implementation status

Implemented
