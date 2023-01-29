# Testcase dm_verify_counter_inc_reboot_status

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that in the OVSDB `Reboot_Status` table,
field `count` is incremented after device is rebooted.\
During this testcase device is rebooted, value of the `count` field is
stored prior to the reboot.

## Expected outcome and pass criteria

The field `count` in the `Reboot_Status` table is incremented by one after
reboot of the device and the reboot reason is `USER`.

## Implementation status

Implemented
