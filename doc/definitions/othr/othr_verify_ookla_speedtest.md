# Testcase othr_verify_ookla_speedtest

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Ookla speedtest binary is present on the system.

## Testcase description

Testcase verifies that the speed test feature can be triggered on the DUT by inserting the value to the `test_type`
field in the `Wifi_Speedtest_Config` table.

**Note:**\
Speed test feature must be available on DUT.\
The `path` to the binary might differ from model to model.

## Expected outcome and pass criteria

The table `Wifi_Speedtest_Config` is initially empty. After the value is inserted to the `test_type` field in the
`Wifi_Speedtest_Config` table, the process is started.

Wait for the results in the `Wifi_Speedtest_Status` table (**Note:** not "State" table, but "Status").\
The wait time
for speed test to finish might differ from model to model.

## Implementation status

Implemented
