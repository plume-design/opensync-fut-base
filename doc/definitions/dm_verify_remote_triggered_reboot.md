# Testcase dm_verify_remote_triggered_reboot

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the device successfully reboots and saves the event in the OVSDB `Reboot_Status`
table with `reason:=delayed-reboot` and `type:=CLOUD` when a remote reboot is triggered.
The following ovsh command is used to trigger the reboot:

```bash
ovsh i Wifi_Test_Config test_id:=reboot params:='["map",[["arg","10 false"], ["path",""]]]'
```

This is equivalent to the transaction performed by the cloud controller when rebooting devices.

## Expected outcome and pass criteria

The device is rebooted and fields `reason` and `type` in the `Reboot_Status` are set to `delayed-reboot` and `CLOUD`
respectively.

## Implementation status

Implemented
