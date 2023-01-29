# Testcase um_set_upgrade_dl_timer_abort

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server.
The corresponding MD5 file is available on the RPI server.

## Testcase description

The goal of this testcase is to verify that the FW image download process
is aborted. Time to download the image is configured in the field `upgrade_dl_timer`
in the OVSDB table `AWLAN_Node`.

Download must start after the `firmware_url` and `upgrade_dl_timer` fields in the
OVSDB table `AWLAN_Node` are correctly set.

Download of the image must be aborted after time configured in the field
`upgrade_dl_timer` (`upgrade_dl_timer` value plus buffer time) expires.

Abortion of the download is verified by checking the `upgrade_status` field in
the `AWLAN_Node` table.

## Expected outcome and pass criteria

Start of download is indicated by the `upgrade_status` field value
`UPG_STS_FW_DL_START`.\
Abort of download is indicated by the `upgrade_status` field value
`UPG_ERR_DL_FW`.\

At the end of the testcase execution, `upgrade_status` must be set with
`UPG_ERR_DL_FW` code or (-4).
