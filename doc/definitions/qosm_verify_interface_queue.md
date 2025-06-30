# Testcase qosm_verify_interface_queue

## Environment setup and dependencies

Ensure DUT is marked as Linux QoS capable. Kconfig variable CONFIG_OSN_LINUX_QOS needs to be set.

## Testcase description

The goal of this test case is to test basic QoS configuration on an interface via
Interface_QoS/Interface_Queue.

## Expected outcome and pass criteria

Rate-limiting QoS is configured on a dummy interface and verified that configuration is applied
successfuly and that any modification of configuration is applied succesfully.

## Implementation status

Implemented
