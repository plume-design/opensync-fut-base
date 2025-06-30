# Testcase qosm_verify_adaptive_qos

## Environment setup and dependencies

Ensure DUT is marked as Linux qdisc QoS capable, and Adaptive QoS with cake-autorate capable.
The following Kconfig variables need to be set:

- CONFIG_OSN_LINUX_QOS
- CONFIG_OSN_BACKEND_QDISC_LINUX and CONFIG_OSN_LINUX_QDISC
- CONFIG_OSN_BACKEND_ADAPTIVE_QOS_CAKE_AUTORATE

## Testcase description

The goal of this test case is to test Adaptive QoS configuration with cake shaper configured
via Interface_QoS/Linux_Queue with Adaptive QoS enabled in Interface_QoS,
and AdaptiveQoS custom config applied on top.

## Expected outcome and pass criteria

This test creates two dummy interfaces, one for upstream and one for downstream and configures
cake QoS via IP_Interface/Interface_QoS/Linux_Queue on both interfaces. It verifies that cake
shaper can be configured. It then configures Adaptive QoS on top, for both upstream and downstream,
and verifies that Adaptive QoS is applied (cake-autorate running properly). It then applies
custom Adaptive QoS configuration via AdaptiveQoS table and verifies that the custom configuration
properly reflects in the system (cake-autorate running with modified parameters). It then also
verifies disabling of Adaptive QoS and verifying that it gets disabled on the system.

## Implementation status

Implemented
