# Testcase nfm_native_ebtable_template_check

## Environment setup and dependencies

Ensure DUT is configured to use the Native Linux bridge instead of the OVS bridge. Kconfig variable
CONFIG_TARGET_USE_NATIVE_BRIDGE is set when the Native Linux bridge is enabled.

## Testcase description

The goal of this test case is to ensure ebtable with template rules can be configured using `Netfilter` table.\
Testcase
verifies that the setting is applied to the device - LEVEL2.\
Testcase verifies that the settings are deleted from the
device if deleted from the `Netfilter` table.

## Expected outcome and pass criteria

Configure `Netfilter` table with the template rule and the protocol type set to `eth`

Template should be expanded before the rules are applied.\
ebtable rules are configured on the device - LEVEL2.\
ebtable
rules are deleted from the device when `Netfilter` configuration is removed - LEVEL2.\
OpenSync is running and has not
experienced a crash.

## Implementation status

Implemented
