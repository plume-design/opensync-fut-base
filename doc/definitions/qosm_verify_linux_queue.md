# Testcase qosm_verify_linux_queue

## Environment setup and dependencies

Ensure DUT is marked as Linux qdisc QoS capable. The following Kconfig variables need to be set:

- CONFIG_OSN_LINUX_QOS,
- CONFIG_OSN_BACKEND_QDISC_LINUX and CONFIG_OSN_LINUX_QDISC

## Testcase description

The goal of this test case is to test basic Linux qdisc QoS config on an interface via
Interface_QoS/Linux_Queue.

## Expected outcome and pass criteria

This test configures and validates basic Linux qdisc QoS config on an OpenSync node on
a dummy interface by configuring IP_Interface/Interface_Qos/Linux_Queue hierarchy. The test
verifies that that configuration is applied successfully and that any modification of configuration
is applied successfully.

## Implementation status

Implemented
