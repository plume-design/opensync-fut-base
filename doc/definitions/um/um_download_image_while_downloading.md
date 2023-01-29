# Testcase um_download_image_while_downloading

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available at RPI server.
Corresponding md5 file is available at RPI server.

## Testcase description

The goal of this testcase is to verify correct behavior of the device if
download of the FW image is triggered while previous download is still in
progress.

During the testcase preparation the second FW image is generated with different
name to the original.

Image is first downloaded. Download must start after the `firmware_url` field
in the OVSDB table `AWLAN_Node` is correctly set. After the download process
started, the `firmware_url` field is again set with path to the second image.

First download must not be interrupted and must finish, which is indicated by
the `upgrade_status` in the `AWLAN_Node` table.

## Expected outcome and pass criteria

End of download is indicated by `upgrade_status` field value
`UPG_STS_FW_DL_END`.
