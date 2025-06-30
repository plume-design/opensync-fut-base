# Testcase dm_verify_max_memory

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

Check if the file `${INSTALL_PREFIX}/etc/kconfig` contains the entries `CONFIG_DM_OSYNC_CRASH_REPORTS=y`. If not,
skip the test.

## Testcase description

The goal of this test case is to verify whether the `DM` takes the correct action when an `OpenSync` process consumes
too much memory (`PSS`). In that case, the process is aborted by `DM`, the default recovery action is taken, and the
process crash is also reported via the `Crash/Reports` `MQTT` topic using a predefined `JSON` report structure.

First, the `MQTT` broker is set up on the testbed server, and then the `max_memory` limit for the selected `OpenSync`
process is reduced in the `Node_Services::other_config` field to trigger the memory exceeded event. The value is low
enough to always trigger a memory exceeded event.

After the process is aborted by `DM`, an `MQTT` message is sent, and finally, the `max_memory` limit is restored to the
original value.

## Expected outcome and pass criteria

1. The `max_memory` value in the `Node_Services::other_config` field is temporarily reduced.

2. `DM` takes action within  60 seconds.

3. An `MQTT` message is sent to the broker. The test collects the message, which says  `Maximum memory limit exceeded`.

## Implementation status

Implemented.
