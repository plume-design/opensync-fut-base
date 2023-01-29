# BRV Testing

## Overview

The Basic Requirements Verification (BRV) test suite determines:

- On-device FUT testcase execution prerequisites
- OpenSync integration prerequisites

Execution of other functional tests requires availability of multiple tests and
scripts. The testcases use these scripts to perform various actions on devices
that are included in the testbed (OSRT) as well as on DUT itself.

If BRV testcases do not pass, many other functional testcases might fail, as
the device (system) lacks the required tools, or scripts to perform various
actions and procedures.

The suite consists of a number of testcases that verify the following:

- Availability of tools on the device
- Availability of scripts on the device
- Availability of BusyBox built-ins
- Open vSwitch (OVS) version

The BRV test suite must be run after COMPAT tests, and before other functional
suites.
