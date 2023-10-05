# Testcase um_set_upgrade_dl_timer_end

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server. The corresponding MD5 file is available on the RPI server.

## Testcase description

The goal of this testcase is to verify that the FW image download process completes within the given time.

Download must start after the `firmware_url` and `upgrade_timer` fields in the OVSDB table `AWLAN_Node` are correctly
set.

Download of the image must end within the given time.

End of the download is verified by observing the `upgrade_status` field in the `AWLAN_Node` table.

## Expected outcome and pass criteria

Start of download is indicated by the `upgrade_status` field value `UPG_STS_FW_DL_START`.\
End of download is indicated
by the `upgrade_status` field value `UPG_STS_FW_DL_END`.\
The time it takes to download the image must not exceed the
given time.

## Implementation status

Implemented
