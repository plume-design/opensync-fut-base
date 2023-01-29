# Testcase nm2_ovsdb_ip_port_forward

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that IP port forward rule is created
on the device when configured through the OVSDB `IP_Port_Forward` table.\
Testcase verifies that the setting is applied to the device - LEVEL2.\
Testcase verifies that the settings are deleted from the device if deleted from
the `IP_Port_Forward` table.

Test is only valid if WANO (_WAN Orchestrator_) is disabled, otherwise test is
not applicable for the device.

## Expected outcome and pass criteria

IP port forward is configured at the OVSDB level and on the device - LEVEL2.\
IP port forward is deleted from the OVSDB level and from the device - LEVEL2.

## Implementation status

Implemented
