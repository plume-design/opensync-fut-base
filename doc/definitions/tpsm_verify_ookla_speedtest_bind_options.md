# Testcase tpsm_verify_ookla_speedtest_bind_options

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Ookla speedtest binary is present on the system.

## Testcase description

Testcase verifies that the speed test feature can be triggered on the DUT with an additional parameter specifying the
*preferred* interface or IP address to which the ookla agent should bind to in order to perform the speed test. The
interface or ip address can be specified by inserting the respective value to the `st_bind_interface` or
`st_bind_address` field in the `Wifi_Speedtest_Config` table, respectively.

**Note:**\
Speed test feature must be available on DUT.\
The `path` to the binary might differ from model to model.\
The
feature allows users to *suggest* the binding interface/address, hence the test only verifies that suggested values are
actually passed to the ookla agent invocation. A passed test does NOT guarantee that the suggestion was actually
followed by the agent/binary.

## Expected outcome and pass criteria

The table `Wifi_Speedtest_Config` is initially empty. After values are inserted to the `test_type` and
`st_bind_interface`, or `st_bind_address` fields in the `Wifi_Speedtest_Config` table, the speed test is started.

Wait for the results in the `Wifi_Speedtest_Status` table (**Note:** not "State" table, but "Status").\
The wait time
for speed test to finish might differ from model to model.\
Logs indicate that the ookla binary invocation was properly
parameterized.

## Implementation status

Implemented
