# Testcase nm2_verify_linux_traffic_control_rules

## Environment setup and dependencies

Ensure DUT is configured to use the Native Linux bridge instead of the OVS bridge. Kconfig variable
CONFIG_TARGET_USE_NATIVE_BRIDGE is set when the Native Linux bridge is enabled.

## Testcase description

The goal of this test case is to ensure ingress and egress Linux Traffic Control rules can be configured using
`IP_Interface` table.\
Testcase verifies that the setting is applied to the device - LEVEL2.\
Testcase verifies that the
settings are deleted from the device if deleted from the `IP_Interface` table.

## Expected outcome and pass criteria

A non-existent interface is configured in the table `Wifi_VIF_Config`.\
`Interface_Classifier` table entries are
configured one for the Ingress rule and one for the Egress rule.\\

Ingress and Egress Linux Traffic Control (tc) rules are configured on the device - LEVEL2.\
Ingress and Egress Linux
Traffic Control (tc) rules are deleted from the device - LEVEL2.\
OpenSync is running and has not experienced a crash.

## Implementation status

Implemented
