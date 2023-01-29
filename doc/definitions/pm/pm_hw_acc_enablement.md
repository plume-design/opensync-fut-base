# Testcase pm_hw_acc_enablement

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

This feature is only supported on OpenSync version 4.6 and newer.

## Testcase description

The purpose of this test is to verify the ability to enable and disable
Flow Cache which is controlled by the Platform manager (PM).

The feature is enabled and disabled by the following commands:\
Enable:
`ovsh U Node_Config -w module==pm_hw_acc value:=\"true\" key:=enable`

Disable:
`ovsh U Node_Config -w module==pm_hw_acc value:=\"false\" key:=enable`

Currently, this is supported only on BCM platforms.

## Expected outcome and pass criteria

When the feature is enabled, hardware acceleration should be enabled,
the **value** field in the `Node_Config` and `Node_State` tables should be set
to **true** and the `fcctl status` command should return
`Flow Learning Enabled`. When the feature is disabled, the tables should be set
to **false** and the `fcctl status` command should return
`Flow Learning Disabled`.
