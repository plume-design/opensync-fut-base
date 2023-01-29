# FUT Unit Test execution

## Introduction

This guide provides information on how to execute Unit Tests (UT) using the FUT
framework. This guide also provides information on how to execute the tests
manually, and inside Jenkins environment, using the FUT framework.

All UTs are provided as small programs which are essentially copied to the Pod
and executed on the Pod itself. What is tested are C functions, building blocks
of OpenSync. UT lies below FUT, but FUT framework can be used to execute the
UT.

## How do the UTs work?

Unity C test framework is the base upon which the UTs are developed. Detailed
description of the framework, as well how to develop tests is out of scope of
this document.

For more information, see the website:\
<http://www.throwtheswitch.org/unity>

## Hardware

This manual assumes OSRT is available, and the tested device is its DUT.

## How to execute tests using the init.sh script?

Similar to other test suites, navigate to the fut-base directory and execute:

```bash
./init.sh -path test/UT_test.py -o
```

Results are presented as print-out to the console. Refer to the **Inspecting
the results** section.

## Jenkins execution

### How to execute the UTs inside Jenkins environment?

There is an option to run the UT inside Jenkins jobs. The settings are the same
as for running regular FUT suites, but one must:

- specify `test/UT_test.py` in **FUT_PYTEST_LIST** and
- provide the FW image file at **UPGRADE_BUILD_NAME** and
  **UPGRADE_BUILD_NUMBER** for the selected device.

Jenkins run will execute UT tests and results are provided inside Allure
generated report.

### Inspecting the results

Once the Allure report is generated, open it and open the UT test result
report. All executed tests are listed, the passed ones are marked green, and
failed are marked red.

To inspect the results of each individual test entity, click its label, and
then on the right side of the report, click **Test body** -> Testcase -> OUTPUT
to open the test log.

The actual results are available at the bottom of the log and would look like:

For the passed tests:

```plaintext
arp_plugin_tests:565:test_no_session:PASS (13 ms)
arp_plugin_tests:566:test_load_unload_plugin:PASS (0 ms)
arp_plugin_tests:567:test_arp_req:PASS (91 ms)
arp_plugin_tests:568:test_arp_reply:PASS (213 ms)
arp_plugin_tests:569:test_gratuitous_arp_reply:PASS (24 ms)
arp_plugin_tests:570:test_ip_mac_mapping:PASS (28 ms)
-----------------------
6 Tests 0 Failures 0 Ignored
OK
```

for failed tests:

```plaintext
fcm_ct_stats_tests:94:test_process_v4:FAIL: Expected TRUE Was FALSE (645 ms)
fcm_ct_stats_tests:94:test_process_v6:FAIL: Expected TRUE Was FALSE (48 ms)
fcm_ct_stats_tests:94:test_process_v4_zones:FAIL: Expected TRUE Was FALSE (20 ms)
fcm_ct_stats_tests:94:test_process_v6_zones:FAIL: Expected TRUE Was FALSE (17 ms)
fcm_ct_stats_tests:94:test_ct_stat_v4:FAIL: Expected TRUE Was FALSE (32 ms)
fcm_ct_stats_tests:587:test_ct_stat_v6:PASS (10 ms)
fcm_ct_stats_tests:589:test_ct_stats_collect_filter_cb:PASS (10 ms)
-----------------------
7 Tests 5 Failures 0 Ignored
-----------------------
1:    Failed in test_process_v4
2:    Failed in test_process_v6
3:    Failed in test_process_v4_zones
4:    Failed in test_process_v6_zones
5:    Failed in test_ct_stat_v4
-----------------------
FAIL
```
