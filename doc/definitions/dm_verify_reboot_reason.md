# Testcase dm_verify_reboot_reason

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the stored reboot reason is as expected according to the actual reboot type.

The testcase triggers a reboot of the device in many supported fashions, one by one, and after a device reconnects to
RPI server, the testcase verifies that the reboot file holds the correct information according to the last reboot.

During this testcase, the device will reboot and will lose connection to the RPI server. RPI server will detect the lost
connection to the device, and will start the re-connection procedure.

Reboot types are the following:

- CANCEL
- UNKNOWN
- COLD BOOT
- POWER CYCLE
- WATCHDOG
- CRASH
- USER
- DEVICE
- HEALTH CHECK
- UPGRADE
- THERMAL
- CLOUD

**Note:**\
Currently supported reboot types are USER reboot, CLOUD reboot, and COLD BOOT reboot.

## Expected outcome and pass criteria

After reboot, the reboot file holds information about the last reboot.\
The information matches the actual last reboot
type.

## Implementation status

Implemented
