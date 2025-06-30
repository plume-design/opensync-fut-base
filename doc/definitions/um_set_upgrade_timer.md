# Testcase um_set_upgrade_timer

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server. The corresponding MD5 file is available on the RPI server.

## Testcase description

The goal of this testcase is to verify that the FW upgrade process is started after the delay configured in the field
`upgrade_timer` in the OVSDB table `AWLAN_Node`.

The image is downloaded first. The download of the FW image must complete.

After a successful download, the FW upgrade start must be delayed for the given time after the `upgrade_timer` field is
set. To skip the upgrade process, the FW image is deleted from the device immediately after the `upgrade_timer` field is
set. After the FW image is deleted, we expect an upgrade error. Verify the upgrade status by observing the
`upgrade_status` field. The value stored in this field indicates the actual FW upgrade status.

Note: Do not confuse fields `upgrade_timer` and `upgrade_dl_timer`! The `upgrade_timer` field is tested here, which is
the delay in seconds after the upgrade process must be started from the time the field is set.

## Expected outcome and pass criteria

The FW image download starts after the set time delay. After the download completes, we start the upgrade process and
check if the time delay is within given params. Then the upgrade fails because the FW image has been deleted before the
upgrade started. The upgrade status is indicated in the `upgrade_status` field in the `AWLAN_Node` table.

## Implementation status

Implemented
